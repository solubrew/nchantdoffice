"""DESK T-NEW-140 v5: account tab routes by session-cookie presence
using a self-maintained cookie snapshot (PySide6's QWebEngineCookieStore
has no ``cookiesForUrl`` — only the ``cookieAdded`` signal).

Pins the routing contract for ``NchantdOfficeAccountSettings``:

  1. Cookie snapshot has a session-name cookie for the origin
     → route to ``user_account_url()``.
  2. No cookie + ``user.has_account`` is True
     → route to ``login_url()`` (never ``registration_url()``).
  3. No cookie + no account
     → keep the marketing URL decided by the has_pro/has_account branch.
  4. Profile pool / cookie-store query failures
     → keep marketing URL (best-effort; never blocks tab construction).

Snapshot tests simulate ``cookieAdded`` by appending to the fake
``self._known_cookies`` list directly.
"""
from __future__ import annotations

import types

from nchantdoffice.utilities import urls as _urls_mod


# ---------------------------------------------------------------------------
# URL resolver stub
# ---------------------------------------------------------------------------


class _FakeUrls:
    SERVER_BASE = "https://192.168.1.67"
    USER_ACCOUNT = "https://192.168.1.67/user-account/home"
    LOGIN = "https://192.168.1.67/auth/login"
    REGISTRATION = "https://192.168.1.67/registration"
    COMPARE = "https://192.168.1.67/compare"

    def server_base_url(self) -> str:
        return self.SERVER_BASE

    def user_account_url(self) -> str:
        return self.USER_ACCOUNT

    def login_url(self) -> str:
        return self.LOGIN

    def registration_url(self) -> str:
        return self.REGISTRATION

    def upgrade_compare_url(self) -> str:
        return self.COMPARE


def _make_self(cookies=None, has_account=False, has_pro=False):
    """Duck-typed stand-in for the widget instance.

    Returns a SimpleNamespace with the minimum surface area the
    routing methods need. Tests that want to intercept navigation
    or cookie lookup should override attributes AFTER calling this.
    """
    user = types.SimpleNamespace(has_account=has_account, has_pro=has_pro)
    profile = types.SimpleNamespace(storageName=lambda: "test-profile")
    s = types.SimpleNamespace(
        _known_cookies=list(cookies or []) if cookies is not None else [],
        user=user,
        _get_shared_web_profile=lambda: profile if cookies is not None else None,
        _navigate_account_home=lambda urls: None,  # no-op by default
    )
    # Bind the routing helpers (which call self.X) so v5's logic
    # runs end-to-end. Tests that want to override a method should
    # do so AFTER this helper runs.
    cls = _widget_cls()
    s._has_session_cookie_in_snapshot = (
        lambda origin: cls._has_session_cookie_in_snapshot(s, origin)
    )
    s._on_cookie_added_to_snapshot = (
        lambda cookie: cls._on_cookie_added_to_snapshot(s, cookie)
    )
    return s


def _widget_cls():
    from nchantdoffice.widgets.config.accounts import NchantdOfficeAccountSettings

    return NchantdOfficeAccountSettings


# ---------------------------------------------------------------------------
# _resolve_initial_url (initView-time decision)
# ---------------------------------------------------------------------------


class TestResolveInitialUrl:
    def _call(self, fake_self, urls):
        return _widget_cls()._resolve_initial_url(fake_self, urls, urls.registration_url())

    def test_session_cookie_routes_to_account_home(self):
        s = _make_self(cookies=[("nchantdoffice_session_instance", "192.168.1.67", "/")])
        urls = _FakeUrls()
        assert self._call(s, urls) == urls.user_account_url()

    def test_remember_token_routes_too(self):
        s = _make_self(cookies=[("remember_token", "192.168.1.67", "/")])
        urls = _FakeUrls()
        assert self._call(s, urls) == urls.user_account_url()

    def test_domain_suffix_match(self):
        # ".192.168.1.67" in the cookie domain matches host "192.168.1.67".
        s = _make_self(cookies=[("session", ".192.168.1.67", "/")])
        urls = _FakeUrls()
        assert self._call(s, urls) == urls.user_account_url()

    def test_no_cookies_keeps_marketing(self):
        s = _make_self(cookies=[("theme", "192.168.1.67", "/")])
        urls = _FakeUrls()
        assert self._call(s, urls) == urls.registration_url()

    def test_other_domain_cookies_ignored(self):
        s = _make_self(cookies=[("session", "evil.com", "/")])
        urls = _FakeUrls()
        assert self._call(s, urls) == urls.registration_url()

    def test_no_profile_keeps_marketing(self):
        s = _make_self(cookies=None)
        urls = _FakeUrls()
        assert self._call(s, urls) == urls.registration_url()

    def test_no_cookie_has_account_routes_to_login(self):
        # DESK T-NEW-140 v4: user has an account (per local user record)
        # but the server session cookie is gone (expired / cleared).
        # We route to LOGIN, not REGISTRATION.
        s = _make_self(cookies=[], has_account=True)
        urls = _FakeUrls()
        assert self._call(s, urls) == urls.login_url()


# ---------------------------------------------------------------------------
# _on_cookie_added_to_snapshot + _has_session_cookie_in_snapshot
# ---------------------------------------------------------------------------


