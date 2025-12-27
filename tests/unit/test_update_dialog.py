"""Unit tests for UpdateDialog."""

import pytest

from core.update_checker import ReleaseInfo, UpdateCheckResult, UpdateStatus
from ui.update_dialog import UpdateDialog


class TestUpdateDialog:
    """Test suite for UpdateDialog."""

    def test_dialog_creation_up_to_date(self, qapp):
        """Test dialog creation with UP_TO_DATE status."""
        check_result = UpdateCheckResult(
            status=UpdateStatus.UP_TO_DATE,
            current_version="1.0.0",
        )
        dialog = UpdateDialog(check_result)
        assert dialog is not None
        assert "최신" in dialog._message_label.text() or "up to date" in dialog._message_label.text().lower()

    def test_dialog_creation_update_available(self, qapp):
        """Test dialog creation with UPDATE_AVAILABLE status."""
        check_result = UpdateCheckResult(
            status=UpdateStatus.UPDATE_AVAILABLE,
            current_version="0.1.0",
            latest_release=ReleaseInfo(
                version="1.0.0",
                tag_name="v1.0.0",
                html_url="https://example.com/release",
                is_prerelease=False,
                published_at="2024-01-01T00:00:00Z",
            ),
        )
        dialog = UpdateDialog(check_result)
        assert dialog is not None
        # Should show new version info
        assert "1.0.0" in dialog._message_label.text()

    def test_dialog_creation_error(self, qapp):
        """Test dialog creation with ERROR status."""
        check_result = UpdateCheckResult(
            status=UpdateStatus.ERROR,
            current_version="1.0.0",
            error_message="Network connection failed",
        )
        dialog = UpdateDialog(check_result)
        assert dialog is not None
        # Should show error message
        message_text = dialog._message_label.text()
        assert "오류" in message_text or "error" in message_text.lower()

    def test_dialog_creation_rate_limited(self, qapp):
        """Test dialog creation with RATE_LIMITED status."""
        check_result = UpdateCheckResult(
            status=UpdateStatus.RATE_LIMITED,
            current_version="1.0.0",
            error_message="API rate limit exceeded",
        )
        dialog = UpdateDialog(check_result)
        assert dialog is not None

    def test_download_link_enabled_when_update_available(self, qapp):
        """Test that download link is configured when update is available."""
        check_result = UpdateCheckResult(
            status=UpdateStatus.UPDATE_AVAILABLE,
            current_version="0.1.0",
            latest_release=ReleaseInfo(
                version="1.0.0",
                tag_name="v1.0.0",
                html_url="https://example.com/release",
                is_prerelease=False,
                published_at="2024-01-01T00:00:00Z",
            ),
        )
        dialog = UpdateDialog(check_result)
        dialog.show()  # Need to show dialog for visibility to work
        assert dialog._download_link.isVisibleTo(dialog)
        assert dialog._download_link.openExternalLinks() is True

    def test_download_link_hidden_when_up_to_date(self, qapp):
        """Test that download link is hidden when up to date."""
        check_result = UpdateCheckResult(
            status=UpdateStatus.UP_TO_DATE,
            current_version="1.0.0",
        )
        dialog = UpdateDialog(check_result)
        dialog.show()  # Need to show dialog for visibility to work
        assert not dialog._download_link.isVisibleTo(dialog)

    def test_dialog_can_be_closed(self, qapp):
        """Test that dialog can be closed."""
        check_result = UpdateCheckResult(
            status=UpdateStatus.UP_TO_DATE,
            current_version="1.0.0",
        )
        dialog = UpdateDialog(check_result)
        dialog.show()
        assert dialog.isVisible()
        dialog.close()
        assert not dialog.isVisible()
