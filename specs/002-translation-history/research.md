# Research: 번역 히스토리 (Translation History)

**Date**: 2025-12-27
**Feature Branch**: `002-translation-history`

## 1. QSettings를 이용한 복잡한 데이터 저장

### Decision
QSettings의 `beginWriteArray`/`endArray` 메서드를 사용하여 히스토리 항목 리스트를 저장한다.

### Rationale
- 프로젝트에서 이미 QSettings 패턴을 preferences.py에서 사용 중
- 별도 데이터베이스(SQLite) 없이 간단한 로컬 저장 가능
- macOS에서 자동으로 plist 파일로 저장되어 시스템 통합 우수
- 50개 항목 제한으로 성능 문제 없음

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| SQLite | 50개 항목에 과도한 복잡성, 새 의존성 불필요 |
| JSON 파일 직접 관리 | QSettings가 이미 제공하는 기능, 동시 접근 처리 필요 |
| pickle | 보안 문제, 버전 호환성 문제 |

### Implementation Pattern
```python
# 저장
settings.beginWriteArray("history/entries")
for i, entry in enumerate(entries):
    settings.setArrayIndex(i)
    settings.setValue("id", entry.id)
    settings.setValue("source_text", entry.source_text)
    # ...
settings.endArray()

# 로드
count = settings.beginReadArray("history/entries")
for i in range(count):
    settings.setArrayIndex(i)
    entry = HistoryEntry(
        id=settings.value("id"),
        source_text=settings.value("source_text"),
        # ...
    )
settings.endArray()
```

---

## 2. PySide6 사이드 패널 구현 패턴

### Decision
QSplitter를 사용하여 메인 콘텐츠와 히스토리 패널을 분리하고, 패널 표시/숨김을 토글한다.

### Rationale
- QSplitter는 리사이즈 가능한 분할 뷰 제공
- 사용자가 패널 너비를 조절 가능
- 숨김 시 splitter sizes를 저장하여 복원 가능
- QDockWidget보다 단순하고 데스크톱 앱에 적합

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| QDockWidget | 플로팅/도킹 기능 불필요, 과도한 복잡성 |
| QStackedWidget | 탭 전환 방식으로 동시 뷰 불가 |
| 별도 윈도우 | UX 저하, 윈도우 관리 복잡 |

### Implementation Pattern
```python
# MainWindow에서
self.splitter = QSplitter(Qt.Horizontal)
self.splitter.addWidget(self.main_content)
self.splitter.addWidget(self.history_panel)

# 토글
def toggle_history_panel(self):
    if self.history_panel.isVisible():
        self.saved_sizes = self.splitter.sizes()
        self.history_panel.hide()
    else:
        self.history_panel.show()
        if self.saved_sizes:
            self.splitter.setSizes(self.saved_sizes)
```

---

## 3. 히스토리 항목 리스트 UI 패턴

### Decision
QListWidget과 커스텀 QWidget을 사용하여 히스토리 항목을 표시한다.

### Rationale
- QListWidget은 간단한 리스트 UI에 적합
- setItemWidget()으로 커스텀 위젯 삽입 가능
- 내장 검색/필터링 미지원이지만 50개 항목으로 직접 구현 가능
- 성능 최적화 불필요 (항목 수 적음)

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| QTableView + QAbstractItemModel | 50개 항목에 과도한 복잡성 |
| QListView + delegate | 커스텀 위젯보다 구현 복잡 |
| 순수 QScrollArea | 리스트 관리 기능 직접 구현 필요 |

### Implementation Pattern
```python
class HistoryItemWidget(QWidget):
    """개별 히스토리 항목 위젯"""
    copyClicked = Signal(str)  # entry_id
    deleteClicked = Signal(str)
    itemClicked = Signal(str)

class HistoryPanel(QWidget):
    def add_entry(self, entry: HistoryEntry):
        item = QListWidgetItem()
        widget = HistoryItemWidget(entry)
        item.setSizeHint(widget.sizeHint())
        self.list_widget.insertItem(0, item)
        self.list_widget.setItemWidget(item, widget)
```

---

## 4. 검색 필터링 구현

### Decision
QLineEdit의 textChanged 시그널에 디바운싱을 적용하여 실시간 필터링한다.

### Rationale
- 50개 항목에서 문자열 검색은 즉시 완료 (성능 문제 없음)
- 디바운싱으로 타이핑 중 과도한 업데이트 방지
- 원문과 번역문 모두에서 대소문자 무시 검색

### Implementation Pattern
```python
def __init__(self):
    self.search_input = QLineEdit()
    self.search_timer = QTimer()
    self.search_timer.setSingleShot(True)
    self.search_timer.timeout.connect(self._apply_filter)
    self.search_input.textChanged.connect(self._on_search_changed)

def _on_search_changed(self, text: str):
    self.search_timer.start(150)  # 150ms 디바운스

def _apply_filter(self):
    query = self.search_input.text().lower()
    for i in range(self.list_widget.count()):
        item = self.list_widget.item(i)
        widget = self.list_widget.itemWidget(item)
        visible = query in widget.source_text.lower() or query in widget.translated_text.lower()
        item.setHidden(not visible)
```

---

## 5. 단축키 충돌 확인

### Decision
`Cmd+H` (macOS) / `Ctrl+H` (다른 플랫폼)를 히스토리 패널 토글에 사용한다.

### Rationale
- macOS에서 Cmd+H는 기본적으로 "Hide" 기능이지만, Qt 앱에서 오버라이드 가능
- "History"의 H로 직관적
- 기존 앱 단축키 (Cmd+Enter: 번역, Cmd+C: 복사)와 충돌 없음

### Implementation Pattern
```python
# MainWindow에서
self.toggle_history_action = QAction("히스토리 토글", self)
self.toggle_history_action.setShortcut(QKeySequence("Ctrl+H"))  # macOS에서 Cmd+H로 매핑됨
self.toggle_history_action.triggered.connect(self.toggle_history_panel)
self.addAction(self.toggle_history_action)
```

---

## 6. 고유 ID 생성 전략

### Decision
UUID4의 첫 8자리를 히스토리 항목 ID로 사용한다.

### Rationale
- 50개 항목에서 충돌 확률 무시 가능
- 시간 기반 ID보다 짧고 충분히 유니크
- 기존 translator.py에서 task_id에 동일 패턴 사용 중

### Implementation Pattern
```python
import uuid

def generate_id() -> str:
    return uuid.uuid4().hex[:8]
```

---

## Summary

모든 기술적 결정이 기존 프로젝트 패턴을 따르며, 새로운 의존성 없이 구현 가능하다.

| 영역 | 결정 |
|------|------|
| 저장소 | QSettings beginWriteArray |
| UI 레이아웃 | QSplitter 사이드 패널 |
| 리스트 UI | QListWidget + 커스텀 위젯 |
| 검색 | 디바운스 필터링 |
| 단축키 | Cmd+H / Ctrl+H |
| ID 생성 | UUID4[:8] |
