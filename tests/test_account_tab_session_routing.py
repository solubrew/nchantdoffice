"""DESK T-NEW-140: account tab routes by session-cookie presence.

Pins the contract for ``NchantdOfficeAccountSettings._resolve_initial_url``:

  1. A session cookie (``nchantdoffice_session_instance`` /
     ``session`` / ``remember_token``) in the shared web profile's
     cookie store for the server origin ⇒ the tab routes to
     ``urls.user_account_url()`` (the server-rendered account
     home), NOT the marketing registration/compare page.
  2. No session cookie ⇒ keeps the marketing URL (the fallback the
     has_pro/has_account branch chose).
  3. No profile pool / cookie API failure ⇒ keeps the marketing URL
     (best-effort; never blocks tab construction).

This is the fix for the "Settings tab doesn't persist login" bug:
the cookie WAS persisted (shared QWebEngineProfile), but the tab
always loaded the marketing URL, which doesn't surface the
logged-in dashboard.

The widget methods are plain instance methods, so they are invoked
unbound (``Widget._resolve_initial_url(fake_self, ...)``) with a
duck-typed ``self`` — no Qt widget construction needed. (PySide6
forbids ``object.__new__`` on QWidget subclasses.)
"""
from __future__ import annotations

import types


# ---------------------------------------------------------------------------
# URL resolver stub (no Qt / app needed for the routing decision itself)
# ---------------------------------------------------------------------------


class _FakeUrls:
    """Minimal stand-in for nchantdoffice.utilities.urls."""

    SERVER_BASE = "https://192.168.1.67"
    USER_ACCOUNT = "https://192.168.1.67/user-account/home"
    MARKETING = "https://192.168.1.67/registration"

    def server_base_url(self) -> str:
        return self.SERVER_BASE

    def user_account_url(self) -> str:
        return self.USER_ACCOUNT

    def registration_url(self) -> str:
        return self.MARKETING


class _FakeQByteArray:
    """Stand-in for PySide6 QByteArray — has .data() -> bytes."""

    def __init__(self, value: bytes) -> None:
        self._value = value

    def data(self) -> bytes:
        return self._value


class _FakeCookie:
    def __init__(self, name: str) -> None:
        self._name = _FakeQByteArray(name.encode("utf-8"))

    def name(self):
        return self._name


class _FakeCookieStore:
    def __init__(self, cookie_names) -> None:
        self._cookies = [_FakeCookie(n) for n in cookie_names]

    def cookiesForUrl(self, qurl):
        return self._cookies


class _FakeProfile:
    def __init__(self, cookie_names) -> None:
        self._store = _FakeCookieStore(cookie_names)

    def cookieStore(self):
        return self._store


def _get_widget_cls():
    from nchantdoffice.widgets.config.accounts import NchantdOfficeAccountSettings

    return NchantdOfficeAccountSettings


def _make_self(profile=None):
    """Duck-typed stand-in for the widget instance.

    Wires the two cookie-related helpers so calling
    _resolve_initial_url with this fake exercises the full path.
    """
    import nchantdoffice.widgets.config.accounts as _acct_mod

    return types.SimpleNamespace(
        _get_shared_web_profile=lambda: profile,
        _profile_has_session_cookie=lambda p, urls: _acct_mod.NchantdOfficeAccountSettings._profile_has_session_cookie(
            None, p, urls
        ),
    )


class TestResolveInitialUrl:
    def _call(self, fake_self, urls, fallback):
        return _get_widget_cls()._resolve_initial_url(fake_self, urls, fallback)

    def test_session_cookie_routes_to_account_home(self):
        s = _make_self(_FakeProfile(["nchantdoffice_session_instance"]))
        urls = _FakeUrls()
        assert self._call(s, urls, urls.registration_url()) == urls.user_account_url()

    def test_flask_default_session_name_routes_too(self):
        s = _make_self(_FakeProfile(["session"]))
        urls = _FakeUrls()
        assert self._call(s, urls, urls.registration_url()) == urls.user_account_url()

    def test_remember_token_routes_too(self):
        s = _make_self(_FakeProfile(["remember_token"]))
        urls = _FakeUrls()
        assert self._call(s, urls, urls.registration_url()) == urls.user_account_url()

    def test_unrelated_cookies_keep_marketing_url(self):
        s = _make_self(_FakeProfile(["theme", "lead_id", "_ga"]))
        urls = _FakeUrls()
        assert self._call(s, urls, urls.registration_url()) == urls.registration_url()

    def test_no_cookies_keeps_marketing_url(self):
        s = _make_self(_FakeProfile([]))
        urls = _FakeUrls()
        assert self._call(s, urls, urls.registration_url()) == urls.registration_url()

    def test_no_profile_keeps_marketing_url(self):
        s = _make_self(None)
        urls = _FakeUrls()
        assert self._call(s, urls, urls.registration_url()) == urls.registration_url()

    def test_cookie_api_failure_keeps_marketing_url(self):
        class _Boom:
            def cookiesForUrl(self, qurl):
                raise RuntimeError("cookie api unavailable")

        class _BoomProfile:
            def cookieStore(self):
                return _Boom()

        s = _make_self(_BoomProfile())
        urls = _FakeUrls()
        assert self._call(s, urls, urls.registration_url()) == urls.registration_url()


