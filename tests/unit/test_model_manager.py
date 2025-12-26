"""Unit tests for ModelManager."""

import pytest
from unittest.mock import Mock, MagicMock, patch

from src.core.model_manager import ModelManager
from src.core.config import ModelConfig


class TestModelManagerInit:
    """Tests for ModelManager initialization."""

    def test_init_with_default_config(self):
        """Test initialization with default config."""
        manager = ModelManager()

        assert manager.config is not None
        assert manager.model is None
        assert manager.tokenizer is None
        assert manager.device is None
        assert manager._is_loaded is False

    def test_init_with_custom_config(self):
        """Test initialization with custom config."""
        custom_config = ModelConfig(
            model_id="custom/model",
            device="cpu",
            quantization="int8",
        )
        manager = ModelManager(model_config=custom_config)

        assert manager.config.model_id == "custom/model"
        assert manager.config.device == "cpu"
        assert manager.config.quantization == "int8"

    def test_is_loaded_property_initially_false(self):
        """Test is_loaded property is False initially."""
        manager = ModelManager()

        assert manager.is_loaded is False


class TestModelManagerProgressCallback:
    """Tests for progress callback functionality."""

    def test_set_progress_callback(self):
        """Test setting progress callback."""
        manager = ModelManager()
        callback = Mock()

        manager.set_progress_callback(callback)

        assert manager._progress_callback == callback

    def test_report_progress_calls_callback(self):
        """Test _report_progress calls the callback."""
        manager = ModelManager()
        callback = Mock()
        manager.set_progress_callback(callback)

        manager._report_progress(50, "Test message")

        callback.assert_called_once_with(50, "Test message")

    def test_report_progress_without_callback(self):
        """Test _report_progress works without callback set."""
        manager = ModelManager()

        # Should not raise
        manager._report_progress(50, "Test message")


class TestModelManagerGetDevice:
    """Tests for _get_device method."""

    def test_get_device_returns_specified_device(self):
        """Test _get_device returns specified device when not auto."""
        config = ModelConfig(device="cpu")
        manager = ModelManager(model_config=config)

        result = manager._get_device()

        assert result == "cpu"

    @patch("torch.backends.mps.is_available", return_value=True)
    def test_get_device_returns_mps_when_available(self, mock_mps):
        """Test _get_device returns mps when available."""
        config = ModelConfig(device="auto")
        manager = ModelManager(model_config=config)

        result = manager._get_device()

        assert result == "mps"

    @patch("torch.backends.mps.is_available", return_value=False)
    @patch("torch.cuda.is_available", return_value=True)
    def test_get_device_returns_cuda_when_available(self, mock_cuda, mock_mps):
        """Test _get_device returns cuda when available."""
        config = ModelConfig(device="auto")
        manager = ModelManager(model_config=config)

        result = manager._get_device()

        assert result == "cuda"

    @patch("torch.backends.mps.is_available", return_value=False)
    @patch("torch.cuda.is_available", return_value=False)
    def test_get_device_returns_cpu_as_fallback(self, mock_cuda, mock_mps):
        """Test _get_device returns cpu as fallback."""
        config = ModelConfig(device="auto")
        manager = ModelManager(model_config=config)

        result = manager._get_device()

        assert result == "cpu"


class TestModelManagerTranslate:
    """Tests for translate method."""

    def test_translate_raises_when_model_not_loaded(self):
        """Test translate raises RuntimeError when model not loaded."""
        manager = ModelManager()

        with pytest.raises(RuntimeError, match="Model not loaded"):
            manager.translate("Hello")

    def test_translate_raises_for_empty_text(self):
        """Test translate raises ValueError for empty text."""
        manager = ModelManager()
        manager._is_loaded = True

        with pytest.raises(ValueError, match="Text cannot be empty"):
            manager.translate("")

    def test_translate_raises_for_whitespace_only(self):
        """Test translate raises ValueError for whitespace-only text."""
        manager = ModelManager()
        manager._is_loaded = True

        with pytest.raises(ValueError, match="Text cannot be empty"):
            manager.translate("   ")

    def test_translate_raises_for_too_long_text(self):
        """Test translate raises ValueError for text exceeding limit."""
        manager = ModelManager()
        manager._is_loaded = True

        long_text = "a" * 2001

        with pytest.raises(ValueError, match="Text too long"):
            manager.translate(long_text)

    def test_translate_accepts_max_length_text(self):
        """Test translate accepts text at max length (2000 chars)."""
        manager = ModelManager()
        manager._is_loaded = True

        # Mock model and tokenizer
        manager.model = MagicMock()
        manager.tokenizer = MagicMock()
        manager.tokenizer.apply_chat_template.return_value = "prompt"
        manager.tokenizer.return_value = {"input_ids": MagicMock(shape=[1, 10])}
        manager.model.generate.return_value = [[0] * 20]
        manager.tokenizer.decode.return_value = "Translation"

        max_text = "a" * 2000

        # Should not raise
        result = manager.translate(max_text)


