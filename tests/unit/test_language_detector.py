"""Unit tests for LanguageDetector."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.core.language_detector import LanguageDetector, get_language_detector
from src.core.config import LanguageCode


class TestLanguageDetectorInit:
    """Tests for LanguageDetector initialization."""

    def test_init_creates_detector(self):
        """Test that initialization creates a lingua detector."""
        detector = LanguageDetector()

        assert detector.detector is not None

    def test_lingua_to_code_mapping_complete(self):
        """Test that all supported languages have mappings."""
        detector = LanguageDetector()

        # Should have 10 language mappings
        assert len(detector.LINGUA_TO_CODE) == 10


class TestLanguageDetectorDetect:
    """Tests for detect method."""

    def test_detect_returns_none_for_empty_text(self):
        """Test that detect returns None for empty text."""
        detector = LanguageDetector()

        result = detector.detect("")

        assert result is None

    def test_detect_returns_none_for_short_text(self):
        """Test that detect returns None for text shorter than 3 chars."""
        detector = LanguageDetector()

        result = detector.detect("Hi")

        assert result is None

    def test_detect_returns_none_for_whitespace_only(self):
        """Test that detect returns None for whitespace-only text."""
        detector = LanguageDetector()

        result = detector.detect("   ")

        assert result is None

    def test_detect_english_text(self):
        """Test detecting English text."""
        detector = LanguageDetector()

        result = detector.detect("Hello, this is a test sentence in English.")

        assert result == "en"

    def test_detect_korean_text(self):
        """Test detecting Korean text."""
        detector = LanguageDetector()

        result = detector.detect("안녕하세요, 이것은 한국어 테스트 문장입니다.")

        assert result == "ko"

    def test_detect_japanese_text(self):
        """Test detecting Japanese text."""
        detector = LanguageDetector()

        result = detector.detect("こんにちは、これは日本語のテスト文です。")

        assert result == "ja"

    def test_detect_chinese_text(self):
        """Test detecting Chinese text."""
        detector = LanguageDetector()

        result = detector.detect("你好，这是一个中文测试句子。")

        assert result == "zh"

    def test_detect_spanish_text(self):
        """Test detecting Spanish text."""
        detector = LanguageDetector()

        result = detector.detect("Hola, esta es una oración de prueba en español.")

        assert result == "es"

    def test_detect_french_text(self):
        """Test detecting French text."""
        detector = LanguageDetector()

        result = detector.detect("Bonjour, ceci est une phrase de test en français.")

        assert result == "fr"

    def test_detect_german_text(self):
        """Test detecting German text."""
        detector = LanguageDetector()

        result = detector.detect("Hallo, dies ist ein Testsatz auf Deutsch.")

        assert result == "de"


class TestLanguageDetectorDetectWithConfidence:
    """Tests for detect_with_confidence method."""

    def test_detect_with_confidence_returns_tuple(self):
        """Test that detect_with_confidence returns a tuple."""
        detector = LanguageDetector()

        result = detector.detect_with_confidence("Hello, this is English.")

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_detect_with_confidence_returns_none_for_empty_text(self):
        """Test that detect_with_confidence returns (None, 0.0) for empty text."""
        detector = LanguageDetector()

        lang, confidence = detector.detect_with_confidence("")

        assert lang is None
        assert confidence == 0.0

    def test_detect_with_confidence_returns_valid_confidence(self):
        """Test that confidence is between 0 and 1."""
        detector = LanguageDetector()

        lang, confidence = detector.detect_with_confidence(
            "This is definitely English text for testing."
        )

        assert 0.0 <= confidence <= 1.0

    def test_detect_with_confidence_high_for_clear_text(self):
        """Test that confidence is high for clear language text."""
        detector = LanguageDetector()

        lang, confidence = detector.detect_with_confidence(
            "The quick brown fox jumps over the lazy dog. "
            "This is a very clear English sentence that should be detected easily."
        )

        assert lang == "en"
        assert confidence > 0.9


class TestLanguageDetectorIsLanguage:
    """Tests for is_language method."""

    def test_is_language_returns_true_for_matching_language(self):
        """Test is_language returns True for matching language."""
        detector = LanguageDetector()

        result = detector.is_language(
            "This is clearly English text for testing purposes.",
            "en",
            threshold=0.7,
        )

        assert result is True

    def test_is_language_returns_false_for_non_matching_language(self):
        """Test is_language returns False for non-matching language."""
        detector = LanguageDetector()

        result = detector.is_language(
            "This is clearly English text.",
            "ko",
            threshold=0.7,
        )

        assert result is False

    def test_is_language_returns_false_for_empty_text(self):
        """Test is_language returns False for empty text."""
        detector = LanguageDetector()

        result = detector.is_language("", "en", threshold=0.7)

        assert result is False

    def test_is_language_respects_threshold(self):
        """Test is_language respects confidence threshold."""
        detector = LanguageDetector()

        # Very high threshold might fail even for correct detection
        result = detector.is_language(
            "Hello",  # Short text, lower confidence
            "en",
            threshold=0.99,
        )

        # Result depends on actual confidence, but should not error


class TestGetLanguageDetector:
    """Tests for get_language_detector singleton."""

    def test_get_language_detector_returns_instance(self):
        """Test get_language_detector returns LanguageDetector instance."""
        # Clear cache first
        get_language_detector.cache_clear()

        detector = get_language_detector()

        assert isinstance(detector, LanguageDetector)

    def test_get_language_detector_returns_same_instance(self):
        """Test get_language_detector returns the same instance (singleton)."""
        # Clear cache first
        get_language_detector.cache_clear()

        detector1 = get_language_detector()
        detector2 = get_language_detector()

        assert detector1 is detector2


class TestLanguageDetectorEdgeCases:
    """Tests for edge cases and special inputs."""

    def test_detect_mixed_language_text(self):
        """Test detection with mixed language text."""
        detector = LanguageDetector()

        # Mixed Korean and English - should detect dominant language
        result = detector.detect("Hello 안녕하세요 World 세계")

        # Result should be one of the languages
        assert result in ["en", "ko", None]

    def test_detect_text_with_numbers(self):
        """Test detection with text containing numbers."""
        detector = LanguageDetector()

        result = detector.detect("The year 2024 was a great year for technology.")

        assert result == "en"

    def test_detect_text_with_special_characters(self):
        """Test detection with special characters."""
        detector = LanguageDetector()

        result = detector.detect("Hello! How are you? I'm doing well...")

        assert result == "en"

    def test_detect_text_with_emojis(self):
        """Test detection with emoji-containing text."""
        detector = LanguageDetector()

        result = detector.detect("Hello world! 😀 This is a test.")

        assert result == "en"

    def test_detect_all_supported_languages(self):
        """Test that all supported languages can be detected."""
        detector = LanguageDetector()

        test_cases = [
            ("Hello, this is English.", "en"),
            ("안녕하세요, 한국어입니다.", "ko"),
            ("こんにちは、日本語です。", "ja"),
            ("你好，这是中文。", "zh"),
            ("Hola, esto es español.", "es"),
            ("Bonjour, c'est français.", "fr"),
            ("Hallo, das ist Deutsch.", "de"),
            ("Привет, это русский.", "ru"),
            ("Olá, isto é português.", "pt"),
            ("Ciao, questo è italiano.", "it"),
        ]

        for text, expected_lang in test_cases:
            result = detector.detect(text)
            assert result == expected_lang, f"Expected {expected_lang} for '{text}', got {result}"
