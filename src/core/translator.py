"""Translation service with async execution and debouncing."""

import os
import time
import uuid
from dataclasses import dataclass
from typing import Callable, Optional

from PySide6.QtCore import QObject, QThreadPool, QTimer, Signal

from utils.logger import get_logger
from utils.async_helpers import Worker
from core.model_manager import ModelManager
from core.language_detector import LanguageDetector
from core.config import config
from core.error_handler import ErrorClassifier, ErrorType, TranslationError

logger = get_logger(__name__)


@dataclass
class RetryState:
    """Tracks retry state for a translation task."""

    task_id: str
    text: str
    source_lang: str
    target_lang: str
    attempt: int = 0
    max_attempts: int = 4  # 1 initial + 3 retries


class TranslationService(QObject):
    """
    High-level translation service with debouncing and async execution.
    """

    # Public signals
    translationStarted = Signal(str)  # task_id
    translationProgress = Signal(str, int, str)  # task_id, percentage, message
    translationComplete = Signal(str, str, str)  # task_id, source_lang, translated_text
    translationError = Signal(str, object)  # task_id, TranslationError
    translationRetrying = Signal(str, int, int, int)  # task_id, attempt, max_attempts, delay_ms

    def __init__(
        self,
        model_manager: ModelManager,
        language_detector: LanguageDetector,
        debounce_ms: int = 500,
    ):
        """
        Initialize translation service.

        Args:
            model_manager: Model manager instance
            language_detector: Language detector instance
            debounce_ms: Debounce delay in milliseconds
        """
        super().__init__()
        self.model_manager = model_manager
        self.language_detector = language_detector
        self.debounce_ms = debounce_ms

        # Thread pool for async execution
        self.thread_pool = QThreadPool.globalInstance()
        # Optimize thread count based on CPU cores (min 2, max 4)
        cpu_count = os.cpu_count() or 2
        max_threads = min(4, max(2, cpu_count))
        self.thread_pool.setMaxThreadCount(max_threads)

        # Debouncing support
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._execute_pending_task)
        self.pending_task = None

        # Track active tasks
        self.active_tasks: dict[str, Worker] = {}
        self.last_task_id: Optional[str] = None

        # Retry management
        self.retry_states: dict[str, RetryState] = {}

        # Timeout management
        self.timeout_timers: dict[str, QTimer] = {}

        logger.info(
            f"TranslationService initialized with {debounce_ms}ms debounce, "
            f"{self.thread_pool.maxThreadCount()} max threads"
        )

    def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "Korean",
        debounce: bool = True,
    ) -> str:
        """
        Submit translation task with optional debouncing.

        Args:
            text: Text to translate
            source_lang: Source language code or 'auto'
            target_lang: Target language name
            debounce: If True, debounce rapid successive calls

        Returns:
            task_id: Unique identifier for this task
        """
        # Generate unique task ID
        task_id = str(uuid.uuid4())[:8]

        if debounce:
            # Cancel pending task if exists
            if self.pending_task:
                old_task_id = self.pending_task[0]
                logger.debug(f"Cancelling pending task: {old_task_id}")
                self.pending_task = None

            # Store new task and restart debounce timer
            self.pending_task = (task_id, text, source_lang, target_lang)
            self.debounce_timer.start(self.debounce_ms)
            logger.debug(f"Task {task_id} pending (debouncing {self.debounce_ms}ms)")

        else:
            # Execute immediately without debouncing
            self._execute_task(task_id, text, source_lang, target_lang)

        self.last_task_id = task_id
        return task_id

    def _execute_pending_task(self) -> None:
        """Execute the pending debounced task."""
        if self.pending_task:
            task_id, text, source_lang, target_lang = self.pending_task
            self.pending_task = None
            logger.debug(f"Executing debounced task: {task_id}")
            self._execute_task(task_id, text, source_lang, target_lang)

    def _execute_task(self, task_id: str, text: str, source_lang: str, target_lang: str) -> None:
        """
        Execute translation task with retry support.

        Args:
            task_id: Task identifier
            text: Text to translate
            source_lang: Source language
            target_lang: Target language
        """
        # Cancel all currently active tasks (most recent wins)
        self.cancel_all_tasks()

        # Initialize retry state
        retry_state = RetryState(
            task_id=task_id,
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            max_attempts=config.error_handling.max_retries + 1,
        )
        self.retry_states[task_id] = retry_state

        # Start first attempt
        self._execute_attempt(retry_state)

    def _execute_attempt(self, retry_state: RetryState) -> None:
        """
        Execute a single translation attempt.

        Args:
            retry_state: Current retry state
        """
        retry_state.attempt += 1
        task_id = retry_state.task_id

        # Create worker
        worker = Worker(
            task_id=task_id,
            fn=self._translate_worker,
            text=retry_state.text,
            source_lang=retry_state.source_lang,
            target_lang=retry_state.target_lang,
        )

        # Connect signals
        worker.signals.started.connect(self._on_worker_started)
        worker.signals.progress.connect(self._on_worker_progress)
        worker.signals.result.connect(self._on_worker_result)
        worker.signals.error.connect(self._on_worker_error_with_retry)
        worker.signals.finished.connect(self._on_worker_finished)

        # Track active task
        self.active_tasks[task_id] = worker

        # Setup timeout timer
        self._setup_timeout(task_id)

        # Submit to thread pool
        self.thread_pool.start(worker)
        logger.info(
            f"Task {task_id} attempt {retry_state.attempt}/{retry_state.max_attempts} "
            f"submitted to thread pool"
        )

    def _setup_timeout(self, task_id: str) -> None:
        """Setup timeout timer for a translation task."""
        # Cancel existing timer if any
        self._cancel_timeout(task_id)

        timeout_ms = config.error_handling.translation_timeout_ms

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._on_timeout(task_id))

        # Store timer reference
        self.timeout_timers[task_id] = timer

        timer.start(timeout_ms)
        logger.debug(f"Timeout set for {task_id}: {timeout_ms}ms")

    def _cancel_timeout(self, task_id: str) -> None:
        """Cancel timeout timer for a task."""
        if task_id in self.timeout_timers:
            self.timeout_timers[task_id].stop()
            del self.timeout_timers[task_id]

    def _on_timeout(self, task_id: str) -> None:
        """Handle translation timeout."""
        logger.warning(f"Translation timeout: {task_id}")

        # Cancel the worker
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()

        # Create timeout error
        error = ErrorClassifier.create_timeout_error()

        # Try retry or emit error
        self._handle_error_with_retry(task_id, error)

    def _calculate_retry_delay(self, attempt: int) -> int:
        """Calculate retry delay with exponential backoff."""
        cfg = config.error_handling
        delay = cfg.initial_retry_delay_ms * (cfg.backoff_multiplier ** (attempt - 1))
        return min(int(delay), cfg.max_retry_delay_ms)

    def _handle_error_with_retry(self, task_id: str, error: TranslationError) -> None:
        """Handle error with potential retry."""
        retry_state = self.retry_states.get(task_id)
        if not retry_state:
            self.translationError.emit(task_id, error)
            return

        # Determine max retries based on error type
        max_retries = config.error_handling.max_retries
        if error.error_type == ErrorType.MEMORY:
            max_retries = config.error_handling.memory_error_max_retries

        # Check if retryable and within limits
        if error.is_retryable and retry_state.attempt <= max_retries:
            # Calculate delay with exponential backoff
            delay_ms = self._calculate_retry_delay(retry_state.attempt)

            logger.info(
                f"Retrying {task_id}: attempt {retry_state.attempt}/{max_retries + 1}, "
                f"delay {delay_ms}ms, error: {error.error_type.name}"
            )

            # Emit retrying signal
            self.translationRetrying.emit(
                task_id, retry_state.attempt, max_retries + 1, delay_ms
            )

            # Schedule retry
            QTimer.singleShot(delay_ms, lambda: self._execute_attempt(retry_state))
        else:
            # Max retries exceeded or not retryable
            logger.error(
                f"Translation failed after {retry_state.attempt} attempts: {task_id}, "
                f"error: {error.error_type.name}"
            )
            self.translationError.emit(task_id, error)
            self.retry_states.pop(task_id, None)

    def _translate_worker(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> tuple[str, str]:
        """
        Worker function for translation (runs in background thread).

        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language
            progress_callback: Progress callback from Worker

        Returns:
            Tuple of (detected_source_lang, translated_text)
        """
        start_time = time.time()

        # Auto-detect language if needed
        if source_lang == "auto":
            if progress_callback:
                progress_callback(10, "Detecting language...")

            detected = self.language_detector.detect(text)
            source_lang = detected if detected else "en"
            logger.info(f"Detected source language: {source_lang}")
        else:
            logger.info(f"Using specified source language: {source_lang}")

        # Perform translation
        if progress_callback:
            progress_callback(20, "Translating...")

        translated_text = self.model_manager.translate(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            progress_callback=progress_callback,
        )

        elapsed = time.time() - start_time
        logger.info(
            f"Translation completed in {elapsed:.2f}s: "
            f"'{text[:50]}...' ({len(text)} chars) -> "
            f"'{translated_text[:50]}...' ({len(translated_text)} chars)"
        )

        return source_lang, translated_text

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel specific task.

        Args:
            task_id: Task identifier

        Returns:
            True if task was cancelled, False if not found
        """
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            logger.info(f"Task {task_id} cancelled")
            return True
        return False

    def cancel_all_tasks(self) -> None:
        """Cancel all active tasks."""
        if self.active_tasks:
            logger.info(f"Cancelling {len(self.active_tasks)} active task(s)")
            for worker in self.active_tasks.values():
                worker.cancel()

        # Cancel all timeout timers
        for task_id in list(self.timeout_timers.keys()):
            self._cancel_timeout(task_id)

        # Clear retry states
        self.retry_states.clear()

    def shutdown(self) -> None:
        """Clean shutdown - cancel all tasks and wait for completion."""
        logger.info("Shutting down translation service...")
        self.cancel_all_tasks()
        self.thread_pool.waitForDone(5000)  # Wait up to 5 seconds
        logger.info("Translation service shutdown complete")

    # Signal handlers

    def _on_worker_started(self, task_id: str) -> None:
        """Handle worker started signal."""
        logger.debug(f"Worker started: {task_id}")
        self.translationStarted.emit(task_id)

    def _on_worker_progress(self, task_id: str, percentage: int, message: str) -> None:
        """Handle worker progress signal."""
        self.translationProgress.emit(task_id, percentage, message)

    def _on_worker_result(self, task_id: str, result: tuple) -> None:
        """Handle worker result signal."""
        # Cancel timeout timer on success
        self._cancel_timeout(task_id)

        # Clean up retry state on success
        self.retry_states.pop(task_id, None)

        source_lang, translated_text = result
        logger.info(f"Worker result received: {task_id}")
        self.translationComplete.emit(task_id, source_lang, translated_text)

    def _on_worker_error_with_retry(
        self, task_id: str, error_message: str, traceback_str: str
    ) -> None:
        """Handle worker error with retry logic."""
        logger.error(f"Worker error for {task_id}: {error_message}")
        logger.debug(f"Traceback:\n{traceback_str}")

        # Cancel timeout timer
        self._cancel_timeout(task_id)

        # Classify the error
        error = ErrorClassifier.classify_from_message(error_message, traceback_str)

        # Handle with retry logic
        self._handle_error_with_retry(task_id, error)

    def _on_worker_finished(self, task_id: str) -> None:
        """Handle worker finished signal."""
        logger.debug(f"Worker finished: {task_id}")
        self.active_tasks.pop(task_id, None)
