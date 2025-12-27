# Tasks: About 및 Update Check 메뉴 추가

**Input**: Design documents from `/specs/003-about-update-menu/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓

**Tests**: 프로젝트 요구사항(CLAUDE.md)에 따라 80%+ 테스트 커버리지 유지를 위해 테스트 포함

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Config 확장 및 공통 유틸리티 추가

- [x] T001 AppConfig에 copyright_year, license, github_url, github_api_url 필드 추가 in src/core/config.py
- [x] T002 [P] 버전 비교 유틸리티 모듈 생성 in src/utils/version.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 업데이트 확인 핵심 로직 (두 User Story에서 공유하지 않으므로 US2로 이동)

이 기능에는 두 User Story 간 공유되는 foundational 컴포넌트가 없습니다. 각 스토리가 독립적입니다.

**Checkpoint**: Setup 완료 - User Story 구현 시작 가능

---

## Phase 3: User Story 1 - About 대화상자 열기 (Priority: P1) 🎯 MVP

**Goal**: 사용자가 앱 메뉴에서 About을 선택하여 앱 정보(이름, 버전, 저작권, 라이선스, GitHub 링크)를 확인할 수 있다.

**Independent Test**: LocalTranslate 메뉴 → About LocalTranslate 클릭 → 대화상자에 앱 정보 표시 → ESC 또는 닫기로 닫힘

### Tests for User Story 1

- [x] T003 [P] [US1] AboutDialog 단위 테스트 작성 in tests/unit/test_about_dialog.py

### Implementation for User Story 1

- [x] T004 [P] [US1] AboutDialog 클래스 구현 in src/ui/about_dialog.py
- [x] T005 [US1] MainWindow에 앱 메뉴 추가 및 About 액션 연결 in src/ui/main_window.py
- [x] T006 [US1] About 대화상자 수동 테스트 및 검증

**Checkpoint**: About 대화상자가 완전히 동작하며 독립적으로 테스트 가능

---

## Phase 4: User Story 2 - 업데이트 확인 (Priority: P2)

**Goal**: 사용자가 Help 메뉴에서 Check for Updates를 선택하여 최신 버전 여부를 확인하고, 업데이트가 가능하면 다운로드 링크를 제공받을 수 있다.

**Independent Test**: Help 메뉴 → Check for Updates... 클릭 → 진행 표시 → 결과(최신/업데이트 가능/오류) 대화상자 표시

### Tests for User Story 2

- [x] T007 [P] [US2] 버전 비교 유틸리티 테스트 작성 in tests/unit/test_version.py
- [x] T008 [P] [US2] UpdateChecker 단위 테스트 작성 (mock 사용) in tests/unit/test_update_checker.py
- [x] T009 [P] [US2] UpdateDialog 단위 테스트 작성 in tests/unit/test_update_dialog.py

### Implementation for User Story 2

- [x] T010 [P] [US2] UpdateStatus 열거형 및 ReleaseInfo, UpdateCheckResult 데이터클래스 정의 in src/core/update_checker.py
- [x] T011 [US2] UpdateChecker 클래스 구현 (GitHub API 연동) in src/core/update_checker.py
- [x] T012 [P] [US2] UpdateDialog 클래스 구현 (결과 표시 대화상자) in src/ui/update_dialog.py
- [x] T013 [US2] MainWindow에 Help 메뉴 추가 및 Check for Updates 액션 연결 in src/ui/main_window.py
- [x] T014 [US2] 비동기 업데이트 확인을 위한 QThread 워커 구현 in src/ui/main_window.py
- [x] T015 [US2] 네트워크 오류 및 타임아웃 처리 검증

**Checkpoint**: 업데이트 확인 기능이 완전히 동작하며 독립적으로 테스트 가능

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: 품질 검증 및 최종 마무리

- [x] T016 전체 테스트 실행 및 커버리지 확인 (pytest --cov)
- [x] T017 [P] 타입 체크 통과 확인 (mypy src/)
- [x] T018 [P] 린트 및 포맷팅 확인 (ruff check, black --check)
- [x] T019 quickstart.md의 수동 테스트 체크리스트 완료

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: N/A for this feature
- **User Story 1 (Phase 3)**: Depends on Setup completion
- **User Story 2 (Phase 4)**: Depends on Setup completion (T002 버전 유틸리티)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup - No dependencies on US2
- **User Story 2 (P2)**: Can start after Setup - No dependencies on US1 (완전히 독립적)

### Within Each User Story

- Tests SHOULD be written first (TDD)
- Data classes before service logic
- Service before UI
- UI dialog before menu integration
- Integration before manual verification

### Parallel Opportunities

- T002 (버전 유틸리티) can run in parallel with T001 (config)
- T003 (US1 테스트) can run in parallel with US2 tests (T007, T008, T009)
- T004 (AboutDialog) can run in parallel with T010, T011 (UpdateChecker)
- T012 (UpdateDialog) can run in parallel with T004 (AboutDialog)
- US1 and US2 can be developed entirely in parallel after Setup

---

## Parallel Example: Setup Phase

```bash
# Launch Setup tasks in parallel:
Task: "AppConfig 필드 추가 in src/core/config.py"
Task: "버전 비교 유틸리티 생성 in src/utils/version.py"
```

## Parallel Example: User Stories

```bash
# After Setup, both stories can proceed in parallel:

# US1 Track:
Task: "AboutDialog 테스트 in tests/unit/test_about_dialog.py"
Task: "AboutDialog 구현 in src/ui/about_dialog.py"

# US2 Track (simultaneously):
Task: "버전 유틸리티 테스트 in tests/unit/test_version.py"
Task: "UpdateChecker 테스트 in tests/unit/test_update_checker.py"
Task: "UpdateChecker 구현 in src/core/update_checker.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 3: User Story 1 (T003-T006)
3. **STOP and VALIDATE**: About 대화상자 독립 테스트
4. Deploy/demo if ready - 앱 정보 표시 기능 완성

### Incremental Delivery

1. Setup → US1 → Test → **MVP Complete** (About 기능)
2. Add US2 → Test → **Full Feature** (Update Check 추가)
3. Polish → Final validation

### Suggested MVP Scope

**User Story 1만으로 MVP 완성 가능**:
- About 대화상자로 앱 정보 제공
- macOS 표준 메뉴 패턴 적용
- 독립적으로 가치 제공

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US1과 US2는 완전히 독립적 - 동시 개발 가능
- 각 User Story 완료 후 체크포인트에서 검증
- Commit after each task or logical group
