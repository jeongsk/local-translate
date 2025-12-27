# Tasks: 번역 히스토리 (Translation History)

**Input**: Design documents from `/specs/002-translation-history/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included as this is a core feature requiring reliability.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic configuration

- [x] T001 Add HistoryConfig dataclass to src/core/config.py (max_entries=50, preview_length=100, search_debounce_ms=150)
- [x] T002 [P] Create empty src/core/history_store.py with module docstring
- [x] T003 [P] Create empty src/ui/history_panel.py with module docstring
- [x] T004 [P] Create empty src/ui/history_item.py with module docstring

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data structures that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement HistoryEntry dataclass in src/core/history_store.py (id, source_text, translated_text, source_lang, target_lang, created_at, preview method)
- [x] T006 Implement HistoryStore class skeleton in src/core/history_store.py (signals: entryAdded, entryRemoved, entriesCleared, entriesLoaded)
- [x] T007 Implement HistoryStore.save() method using QSettings beginWriteArray in src/core/history_store.py
- [x] T008 Implement HistoryStore.load() method using QSettings beginReadArray in src/core/history_store.py
- [x] T009 [P] Write unit tests for HistoryEntry in tests/unit/test_history_store.py
- [x] T010 [P] Write unit tests for HistoryStore save/load in tests/unit/test_history_store.py

**Checkpoint**: Foundation ready - HistoryEntry and persistence working

---

## Phase 3: User Story 1 - 번역 히스토리 조회 (Priority: P1) 🎯 MVP

**Goal**: 사용자가 과거에 수행한 번역 목록을 확인하고 재사용할 수 있다

**Independent Test**: 앱에서 번역 수행 후 히스토리 패널에서 최신순으로 표시되고, 클릭 시 메인 화면에 로드됨

### Tests for User Story 1

- [x] T011 [P] [US1] Write unit tests for HistoryStore.add() and entries property in tests/unit/test_history_store.py
- [x] T012 [P] [US1] Write unit tests for HistoryStore.get() in tests/unit/test_history_store.py

### Implementation for User Story 1

- [x] T013 [US1] Implement HistoryStore.add() method with 50 entry limit in src/core/history_store.py
- [x] T014 [US1] Implement HistoryStore.get() method in src/core/history_store.py
- [x] T015 [P] [US1] Create HistoryItemWidget class in src/ui/history_item.py (displays source preview, target lang, timestamp)
- [x] T016 [US1] Create HistoryPanel widget in src/ui/history_panel.py (QListWidget, empty state label, header)
- [x] T017 [US1] Implement HistoryPanel._refresh_list() to populate from HistoryStore in src/ui/history_panel.py
- [x] T018 [US1] Connect HistoryStore.entryAdded signal to HistoryPanel in src/ui/history_panel.py
- [x] T019 [US1] Implement HistoryPanel.entrySelected signal emission on item click in src/ui/history_panel.py
- [x] T020 [US1] Integrate HistoryPanel as side panel using QSplitter in src/ui/main_window.py
- [x] T021 [US1] Add toggle_history_panel() method and Cmd+H shortcut in src/ui/main_window.py
- [x] T022 [US1] Add history toggle button to toolbar in src/ui/main_window.py (View menu instead)
- [x] T023 [US1] Connect HistoryPanel.entrySelected to load source/target text in src/ui/main_window.py
- [x] T024 [US1] Integrate HistoryStore with TranslationService to auto-save on translation complete in src/ui/main_window.py
- [x] T025 [US1] Add history_panel_visible preference to src/core/preferences.py
- [ ] T026 [P] [US1] Write UI tests for HistoryPanel in tests/unit/test_history_panel.py

**Checkpoint**: User Story 1 complete - history viewing and loading works independently

---

## Phase 4: User Story 2 - 히스토리 항목 삭제 (Priority: P2)

**Goal**: 사용자가 개별 또는 전체 히스토리 항목을 삭제할 수 있다

**Independent Test**: 히스토리 항목의 삭제 버튼 클릭 시 해당 항목만 삭제되고, 전체 삭제 시 확인 후 모두 삭제됨

### Tests for User Story 2

- [x] T027 [P] [US2] Write unit tests for HistoryStore.remove() in tests/unit/test_history_store.py
- [x] T028 [P] [US2] Write unit tests for HistoryStore.clear() in tests/unit/test_history_store.py

### Implementation for User Story 2

- [x] T029 [US2] Implement HistoryStore.remove() method in src/core/history_store.py
- [x] T030 [US2] Implement HistoryStore.clear() method in src/core/history_store.py
- [x] T031 [US2] Add delete button to HistoryItemWidget in src/ui/history_item.py
- [x] T032 [US2] Connect delete button to HistoryStore.remove() via signal in src/ui/history_panel.py
- [x] T033 [US2] Connect HistoryStore.entryRemoved signal to remove item from list in src/ui/history_panel.py
- [x] T034 [US2] Add "전체 삭제" button to HistoryPanel header in src/ui/history_panel.py
- [x] T035 [US2] Implement confirmation dialog for clear all action in src/ui/history_panel.py
- [x] T036 [US2] Connect HistoryStore.entriesCleared signal to refresh empty state in src/ui/history_panel.py

**Checkpoint**: User Story 2 complete - delete functionality works independently

---

## Phase 5: User Story 3 - 히스토리 검색 (Priority: P3)

**Goal**: 사용자가 키워드로 히스토리를 검색하여 필터링할 수 있다

**Independent Test**: 검색창에 키워드 입력 시 해당 텍스트가 포함된 항목만 표시되고, 검색어 삭제 시 전체 목록 복원

### Tests for User Story 3

- [x] T037 [P] [US3] Write unit tests for HistoryStore.search() in tests/unit/test_history_store.py

### Implementation for User Story 3

- [x] T038 [US3] Implement HistoryStore.search() method with case-insensitive matching in src/core/history_store.py
- [x] T039 [US3] Add QLineEdit search input to HistoryPanel in src/ui/history_panel.py
- [x] T040 [US3] Implement search debounce timer (150ms) in src/ui/history_panel.py
- [x] T041 [US3] Implement _apply_filter() to show/hide items based on search in src/ui/history_panel.py
- [x] T042 [US3] Add "검색 결과가 없습니다" message for empty search results in src/ui/history_panel.py

**Checkpoint**: User Story 3 complete - search functionality works independently

---

## Phase 6: User Story 4 - 히스토리 항목 복사 (Priority: P3)

**Goal**: 사용자가 히스토리에서 번역 결과를 클립보드에 빠르게 복사할 수 있다

**Independent Test**: 히스토리 항목의 복사 버튼 클릭 시 번역 결과가 클립보드에 복사되고 "복사됨" 알림 표시

### Implementation for User Story 4

- [x] T043 [US4] Add copy button to HistoryItemWidget in src/ui/history_item.py
- [x] T044 [US4] Emit copyRequested signal with translated_text on copy button click in src/ui/history_item.py
- [x] T045 [US4] Connect copyRequested to clipboard copy and show status message in src/ui/history_panel.py

**Checkpoint**: User Story 4 complete - copy functionality works independently

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T046 Write integration test for full translation→save→view→delete flow in tests/integration/test_history_flow.py
- [ ] T047 [P] Apply consistent styling to HistoryPanel and HistoryItemWidget matching app theme in src/ui/history_panel.py
- [ ] T048 [P] Add dark/light mode support to history widgets in src/ui/styles.py
- [ ] T049 Verify performance: history load <1s, search <0.5s with 50 entries
- [ ] T050 Run quickstart.md validation to ensure all implementation matches documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in priority order (P1 → P2 → P3)
  - US3 and US4 can run in parallel after US2 completes (or after Foundational if independent)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires US1 UI to be in place for delete buttons
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Requires US1 UI for search filter
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Requires US1 UI for copy button placement

### Within Each User Story

- Tests MUST be written and FAIL before implementation (if tests included)
- Core logic (HistoryStore methods) before UI
- UI components before integration with MainWindow
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003, T004 can run in parallel (different files)
- T009, T010 can run in parallel (different test functions)
- T011, T012 can run in parallel within US1
- T015 can run in parallel with T013, T014 (different files)
- T027, T028 can run in parallel within US2
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: Phase 2 (Foundational)

```bash
# These can run in parallel (different files):
T002: Create empty src/core/history_store.py
T003: Create empty src/ui/history_panel.py
T004: Create empty src/ui/history_item.py
```

## Parallel Example: User Story 1

```bash
# Tests can be written in parallel:
T011: Write unit tests for HistoryStore.add()
T012: Write unit tests for HistoryStore.get()

# Model and UI widget can be parallel (different files):
T013: Implement HistoryStore.add() in src/core/history_store.py
T015: Create HistoryItemWidget in src/ui/history_item.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T010)
3. Complete Phase 3: User Story 1 (T011-T026)
4. **STOP and VALIDATE**: Test history viewing and loading independently
5. Deploy/demo if ready - users can view and reuse past translations

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP! - View history)
3. Add User Story 2 → Test independently → Deploy (Delete history)
4. Add User Story 3 → Test independently → Deploy (Search history)
5. Add User Story 4 → Test independently → Deploy (Copy from history)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (required first for UI foundation)
   - After US1 UI ready:
     - Developer B: User Story 2
     - Developer C: User Story 3 + 4

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are relative to repository root

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 50 |
| Phase 1 (Setup) | 4 tasks |
| Phase 2 (Foundational) | 6 tasks |
| Phase 3 (US1 - MVP) | 16 tasks |
| Phase 4 (US2) | 10 tasks |
| Phase 5 (US3) | 6 tasks |
| Phase 6 (US4) | 3 tasks |
| Phase 7 (Polish) | 5 tasks |
| Parallelizable Tasks | 18 tasks (36%) |
