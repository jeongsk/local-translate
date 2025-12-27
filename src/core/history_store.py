"""Translation history storage and management.

This module provides functionality for storing and retrieving translation history,
including persistence using QSettings and search capabilities.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime

from PySide6.QtCore import QObject, QSettings, Signal

from core.config import config


@dataclass(frozen=True)
class HistoryEntry:
    """Represents a single translation history entry.

    Attributes:
        id: Unique identifier (8-character hex string from UUID4)
        source_text: Original text that was translated
        translated_text: Resulting translated text
        source_lang: Source language code
        target_lang: Target language code
        created_at: Timestamp when translation was performed (UTC)
    """

    id: str
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    created_at: datetime

    @staticmethod
    def create(
        source_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str,
    ) -> "HistoryEntry":
        """Create a new HistoryEntry with auto-generated ID and timestamp.

        Args:
            source_text: Original text
            translated_text: Translated text
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            New HistoryEntry instance
        """
        return HistoryEntry(
            id=uuid.uuid4().hex[:8],
            source_text=source_text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            created_at=datetime.utcnow(),
        )

    def preview(self, max_length: int | None = None) -> str:
        """Get a preview of the source text, truncated if necessary.

        Args:
            max_length: Maximum length for preview. Defaults to config value.

        Returns:
            Source text, truncated with ellipsis if longer than max_length
        """
        if max_length is None:
            max_length = config.history.preview_length

        if len(self.source_text) <= max_length:
            return self.source_text
        return self.source_text[: max_length - 3] + "..."


class HistoryStore(QObject):
    """Manages translation history with persistence.

    Signals:
        entryAdded: Emitted when a new entry is added (HistoryEntry)
        entryRemoved: Emitted when an entry is removed (entry_id: str)
        entriesCleared: Emitted when all entries are cleared
        entriesLoaded: Emitted when entries are loaded from storage
    """

    entryAdded = Signal(object)  # HistoryEntry
    entryRemoved = Signal(str)  # entry_id
    entriesCleared = Signal()
    entriesLoaded = Signal()

    def __init__(self, settings: QSettings, parent: QObject | None = None):
        """Initialize the history store.

        Args:
            settings: QSettings instance for persistence
            parent: Optional parent QObject
        """
        super().__init__(parent)
        self._settings = settings
        self._entries: list[HistoryEntry] = []
        self._max_entries = config.history.max_entries

    @property
    def entries(self) -> list[HistoryEntry]:
        """Get a copy of all history entries (newest first)."""
        return self._entries.copy()

    @property
    def count(self) -> int:
        """Get the number of history entries."""
        return len(self._entries)

    def add(self, entry: HistoryEntry) -> None:
        """Add a new entry to history.

        If the maximum number of entries is exceeded, the oldest entry is removed.

        Args:
            entry: HistoryEntry to add
        """
        self._entries.insert(0, entry)
        if len(self._entries) > self._max_entries:
            self._entries.pop()
        self.save()
        self.entryAdded.emit(entry)

    def get(self, entry_id: str) -> HistoryEntry | None:
        """Get an entry by ID.

        Args:
            entry_id: The entry ID to look up

        Returns:
            HistoryEntry if found, None otherwise
        """
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None

    def remove(self, entry_id: str) -> bool:
        """Remove an entry by ID.

        Args:
            entry_id: The entry ID to remove

        Returns:
            True if entry was removed, False if not found
        """
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id:
                self._entries.pop(i)
                self.save()
                self.entryRemoved.emit(entry_id)
                return True
        return False

    def clear(self) -> None:
        """Remove all history entries."""
        self._entries.clear()
        self.save()
        self.entriesCleared.emit()

    def search(self, query: str) -> list[HistoryEntry]:
        """Search entries by keyword.

        Searches both source and translated text, case-insensitive.

        Args:
            query: Search query string

        Returns:
            List of matching entries (newest first)
        """
        if not query:
            return self.entries

        query_lower = query.lower()
        return [
            e
            for e in self._entries
            if query_lower in e.source_text.lower()
            or query_lower in e.translated_text.lower()
        ]

    def save(self) -> None:
        """Persist entries to QSettings."""
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
        self._settings.sync()

    def load(self) -> None:
        """Load entries from QSettings."""
        count = self._settings.beginReadArray("history/entries")
        self._entries = []
        for i in range(count):
            self._settings.setArrayIndex(i)
            try:
                entry_id = self._settings.value("id", "")
                source_text = self._settings.value("source_text", "")
                translated_text = self._settings.value("translated_text", "")
                source_lang = self._settings.value("source_lang", "")
                target_lang = self._settings.value("target_lang", "")
                created_at_str = self._settings.value(
                    "created_at", datetime.utcnow().isoformat()
                )

                # Skip invalid entries
                if not entry_id or not source_text:
                    continue

                entry = HistoryEntry(
                    id=entry_id,
                    source_text=source_text,
                    translated_text=translated_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    created_at=datetime.fromisoformat(created_at_str),
                )
                self._entries.append(entry)
            except (ValueError, TypeError):
                # Skip entries with invalid data
                continue
        self._settings.endArray()
        self.entriesLoaded.emit()
