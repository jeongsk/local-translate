"""Unit tests for AboutDialog."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from core.config import config
from ui.about_dialog import AboutDialog


class TestAboutDialog:
    """Test suite for AboutDialog."""

    def test_dialog_creation(self, qapp):
        """Test that AboutDialog can be created."""
        dialog = AboutDialog()
        assert dialog is not None
        assert dialog.windowTitle() == f"About {config.app_name}"

    def test_displays_app_name(self, qapp):
        """Test that dialog displays the app name."""
        dialog = AboutDialog()
        # Check that the app name appears in the dialog
        assert config.app_name in dialog._get_about_text()

    def test_displays_version(self, qapp):
        """Test that dialog displays the version."""
        dialog = AboutDialog()
        assert config.version in dialog._get_about_text()

    def test_displays_copyright(self, qapp):
        """Test that dialog displays copyright information."""
        dialog = AboutDialog()
        text = dialog._get_about_text()
        assert config.copyright_year in text
        assert "Copyright" in text or "©" in text

    def test_displays_license(self, qapp):
        """Test that dialog displays license information."""
        dialog = AboutDialog()
        assert config.license_type in dialog._get_about_text()

    def test_displays_github_link(self, qapp):
        """Test that dialog displays GitHub link."""
        dialog = AboutDialog()
        text = dialog._get_about_text()
        assert config.github_url in text or "github" in text.lower()

    def test_dialog_can_be_closed(self, qapp):
        """Test that dialog can be closed."""
        dialog = AboutDialog()
        dialog.show()
        assert dialog.isVisible()
        dialog.close()
        assert not dialog.isVisible()

    def test_dialog_has_close_button(self, qapp):
        """Test that dialog has a close/OK button."""
        dialog = AboutDialog()
        # Find OK/Close button
        buttons = dialog.findChildren(type(dialog._close_button))
        assert len(buttons) >= 1

    def test_github_link_is_clickable(self, qapp):
        """Test that GitHub link label has openExternalLinks enabled."""
        dialog = AboutDialog()
        link_label = dialog._github_link
        assert link_label.openExternalLinks() is True
