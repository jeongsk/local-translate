"""Test data generator for translation tests."""

import random
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class TranslationSample:
    """Sample translation data for testing."""

    source_text: str
    source_lang: str
    target_lang: str
    expected_contains: List[str]  # Keywords expected in translation
    category: str


class TranslationDataGenerator:
    """Generate diverse test data for translation benchmarks."""

    # Sample texts by category
    TECHNICAL = [
        "Machine learning models require significant computational resources.",
        "The API endpoint returns a JSON response with authentication tokens.",
        "Database indexing improves query performance by orders of magnitude.",
        "PyTorch is a machine learning framework based on the Torch library.",
        "The function implements lazy loading with memory optimization.",
    ]

    CASUAL = [
        "Hey! How are you doing today?",
        "Thanks for your help, I really appreciate it!",
        "Let's grab coffee sometime next week.",
        "Good morning! Hope you have a great day.",
        "See you later! Take care.",
    ]

    BUSINESS = [
        "Please review the quarterly financial report by end of day.",
        "Our customer satisfaction scores have improved by 15% this quarter.",
        "The project deadline has been extended to next month.",
        "We need to schedule a meeting to discuss the new initiative.",
        "Thank you for your continued partnership and support.",
    ]

    MIXED = [
        "The ML model achieved 95% accuracy on the test set! 🎉",
        "Can you send me the API docs? I need to integrate by tomorrow.",
        "Our system handles 1M requests/day with 99.9% uptime.",
        "Check out this cool feature: real-time collaboration! 🚀",
        "The server crashed again... need to debug ASAP 😓",
    ]

    KOREAN = [
        "안녕하세요! 오늘 날씨가 정말 좋네요.",
        "회의는 내일 오전 10시에 시작합니다.",
        "이 프로젝트는 다음 주까지 완료해야 합니다.",
        "점심 식사 같이 하실래요?",
        "고맙습니다! 좋은 하루 보내세요.",
    ]

    @staticmethod
    def generate_batch(category: str, count: int = 10) -> List[str]:
        """
        Generate a batch of test strings from a category.

        Args:
            category: Category name (technical, casual, business, mixed, korean)
            count: Number of samples to generate

        Returns:
            List of test strings
        """
        category_map = {
            "technical": TranslationDataGenerator.TECHNICAL,
            "casual": TranslationDataGenerator.CASUAL,
            "business": TranslationDataGenerator.BUSINESS,
            "mixed": TranslationDataGenerator.MIXED,
            "korean": TranslationDataGenerator.KOREAN,
        }

        base_texts = category_map.get(category.lower(), TranslationDataGenerator.CASUAL)
        return random.choices(base_texts, k=count)

    @staticmethod
    def generate_length_varied(min_words: int, max_words: int) -> str:
        """
        Generate text with specific word count.

        Args:
            min_words: Minimum word count
            max_words: Maximum word count

        Returns:
            Generated text string
        """
        words = [
            "test",
            "data",
            "translation",
            "benchmark",
            "performance",
            "quality",
            "accuracy",
            "speed",
            "latency",
            "throughput",
        ]
        word_count = random.randint(min_words, max_words)
        return " ".join(random.choices(words, k=word_count))

    @staticmethod
    def generate_by_char_count(target_chars: int, variance: int = 50) -> str:
        """
        Generate text with approximate character count.

        Args:
            target_chars: Target character count
            variance: Allowed variance in character count

        Returns:
            Generated text with target length
        """
        base_text = "The quick brown fox jumps over the lazy dog. "
        repetitions = (target_chars // len(base_text)) + 1
        text = base_text * repetitions

        # Trim to target length (with variance)
        actual_target = target_chars + random.randint(-variance, variance)
        return text[:actual_target]

    @staticmethod
    def generate_real_world_samples() -> Dict[str, List[TranslationSample]]:
        """
        Generate real-world test scenarios.

        Returns:
            Dictionary of test scenarios
        """
        return {
            "user_input": [
                TranslationSample(
                    source_text="How do I reset my password?",
                    source_lang="en",
                    target_lang="ko",
                    expected_contains=["비밀번호", "재설정"],
                    category="user_query",
                ),
                TranslationSample(
                    source_text="What's the weather like today?",
                    source_lang="en",
                    target_lang="ko",
                    expected_contains=["날씨", "오늘"],
                    category="user_query",
                ),
                TranslationSample(
                    source_text="Translate this to Korean please",
                    source_lang="en",
                    target_lang="ko",
                    expected_contains=["번역", "한국어"],
                    category="user_query",
                ),
            ],
            "document_snippets": [
                TranslationSample(
                    source_text="Chapter 1: Introduction to Machine Learning. In this chapter, we explore the fundamental concepts and principles.",
                    source_lang="en",
                    target_lang="ko",
                    expected_contains=["장", "소개", "기계", "학습"],
                    category="document",
                ),
                TranslationSample(
                    source_text="Product Description: High-performance laptop with 16GB RAM and 512GB SSD.",
                    source_lang="en",
                    target_lang="ko",
                    expected_contains=["제품", "노트북", "RAM", "SSD"],
                    category="document",
                ),
            ],
            "code_comments": [
                TranslationSample(
                    source_text="TODO: Optimize this function for better performance",
                    source_lang="en",
                    target_lang="ko",
                    expected_contains=["최적화", "성능"],
                    category="code",
                ),
                TranslationSample(
                    source_text="Initialize the translation model with default parameters",
                    source_lang="en",
                    target_lang="ko",
                    expected_contains=["초기화", "번역", "모델"],
                    category="code",
                ),
            ],
        }

    @staticmethod
    def generate_edge_cases() -> List[TranslationSample]:
        """
        Generate edge case test data.

        Returns:
            List of edge case samples
        """
        return [
            TranslationSample(
                source_text="",
                source_lang="en",
                target_lang="ko",
                expected_contains=[],
                category="edge_empty",
            ),
            TranslationSample(
                source_text="   ",
                source_lang="en",
                target_lang="ko",
                expected_contains=[],
                category="edge_whitespace",
            ),
            TranslationSample(
                source_text="a",
                source_lang="en",
                target_lang="ko",
                expected_contains=[],
                category="edge_single_char",
            ),
            TranslationSample(
                source_text="Hello 안녕 Bonjour",
                source_lang="auto",
                target_lang="ko",
                expected_contains=[],
                category="edge_mixed_languages",
            ),
            TranslationSample(
                source_text="😀 🎉 🚀 ❤️",
                source_lang="en",
                target_lang="ko",
                expected_contains=["😀", "🎉"],
                category="edge_emoji_only",
            ),
            TranslationSample(
                source_text="import torch\nprint('Hello World')",
                source_lang="en",
                target_lang="ko",
                expected_contains=["import", "torch"],
                category="edge_code",
            ),
        ]

    @staticmethod
    def generate_performance_test_data() -> Dict[str, List[str]]:
        """
        Generate data specifically for performance benchmarks.

        Returns:
            Dictionary with test data organized by size
        """
        return {
            "short": [
                TranslationDataGenerator.generate_by_char_count(100),
                TranslationDataGenerator.generate_by_char_count(200),
                TranslationDataGenerator.generate_by_char_count(400),
            ],
            "medium": [
                TranslationDataGenerator.generate_by_char_count(600),
                TranslationDataGenerator.generate_by_char_count(1000),
                TranslationDataGenerator.generate_by_char_count(1500),
            ],
            "long": [
                TranslationDataGenerator.generate_by_char_count(2000),
                TranslationDataGenerator.generate_by_char_count(2500),
                TranslationDataGenerator.generate_by_char_count(3000),
            ],
        }


# Convenience function for quick access
def get_test_data() -> TranslationDataGenerator:
    """
    Get test data generator instance.

    Returns:
        TranslationDataGenerator instance
    """
    return TranslationDataGenerator()
