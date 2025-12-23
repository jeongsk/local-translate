# Tasks: DeepL-Like Translation Application

**Input**: Design documents from `/specs/001-deepl-translation-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Constitution requires >80% test coverage. Unit and integration tests are REQUIRED for all core functionality.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Project uses three-layer architecture: `src/core/`, `src/ui/`, `src/macos_platform/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure (src/core/, src/ui/, src/macos_platform/, src/utils/, tests/unit/, tests/integration/, tests/contract/, resources/)
- [X] T002 Initialize Python project with uv (create pyproject.toml with Python 3.11+ and dependencies: PySide6, torch, transformers, accelerate, optimum-quanto, lingua-language-detector, pytest, pytest-qt, pytest-benchmark, black, ruff, mypy)
- [X] T003 [P] Create .python-version file specifying Python 3.11
- [X] T004 [P] Create .gitignore for Python project (include .benchmarks/, profiling/, __pycache__, *.pyc, .pytest_cache, models/, .DS_Store)
- [X] T005 [P] Configure black formatter in pyproject.toml
- [X] T006 [P] Configure ruff linter in pyproject.toml
- [X] T007 [P] Configure mypy type checker in pyproject.toml
- [X] T008 [P] Configure pytest in pytest.ini with benchmark settings
- [X] T009 [P] Create README.md with project overview and setup instructions
- [X] T010 Create src/__init__.py, src/core/__init__.py, src/ui/__init__.py, src/macos_platform/__init__.py, src/utils/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 [P] Implement logger configuration in src/utils/logger.py (structured logging with rotation, debug/info/warning/error levels)
- [X] T012 [P] Implement configuration management in src/core/config.py (model settings, supported languages, performance thresholds)
- [X] T013 [P] Create Language entity/enum in src/core/config.py (ISO 639-1 codes for Korean, English, Japanese, Chinese, Spanish, French, German, Russian, Portuguese, Italian with display names)
- [X] T014 Implement async task helpers in src/utils/async_helpers.py (QRunnable worker base class, signal definitions)
- [X] T015 Implement UserPreferences with QSettings in src/core/preferences.py (language preferences, window geometry, theme persistence)
- [X] T016 [P] Create pytest fixtures for mocked translator in tests/conftest.py
- [X] T017 [P] Create test data generator in tests/fixtures/translation_data.py (various text lengths and languages)
- [X] T018 Setup GitHub Actions workflow for CI in .github/workflows/tests.yml (run tests, linting, type checking)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Quick Text Translation (Priority: P1) 🎯 MVP

**Goal**: Users can input text and get translation results within 2 seconds for text under 500 characters

**Independent Test**: Run app, input "Hello World" in source text box, verify Korean translation "안녕하세요" appears in result box within 2 seconds

### Unit Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T019 [P] [US1] Unit test for ModelManager initialization in tests/unit/test_model_manager.py (test lazy loading, MPS device detection, model loading with INT8 quantization)
- [ ] T020 [P] [US1] Unit test for Translator service in tests/unit/test_translator.py (test translation with mocked model, input validation, timeout handling)
- [ ] T021 [P] [US1] Unit test for LanguageDetector in tests/unit/test_language_detector.py (test detection accuracy for supported languages, edge cases)

### Integration Tests for User Story 1

