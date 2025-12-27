# Quickstart: 번역 히스토리 구현 가이드

**Date**: 2025-12-27
**Feature Branch**: `002-translation-history`

## 개요

이 문서는 번역 히스토리 기능 구현을 위한 빠른 시작 가이드입니다.

## 선행 조건

- Python 3.11+
- PySide6 설치됨
- 프로젝트 의존성 설치: `uv pip install -e ".[dev]"`

## 구현 순서

### 1. HistoryEntry 데이터 클래스 (core/history_store.py)

```python
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass(frozen=True)
class HistoryEntry:
    id: str
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    created_at: datetime

    @staticmethod
    def create(source_text: str, translated_text: str,
               source_lang: str, target_lang: str) -> "HistoryEntry":
        return HistoryEntry(
            id=uuid.uuid4().hex[:8],
            source_text=source_text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            created_at=datetime.utcnow()
        )

    def preview(self, max_length: int = 100) -> str:
        if len(self.source_text) <= max_length:
            return self.source_text
        return self.source_text[:max_length-3] + "..."
```

### 2. HistoryStore 저장소 (core/history_store.py)

```python
from PySide6.QtCore import QObject, Signal, QSettings

class HistoryStore(QObject):
    entryAdded = Signal(object)
    entryRemoved = Signal(str)
    entriesCleared = Signal()

    MAX_ENTRIES = 50

    def __init__(self, settings: QSettings):
        super().__init__()
        self._settings = settings
        self._entries: list[HistoryEntry] = []
        self.load()

    def add(self, entry: HistoryEntry) -> None:
        self._entries.insert(0, entry)
        if len(self._entries) > self.MAX_ENTRIES:
            self._entries.pop()
        self.save()
        self.entryAdded.emit(entry)

    def save(self) -> None:
        self._settings.beginWriteArray("history/entries")
        for i, entry in enumerate(self._entries):
            self._settings.setArrayIndex(i)
            self._settings.setValue("id", entry.id)
            self._settings.setValue("source_text", entry.source_text)
            self._settings.setValue("translated_text", entry.translated_text)
            self._settings.setValue("source_lang", entry.source_lang)
            self._settings.setValue("target_lang", entry.target_lang)
            self._settings.setValue("created_at", entry.created_at.isoformat())
        self._settings.endArray()

    def load(self) -> None:
        count = self._settings.beginReadArray("history/entries")
        self._entries = []
        for i in range(count):
            self._settings.setArrayIndex(i)
            try:
                entry = HistoryEntry(
                    id=self._settings.value("id", ""),
                    source_text=self._settings.value("source_text", ""),
                    translated_text=self._settings.value("translated_text", ""),
                    source_lang=self._settings.value("source_lang", ""),
                    target_lang=self._settings.value("target_lang", ""),
                    created_at=datetime.fromisoformat(
                        self._settings.value("created_at", datetime.utcnow().isoformat())
                    )
                )
                if entry.id and entry.source_text:
                    self._entries.append(entry)
            except (ValueError, TypeError):
                continue
        self._settings.endArray()
```

### 3. HistoryPanel UI (ui/history_panel.py)

```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QLabel, QHBoxLayout
)
from PySide6.QtCore import Signal, Qt, QTimer

class HistoryPanel(QWidget):
    entrySelected = Signal(object)  # HistoryEntry

    def __init__(self, history_store: HistoryStore, parent=None):
        super().__init__(parent)
        self._store = history_store
        self._setup_ui()
        self._connect_signals()
        self._refresh_list()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 헤더
        header = QHBoxLayout()
        header.addWidget(QLabel("번역 기록"))
        self.clear_btn = QPushButton("전체 삭제")
        header.addWidget(self.clear_btn)
        layout.addLayout(header)

        # 검색
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색...")
        layout.addWidget(self.search_input)

        # 리스트
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # 빈 상태
        self.empty_label = QLabel("번역 기록이 없습니다")
        self.empty_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.empty_label)

    def _connect_signals(self):
        self._store.entryAdded.connect(self._on_entry_added)
        self._store.entryRemoved.connect(self._on_entry_removed)
        self._store.entriesCleared.connect(self._refresh_list)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.clear_btn.clicked.connect(self._on_clear_clicked)

        # 검색 디바운스
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._apply_filter)
        self.search_input.textChanged.connect(
            lambda: self.search_timer.start(150)
        )
```

### 4. MainWindow 통합 (ui/main_window.py)

```python
# 기존 MainWindow에 추가

from PySide6.QtWidgets import QSplitter
from PySide6.QtGui import QAction, QKeySequence

def _setup_history(self):
    # 히스토리 저장소
    self.history_store = HistoryStore(self.preferences._settings)

    # 사이드 패널
    self.history_panel = HistoryPanel(self.history_store)
    self.history_panel.setVisible(False)
    self.history_panel.setMinimumWidth(250)

    # 스플리터로 레이아웃 재구성
    self.splitter = QSplitter(Qt.Horizontal)
    self.splitter.addWidget(self.main_content)
    self.splitter.addWidget(self.history_panel)

    # 단축키
    toggle_action = QAction("히스토리 토글", self)
    toggle_action.setShortcut(QKeySequence("Ctrl+H"))
    toggle_action.triggered.connect(self.toggle_history_panel)
    self.addAction(toggle_action)

def toggle_history_panel(self):
    visible = not self.history_panel.isVisible()
    self.history_panel.setVisible(visible)
```

## 테스트 실행

```bash
# 단위 테스트
pytest tests/unit/test_history_store.py -v

# UI 테스트 (pytest-qt 필요)
pytest tests/unit/test_history_panel.py -v

# 전체 테스트
pytest --cov=src
```

## 주요 파일

| 파일 | 설명 |
|------|------|
| `src/core/history_store.py` | HistoryEntry, HistoryStore |
| `src/ui/history_panel.py` | HistoryPanel 위젯 |
| `src/ui/main_window.py` | 패널 통합, 단축키 |
| `tests/unit/test_history_store.py` | 저장소 테스트 |
| `tests/unit/test_history_panel.py` | UI 테스트 |
