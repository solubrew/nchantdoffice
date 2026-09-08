"""Tests for nchantdoffice.utilities.links (DESK T-NEW-055 / T-NEW-057).

The affiliate-link sync path constructs a URL from the
``affiliate_api_base`` resolver plus a hardcoded resource
path. The pre-T-NEW-055 code doubled the path
(``/api/affiliate/links/affiliate/links/``) because the base
ALREADY included ``/links/`` AND the resource path also
included ``affiliate/links/``. Production masked the bug with
a wildcard route; dev mode (run-mode: dev) surfaced it with
a connection-refused because no docker stack would handle the
doubled path.

DESK T-NEW-057 added the auth contract: the server's
@require_desktop_api_key decorator reads ``x-api-key``, NOT
``Authorization: Bearer``. The original APIClient was using
the FAB-User ``Bearer`` convention, so live calls returned
401 even with a valid api_key.

These tests pin URL construction + auth header + the
fail-soft 401 behavior so the bugs can't regress.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from unittest.mock import patch

import pytest
import requests  # for the HTTPError exception class


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


class _MockSession:
    """Captures the URL + headers passed to ``Session.get`` and returns a canned body.

    Used to verify URL construction and auth header behavior
    without hitting the network. The mock returns a configurable
    status code so we can simulate 200 (success), 401 (auth
    failure), etc.
    """

    def __init__(
        self,
        body: Any = None,
        status_code: int = 200,
    ) -> None:
        self.body = body if body is not None else []
        self.status_code = status_code
        self.calls: list[Dict[str, Any]] = []
        # ``APIClient.__init__`` does
        # ``self.session.headers.update(...)`` — provide a
        # ``headers``-like attribute so the constructor doesn't
        # blow up before ``get`` is called.
        self.headers: Dict[str, str] = {}

    def get(self, url: str, params: Optional[Dict[str, Any]] = None,
            timeout: Any = None) -> "_MockResponse":
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return _MockResponse(self.body, status_code=self.status_code)


class _MockResponse:
    def __init__(self, body: Any, status_code: int = 200) -> None:
        self._body = body
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if 400 <= self.status_code < 600:
            # Mimic requests' HTTPError signature. The mock
            # doesn't need a real Response object — passing
            # ``self`` is enough for the .response attribute.
            raise requests.exceptions.HTTPError(
                f"{self.status_code} HTTP Error", response=self  # type: ignore[arg-type]
            )

    def json(self) -> Any:
        return self._body


# Fake InstallStore so the lazy import in update_affiliate_links
# finds a deterministic api_key. We patch the symbol at the
# location where it's looked up: inside
# ``nchantdoffice.license.install_store``.
class _FakeInstallStore:
    def __init__(self, api_key: Optional[str] = "nk_test_default") -> None:
        self._api_key = api_key

    def get_or_create(self) -> Dict[str, Any]:
        return {
            "install_id": "test-install-id",
            "hardware_key": "test-hardware-key",
            "api_key": self._api_key,
            "desktop_uuid": "test-uuid",
        }


@pytest.fixture
def fake_install_store():
    """Patch InstallStore to return a controllable api_key.

    The default api_key is ``nk_test_default``; tests that want
    to verify the no-api_key / 401 path can call
    ``fake_install_store["set"](None)``.
    """
    state: Dict[str, Any] = {"api_key": "nk_test_default"}

    def _factory(*args, **kwargs):
        return _FakeInstallStore(api_key=state["api_key"])

    with patch(
        "nchantdoffice.license.install_store.InstallStore",
        _factory,
    ):
        def _set(v: Optional[str]) -> None:
            state["api_key"] = v
        state["set"] = _set
        yield state


# -----------------------------------------------------------------------------
# Regression: URL construction must not double the path.
# -----------------------------------------------------------------------------


def test_update_affiliate_links_uses_correct_api_url(
    monkeypatch: pytest.MonkeyPatch,
    fake_install_store,
) -> None:
    """``update_affiliate_links`` must hit ``{server_base_url}/api/v1/quicklinks/``.

    Fixed in COMPAT-002 (2026-08-29): the old
    ``{affiliate_api_base}/links/`` path (maps to
    ``/api/affiliate/links/``) was wrong — the live server
    serves quicklinks at ``/api/v1/quicklinks/`` via
    ``server_base_url``.

    We mock the requests Session so the assertion runs offline.
    The test is run-mode agnostic — it just verifies the URL
    construction contract, not which specific host is hit.
    """
    from nchantdoffice.utilities import links
    from nchantdoffice.utilities import urls

    # Pick prod (production URLs) for the assertion.
    urls.set_run_mode("prod")
    urls.reload()

    mock = _MockSession(body=[])  # empty list -> the loop is a no-op

    def _fake_session_factory(*args, **kwargs):
        return mock

    monkeypatch.setattr(links.requests, "Session", _fake_session_factory)

    class _FakeModel:
        def remove_affiliate_links(self) -> None:
            pass

    result = links.update_affiliate_links(model=_FakeModel(), reload=False)
    assert result == {"affiliate_count": 0, "non_affiliate_count": 0}

    # The captured URL must be exactly ``{server_base_url}/api/v1/quicklinks/``.
    assert len(mock.calls) == 1, (
        f"expected exactly 1 GET call, got {len(mock.calls)}: {mock.calls}"
    )
    captured_url = mock.calls[0]["url"]
    expected_base = urls.server_base_url()
    assert captured_url == f"{expected_base}/api/v1/quicklinks/", (
        f"got {captured_url!r}, expected {expected_base + '/api/v1/quicklinks/'!r}. "
        f"The pre-fix code hit affiliate_api_base + '/links/' "
        f"(which resolved to /api/affiliate/links/ — wrong). "
        f"Now hits server_base_url + '/api/v1/quicklinks/'."
    )


def test_update_affiliate_links_dev_url_constructs_correctly(
    monkeypatch: pytest.MonkeyPatch,
    fake_install_store,
) -> None:
    """In dev mode, the URL must be ``http://192.168.1.67:5000/api/v1/quicklinks/``.

    COMPAT-002 (2026-08-29): same contract as the prod test
    but with the dev profile active. Confirms the run-mode
    profile flows through to the correct ``server_base_url``,
    and that the path is ``/api/v1/quicklinks/`` (not the
    old ``/api/affiliate/links/``).
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
            "http://192.168.1.67:5000/api/v1/quicklinks/"
        ), (
            f"dev-mode URL construction failed: got {captured_url!r}. "
            f"Expected ``http://192.168.1.67:5000/api/v1/quicklinks/`` "
            f"(server_base_url + /api/v1/quicklinks/)."
        )
    finally:
        # Always reset run-mode so the next test in the suite
        # starts clean.
        urls.set_run_mode("prod")
        urls.reload()


