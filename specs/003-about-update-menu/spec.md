# Feature Specification: About 및 Update Check 메뉴 추가

**Feature Branch**: `003-about-update-menu`
**Created**: 2025-12-27
**Status**: Draft
**Input**: User description: "메뉴에 About와 Update Check 메뉴를 추가해줘."

## Clarifications

### Session 2025-12-27

- Q: 메뉴 배치 위치는 어떻게 할 것인가? → A: macOS 표준 패턴 적용 - About은 앱 메뉴(LocalTranslate 메뉴)에, Update Check는 Help 메뉴에 배치

## User Scenarios & Testing *(mandatory)*

### User Story 1 - About 대화상자 열기 (Priority: P1)

사용자가 LocalTranslate 앱의 버전 정보, 개발자 정보, 라이선스 정보를 확인하고 싶을 때, 메뉴에서 About을 선택하여 앱 정보를 볼 수 있다.

**Why this priority**: 앱의 기본적인 정보 제공은 사용자 신뢰와 투명성을 위해 필수적이다. 모든 데스크톱 앱에서 기대되는 표준 기능이다.

**Independent Test**: About 메뉴를 클릭하면 앱 정보가 담긴 대화상자가 표시되고, 닫기 버튼으로 대화상자를 닫을 수 있다.

**Acceptance Scenarios**:

1. **Given** 앱이 실행 중인 상태, **When** 사용자가 메뉴바에서 About 메뉴를 클릭, **Then** 앱 이름, 버전, 저작권, 라이선스 정보가 표시된 About 대화상자가 나타난다
2. **Given** About 대화상자가 열린 상태, **When** 사용자가 닫기 버튼을 클릭하거나 ESC 키를 누름, **Then** 대화상자가 닫히고 메인 윈도우로 돌아간다
3. **Given** About 대화상자가 열린 상태, **When** 사용자가 대화상자 내 링크(예: 프로젝트 GitHub)를 클릭, **Then** 기본 브라우저에서 해당 링크가 열린다

---

### User Story 2 - 업데이트 확인 (Priority: P2)

사용자가 현재 사용 중인 앱이 최신 버전인지 확인하고 싶을 때, 메뉴에서 Update Check를 선택하여 업데이트 가능 여부를 확인할 수 있다.

**Why this priority**: 업데이트 확인은 사용자가 최신 기능과 버그 수정을 받을 수 있게 하는 중요한 기능이지만, About 정보 표시보다는 우선순위가 낮다.

**Independent Test**: Update Check 메뉴를 클릭하면 업데이트 확인이 진행되고, 결과(최신 버전/업데이트 가능)가 표시된다.

**Acceptance Scenarios**:

1. **Given** 앱이 실행 중이고 인터넷에 연결된 상태, **When** 사용자가 Update Check 메뉴를 클릭, **Then** 업데이트 확인 진행 표시가 나타나고, 확인 완료 후 결과를 보여준다
2. **Given** 업데이트 확인이 완료되고 새 버전이 있는 경우, **When** 결과 대화상자가 표시됨, **Then** 새 버전 번호와 다운로드 페이지 링크가 표시된다
3. **Given** 업데이트 확인이 완료되고 이미 최신 버전인 경우, **When** 결과 대화상자가 표시됨, **Then** "이미 최신 버전입니다" 메시지가 표시된다
4. **Given** 앱이 실행 중이지만 인터넷에 연결되지 않은 상태, **When** 사용자가 Update Check 메뉴를 클릭, **Then** 네트워크 오류 메시지와 함께 나중에 다시 시도할 것을 안내한다

---

### Edge Cases

- 업데이트 확인 중 네트워크 연결이 끊어지면 어떻게 되는가? → 타임아웃 후 오류 메시지를 표시하고 재시도 옵션 제공
- 업데이트 확인 서버가 응답하지 않으면? → 타임아웃 후 적절한 오류 메시지 표시
- 사용자가 업데이트 확인 중 창을 닫으면? → 백그라운드 작업을 취소하고 정상적으로 앱 종료
- About 대화상자가 열린 상태에서 앱 창이 닫히면? → About 대화상자도 함께 닫힘

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 메뉴바에 앱 메뉴(LocalTranslate)와 Help 메뉴를 제공해야 한다
- **FR-002**: 앱 메뉴(LocalTranslate)에는 "About LocalTranslate" 항목이 있어야 한다 (macOS 표준)
- **FR-003**: Help 메뉴에는 "Check for Updates..." 항목이 있어야 한다
- **FR-004**: About 대화상자는 앱 이름, 버전 번호, 저작권 표시, 라이선스 정보를 표시해야 한다
- **FR-005**: About 대화상자는 앱 아이콘을 표시해야 한다
- **FR-006**: About 대화상자는 프로젝트 링크(GitHub 등)를 포함해야 한다
- **FR-007**: Update Check 기능은 GitHub Releases에서 최신 버전 정보를 확인해야 한다
- **FR-008**: Update Check는 현재 버전과 최신 버전을 비교하여 업데이트 필요 여부를 판단해야 한다
- **FR-009**: 업데이트가 가능한 경우 릴리스 페이지로 이동할 수 있는 링크를 제공해야 한다
- **FR-010**: 업데이트 확인 중에는 진행 상태를 사용자에게 표시해야 한다

### Key Entities

- **AppInfo**: 앱 이름, 버전, 저작권 연도, 라이선스 유형, 프로젝트 URL 등 앱 메타데이터
- **ReleaseInfo**: 최신 릴리스 버전, 릴리스 노트, 다운로드 URL 등 GitHub Release 정보
- **UpdateStatus**: 업데이트 확인 상태(확인 중, 최신 버전, 업데이트 가능, 오류)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 사용자가 About 대화상자를 2번 클릭 이내에 열 수 있다 (메뉴 → About)
- **SC-002**: About 대화상자가 1초 이내에 표시된다
- **SC-003**: 업데이트 확인이 정상적인 네트워크 환경에서 5초 이내에 완료된다
- **SC-004**: 네트워크 오류 시 사용자에게 15초 이내에 오류 메시지가 표시된다
- **SC-005**: 사용자가 현재 버전과 최신 버전 정보를 명확히 구분하여 확인할 수 있다

## Assumptions

- GitHub Releases API를 사용하여 버전 정보를 확인한다
- 버전 번호는 Semantic Versioning (예: v1.0.0) 형식을 따른다
- 앱 버전 정보는 기존 config에서 가져온다 (config.app_version)
- 자동 업데이트 기능은 이 기능 범위에 포함되지 않으며, 수동 다운로드 링크만 제공한다
- macOS 플랫폼에서 표준 UI 패턴을 따른다 (Qt/PySide6 다이얼로그 사용)
- 프로젝트는 GitHub에 호스팅되어 있다고 가정한다 (jeongsk/local-translate)

## Out of Scope

- 자동 업데이트 다운로드 및 설치
- 업데이트 릴리스 노트 상세 표시
- 베타/알파 버전 채널 선택
- 업데이트 알림 자동 표시 (수동 확인만 지원)
