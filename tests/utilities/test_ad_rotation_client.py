"""Tests for the server-driven ad rotation client (DESK T-NEW-061).

The desktop's right-side Ad tab calls
``fetch_rotation_ad(server_base_url)`` every 5 minutes and
renders whichever single ad the server returns. These tests
pin the URL construction, the response handling, and the
fail-soft contract.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import pytest


def _mock_response(
    body: Any = None,
    status_code: int = 200,
) -> MagicMock:
    """Build a requests.Response mock with the given body / status."""
    resp = MagicMock()
    resp.status_code = status_code
    if body is not None:
        resp.json.return_value = body
    resp.text = "" if body is None else str(body)
    return resp


def _capture(url_holder: Dict[str, Any], body: Any = None, status_code: int = 200, raise_exc: Optional[Exception] = None):
    """Build a fake ``requests.get`` that records the URL hit."""
    def _fake_get(url, timeout=None):
        url_holder["url"] = url
        url_holder["timeout"] = timeout
        if raise_exc is not None:
            raise raise_exc
        return _mock_response(body=body, status_code=status_code)
    return _fake_get


def _patch_get(monkeypatch, **kwargs):
    """Patch ``requests.get`` inside the ad_rotation_client module."""
    from nchantdoffice.widgets import ad_rotation_client

    # Make sure the local ``import requests`` inside
    # fetch_rotation_ad resolves to a module we control.
    # The client does ``import requests`` inside the function,
    # so we patch ``sys.modules['requests']`` with a stub
    # that has ``get = ...``.
    import requests
    fake = MagicMock()
    fake.get = _capture(kwargs.pop("url_holder", {}), **kwargs)
    monkeypatch.setitem(
        __import__("sys").modules, "requests", fake
    )


def test_fetch_returns_ad_dict_on_200_with_ad_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The happy path: server returns 200 + ``{"ad": {...}}``.
    The client returns the inner ad dict so the AdTab
    renderer doesn't have to unwrap the envelope.
    """
    from nchantdoffice.widgets.ad_rotation_client import (
        fetch_rotation_ad,
    )

    ad = {"id": 1, "title": "Try Notion", "cta_url": "https://x"}
    captured: Dict[str, Any] = {}
    _patch_get(monkeypatch, url_holder=captured, body={"ad": ad})

    result = fetch_rotation_ad("http://192.168.1.67:8081")
    assert result == ad
    # The URL must include the interval query param so the
    # server's bucket calculation matches the desktop's
    # surface cadence.
    assert "interval_seconds=300" in captured["url"]
    assert captured["url"].startswith(
        "http://192.168.1.67:8081/api/ads/rotation/next"
    )


def test_fetch_returns_none_on_204(monkeypatch: pytest.MonkeyPatch) -> None:
    """204 No Content means the server has no active ads
    right now. The client returns ``None`` so the AdTab
    renders its empty state ("No ads right now").
    """
    from nchantdoffice.widgets.ad_rotation_client import (
        fetch_rotation_ad,
    )

    _patch_get(monkeypatch, status_code=204)
    assert fetch_rotation_ad("http://x") is None


def test_fetch_returns_none_on_connection_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Network failures (DNS, connection refused, timeout) must
    return ``None`` and not raise. The AdTab shows an empty
    state and re-tries on the next 5-minute tick.
    """
    from nchantdoffice.widgets.ad_rotation_client import (
        fetch_rotation_ad,
    )

    _patch_get(
        monkeypatch,
        raise_exc=ConnectionRefusedError("LAN docker down"),
    )
    result = fetch_rotation_ad("http://192.168.1.67:8081")
    assert result is None


def test_fetch_returns_none_on_500(monkeypatch: pytest.MonkeyPatch) -> None:
    """5xx server errors must not crash the AdTab — the desktop
    shows an empty state and re-tries next tick."""
    from nchantdoffice.widgets.ad_rotation_client import (
        fetch_rotation_ad,
    )

    _patch_get(
        monkeypatch,
        body="Internal Server Error",
        status_code=500,
    )
    assert fetch_rotation_ad("http://192.168.1.67:8081") is None


def test_fetch_returns_none_on_malformed_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """200 with a body that doesn't have an ``ad`` key must
    return ``None`` (defensive — server bug protection).
    """
    from nchantdoffice.widgets.ad_rotation_client import (
        fetch_rotation_ad,
    )

    _patch_get(monkeypatch, body={"wrong": "shape"})
    assert fetch_rotation_ad("http://x") is None


def test_fetch_returns_none_on_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """200 with non-JSON body must return ``None`` (the
    operator may have a reverse proxy misconfig returning
    HTML)."""
    from nchantdoffice.widgets.ad_rotation_client import (
        fetch_rotation_ad,
    )

    resp = MagicMock()
    resp.status_code = 200
    resp.json.side_effect = ValueError("not json")
    resp.text = "<html>some html</html>"

    import sys as _sys
    fake = MagicMock()
    fake.get = lambda url, timeout=None: resp
    monkeypatch.setitem(_sys.modules, "requests", fake)

    assert fetch_rotation_ad("http://x") is None


def test_surface_interval_is_5_minutes() -> None:
    """The AdTab surfaces at 5 minutes — operator-mandated.

    Regression guard for DESK T-NEW-061. The previous
    implementation rotated every 12 seconds (DEFAULT_INTERVAL_MS=12000)
    which caused UI lockups when the rotation callback raced
    with the in-flight HTTP fetches.
    """
    from nchantdoffice.widgets.ad_rotation_client import (
        SURFACE_INTERVAL_MS,
    )
    assert SURFACE_INTERVAL_MS == 5 * 60 * 1000, (
        f"SURFACE_INTERVAL_MS should be 5 minutes (300_000 ms); "
        f"got {SURFACE_INTERVAL_MS}. Returning to the 12-second "
        f"rotation caused the lockup the operator reported."
    )


def test_fetch_honors_custom_interval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The ``rotation_interval_seconds`` kwarg lets the AdTab
    pass its actual surface cadence so the server's bucket
    calculation matches."""
    from nchantdoffice.widgets.ad_rotation_client import (
        fetch_rotation_ad,
    )

    captured: Dict[str, Any] = {}
    _patch_get(monkeypatch, url_holder=captured, status_code=204)
    fetch_rotation_ad("http://x", rotation_interval_seconds=600)
    assert "interval_seconds=600" in captured["url"]