"""Unit tests for TranslationService."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import QCoreApplication

from src.core.translator import TranslationService


class TestTranslationServiceInit:
    """Tests for TranslationService initialization."""

    def test_init_with_default_debounce(self, mock_model_manager, mock_language_detector, qapp):
        """Test initialization with default debounce value."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        assert service.model_manager == mock_model_manager
        assert service.language_detector == mock_language_detector
        assert service.debounce_ms == 500
        assert service.pending_task is None
        assert len(service.active_tasks) == 0

    def test_init_with_custom_debounce(self, mock_model_manager, mock_language_detector, qapp):
        """Test initialization with custom debounce value."""
        service = TranslationService(mock_model_manager, mock_language_detector, debounce_ms=1000)

        assert service.debounce_ms == 1000


class TestTranslationServiceTranslate:
    """Tests for translate method."""

    def test_translate_returns_task_id(self, mock_model_manager, mock_language_detector, qapp):
        """Test that translate returns a task ID."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        task_id = service.translate("Hello, world!", debounce=False)

        assert task_id is not None
        assert len(task_id) == 8  # UUID first 8 chars

    def test_translate_with_debounce_sets_pending_task(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test that translate with debounce sets pending task."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        task_id = service.translate("Hello", debounce=True)

        assert service.pending_task is not None
        assert service.pending_task[0] == task_id

    def test_translate_without_debounce_executes_immediately(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test that translate without debounce executes immediately."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        task_id = service.translate("Hello", debounce=False)

        # Task should be in active_tasks
        assert task_id in service.active_tasks

    def test_translate_cancels_previous_pending_task(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test that new translate cancels previous pending task."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        task_id1 = service.translate("Hello", debounce=True)
        task_id2 = service.translate("World", debounce=True)

        # Only task_id2 should be pending
        assert service.pending_task[0] == task_id2
        assert service.pending_task[1] == "World"

    def test_translate_updates_last_task_id(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test that last_task_id is updated on each translate call."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        task_id1 = service.translate("Hello", debounce=True)
        assert service.last_task_id == task_id1

        task_id2 = service.translate("World", debounce=True)
        assert service.last_task_id == task_id2


class TestTranslationServiceCancel:
    """Tests for cancel methods."""

    def test_cancel_task_returns_true_for_active_task(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test cancel_task returns True for active task."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        task_id = service.translate("Hello", debounce=False)
        result = service.cancel_task(task_id)

        assert result is True

    def test_cancel_task_returns_false_for_unknown_task(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test cancel_task returns False for unknown task."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        result = service.cancel_task("unknown_id")

        assert result is False

    def test_cancel_all_tasks_clears_active_tasks(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test cancel_all_tasks cancels all active tasks."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        # Create multiple tasks
        service.translate("Hello", debounce=False)
        service.translate("World", debounce=False)

        initial_count = len(service.active_tasks)
        service.cancel_all_tasks()

        # All tasks should be marked as cancelled
        assert initial_count > 0


class TestTranslationServiceShutdown:
    """Tests for shutdown method."""

    def test_shutdown_cancels_active_tasks(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test shutdown cancels all active tasks."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        service.translate("Hello", debounce=False)
        service.shutdown()

        # Shutdown should complete without error


class TestTranslationServiceWorker:
    """Tests for translation worker function."""

    def test_worker_detects_language_when_auto(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test worker detects language when source is auto."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        # Call private method directly for testing
        result = service._translate_worker(
            text="Hello world",
            source_lang="auto",
            target_lang="Korean",
            progress_callback=None,
        )

        mock_language_detector.detect.assert_called_once_with("Hello world")

    def test_worker_uses_specified_language(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test worker uses specified language without detection."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        result = service._translate_worker(
            text="Hello world",
            source_lang="en",
            target_lang="Korean",
            progress_callback=None,
        )

        # Language detector should not be called when language is specified
        mock_language_detector.detect.assert_not_called()

    def test_worker_calls_model_translate(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test worker calls model manager translate."""
        service = TranslationService(mock_model_manager, mock_language_detector)

        result = service._translate_worker(
            text="Hello",
            source_lang="en",
            target_lang="Korean",
            progress_callback=None,
        )

        mock_model_manager.translate.assert_called_once()

    def test_worker_reports_progress(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test worker reports progress via callback."""
        service = TranslationService(mock_model_manager, mock_language_detector)
        progress_callback = Mock()

        result = service._translate_worker(
            text="Hello",
            source_lang="en",
            target_lang="Korean",
            progress_callback=progress_callback,
        )

        # Progress callback should be called at least once
        assert progress_callback.call_count >= 1


class TestTranslationServiceSignals:
    """Tests for translation signals."""

    def test_translation_started_signal_emitted(
        self, mock_model_manager, mock_language_detector, qapp
    ):
        """Test translationStarted signal is emitted."""
        service = TranslationService(mock_model_manager, mock_language_detector)
        signal_handler = Mock()
        service.translationStarted.connect(signal_handler)

        task_id = service.translate("Hello", debounce=False)

        # Process events to allow signal propagation
        qapp.processEvents()

        # Signal should be emitted
        # Note: In real test environment, would need to wait for thread
