"""Tests for nchantdoffice.utilities.links (DESK T-NEW-055).

The affiliate-link sync path constructs a URL from the
``affiliate_api_base`` resolver plus a hardcoded resource
path. The pre-T-NEW-055 code doubled the path
(``/api/affiliate/links/affiliate/links/``) because the base
ALREADY included ``/links/`` AND the resource path also
included ``affiliate/links/``. Production masked the bug with
a wildcard route; dev mode (run-mode: dev) surfaced it with
a connection-refused because no docker stack would handle the
doubled path.

These tests pin the URL construction so the bug can't
regress. We mock ``requests.Session.get`` so the assertion
runs without any network.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import pytest


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


class _MockSession:
    """Captures the URL passed to ``Session.get`` and returns a canned body.

    Used to verify URL construction without hitting the network.
    The mock returns a 200 with an empty JSON body so the
    ``update_affiliate_links`` caller exits cleanly via its
    ``response.json()`` call.
    """

    def __init__(self, body: Any = []) -> None:
        self.body = body
        self.calls: list[Dict[str, Any]] = []
        # ``APIClient.__init__`` does
        # ``self.session.headers.update(...)`` — provide a
        # ``headers``-like attribute so the constructor doesn't
        # blow up before ``get`` is called.
        self.headers: Dict[str, str] = {}

    def get(self, url: str, params: Optional[Dict[str, Any]] = None,
            timeout: Any = None) -> "_MockResponse":
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return _MockResponse(self.body)


class _MockResponse:
    def __init__(self, body: Any) -> None:
        self._body = body

    def raise_for_status(self) -> None:
        pass

    def json(self) -> Any:
        return self._body


# -----------------------------------------------------------------------------
# Regression: URL construction must not double the path.
# -----------------------------------------------------------------------------


def test_update_affiliate_links_uses_correct_api_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``update_affiliate_links`` must hit ``{affiliate_api_base}/links/`` —

    NOT ``{affiliate_api_base}/links/affiliate/links/``. Regression
    for DESK T-NEW-055 — the pre-fix code doubled the path.

    We mock the requests Session so the assertion runs offline.
    The test is run-mode agnostic — it just verifies the URL
    construction contract, not which specific host is hit.
    """
    import requests  # noqa: F401  (the mock duck-types it)
    from nchantdoffice.utilities import links
    from nchantdoffice.utilities import urls

    # Pick prod (production URLs) for the assertion — the doubled
    # path bug was identical in dev and prod; production was just
    # masking it via a wildcard route.
    urls.set_run_mode("prod")
    urls.reload()

    mock = _MockSession(body=[])  # empty list -> the loop is a no-op

    def _fake_session_factory(*args, **kwargs):
        return mock

    monkeypatch.setattr(links.requests, "Session", _fake_session_factory)

    # Fake model — only ``remove_affiliate_links`` is called when
    # ``reload=True``; the rest of the body just iterates over the
    # empty response list and is a no-op.
    class _FakeModel:
        def remove_affiliate_links(self) -> None:
            pass

    result = links.update_affiliate_links(model=_FakeModel(), reload=False)
    assert result == {"affiliate_count": 0, "non_affiliate_count": 0}

    # The captured URL must be exactly ``{base}/links/`` —
    # NOT ``{base}/links/affiliate/links/``.
    assert len(mock.calls) == 1, (
        f"expected exactly 1 GET call, got {len(mock.calls)}: {mock.calls}"
    )
    captured_url = mock.calls[0]["url"]
    expected_base = urls.affiliate_api_base()
    assert captured_url == f"{expected_base}/links/", (
        f"doubled-path regression (DESK T-NEW-055): "
        f"got {captured_url!r}, expected {expected_base + '/links/'!r}. "
        f"The pre-fix code passed 'affiliate/links/' to client.get() "
        f"while API_URL already ended with '/links/', producing the "
        f"doubled path."
    )


def test_update_affiliate_links_dev_url_constructs_correctly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """In dev mode, the URL must be ``http://192.168.1.67:8080/api/affiliate/links/``.

    Same contract as the prod test, just with the dev profile
    active. Confirms the run-mode profile flows through to the
    affiliate URL correctly AND that the path isn't doubled.
    """
    from nchantdoffice.utilities import links
    from nchantdoffice.utilities import urls

    try:
        urls.set_run_mode("dev")
        urls.reload()

        mock = _MockSession(body=[])

        def _fake_session_factory(*args, **kwargs):
            return mock

        monkeypatch.setattr(links.requests, "Session", _fake_session_factory)

        class _FakeModel:
            def remove_affiliate_links(self) -> None:
                pass

        links.update_affiliate_links(model=_FakeModel(), reload=False)

        assert len(mock.calls) == 1
        captured_url = mock.calls[0]["url"]
        assert captured_url == (
            "http://192.168.1.67:8080/api/affiliate/links/"
        ), (
            f"dev-mode URL construction failed: got {captured_url!r}. "
            f"Expected the canonical ``/api/affiliate/links/`` path "
            f"without doubling."
        )
    finally:
        # Always reset run-mode so the next test in the suite
        # starts clean.
        urls.set_run_mode("prod")
        urls.reload()