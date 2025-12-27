# Internal API Contract: History Module

**Date**: 2025-12-27
**Feature Branch**: `002-translation-history`

## Overview

데스크톱 앱 내부 모듈 간 인터페이스 정의. REST API가 아닌 Python 클래스 인터페이스.

---

## HistoryStore API

### Methods

#### `add(entry: HistoryEntry) -> None`
새 히스토리 항목 추가.

**Preconditions**:
- `entry`는 유효한 HistoryEntry 객체
- `entry.id`는 고유해야 함

**Postconditions**:
- 항목이 리스트 맨 앞에 추가됨
- 50개 초과 시 마지막 항목 자동 삭제
- `entryAdded` 시그널 발생
- 저장소에 자동 저장됨

**Errors**:
- `ValueError`: entry가 None이거나 유효하지 않은 경우

---

#### `remove(entry_id: str) -> bool`
ID로 항목 삭제.

**Preconditions**:
- `entry_id`는 빈 문자열이 아님

**Postconditions**:
- 성공 시 `True` 반환, 항목이 리스트에서 제거됨
- 실패 시 `False` 반환 (항목 없음)
- 성공 시 `entryRemoved` 시그널 발생
- 저장소에 자동 저장됨

---

#### `clear() -> None`
모든 항목 삭제.

**Postconditions**:
- 리스트가 비워짐
- `entriesCleared` 시그널 발생
- 저장소에 자동 저장됨

---

#### `search(query: str) -> list[HistoryEntry]`
키워드로 검색.

**Preconditions**:
- `query`는 문자열 (빈 문자열 허용)

**Postconditions**:
- 빈 쿼리: 전체 항목 반환
- 비어있지 않은 쿼리: 원문 또는 번역문에 쿼리가 포함된 항목만 반환
- 대소문자 무시
- 원본 리스트 순서 유지 (최신순)

---

#### `get(entry_id: str) -> HistoryEntry | None`
ID로 단일 항목 조회.

**Postconditions**:
- 항목 존재 시 해당 HistoryEntry 반환
- 항목 없으면 None 반환

---

#### `save() -> None`
현재 상태를 영구 저장소에 저장.

**Postconditions**:
- QSettings에 모든 항목이 저장됨
- 저장 실패 시 예외 발생하지 않음 (로깅만)

---

#### `load() -> None`
영구 저장소에서 상태 복원.

**Postconditions**:
- QSettings에서 항목 로드
- 잘못된 형식의 항목은 무시됨
- `entriesLoaded` 시그널 발생

---

## Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `entryAdded` | `HistoryEntry` | 새 항목 추가됨 |
| `entryRemoved` | `str` (entry_id) | 항목 삭제됨 |
| `entriesCleared` | None | 모든 항목 삭제됨 |
| `entriesLoaded` | None | 저장소에서 로드 완료 |

---

## HistoryPanel API

### Slots

#### `on_entry_added(entry: HistoryEntry) -> None`
HistoryStore.entryAdded 시그널에 연결. UI 리스트에 항목 추가.

#### `on_entry_removed(entry_id: str) -> None`
HistoryStore.entryRemoved 시그널에 연결. UI 리스트에서 항목 제거.

#### `on_entries_cleared() -> None`
HistoryStore.entriesCleared 시그널에 연결. UI 리스트 비우고 빈 상태 표시.

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `entrySelected` | `HistoryEntry` | 항목 클릭됨 (메인 화면에 로드 요청) |
| `copyRequested` | `str` (translated_text) | 복사 버튼 클릭됨 |

---

## Integration Points

### TranslationService → HistoryStore

번역 완료 시 자동 저장:

```python
# translator.py
def _on_translation_complete(self, task_id, source_lang, translated_text):
    entry = HistoryEntry(
        id=generate_id(),
        source_text=self.current_source_text,
        translated_text=translated_text,
        source_lang=source_lang,
        target_lang=self.current_target_lang,
        created_at=datetime.utcnow()
    )
    self.history_store.add(entry)
```

### MainWindow → HistoryPanel

패널 토글 및 항목 로드:

```python
# main_window.py
def toggle_history_panel(self):
    self.history_panel.setVisible(not self.history_panel.isVisible())

def on_history_entry_selected(self, entry: HistoryEntry):
    self.source_text_edit.setText(entry.source_text)
    self.target_text_edit.setText(entry.translated_text)
    self.source_lang_selector.set_language(entry.source_lang)
    self.target_lang_selector.set_language(entry.target_lang)
```
