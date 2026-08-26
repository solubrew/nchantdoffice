"""Tests for nchantdoffice.utilities.base_layer (DESK T-NEW-060).

The base-layer ad feed (``GET /api/ads/base-layer``) is the
primary source for the right-side Ad tab's rotation. The
client MUST source its server URL from the unified
``urls.server_base_url()`` resolver so the operator can
switch between internal docker (dev mode) and production
without code changes — the previous implementation used
``user_config.get_server_url()`` which falls back to
``http://localhost:5000`` in dev mode (wrong — the LAN
docker is on ``192.168.1.67:8081``).

These tests pin the URL the client constructs in both
run-mode profiles.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest


def _mock_session_factory(captured: Dict[str, Any]) -> Any:
    """Build a requests.get replacement that captures the URL hit
    and returns a canned JSON body."""
    def _get(url, **kwargs):
        captured["url"] = url
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"ads": []}
        return resp
    return _get


@pytest.fixture(autouse=True)
def _clear_base_layer_cache():
    """Wipe the base-layer cache so each test forces a network fetch."""
    from nchantdoffice.utilities import base_layer
    try:
        base_layer._write_cache(
            {"ads": [], "_cached_at": "1970-01-01T00:00:00"}
        )
    except Exception:
        pass
    yield
    try:
        base_layer._write_cache(
            {"ads": [], "_cached_at": "1970-01-01T00:00:00"}
        )
    except Exception:
        pass


def test_base_layer_uses_resolver_server_url_in_prod(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """In prod mode, ``get_base_layer_ads`` constructs the URL
    from ``urls.server_base_url()`` (production base), not the
    legacy ``get_server_url`` config (which would silently
    fall through to localhost in dev and produce an unreachable
    URL on the operator's LAN docker).
    """
    from nchantdoffice.utilities import base_layer
    from nchantdoffice.utilities import urls

    urls.set_run_mode("prod")
    urls.reload()

    captured: Dict[str, Any] = {}
    from nchantdoffice.utilities import base_layer
    monkeypatch.setattr(
        base_layer.requests, "get",
        _mock_session_factory(captured),
    )

    # Force a fresh fetch (don't serve from cache).
    base_layer._write_cache({"ads": [], "_cached_at": "1970-01-01T00:00:00"})
    base_layer.get_base_layer_ads(force_refresh=True)

    expected_base = urls.server_base_url()
    assert captured.get("url") == f"{expected_base}/api/ads/base-layer", (
        f"base_layer.get_base_layer_ads hit {captured.get('url')!r}; "
        f"expected the resolver URL {expected_base!r} + "
        f"'/api/ads/base-layer'. The legacy get_server_url() was "
        f"being used and falling back to localhost:5000 in dev mode "
        f"— switching to urls.server_base_url() makes dev mode "
        f"route to the operator's LAN docker at "
        f"http://192.168.1.67:8081."
    )


def test_base_layer_uses_resolver_server_url_in_dev(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """In dev mode, the URL MUST be ``http://192.168.1.67:8081/api/ads/base-layer``
    (the LAN docker), NOT ``http://localhost:5000/api/ads/base-layer``.

    Regression for DESK T-NEW-060 — the previous implementation
    used ``user_config.get_server_url()`` which returned
    ``http://localhost:5000`` when ``dev_mode: true`` was set.
    That URL is unreachable on the operator's LAN since the
    docker stack is at 192.168.1.67, not localhost (which
    would only work if the desktop ran on the same host as
    the docker).
    """
    from nchantdoffice.utilities import base_layer
    from nchantdoffice.utilities import urls

    try:
        urls.set_run_mode("dev")
        urls.reload()

        captured: Dict[str, Any] = {}
        from nchantdoffice.utilities import base_layer
        monkeypatch.setattr(
            base_layer.requests, "get",
            _mock_session_factory(captured),
        )

        # Force a fresh fetch.
        base_layer._write_cache(
            {"ads": [], "_cached_at": "1970-01-01T00:00:00"}
        )
        base_layer.get_base_layer_ads(force_refresh=True)

        assert captured.get("url") == (
            "http://192.168.1.67:8081/api/ads/base-layer"
        ), (
            f"base_layer dev URL was {captured.get('url')!r}; "
            f"expected http://192.168.1.67:8081/api/ads/base-layer. "
            f"The legacy get_server_url() fallback "
            f"(http://localhost:5000) was being used instead of "
            f"the resolver."
        )
    finally:
        urls.set_run_mode("prod")
        urls.reload()
