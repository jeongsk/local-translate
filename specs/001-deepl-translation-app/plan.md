# Implementation Plan: DeepL-Like Translation Application

**Branch**: `001-deepl-translation-app` | **Date**: 2025-12-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-deepl-translation-app/spec.md`

## Summary

로컬 환경에서 동작하는 번역 애플리케이션 구축. Yanolja NEXT Rosetta-4B 모델을 사용하여 오프라인 번역 기능을 제공하며, PySide6 기반의 사용자 친화적인 GUI를 통해 빠르고 정확한 번역 서비스를 제공합니다.

**핵심 기능**:
- 텍스트 입력 시 자동 언어 감지 및 번역
- 최소 10개 언어 지원 (한국어, 영어, 일본어, 중국어, 스페인어, 프랑스어, 독일어, 러시아어, 포르투갈어, 이탈리아어)
- 500자 미만 텍스트 2초 이내 번역, 500-2000자 텍스트 5초 이내 번역
- 사용자 설정 영속화 (언어 선호도, 윈도우 크기/위치)
- macOS 다크/라이트 모드 지원

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- UI Framework: PySide6 (Qt for Python)
- ML Framework: PyTorch 2.0+, Transformers (Hugging Face)
- Translation Model: yanolja/YanoljaNEXT-Rosetta-4B
- Package Manager: uv

**Storage**:
- Local JSON files for user preferences (language settings, window state)
- Model cache: Hugging Face transformers cache (~8GB for Rosetta-4B model)

**Testing**:
- pytest for unit and integration tests
- pytest-qt for PySide6 UI testing
- pytest-benchmark for performance regression tests

**Target Platform**: macOS 11.0+
**Project Type**: Desktop application (single project structure)

**Performance Goals**:
- Translation latency: <2s (p95) for <500 chars, <5s (p95) for 500-2000 chars
- App startup: <3s to show UI (model loading in background)
- Memory usage: <500MB during normal operation
- UI responsiveness: 60 FPS, non-blocking async operations

**Constraints**:
- Offline-first: All core functionality must work without network
- GPU acceleration via MPS (Metal Performance Shaders) on Apple Silicon
- Model must fit in memory: requires 8GB RAM minimum
- UI must remain responsive during translation (async task execution)

**Scale/Scope**:
- Single-user desktop application
- Support 10+ languages initially
- Handle up to 2000 characters per translation request
- Model size: ~4B parameters, ~8GB disk space

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality (NON-NEGOTIABLE)

**Status**: ✅ **PASS** - Design adheres to constitution requirements

- ✅ Python code will follow PEP 8 style guidelines (enforced via black + ruff)
- ✅ Type hints will be used for all public functions and class methods
- ✅ Code complexity minimized - separation of concerns enforced (UI / Core / Platform layers)
- ✅ DRY principle enforced - no duplicate code allowed
- ✅ Clear layer separation: `src/ui/` (PySide6), `src/core/` (business logic), `src/macos_platform/` (macOS-specific)

### II. Testing Standards (NON-NEGOTIABLE)

**Status**: ✅ **PASS** - Comprehensive testing strategy planned

- ✅ Unit tests for all business logic in `src/core/`
- ✅ Integration tests for UI-to-model interactions
- ✅ Test coverage target: >80% for core translation functionality
- ✅ Performance regression tests for translation speed benchmarks
- ✅ Mock translation models in unit tests to avoid heavy model loading
- ✅ Test structure: `tests/unit/`, `tests/integration/`, `tests/contract/`

### III. User Experience Consistency (NON-NEGOTIABLE)

**Status**: ✅ **PASS** - macOS HIG compliance and UX requirements met

- ✅ All UI components follow macOS Human Interface Guidelines
- ✅ Translation results within 2s for <500 chars (FR-005)
- ✅ Error messages user-friendly and actionable (FR-012)
- ✅ UI state persistence across restarts (FR-009, FR-010)
- ✅ Keyboard shortcuts consistent and discoverable (FR-014)
- ✅ Accessibility supported: VoiceOver compatibility (FR-015)
- ✅ Dark/light mode fully supported (FR-013)
- ✅ Loading states clearly indicated (FR-007)

### IV. Performance Requirements (NON-NEGOTIABLE)

**Status**: ✅ **PASS** - Performance targets aligned with spec

- ✅ Translation latency: <2s (p95) for <500 chars (FR-005, SC-001)
- ✅ Translation latency: <5s (p95) for 500-2000 chars (FR-006, SC-002)
- ✅ App startup: <3s (FR-011, SC-003)
- ✅ Memory usage: <500MB (SC-004)
- ✅ Model loading: <10s with progress indicator (FR-011)
- ✅ UI responsiveness: non-blocking async operations (FR-016)
- ✅ Performance metrics logged and reviewable
- ✅ Regression tests fail if latency exceeds thresholds by >10%

**Constitution Re-evaluation Required After**: Phase 1 design completion

## Project Structure

### Documentation (this feature)

```text
specs/001-deepl-translation-app/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - technology research and decisions
├── data-model.md        # Phase 1 output - entity and state model design
├── quickstart.md        # Phase 1 output - developer onboarding guide
├── contracts/           # Phase 1 output - API contracts (if applicable)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
open-deepl/
├── src/
│   ├── core/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── translator.py        # Translation service (model wrapper)
│   │   ├── language_detector.py # Auto language detection
│   │   └── preferences.py       # User preferences persistence
│   │
│   ├── ui/                      # PySide6 UI components
│   │   ├── __init__.py
│   │   ├── main_window.py       # Main translation window
│   │   ├── splash_screen.py     # Startup splash with model loading
│   │   ├── language_selector.py # Language dropdown components
│   │   ├── text_editor.py       # Custom text input/output widgets
│   │   └── styles.py            # Dark/light mode styling
│   │
│   ├── macos_platform/          # macOS-specific integrations
│   │   ├── __init__.py
│   │   ├── appearance.py        # Dark/light mode detection
│   │   └── accessibility.py     # VoiceOver support utilities
│   │
│   ├── utils/                   # Shared utilities
│   │   ├── __init__.py
│   │   ├── logger.py            # Logging configuration
│   │   └── async_helpers.py     # Async task management utilities
│   │
│   └── main.py                  # Application entry point
│
├── tests/
│   ├── unit/                    # Isolated component tests
│   │   ├── test_translator.py
│   │   ├── test_language_detector.py
│   │   └── test_preferences.py
│   │
│   ├── integration/             # End-to-end workflow tests
│   │   ├── test_translation_flow.py
│   │   └── test_ui_integration.py
│   │
│   └── contract/                # Model API contract tests
│       └── test_model_api.py
│
├── resources/                   # Application resources
│   ├── icons/                   # App icons for different sizes
│   └── translations/            # UI text localizations (if needed)
│
├── pyproject.toml               # Project configuration (uv)
├── .python-version              # Python version specification
├── README.md                    # Project documentation
└── .gitignore                   # Git ignore rules
```

**Structure Decision**: Single project structure chosen because this is a desktop application with all components tightly integrated. The three-layer architecture (UI / Core / Platform) provides clear separation of concerns while maintaining simplicity. No need for separate backend/frontend projects as all logic runs in the same process.

## Complexity Tracking

> **No violations - this section intentionally left empty**

All constitution requirements are satisfied by the planned design. No complexity justifications needed.

---

## Phase 0: Outline & Research

### Research Questions to Address

Based on the Technical Context, the following areas require research to make informed implementation decisions:

#### 1. Translation Model Integration
**Question**: How to efficiently load and manage the Yanolja NEXT Rosetta-4B model in a desktop application?
- Model loading strategies: lazy loading vs. eager loading
- Memory management for 4B parameter model
- GPU acceleration via MPS on Apple Silicon
- Model quantization options for reduced memory footprint

#### 2. Language Detection
**Question**: What library/approach is best for automatic language detection in offline mode?
- Options: langdetect, lingua-py, fasttext, or model-based detection
- Accuracy requirements: >85% for 10 major languages
- Performance: must not add >100ms latency
- Offline capability essential

#### 3. Asynchronous Translation Execution
**Question**: How to implement non-blocking translation in PySide6 to maintain UI responsiveness?
- QThread vs. asyncio vs. concurrent.futures
- Progress reporting during translation
- Cancellation support for debouncing (when user modifies text rapidly)
- Error handling and retry strategies

#### 4. User Preferences Persistence
**Question**: What's the best approach for storing user settings on macOS?
- Options: JSON files, QSettings, macOS UserDefaults via PyObjC
- Data to persist: language preferences, window geometry, theme preference
- Migration strategy for future schema changes

#### 5. PySide6 Dark/Light Mode Support
**Question**: How to implement robust dark/light mode switching that follows macOS system appearance?
- QStyleSheet approach vs. QPalette
- Detecting system appearance changes
- Custom widget styling for both modes
- Testing strategy for visual consistency

#### 6. Performance Benchmarking
**Question**: How to implement automated performance testing for translation latency?
- pytest-benchmark integration
- Realistic test data generation
- CI/CD integration for regression detection
- Profiling tools for identifying bottlenecks

### Research Deliverables

The `research.md` document will contain:
- **Decision**: Chosen approach for each research question
- **Rationale**: Why this approach was selected
- **Alternatives considered**: What other options were evaluated and why they were rejected
- **Implementation notes**: Key technical details, gotchas, and best practices
- **References**: Links to documentation, benchmarks, and example code

---

## Phase 1: Design & Contracts

### Prerequisites
- `research.md` complete with all research questions resolved
- All "NEEDS CLARIFICATION" items from Technical Context addressed

### Phase 1 Deliverables

#### 1. Data Model Design (`data-model.md`)

Will extract and formalize the following entities from the feature spec:

**Core Entities**:
- **TranslationRequest**: Request data model
  - Fields: source_text, source_language, target_language, timestamp, request_id
  - Validation: max 2000 chars, non-empty text, valid language codes
  - Relationships: one-to-one with TranslationResult

- **TranslationResult**: Result data model
  - Fields: translated_text, completion_time, model_info, request_id
  - Validation: non-empty translated text
  - State transitions: pending → in_progress → completed/failed

- **UserPreferences**: Settings data model
  - Fields: default_source_language, default_target_language, window_geometry, theme
  - Validation: valid language codes, valid JSON schema
  - Persistence: JSON file in user's application support directory

- **Language**: Supported language model
  - Fields: code (ISO 639-1), name, display_name, is_supported
  - Validation: valid ISO codes
  - Static data: 10+ languages from FR-002

- **TranslationModel**: Model metadata
  - Fields: model_id, version, loading_state, memory_usage, device
  - State transitions: unloaded → loading → loaded → error
  - Singleton: only one model loaded at a time

#### 2. API Contracts (`contracts/`)

Since this is a desktop application with no REST/GraphQL API, the "contracts" will be:
- **Internal Python API contracts**: Type-annotated interfaces between layers
- **UI Event Contracts**: Signals/slots definitions for Qt events
- **Model Inference Contract**: Expected input/output format for translation model

Example contract files:
- `contracts/translator_interface.py`: Type protocol for translation service
- `contracts/ui_events.py`: Signal/slot type definitions
- `contracts/model_api.json`: Model inference schema (input messages format, expected output format)

#### 3. Developer Quickstart (`quickstart.md`)

Will provide:
- Environment setup instructions (Python version, uv installation)
- Model download and cache setup
- Running the application locally
- Running tests
- Code organization overview
- Common development tasks (adding a language, modifying UI)

#### 4. Agent Context Update

Execute `.specify/scripts/bash/update-agent-context.sh claude` to:
- Add PySide6 development patterns to Claude's context
- Add PyTorch/Transformers model loading patterns
- Preserve any manual additions in agent-specific context files

---

## Phase 2: Task Generation

**NOT EXECUTED BY THIS COMMAND** - Use `/speckit.tasks` command after Phase 1 completion.

The tasks.md will break down implementation into:
- **P0 Tasks**: Model loading, basic translation, simple UI
- **P1 Tasks**: Language selection, auto-detection, debouncing
- **P2 Tasks**: Clipboard copy, keyboard shortcuts, error handling
- **P3 Tasks**: Preferences persistence, window state, dark mode
- **P4 Tasks**: Performance optimization, accessibility, polish

Each task will include:
- Clear acceptance criteria
- Estimated complexity
- Dependencies on other tasks
- Test requirements

---

## Next Steps

1. ✅ **Phase 0**: Generate `research.md` addressing all research questions
2. ⏳ **Phase 1**: Generate `data-model.md`, `contracts/`, `quickstart.md`
3. ⏳ **Constitution Re-check**: Verify design adheres to all gates
4. ⏳ **Phase 2**: Execute `/speckit.tasks` to generate actionable task breakdown

**Implementation will begin after** `/speckit.tasks` completion and user approval of the generated task plan.
