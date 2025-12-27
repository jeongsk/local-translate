# Implementation Plan: 번역 히스토리 (Translation History)

**Branch**: `002-translation-history` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-translation-history/spec.md`

## Summary

번역 완료 시 자동으로 히스토리에 저장하고, 사용자가 과거 번역을 조회/검색/삭제/복사할 수 있는 사이드 패널 UI를 구현한다. QSettings 기반 로컬 영구 저장, 최대 50개 항목 제한, Cmd+H 단축키 토글 지원.

## Technical Context

**Language/Version**: Python 3.11+ (프로젝트는 3.12 사용)
**Primary Dependencies**: PySide6 (Qt6 GUI), QSettings (영구 저장)
**Storage**: QSettings (로컬 파일 시스템, `~/.config/LocalTranslate/` 또는 macOS plist)
**Testing**: pytest, pytest-qt, pytest-cov
**Target Platform**: macOS 11.0+ (Apple Silicon MPS 가속)
**Project Type**: Single desktop application
**Performance Goals**: 히스토리 로드 <1초, 검색 결과 <0.5초
**Constraints**: 최대 50개 항목, 앱 시작 시간 증가 <0.5초
**Scale/Scope**: 단일 사용자, 로컬 전용, 50개 항목

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Existing patterns followed | ✅ Pass | QSettings 패턴 이미 preferences.py에서 사용 중 |
| No unnecessary dependencies | ✅ Pass | 새 의존성 없음, 기존 PySide6/QSettings 활용 |
| Test-first approach planned | ✅ Pass | 테스트 마커 및 fixtures 활용 계획 |
| Simplicity (YAGNI) | ✅ Pass | MVP 기능만 구현, 확장은 향후 |

## Project Structure

### Documentation (this feature)

```text
specs/002-translation-history/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal API)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── history_store.py     # NEW: 히스토리 저장소 (HistoryEntry, HistoryStore)
│   ├── preferences.py       # MODIFY: 히스토리 패널 상태 저장 추가
│   ├── translator.py        # MODIFY: 번역 완료 시 히스토리 저장 연동
│   └── config.py            # MODIFY: 히스토리 관련 설정 상수 추가
├── ui/
│   ├── history_panel.py     # NEW: 사이드 패널 위젯
│   ├── history_item.py      # NEW: 히스토리 항목 위젯
│   └── main_window.py       # MODIFY: 히스토리 패널 통합, 단축키 추가
└── utils/

tests/
├── unit/
│   ├── test_history_store.py    # NEW: HistoryStore 단위 테스트
│   └── test_history_panel.py    # NEW: HistoryPanel UI 테스트
└── integration/
    └── test_history_flow.py     # NEW: 번역→저장→조회 통합 테스트
```

**Structure Decision**: 기존 Single project 구조 유지. core/에 비즈니스 로직, ui/에 위젯 추가.

## Complexity Tracking

> No violations detected. All requirements align with existing patterns.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
