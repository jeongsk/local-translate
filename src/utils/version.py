"""Version comparison utilities."""

from packaging.version import Version


def normalize_version(version_str: str) -> str:
    """
    Normalize version string by removing 'v' prefix.

    Args:
        version_str: Version string (e.g., "v1.0.0" or "1.0.0")

    Returns:
        Normalized version string without 'v' prefix
    """
    return version_str.lstrip("v")


def parse_version(version_str: str) -> Version:
    """
    Parse version string into Version object.

    Args:
        version_str: Version string (e.g., "v1.0.0" or "1.0.0")

    Returns:
        Version object for comparison

    Raises:
        InvalidVersion: If version string is invalid
    """
    normalized = normalize_version(version_str)
    return Version(normalized)


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.

    Args:
        version1: First version string
        version2: Second version string

    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2

    Raises:
        InvalidVersion: If either version string is invalid
    """
    v1 = parse_version(version1)
    v2 = parse_version(version2)

    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


def is_newer_version(current: str, latest: str) -> bool:
    """
    Check if the latest version is newer than the current version.

    Args:
        current: Current version string
        latest: Latest available version string

    Returns:
        True if latest > current, False otherwise
    """
    return compare_versions(current, latest) < 0
