"""Unit tests for version comparison utilities."""

import pytest
from packaging.version import InvalidVersion

from utils.version import (
    compare_versions,
    is_newer_version,
    normalize_version,
    parse_version,
)


class TestNormalizeVersion:
    """Test suite for normalize_version function."""

    def test_removes_v_prefix(self):
        """Test that v prefix is removed."""
        assert normalize_version("v1.0.0") == "1.0.0"

    def test_handles_no_prefix(self):
        """Test that version without prefix is unchanged."""
        assert normalize_version("1.0.0") == "1.0.0"

    def test_handles_lowercase_v(self):
        """Test that lowercase v is removed."""
        assert normalize_version("v2.1.3") == "2.1.3"

    def test_handles_multiple_v(self):
        """Test that all leading v's are removed (lstrip behavior)."""
        # lstrip removes all leading 'v' characters
        assert normalize_version("vv1.0.0") == "1.0.0"


class TestParseVersion:
    """Test suite for parse_version function."""

    def test_parses_simple_version(self):
        """Test parsing simple version string."""
        version = parse_version("1.0.0")
        assert str(version) == "1.0.0"

    def test_parses_version_with_v_prefix(self):
        """Test parsing version with v prefix."""
        version = parse_version("v1.2.3")
        assert str(version) == "1.2.3"

    def test_raises_on_invalid_version(self):
        """Test that invalid version raises exception."""
        with pytest.raises(InvalidVersion):
            parse_version("not-a-version")


class TestCompareVersions:
    """Test suite for compare_versions function."""

    @pytest.mark.parametrize(
        "v1,v2,expected",
        [
            ("0.1.0", "0.1.1", -1),
            ("1.0.0", "0.9.9", 1),
            ("1.0.0", "1.0.0", 0),
            ("v1.0.0", "1.0.0", 0),
            ("1.0.0", "v1.0.0", 0),
            ("v1.0.0", "v1.0.0", 0),
            ("2.0.0", "1.9.9", 1),
            ("1.10.0", "1.9.0", 1),
            ("0.1.2", "1.0.0", -1),
        ],
    )
    def test_compare_versions(self, v1, v2, expected):
        """Test version comparison returns correct result."""
        result = compare_versions(v1, v2)
        assert result == expected

    def test_compare_prerelease_versions(self):
        """Test comparison of prerelease versions."""
        # Prerelease versions are considered less than release versions
        assert compare_versions("1.0.0a1", "1.0.0") == -1
        assert compare_versions("1.0.0", "1.0.0a1") == 1


class TestIsNewerVersion:
    """Test suite for is_newer_version function."""

    def test_newer_version_returns_true(self):
        """Test that newer version is detected."""
        assert is_newer_version("0.1.2", "1.0.0") is True

    def test_same_version_returns_false(self):
        """Test that same version returns False."""
        assert is_newer_version("1.0.0", "1.0.0") is False

    def test_older_version_returns_false(self):
        """Test that older latest version returns False."""
        assert is_newer_version("2.0.0", "1.0.0") is False

    def test_handles_v_prefix(self):
        """Test that v prefix is handled correctly."""
        assert is_newer_version("v0.1.2", "v1.0.0") is True
        assert is_newer_version("0.1.2", "v1.0.0") is True
        assert is_newer_version("v0.1.2", "1.0.0") is True
