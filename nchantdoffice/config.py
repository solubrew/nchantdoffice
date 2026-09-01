# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name: NchantdOffice Configuration Module
    description: >
        Centralized configuration management for NchantdOffice.
        Provides constants, defaults, and configuration utilities.
    version: 0.0.1.0.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""

# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
from os.path import join, dirname
from os import environ
from typing import Any, Dict, Optional

# ======================================3rd Party Library Modules=====================================================||
from kahndor import kahndor

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor.logma import Logma

# ====================================================================================================================||
# Module-level logging setup
# ====================================================================================================================||
logger = Logma(__name__)


# ====================================================================================================================||
# Application Constants
# ====================================================================================================================||

# Application Identity
APP_NAME: str = "NchantdOffice"
APP_VERSION: str = "0.0.1.0.1.4"
APP_ID: str = "nchantdoffice"

# Application Type
APP_TYPE: str = "desktop"  # desktop, web, mobile, cli
APP_PLATFORM: str = "qt5"  # qt5, qt6, gtk, web

# Companion server URL — override via COMPANION_BASE_URL env var
# for LAN docker dev/testing. Defaults to the production public domain.
# e.g. export COMPANION_BASE_URL="http://192.168.1.67:5000"
COMPANION_BASE_URL: str = environ.get(
    "COMPANION_BASE_URL", "https://nchantdoffice.com"
)

# Window Configuration
WINDOW_MIN_WIDTH: int = 800
WINDOW_MIN_HEIGHT: int = 600
WINDOW_DEFAULT_WIDTH: int = 1200
WINDOW_DEFAULT_HEIGHT: int = 800
WINDOW_TITLE: str = f"{APP_NAME} - Office Platform"

# Theme Configuration
DEFAULT_THEME: str = "auto"  # light, dark, auto
THEME_LIGHT: str = "light"
THEME_DARK: str = "dark"
THEME_AUTO: str = "auto"
VALID_THEMES: tuple = (THEME_LIGHT, THEME_DARK, THEME_AUTO)

# Color Scheme
PRIMARY_COLOR: str = "#3498db"
SECONDARY_COLOR: str = "#2ecc71"
ACCENT_COLOR: str = "#e74c3c"
WARNING_COLOR: str = "#f39c12"
ERROR_COLOR: str = "#c0392b"
SUCCESS_COLOR: str = "#27ae60"

# Typography
FONT_FAMILY_DEFAULT: str = "Segoe UI, sans-serif"
FONT_SIZE_SMALL: int = 10
FONT_SIZE_NORMAL: int = 12
FONT_SIZE_LARGE: int = 14
FONT_SIZE_HEADING: int = 16
FONT_SIZE_TITLE: int = 18

# Spacing (in pixels)
SPACING_XS: int = 2
SPACING_SM: int = 4
SPACING_MD: int = 8
SPACING_LG: int = 16
SPACING_XL: int = 24
SPACING_XXL: int = 32

# Border Configuration
BORDER_WIDTH_THIN: int = 1
BORDER_WIDTH_NORMAL: int = 2
BORDER_WIDTH_THICK: int = 3
BORDER_RADIUS_SMALL: int = 4
BORDER_RADIUS_NORMAL: int = 8
BORDER_RADIUS_LARGE: int = 12

# Animation Timing (in milliseconds)
ANIMATION_DURATION_FAST: int = 100
ANIMATION_DURATION_NORMAL: int = 200
ANIMATION_DURATION_SLOW: int = 300
ANIMATION_DURATION_VERY_SLOW: int = 500

# Timeout Values (in seconds)
TIMEOUT_SHORT: int = 5
TIMEOUT_NORMAL: int = 30
TIMEOUT_LONG: int = 60
TIMEOUT_EXTENDED: int = 300

# Retry Configuration
RETRY_COUNT_DEFAULT: int = 3
RETRY_DELAY_MS: int = 1000
RETRY_BACKOFF_MULTIPLIER: float = 2.0

