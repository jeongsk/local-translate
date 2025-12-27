# CLAUDE.md - AI Assistant Guide for LocalTranslate

This document provides comprehensive guidance for AI assistants working with the LocalTranslate codebase.

## Project Overview

**LocalTranslate** is a macOS desktop application for offline translation using the Yanolja NEXT Rosetta-4B model. It provides privacy-focused, local AI-powered translation with a native PySide6 GUI.

### Key Features
- Offline-first translation (no network required after model download)
- 10+ language support (Korean, English, Japanese, Chinese, Spanish, French, German, Russian, Portuguese, Italian)
- Apple Silicon MPS acceleration
- Native macOS dark/light mode support
- Manual translation via button click or `Cmd+Enter`

### System Requirements
- macOS 11.0+
- Python 3.11+ (project uses 3.12)
- 8GB+ RAM
- 10GB+ storage (for model)

---

## Project Structure

```
local-translate/
├── src/                      # Main source code
│   ├── main.py              # Application entry point
│   ├── core/                # Business logic layer
│   │   ├── config.py        # App configuration, language codes, model settings
│   │   ├── model_manager.py # Rosetta-4B model loading and inference
│   │   ├── translator.py    # Translation service with async execution
│   │   ├── language_detector.py  # Language auto-detection (lingua-py)
│   │   └── preferences.py   # User preferences persistence
│   ├── ui/                  # PySide6 UI components
│   │   ├── main_window.py   # Main application window
│   │   ├── splash_screen.py # Startup splash with progress
│   │   ├── language_selector.py  # Language dropdown widget
│   │   └── styles.py        # Theme management (dark/light)
│   ├── utils/               # Shared utilities
│   │   ├── logger.py        # Logging configuration
│   │   └── async_helpers.py # Qt thread pool workers
│   └── macos_platform/      # macOS-specific code (future)
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest fixtures and mocks
│   ├── fixtures/            # Test data
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── performance/         # Benchmark tests
├── specs/                   # Feature specifications
├── .github/workflows/       # CI/CD pipelines
│   ├── tests.yml            # Testing and quality checks
│   └── release.yml          # Build and release automation
├── pyproject.toml           # Project configuration and dependencies
├── pytest.ini               # Pytest configuration
├── LocalTranslate.spec      # PyInstaller build specification
└── build.sh                 # macOS app build script
```

---

## Development Setup

### Quick Start
```bash
# Clone and navigate to project
cd local-translate

# Install uv package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e ".[dev]"

# Run the application
python src/main.py
```

### Virtual Environment
The project expects a `.venv` directory for the virtual environment. The `.python-version` file specifies Python 3.12.

---

## Key Commands

### Running the Application
```bash
python src/main.py
# Or as a module:
python -m src.main
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run unit tests only
pytest tests/unit/

# Skip benchmarks
pytest --benchmark-skip

# Run specific test markers
pytest -m "unit"           # Unit tests
pytest -m "integration"    # Integration tests
pytest -m "performance"    # Performance benchmarks
pytest -m "not slow"       # Skip slow tests

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_translator.py
```

### Code Quality
```bash
# Format code (black)
black src/ tests/

# Lint code (ruff)
ruff check src/ tests/

# Auto-fix lint issues
ruff check --fix src/ tests/

# Type checking (mypy)
mypy src/

# Run all quality checks
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

### Building
```bash
# Build macOS app (requires .venv activated)
./build.sh

# Or manually with PyInstaller
pyinstaller --clean --noconfirm LocalTranslate.spec

# Output: dist/LocalTranslate.app
```

---

## Code Conventions

### Python Style
- **Line length**: 100 characters (configured in `pyproject.toml`)
- **Formatter**: Black with Python 3.11 target
- **Linter**: Ruff with E, W, F, I, B, C4, UP rules
- **Type hints**: Required for all function definitions (mypy strict mode)

### Import Order (enforced by ruff/isort)
1. Standard library
2. Third-party packages
3. Local imports

### Naming Conventions
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`
- Signals (Qt): `camelCase` (e.g., `translationComplete`)

### Qt/PySide6 Patterns
- Use `@Slot()` decorator for slot methods
- Connect signals in `_connect_signals()` method
- Use `QThread` and `QThreadPool` for background work
- Prefer signals over direct method calls for inter-component communication

### Logging
```python
from utils.logger import get_logger
logger = get_logger(__name__)

logger.info("Informational message")
logger.debug("Debug details")
logger.error("Error occurred", exc_info=True)
```

---

## Key Components

### TranslationService (`src/core/translator.py`)
- Manages translation requests with debouncing
- Emits signals: `translationStarted`, `translationProgress`, `translationComplete`, `translationError`
- Uses `QThreadPool` for async execution

### ModelManager (`src/core/model_manager.py`)
- Loads Yanolja NEXT Rosetta-4B model
- Handles device detection (MPS/CUDA/CPU)
- Supports INT8/INT4 quantization via `optimum-quanto`
- Progress callbacks for UI updates

### MainWindow (`src/ui/main_window.py`)
- Central UI component with source/target text areas
- Manual translation button (Cmd+Enter shortcut)
- Language selectors with auto-detect option
- Dark/light mode toggle

