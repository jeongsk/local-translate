"""Unit tests for configuration module."""

import pytest

from src.core.config import (
    LanguageCode,
    Language,
    SUPPORTED_LANGUAGES,
    get_language,
    get_supported_languages,
    ModelConfig,
    PerformanceConfig,
    AppConfig,
    config,
)


class TestLanguageCode:
    """Tests for LanguageCode enum."""

    def test_language_code_values(self):
        """Test LanguageCode enum has correct ISO 639-1 values."""
        assert LanguageCode.AUTO.value == "auto"
        assert LanguageCode.KOREAN.value == "ko"
        assert LanguageCode.ENGLISH.value == "en"
        assert LanguageCode.JAPANESE.value == "ja"
        assert LanguageCode.CHINESE.value == "zh"
        assert LanguageCode.SPANISH.value == "es"
        assert LanguageCode.FRENCH.value == "fr"
        assert LanguageCode.GERMAN.value == "de"
        assert LanguageCode.RUSSIAN.value == "ru"
        assert LanguageCode.PORTUGUESE.value == "pt"
        assert LanguageCode.ITALIAN.value == "it"

    def test_all_language_codes_are_strings(self):
        """Test all language codes are strings."""
        for code in LanguageCode:
            assert isinstance(code.value, str)

    def test_language_code_count(self):
        """Test total number of language codes (10 + auto)."""
        assert len(LanguageCode) == 11


