"""Tiny HTTP client for the server-driven ad rotation endpoint
(DESK T-NEW-061).

The desktop's right-side Ad tab calls
``GET {server_base_url}/api/ads/rotation/next`` every 5 minutes
and renders whichever single ad the server returns. All
rotation logic — priority, schedule, even-round-robin —
lives in the server. The desktop has no per-ad state.

This module is intentionally minimal: a single function
``fetch_rotation_ad()`` that returns either an ad dict or
``None`` (when the server has no ads to show or the call
fails). The desktop renders ``None`` as an empty state.

Why a separate module:
  - Tests can import ``fetch_rotation_ad`` and mock it
    with a single ``monkeypatch`` call. Mocking
    ``requests.get`` directly is more brittle (URL
    construction, timeout handling, response shape).
  - Keeps the 5-minute surface cadence logic
    (``SURFACE_INTERVAL_MS``) co-located with the call.
  - The desktop's AdTab is ~250 lines and shouldn't grow;
    putting the network call here keeps the rotation
    renderer view-only.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Cadence at which the desktop surfaces the Ad tab and
# re-asks the server for the next ad. Mirrors
# ``DEFAULT_ROTATION_INTERVAL_SECONDS`` on the server side
# (``nchantdoffice_com/app/apis/ad_rotation.py``). When the
# operator changes the server default, change this too (or
# extend this client to read the value from the server's
# /api/ads/rotation/health response).
SURFACE_INTERVAL_MS = 5 * 60 * 1000  # 5 minutes

# Per-call timeout for the GET. The endpoint is local-network
# in dev (LAN docker) and global in prod; 3s covers the worst
# case (LAN blip, TLS handshake) without making the desktop
# feel unresponsive if the server is briefly down.
HTTP_TIMEOUT_SECONDS = 3


def fetch_rotation_ad(
    server_base_url: str,
    *,
    rotation_interval_seconds: int = 300,
    timeout_seconds: float = HTTP_TIMEOUT_SECONDS,
) -> Optional[Dict[str, Any]]:
    """Fetch the single ad that should be shown right now.

    Returns the ad dict (matching the existing FALLBACK_BANNERS
    shape) on a 200 response, or ``None`` on:
      - 204 No Content (no active ads to show)
      - any HTTP error
      - any network failure (DNS, timeout, connection refused)
      - a malformed response

    Args:
        server_base_url: The server's base URL. Defaults to
            ``urls.server_base_url()`` via the AdTab when this
            module is imported. Tests pass a value directly.
        rotation_interval_seconds: Tells the server the
            cadence the desktop uses. Mirrors
            ``SURFACE_INTERVAL_MS`` but in seconds. The
            server uses this for its deterministic bucket
            calculation; the desktop passes it through so
            the bucket advances synchronously with the
            desktop's surface timer.
        timeout_seconds: Per-call HTTP timeout.

    Returns:
        An ad dict or ``None``. Never raises — network
        failures are an expected state (server down,
        LAN docker restarting) and the AdTab handles None
        by rendering an empty state.
    """
    import requests  # local import so tests can patch

    url = (
        f"{server_base_url.rstrip('/')}/api/ads/rotation/next"
        f"?interval_seconds={int(rotation_interval_seconds)}"
    )
    try:
        resp = requests.get(url, timeout=timeout_seconds)
    except Exception as exc:
        # DNS, connection refused, timeout, TLS handshake,
        # etc. All fail-soft — the AdTab shows an empty
        # state and re-tries on the next 5-minute tick.
        logger.warning(
            f"[ad_tab] rotation fetch failed: {exc}"
        )
        return None

    if resp.status_code == 204:
        # Server has no active ads right now.
        return None
    if resp.status_code != 200:
        logger.warning(
            f"[ad_tab] rotation fetch non-200: "
            f"{resp.status_code} {resp.text[:200]!r}"
        )
        return None

    try:
        body = resp.json()
    except Exception as exc:
        logger.warning(f"[ad_tab] malformed response: {exc}")
        return None

    ad = body.get("ad") if isinstance(body, dict) else None
    if not isinstance(ad, dict):
        logger.warning(
            f"[ad_tab] response missing 'ad' dict: {body!r}"
        )
        return None
    return ad
