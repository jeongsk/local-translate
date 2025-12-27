"""Configuration management and language definitions."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class LanguageCode(str, Enum):
    """ISO 639-1 language codes for supported languages."""

    AUTO = "auto"  # Auto-detection
    KOREAN = "ko"
    ENGLISH = "en"
    JAPANESE = "ja"
    CHINESE = "zh"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    RUSSIAN = "ru"
    PORTUGUESE = "pt"
    ITALIAN = "it"


@dataclass(frozen=True)
class Language:
    """Language configuration with ISO code and display information."""

    code: LanguageCode
    name: str  # English name
    display_name: str  # Native name
    is_supported: bool = True

    def __str__(self) -> str:
        """Return display name for UI."""
        return self.display_name


# Language registry
SUPPORTED_LANGUAGES: Dict[LanguageCode, Language] = {
    LanguageCode.AUTO: Language(
        code=LanguageCode.AUTO,
        name="Auto Detect",
        display_name="자동 감지",
        is_supported=True,
    ),
    LanguageCode.KOREAN: Language(
        code=LanguageCode.KOREAN,
        name="Korean",
        display_name="한국어",
        is_supported=True,
    ),
    LanguageCode.ENGLISH: Language(
        code=LanguageCode.ENGLISH,
        name="English",
        display_name="English",
        is_supported=True,
    ),
    LanguageCode.JAPANESE: Language(
        code=LanguageCode.JAPANESE,
        name="Japanese",
        display_name="日本語",
        is_supported=True,
    ),
    LanguageCode.CHINESE: Language(
        code=LanguageCode.CHINESE,
        name="Chinese",
        display_name="中文",
        is_supported=True,
    ),
    LanguageCode.SPANISH: Language(
        code=LanguageCode.SPANISH,
        name="Spanish",
        display_name="Español",
        is_supported=True,
    ),
    LanguageCode.FRENCH: Language(
        code=LanguageCode.FRENCH,
        name="French",
        display_name="Français",
        is_supported=True,
    ),
    LanguageCode.GERMAN: Language(
        code=LanguageCode.GERMAN,
        name="German",
        display_name="Deutsch",
        is_supported=True,
    ),
    LanguageCode.RUSSIAN: Language(
        code=LanguageCode.RUSSIAN,
        name="Russian",
        display_name="Русский",
        is_supported=True,
    ),
    LanguageCode.PORTUGUESE: Language(
        code=LanguageCode.PORTUGUESE,
        name="Portuguese",
        display_name="Português",
        is_supported=True,
    ),
    LanguageCode.ITALIAN: Language(
        code=LanguageCode.ITALIAN,
        name="Italian",
        display_name="Italiano",
        is_supported=True,
    ),
}


def get_language(code: LanguageCode) -> Language:
    """
    Get language configuration by code.

    Args:
        code: ISO 639-1 language code

    Returns:
        Language configuration

    Raises:
        KeyError: If language code is not supported
    """
    return SUPPORTED_LANGUAGES[code]


def get_supported_languages(exclude_auto: bool = False) -> List[Language]:
    """
    Get list of all supported languages.

    Args:
        exclude_auto: If True, exclude auto-detection option

    Returns:
        List of supported languages
    """
    languages = [lang for lang in SUPPORTED_LANGUAGES.values() if lang.is_supported]

    if exclude_auto:
        languages = [lang for lang in languages if lang.code != LanguageCode.AUTO]

    return languages


@dataclass(frozen=True)
class ModelConfig:
    """Translation model configuration."""

    model_id: str = "yanolja/YanoljaNEXT-Rosetta-4B"
    device: str = "auto"  # auto, mps, cpu
    quantization: str = "none"  # int8, int4, none - using "none" for MPS compatibility
    max_new_tokens: int = 512
    dtype: str = "bfloat16"
    repetition_penalty: float = 1.2
    no_repeat_ngram_size: int = 3


@dataclass(frozen=True)
class PerformanceConfig:
    """Performance thresholds and limits."""

    # Translation latency thresholds (seconds)
    short_text_threshold: float = 2.0  # <500 chars
    medium_text_threshold: float = 5.0  # 500-2000 chars

    # Text length limits (characters)
    max_text_length: int = 2000
    short_text_max: int = 500

    # Memory limits (MB)
    max_memory_usage: int = 500

    # UI responsiveness
    debounce_delay_ms: int = 500  # Debounce delay for text input

    # Model loading
    model_load_timeout: int = 30  # seconds


@dataclass(frozen=True)
class ErrorHandlingConfig:
    """Error handling and retry configuration."""

    # Retry settings
    max_retries: int = 3  # Maximum retry attempts
    initial_retry_delay_ms: int = 1000  # First retry delay (1 second)
    max_retry_delay_ms: int = 10000  # Maximum delay (10 seconds)
    backoff_multiplier: float = 2.0  # Exponential backoff multiplier

    # Timeout settings
    translation_timeout_ms: int = 60000  # Translation timeout (60 seconds)

    # Special handling for memory errors
    memory_error_max_retries: int = 1  # Only retry once for memory errors


@dataclass(frozen=True)
class HistoryConfig:
    """Translation history configuration."""

    max_entries: int = 50  # Maximum number of history entries
    preview_length: int = 100  # Characters to show in preview
    search_debounce_ms: int = 150  # Search debounce delay


@dataclass(frozen=True)
class AppConfig:
    """Application-wide configuration."""

    app_name: str = "LocalTranslate"
    organization: str = "LocalTranslate"
    version: str = "0.1.2"

    # UI Configuration
    window_min_width: int = 800
    window_min_height: int = 600
    window_default_width: int = 1000
    window_default_height: int = 700

    # Model Configuration
    model: ModelConfig = ModelConfig()

    # Performance Configuration
    performance: PerformanceConfig = PerformanceConfig()

    # Error Handling Configuration
    error_handling: ErrorHandlingConfig = ErrorHandlingConfig()

    # History Configuration
    history: HistoryConfig = HistoryConfig()

    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR


# Global configuration instance
config = AppConfig()
