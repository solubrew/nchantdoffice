# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-update-checker
    name: Application Update Checker
    description: >
        T-DESK-053 (cross-repo review §1.2): consumer for the
        server's ``GET /api/check-update`` endpoint. Polls the
        server on startup + every REFRESH_INTERVAL_SECONDS and
        surfaces "new version available" notifications to the
        tray + log.

        Best-effort: any network failure returns ``None`` and
        does NOT clobber a previously-cached good response.

        Dismissed versions are persisted to
        ``~/.nchantd/state.yaml`` so the notification doesn't
        fire twice for the same release.
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
import datetime as dt
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

# ======================================3rd Party Library Modules=====================================================||
import requests

# ======================================Solutions Brewer Library Modules=============================================||
from kahndor.logma import Logma
from nchantdoffice.utilities.constants import APP_VERSION_SHORT, APP_PLATFORM

logma = Logma(__name__)

# ---------------------------------------------------------------------------
# T-DESK-053 — module-level constants
# ---------------------------------------------------------------------------

# Server endpoint (matches nchantdoffice_com/app/apis/updates.py:209).
DEFAULT_CHECK_UPDATE_PATH: str = "/api/check-update"

# How often to re-poll the server (6 hours; mirrors base_layer.py).
# T-NEW-059: retained as a default constant for callers that don't
# pass a cfg dict. New code should call ``refresh_interval_seconds(cfg)``
# with the app config to honour the user's
# ``check_update_interval_hours`` override (see Interface Tab
# settings → "Update check interval (hours)").
REFRESH_INTERVAL_SECONDS: int = 6 * 60 * 60
DEFAULT_CHECK_UPDATE_INTERVAL_HOURS: int = 6
MIN_CHECK_UPDATE_INTERVAL_HOURS: int = 1
MAX_CHECK_UPDATE_INTERVAL_HOURS: int = 168  # 1 week

# Local cache file (~/.nchantd/update_check_cache.json, mode 0o600).
CACHE_FILENAME: str = "update_check_cache.json"

# Dismissed-versions store (~~/.nchantd/state.yaml).
STATE_FILENAME: str = "state.yaml"

# Per-call HTTP timeout (5 s; matches ReferralAPIClient).
HTTP_TIMEOUT: float = 5.0


def refresh_interval_seconds(cfg=None):
    """Return the configured update-check interval in seconds (T-NEW-059).

    Reads ``cfg.get("check_update_interval_hours", DEFAULT_CHECK_UPDATE_INTERVAL_HOURS)``
    and converts to seconds. Invalid values (< MIN or > MAX) fall back
    to the default. Accepts a plain dict OR a kahndor.Instruct-like
    object that supports ``.get(...)``.

    Parameters
    ----------
    cfg : dict or object with .get(), optional
        The app config (typically ``self.config.dikt`` on
        ``NchantdOfficeCloak``). If None, returns the default
        interval.

    Returns
    -------
    int
        The interval in seconds. Guaranteed to be >= MIN and <= MAX.
    """
    if cfg is None:
        hours = DEFAULT_CHECK_UPDATE_INTERVAL_HOURS
    else:
        try:
            raw = cfg.get("check_update_interval_hours", DEFAULT_CHECK_UPDATE_INTERVAL_HOURS)
            hours = int(raw)
        except (TypeError, ValueError):
            hours = DEFAULT_CHECK_UPDATE_INTERVAL_HOURS
    if hours < MIN_CHECK_UPDATE_INTERVAL_HOURS or hours > MAX_CHECK_UPDATE_INTERVAL_HOURS:
        return DEFAULT_CHECK_UPDATE_INTERVAL_HOURS * 3600
    return hours * 3600

# Where caches + state live. Override with NCHANT_DATA_DIR for tests.
_CACHE_DIR = Path(
    os.environ.get(
        "NCHANT_DATA_DIR",
        os.path.join(os.path.expanduser("~"), ".nchantd"),
    )
)
_CACHE_PATH = _CACHE_DIR / CACHE_FILENAME
_STATE_PATH = _CACHE_DIR / STATE_FILENAME


# ---------------------------------------------------------------------------
# T-DESK-053 — parsed-response dataclass
# ---------------------------------------------------------------------------


