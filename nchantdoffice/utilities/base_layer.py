"""Desktop base-layer ad feed client (T-DESK-063).

Fetches the curated house-ad slate from
``GET /api/ads/base-layer`` (unauthenticated) on first
launch and every ``REFRESH_INTERVAL_SECONDS`` (6h). The
ad tab renders these as the default; per-user ad campaigns
override individual slots later.

Design:
  1. On startup, call ``get_base_layer_ads()`` which checks
     the local cache first.
  2. If the cache is fresh (< 6h old), return it.
  3. If the cache is stale or missing, fetch from the server.
  4. If the server is unreachable, fall back to the hardcoded
     FALLBACK_BANNERS in ``advertisements.py`` (the desktop
     always has ads to show, even offline).

The cache lives at ``~/.nchantd/base_layer_cache.json``
(mode 0600) so the desktop doesn't re-fetch on every
restart.
"""
# -*- coding: utf-8 -*-
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from nchantdoffice.utilities.constants import APP_VERSION_SHORT

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore

# How often to re-fetch from the server (6 hours).
REFRESH_INTERVAL_SECONDS = 6 * 60 * 60

# T-NEW-070 (DESK-2 + DESK-3 hard-break): both
# NCHANT_API_BASE and NCHANT_DATA_DIR env vars removed.
# The API base URL + cache dir now come from the unified URL
# resolver (DESK T-NEW-052 + DESK T-NEW-060). ``urls.server_base_url()``
# reads the ``server_base_url`` key from the resolver, which
# is itself sourced from:
#   1. The bundled ``urls.yaml`` defaults (production hosts)
#   2. The ``run-mode`` launch profile (dev → LAN docker)
#   3. The XDG ``urls:`` override block (per-deploy)
# When the operator runs ``cfg = {"run-mode": "dev"}`` at
# launch, this returns ``http://192.168.1.67:8081`` (the
# LAN docker on the operator's host). Without this change
# the legacy ``user_config.get_server_url()`` returned
# ``http://localhost:5000`` in dev mode — which only works
# if the desktop runs on the docker host. The resolver
# makes the desktop follow the operator's run-mode config
# regardless of which host it runs on.
from nchantdoffice.utilities.urls import server_base_url as _resolver_server_url  # noqa: E402
from nchantdoffice.utilities.user_config import (  # noqa: E402
    get_cache_dir,
    get_server_timeout,
)

# DESK T-NEW-060: ``_DEFAULT_API_BASE`` is now a callable (not a
# module-level constant) so the run-mode profile swap that
# happens between import time and ``get_base_layer_ads()`` is
# reflected on the very next fetch. The previous shape
# (constant computed at import time) meant that a desktop
# launched with ``cfg = {"run-mode": "dev"}`` would still hit
# the prod URL because the prod value was frozen at module
# import — before the launch entrypoint called
# ``urls.set_run_mode("dev")``.
def _default_api_base() -> str:
    """Return the current run-mode-resolved server base URL.

    Read on each call so the dev/prod profile flip that
    happens at launch (``urls.set_run_mode`` in
    ``cmds/runNchantdOffice.py``) takes effect immediately
    for the very next ``get_base_layer_ads()`` call.
    """
    return _resolver_server_url().rstrip("/")
_CACHE_DIR = get_cache_dir()
_CACHE_PATH = _CACHE_DIR / "base_layer_cache.json"

# Timeout for the HTTP call (short — desktop should not hang
# on a slow server). Pulled from the user config (default 5s)
# or the explicit 10s value below if config is unavailable.
_HTTP_TIMEOUT = get_server_timeout() or 10  # seconds


def _read_cache() -> Optional[Dict[str, Any]]:
    """Read the cache file. Returns None if missing or
    corrupt (the caller falls back to a fresh fetch).
    """
    try:
        raw = _CACHE_PATH.read_text(encoding="utf-8")
        return json.loads(raw)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _write_cache(data: Dict[str, Any]) -> None:
    """Write the cache file (mode 0600 so other users on
    the machine can't read the desktop's ad state).
    """
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_text(
            json.dumps(data), encoding="utf-8",
        )
        os.chmod(_CACHE_PATH, 0o600)
    except OSError:
        pass  # Best-effort; don't crash the ad tab.


def _cache_is_fresh(cache: Optional[Dict[str, Any]]) -> bool:
    """Check if the cache is within the refresh interval.
    """
    if cache is None:
        return False
    cached_at = cache.get("_cached_at")
    if cached_at is None:
        return False
    try:
        cached_dt = dt.datetime.fromisoformat(cached_at)
    except (ValueError, TypeError):
        return False
    age = (dt.datetime.utcnow() - cached_dt).total_seconds()
    return age < REFRESH_INTERVAL_SECONDS


def _extract_ads(cache: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract the ``ads`` list from a cache entry."""
    if cache is None:
        return []
    ads = cache.get("ads", [])
    if not isinstance(ads, list):
        return []
    return ads


def _fetch_from_server(
    api_base: str,
    *,
    timeout: int = _HTTP_TIMEOUT,
) -> Optional[Dict[str, Any]]:
    """Fetch the base layer from the server.

    Returns the parsed JSON dict or None on any failure
    (network error, non-200, malformed JSON).
    """
    if requests is None:
        return None
    url = f"{api_base.rstrip('/')}/api/ads/base-layer"
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": (
                    f"NchantdOffice/{APP_VERSION_SHORT} "
                    f"(desktop; base-layer)"
                ),
            },
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not isinstance(data, dict) or "ads" not in data:
            return None
        return data
    except Exception:
        return None


def get_base_layer_ads(
    api_base: Optional[str] = None,
    *,
    force_refresh: bool = False,
) -> List[Dict[str, Any]]:
    """Return the base-layer ad list.

    This is the main entry point. The desktop's ad tab
    calls this on startup. The function:
      1. Checks the cache (if not force_refresh).
      2. If fresh, returns the cached ads.
      3. If stale, fetches from the server.
      4. If the fetch fails, returns the stale cache (if
         any) or an empty list.

    Args:
        api_base: override the server URL (mainly for
            testing). Defaults to the NCHANT_API_BASE env
            var or https://nchantdoffice.com.
        force_refresh: bypass the cache and fetch from
            the server. Useful for a "refresh ads" button
            in the UI.

    Returns:
        A list of ad dicts matching the FALLBACK_BANNERS
        shape. May be empty if both cache and server are
        unavailable (the ad tab handles this by falling
        back to its own hardcoded list).
    """
    base = api_base or _default_api_base()

    # Step 1: Check cache.
    cache = _read_cache()
    if not force_refresh and _cache_is_fresh(cache):
        return _extract_ads(cache)

    # Step 2: Fetch from server.
    server_data = _fetch_from_server(base)
    if server_data is not None:
        # Write the fresh data to cache.
        server_data["_cached_at"] = (
            dt.datetime.utcnow().isoformat()
        )
        _write_cache(server_data)
        return _extract_ads(server_data)

    # Step 3: Server unreachable. Use stale cache if any.
    if cache is not None:
        return _extract_ads(cache)

    # Step 4: No cache, no server. Empty list (the ad tab
    # falls back to FALLBACK_BANNERS).
    return []


def clear_cache() -> None:
    """Remove the cache file. Useful for testing or for
    a "reset ads" action in the UI."""
    try:
        _CACHE_PATH.unlink()
    except FileNotFoundError:
        pass