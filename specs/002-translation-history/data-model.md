# Data Model: 번역 히스토리 (Translation History)

**Date**: 2025-12-27
**Feature Branch**: `002-translation-history`

## Entities

### HistoryEntry

번역 기록의 개별 항목을 나타내는 불변 데이터 클래스.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | `str` | 고유 식별자 | UUID4[:8], 8자 hex 문자열 |
| `source_text` | `str` | 원문 텍스트 | 1-2000자, 빈 문자열 불가 |
| `translated_text` | `str` | 번역된 텍스트 | 빈 문자열 가능 (번역 실패 시) |
| `source_lang` | `str` | 소스 언어 코드 | LanguageCode enum 값 |
| `target_lang` | `str` | 타겟 언어 코드 | LanguageCode enum 값 |
| `created_at` | `datetime` | 생성 시간 | UTC 기준, ISO 8601 형식 저장 |

**Validation Rules**:
- `id`: 정확히 8자의 hex 문자열
- `source_text`: 1자 이상 2000자 이하
- `source_lang`, `target_lang`: 유효한 LanguageCode 값
- `created_at`: 유효한 datetime 객체

**Python Definition**:
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class HistoryEntry:
    id: str
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    created_at: datetime

    def preview(self, max_length: int = 100) -> str:
        """원문의 미리보기 텍스트 반환"""
        if len(self.source_text) <= max_length:
            return self.source_text
        return self.source_text[:max_length-3] + "..."
```

---

### HistoryStore

히스토리 저장소를 관리하는 클래스. 싱글톤 패턴 또는 의존성 주입으로 사용.

| Property/Method | Type | Description |
|-----------------|------|-------------|
| `entries` | `list[HistoryEntry]` | 모든 히스토리 항목 (최신순) |
| `max_entries` | `int` | 최대 저장 개수 (기본값: 50) |
| `add(entry)` | `None` | 항목 추가, 초과 시 오래된 항목 삭제 |
| `remove(id)` | `bool` | ID로 항목 삭제, 성공 여부 반환 |
| `clear()` | `None` | 모든 항목 삭제 |
| `search(query)` | `list[HistoryEntry]` | 키워드 검색 (원문+번역문) |
| `get(id)` | `HistoryEntry | None` | ID로 항목 조회 |
| `save()` | `None` | 저장소를 영구 저장 |
| `load()` | `None` | 저장소에서 로드 |

**State Transitions**:

```
[Empty] --add()--> [Has Entries]
[Has Entries] --add()--> [Has Entries] (최대 50개 유지)
[Has Entries] --remove(id)--> [Has Entries | Empty]
[Has Entries] --clear()--> [Empty]
```

**Python Definition**:
```python
from PySide6.QtCore import QObject, Signal

class HistoryStore(QObject):
    entryAdded = Signal(object)      # HistoryEntry
    entryRemoved = Signal(str)       # entry_id
    entriesCleared = Signal()
    entriesLoaded = Signal()

    MAX_ENTRIES = 50

    def __init__(self, settings: QSettings):
        super().__init__()
        self._settings = settings
        self._entries: list[HistoryEntry] = []

    @property
    def entries(self) -> list[HistoryEntry]:
        return self._entries.copy()

    def add(self, entry: HistoryEntry) -> None:
        self._entries.insert(0, entry)
        if len(self._entries) > self.MAX_ENTRIES:
            self._entries.pop()
        self.save()
        self.entryAdded.emit(entry)

    def remove(self, entry_id: str) -> bool:
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id:
                self._entries.pop(i)
                self.save()
                self.entryRemoved.emit(entry_id)
                return True
        return False

    def clear(self) -> None:
        self._entries.clear()
        self.save()
        self.entriesCleared.emit()

    def search(self, query: str) -> list[HistoryEntry]:
        if not query:
            return self.entries
        query_lower = query.lower()
        return [
            e for e in self._entries
            if query_lower in e.source_text.lower()
            or query_lower in e.translated_text.lower()
        ]

    def get(self, entry_id: str) -> HistoryEntry | None:
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None
```

---

## Relationships

```
┌─────────────────┐         ┌─────────────────┐
│  HistoryStore   │ 1:N     │  HistoryEntry   │
│                 │────────>│                 │
│ - entries[]     │         │ - id            │
│ - max_entries   │         │ - source_text   │
│                 │         │ - translated_text│
│ + add()         │         │ - source_lang   │
│ + remove()      │         │ - target_lang   │
│ + search()      │         │ - created_at    │
│ + save()        │         │                 │
│ + load()        │         │ + preview()     │
└─────────────────┘         └─────────────────┘
        │
        │ uses
        ▼
┌─────────────────┐
│   QSettings     │
│                 │
│ - beginWriteArray
│ - endArray      │
│ - setValue      │
│ - value         │
└─────────────────┘
```

---

## Storage Schema

QSettings 배열 형식으로 저장:

```
history/entries/size = 3
history/entries/1/id = "a1b2c3d4"
history/entries/1/source_text = "Hello, world!"
history/entries/1/translated_text = "안녕하세요, 세계!"
history/entries/1/source_lang = "en"
history/entries/1/target_lang = "ko"
history/entries/1/created_at = "2025-12-27T10:30:00Z"
history/entries/2/...
```

---

## Config Constants

`src/core/config.py`에 추가:

```python
@dataclass(frozen=True)
class HistoryConfig:
    max_entries: int = 50
    preview_length: int = 100
    search_debounce_ms: int = 150
```
