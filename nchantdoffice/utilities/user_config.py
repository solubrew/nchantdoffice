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
  urls:               # DESK T-NEW-052 — per-host URL overrides
    server_base_url: str          # default: "https://api.nchantdoffice.com"
    affiliate_api_base: str       # default: "https://nchantdoffice.com/api/affiliate"
    feature_gates_url: str        # default: "https://nchantdoffice.com"
    updates_url: str              # default: "https://nchantdoffice.com"
    sync_url: str                 # default: "https://nchantdoffice.com"
    home_page: str                # default: "https://www.nchantdoffice.com/"
    upgrade_compare_url: str      # default: "https://www.nchantdoffice.com/compare"
    share_landing_url: str        # default: "https://nchantdoffice.com"
    registration_url: str         # default: "https://www.nchantdoffice.com/registration"
    whats_new_url: str            # default: "https://www.nchantdoffice.com/whats_new"
    affiliate_marketing_url: str  # default: "https://www.nchantdoffice.com/affiliate_marketing"

Example ~/.config/nchantdoffice/config.yaml (dev mode):

  dev_mode: true
  server:
    url: "http://localhost:5000"
    timeout: 3
  urls:
    server_base_url: "http://192.168.1.67"   # internal docker server
    affiliate_api_base: "http://192.168.1.67/api/affiliate"
    feature_gates_url: "http://192.168.1.67"
    updates_url: "http://192.168.1.67"
    sync_url: "http://192.168.1.67"
    home_page: "http://192.168.1.67"

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
import datetime as dt

import yaml

from kahndor.logma import Logma

logma = Logma(__name__)

# Canonical defaults. These are written to
# ``~/.config/nchantdoffice/config.yaml`` on first launch
# via :func:`write_default_config`; operators override any
# of them per-deploy.
#
# ``urls`` (DESK T-NEW-052) is seeded as an empty dict so
# the operator's config file already has a place for
# ``urls.server_base_url: http://192.168.1.67`` (or any
# other internal host) without needing to invent the key.
# The resolver falls through to the bundled
# ``_data_/urls.yaml`` defaults when the operator leaves the
# section empty.
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
    # DESK T-NEW-052: per-host URL overrides (production
    # defaults come from the bundled
    # ``nchantdoffice/utilities/_data_/urls.yaml`` — leave
    # empty for production, or set one or more keys here to
    # point the desktop at an internal docker). See
    # ``urls.py`` for the full list of recognised keys
    # and the XDG config example in this module's docstring.
    "urls": {},
    # T-NEW-042 (DESK-0): per-install user UUID. Empty by
    # default — NchantdOfficeUser.persist_uuid() generates
    # one on first launch and writes it here so it survives
    # across launches.
    "user": {
        "uuid": "",
        # T-NEW-044 (UI-2): timestamp (ISO 8601 UTC) until
        # which the user has ad-tab-free hours granted
        # (via the free-tier referral reward — see
        # AppReferralSpec §10). None / empty when no grant
        # is active. The Ad tab is hidden while this is
        # in the future. Stamped via set_ad_tab_free_hours().
        "ad_tab_free_until": "",
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


# -----------------------------------------------------------------------------
# T-NEW-044 (UI-2): ad-tab-free-hours helpers (free-tier referral reward)
# -----------------------------------------------------------------------------

def get_ad_tab_free_until(
    config: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """T-NEW-044 (UI-2): return the ISO timestamp until which
    the user has ad-tab-free hours, or None when no grant is
    active (or the grant has already expired).

    Used by ``NchantdOfficeAdTab._is_visible_for_user`` to
    hide the Ad tab for free-tier referrers who have been
    granted ad-tab-free hours as a referral reward
    (AppReferralSpec §10).
    """
    if config is None:
        config = load_config()
    raw = (config.get("user") or {}).get("ad_tab_free_until") or ""
    if not raw:
        return None
    return raw


def set_ad_tab_free_hours(hours: int, path: Optional[Path] = None) -> str:
    """T-NEW-044 (UI-2): grant N hours of ad-tab-free time
    (free-tier referral reward).

    Stamps ``user.ad_tab_free_until`` to ``now() + hours`` in
    ISO 8601 UTC. Returns the new expiry timestamp (ISO string).

    Called by the desktop when the server returns
    ``reason='free_tier'`` from ``get_payout_eligibility``
    (T-NEW-043 PAY-1 + AppReferralSpec §10) AND the user has
    earned enough referral credit to qualify. (The actual
    grant logic lives in the referral panel — this helper
    just persists the timer.)
    """
    if hours <= 0:
        raise ValueError(f"hours must be positive (got {hours})")
    expiry = dt.datetime.utcnow() + dt.timedelta(hours=hours)
    iso = expiry.isoformat() + "Z"
    target_p = path or USER_CONFIG_PATH
    config = load_config()
    config.setdefault("user", {})["ad_tab_free_until"] = iso
    target_p.parent.mkdir(parents=True, exist_ok=True)
    with target_p.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(config, fh, default_flow_style=False, sort_keys=True)
    logma.info(f"[user_config] persisted user.ad_tab_free_until={iso}")
    return iso


def clear_ad_tab_free_hours(path: Optional[Path] = None) -> None:
    """T-NEW-044 (UI-2): clear any active ad-tab-free grant.

    Useful when the user upgrades to Pro (their paid status
    already hides the Ad tab, so the timer is redundant)
    or when manually resetting for testing.
    """
    target_p = path or USER_CONFIG_PATH
    config = load_config()
    config.setdefault("user", {})["ad_tab_free_until"] = ""
    target_p.parent.mkdir(parents=True, exist_ok=True)
    with target_p.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(config, fh, default_flow_style=False, sort_keys=True)
    logma.info(f"[user_config] cleared user.ad_tab_free_until")


def is_ad_tab_free_active(
    config: Optional[Dict[str, Any]] = None,
    path: Optional[Path] = None,
) -> bool:
    """T-NEW-044 (UI-2): True when the user has active
    ad-tab-free hours (granted + not yet expired).

    Returns False when no grant is set, or when the grant
    has already expired (the timestamp is in the past).
    """
    until = get_ad_tab_free_until(config=config)
    if not until:
        return False
    try:
        # Strip the trailing Z for parsing.
        ts = dt.datetime.fromisoformat(until.rstrip("Z"))
    except ValueError:
        return False
    return ts > dt.datetime.utcnow()


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
