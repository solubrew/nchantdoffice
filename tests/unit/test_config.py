"""Tests for nchantdoffice.config module."""

import pytest

# Constants moved from nchantdoffice.config -> nchantdoffice.utilities.constants
# during commit cc77e57 (refactor of config, 2026-07-20). The 100+ constants
# and helpers now live in nchantdoffice/utilities/constants.py.
from nchantdoffice.utilities.constants import (
    APP_NAME,
    APP_VERSION,
    APP_VERSION_SHORT,
    APP_PLATFORM,
    DEFAULT_THEME,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    CONFIG_DEFAULTS,
    get_config_value,
    get_window_geometry,
)


class TestConfigConstants:
    """Test configuration constants."""

    def test_app_name(self):
        assert APP_NAME == "NchantdOffice"

    def test_app_version(self):
        assert APP_VERSION.startswith("0.0.1")

    def test_app_version_short_is_3_segment(self):
        """T-DESK-055: APP_VERSION_SHORT is the 3-segment version
        the server's _parse_version() understands. Must be
        ``X.Y.Z`` format, not the 5-segment APP_VERSION.
        """
        assert APP_VERSION_SHORT.count(".") == 2, (
            f"APP_VERSION_SHORT must have 3 segments (X.Y.Z), "
            f"got {APP_VERSION_SHORT!r}"
        )
        parts = APP_VERSION_SHORT.split(".")
        for p in parts:
            assert p.isdigit(), (
                f"Each segment must be numeric, got {p!r} in "
                f"{APP_VERSION_SHORT!r}"
            )

    def test_app_version_short_differs_from_full(self):
        """The short version must not equal the full version —
        otherwise we'd be sending the 5-segment version to the
        server and the comparison would silently fail."""
        assert APP_VERSION_SHORT != APP_VERSION

    def test_app_platform_is_qt6(self):
        """T-DESK-056: codebase uses PySide6 (Qt6). The constant
        previously said 'qt5' which was a latent bug."""
        assert APP_PLATFORM == "qt6", (
            f"APP_PLATFORM must be 'qt6' (the codebase uses "
            f"PySide6), got {APP_PLATFORM!r}"
        )

    def test_default_theme(self):
        assert DEFAULT_THEME in ["light", "dark", "auto"]

    def test_window_dimensions(self):
        assert WINDOW_MIN_WIDTH > 0
        assert WINDOW_MIN_HEIGHT > 0


class TestConfigDefaults:
    """Test configuration defaults structure."""

    def test_config_defaults_exists(self):
        assert isinstance(CONFIG_DEFAULTS, dict)

    def test_config_defaults_has_required_keys(self):
        required = ["theme", "window", "editor", "tree"]
        for key in required:
            assert key in CONFIG_DEFAULTS


class TestGetConfigValue:
    """Test get_config_value function."""

    def test_get_existing_key(self):
        value = get_config_value("theme")
        assert value is not None

    def test_get_default_for_missing_key(self):
        value = get_config_value("nonexistent_key", default="default_value")
        assert value == "default_value"


class TestWindowGeometry:
    """Test window geometry helpers."""

    def test_geometry_values_positive(self):
        geom = get_window_geometry()
        assert all(v > 0 for v in geom.values())