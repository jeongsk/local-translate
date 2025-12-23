"""Async task management utilities for PySide6."""

from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from typing import Any, Callable, Optional
import traceback
import sys


class WorkerSignals(QObject):
    """
    Signals for worker communication.
    Must be a separate QObject because QRunnable is not a QObject.
    """

    started = Signal(str)  # task_id
    progress = Signal(str, int, str)  # task_id, percentage, status_message
    result = Signal(str, object)  # task_id, result_data
    error = Signal(str, str, str)  # task_id, error_message, traceback
    finished = Signal(str)  # task_id


class Worker(QRunnable):
    """
    Generic worker for running tasks in background thread.
    Handles cancellation, progress reporting, and error handling.
    """

    def __init__(
        self,
        task_id: str,
        fn: Callable,
        *args: Any,
        **kwargs: Any,
    ):
        """
        Initialize worker.

        Args:
            task_id: Unique task identifier
            fn: Function to execute in background
            *args: Positional arguments for fn
            **kwargs: Keyword arguments for fn
        """
        super().__init__()
        self.task_id = task_id
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self._is_cancelled = False

        # Allow task to be auto-deleted after completion
        self.setAutoDelete(True)

    def cancel(self) -> None:
        """Request cancellation of this task."""
        self._is_cancelled = True

    @property
    def is_cancelled(self) -> bool:
        """Check if task has been cancelled."""
        return self._is_cancelled

    @Slot()
    def run(self) -> None:
        """
        Execute the task.
        This runs in a background thread.
        """
        try:
            self.signals.started.emit(self.task_id)

            # Check cancellation before starting
            if self._is_cancelled:
                self.signals.finished.emit(self.task_id)
                return

            # Add progress_callback to kwargs if function supports it
            if "progress_callback" not in self.kwargs:
                self.kwargs["progress_callback"] = self._progress_callback

            # Execute function
            result = self.fn(*self.args, **self.kwargs)

            # Check if cancelled during execution
            if self._is_cancelled:
                self.signals.finished.emit(self.task_id)
                return

            # Emit result
            self.signals.result.emit(self.task_id, result)

        except Exception as e:
            # Capture full traceback for debugging
            tb = traceback.format_exception(*sys.exc_info())
            self.signals.error.emit(self.task_id, str(e), "".join(tb))

        finally:
            # Always emit finished signal
            self.signals.finished.emit(self.task_id)

    def _progress_callback(self, percentage: int, message: str) -> None:
        """
        Internal progress callback.

        Args:
            percentage: Progress percentage (0-100)
            message: Status message
        """
        if not self._is_cancelled:
            self.signals.progress.emit(self.task_id, percentage, message)


class TaskManager(QObject):
    """
    Manages background tasks with cancellation support.
    """

    def __init__(self) -> None:
        """Initialize task manager."""
        super().__init__()
        self.active_tasks: dict[str, Worker] = {}
        self.task_counter = 0

    def generate_task_id(self) -> str:
        """
        Generate unique task ID.

        Returns:
            Unique task identifier
        """
        self.task_counter += 1
        return f"task_{self.task_counter}"

    def submit_task(
        self,
        fn: Callable,
        *args: Any,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Worker:
        """
        Submit a task for background execution.

        Args:
            fn: Function to execute
            *args: Positional arguments
            task_id: Optional task ID (generated if not provided)
            **kwargs: Keyword arguments

        Returns:
            Worker instance
        """
        if task_id is None:
            task_id = self.generate_task_id()

        worker = Worker(task_id, fn, *args, **kwargs)

        # Track active task
        self.active_tasks[task_id] = worker

        # Clean up when finished
        worker.signals.finished.connect(lambda tid: self._on_task_finished(tid))

        return worker

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a specific task.

        Args:
            task_id: Task identifier

        Returns:
            True if task was cancelled, False if not found
        """
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            return True
        return False

    def cancel_all_tasks(self) -> None:
        """Cancel all active tasks."""
        for worker in self.active_tasks.values():
            worker.cancel()

    def _on_task_finished(self, task_id: str) -> None:
        """
        Handle task completion.

        Args:
            task_id: Finished task identifier
        """
        self.active_tasks.pop(task_id, None)

    def get_active_task_count(self) -> int:
        """
        Get number of active tasks.

        Returns:
            Active task count
        """
        return len(self.active_tasks)
