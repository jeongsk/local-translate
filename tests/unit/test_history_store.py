"""Unit tests for HistoryEntry and HistoryStore."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QSettings

from core.history_store import HistoryEntry, HistoryStore


class TestHistoryEntry:
    """Tests for HistoryEntry dataclass."""

    def test_create_generates_unique_id(self) -> None:
        """HistoryEntry.create() should generate unique 8-char hex IDs."""
        entry1 = HistoryEntry.create("Hello", "안녕", "en", "ko")
        entry2 = HistoryEntry.create("Hello", "안녕", "en", "ko")

        assert len(entry1.id) == 8
        assert len(entry2.id) == 8
        assert entry1.id != entry2.id

    def test_create_sets_timestamp(self) -> None:
        """HistoryEntry.create() should set created_at to current UTC time."""
        before = datetime.utcnow()
        entry = HistoryEntry.create("Hello", "안녕", "en", "ko")
        after = datetime.utcnow()

        assert before <= entry.created_at <= after

    def test_create_stores_text_and_languages(self) -> None:
        """HistoryEntry.create() should store source/target text and languages."""
        entry = HistoryEntry.create(
            source_text="Hello world",
            translated_text="안녕하세요 세계",
            source_lang="en",
            target_lang="ko",
        )

        assert entry.source_text == "Hello world"
        assert entry.translated_text == "안녕하세요 세계"
        assert entry.source_lang == "en"
        assert entry.target_lang == "ko"

    def test_preview_short_text(self) -> None:
        """preview() should return full text if shorter than max_length."""
        entry = HistoryEntry.create("Short text", "짧은 텍스트", "en", "ko")

        assert entry.preview(100) == "Short text"

    def test_preview_long_text_truncates(self) -> None:
        """preview() should truncate long text with ellipsis."""
        long_text = "A" * 150
        entry = HistoryEntry.create(long_text, "번역", "en", "ko")

        preview = entry.preview(100)
        assert len(preview) == 100
        assert preview.endswith("...")
        assert preview == "A" * 97 + "..."

    def test_entry_is_immutable(self) -> None:
        """HistoryEntry should be frozen (immutable)."""
        entry = HistoryEntry.create("Hello", "안녕", "en", "ko")

        with pytest.raises(AttributeError):
            entry.source_text = "Modified"  # type: ignore


class TestHistoryStoreSaveLoad:
    """Tests for HistoryStore save/load functionality."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Create a mock QSettings object."""
        settings = MagicMock(spec=QSettings)
        settings.beginWriteArray = MagicMock()
        settings.endArray = MagicMock()
        settings.setArrayIndex = MagicMock()
        settings.setValue = MagicMock()
        settings.sync = MagicMock()
        settings.beginReadArray = MagicMock(return_value=0)
        settings.value = MagicMock(return_value="")
        return settings

    @pytest.fixture
    def history_store(self, mock_settings: MagicMock) -> HistoryStore:
        """Create a HistoryStore with mock settings."""
        return HistoryStore(mock_settings)

    def test_save_empty_store(
        self, history_store: HistoryStore, mock_settings: MagicMock
    ) -> None:
        """save() should handle empty store correctly."""
        history_store.save()

        mock_settings.beginWriteArray.assert_called_once_with("history/entries")
        mock_settings.endArray.assert_called_once()
        mock_settings.sync.assert_called_once()

    def test_save_with_entries(
        self, history_store: HistoryStore, mock_settings: MagicMock
    ) -> None:
        """save() should persist all entry fields."""
        entry = HistoryEntry(
            id="abc12345",
            source_text="Hello",
            translated_text="안녕",
            source_lang="en",
            target_lang="ko",
            created_at=datetime(2025, 12, 27, 10, 30, 0),
        )
        history_store._entries = [entry]

        history_store.save()

        # Verify setArrayIndex was called
        mock_settings.setArrayIndex.assert_called_with(0)

        # Verify all fields were saved
        calls = mock_settings.setValue.call_args_list
        saved_data = {call[0][0]: call[0][1] for call in calls}

        assert saved_data["id"] == "abc12345"
        assert saved_data["source_text"] == "Hello"
        assert saved_data["translated_text"] == "안녕"
        assert saved_data["source_lang"] == "en"
        assert saved_data["target_lang"] == "ko"
        assert saved_data["created_at"] == "2025-12-27T10:30:00"

    def test_load_empty_store(
        self, history_store: HistoryStore, mock_settings: MagicMock
    ) -> None:
        """load() should handle empty store correctly."""
        mock_settings.beginReadArray.return_value = 0

        history_store.load()

        assert history_store.count == 0
        mock_settings.beginReadArray.assert_called_once_with("history/entries")
        mock_settings.endArray.assert_called_once()

    def test_load_with_entries(
        self, history_store: HistoryStore, mock_settings: MagicMock
    ) -> None:
        """load() should restore all entry fields."""
        mock_settings.beginReadArray.return_value = 1

        def mock_value(key: str, default: str = "") -> str:
            values = {
                "id": "abc12345",
                "source_text": "Hello",
                "translated_text": "안녕",
                "source_lang": "en",
                "target_lang": "ko",
                "created_at": "2025-12-27T10:30:00",
            }
            return values.get(key, default)

        mock_settings.value = mock_value

        history_store.load()

        assert history_store.count == 1
        entry = history_store.entries[0]
        assert entry.id == "abc12345"
        assert entry.source_text == "Hello"
        assert entry.translated_text == "안녕"
        assert entry.source_lang == "en"
        assert entry.target_lang == "ko"
        assert entry.created_at == datetime(2025, 12, 27, 10, 30, 0)

    def test_load_skips_invalid_entries(
        self, history_store: HistoryStore, mock_settings: MagicMock
    ) -> None:
        """load() should skip entries with missing required fields."""
        mock_settings.beginReadArray.return_value = 1

        # Missing id
        def mock_value(key: str, default: str = "") -> str:
            values = {
                "id": "",
                "source_text": "Hello",
            }
            return values.get(key, default)

        mock_settings.value = mock_value

        history_store.load()

        assert history_store.count == 0

    def test_load_emits_signal(
        self, history_store: HistoryStore, mock_settings: MagicMock
    ) -> None:
        """load() should emit entriesLoaded signal."""
        mock_settings.beginReadArray.return_value = 0
        signal_received = []
        history_store.entriesLoaded.connect(lambda: signal_received.append(True))

        history_store.load()

        assert len(signal_received) == 1