# File Size Limits (in bytes)
MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
MAX_EXPORT_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB

# Path Configuration
CONFIG_DIR_NAME: str = ".nchantdoffice"
DATA_DIR_NAME: str = "data"
CACHE_DIR_NAME: str = "cache"
LOG_DIR_NAME: str = "logs"
TEMP_DIR_NAME: str = "temp"

# Database Configuration
DB_FILE_NAME: str = "nchantdoffice.db"
DB_VERSION: int = 1
DB_BACKUP_ENABLED: bool = True
DB_BACKUP_COUNT: int = 5

# Signal Names
SIGNAL_DOCUMENT_CREATED: str = "document_created"
SIGNAL_DOCUMENT_OPENED: str = "document_opened"
SIGNAL_DOCUMENT_SAVED: str = "document_saved"
SIGNAL_DOCUMENT_CLOSED: str = "document_closed"
SIGNAL_TAB_CHANGED: str = "tab_changed"
SIGNAL_TREE_EXPANDED: str = "tree_expanded"
SIGNAL_TREE_COLLAPSED: str = "tree_collapsed"

# Menu Actions
ACTION_NEW: str = "new"
ACTION_OPEN: str = "open"
ACTION_SAVE: str = "save"
ACTION_SAVE_AS: str = "save_as"
ACTION_EXPORT: str = "export"
ACTION_IMPORT: str = "import"
ACTION_CLOSE: str = "close"
ACTION_QUIT: str = "quit"
ACTION_UNDO: str = "undo"
ACTION_REDO: str = "redo"
ACTION_CUT: str = "cut"
ACTION_COPY: str = "copy"
ACTION_PASTE: str = "paste"
ACTION_DELETE: str = "delete"
ACTION_SELECT_ALL: str = "select_all"
ACTION_FIND: str = "find"
ACTION_REPLACE: str = "replace"

# Toolbar Configuration
TOOLBAR_POSITION_TOP: str = "top"
TOOLBAR_POSITION_BOTTOM: str = "bottom"
TOOLBAR_POSITION_LEFT: str = "left"
TOOLBAR_POSITION_RIGHT: str = "right"

# Document Types
DOCTYPE_TEXT: str = "text"
DOCTYPE_SPREADSHEET: str = "spreadsheet"
DOCTYPE_PRESENTATION: str = "presentation"
DOCTYPE_PDF: str = "pdf"
DOCTYPE_IMAGE: str = "image"
DOCTYPE_HTML: str = "html"
DOCTYPE_MARKDOWN: str = "markdown"

# File Extensions
EXT_TEXT: tuple = (".txt", ".log")
EXT_SPREADSHEET: tuple = (".csv", ".xlsx", ".ods")
EXT_PRESENTATION: tuple = (".pptx", ".odp")
EXT_IMAGE: tuple = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")
EXT_DOCUMENT: tuple = (".docx", ".odt", ".rtf")
EXT_WEB: tuple = (".html", ".htm", ".xml")
EXT_CODE: tuple = (".py", ".js", ".ts", ".json", ".yaml", ".yml")

# Status Codes
STATUS_OK: int = 200
STATUS_CREATED: int = 201
STATUS_ACCEPTED: int = 202
STATUS_BAD_REQUEST: int = 400
STATUS_UNAUTHORIZED: int = 401
STATUS_FORBIDDEN: int = 403
STATUS_NOT_FOUND: int = 404
STATUS_CONFLICT: int = 409
STATUS_SERVER_ERROR: int = 500

# Error Messages
ERR_FILE_NOT_FOUND: str = "File not found: {path}"
ERR_PERMISSION_DENIED: str = "Permission denied: {path}"
ERR_INVALID_FORMAT: str = "Invalid format: {format}"
ERR_NETWORK_ERROR: str = "Network error: {message}"
ERR_DATABASE_ERROR: str = "Database error: {message}"
ERR_CONFIG_ERROR: str = "Configuration error: {message}"