# -----------------------------------------------------------------------------
# DESK T-NEW-057 — APIClient must use x-api-key header, not Bearer.
# -----------------------------------------------------------------------------


def test_apiclient_uses_x_api_key_header_not_bearer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """APIClient must attach the api_key as ``x-api-key``, not
    ``Authorization: Bearer``.

    Regression for DESK T-NEW-057 — the server's
    @require_desktop_api_key decorator reads
    ``request.headers.get("x-api-key")`` and returns 401 when
    the header is missing or named differently.
    """
    from nchantdoffice.utilities.links import APIClient

    session = _MockSession()
    monkeypatch.setattr(
        "nchantdoffice.utilities.links.requests.Session",
        lambda: session,
    )

    APIClient(
        base_url="http://192.168.1.67:5000",
        api_key="nk_test_DESKTOP_KEY_abc123",
    )

    # After construction, the session should have x-api-key set
    # and NOT Authorization.
    assert session.headers.get("x-api-key") == "nk_test_DESKTOP_KEY_abc123", (
        f"APIClient did not set x-api-key header. "
        f"Got headers: {session.headers!r}"
    )
    assert "Authorization" not in session.headers, (
        f"APIClient should NOT set Authorization header (FAB-User "
        f"convention). The desktop-install API uses x-api-key. "
        f"Got headers: {session.headers!r}"
    )