class TestHistoryStoreAdd:
    """Tests for HistoryStore.add() method."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Create a mock QSettings object."""
        settings = MagicMock(spec=QSettings)
        settings.beginWriteArray = MagicMock()
        settings.endArray = MagicMock()
        settings.setArrayIndex = MagicMock()
        settings.setValue = MagicMock()
        settings.sync = MagicMock()
        return settings

    @pytest.fixture
    def history_store(self, mock_settings: MagicMock) -> HistoryStore:
        """Create a HistoryStore with mock settings."""
        return HistoryStore(mock_settings)

    def test_add_inserts_at_beginning(self, history_store: HistoryStore) -> None:
        """add() should insert new entries at the beginning (newest first)."""
        entry1 = HistoryEntry.create("First", "첫번째", "en", "ko")
        entry2 = HistoryEntry.create("Second", "두번째", "en", "ko")

        history_store.add(entry1)
        history_store.add(entry2)

        entries = history_store.entries
        assert entries[0].source_text == "Second"
        assert entries[1].source_text == "First"

    def test_add_emits_signal(self, history_store: HistoryStore) -> None:
        """add() should emit entryAdded signal with the entry."""
        entry = HistoryEntry.create("Hello", "안녕", "en", "ko")
        received_entries: list[HistoryEntry] = []
        history_store.entryAdded.connect(lambda e: received_entries.append(e))

        history_store.add(entry)

        assert len(received_entries) == 1
        assert received_entries[0] == entry

    def test_add_respects_max_entries(self, history_store: HistoryStore) -> None:
        """add() should remove oldest entry when exceeding max_entries."""
        history_store._max_entries = 3

        entries = [
            HistoryEntry.create(f"Entry {i}", f"항목 {i}", "en", "ko") for i in range(5)
        ]

        for entry in entries:
            history_store.add(entry)

        assert history_store.count == 3
        # Newest entries should be kept
        assert history_store.entries[0].source_text == "Entry 4"
        assert history_store.entries[2].source_text == "Entry 2"

    def test_add_calls_save(
        self, history_store: HistoryStore, mock_settings: MagicMock
    ) -> None:
        """add() should automatically save to settings."""
        entry = HistoryEntry.create("Hello", "안녕", "en", "ko")

        history_store.add(entry)

        mock_settings.beginWriteArray.assert_called()
        mock_settings.sync.assert_called()


class TestHistoryStoreGet:
    """Tests for HistoryStore.get() method."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Create a mock QSettings object."""
        settings = MagicMock(spec=QSettings)
        settings.beginWriteArray = MagicMock()
        settings.endArray = MagicMock()
        settings.sync = MagicMock()
        return settings

    @pytest.fixture
    def history_store(self, mock_settings: MagicMock) -> HistoryStore:
        """Create a HistoryStore with mock settings."""
        return HistoryStore(mock_settings)

    def test_get_existing_entry(self, history_store: HistoryStore) -> None:
        """get() should return entry with matching ID."""
        entry = HistoryEntry(
            id="test1234",
            source_text="Hello",
            translated_text="안녕",
            source_lang="en",
            target_lang="ko",
            created_at=datetime.utcnow(),
        )
        history_store._entries = [entry]

        result = history_store.get("test1234")

        assert result == entry

    def test_get_nonexistent_entry(self, history_store: HistoryStore) -> None:
        """get() should return None for non-existent ID."""
        result = history_store.get("nonexistent")

        assert result is None