class TestModelManagerUnload:
    """Tests for unload method."""

    def test_unload_clears_model(self):
        """Test unload clears model and tokenizer."""
        manager = ModelManager()
        manager.model = Mock()
        manager.tokenizer = Mock()
        manager._is_loaded = True
        manager.device = "cpu"

        manager.unload()

        assert manager.model is None
        assert manager.tokenizer is None
        assert manager._is_loaded is False

    def test_unload_when_no_model_loaded(self):
        """Test unload works when no model is loaded."""
        manager = ModelManager()

        # Should not raise
        manager.unload()

    @patch("torch.backends.mps.is_available", return_value=True)
    @patch("torch.mps.empty_cache")
    def test_unload_clears_mps_cache(self, mock_empty_cache, mock_is_available):
        """Test unload clears MPS cache."""
        manager = ModelManager()
        manager.model = Mock()
        manager.tokenizer = Mock()
        manager._is_loaded = True
        manager.device = "mps"

        manager.unload()

        mock_empty_cache.assert_called_once()

    @patch("torch.cuda.is_available", return_value=True)
    @patch("torch.cuda.empty_cache")
    def test_unload_clears_cuda_cache(self, mock_empty_cache, mock_is_available):
        """Test unload clears CUDA cache."""
        manager = ModelManager()
        manager.model = Mock()
        manager.tokenizer = Mock()
        manager._is_loaded = True
        manager.device = "cuda"

        manager.unload()

        mock_empty_cache.assert_called_once()


class TestModelManagerGetMemoryUsage:
    """Tests for get_memory_usage method."""

    def test_get_memory_usage_returns_dict(self):
        """Test get_memory_usage returns a dictionary."""
        manager = ModelManager()
        manager.device = "cpu"

        result = manager.get_memory_usage()

        assert isinstance(result, dict)
        assert "device" in result
        assert "is_loaded" in result

    def test_get_memory_usage_includes_device(self):
        """Test get_memory_usage includes device info."""
        manager = ModelManager()
        manager.device = "cpu"

        result = manager.get_memory_usage()

        assert result["device"] == "cpu"

    def test_get_memory_usage_includes_is_loaded(self):
        """Test get_memory_usage includes is_loaded status."""
        manager = ModelManager()
        manager.device = "cpu"
        manager._is_loaded = True

        result = manager.get_memory_usage()

        assert result["is_loaded"] is True


class TestModelManagerInitialize:
    """Tests for initialize method (integration-like tests with mocks)."""

    @patch("src.core.model_manager.AutoTokenizer")
    @patch("src.core.model_manager.AutoModelForCausalLM")
    @patch("torch.backends.mps.is_available", return_value=False)
    @patch("torch.cuda.is_available", return_value=False)
    def test_initialize_success(
        self, mock_cuda, mock_mps, mock_model_class, mock_tokenizer_class
    ):
        """Test successful initialization."""
        manager = ModelManager()
        mock_tokenizer_class.from_pretrained.return_value = Mock()
        mock_model_class.from_pretrained.return_value = Mock()

        result = manager.initialize()

        assert result is True
        assert manager._is_loaded is True
        assert manager.device == "cpu"

    @patch("src.core.model_manager.AutoTokenizer")
    def test_initialize_failure_raises_runtime_error(self, mock_tokenizer_class):
        """Test that initialization failure raises RuntimeError."""
        manager = ModelManager()
        mock_tokenizer_class.from_pretrained.side_effect = Exception("Load failed")

        with pytest.raises(RuntimeError, match="Failed to load translation model"):
            manager.initialize()

        assert manager._is_loaded is False

    @patch("src.core.model_manager.AutoTokenizer")
    @patch("src.core.model_manager.AutoModelForCausalLM")
    @patch("torch.backends.mps.is_available", return_value=False)
    @patch("torch.cuda.is_available", return_value=False)
    def test_initialize_reports_progress(
        self, mock_cuda, mock_mps, mock_model_class, mock_tokenizer_class
    ):
        """Test that initialize reports progress."""
        manager = ModelManager()
        callback = Mock()
        manager.set_progress_callback(callback)

        mock_tokenizer_class.from_pretrained.return_value = Mock()
        mock_model_class.from_pretrained.return_value = Mock()

        manager.initialize()

        # Should have called progress multiple times
        assert callback.call_count >= 5
