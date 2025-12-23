"""Language selection dropdown component."""

from typing import Optional
from PySide6.QtWidgets import QComboBox, QWidget
from PySide6.QtCore import Signal

from ..core.config import SUPPORTED_LANGUAGES, LanguageCode, Language
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LanguageSelector(QComboBox):
    """
    Dropdown component for language selection.

    Signals:
        languageChanged: Emitted when language selection changes (language_code: str)
    """

    languageChanged = Signal(str)  # language code

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        include_auto: bool = True,
        auto_label: str = "자동 감지"
    ):
        """
        Initialize language selector.

        Args:
            parent: Parent widget
            include_auto: Whether to include "Auto Detect" option
            auto_label: Label text for auto-detect option
        """
        super().__init__(parent)

        self.include_auto = include_auto
        self.auto_label = auto_label

        self._populate_languages()
        self._connect_signals()

        logger.info(f"LanguageSelector initialized (auto: {include_auto})")

    def _populate_languages(self) -> None:
        """Populate dropdown with supported languages."""
        self.clear()

        # Add auto-detect option if enabled
        if self.include_auto:
            self.addItem(self.auto_label, LanguageCode.AUTO.value)

        # Add all supported languages sorted by display name
        sorted_languages = sorted(
            SUPPORTED_LANGUAGES.values(),
            key=lambda lang: lang.display_name
        )

        for language in sorted_languages:
            if language.code != LanguageCode.AUTO:
                self.addItem(language.display_name, language.code.value)

        logger.debug(f"Populated {self.count()} languages")

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self.currentIndexChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self, index: int) -> None:
        """
        Handle selection change.

        Args:
            index: New selection index
        """
        if index >= 0:
            code = self.currentData()
            logger.info(f"Language selected: {code} ({self.currentText()})")
            self.languageChanged.emit(code)

    def get_selected_language(self) -> str:
        """
        Get currently selected language code.

        Returns:
            Language code (e.g., "ko", "en", "auto")
        """
        return self.currentData() or LanguageCode.AUTO.value

    def set_language(self, language_code: str) -> bool:
        """
        Set selected language by code.

        Args:
            language_code: Language code to select

        Returns:
            True if language was found and selected, False otherwise
        """
        for i in range(self.count()):
            if self.itemData(i) == language_code:
                self.setCurrentIndex(i)
                logger.debug(f"Language set to: {language_code}")
                return True

        logger.warning(f"Language code not found: {language_code}")
        return False

    def get_language_display_name(self, language_code: str) -> str:
        """
        Get display name for a language code.

        Args:
            language_code: Language code

        Returns:
            Display name or the code itself if not found
        """
        if language_code == LanguageCode.AUTO.value:
            return self.auto_label

        for lang in SUPPORTED_LANGUAGES.values():
            if lang.code.value == language_code:
                return lang.display_name

        return language_code