class TestHistoryStoreRemove:
    """Tests for HistoryStore.remove() method."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Create a mock QSettings object."""
        settings = MagicMock(spec=QSettings)
        settings.beginWriteArray = MagicMock()
        settings.endArray = MagicMock()
        settings.sync = MagicMock()
        return settings

    @pytest.fixture
    def history_store(self, mock_settings: MagicMock) -> HistoryStore:
        """Create a HistoryStore with mock settings."""
        return HistoryStore(mock_settings)

    def test_remove_existing_entry(self, history_store: HistoryStore) -> None:
        """remove() should remove entry and return True."""
        entry = HistoryEntry(
            id="test1234",
            source_text="Hello",
            translated_text="안녕",
            source_lang="en",
            target_lang="ko",
            created_at=datetime.utcnow(),
        )
        history_store._entries = [entry]

        result = history_store.remove("test1234")

        assert result is True
        assert history_store.count == 0

    def test_remove_nonexistent_entry(self, history_store: HistoryStore) -> None:
        """remove() should return False for non-existent ID."""
        result = history_store.remove("nonexistent")

        assert result is False

    def test_remove_emits_signal(self, history_store: HistoryStore) -> None:
        """remove() should emit entryRemoved signal with entry ID."""
        entry = HistoryEntry(
            id="test1234",
            source_text="Hello",
            translated_text="안녕",
            source_lang="en",
            target_lang="ko",
            created_at=datetime.utcnow(),
        )
        history_store._entries = [entry]

        removed_ids: list[str] = []
        history_store.entryRemoved.connect(lambda id: removed_ids.append(id))

        history_store.remove("test1234")

        assert removed_ids == ["test1234"]


class TestHistoryStoreClear:
    """Tests for HistoryStore.clear() method."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Create a mock QSettings object."""
        settings = MagicMock(spec=QSettings)
        settings.beginWriteArray = MagicMock()
        settings.endArray = MagicMock()
        settings.sync = MagicMock()
        return settings

    @pytest.fixture
    def history_store(self, mock_settings: MagicMock) -> HistoryStore:
        """Create a HistoryStore with mock settings."""
        return HistoryStore(mock_settings)

    def test_clear_removes_all_entries(self, history_store: HistoryStore) -> None:
        """clear() should remove all entries."""
        history_store._entries = [
            HistoryEntry.create("Hello", "안녕", "en", "ko"),
            HistoryEntry.create("World", "세계", "en", "ko"),
        ]

        history_store.clear()

        assert history_store.count == 0

    def test_clear_emits_signal(self, history_store: HistoryStore) -> None:
        """clear() should emit entriesCleared signal."""
        signal_received = []
        history_store.entriesCleared.connect(lambda: signal_received.append(True))

        history_store.clear()

        assert len(signal_received) == 1


class TestHistoryStoreSearch:
    """Tests for HistoryStore.search() method."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Create a mock QSettings object."""
        return MagicMock(spec=QSettings)

    @pytest.fixture
    def history_store(self, mock_settings: MagicMock) -> HistoryStore:
        """Create a HistoryStore with test entries."""
        store = HistoryStore(mock_settings)
        store._entries = [
            HistoryEntry(
                id="1",
                source_text="Hello world",
                translated_text="안녕하세요 세계",
                source_lang="en",
                target_lang="ko",
                created_at=datetime.utcnow(),
            ),
            HistoryEntry(
                id="2",
                source_text="Good morning",
                translated_text="좋은 아침",
                source_lang="en",
                target_lang="ko",
                created_at=datetime.utcnow(),
            ),
            HistoryEntry(
                id="3",
                source_text="안녕하세요",
                translated_text="Hello",
                source_lang="ko",
                target_lang="en",
                created_at=datetime.utcnow(),
            ),
        ]
        return store

    def test_search_empty_query_returns_all(
        self, history_store: HistoryStore
    ) -> None:
        """search() with empty query should return all entries."""
        results = history_store.search("")

        assert len(results) == 3

    def test_search_matches_source_text(self, history_store: HistoryStore) -> None:
        """search() should find matches in source text."""
        results = history_store.search("Hello")

        assert len(results) == 2
        assert any(e.id == "1" for e in results)
        assert any(e.id == "3" for e in results)

    def test_search_matches_translated_text(
        self, history_store: HistoryStore
    ) -> None:
        """search() should find matches in translated text."""
        results = history_store.search("안녕")

        assert len(results) == 2

    def test_search_case_insensitive(self, history_store: HistoryStore) -> None:
        """search() should be case-insensitive."""
        results = history_store.search("HELLO")

        assert len(results) == 2

    def test_search_no_matches(self, history_store: HistoryStore) -> None:
        """search() should return empty list when no matches."""
        results = history_store.search("xyz123")

        assert len(results) == 0
