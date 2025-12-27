# Implementation Plan: About 및 Update Check 메뉴 추가

**Branch**: `003-about-update-menu` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-about-update-menu/spec.md`

## Summary

macOS 표준 패턴에 따라 앱 메뉴(LocalTranslate)에 "About LocalTranslate" 항목을, Help 메뉴에 "Check for Updates..." 항목을 추가한다. About 대화상자는 앱 정보(이름, 버전, 저작권, 라이선스, GitHub 링크)를 표시하고, Update Check는 GitHub Releases API를 통해 최신 버전을 확인하여 업데이트 가능 여부를 사용자에게 알린다.

## Technical Context

**Language/Version**: Python 3.11+ (프로젝트는 3.12 사용)
**Primary Dependencies**: PySide6 6.5.0+, requests (HTTP 클라이언트)
**Storage**: N/A (앱 메타데이터는 config.py에서 관리)
**Testing**: pytest, pytest-qt
**Target Platform**: macOS 11.0+
**Project Type**: single (데스크톱 앱)
**Performance Goals**: About 대화상자 1초 이내 표시, 업데이트 확인 5초 이내 완료
**Constraints**: 네트워크 오류 시 15초 이내 타임아웃
**Scale/Scope**: 단일 사용자 데스크톱 앱

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

프로젝트 constitution이 템플릿 상태이므로 특별한 제약 조건이 없습니다. 기존 프로젝트 패턴(CLAUDE.md)을 따릅니다:
- [x] PySide6 UI 패턴 사용 (QDialog, QAction)
- [x] Qt 시그널/슬롯 패턴 적용
- [x] 타입 힌트 필수 (mypy strict)
- [x] 테스트 커버리지 80%+ 유지

## Project Structure

### Documentation (this feature)

```text
specs/003-about-update-menu/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A - no external API exposed)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── config.py            # 기존 - app_version, app_name 등 메타데이터
│   └── update_checker.py    # 신규 - GitHub Releases API 연동
├── ui/
│   ├── main_window.py       # 수정 - 메뉴바에 About/Help 메뉴 추가
│   ├── about_dialog.py      # 신규 - About 대화상자
│   └── update_dialog.py     # 신규 - 업데이트 확인 결과 대화상자
└── utils/
    └── version.py           # 신규 - 버전 비교 유틸리티

tests/
├── unit/
│   ├── test_update_checker.py  # 신규
│   ├── test_about_dialog.py    # 신규
│   └── test_version.py         # 신규
└── integration/
    └── test_menu_integration.py  # 신규 - 메뉴 동작 통합 테스트
```

**Structure Decision**: 기존 src/ 단일 프로젝트 구조를 유지하며, core/에 업데이트 확인 로직, ui/에 대화상자 컴포넌트를 추가합니다.

## Complexity Tracking

해당 없음 - 모든 변경사항이 기존 아키텍처 패턴을 따릅니다.