### Configuration (`src/core/config.py`)
- `LanguageCode` enum with ISO 639-1 codes
- `ModelConfig` for model settings
- `PerformanceConfig` for thresholds
- `AppConfig` global configuration singleton

---

## Testing Guidelines

### Test Structure
- Use pytest fixtures from `conftest.py`
- Mock heavy dependencies (ModelManager, LanguageDetector)
- Tests require `qapp` fixture for Qt components

### Key Fixtures
```python
@pytest.fixture
def mock_model_manager() -> Mock:
    """Mocked ModelManager for testing without loading actual model."""

@pytest.fixture
def mock_language_detector() -> Mock:
    """Mocked LanguageDetector for testing."""

@pytest.fixture
def qapp() -> QApplication:
    """Session-scoped QApplication for Qt tests."""
```

### Test Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Benchmark tests
- `@pytest.mark.slow` - Long-running tests

### Coverage Requirements
- Minimum 80% code coverage (configured in `pytest.ini`)
- Coverage reports generated in HTML format

---

## CI/CD Pipelines

### Tests Workflow (`.github/workflows/tests.yml`)
Triggered on: push to main/develop, pull requests

Jobs:
1. **test**: Runs on Python 3.11 and 3.12
   - Linting (ruff), formatting (black), type checking (mypy)
   - Test execution with coverage
2. **security**: Bandit security audit
3. **benchmark**: Performance tests on PRs

### Release Workflow (`.github/workflows/release.yml`)
Triggered on: version tags (`v*`) or manual dispatch

Jobs:
1. **build-macos**: Build macOS app with PyInstaller
2. **release**: Create GitHub release with ZIP and DMG

---

## Common Tasks for AI Assistants

### Adding a New Language
1. Add `LanguageCode` enum value in `src/core/config.py`
2. Add corresponding `Language` entry in `SUPPORTED_LANGUAGES` dict
3. Test language detection in `tests/`

### Modifying UI
1. Edit `src/ui/main_window.py` for main window changes
2. Update `src/ui/styles.py` for theme changes
3. Ensure dark/light mode compatibility

### Adding a Feature
1. Create specification in `specs/` directory
2. Implement in appropriate `src/` module
3. Add tests with proper markers
4. Run full quality check before committing

### Debugging Translation Issues
1. Check logs in `logs/translation.log`
2. Verify model loading in ModelManager
3. Check text length limits (max 2000 chars)
4. Verify language pair support

### Performance Optimization
1. Run benchmarks: `pytest tests/performance/ --benchmark-only`
2. Check memory usage via `ModelManager.get_memory_usage()`
3. Target: <2s for <500 chars, <5s for 500-2000 chars

---

## Important Files Reference

| File | Purpose |
|------|---------|
| `src/main.py` | Application entry point, initialization flow |
| `src/core/config.py` | All configuration and language definitions |
| `src/core/translator.py` | Translation service with Qt signals |
| `src/core/model_manager.py` | Model loading and inference |
| `src/ui/main_window.py` | Main window UI and event handling |
| `pyproject.toml` | Dependencies and tool configuration |
| `pytest.ini` | Test configuration and markers |
| `LocalTranslate.spec` | PyInstaller build specification |

---

## Dependencies Overview

### Core
- **PySide6**: Qt6 GUI framework
- **torch**: PyTorch for model inference
- **transformers**: Hugging Face model loading
- **accelerate**: Model optimization
- **optimum-quanto**: Quantization (INT8/INT4)
- **lingua-language-detector**: Language detection

### Development
- **pytest**: Testing framework
- **pytest-qt**: Qt testing support
- **pytest-cov**: Coverage reporting
- **pytest-benchmark**: Performance benchmarks
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking
- **pyinstaller**: macOS app packaging

---

## Notes for AI Assistants

1. **Model Loading**: The Rosetta-4B model is ~8GB. Tests use mocks to avoid loading.
2. **macOS Focus**: This is a macOS-specific app. UI uses native styling.
3. **Korean-centric**: Many UI strings are in Korean. Maintain bilingual approach.
4. **Manual Translation**: Translation is triggered by button/shortcut, not automatically on text change.
5. **Thread Safety**: Use Qt signals for cross-thread communication.
6. **Type Hints**: All new code must have type annotations.
7. **Test Coverage**: Maintain 80%+ coverage. Add tests for new features.

## Active Technologies
- Python 3.11+ (프로젝트는 3.12 사용) + PySide6 (Qt6 GUI), QSettings (영구 저장) (002-translation-history)
- QSettings (로컬 파일 시스템, `~/.config/LocalTranslate/` 또는 macOS plist) (002-translation-history)
- Python 3.11+ (프로젝트는 3.12 사용) + PySide6 6.5.0+, requests (HTTP 클라이언트) (003-about-update-menu)
- N/A (앱 메타데이터는 config.py에서 관리) (003-about-update-menu)

## Recent Changes
- 002-translation-history: Added Python 3.11+ (프로젝트는 3.12 사용) + PySide6 (Qt6 GUI), QSettings (영구 저장)
