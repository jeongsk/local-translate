"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

# Add src to path for imports
_src_path = Path(__file__).parent.parent / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

import pytest
from typing import Generator
from unittest.mock import Mock, MagicMock
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication, None, None]:
    """
    Create QApplication instance for tests.
    Session-scoped to avoid multiple QApplication instances.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Don't quit the app as it may be needed by other tests


@pytest.fixture
def mock_model_manager() -> Mock:
    """
    Create a mocked ModelManager for testing without loading actual model.

    Returns:
        Mocked ModelManager instance
    """
    mock = Mock()
    mock.is_loaded = True
    mock.device = "cpu"
    mock.model_id = "yanolja/YanoljaNEXT-Rosetta-4B"

    # Mock translate method
    def mock_translate(text: str, source_lang: str = "auto", target_lang: str = "ko") -> str:
        """Mock translation that returns a predictable result."""
        return f"[MOCK TRANSLATION: {text[:20]}... -> {target_lang}]"

    mock.translate = Mock(side_effect=mock_translate)

    # Mock initialize method
    mock.initialize = Mock(return_value=True)

    # Mock progress callback
    mock.set_progress_callback = Mock()

    return mock


@pytest.fixture
def mock_language_detector() -> Mock:
    """
    Create a mocked LanguageDetector for testing.

    Returns:
        Mocked LanguageDetector instance
    """
    mock = Mock()

    def mock_detect(text: str) -> str:
        """Mock detection that returns 'en' for English-looking text."""
        if any(word in text.lower() for word in ["hello", "world", "good", "morning"]):
            return "en"
        elif any(
            char in text for char in ["안녕", "하세요", "감사", "세계"]
        ):  # Korean characters
            return "ko"
        else:
            return "en"  # Default to English

    mock.detect = Mock(side_effect=mock_detect)
    mock.detect_with_confidence = Mock(return_value=("en", 0.95))

    return mock


@pytest.fixture
def mock_translator_service(mock_model_manager: Mock, mock_language_detector: Mock) -> Mock:
    """
    Create a mocked TranslationService for integration tests.

    Args:
        mock_model_manager: Mocked model manager
        mock_language_detector: Mocked language detector

    Returns:
        Mocked TranslationService instance
    """
    mock = Mock()
    mock.model_manager = mock_model_manager
    mock.language_detector = mock_language_detector

    # Mock translate method that combines detection + translation
    def mock_translate_service(
        text: str,
        source_lang: str = "auto",
        target_lang: str = "ko",
        debounce: bool = False,
    ) -> str:
        task_id = "mock_task_123"

        # Auto-detect if needed
        if source_lang == "auto":
            source_lang = mock_language_detector.detect(text)

        # Translate
        result = mock_model_manager.translate(text, source_lang, target_lang)

        return task_id

    mock.translate = Mock(side_effect=mock_translate_service)
    mock.cancel_all_tasks = Mock()
    mock.shutdown = Mock()

    return mock


@pytest.fixture
def mock_preferences() -> Mock:
    """
    Create a mocked UserPreferences for testing.

    Returns:
        Mocked UserPreferences instance
    """
    mock = Mock()
    mock.source_language = "auto"
    mock.target_language = "ko"
    mock.auto_detect = True
    mock.theme = "auto"
    mock.window_geometry = None
    mock.window_state = None

    # Make properties writable
    type(mock).source_language = property(
        lambda self: self._source_language,
        lambda self, value: setattr(self, "_source_language", value),
    )
    type(mock).target_language = property(
        lambda self: self._target_language,
        lambda self, value: setattr(self, "_target_language", value),
    )

    mock._source_language = "auto"
    mock._target_language = "ko"

    mock.sync = Mock()
    mock.clear = Mock()

    return mock


@pytest.fixture(autouse=True)
def reset_singletons() -> Generator[None, None, None]:
    """
    Reset singleton instances between tests to avoid state leakage.
    """
    yield
    # Cleanup after test
    # Add singleton cleanup if needed


@pytest.fixture
def sample_text_short() -> str:
    """Short sample text for testing (<500 chars)."""
    return "Hello, world! This is a test translation."


@pytest.fixture
def sample_text_medium() -> str:
    """Medium sample text for testing (500-2000 chars)."""
    return "The quick brown fox jumps over the lazy dog. " * 50  # ~2,250 chars total


@pytest.fixture
def sample_text_long() -> str:
    """Long sample text for testing (>2000 chars)."""
    return "The quick brown fox jumps over the lazy dog. " * 100  # ~4,500 chars total