class TestProfileHasSessionCookie:
    def _call(self, fake_self, profile, urls):
        return _get_widget_cls()._profile_has_session_cookie(fake_self, profile, urls)

    def test_session_cookie_found(self):
        s = types.SimpleNamespace()
        urls = _FakeUrls()
        assert self._call(s, _FakeProfile(["nchantdoffice_session_instance"]), urls)

    def test_remember_token_found(self):
        s = types.SimpleNamespace()
        urls = _FakeUrls()
        assert self._call(s, _FakeProfile(["remember_token"]), urls)

    def test_unrelated_not_found(self):
        s = types.SimpleNamespace()
        urls = _FakeUrls()
        assert not self._call(s, _FakeProfile(["theme", "_ga"]), urls)

    def test_empty_not_found(self):
        s = types.SimpleNamespace()
        urls = _FakeUrls()
        assert not self._call(s, _FakeProfile([]), urls)


class TestCookieLoadWatcher:
    def test_watcher_routes_on_cookie_added(self):
        """Simulates: initView found no cookie (store still loading);
        the watcher fires when the session cookie streams in."""
        calls = []
        urls = _FakeUrls()

        store = _FakeCookieStore([])  # starts empty

        class _LiveStore:
            """Cookie store whose cookieAdded can be connected and fired."""

            def __init__(self):
                self._handlers = []
                self._cookies = []

            def cookiesForUrl(self, qurl):
                return list(self._cookies)

            def loadAllCookies(self):
                # Simulate the disk read streaming cookies in —
                # fire each handler with each cookie.
                for c in self._cookies:
                    for h in list(self._handlers):
                        h(c)

            def cookieAdded(self):
                # Signal-like object
                return self

            def _connect(self, handler):
                self._handlers.append(handler)

            def _disconnect(self, handler):
                if handler in self._handlers:
                    self._handlers.remove(handler)

        # Piggyback connect/disconnect on the store object
        live = _LiveStore()

        class _Signal:
            def __init__(self, store):
                self._store = store

            def connect(self, h):
                self._store._connect(h)

            def disconnect(self, h):
                self._store._disconnect(h)

        live.cookieAdded = _Signal(live)

        class _LiveProfile:
            def __init__(self, store):
                self._store = store

            def cookieStore(self):
                return self._store

        # Seed the session cookie as if loaded from disk
        live._cookies = [_FakeCookie("nchantdoffice_session_instance")]
        profile = _LiveProfile(live)

        s = types.SimpleNamespace(
            browser=types.SimpleNamespace(),  # non-None: watcher arms
            _get_shared_web_profile=lambda: profile,
            _navigate_account_home=lambda urls_: calls.append(urls_.user_account_url()),
            _profile_has_session_cookie=lambda p, urls_: _get_widget_cls()._profile_has_session_cookie(s, p, urls_),
            _cookie_watch_armed_at=None,
        )
        _get_widget_cls()._watch_cookie_load(s, urls)
        # loadAllCookies fired synchronously in our simulation →
        # the watcher should have routed already.
        assert calls == [urls.user_account_url()]

    def test_watcher_no_cookie_no_route(self):
        calls = []
        urls = _FakeUrls()

        class _EmptyStore:
            def cookiesForUrl(self, qurl):
                return []

            def loadAllCookies(self):
                pass

            cookieAdded = types.SimpleNamespace(
                connect=lambda h: None, disconnect=lambda h: None
            )

        class _EmptyProfile:
            def cookieStore(self):
                return _EmptyStore()

        s = types.SimpleNamespace(
            _get_shared_web_profile=lambda: _EmptyProfile(),
            _navigate_account_home=lambda urls_: calls.append(1),
            _cookie_watch_armed_at=None,
        )
        _get_widget_cls()._watch_cookie_load(s, urls)
        assert calls == []


class TestNavigateAccountHome:
    def test_engine_seturl_preferred(self):
        urls = _FakeUrls()
        set_calls = []
        engine = types.SimpleNamespace(setUrl=lambda q: set_calls.append(str(q)))
        browser = types.SimpleNamespace(engine=engine)
        s = types.SimpleNamespace(browser=browser)

        # pyqt.QUrl may not be importable without a QApplication; the
        # method imports it at module level via the widget module's
        # import. Call through the class with our fake self.
        _get_widget_cls()._navigate_account_home(s, urls)
        assert len(set_calls) == 1
        assert urls.USER_ACCOUNT in set_calls[0]

    def test_no_browser_noop(self):
        s = types.SimpleNamespace(browser=None)
        _get_widget_cls()._navigate_account_home(s, _FakeUrls())  # must not raise


class TestGetSharedWebProfile:
    def _call(self, fake_self):
        return _get_widget_cls()._get_shared_web_profile(fake_self)

    def test_pool_default_profile_returned(self):
        profile = _FakeProfile([])
        s = types.SimpleNamespace(
            app=types.SimpleNamespace(
                model=types.SimpleNamespace(
                    get_web_profiles=lambda: types.SimpleNamespace(
                        get_default_profile=lambda: profile
                    )
                )
            )
        )
        assert self._call(s) is profile

    def test_no_pool_returns_none(self):
        class _NoPoolModel:
            def get_web_profiles(self):
                return None

        s = types.SimpleNamespace(
            app=types.SimpleNamespace(model=_NoPoolModel())
        )
        assert self._call(s) is None

    def test_missing_model_returns_none(self):
        s = types.SimpleNamespace(app=None)
        assert self._call(s) is None

    def test_model_without_pool_attr_returns_none(self):
        s = types.SimpleNamespace(
            app=types.SimpleNamespace(model=types.SimpleNamespace())
        )
        assert self._call(s) is None
