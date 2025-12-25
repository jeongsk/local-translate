"""User preferences persistence using QSettings."""

from PySide6.QtCore import QSettings, QByteArray
from typing import Optional
from enum import Enum

from core.config import LanguageCode


class Theme(str, Enum):
    """Theme preference options."""

    AUTO = "auto"
    LIGHT = "light"
    DARK = "dark"


class UserPreferences:
    """Manages user preferences using QSettings."""

    SETTINGS_VERSION = 1

    def __init__(self, organization: str = "OpenDeepL", application: str = "OpenDeepL"):
        """
        Initialize preferences manager.

        Args:
            organization: Organization name for QSettings
            application: Application name for QSettings
        """
        self._settings = QSettings(organization, application)
        self._migrate_if_needed()

    # Language preferences

    @property
    def source_language(self) -> str:
        """Get source language preference."""
        return self._settings.value("language/source", LanguageCode.AUTO.value, type=str)

    @source_language.setter
    def source_language(self, value: str) -> None:
        """Set source language preference."""
        self._settings.setValue("language/source", value)

    @property
    def target_language(self) -> str:
        """Get target language preference."""
        return self._settings.value("language/target", LanguageCode.KOREAN.value, type=str)

    @target_language.setter
    def target_language(self, value: str) -> None:
        """Set target language preference."""
        self._settings.setValue("language/target", value)

    @property
    def auto_detect(self) -> bool:
        """Get auto-detect language preference."""
        return self._settings.value("language/auto_detect", True, type=bool)

    @auto_detect.setter
    def auto_detect(self, value: bool) -> None:
        """Set auto-detect language preference."""
        self._settings.setValue("language/auto_detect", value)

    # Window geometry

    @property
    def window_geometry(self) -> Optional[QByteArray]:
        """Get window geometry."""
        value = self._settings.value("window/geometry")
        if value is not None:
            return QByteArray(value)
        return None

    @window_geometry.setter
    def window_geometry(self, value: QByteArray) -> None:
        """Set window geometry."""
        self._settings.setValue("window/geometry", value)

    @property
    def window_state(self) -> Optional[QByteArray]:
        """Get window state."""
        value = self._settings.value("window/state")
        if value is not None:
            return QByteArray(value)
        return None

    @window_state.setter
    def window_state(self, value: QByteArray) -> None:
        """Set window state."""
        self._settings.setValue("window/state", value)

    # Theme preference

    @property
    def theme(self) -> Theme:
        """Get theme preference."""
        value = self._settings.value("appearance/theme", Theme.AUTO.value, type=str)
        try:
            return Theme(value)
        except ValueError:
            return Theme.AUTO

    @theme.setter
    def theme(self, value: Theme) -> None:
        """Set theme preference."""
        self._settings.setValue("appearance/theme", value.value)

    @property
    def dark_mode(self) -> bool:
        """Get dark mode preference (simpler alternative to theme)."""
        return self._settings.value("appearance/dark_mode", False, type=bool)

    @dark_mode.setter
    def dark_mode(self, value: bool) -> None:
        """Set dark mode preference."""
        self._settings.setValue("appearance/dark_mode", value)

    # Utility methods

    def sync(self) -> None:
        """Force write settings to disk."""
        self._settings.sync()

    def clear(self) -> None:
        """Clear all settings."""
        self._settings.clear()

    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        self.clear()
        # Trigger default values by reading
        _ = self.source_language
        _ = self.target_language
        _ = self.auto_detect
        _ = self.theme
        self.sync()

    # Migration support

    def _migrate_if_needed(self) -> None:
        """Migrate settings from old versions if needed."""
        current_version = self._settings.value("schema/version", 0, type=int)

        if current_version < 1:
            self._migrate_v0_to_v1()

        # Update version
        if current_version < self.SETTINGS_VERSION:
            self._settings.setValue("schema/version", self.SETTINGS_VERSION)
            self.sync()

    def _migrate_v0_to_v1(self) -> None:
        """
        Migrate from version 0 to version 1.
        Version 0: No schema version, potential legacy keys
        Version 1: Current schema with versioning
        """
        # Example migration: rename old keys if they exist
        if self._settings.contains("source_lang"):
            value = self._settings.value("source_lang")
            self._settings.setValue("language/source", value)
            self._settings.remove("source_lang")

        if self._settings.contains("target_lang"):
            value = self._settings.value("target_lang")
            self._settings.setValue("language/target", value)
            self._settings.remove("target_lang")

        # Set default values if not present
        if not self._settings.contains("language/source"):
            self.source_language = LanguageCode.AUTO.value

        if not self._settings.contains("language/target"):
            self.target_language = LanguageCode.KOREAN.value

        if not self._settings.contains("language/auto_detect"):
            self.auto_detect = True

        if not self._settings.contains("appearance/theme"):
            self.theme = Theme.AUTO
