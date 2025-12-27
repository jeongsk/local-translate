"""History item widget for displaying individual translation history entries.

This module provides the widget for rendering a single history entry with
preview text, language info, timestamp, and action buttons.
"""


from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.history_store import HistoryEntry


class HistoryItemWidget(QFrame):
    """Widget for displaying a single history entry.

    Signals:
        clicked: Emitted when the item is clicked (entry_id)
        deleteClicked: Emitted when delete button is clicked (entry_id)
        copyClicked: Emitted when copy button is clicked (entry_id)
    """

    clicked = Signal(str)  # entry_id
    deleteClicked = Signal(str)  # entry_id
    copyClicked = Signal(str)  # entry_id

    def __init__(self, entry: HistoryEntry, parent: QWidget | None = None):
        """Initialize the history item widget.

        Args:
            entry: The history entry to display
            parent: Optional parent widget
        """
        super().__init__(parent)
        self._entry = entry
        self._setup_ui()
        self._apply_styles()

    @property
    def entry(self) -> HistoryEntry:
        """Get the associated history entry."""
        return self._entry

    @property
    def entry_id(self) -> str:
        """Get the entry ID."""
        return self._entry.id

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(8)

        # Content section (left)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        # Preview text
        self._preview_label = QLabel(self._entry.preview())
        self._preview_label.setWordWrap(True)
        self._preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        content_layout.addWidget(self._preview_label)

        # Meta info (language and time)
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(8)

        # Language pair
        lang_text = f"{self._entry.source_lang} → {self._entry.target_lang}"
        self._lang_label = QLabel(lang_text)
        self._lang_label.setObjectName("langLabel")
        meta_layout.addWidget(self._lang_label)

        # Timestamp
        time_text = self._entry.created_at.strftime("%Y-%m-%d %H:%M")
        self._time_label = QLabel(time_text)
        self._time_label.setObjectName("timeLabel")
        meta_layout.addWidget(self._time_label)

        meta_layout.addStretch()
        content_layout.addLayout(meta_layout)

        main_layout.addLayout(content_layout, 1)

        # Action buttons (right)
        button_layout = QVBoxLayout()
        button_layout.setSpacing(4)

        # Copy button
        self._copy_btn = QPushButton("복사")
        self._copy_btn.setObjectName("copyButton")
        self._copy_btn.setFixedWidth(50)
        self._copy_btn.clicked.connect(self._on_copy_clicked)
        button_layout.addWidget(self._copy_btn)

        # Delete button
        self._delete_btn = QPushButton("삭제")
        self._delete_btn.setObjectName("deleteButton")
        self._delete_btn.setFixedWidth(50)
        self._delete_btn.clicked.connect(self._on_delete_clicked)
        button_layout.addWidget(self._delete_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    def _apply_styles(self) -> None:
        """Apply styles to the widget."""
        # Note: Styles are applied via ThemeManager in styles.py
        # Only set minimal frame-specific styles here
        pass

    def mousePressEvent(self, event: any) -> None:
        """Handle mouse press to emit clicked signal."""
        # Only emit if not clicking on a button
        if not self._copy_btn.underMouse() and not self._delete_btn.underMouse():
            self.clicked.emit(self._entry.id)
        super().mousePressEvent(event)

    def _on_copy_clicked(self) -> None:
        """Handle copy button click."""
        self.copyClicked.emit(self._entry.id)

    def _on_delete_clicked(self) -> None:
        """Handle delete button click."""
        self.deleteClicked.emit(self._entry.id)
