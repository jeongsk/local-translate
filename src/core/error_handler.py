"""Error handling and classification for translation errors."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
import re


class ErrorType(Enum):
    """Translation error types."""

    NETWORK = auto()  # 네트워크 연결 문제
    MEMORY = auto()  # 메모리 부족
    MODEL = auto()  # 모델 로딩/실행 문제
    TIMEOUT = auto()  # 작업 시간 초과
    VALIDATION = auto()  # 입력 검증 실패
    UNKNOWN = auto()  # 알 수 없는 에러


@dataclass
class TranslationError:
    """Structured translation error information."""

    error_type: ErrorType
    message: str  # 원본 에러 메시지
    cause: str  # 사용자 친화적 원인 설명
    solution: str  # 해결 방법
    is_retryable: bool  # 재시도 가능 여부
    original_exception: Optional[Exception] = None
    traceback: Optional[str] = None


# 에러 유형별 사용자 친화적 메시지
ERROR_MESSAGES: dict[ErrorType, dict] = {
    ErrorType.NETWORK: {
        "cause": "네트워크 연결에 문제가 발생했습니다.",
        "solution": "인터넷 연결을 확인하고 잠시 후 다시 시도해주세요.",
        "is_retryable": True,
    },
    ErrorType.MEMORY: {
        "cause": "시스템 메모리가 부족합니다.",
        "solution": "다른 프로그램을 종료하거나, 더 짧은 텍스트로 시도해주세요.",
        "is_retryable": True,
    },
    ErrorType.MODEL: {
        "cause": "번역 모델을 사용할 수 없습니다.",
        "solution": "애플리케이션을 재시작해주세요. 문제가 지속되면 저장공간(10GB 이상)을 확인해주세요.",
        "is_retryable": False,
    },
    ErrorType.TIMEOUT: {
        "cause": "번역 시간이 초과되었습니다.",
        "solution": "텍스트가 너무 길 수 있습니다. 텍스트를 나누어 시도하거나, 잠시 후 다시 시도해주세요.",
        "is_retryable": True,
    },
    ErrorType.VALIDATION: {
        "cause": "입력 텍스트에 문제가 있습니다.",
        "solution": "텍스트를 확인하고 다시 입력해주세요.",
        "is_retryable": False,
    },
    ErrorType.UNKNOWN: {
        "cause": "예상치 못한 오류가 발생했습니다.",
        "solution": "잠시 후 다시 시도해주세요. 문제가 지속되면 앱을 재시작해주세요.",
        "is_retryable": True,
    },
}


class ErrorClassifier:
    """Classifies exceptions into structured TranslationError."""

    # 에러 패턴 매핑 (정규식)
    NETWORK_PATTERNS = [
        r"connection",
        r"network",
        r"socket",
        r"ConnectionError",
        r"URLError",
        r"ConnectionRefused",
        r"ConnectionReset",
    ]

    MEMORY_PATTERNS = [
        r"out of memory",
        r"OOM",
        r"MemoryError",
        r"CUDA out of memory",
        r"MPS out of memory",
        r"cannot allocate",
        r"allocation failed",
    ]

    MODEL_PATTERNS = [
        r"Model not loaded",
        r"model.*not.*initialized",
        r"failed to load.*model",
        r"model.*failed",
    ]

    TIMEOUT_PATTERNS = [
        r"timed? ?out",
        r"timeout",
        r"deadline exceeded",
    ]

    @classmethod
    def classify(
        cls,
        exception: Exception,
        message: str,
        traceback_str: Optional[str] = None,
    ) -> TranslationError:
        """
        Classify an exception into a TranslationError.

        Args:
            exception: The original exception
            message: Error message string
            traceback_str: Optional traceback string

        Returns:
            TranslationError with classified type and user-friendly messages
        """
        error_type = cls._determine_type(exception, message)
        error_info = ERROR_MESSAGES[error_type]

        return TranslationError(
            error_type=error_type,
            message=message,
            cause=error_info["cause"],
            solution=error_info["solution"],
            is_retryable=error_info["is_retryable"],
            original_exception=exception,
            traceback=traceback_str,
        )

    @classmethod
    def classify_from_message(
        cls,
        message: str,
        traceback_str: Optional[str] = None,
    ) -> TranslationError:
        """
        Classify an error from message string only.

        Args:
            message: Error message string
            traceback_str: Optional traceback string

        Returns:
            TranslationError with classified type and user-friendly messages
        """
        # Create a generic exception for classification
        exception = Exception(message)
        return cls.classify(exception, message, traceback_str)

    @classmethod
    def create_timeout_error(cls) -> TranslationError:
        """Create a timeout error."""
        error_info = ERROR_MESSAGES[ErrorType.TIMEOUT]
        return TranslationError(
            error_type=ErrorType.TIMEOUT,
            message="Translation timed out",
            cause=error_info["cause"],
            solution=error_info["solution"],
            is_retryable=error_info["is_retryable"],
        )

    @classmethod
    def _determine_type(cls, exception: Exception, message: str) -> ErrorType:
        """Determine error type from exception and message."""
        message_lower = message.lower()

        # Check for specific exception types first
        if isinstance(exception, ValueError):
            return ErrorType.VALIDATION

        if isinstance(exception, MemoryError):
            return ErrorType.MEMORY

        if isinstance(exception, TimeoutError):
            return ErrorType.TIMEOUT

        if isinstance(exception, (ConnectionError, OSError)):
            # Check if it's a timeout-related OSError
            if any(
                re.search(pattern, message, re.IGNORECASE)
                for pattern in cls.TIMEOUT_PATTERNS
            ):
                return ErrorType.TIMEOUT
            return ErrorType.NETWORK

        # Pattern matching on message - check in priority order
        for pattern in cls.TIMEOUT_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return ErrorType.TIMEOUT

        for pattern in cls.MEMORY_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return ErrorType.MEMORY

        for pattern in cls.NETWORK_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return ErrorType.NETWORK

        for pattern in cls.MODEL_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return ErrorType.MODEL

        return ErrorType.UNKNOWN
