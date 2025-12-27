"""Model manager for loading and managing the Rosetta-4B translation model."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, QuantoConfig
from typing import Optional, Callable
from pathlib import Path

from utils.logger import get_logger
from core.config import ModelConfig, config

logger = get_logger(__name__)


class ModelManager:
    """Manages the Rosetta-4B translation model with lazy loading and quantization."""

    def __init__(self, model_config: Optional[ModelConfig] = None):
        """
        Initialize model manager.

        Args:
            model_config: Model configuration. Uses default if not provided.
        """
        self.config = model_config or config.model
        self.model = None
        self.tokenizer = None
        self.device = None
        self._is_loaded = False
        self._progress_callback: Optional[Callable[[int, str], None]] = None

        logger.info(f"ModelManager initialized with model: {self.config.model_id}")

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded

    def set_progress_callback(self, callback: Callable[[int, str], None]) -> None:
        """
        Set progress callback for model loading.

        Args:
            callback: Function(percentage: int, message: str) called during loading
        """
        self._progress_callback = callback

    def _report_progress(self, percentage: int, message: str) -> None:
        """
        Report loading progress.

        Args:
            percentage: Progress percentage (0-100)
            message: Status message
        """
        logger.info(f"Model loading: {percentage}% - {message}")
        if self._progress_callback:
            self._progress_callback(percentage, message)

    def initialize(self) -> bool:
        """
        Initialize and load the model with INT8 quantization.

        Returns:
            True if successful, False otherwise

        Raises:
            RuntimeError: If model loading fails
        """
        try:
            logger.info("Starting model initialization...")
            self._report_progress(10, "Checking device availability...")

            # Step 1: Determine device
            self.device = self._get_device()
            logger.info(f"Using device: {self.device}")

            self._report_progress(20, "Loading tokenizer...")

            # Step 2: Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_id)
            logger.info("Tokenizer loaded successfully")

            self._report_progress(30, "Configuring model quantization...")

            # Step 3: Configure quantization
            quantization_config = None
            if self.config.quantization == "int8":
                quantization_config = QuantoConfig(weights="int8", activations=None)
                logger.info("INT8 quantization enabled")
            elif self.config.quantization == "int4":
                quantization_config = QuantoConfig(weights="int4", activations=None)
                logger.info("INT4 quantization enabled")

            self._report_progress(40, "Loading model (this may take a while)...")

            # Step 4: Load model with lazy loading
            dtype = getattr(torch, self.config.dtype)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_id,
                quantization_config=quantization_config,
                device_map="auto" if self.config.device == "auto" else self.device,
                low_cpu_mem_usage=True,
                torch_dtype=dtype,
            )

            logger.info(f"Model loaded on device: {self.model.device}")
            self._report_progress(90, "Finalizing model setup...")

            # Step 5: Set to evaluation mode
            self.model.eval()

            self._is_loaded = True
            self._report_progress(100, "Model ready!")

            logger.info(
                f"Model initialization complete. Device: {self.device}, "
                f"Quantization: {self.config.quantization}"
            )
            return True

        except Exception as e:
            logger.error(f"Model initialization failed: {e}", exc_info=True)
            self._is_loaded = False
            raise RuntimeError(f"Failed to load translation model: {e}") from e

    def _get_device(self) -> str:
        """
        Determine the best available device.

        Returns:
            Device string (mps, cuda, or cpu)
        """
        if self.config.device != "auto":
            return self.config.device

        # Check for MPS (Apple Silicon)
        if torch.backends.mps.is_available():
            logger.info("MPS (Apple Silicon GPU) detected")
            return "mps"

        # Check for CUDA
        if torch.cuda.is_available():
            logger.info("CUDA GPU detected")
            return "cuda"

        # Fallback to CPU
        logger.info("No GPU detected, using CPU")
        return "cpu"

    def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "Korean",
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> str:
        """
        Translate text using the model.

        Args:
            text: Text to translate
            source_lang: Source language (not used, auto-detected by model)
            target_lang: Target language name
            progress_callback: Optional progress callback

        Returns:
            Translated text

        Raises:
            RuntimeError: If model is not loaded
            ValueError: If text is empty or too long
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call initialize() first.")

        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if len(text) > 2000:
            raise ValueError(f"Text too long: {len(text)} chars (max 2000)")

        try:
            if progress_callback:
                progress_callback(10, "Preparing translation...")

            # Prepare messages for chat template
            messages = [
                {
                    "role": "system",
                    "content": (
                        f"Translate the user's text to {target_lang}. "
                        "Output only one sentence of the final translation. "
                        "Do not print explanations, thought processes, or examples."
                    ),
                },
                {"role": "user", "content": text},
            ]

            # Apply chat template
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )

            if progress_callback:
                progress_callback(30, "Tokenizing input...")

            # Tokenize
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            input_length = inputs["input_ids"].shape[1]

            if progress_callback:
                progress_callback(50, "Translating...")

            # Generate translation
            # 입력 길이에 비례한 동적 max_new_tokens (최소 50, 최대 config값)
            dynamic_max_tokens = max(50, min(input_length * 3, self.config.max_new_tokens))

            with torch.inference_mode():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=dynamic_max_tokens,
                    do_sample=False,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=self.config.repetition_penalty,
                    no_repeat_ngram_size=self.config.no_repeat_ngram_size,
                )

            if progress_callback:
                progress_callback(90, "Decoding output...")

            # Extract and decode translation
            generated_tokens = outputs[0][input_length:]
            translation = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

            if progress_callback:
                progress_callback(100, "Translation complete!")

            logger.debug(f"Translation: '{text[:50]}...' -> '{translation[:50]}...'")
            return translation.strip()

        except Exception as e:
            logger.error(f"Translation failed: {e}", exc_info=True)
            raise RuntimeError(f"Translation error: {e}") from e

    def unload(self) -> None:
        """Unload model and free memory."""
        if self.model is not None:
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None

            # Clear device cache
            if self.device == "mps" and torch.backends.mps.is_available():
                torch.mps.empty_cache()
            elif self.device == "cuda" and torch.cuda.is_available():
                torch.cuda.empty_cache()

            self._is_loaded = False
            logger.info("Model unloaded and memory cleared")

    def get_memory_usage(self) -> dict:
        """
        Get current memory usage statistics.

        Returns:
            Dictionary with memory usage info
        """
        stats = {"device": self.device, "is_loaded": self._is_loaded}

        if self.device == "mps" and torch.backends.mps.is_available():
            try:
                stats["allocated_mb"] = torch.mps.current_allocated_memory() / 1024**2
            except (AttributeError, RuntimeError) as e:
                logger.debug(f"MPS memory stats unavailable: {e}")
                stats["allocated_mb"] = 0
        elif self.device == "cuda" and torch.cuda.is_available():
            stats["allocated_mb"] = torch.cuda.memory_allocated() / 1024**2
            stats["reserved_mb"] = torch.cuda.memory_reserved() / 1024**2

        return stats
