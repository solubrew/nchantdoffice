"""Tests for advertisements._load_affiliate_rotation (DESK T-NEW-060).

The right-side Ad tab's affiliate rotation fetches its
catalog from ``/api/v1/quicklinks/?ad_rotation_categories=...``.
When the AdTab is constructed without an explicit
``api_base_url`` in models.yaml (the typical case), the
function previously fell through to a relative URL —
never reaching the LAN docker when ``run-mode: dev`` is
active. DESK T-NEW-060 made the function fall back to
``urls.server_base_url()`` so the dev profile picks the
LAN docker and the prod profile picks the public site.

These tests pin the URL construction in both run-mode profiles.
"""
from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _reset_run_mode():
    """Each test starts with run-mode=prod; tests that need
    dev flip it explicitly and reset on exit."""
    from nchantdoffice.utilities import urls
    urls.set_run_mode("prod")
    urls.reload()
    yield
    urls.set_run_mode("prod")
    urls.reload()


def _patch_urlopen(captured: Dict[str, Any], body: List[Dict[str, Any]]):
    """Replace ``urllib.request.urlopen`` with a mock that captures
    the URL hit and returns ``body`` as the response payload.
    """
    import urllib.request

    def _fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url if hasattr(req, "full_url") else str(req)
        resp = MagicMock()
        resp.read.return_value = (
            ("[" + ",".join(str(b) for b in body) + "]").encode()
            if body
            else b"[]"
        )
        resp.__enter__ = lambda self: self
        resp.__exit__ = lambda self, *a: None
        return resp

    return patch.object(
        urllib.request,
        "urlopen",
        _fake_urlopen,
    )


def test_load_affiliate_rotation_uses_resolver_in_prod() -> None:
    """In prod mode, the URL must be the resolver's
    ``server_base_url()`` + ``/api/v1/quicklinks/`` — i.e.,
    ``https://api.nchantdoffice.com/api/v1/quicklinks/...``.
    """
    from nchantdoffice.utilities import urls
    from nchantdoffice.widgets import advertisements

    urls.set_run_mode("prod")
    urls.reload()

    captured: Dict[str, Any] = {}
    with _patch_urlopen(captured, body=[]):
        advertisements._load_affiliate_rotation()

    expected_base = urls.server_base_url().rstrip("/")
    expected_url = f"{expected_base}/api/v1/quicklinks/"
    actual = captured.get("url", "")
    assert actual.startswith(expected_url), (
        f"_load_affiliate_rotation hit {actual!r}; expected it "
        f"to start with the resolver URL {expected_url!r}. "
        f"Without DESK T-NEW-060 the relative URL "
        f"'/api/v1/quicklinks/...' would be used, never "
        f"reaching the operator's LAN docker."
    )
    assert "ad_rotation_categories=" in actual, (
        f"quicklinks URL missing the ad_rotation_categories "
        f"query param: {actual!r}"
    )


def test_load_affiliate_rotation_uses_resolver_in_dev() -> None:
    """In dev mode, the URL must be
    ``http://192.168.1.67:8081/api/v1/quicklinks/...``
    (the operator's LAN docker).
    """
    from nchantdoffice.utilities import urls
    from nchantdoffice.widgets import advertisements

    urls.set_run_mode("dev")
    urls.reload()

    captured: Dict[str, Any] = {}
    with _patch_urlopen(captured, body=[]):
        advertisements._load_affiliate_rotation()

    actual = captured.get("url", "")
    assert actual.startswith(
        "http://192.168.1.67:8081/api/v1/quicklinks/"
    ), (
        f"_load_affiliate_rotation dev URL was {actual!r}; "
        f"expected http://192.168.1.67:8081/api/v1/quicklinks/. "
        f"The previous code used a relative URL when no "
        f"api_base_url was passed in models.yaml, never "
        f"reaching the LAN docker."
    )


def test_load_affiliate_rotation_honors_explicit_api_base_url() -> None:
    """When an explicit ``api_base_url`` is passed, the resolver
    is bypassed. This preserves the test override path used by
    the existing tests in tests/unit/widgets/.
    """
    from nchantdoffice.widgets import advertisements

    captured: Dict[str, Any] = {}
    with _patch_urlopen(captured, body=[]):
        advertisements._load_affiliate_rotation(
            api_base_url="http://test.example.com"
        )

    actual = captured.get("url", "")
    assert actual.startswith("http://test.example.com/api/v1/quicklinks/"), (
        f"_load_affiliate_rotation explicit api_base_url was "
        f"not honored: {actual!r}"
    )
