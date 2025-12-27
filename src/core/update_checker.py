"""Update checker for checking new versions on GitHub Releases."""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from core.config import config
from utils.logger import get_logger
from utils.version import is_newer_version, normalize_version

logger = get_logger(__name__)


class UpdateStatus(Enum):
    """Update check status."""

    CHECKING = "checking"
    UP_TO_DATE = "up_to_date"
    UPDATE_AVAILABLE = "update_available"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class ReleaseInfo:
    """Information about a GitHub release."""

    version: str
    tag_name: str
    html_url: str
    is_prerelease: bool
    published_at: str

    @classmethod
    def from_github_response(cls, data: dict) -> "ReleaseInfo":
        """
        Create ReleaseInfo from GitHub API response.

        Args:
            data: GitHub API response dictionary

        Returns:
            ReleaseInfo instance
        """
        return cls(
            version=normalize_version(data["tag_name"]),
            tag_name=data["tag_name"],
            html_url=data["html_url"],
            is_prerelease=data.get("prerelease", False),
            published_at=data.get("published_at", ""),
        )


@dataclass
class UpdateCheckResult:
    """Result of an update check."""

    status: UpdateStatus
    current_version: str
    latest_release: ReleaseInfo | None = None
    error_message: str | None = None

    @property
    def is_update_available(self) -> bool:
        """Check if an update is available."""
        return self.status == UpdateStatus.UPDATE_AVAILABLE

    @property
    def download_url(self) -> str | None:
        """Get the download URL if available."""
        return self.latest_release.html_url if self.latest_release else None


class UpdateChecker:
    """Checks for updates using GitHub Releases API."""

    DEFAULT_TIMEOUT = 15  # seconds

    def __init__(
        self,
        current_version: str | None = None,
        api_url: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the update checker.

        Args:
            current_version: Current app version (defaults to config.version)
            api_url: GitHub API URL (defaults to config.github_api_url)
            timeout: Request timeout in seconds
        """
        self.current_version = current_version or config.version
        self.api_url = api_url or config.github_api_url
        self.timeout = timeout

    def check(self) -> UpdateCheckResult:
        """
        Check for updates.

        Returns:
            UpdateCheckResult with status and release info
        """
        logger.info(f"Checking for updates (current version: {self.current_version})")

        try:
            release_data = self._fetch_latest_release()

            # Skip prereleases and drafts
            if release_data.get("prerelease", False) or release_data.get("draft", False):
                logger.info("Latest release is prerelease or draft, skipping")
                return UpdateCheckResult(
                    status=UpdateStatus.UP_TO_DATE,
                    current_version=self.current_version,
                )

            release_info = ReleaseInfo.from_github_response(release_data)
            logger.info(f"Latest release: {release_info.version}")

            # Compare versions
            if is_newer_version(self.current_version, release_info.version):
                logger.info(f"Update available: {release_info.version}")
                return UpdateCheckResult(
                    status=UpdateStatus.UPDATE_AVAILABLE,
                    current_version=self.current_version,
                    latest_release=release_info,
                )
            else:
                logger.info("Already up to date")
                return UpdateCheckResult(
                    status=UpdateStatus.UP_TO_DATE,
                    current_version=self.current_version,
                    latest_release=release_info,
                )

        except HTTPError as e:
            if e.code == 403:
                logger.warning("GitHub API rate limit exceeded")
                return UpdateCheckResult(
                    status=UpdateStatus.RATE_LIMITED,
                    current_version=self.current_version,
                    error_message="GitHub API 요청 한도를 초과했습니다. 나중에 다시 시도해주세요.",
                )
            elif e.code == 404:
                logger.warning("No releases found")
                return UpdateCheckResult(
                    status=UpdateStatus.ERROR,
                    current_version=self.current_version,
                    error_message="릴리스 정보를 찾을 수 없습니다.",
                )
            else:
                logger.error(f"HTTP error: {e.code} {e.reason}")
                return UpdateCheckResult(
                    status=UpdateStatus.ERROR,
                    current_version=self.current_version,
                    error_message=f"서버 오류가 발생했습니다: {e.code}",
                )

        except URLError as e:
            logger.error(f"Network error: {e.reason}")
            return UpdateCheckResult(
                status=UpdateStatus.ERROR,
                current_version=self.current_version,
                error_message="네트워크 연결을 확인해주세요.",
            )

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return UpdateCheckResult(
                status=UpdateStatus.ERROR,
                current_version=self.current_version,
                error_message=f"예상치 못한 오류가 발생했습니다: {str(e)}",
            )

    def _fetch_latest_release(self) -> dict[str, Any]:
        """
        Fetch the latest release from GitHub API.

        Returns:
            Dictionary containing release data

        Raises:
            HTTPError: On HTTP errors
            URLError: On network errors
        """
        url = f"{self.api_url}/releases/latest"
        headers = {
            "User-Agent": f"{config.app_name}/{config.version}",
            "Accept": "application/vnd.github.v3+json",
        }

        request = Request(url, headers=headers)
        logger.debug(f"Fetching: {url}")

        with urlopen(request, timeout=self.timeout) as response:
            data: dict[str, Any] = json.loads(response.read().decode("utf-8"))
            return data