- [ ] T022 [US1] Integration test for basic translation flow in tests/integration/test_translation_flow.py (end-to-end: text input → detection → translation → result display)
- [ ] T023 [US1] Integration test for UI responsiveness in tests/integration/test_ui_integration.py (verify UI doesn't freeze during translation)

### Performance Tests for User Story 1

- [ ] T024 [P] [US1] Benchmark test for short text translation (<500 chars) in tests/performance/test_translation_latency.py (pytest-benchmark, verify <2s threshold, fail if >10% regression)
- [ ] T025 [P] [US1] Benchmark test for medium text translation (500-2000 chars) in tests/performance/test_translation_latency.py (verify <5s threshold)
- [ ] T026 [P] [US1] Memory usage test in tests/performance/test_memory_usage.py (verify <500MB during normal operation)

### Implementation for User Story 1

- [X] T027 [P] [US1] Implement ModelManager for Rosetta-4B model loading in src/core/model_manager.py (lazy loading with low_cpu_mem_usage, INT8 quantization via optimum-quanto, MPS device support, progress callbacks)
- [X] T028 [P] [US1] Implement LanguageDetector using lingua-py in src/core/language_detector.py (load 10 supported languages, detect with confidence scores, handle short texts)
- [X] T029 [US1] Implement TranslationService in src/core/translator.py (integrate ModelManager and LanguageDetector, QThreadPool worker for async translation, debouncing with QTimer 500ms, cancellation support, error handling)
- [X] T030 [US1] Implement WorkerSignals and TranslationWorker QRunnable in src/utils/async_helpers.py (started, progress, result, error, finished signals)
- [X] T031 [US1] Implement ThemeManager in src/ui/styles.py (QPalette for dark/light mode, detect macOS system appearance, apply custom QStyleSheet for specific widgets)
- [X] T032 [US1] Implement MainWindow UI in src/ui/main_window.py (source text input QTextEdit, target text output QTextEdit, progress bar, status label, connect to TranslationService signals)
- [X] T033 [US1] Implement SplashScreen for model loading in src/ui/splash_screen.py (display during model initialization, show progress, close when model loaded or on error)
- [X] T034 [US1] Implement application entry point in src/main.py (QApplication setup, ThemeManager initialization, ModelManager background loading with SplashScreen, MainWindow creation)
- [X] T035 [US1] Add error handling and user-friendly error messages in src/ui/main_window.py (model loading failures, translation errors, network timeouts)
- [X] T036 [US1] Add logging for translation operations in src/core/translator.py (request ID, input length, detected language, translation time, errors)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can translate text with auto language detection.

---

## Phase 4: User Story 2 - Language Selection and Detection (Priority: P2)

**Goal**: Users can manually select source and target languages, or use auto-detection

**Independent Test**: Select "English" from source dropdown, "Japanese" from target dropdown, input "Good morning", verify Japanese translation appears

### Unit Tests for User Story 2

- [ ] T037 [P] [US2] Unit test for LanguageSelector component in tests/unit/test_language_selector.py (test language list population, selection change events, auto-detect option)
- [ ] T038 [P] [US2] Unit test for language preference persistence in tests/unit/test_preferences.py (test save/load source/target language, default values)

### Integration Tests for User Story 2

- [ ] T039 [US2] Integration test for manual language selection in tests/integration/test_language_selection.py (select languages → translate → verify correct target language)
- [ ] T040 [US2] Integration test for language change triggers re-translation in tests/integration/test_language_selection.py (translate → change target language → verify re-translation)

### Implementation for User Story 2

- [ ] T041 [P] [US2] Implement LanguageSelector dropdown component in src/ui/language_selector.py (QComboBox with language names and flags, auto-detect option, signal on change)
- [ ] T042 [US2] Add language selection UI to MainWindow in src/ui/main_window.py (source language selector, target language selector, layout integration)
- [ ] T043 [US2] Update TranslationService to accept manual language selection in src/core/translator.py (override auto-detection when manual language specified)
- [ ] T044 [US2] Implement language preference save/load in src/core/preferences.py (default_source_language, default_target_language properties with QSettings persistence)
- [ ] T045 [US2] Connect language selectors to preferences in src/ui/main_window.py (restore from preferences on startup, save on change)
- [ ] T046 [US2] Implement re-translation on target language change in src/ui/main_window.py (if source text exists and target language changes, trigger new translation)

**Checkpoint**: User Stories 1 AND 2 should both work independently. Users can choose languages or use auto-detect.

---

## Phase 5: User Story 3 - Translation Result Management (Priority: P3)

**Goal**: Users can easily copy translation results to clipboard

**Independent Test**: After translation appears, click "Copy" button, paste in another app, verify translated text is pasted

### Unit Tests for User Story 3

- [ ] T047 [P] [US3] Unit test for clipboard operations in tests/unit/test_clipboard.py (test copy to clipboard, verify clipboard content)

### Integration Tests for User Story 3

- [ ] T048 [US3] Integration test for copy button in tests/integration/test_result_management.py (translate → click copy → verify clipboard)
- [ ] T049 [US3] Integration test for keyboard shortcut in tests/integration/test_result_management.py (translate → press Cmd+C → verify clipboard)

### Implementation for User Story 3

- [ ] T050 [US3] Add copy button to result text area in src/ui/main_window.py (QPushButton with icon, positioned near result QTextEdit)
- [ ] T051 [US3] Implement copy to clipboard functionality in src/ui/main_window.py (QApplication.clipboard().setText(), show visual feedback with status label)
- [ ] T052 [US3] Add keyboard shortcut for copy in src/ui/main_window.py (QShortcut for Cmd+C/Ctrl+C when result text has focus)
- [ ] T053 [US3] Implement visual feedback for copy action in src/ui/main_window.py (temporary "Copied!" message in status label, fade after 2 seconds with QTimer)
- [ ] T054 [US3] Enable text selection in result QTextEdit in src/ui/main_window.py (setTextInteractionFlags to allow selection and copying)

**Checkpoint**: All three user stories (quick translation, language selection, result management) should work independently

---

## Phase 6: User Story 4 - Application Lifecycle (Priority: P4)

**Goal**: User settings and preferences persist across app restarts

**Independent Test**: Set source="Korean", target="English", close app, reopen app, verify language settings are restored

### Unit Tests for User Story 4

- [ ] T055 [P] [US4] Unit test for window geometry persistence in tests/unit/test_preferences.py (test save/restore window size and position)
- [ ] T056 [P] [US4] Unit test for theme preference persistence in tests/unit/test_preferences.py (test save/restore dark/light mode preference)
- [ ] T057 [P] [US4] Unit test for preferences migration in tests/unit/test_preferences.py (test schema version upgrade, old data migration)

### Integration Tests for User Story 4

- [ ] T058 [US4] Integration test for settings persistence in tests/integration/test_lifecycle.py (change settings → close app → reopen → verify all settings restored)
- [ ] T059 [US4] Integration test for splash screen in tests/integration/test_lifecycle.py (launch app → verify splash shown during model load → verify splash closes when ready)

### Implementation for User Story 4

- [ ] T060 [US4] Add window geometry save/restore in src/ui/main_window.py (saveGeometry() on close, restoreGeometry() on init using UserPreferences)
- [ ] T061 [US4] Add window state save/restore in src/ui/main_window.py (saveState() on close, restoreState() on init for toolbars/dockwidgets if any)
- [ ] T062 [US4] Update SplashScreen with progress reporting in src/ui/splash_screen.py (progress bar, status message label, connect to ModelManager progress signals)
- [ ] T063 [US4] Implement model loading progress in src/core/model_manager.py (emit progress at 10%, 30%, 90%, 100% during tokenizer load, model download, model init)
- [ ] T064 [US4] Add theme preference to UserPreferences in src/core/preferences.py (theme property with auto/light/dark enum, persist with QSettings)
- [ ] T065 [US4] Implement theme preference UI in src/ui/main_window.py (optional: theme selector in menu bar or preferences dialog)
- [ ] T066 [US4] Implement preferences schema migration in src/core/preferences.py (version tracking, migrate_v0_to_v1 methods for future schema changes)
- [ ] T067 [US4] Add graceful shutdown in src/main.py (TranslationService.shutdown(), cancel pending tasks, wait for completion)

**Checkpoint**: All four user stories complete. App has full persistence, smooth lifecycle, and professional UX.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T068 [P] Implement macOS appearance detection in src/macos_platform/appearance.py (optional: NSAppearance observer via PyObjC for enhanced detection beyond QPalette)
- [ ] T069 [P] Implement VoiceOver accessibility support in src/macos_platform/accessibility.py (accessible labels for all UI elements, keyboard navigation)
- [ ] T070 [P] Add keyboard shortcuts documentation in README.md (Cmd+C for copy, Cmd+Q for quit, Cmd+W for close)
- [ ] T071 [P] Create app icons in resources/icons/ (16x16, 32x32, 64x64, 128x128, 256x256, 512x512 PNG files)
- [ ] T072 [P] Add UI text localization support in resources/translations/ (optional: QTranslator for UI in multiple languages)
- [ ] T073 Code cleanup and refactoring (remove debug prints, consolidate duplicate code, improve variable names)
- [ ] T074 Performance optimization (profile with PyTorch Profiler, optimize hot paths identified in benchmarks)
- [ ] T075 Security audit (check for hardcoded secrets, validate user input sanitization, review error message exposure)
- [ ] T076 [P] Add edge case handling for 2000+ character texts in src/core/translator.py (show user warning, truncate or reject)
- [ ] T077 [P] Add edge case handling for empty text input in src/ui/main_window.py (disable translate button, clear result)
- [ ] T078 [P] Add edge case handling for unsupported language pairs in src/core/translator.py (show user-friendly error message)
- [ ] T079 [P] Add edge case handling for rapid text changes in src/core/translator.py (verify debouncing works, cancel outdated requests)
- [ ] T080 [P] Add edge case handling for memory errors in src/core/model_manager.py (catch OOM, show user-friendly message with resolution steps)
- [ ] T081 [P] Implement macOS dark/light mode transition handling in src/ui/styles.py (connect to system appearance change events, update UI instantly)
- [ ] T082 Run full constitution compliance check (verify >80% test coverage, all tests pass, black/ruff/mypy pass, performance thresholds met)
- [ ] T083 Final integration testing (run all user stories sequentially, verify no regressions, test on fresh macOS install)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion - Can start in parallel with US1 but integration easier after US1
- **User Story 3 (Phase 5)**: Depends on Foundational phase completion - Requires US1 complete (needs translation results to copy)
- **User Story 4 (Phase 6)**: Depends on Foundational phase completion - Can start after US1 (needs basic UI to persist)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories - Can start after Foundational
- **User Story 2 (P2)**: Extends US1 - Best implemented after US1 complete, but can be parallel if careful
- **User Story 3 (P3)**: Requires US1 complete (needs translation results to exist)
- **User Story 4 (P4)**: Requires US1 complete (needs UI components to persist state)

### Within Each User Story

1. **Tests FIRST** (write and verify they fail)
2. **Unit tests** before implementation (can run in parallel)
3. **Models/entities** (parallelizable within story)
4. **Services/business logic** (depends on models)
5. **UI components** (depends on services)
6. **Integration** (depends on all components)
7. **Integration tests** (verify story complete)
8. **Performance tests** (verify story meets thresholds)

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004, T005, T006, T007, T008, T009 can all run in parallel
- **Phase 2 (Foundational)**: T011, T012, T013, T016, T017 can run in parallel
- **Within US1**:
  - Unit tests T019, T020, T021 can run in parallel
  - Performance tests T024, T025, T026 can run in parallel
  - Models/components T027, T028 can run in parallel
- **Within US2**: Tests T037, T038 can run in parallel, components T041 can be parallel with T044
- **Within US3**: All tests can run in parallel
- **Within US4**: All unit tests T055, T056, T057 can run in parallel
- **Polish Phase**: Most tasks T068-T081 can run in parallel

### Story-Level Parallelization

If multiple developers are available:
- After Foundational (Phase 2) completes, US1 and US2 can proceed in parallel
- US3 can start once US1 reaches T036 (basic translation working)
- US4 can start once US1 reaches T034 (UI exists)

---

## Parallel Example: User Story 1

```bash
# Launch all unit tests for US1 together:
Task: "Unit test for ModelManager in tests/unit/test_model_manager.py"
Task: "Unit test for Translator in tests/unit/test_translator.py"
Task: "Unit test for LanguageDetector in tests/unit/test_language_detector.py"

# Launch performance tests for US1 together:
Task: "Benchmark short text translation in tests/performance/test_translation_latency.py"
Task: "Benchmark medium text translation in tests/performance/test_translation_latency.py"
Task: "Memory usage test in tests/performance/test_memory_usage.py"

# Launch core components for US1 together:
Task: "Implement ModelManager in src/core/model_manager.py"
Task: "Implement LanguageDetector in src/core/language_detector.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. ✅ Complete Phase 1: Setup (T001-T010)
2. ✅ Complete Phase 2: Foundational (T011-T018) - **CRITICAL BLOCKER**
3. ✅ Complete Phase 3: User Story 1 (T019-T036)
4. **STOP and VALIDATE**:
   - Run tests: `pytest tests/ --benchmark-skip`
   - Run app: `python src/main.py`
   - Test independent scenario: Input "Hello World" → Verify Korean translation in <2s
   - Check constitution: `black src/ tests/ && ruff check src/ tests/ && mypy src/ && pytest tests/ --cov=src --cov-report=term`
5. **MVP READY**: Demo basic translation functionality

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Test infrastructure works → ~10 tasks
2. **MVP** (Phase 3: US1) → Test independently → Deploy/Demo → ~18 tasks
3. **Enhanced** (Phase 4: US2) → Test independently → Deploy/Demo → ~10 tasks
4. **Full-featured** (Phase 5: US3) → Test independently → Deploy/Demo → ~8 tasks
5. **Production** (Phase 6: US4) → Test independently → Deploy/Demo → ~13 tasks
6. **Polished** (Phase 7) → Final validation → Public release → ~16 tasks

Total: **83 tasks** organized into 7 phases

Each phase adds value without breaking previous functionality. Each user story is independently testable and deliverable.

### Parallel Team Strategy

With 3 developers after Foundational phase:
1. **Dev A**: User Story 1 (T019-T036) - Core translation, ~2-3 days
2. **Dev B**: User Story 2 (T037-T046) - Language selection, starts after US1 reaches T032, ~1-2 days
3. **Dev C**: User Story 4 (T055-T067) - Persistence, starts after US1 reaches T034, ~2 days

Then sequentially:
4. **All**: User Story 3 (T047-T054) - Quick wins, ~1 day
5. **All**: Polish (T068-T083) - Parallel polishing, ~2-3 days

**Total estimated time with 3 devs: ~6-8 days** vs **~15-20 days single developer**

---

## Notes

- **[P] tasks**: Different files, no dependencies, safe to parallelize
- **[Story] labels**: Map tasks to user stories for traceability and independent testing
- **Constitution compliance**: >80% test coverage REQUIRED, all quality gates MUST pass
- **Performance thresholds**: <2s for <500 chars, <5s for 500-2000 chars, <500MB memory - tests MUST fail if exceeded by >10%
- **Tests first**: Write failing tests before implementation (TDD approach)
- **Commit frequently**: After each task or logical group
- **Stop at checkpoints**: Validate each user story independently before proceeding
- **Avoid**: Vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Validation Checklist

Before marking tasks.md as complete, verify:

- ✅ All tasks follow strict format: `- [ ] [ID] [P?] [Story?] Description with file path`
- ✅ Tasks organized by user story priority (P1, P2, P3, P4)
- ✅ Each user story has Independent Test criteria
- ✅ Test tasks included (constitution requires >80% coverage)
- ✅ Each task includes exact file path
- ✅ Dependencies clearly documented
- ✅ Parallel opportunities identified with [P] marker
- ✅ Story labels [US1-US4] correctly applied
- ✅ Total task count documented (83 tasks)
- ✅ MVP scope defined (Phases 1-3, ~28 tasks)
- ✅ Implementation strategy includes incremental delivery
