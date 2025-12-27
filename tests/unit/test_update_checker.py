"""Unit tests for UpdateChecker."""

import json
from unittest.mock import MagicMock, patch

import pytest

from core.update_checker import (
    ReleaseInfo,
    UpdateCheckResult,
    UpdateChecker,
    UpdateStatus,
)


class TestReleaseInfo:
    """Test suite for ReleaseInfo dataclass."""

    def test_from_github_response(self):
        """Test creating ReleaseInfo from GitHub API response."""
        response = {
            "tag_name": "v1.0.0",
            "html_url": "https://github.com/test/repo/releases/tag/v1.0.0",
            "prerelease": False,
            "published_at": "2024-01-15T10:00:00Z",
        }
        info = ReleaseInfo.from_github_response(response)

        assert info.version == "1.0.0"
        assert info.tag_name == "v1.0.0"
        assert info.html_url == response["html_url"]
        assert info.is_prerelease is False
        assert info.published_at == response["published_at"]

    def test_from_github_response_strips_v_prefix(self):
        """Test that v prefix is stripped from version."""
        response = {
            "tag_name": "v2.1.3",
            "html_url": "https://example.com",
            "prerelease": False,
            "published_at": "2024-01-01T00:00:00Z",
        }
        info = ReleaseInfo.from_github_response(response)
        assert info.version == "2.1.3"


class TestUpdateCheckResult:
    """Test suite for UpdateCheckResult dataclass."""

    def test_is_update_available_when_available(self):
        """Test is_update_available property when update is available."""
        result = UpdateCheckResult(
            status=UpdateStatus.UPDATE_AVAILABLE,
            current_version="0.1.0",
            latest_release=ReleaseInfo(
                version="1.0.0",
                tag_name="v1.0.0",
                html_url="https://example.com",
                is_prerelease=False,
                published_at="2024-01-01T00:00:00Z",
            ),
        )
        assert result.is_update_available is True

    def test_is_update_available_when_up_to_date(self):
        """Test is_update_available property when up to date."""
        result = UpdateCheckResult(
            status=UpdateStatus.UP_TO_DATE,
            current_version="1.0.0",
        )
        assert result.is_update_available is False

    def test_download_url_when_release_available(self):
        """Test download_url property when release info is available."""
        result = UpdateCheckResult(
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
        assert result.download_url == "https://example.com/release"

    def test_download_url_when_no_release(self):
        """Test download_url property when no release info."""
        result = UpdateCheckResult(
            status=UpdateStatus.UP_TO_DATE,
            current_version="1.0.0",
        )
        assert result.download_url is None


class TestUpdateChecker:
    """Test suite for UpdateChecker class."""

    def test_check_returns_up_to_date(self):
        """Test check returns UP_TO_DATE when versions match."""
        mock_response = {
            "tag_name": "v0.1.2",
            "html_url": "https://github.com/test/repo/releases/tag/v0.1.2",
            "prerelease": False,
            "draft": False,
            "published_at": "2024-01-01T00:00:00Z",
        }

        with patch("core.update_checker.urlopen") as mock_urlopen:
            mock_context = MagicMock()
            mock_context.__enter__ = MagicMock(return_value=mock_context)
            mock_context.__exit__ = MagicMock(return_value=False)
            mock_context.read.return_value = json.dumps(mock_response).encode()
            mock_urlopen.return_value = mock_context

            checker = UpdateChecker(current_version="0.1.2")
            result = checker.check()

            assert result.status == UpdateStatus.UP_TO_DATE
            assert result.current_version == "0.1.2"

    def test_check_returns_update_available(self):
        """Test check returns UPDATE_AVAILABLE when new version exists."""
        mock_response = {
            "tag_name": "v1.0.0",
            "html_url": "https://github.com/test/repo/releases/tag/v1.0.0",
            "prerelease": False,
            "draft": False,
            "published_at": "2024-01-01T00:00:00Z",
        }

        with patch("core.update_checker.urlopen") as mock_urlopen:
            mock_context = MagicMock()
            mock_context.__enter__ = MagicMock(return_value=mock_context)
            mock_context.__exit__ = MagicMock(return_value=False)
            mock_context.read.return_value = json.dumps(mock_response).encode()
            mock_urlopen.return_value = mock_context

            checker = UpdateChecker(current_version="0.1.2")
            result = checker.check()

            assert result.status == UpdateStatus.UPDATE_AVAILABLE
            assert result.latest_release is not None
            assert result.latest_release.version == "1.0.0"

    def test_check_returns_error_on_network_failure(self):
        """Test check returns ERROR on network failure."""
        from urllib.error import URLError

        with patch("core.update_checker.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = URLError("Network error")

            checker = UpdateChecker(current_version="0.1.2")
            result = checker.check()

            assert result.status == UpdateStatus.ERROR
            assert result.error_message is not None

    def test_check_returns_error_on_http_error(self):
        """Test check returns ERROR on HTTP error."""
        from urllib.error import HTTPError

        with patch("core.update_checker.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = HTTPError(
                url="https://api.github.com",
                code=404,
                msg="Not Found",
                hdrs={},
                fp=None,
            )

            checker = UpdateChecker(current_version="0.1.2")
            result = checker.check()

            assert result.status == UpdateStatus.ERROR

    def test_check_returns_rate_limited_on_403(self):
        """Test check returns RATE_LIMITED on 403 error."""
        from urllib.error import HTTPError

        with patch("core.update_checker.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = HTTPError(
                url="https://api.github.com",
                code=403,
                msg="Forbidden",
                hdrs={},
                fp=None,
            )

            checker = UpdateChecker(current_version="0.1.2")
            result = checker.check()

            assert result.status == UpdateStatus.RATE_LIMITED

    def test_check_skips_prerelease(self):
        """Test that prerelease versions are skipped."""
        mock_response = {
            "tag_name": "v2.0.0-beta",
            "html_url": "https://github.com/test/repo/releases/tag/v2.0.0-beta",
            "prerelease": True,
            "draft": False,
            "published_at": "2024-01-01T00:00:00Z",
        }

        with patch("core.update_checker.urlopen") as mock_urlopen:
            mock_context = MagicMock()
            mock_context.__enter__ = MagicMock(return_value=mock_context)
            mock_context.__exit__ = MagicMock(return_value=False)
            mock_context.read.return_value = json.dumps(mock_response).encode()
            mock_urlopen.return_value = mock_context

            checker = UpdateChecker(current_version="0.1.2")
            result = checker.check()

            # Should be up to date since prerelease is skipped
            assert result.status == UpdateStatus.UP_TO_DATE