# Validation Patterns
PATTERN_EMAIL: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PATTERN_URL: str = r"^https?://[^\s/$.?#].[^\s]*$"
PATTERN_PATH: str = r"^[a-zA-Z]:\\|^/"

# Feature Flags
FEATURE_AUTO_SAVE: bool = True
FEATURE_AUTO_BACKUP: bool = True
FEATURE_HISTORY: bool = True
FEATURE_TEMPLATES: bool = True
FEATURE_PLUGINS: bool = False
FEATURE_CLOUD_SYNC: bool = False

# Performance Thresholds
PERF_SLOW_THRESHOLD_MS: int = 1000
PERF_WARNING_THRESHOLD_MS: int = 500
PERF_MEMORY_WARNING_MB: int = 500

# Logging Configuration
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL_DEFAULT: str = "INFO"
LOG_LEVEL_DEBUG: str = "DEBUG"
LOG_LEVEL_WARNING: str = "WARNING"
LOG_LEVEL_ERROR: str = "ERROR"
LOG_MAX_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT: int = 5

# Cache Configuration
CACHE_ENABLED: bool = True
CACHE_TTL_SECONDS: int = 3600  # 1 hour
CACHE_MAX_ITEMS: int = 1000

# Security Configuration
SECURITY_SALT_LENGTH: int = 32
SECURITY_ITERATIONS: int = 100000
SECURITY_KEY_SIZE: int = 256

# Internationalization
LOCALE_DEFAULT: str = "en_US"
TIMEZONE_DEFAULT: str = "UTC"
DATE_FORMAT_DEFAULT: str = "%Y-%m-%d"
TIME_FORMAT_DEFAULT: str = "%H:%M:%S"
DATETIME_FORMAT_DEFAULT: str = "%Y-%m-%d %H:%M:%S"

# UI Layout
SIDEBAR_WIDTH_DEFAULT: int = 250
SIDEBAR_WIDTH_MIN: int = 150
SIDEBAR_WIDTH_MAX: int = 400
PANEL_HEIGHT_DEFAULT: int = 200
PANEL_HEIGHT_MIN: int = 100
PANEL_HEIGHT_MAX: int = 500

# Editor Configuration
EDITOR_TAB_SIZE: int = 4
EDITOR_INDENT_SIZE: int = 4
EDITOR_LINE_WRAP: bool = True
EDITOR_SHOW_LINE_NUMBERS: bool = True
EDITOR_SHOW_WHITESPACE: bool = False
EDITOR_AUTO_INDENT: bool = True

# Tree View Configuration
TREE_ICON_SIZE: int = 16
TREE_INDENT: int = 20
TREE_SHOW_HIDDEN: bool = False

# Tab Configuration
TAB_CLOSE_BUTTON_VISIBLE: bool = True
TAB_MIDDLE_CLICK_CLOSE: bool = True
TAB_MAX_COUNT: int = 20


# ====================================================================================================================||
# Configuration Defaults
# ====================================================================================================================||