def test_apiclient_no_auth_sends_no_auth_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When constructed without an api_key, APIClient sends NO
    auth header at all (so unauth endpoints like ``/health``
    still work without spurious credentials).
    """
    from nchantdoffice.utilities.links import APIClient

    session = _MockSession()
    monkeypatch.setattr(
        "nchantdoffice.utilities.links.requests.Session",
        lambda: session,
    )

    APIClient(base_url="http://192.168.1.67:5000")

    # No auth header should be set on the session.
    assert session.headers.get("x-api-key") is None
    assert session.headers.get("Authorization") is None


def test_401_response_returns_zeros_not_crash(
    monkeypatch: pytest.MonkeyPatch,
    fake_install_store,
) -> None:
    """A 401 from the affiliate endpoint must NOT crash the boot
    (it just means the install hasn't bootstrapped yet, or the
    api_key is stale). The desktop should log the failure,
    persist 0 affiliates, and move on.

    DESK T-NEW-057 contract: even with the x-api-key header
    fix, a 401 can still happen transiently (e.g. the desktop
    is mid-bootstrap and the api_key hasn't been written to
    InstallStore yet). The affiliate sync must fail soft.
    """
    from nchantdoffice.utilities import links
    from nchantdoffice.utilities import urls

    urls.set_run_mode("prod")
    urls.reload()

    # Mock the session to return 401 Unauthorized (the real
    # response from the live server when the desktop is in a
    # pre-bootstrap state).
    session = _MockSession(
        body={"error": "API key is missing"}, status_code=401
    )

    def _fake_session_factory(*args, **kwargs):
        return session

    monkeypatch.setattr(links.requests, "Session", _fake_session_factory)

    class _FakeModel:
        def remove_affiliate_links(self) -> None:
            pass

    # Must NOT raise.
    result = links.update_affiliate_links(model=_FakeModel(), reload=False)
    assert result == {"affiliate_count": 0, "non_affiliate_count": 0}, (
        f"update_affiliate_links must return zeros on 401, not "
        f"propagate the error. Got: {result!r}"
    )


def test_update_affiliate_links_passes_api_key_as_x_api_key_header(
    monkeypatch: pytest.MonkeyPatch,
    fake_install_store,
) -> None:
    """End-to-end: ``update_affiliate_links`` reads the install's
    api_key from InstallStore and sends it as the
    ``x-api-key`` header on the affiliate GET.

    Regression for DESK T-NEW-057 — the live launch was
    failing with 401 because APIClient was setting
    ``Authorization: Bearer`` (FAB-User convention) instead
    of ``x-api-key`` (Desktop-Install convention), AND because
    ``update_affiliate_links`` wasn't reading the api_key
    from InstallStore at all (the client was constructed
    with ``api_key=None``).

    This test pins both: the api_key is read from
    InstallStore AND it reaches the request as ``x-api-key``.
    """
    from nchantdoffice.utilities import links
    from nchantdoffice.utilities import urls

    urls.set_run_mode("prod")
    urls.reload()
    fake_install_store["set"]("nk_test_DESKTOP_KEY_xyz")

    # The session captures the headers attached at construction
    # time. We verify them post-construction.
    session = _MockSession(body=[])

    def _fake_session_factory(*args, **kwargs):
        return session

    monkeypatch.setattr(links.requests, "Session", _fake_session_factory)

    class _FakeModel:
        def remove_affiliate_links(self) -> None:
            pass

    links.update_affiliate_links(model=_FakeModel(), reload=False)

    # The api_key from InstallStore must have reached the
    # request as x-api-key (not as Authorization: Bearer).
    assert session.headers.get("x-api-key") == "nk_test_DESKTOP_KEY_xyz", (
        f"update_affiliate_links did not pass the install's "
        f"api_key as x-api-key. Got headers: {session.headers!r}"
    )
    assert "Authorization" not in session.headers


def test_update_affiliate_links_skips_when_no_api_key(
    monkeypatch: pytest.MonkeyPatch,
    fake_install_store,
) -> None:
    """If the install has no api_key yet (pre-bootstrap), skip
    the affiliate call entirely. The next launch — once the
    bootstrap has minted an api_key — will retry.

    DESK T-NEW-058: this is a sequencing fix. The bootstrap
    runs synchronously in NchantdOfficeCloakView.__init__,
    but the model init (which calls update_affiliate_links)
    can fire before the bootstrap has completed. The fix is
    NOT to make the affiliate call wait (that would require a
    callback chain) — the fix is to skip when there's no key
    and let the next launch retry once the key is on file.
    """
    from nchantdoffice.utilities import links
    from nchantdoffice.utilities import urls

    urls.set_run_mode("prod")
    urls.reload()
    fake_install_store["set"](None)  # pre-bootstrap state

    # The session SHOULD NOT be created at all when api_key is
    # None. Set up a session that would explode if invoked.
    def _should_not_be_called(*args, **kwargs):
        raise AssertionError(
            "update_affiliate_links must NOT construct a "
            "requests.Session when no api_key is available "
            "(DESK T-NEW-058)"
        )

    monkeypatch.setattr(
        links.requests, "Session", _should_not_be_called
    )

    class _FakeModel:
        def remove_affiliate_links(self) -> None:
            pass

    # Must NOT raise — just return zeros.
    result = links.update_affiliate_links(model=_FakeModel(), reload=False)
    assert result == {"affiliate_count": 0, "non_affiliate_count": 0}, (
        f"update_affiliate_links must return zeros when the install "
        f"has no api_key (skip path, not network call). Got: {result!r}"
    )
