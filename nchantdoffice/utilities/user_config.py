"""T-NEW-070 (DESK-1): user_config.py — XDG user config resolver.

The desktop's runtime configuration comes from a YAML file
on disk, not from environment variables. Two locations are
checked (in order of precedence):

  1. <cwd>/nchantdoffice.yaml         — project-local override
  2. ~/.config/nchantdoffice/config.yaml  — XDG user config

Schema (T-NEW-070):

  dev_mode: bool       # default: false
  server:
    url: str          # default: "https://nchantdoffice.com"
    timeout: int      # default: 5 (seconds)
  cache:
    dir: str          # default: ~/.local/share/nchantdoffice
  webengine:
    software_render: bool  # default: false

Example ~/.config/nchantdoffice/config.yaml (dev mode):

  dev_mode: true
  server:
    url: "http://localhost:5000"
    timeout: 3

Per the user's directive (2026-08-11, hard-break):
"there should never be env variables used for anything."
This module does NOT read os.environ. The legacy
NCHANT_API_BASE / NCHANT_DATA_DIR / NCHANT_WEBENGINE_SOFTWARE
env vars are removed from all consumers in this PR.
"""
from os.path import expanduser
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from kahndor.logma import Logma

logma = Logma(__name__)

# Canonical defaults
DEFAULTS: Dict[str, Any] = {
    "dev_mode": False,
    "server": {
        "url": "https://nchantdoffice.com",
        "timeout": 5,
    },
    "cache": {
        "dir": str(Path.home() / ".local" / "share" / "nchantdoffice"),
    },
    "webengine": {
        "software_render": False,
    },
    # T-NEW-042 (DESK-0): per-install user UUID. Empty by
    # default — NchantdOfficeUser.persist_uuid() generates
    # one on first launch and writes it here so it survives
    # across launches.
    "user": {
        "uuid": "",
    },
}

# XDG Base Directory Specification: ~/.config/<app>/config.yaml
XDG_CONFIG_HOME = Path(expanduser("~")) / ".config"
NCHANTDOFFICE_CONFIG_DIR = XDG_CONFIG_HOME / "nchantdoffice"
USER_CONFIG_PATH = NCHANTDOFFICE_CONFIG_DIR / "config.yaml"

# Project-local override: <cwd>/nchantdoffice.yaml
CWD_OVERRIDE_FILENAME = "nchantdoffice.yaml"


def get_user_config_path() -> Path:
    """Return the XDG user config path (~/.config/nchantdoffice/config.yaml)."""
    return USER_CONFIG_PATH


def get_cwd_override_path() -> Path:
    """Return the cwd project-local override path (./nchantdoffice.yaml)."""
    return Path.cwd() / CWD_OVERRIDE_FILENAME


def _load_yaml(path: Path) -> Optional[Dict[str, Any]]:
    """Load YAML from path, returning None if missing or unparseable."""
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except (yaml.YAMLError, OSError) as e:
        logma.warning(f"[user_config] {path} unparseable: {e}")
        return None
    if not isinstance(data, dict):
        logma.warning(
            f"[user_config] {path} root must be a mapping, got {type(data).__name__}"
        )
        return None
    return data


def load_config() -> Dict[str, Any]:
    """Load config with cwd override > XDG > defaults."""
    merged: Dict[str, Any] = {k: v for k, v in DEFAULTS.items()}

    xdg_data = _load_yaml(USER_CONFIG_PATH)
    if xdg_data:
        merged.update(xdg_data)
        logma.info(f"[user_config] loaded XDG config from {USER_CONFIG_PATH}")

    cwd_data = _load_yaml(get_cwd_override_path())
    if cwd_data:
        merged.update(cwd_data)
        logma.info(
            f"[user_config] cwd override applied from {get_cwd_override_path()}"
        )

    return merged


def get_dev_mode(config: Optional[Dict[str, Any]] = None) -> bool:
    """Return True iff dev_mode is enabled in the config."""
    if config is None:
        config = load_config()
    return bool(config.get("dev_mode", False))


def get_server_url(config: Optional[Dict[str, Any]] = None) -> str:
    """Return the server base URL.

    Precedence:
      1. config.server.url (if set)
      2. http://localhost:5000 (if dev_mode is True and no
         explicit server.url)
      3. https://nchantdoffice.com (production default)
    """
    if config is None:
        config = load_config()
    server = config.get("server", {})
    explicit = server.get("url")
    if explicit:
        return str(explicit).rstrip("/")
    if get_dev_mode(config):
        return "http://localhost:5000"
    return "https://nchantdoffice.com"


def get_server_timeout(config: Optional[Dict[str, Any]] = None) -> int:
    """Return the server request timeout (seconds)."""
    if config is None:
        config = load_config()
    return int(config.get("server", {}).get("timeout", 5))


def get_cache_dir(config: Optional[Dict[str, Any]] = None) -> Path:
    """Return the local cache directory."""
    if config is None:
        config = load_config()
    return Path(config.get("cache", {}).get(
        "dir", str(Path.home() / ".local" / "share" / "nchantdoffice")
    ))


def get_webengine_software_render(
    config: Optional[Dict[str, Any]] = None,
) -> bool:
    """Return True if QtWebEngine should force software rendering.

    T-NEW-070: replaces the legacy NCHANT_WEBENGINE_SOFTWARE
    env var. The config file is the only source of this flag.
    """
    if config is None:
        config = load_config()
    return bool(config.get("webengine", {}).get("software_render", False))


def get_user_uuid(config: Optional[Dict[str, Any]] = None) -> str:
    """Return the per-install user UUID (T-NEW-042 DESK-0).

    Empty string on first launch — caller is responsible for
    generating + persisting via set_user_uuid(). After the
    first launch, returns the persisted UUID so subsequent
    launches reuse the same identifier.
    """
    if config is None:
        config = load_config()
    return str(config.get("user", {}).get("uuid", "") or "")


def set_user_uuid(uuid: str, path: Optional[Path] = None) -> None:
    """Persist the per-install user UUID to the user config file.

    Called once on first launch after NchantdOfficeUser
    generates self.uuid. Idempotent — overwrites if already
    set (callers should check get_user_uuid() first).
    """
    target = path or USER_CONFIG_PATH
    config = load_config()
    config.setdefault("user", {})["uuid"] = uuid
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(config, fh, default_flow_style=False, sort_keys=True)
    logma.info(f"[user_config] persisted user.uuid to {target}")


def write_default_config(path: Optional[Path] = None) -> Path:
    """Write the default config to `path` (or USER_CONFIG_PATH).

    Convenience for first-time setup. Safe to call multiple
    times — will only write if the file doesn't already
    exist.
    """
    target = path or USER_CONFIG_PATH
    if target.exists():
        logma.info(f"[user_config] {target} already exists, skipping")
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(DEFAULTS, fh, default_flow_style=False, sort_keys=True)
    logma.info(f"[user_config] wrote default config to {target}")
    return target