@dataclass
class UpdateInfo:
    """Parsed response from ``GET /api/check-update``.

    Fields mirror the server's response shape (see
    nchantdoffice_com/app/apis/updates.py:209). All fields
    except ``latest_version`` and ``update_available`` are
    optional (the server may omit ``changelog_url`` when
    there's no human-readable changelog).
    """

    latest_version: str
    release_date: str = ""
    update_available: Optional[bool] = None
    download_url: str = ""
    changelog_url: str = ""
    os: str = ""

    @classmethod
    def from_response(cls, payload: Dict[str, Any]) -> "UpdateInfo":
        """Build an ``UpdateInfo`` from the server's JSON.

        Defensive against missing keys (the server is the
        source of truth; the desktop tolerates partial
        responses rather than crashing on a key rename).
        """
        return cls(
            latest_version=str(payload.get("latest_version", "")),
            release_date=str(payload.get("release_date", "")),
            update_available=payload.get("update_available"),
            download_url=str(payload.get("download_url", "")),
            changelog_url=str(payload.get("changelog_url", "")),
            os=str(payload.get("os", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for the cache file."""
        return {
            "latest_version": self.latest_version,
            "release_date": self.release_date,
            "update_available": self.update_available,
            "download_url": self.download_url,
            "changelog_url": self.changelog_url,
            "os": self.os,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "UpdateInfo":
        """Inverse of ``to_dict`` (for cache reads)."""
        return cls.from_response(payload)


# ---------------------------------------------------------------------------
# T-DESK-053 — UpdateChecker
# ---------------------------------------------------------------------------


class UpdateChecker:
    """Caller-driven poller for ``GET /api/check-update``.

    The caller decides when to call ``check()`` (startup hook,
    settings panel button, scheduled 6h timer). The class
    itself does not start any background thread — keeps the
    surface small and testable.

    Cache behaviour (mirrors ``base_layer.py``):
      1. ``check()`` first checks the local cache.
      2. If fresh (< REFRESH_INTERVAL_SECONDS), return cached
         response without hitting the network.
      3. If stale or missing, hit ``/api/check-update`` and
         overwrite the cache on success.
      4. Network failure returns ``None`` and does NOT touch
         the cache (a transient 503 must not lose a good
         cache hit).

    Auth: none. The endpoint is unauthenticated per the
    server's design (the desktop calls it BEFORE login /
    registration).
    """

    def __init__(
        self,
        base_url: str = "https://nchantdoffice.com",
        check_path: str = DEFAULT_CHECK_UPDATE_PATH,
        timeout: float = HTTP_TIMEOUT,
        cfg=None,
    ):
        self.base_url = base_url.rstrip("/")
        self.check_path = check_path.lstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        # T-NEW-059: store the config reference so check() can
        # honour the user's ``check_update_interval_hours`` override.
        # None means "use the module-level default".
        self._cfg = cfg

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check(self) -> Optional[UpdateInfo]:
        """Return the latest update info, or ``None`` if the
        server is unreachable AND no fresh cache exists.

        Flow:
          1. Try cache (return ``UpdateInfo`` if fresh).
          2. Try server (return ``UpdateInfo`` + write cache
             on success).
          3. Fall back to stale cache (return ``UpdateInfo``
             rather than ``None`` — better to show a slightly
             old "update available" than nothing).
          4. Return ``None`` only when both cache and server
             are unavailable.
        """
        # 1. Fresh cache → short-circuit (no network call).
        cached = self._read_cache()
        if cached is not None:
            return cached

        # 2. Try server.
        try:
            response = self._session.get(
                f"{self.base_url}/{self.check_path}",
                params={
                    "current_version": APP_VERSION_SHORT,
                    "os": self._platform_for_query(),
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json() if response.content else {}
            info = UpdateInfo.from_response(payload)
            # 3. Write cache only on success.
            self._write_cache(info)
            return info
        except (requests.RequestException, ValueError) as e:
            logma.warning(
                f"[update_checker] GET {self.check_path} failed: {e}"
            )

        # 4. Server unreachable + no fresh cache → try the
        # stale cache (better than nothing).
        stale = self._read_cache(allow_stale=True)
        if stale is not None:
            return stale
        return None

    # ------------------------------------------------------------------
    # Cache helpers (mirrors base_layer.py)
    # ------------------------------------------------------------------

    def _read_cache(self, allow_stale: bool = False) -> Optional[UpdateInfo]:
        """Return the cached ``UpdateInfo`` if present and
        fresh. When ``allow_stale=True`` (the fallback path),
        return even if older than ``refresh_interval_seconds(self._cfg)``
        (T-NEW-059 — the user-configurable interval; was hard-coded
        ``REFRESH_INTERVAL_SECONDS`` before T-NEW-059).
        """
        try:
            if not _CACHE_PATH.exists():
                return None
            raw = _CACHE_PATH.read_text(encoding="utf-8")
            payload = json.loads(raw)
        except (OSError, ValueError) as e:
            logma.warning(f"[update_checker] cache read failed: {e}")
            return None

        # Freshness check — skipped when allow_stale=True. T-NEW-059
        # honours the user-configurable check_update_interval_hours.
        if not allow_stale:
            try:
                cache_time = dt.datetime.fromisoformat(
                    payload.get("_cached_at", "")
                )
                age = (
                    dt.datetime.now(dt.timezone.utc) - cache_time
                ).total_seconds()
                if age >= refresh_interval_seconds(self._cfg):
                    return None
            except (ValueError, TypeError):
                # No timestamp or malformed — treat as stale.
                return None

        try:
            return UpdateInfo.from_dict(payload)
        except Exception as e:
            logma.warning(f"[update_checker] cache parse failed: {e}")
            return None

    def _write_cache(self, info: UpdateInfo) -> None:
        """Persist the ``UpdateInfo`` to ``_CACHE_PATH`` with
        mode 0o600 (mirrors base_layer + credentials pattern).
        """
        try:
            _CACHE_DIR.mkdir(parents=True, exist_ok=True)
            payload = info.to_dict()
            payload["_cached_at"] = dt.datetime.now(
                dt.timezone.utc
            ).isoformat()
            _CACHE_PATH.write_text(
                json.dumps(payload, indent=2),
                encoding="utf-8",
            )
            os.chmod(_CACHE_PATH, 0o600)
        except OSError as e:
            logma.warning(f"[update_checker] cache write failed: {e}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _platform_for_query() -> str:
        """Map the desktop's APP_PLATFORM constant + sys.platform
        to one of ``linux`` / ``macos`` / ``windows`` (the
        three values the server's check_update endpoint accepts).
        """
        # APP_PLATFORM is "qt6" / "qt5" / "gtk" / "web" — those
        # are UI toolkits, not OSes. The OS comes from
        # sys.platform. The two are combined so the server
        # can pick the right download URL later (e.g.
        # ``qt6-linux`` vs ``gtk-linux``).
        sys_platform = sys.platform.lower() if sys else ""
        if sys_platform.startswith("linux"):
            return f"{APP_PLATFORM}-linux"
        if sys_platform.startswith("darwin"):
            return f"{APP_PLATFORM}-macos"
        if sys_platform.startswith("win"):
            return f"{APP_PLATFORM}-windows"
        return f"{APP_PLATFORM}-{sys_platform or 'unknown'}"


# ---------------------------------------------------------------------------
# T-DESK-053 — dismissed-versions helpers (module-level)
# ---------------------------------------------------------------------------


def _load_state() -> Dict[str, Any]:
    """Read ~/.nchantd/state.yaml. Returns an empty dict when
    missing or malformed (the dismissed-versions store is
    best-effort — losing it just means a notification may
    re-fire once, which is fine).
    """
    try:
        if not _STATE_PATH.exists():
            return {}
        # Tiny hand-rolled parser — keeps zero new deps.
        # state.yaml looks like:
        #   dismissed_versions:
        #     - 0.1.0
        #     - 0.2.0
        text = _STATE_PATH.read_text(encoding="utf-8")
        state: Dict[str, Any] = {"dismissed_versions": []}
        current_list_key: Optional[str] = None
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.endswith(":"):
                key = stripped[:-1].strip()
                if key == "dismissed_versions":
                    state[key] = []
                    current_list_key = key
                else:
                    current_list_key = None
            elif current_list_key and stripped.startswith("- "):
                state[current_list_key].append(stripped[2:].strip())
        return state
    except OSError as e:
        logma.warning(f"[update_checker] state read failed: {e}")
        return {"dismissed_versions": []}


def _save_state(state: Dict[str, Any]) -> None:
    """Persist the dismissed-versions state to
    ``~/.nchantd/state.yaml``. Mode 0o600 (mirrors the
    credentials / cache pattern).
    """
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        lines = ["dismissed_versions:"]
        for v in state.get("dismissed_versions", []):
            lines.append(f"  - {v}")
        _STATE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.chmod(_STATE_PATH, 0o600)
    except OSError as e:
        logma.warning(f"[update_checker] state write failed: {e}")


def dismiss_version(version: str) -> None:
    """Record that the user dismissed the notification for
    ``version``. Idempotent (no duplicates).

    T-DESK-053 step "Persist dismissed versions in
    ~/.nchantd/state.yaml".
    """
    if not version or not isinstance(version, str):
        return
    state = _load_state()
    dismissed = state.setdefault("dismissed_versions", [])
    if version not in dismissed:
        dismissed.append(version)
        _save_state(state)


def is_dismissed(version: str) -> bool:
    """Return True iff the user previously dismissed
    ``version``. Caller passes the ``UpdateInfo.latest_version``
    string; comparison is exact-match (the server uses
    semantic versioning so two releases can't share a version
    string).
    """
    if not version or not isinstance(version, str):
        return False
    state = _load_state()
    return version in state.get("dismissed_versions", [])


__all__ = [
    "UpdateChecker",
    "UpdateInfo",
    "dismiss_version",
    "is_dismissed",
    "DEFAULT_CHECK_UPDATE_PATH",
    "REFRESH_INTERVAL_SECONDS",
    "CACHE_FILENAME",
    "STATE_FILENAME",
]