class TestCookieSnapshot:
    def test_append_and_match(self):
        s = _make_self()
        # Fake a cookie object with .name().data() / .domain().data() / .path().data()
        cookie = types.SimpleNamespace(
            name=lambda: types.SimpleNamespace(data=lambda: b"nchantdoffice_session_instance"),
            domain=lambda: types.SimpleNamespace(data=lambda: b"192.168.1.67"),
            path=lambda: types.SimpleNamespace(data=lambda: b"/"),
        )
        _widget_cls()._on_cookie_added_to_snapshot(s, cookie)
        assert len(s._known_cookies) == 1
        assert s._known_cookies[0][0] == "nchantdoffice_session_instance"
        assert _widget_cls()._has_session_cookie_in_snapshot(s, "https://192.168.1.67/")

    def test_append_handles_garbage_cookie(self):
        s = _make_self()

        class _BadCookie:
            def name(self):
                raise RuntimeError("cookie data unavailable")

        _widget_cls()._on_cookie_added_to_snapshot(s, _BadCookie())
        assert s._known_cookies == []

    def test_origin_match_ignores_unrelated_cookies(self):
        s = _make_self(
            cookies=[
                ("_ga", "google-analytics.com", "/"),
                ("lead_id", "192.168.1.67", "/"),
            ]
        )
        assert not _widget_cls()._has_session_cookie_in_snapshot(
            s, "https://192.168.1.67/"
        )


# ---------------------------------------------------------------------------
# _make_marketing_url_guard
# ---------------------------------------------------------------------------


class TestMarketingUrlGuard:
    def test_no_session_cookie_no_redirect(self):
        s = _make_self(cookies=[])
        navigated = []
        s._navigate_account_home = lambda urls: navigated.append(urls.user_account_url())
        guard = _widget_cls()._make_marketing_url_guard(s)
        # Guard expects a QUrl-like object with .toString()
        fake_qurl = types.SimpleNamespace(toString=lambda: "https://anywhere.example/registration")
        guard(fake_qurl)
        assert navigated == []

    def test_session_cookie_redirects_marketing_to_account(self):
        s = _make_self(
            cookies=[("nchantdoffice_session_instance", "192.168.1.67", "/")]
        )
        navigated = []
        s._navigate_account_home = lambda urls: navigated.append(urls.user_account_url())
        guard = _widget_cls()._make_marketing_url_guard(s)
        # Guard only cares that _navigate_account_home was invoked; it
        # doesn't need to inspect the URL because _navigate is the one
        # that decides the actual destination (via _urls.user_account_url()).
        fake_qurl = types.SimpleNamespace(toString=lambda: "https://anywhere.example/registration")
        guard(fake_qurl)
        assert len(navigated) == 1
        assert navigated[0].endswith("/user-account/home")


# ---------------------------------------------------------------------------
# _watch_cookie_load (re-arms on every show, prevents listener accumulation)
# ---------------------------------------------------------------------------


class TestCookieLoadWatcher:
    def test_watcher_routes_on_cookie_added(self):
        calls = []
        s = _make_self(cookies=[])

        handlers = []

        class _LiveStore:
            def cookiesForUrl(self, qurl):
                return []

            def loadAllCookies(self):
                # Simulate persistent cookie disk read streaming in
                # one cookie at a time.
                for name_b, domain_b, path_b in [
                    (b"nchantdoffice_session_instance", b"192.168.1.67", b"/")
                ]:
                    fake = type(
                        "FakeCookie",
                        (),
                        {
                            "name": lambda self, b=name_b: type(
                                "N", (), {"data": lambda self, b=b: b}
                            )(),
                            "domain": lambda self, b=domain_b: type(
                                "N", (), {"data": lambda self, b=b: b}
                            )(),
                            "path": lambda self, b=path_b: type(
                                "N", (), {"data": lambda self, b=b: b}
                            )(),
                        },
                    )()
                    for h in list(handlers):
                        h(fake)

            def connect(self, handler):
                handlers.append(handler)

            def disconnect(self, handler):
                if handler in handlers:
                    handlers.remove(handler)

        # cookieAdded is a Qt *signal* — in the real Qt API it's a
        # property that yields a Signal object, not a method.
        # Reflect that here so store.cookieAdded.connect(handler)
        # resolves to the Signal's connect method.
        class _CookieAddedSignal:
            def connect(self, h):
                handlers.append(h)

            def disconnect(self, h):
                if h in handlers:
                    handlers.remove(h)

        class _LiveStoreWithSignal(_LiveStore):
            cookieAdded = _CookieAddedSignal()

        class _Profile:
            def cookieStore(self):
                return _LiveStoreWithSignal()

        s._get_shared_web_profile = lambda: _Profile()
        s._navigate_account_home = lambda urls: calls.append(urls.user_account_url())
        s.browser = types.SimpleNamespace()  # non-None so the watcher arms
        urls = _FakeUrls()
        _widget_cls()._watch_cookie_load(s, urls)
        assert len(calls) == 1
        assert calls[0].endswith("/user-account/home")

    def test_watcher_no_op_without_browser(self):
        s = _make_self()
        s._get_shared_web_profile = lambda: types.SimpleNamespace(
            cookieStore=lambda: types.SimpleNamespace()
        )
        s.browser = None  # the critical case — no widget, no watcher
        _widget_cls()._watch_cookie_load(s, _FakeUrls())  # must not raise
