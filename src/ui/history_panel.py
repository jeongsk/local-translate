"""History panel widget for displaying translation history.

This module provides the side panel UI for viewing, searching, and managing
translation history entries.
"""


from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.config import config
from core.history_store import HistoryEntry, HistoryStore
from ui.history_item import HistoryItemWidget


class HistoryPanel(QWidget):
    """Side panel for displaying and managing translation history.

    Signals:
        entrySelected: Emitted when a history entry is selected (HistoryEntry)
        copyRequested: Emitted when copy is requested (translated_text)
        collapsedChanged: Emitted when collapsed state changes (is_collapsed)
    """

    entrySelected = Signal(object)  # HistoryEntry
    copyRequested = Signal(str)  # translated_text
    collapsedChanged = Signal(bool)  # is_collapsed

    def __init__(
        self,
        history_store: HistoryStore,
        parent: QWidget | None = None,
    ):
        """Initialize the history panel.

        Args:
            history_store: The history store to display
            parent: Optional parent widget
        """
        super().__init__(parent)
        self._store = history_store
        self._item_widgets: dict[str, HistoryItemWidget] = {}
        self._is_collapsed = False
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(config.history.search_debounce_ms)
        self._search_timer.timeout.connect(self._apply_filter)

        self._setup_ui()
        self._connect_signals()
        self._refresh_list()

    def _setup_ui(self) -> None:
        """Set up the panel UI."""
        self._expanded_width = 320
        self._collapsed_width = 36

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Collapsed bar (shown when collapsed)
        self._collapsed_bar = QWidget()
        self._collapsed_bar.setFixedWidth(self._collapsed_width)
        collapsed_layout = QVBoxLayout(self._collapsed_bar)
        collapsed_layout.setContentsMargins(4, 8, 4, 8)
        collapsed_layout.setSpacing(4)

        self._expand_btn = QPushButton("◀")
        self._expand_btn.setObjectName("expandButton")
        self._expand_btn.setFixedSize(28, 28)
        self._expand_btn.setToolTip("히스토리 패널 펼치기")
        self._expand_btn.clicked.connect(self._on_expand_clicked)
        self._expand_btn.setStyleSheet("""
            QPushButton#expandButton {
                border: 1px solid palette(mid);
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton#expandButton:hover {
                background-color: palette(mid);
            }
        """)
        collapsed_layout.addWidget(self._expand_btn)

        # Vertical label for collapsed state
        self._collapsed_label = QLabel("기\n록")
        self._collapsed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._collapsed_label.setStyleSheet("font-size: 12px; color: palette(text);")
        collapsed_layout.addWidget(self._collapsed_label)
        collapsed_layout.addStretch()

        self._collapsed_bar.hide()
        main_layout.addWidget(self._collapsed_bar)

        # Expanded content (main panel)
        self._expanded_content = QWidget()
        self._expanded_content.setMinimumWidth(280)
        self._expanded_content.setMaximumWidth(400)
        content_layout = QVBoxLayout(self._expanded_content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Collapse button
        self._collapse_btn = QPushButton("▶")
        self._collapse_btn.setObjectName("collapseButton")
        self._collapse_btn.setFixedSize(24, 24)
        self._collapse_btn.setToolTip("히스토리 패널 접기")
        self._collapse_btn.clicked.connect(self._on_collapse_clicked)
        self._collapse_btn.setStyleSheet("""
            QPushButton#collapseButton {
                border: 1px solid palette(mid);
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton#collapseButton:hover {
                background-color: palette(mid);
            }
        """)
        header_layout.addWidget(self._collapse_btn)

        title_label = QLabel("번역 기록")
        title_label.setObjectName("historyTitle")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self._clear_all_btn = QPushButton("전체 삭제")
        self._clear_all_btn.setObjectName("clearAllButton")
        self._clear_all_btn.setFixedWidth(70)
        header_layout.addWidget(self._clear_all_btn)

        content_layout.addLayout(header_layout)

        # Search input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("검색...")
        self._search_input.setClearButtonEnabled(True)
        content_layout.addWidget(self._search_input)

        # Scroll area for history items
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        # Container for items
        self._items_container = QWidget()
        self._items_layout = QVBoxLayout(self._items_container)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSpacing(8)
        self._items_layout.addStretch()

        self._scroll_area.setWidget(self._items_container)
        content_layout.addWidget(self._scroll_area, 1)

        # Empty state label
        self._empty_label = QLabel("번역 기록이 없습니다")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: palette(placeholderText);")
        content_layout.addWidget(self._empty_label)

        # No results label (for search)
        self._no_results_label = QLabel("검색 결과가 없습니다")
        self._no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_results_label.setStyleSheet("color: palette(placeholderText);")
        self._no_results_label.hide()
        content_layout.addWidget(self._no_results_label)

        main_layout.addWidget(self._expanded_content)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        # Store signals
        self._store.entryAdded.connect(self._on_entry_added)
        self._store.entryRemoved.connect(self._on_entry_removed)
        self._store.entriesCleared.connect(self._on_entries_cleared)
        self._store.entriesLoaded.connect(self._refresh_list)

        # UI signals
        self._search_input.textChanged.connect(self._on_search_changed)
        self._clear_all_btn.clicked.connect(self._on_clear_all_clicked)

    def _refresh_list(self) -> None:
        """Refresh the list from the history store."""
        # Clear existing items
        for widget in self._item_widgets.values():
            self._items_layout.removeWidget(widget)
            widget.deleteLater()
        self._item_widgets.clear()

        # Add items from store
        for entry in self._store.entries:
            self._add_item_widget(entry)

        self._update_empty_state()

    def _add_item_widget(self, entry: HistoryEntry) -> None:
        """Add a widget for the given entry.

        Args:
            entry: The history entry to add
        """
        widget = HistoryItemWidget(entry)
        widget.clicked.connect(self._on_item_clicked)
        widget.deleteClicked.connect(self._on_item_delete_clicked)
        widget.copyClicked.connect(self._on_item_copy_clicked)

        # Insert at the beginning (after existing items, before stretch)
        insert_index = self._items_layout.count() - 1  # Before the stretch
        self._items_layout.insertWidget(insert_index, widget)
        self._item_widgets[entry.id] = widget

    def _remove_item_widget(self, entry_id: str) -> None:
        """Remove the widget for the given entry ID.

        Args:
            entry_id: The entry ID to remove
        """
        if entry_id in self._item_widgets:
            widget = self._item_widgets.pop(entry_id)
            self._items_layout.removeWidget(widget)
            widget.deleteLater()

    def _update_empty_state(self) -> None:
        """Update visibility of empty state elements."""
        has_items = len(self._item_widgets) > 0
        has_search = bool(self._search_input.text())

        self._scroll_area.setVisible(has_items)
        self._empty_label.setVisible(not has_items and not has_search)
        self._no_results_label.hide()  # Handled by filter

    @Slot(object)
    def _on_entry_added(self, entry: HistoryEntry) -> None:
        """Handle new entry added to store.

        Args:
            entry: The new history entry
        """
        self._add_item_widget(entry)
        self._update_empty_state()

        # Re-apply filter if search is active
        if self._search_input.text():
            self._apply_filter()

    @Slot(str)
    def _on_entry_removed(self, entry_id: str) -> None:
        """Handle entry removed from store.

        Args:
            entry_id: The removed entry ID
        """
        self._remove_item_widget(entry_id)
        self._update_empty_state()

    @Slot()
    def _on_entries_cleared(self) -> None:
        """Handle all entries cleared from store."""
        self._refresh_list()

    @Slot(str)
    def _on_item_clicked(self, entry_id: str) -> None:
        """Handle item click.

        Args:
            entry_id: The clicked entry ID
        """
        entry = self._store.get(entry_id)
        if entry:
            self.entrySelected.emit(entry)

    @Slot(str)
    def _on_item_delete_clicked(self, entry_id: str) -> None:
        """Handle item delete button click.

        Args:
            entry_id: The entry ID to delete
        """
        self._store.remove(entry_id)

    @Slot(str)
    def _on_item_copy_clicked(self, entry_id: str) -> None:
        """Handle item copy button click.

        Args:
            entry_id: The entry ID to copy
        """
        entry = self._store.get(entry_id)
        if entry:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(entry.translated_text)
            self.copyRequested.emit(entry.translated_text)

    @Slot()
    def _on_clear_all_clicked(self) -> None:
        """Handle clear all button click."""
        if self._store.count == 0:
            return

        reply = QMessageBox.question(
            self,
            "전체 삭제",
            "모든 번역 기록을 삭제하시겠습니까?\n이 작업은 취소할 수 없습니다.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._store.clear()

    @Slot(str)
    def _on_search_changed(self, text: str) -> None:
        """Handle search input change.

        Args:
            text: The new search text
        """
        self._search_timer.start()

    @Slot()
    def _apply_filter(self) -> None:
        """Apply search filter to the list."""
        query = self._search_input.text().lower()

        if not query:
            # Show all items
            for widget in self._item_widgets.values():
                widget.show()
            self._no_results_label.hide()
            self._update_empty_state()
            return

        # Filter items
        visible_count = 0
        for _entry_id, widget in self._item_widgets.items():
            entry = widget.entry
            matches = (
                query in entry.source_text.lower()
                or query in entry.translated_text.lower()
            )
            widget.setVisible(matches)
            if matches:
                visible_count += 1

        # Show no results message if needed
        self._no_results_label.setVisible(visible_count == 0 and len(self._item_widgets) > 0)
        self._scroll_area.setVisible(visible_count > 0)
        self._empty_label.hide()

    # Collapse/Expand functionality

    @property
    def is_collapsed(self) -> bool:
        """Check if the panel is collapsed."""
        return self._is_collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        """Set the collapsed state of the panel.

        Args:
            collapsed: True to collapse, False to expand
        """
        if self._is_collapsed == collapsed:
            return

        self._is_collapsed = collapsed
        self._collapsed_bar.setVisible(collapsed)
        self._expanded_content.setVisible(not collapsed)

        # Update size constraints
        if collapsed:
            self.setFixedWidth(self._collapsed_width)
        else:
            self.setMinimumWidth(280)
            self.setMaximumWidth(400)
            self.setFixedWidth(self._expanded_width)
            # Remove fixed width constraint after setting
            self.setMinimumWidth(280)
            self.setMaximumWidth(400)

        self.collapsedChanged.emit(collapsed)

    @Slot()
    def _on_collapse_clicked(self) -> None:
        """Handle collapse button click."""
        self.set_collapsed(True)

    @Slot()
    def _on_expand_clicked(self) -> None:
        """Handle expand button click."""
        self.set_collapsed(False)

    def toggle_collapsed(self) -> None:
        """Toggle the collapsed state."""
        self.set_collapsed(not self._is_collapsed)