CONFIG_DEFAULTS: Dict[str, Any] = {
    "app": {
        "name": APP_NAME,
        "version": APP_VERSION,
        "type": APP_TYPE,
    },
    "theme": {
        "default": DEFAULT_THEME,
        "available": list(VALID_THEMES),
        "primary_color": PRIMARY_COLOR,
        "secondary_color": SECONDARY_COLOR,
        "accent_color": ACCENT_COLOR,
    },
    "window": {
        "min_width": WINDOW_MIN_WIDTH,
        "min_height": WINDOW_MIN_HEIGHT,
        "default_width": WINDOW_DEFAULT_WIDTH,
        "default_height": WINDOW_DEFAULT_HEIGHT,
        "title": WINDOW_TITLE,
    },
    "editor": {
        "tab_size": EDITOR_TAB_SIZE,
        "indent_size": EDITOR_INDENT_SIZE,
        "line_wrap": EDITOR_LINE_WRAP,
        "show_line_numbers": EDITOR_SHOW_LINE_NUMBERS,
        "auto_indent": EDITOR_AUTO_INDENT,
    },
    "tree": {
        "icon_size": TREE_ICON_SIZE,
        "indent": TREE_INDENT,
        "show_hidden": TREE_SHOW_HIDDEN,
    },
    "tabs": {
        "close_button_visible": TAB_CLOSE_BUTTON_VISIBLE,
        "middle_click_close": TAB_MIDDLE_CLICK_CLOSE,
        "max_count": TAB_MAX_COUNT,
    },
    "logging": {
        "level": LOG_LEVEL_DEFAULT,
        "format": LOG_FORMAT,
        "date_format": LOG_DATE_FORMAT,
        "max_size": LOG_MAX_SIZE_BYTES,
        "backup_count": LOG_BACKUP_COUNT,
    },
    "cache": {
        "enabled": CACHE_ENABLED,
        "ttl_seconds": CACHE_TTL_SECONDS,
        "max_items": CACHE_MAX_ITEMS,
    },
    "features": {
        "auto_save": FEATURE_AUTO_SAVE,
        "auto_backup": FEATURE_AUTO_BACKUP,
        "history": FEATURE_HISTORY,
        "templates": FEATURE_TEMPLATES,
        "plugins": FEATURE_PLUGINS,
        "cloud_sync": FEATURE_CLOUD_SYNC,
    },
    "security": {
        "salt_length": SECURITY_SALT_LENGTH,
        "iterations": SECURITY_ITERATIONS,
        "key_size": SECURITY_KEY_SIZE,
    },
    "i18n": {
        "locale": LOCALE_DEFAULT,
        "timezone": TIMEZONE_DEFAULT,
        "date_format": DATE_FORMAT_DEFAULT,
        "time_format": TIME_FORMAT_DEFAULT,
    },
}

# ====================================================================================================================||
# Internal Configuration Storage
# ====================================================================================================================||
_internal_config: Dict[str, Any] = {}
_internal_initialized: bool = False


# ====================================================================================================================||
# Configuration Functions
# ====================================================================================================================||


