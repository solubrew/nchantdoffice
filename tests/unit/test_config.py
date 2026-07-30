"""Tests for nchantdoffice.config module."""

import pytest

# Constants moved from nchantdoffice.config -> nchantdoffice.utilities.constants
# during commit cc77e57 (refactor of config, 2026-07-20). The 100+ constants
# and helpers now live in nchantdoffice/utilities/constants.py.
from nchantdoffice.utilities.constants import (
    APP_NAME,
    APP_VERSION,
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