class TestLanguage:
    """Tests for Language dataclass."""

    def test_language_creation(self):
        """Test creating a Language instance."""
        lang = Language(
            code=LanguageCode.ENGLISH,
            name="English",
            display_name="English",
            is_supported=True,
        )

        assert lang.code == LanguageCode.ENGLISH
        assert lang.name == "English"
        assert lang.display_name == "English"
        assert lang.is_supported is True

    def test_language_str_returns_display_name(self):
        """Test __str__ returns display_name."""
        lang = Language(
            code=LanguageCode.KOREAN,
            name="Korean",
            display_name="한국어",
        )

        assert str(lang) == "한국어"

    def test_language_is_frozen(self):
        """Test Language is immutable (frozen dataclass)."""
        lang = Language(
            code=LanguageCode.ENGLISH,
            name="English",
            display_name="English",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            lang.name = "Modified"


class TestSupportedLanguages:
    """Tests for SUPPORTED_LANGUAGES dictionary."""

    def test_supported_languages_contains_all_codes(self):
        """Test SUPPORTED_LANGUAGES contains all LanguageCode values."""
        for code in LanguageCode:
            assert code in SUPPORTED_LANGUAGES

    def test_supported_languages_values_are_language_instances(self):
        """Test all values are Language instances."""
        for lang in SUPPORTED_LANGUAGES.values():
            assert isinstance(lang, Language)

    def test_auto_language_exists(self):
        """Test auto-detect language is in supported languages."""
        auto_lang = SUPPORTED_LANGUAGES[LanguageCode.AUTO]

        assert auto_lang.code == LanguageCode.AUTO
        assert auto_lang.name == "Auto Detect"

    def test_korean_language_display_name(self):
        """Test Korean language has correct display name."""
        korean = SUPPORTED_LANGUAGES[LanguageCode.KOREAN]

        assert korean.display_name == "한국어"

    def test_all_languages_marked_supported(self):
        """Test all languages are marked as supported."""
        for lang in SUPPORTED_LANGUAGES.values():
            assert lang.is_supported is True


class TestGetLanguage:
    """Tests for get_language function."""

    def test_get_language_returns_language(self):
        """Test get_language returns Language instance."""
        lang = get_language(LanguageCode.ENGLISH)

        assert isinstance(lang, Language)
        assert lang.code == LanguageCode.ENGLISH

    def test_get_language_raises_for_unknown_code(self):
        """Test get_language raises KeyError for unknown code."""
        with pytest.raises(KeyError):
            get_language("unknown")  # type: ignore


class TestGetSupportedLanguages:
    """Tests for get_supported_languages function."""

    def test_get_supported_languages_returns_list(self):
        """Test get_supported_languages returns a list."""
        languages = get_supported_languages()

        assert isinstance(languages, list)

    def test_get_supported_languages_includes_auto(self):
        """Test get_supported_languages includes auto by default."""
        languages = get_supported_languages()
        codes = [lang.code for lang in languages]

        assert LanguageCode.AUTO in codes

    def test_get_supported_languages_exclude_auto(self):
        """Test get_supported_languages can exclude auto."""
        languages = get_supported_languages(exclude_auto=True)
        codes = [lang.code for lang in languages]

        assert LanguageCode.AUTO not in codes

    def test_get_supported_languages_count(self):
        """Test get_supported_languages returns correct count."""
        with_auto = get_supported_languages()
        without_auto = get_supported_languages(exclude_auto=True)

        assert len(with_auto) == 11
        assert len(without_auto) == 10


class TestModelConfig:
    """Tests for ModelConfig dataclass."""

    def test_model_config_default_values(self):
        """Test ModelConfig has correct default values."""
        config = ModelConfig()

        assert config.model_id == "yanolja/YanoljaNEXT-Rosetta-4B"
        assert config.device == "auto"
        assert config.quantization == "none"
        assert config.max_new_tokens == 512
        assert config.dtype == "bfloat16"

    def test_model_config_custom_values(self):
        """Test ModelConfig accepts custom values."""
        config = ModelConfig(
            model_id="custom/model",
            device="cpu",
            quantization="int8",
            max_new_tokens=256,
        )

        assert config.model_id == "custom/model"
        assert config.device == "cpu"
        assert config.quantization == "int8"
        assert config.max_new_tokens == 256

    def test_model_config_is_frozen(self):
        """Test ModelConfig is immutable."""
        config = ModelConfig()

        with pytest.raises(Exception):
            config.model_id = "different/model"


class TestPerformanceConfig:
    """Tests for PerformanceConfig dataclass."""

    def test_performance_config_default_values(self):
        """Test PerformanceConfig has correct defaults."""
        config = PerformanceConfig()

        assert config.short_text_threshold == 2.0
        assert config.medium_text_threshold == 5.0
        assert config.max_text_length == 2000
        assert config.short_text_max == 500
        assert config.max_memory_usage == 500
        assert config.debounce_delay_ms == 500
        assert config.model_load_timeout == 30

    def test_performance_config_is_frozen(self):
        """Test PerformanceConfig is immutable."""
        config = PerformanceConfig()

        with pytest.raises(Exception):
            config.max_text_length = 5000


class TestAppConfig:
    """Tests for AppConfig dataclass."""

    def test_app_config_default_values(self):
        """Test AppConfig has correct defaults."""
        app_config = AppConfig()

        assert app_config.app_name == "LocalTranslate"
        assert app_config.organization == "LocalTranslate"
        assert app_config.version == "0.1.0"
        assert app_config.window_min_width == 800
        assert app_config.window_min_height == 600

    def test_app_config_contains_model_config(self):
        """Test AppConfig contains ModelConfig."""
        app_config = AppConfig()

        assert isinstance(app_config.model, ModelConfig)

    def test_app_config_contains_performance_config(self):
        """Test AppConfig contains PerformanceConfig."""
        app_config = AppConfig()

        assert isinstance(app_config.performance, PerformanceConfig)

    def test_app_config_is_frozen(self):
        """Test AppConfig is immutable."""
        app_config = AppConfig()

        with pytest.raises(Exception):
            app_config.app_name = "NewName"


class TestGlobalConfig:
    """Tests for global config instance."""

    def test_global_config_exists(self):
        """Test global config instance exists."""
        assert config is not None

    def test_global_config_is_app_config(self):
        """Test global config is AppConfig instance."""
        assert isinstance(config, AppConfig)

    def test_global_config_has_expected_app_name(self):
        """Test global config has expected app name."""
        assert config.app_name == "LocalTranslate"
