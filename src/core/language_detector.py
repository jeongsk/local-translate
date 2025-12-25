"""Language detection using lingua-py."""

from lingua import Language, LanguageDetectorBuilder
from typing import Optional, Tuple
from functools import lru_cache

from utils.logger import get_logger
from core.config import LanguageCode

logger = get_logger(__name__)


class LanguageDetector:
    """Detects language of input text using lingua-py."""

    # Map lingua Language enum to our LanguageCode
    LINGUA_TO_CODE = {
        Language.KOREAN: LanguageCode.KOREAN,
        Language.ENGLISH: LanguageCode.ENGLISH,
        Language.JAPANESE: LanguageCode.JAPANESE,
        Language.CHINESE: LanguageCode.CHINESE,
        Language.SPANISH: LanguageCode.SPANISH,
        Language.FRENCH: LanguageCode.FRENCH,
        Language.GERMAN: LanguageCode.GERMAN,
        Language.RUSSIAN: LanguageCode.RUSSIAN,
        Language.PORTUGUESE: LanguageCode.PORTUGUESE,
        Language.ITALIAN: LanguageCode.ITALIAN,
    }

    def __init__(self):
        """Initialize language detector with supported languages."""
        logger.info("Initializing LanguageDetector...")

        # Build detector with only supported languages
        self.detector = LanguageDetectorBuilder.from_languages(
            Language.KOREAN,
            Language.ENGLISH,
            Language.JAPANESE,
            Language.CHINESE,
            Language.SPANISH,
            Language.FRENCH,
            Language.GERMAN,
            Language.RUSSIAN,
            Language.PORTUGUESE,
            Language.ITALIAN,
        ).with_preloaded_language_models().build()

        logger.info("LanguageDetector initialized with 10 languages")

    def detect(self, text: str) -> Optional[str]:
        """
        Detect language of text.

        Args:
            text: Input text to detect

        Returns:
            ISO 639-1 language code (e.g., 'en', 'ko'), or None if detection fails
        """
        if not text or len(text.strip()) < 3:
            logger.warning("Text too short for reliable detection")
            return None

        try:
            detected = self.detector.detect_language_of(text)

            if detected is None:
                logger.warning(f"Could not detect language for text: '{text[:50]}...'")
                return None

            # Convert to our language code
            if detected in self.LINGUA_TO_CODE:
                code = self.LINGUA_TO_CODE[detected].value
                logger.debug(f"Detected language: {code} for text: '{text[:50]}...'")
                return code
            else:
                logger.warning(f"Detected unsupported language: {detected}")
                return None

        except Exception as e:
            logger.error(f"Language detection error: {e}", exc_info=True)
            return None

    def detect_with_confidence(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect language with confidence score.

        Args:
            text: Input text to detect

        Returns:
            Tuple of (language_code, confidence_score)
            confidence_score is 0.0 if detection fails
        """
        if not text or len(text.strip()) < 3:
            return None, 0.0

        try:
            confidence_values = self.detector.compute_language_confidence_values(text)

            if not confidence_values:
                logger.warning(f"No confidence values for text: '{text[:50]}...'")
                return None, 0.0

            # Get highest confidence result
            best = confidence_values[0]

            if best.language in self.LINGUA_TO_CODE:
                code = self.LINGUA_TO_CODE[best.language].value
                confidence = best.value
                logger.debug(
                    f"Detected {code} with {confidence:.2%} confidence for: '{text[:50]}...'"
                )
                return code, confidence
            else:
                return None, 0.0

        except Exception as e:
            logger.error(f"Language detection with confidence error: {e}", exc_info=True)
            return None, 0.0

    def is_language(self, text: str, expected_lang: str, threshold: float = 0.7) -> bool:
        """
        Check if text is in expected language with confidence threshold.

        Args:
            text: Input text
            expected_lang: Expected language code (e.g., 'en', 'ko')
            threshold: Confidence threshold (0.0-1.0)

        Returns:
            True if detected language matches expected with sufficient confidence
        """
        detected_lang, confidence = self.detect_with_confidence(text)

        if detected_lang is None:
            return False

        is_match = detected_lang == expected_lang and confidence >= threshold

        if not is_match:
            logger.debug(
                f"Language mismatch: expected {expected_lang}, "
                f"detected {detected_lang} ({confidence:.2%})"
            )

        return is_match


@lru_cache(maxsize=1)
def get_language_detector() -> LanguageDetector:
    """
    Get singleton language detector instance.

    Returns:
        LanguageDetector instance
    """
    return LanguageDetector()
