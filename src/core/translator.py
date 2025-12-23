"""Translation service with async execution and debouncing."""

from PySide6.QtCore import QObject, QThreadPool, QTimer, Signal
from typing import Optional
import time
import uuid

from ..utils.logger import get_logger
from ..utils.async_helpers import Worker
from .model_manager import ModelManager
from .language_detector import LanguageDetector
from .config import config

logger = get_logger(__name__)


class TranslationService(QObject):
    """
    High-level translation service with debouncing and async execution.
    """

    # Public signals
    translationStarted = Signal(str)  # task_id
    translationProgress = Signal(str, int, str)  # task_id, percentage, message
    translationComplete = Signal(str, str, str)  # task_id, source_lang, translated_text
    translationError = Signal(str, str)  # task_id, error_message

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
        self.thread_pool.setMaxThreadCount(2)  # Max 2 concurrent translations

        # Debouncing support
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._execute_pending_task)
        self.pending_task = None

        # Track active tasks
        self.active_tasks: dict[str, Worker] = {}
        self.last_task_id: Optional[str] = None

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
        Execute translation task in thread pool.

        Args:
            task_id: Task identifier
            text: Text to translate
            source_lang: Source language
            target_lang: Target language
        """
        # Cancel all currently active tasks (most recent wins)
        self.cancel_all_tasks()

        # Create worker
        worker = Worker(
            task_id=task_id,
            fn=self._translate_worker,
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
        )

        # Connect signals
        worker.signals.started.connect(self._on_worker_started)
        worker.signals.progress.connect(self._on_worker_progress)
        worker.signals.result.connect(self._on_worker_result)
        worker.signals.error.connect(self._on_worker_error)
        worker.signals.finished.connect(self._on_worker_finished)

        # Track active task
        self.active_tasks[task_id] = worker

        # Submit to thread pool
        self.thread_pool.start(worker)
        logger.info(f"Task {task_id} submitted to thread pool")

    def _translate_worker(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        progress_callback: Optional[callable] = None,
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
        source_lang, translated_text = result
        logger.info(f"Worker result received: {task_id}")
        self.translationComplete.emit(task_id, source_lang, translated_text)

    def _on_worker_error(self, task_id: str, error_message: str, traceback_str: str) -> None:
        """Handle worker error signal."""
        logger.error(f"Worker error for {task_id}: {error_message}")
        logger.debug(f"Traceback:\n{traceback_str}")
        self.translationError.emit(task_id, error_message)

    def _on_worker_finished(self, task_id: str) -> None:
        """Handle worker finished signal."""
        logger.debug(f"Worker finished: {task_id}")
        self.active_tasks.pop(task_id, None)