def init_config(config_path: Optional[str] = None) -> None:
    """Initialize the configuration system.

    Args:
        config_path: Optional path to configuration file.
    """
    global _internal_config, _internal_initialized

    logger.info("Initializing NchantdOffice configuration")
    _internal_config = CONFIG_DEFAULTS.copy()
    _internal_initialized = True

    if config_path:
        logger.debug(f"Loading config from: {config_path}")


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value by key.

    Args:
        key: Configuration key (supports dot notation for nested keys).
        default: Default value if key not found.

    Returns:
        Configuration value or default.
    """
    if not _internal_initialized:
        init_config()

    keys = key.split(".")
    value = _internal_config

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default

    return value


def set_config_value(key: str, value: Any) -> None:
    """Set a configuration value by key.

    Args:
        key: Configuration key (supports dot notation for nested keys).
        value: Value to set.
    """
    if not _internal_initialized:
        init_config()

    keys = key.split(".")
    config = _internal_config

    for k in keys[:-1]:
        if k not in config:
            config[k] = {}
        config = config[k]

    config[keys[-1]] = value
    logger.debug(f"Config set: {key} = {value}")


def get_window_geometry() -> Dict[str, int]:
    """Get default window geometry.

    Returns:
        Dictionary with width, height, x, y.
    """
    return {
        "width": WINDOW_DEFAULT_WIDTH,
        "height": WINDOW_DEFAULT_HEIGHT,
        "x": 100,
        "y": 100,
    }


def reset_config() -> None:
    """Reset configuration to defaults."""
    global _internal_config, _internal_initialized
    _internal_config = CONFIG_DEFAULTS.copy()
    logger.info("Configuration reset to defaults")


# ====================================================================================================================||
# Export Configuration
# ====================================================================================================================||

__all__ = [
    # Application Constants
    "APP_NAME",
    "APP_VERSION",
    "APP_ID",
    "APP_TYPE",
    "APP_PLATFORM",
    "COMPANION_BASE_URL",
    # Window Configuration
    "WINDOW_MIN_WIDTH",
    "WINDOW_MIN_HEIGHT",
    "WINDOW_DEFAULT_WIDTH",
    "WINDOW_DEFAULT_HEIGHT",
    "WINDOW_TITLE",
    # Theme Configuration
    "DEFAULT_THEME",
    "VALID_THEMES",
    # Colors
    "PRIMARY_COLOR",
    "SECONDARY_COLOR",
    "ACCENT_COLOR",
    "WARNING_COLOR",
    "ERROR_COLOR",
    "SUCCESS_COLOR",
    # Typography
    "FONT_FAMILY_DEFAULT",
    "FONT_SIZE_SMALL",
    "FONT_SIZE_NORMAL",
    "FONT_SIZE_LARGE",
    "FONT_SIZE_HEADING",
    "FONT_SIZE_TITLE",
    # Spacing
    "SPACING_XS",
    "SPACING_SM",
    "SPACING_MD",
    "SPACING_LG",
    "SPACING_XL",
    "SPACING_XXL",
    # Border
    "BORDER_WIDTH_THIN",
    "BORDER_WIDTH_NORMAL",
    "BORDER_WIDTH_THICK",
    "BORDER_RADIUS_SMALL",
    "BORDER_RADIUS_NORMAL",
    "BORDER_RADIUS_LARGE",
    # Animation
    "ANIMATION_DURATION_FAST",
    "ANIMATION_DURATION_NORMAL",
    "ANIMATION_DURATION_SLOW",
    "ANIMATION_DURATION_VERY_SLOW",
    # Timeouts
    "TIMEOUT_SHORT",
    "TIMEOUT_NORMAL",
    "TIMEOUT_LONG",
    "TIMEOUT_EXTENDED",
    # Retry
    "RETRY_COUNT_DEFAULT",
    "RETRY_DELAY_MS",
    "RETRY_BACKOFF_MULTIPLIER",
    # File Size
    "MAX_FILE_SIZE_BYTES",
    "MAX_IMAGE_SIZE_BYTES",
    "MAX_EXPORT_SIZE_BYTES",
    # Path
    "CONFIG_DIR_NAME",
    "DATA_DIR_NAME",
    "CACHE_DIR_NAME",
    "LOG_DIR_NAME",
    "TEMP_DIR_NAME",
    # Database
    "DB_FILE_NAME",
    "DB_VERSION",
    "DB_BACKUP_ENABLED",
    "DB_BACKUP_COUNT",
    # Signals
    "SIGNAL_DOCUMENT_CREATED",
    "SIGNAL_DOCUMENT_OPENED",
    "SIGNAL_DOCUMENT_SAVED",
    "SIGNAL_DOCUMENT_CLOSED",
    "SIGNAL_TAB_CHANGED",
    "SIGNAL_TREE_EXPANDED",
    "SIGNAL_TREE_COLLAPSED",
    # Actions
    "ACTION_NEW",
    "ACTION_OPEN",
    "ACTION_SAVE",
    "ACTION_SAVE_AS",
    "ACTION_EXPORT",
    "ACTION_IMPORT",
    "ACTION_CLOSE",
    "ACTION_QUIT",
    "ACTION_UNDO",
    "ACTION_REDO",
    "ACTION_CUT",
    "ACTION_COPY",
    "ACTION_PASTE",
    "ACTION_DELETE",
    "ACTION_SELECT_ALL",
    "ACTION_FIND",
    "ACTION_REPLACE",
    # Toolbar
    "TOOLBAR_POSITION_TOP",
    "TOOLBAR_POSITION_BOTTOM",
    "TOOLBAR_POSITION_LEFT",
    "TOOLBAR_POSITION_RIGHT",
    # Document Types
    "DOCTYPE_TEXT",
    "DOCTYPE_SPREADSHEET",
    "DOCTYPE_PRESENTATION",
    "DOCTYPE_PDF",
    "DOCTYPE_IMAGE",
    "DOCTYPE_HTML",
    "DOCTYPE_MARKDOWN",
    # File Extensions
    "EXT_TEXT",
    "EXT_SPREADSHEET",
    "EXT_PRESENTATION",
    "EXT_IMAGE",
    "EXT_DOCUMENT",
    "EXT_WEB",
    "EXT_CODE",
    # Status Codes
    "STATUS_OK",
    "STATUS_CREATED",
    "STATUS_ACCEPTED",
    "STATUS_BAD_REQUEST",
    "STATUS_UNAUTHORIZED",
    "STATUS_FORBIDDEN",
    "STATUS_NOT_FOUND",
    "STATUS_CONFLICT",
    "STATUS_SERVER_ERROR",
    # Error Messages
    "ERR_FILE_NOT_FOUND",
    "ERR_PERMISSION_DENIED",
    "ERR_INVALID_FORMAT",
    "ERR_NETWORK_ERROR",
    "ERR_DATABASE_ERROR",
    "ERR_CONFIG_ERROR",
    # Validation Patterns
    "PATTERN_EMAIL",
    "PATTERN_URL",
    "PATTERN_PATH",
    # Feature Flags
    "FEATURE_AUTO_SAVE",
    "FEATURE_AUTO_BACKUP",
    "FEATURE_HISTORY",
    "FEATURE_TEMPLATES",
    "FEATURE_PLUGINS",
    "FEATURE_CLOUD_SYNC",
    # Performance
    "PERF_SLOW_THRESHOLD_MS",
    "PERF_WARNING_THRESHOLD_MS",
    "PERF_MEMORY_WARNING_MB",
    # Logging
    "LOG_FORMAT",
    "LOG_DATE_FORMAT",
    "LOG_LEVEL_DEFAULT",
    "LOG_LEVEL_DEBUG",
    "LOG_LEVEL_WARNING",
    "LOG_LEVEL_ERROR",
    "LOG_MAX_SIZE_BYTES",
    "LOG_BACKUP_COUNT",
    # Cache
    "CACHE_ENABLED",
    "CACHE_TTL_SECONDS",
    "CACHE_MAX_ITEMS",
    # Security
    "SECURITY_SALT_LENGTH",
    "SECURITY_ITERATIONS",
    "SECURITY_KEY_SIZE",
    # i18n
    "LOCALE_DEFAULT",
    "TIMEZONE_DEFAULT",
    "DATE_FORMAT_DEFAULT",
    "TIME_FORMAT_DEFAULT",
    "DATETIME_FORMAT_DEFAULT",
    # Layout
    "SIDEBAR_WIDTH_DEFAULT",
    "SIDEBAR_WIDTH_MIN",
    "SIDEBAR_WIDTH_MAX",
    "PANEL_HEIGHT_DEFAULT",
    "PANEL_HEIGHT_MIN",
    "PANEL_HEIGHT_MAX",
    # Editor
    "EDITOR_TAB_SIZE",
    "EDITOR_INDENT_SIZE",
    "EDITOR_LINE_WRAP",
    "EDITOR_SHOW_LINE_NUMBERS",
    "EDITOR_SHOW_WHITESPACE",
    "EDITOR_AUTO_INDENT",
    # Tree
    "TREE_ICON_SIZE",
    "TREE_INDENT",
    "TREE_SHOW_HIDDEN",
    # Tabs
    "TAB_CLOSE_BUTTON_VISIBLE",
    "TAB_MIDDLE_CLICK_CLOSE",
    "TAB_MAX_COUNT",
    # Configuration
    "CONFIG_DEFAULTS",
    "init_config",
    "get_config_value",
    "set_config_value",
    "get_window_geometry",
    "reset_config",
]


# ====================================================================================================================||
# Initialize on import
# ====================================================================================================================||
init_config()
logger.info(f"NchantdOffice configuration initialized - Version {APP_VERSION}")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
