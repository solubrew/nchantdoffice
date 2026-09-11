# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid:
        name:
        description: >
        version: 0.0.0.0.0.0
        authority: filesystem
        security: seclvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from __future__ import annotations

from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.widgets.config.accounts import NchantdAccountOverview
from kahndor.logma import Logma
from nchantrs.widgets.config.accounts import NchantdAccountSettings
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.browsers.browsers import NchantdWebViewer
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.media.images import NchantdImage
from nchantrs.widgets.media.editors.editors import NchantdEntryEditor

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# Re-export ClaimFlow so the test suite can monkeypatch it on the
# accounts module (e.g. test_claim_flow.py patches
# accounts_mod.ClaimFlow to verify sync_with_server wires through).
from nchantdoffice.license.claim_flow import ClaimFlow  # noqa: F401

# ====================================================================================================================||
pxcfg = join(here, "_data_", "accounts.yaml")


class NchantdOfficeAccountOverview(NchantdAccountOverview):
    """Account overview widget showing account status and key metrics"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeAccountOverview").override(cfg))
        self.account_settings = None
        self.account_name_label = None
        self.account_type_label = None
        self.subscription_label = None
        self.storage_label = None
        self.documents_label = None

    def initModel(self) -> "NchantdOfficeAccountOverview":
        """"""
        super().initModel()
        self.account_settings = self.app.model.settings.account_settings
        return self

    def initView(self, cfg=None) -> "NchantdOfficeAccountOverview":
        """"""
        cfg = cfg or {}
        if not cfg.get("buttons", None):
            cfg["buttons"] = {}
        cfg["buttons"][100] = "_skip"
        super().initView(cfg)
        # Account name
        cfg = {"text": f"Account: {self.app.model.user.name}", "size": ["auto", "auto"]}
        self.account_name_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.account_name_label)
        # Account type
        account_type = "Pro" if self.app.model.user.has_pro else "Free"
        cfg = {"text": f"Type: {account_type}", "size": ["auto", "auto"]}
        self.account_type_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.account_type_label)
        # Subscription status
        subscription_status = "Active" if self.app.model.user.is_paid else "Inactive"
        cfg = {"text": f"Subscription: {subscription_status}", "size": ["auto", "auto"]}
        self.subscription_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.subscription_label)
        # Sprint 20: Storage usage (live). Query the user's quota
        # when available; fall back to a placeholder when the
        # account backend doesn't expose the quota yet.
        storage_quota = None
        storage_used = None
        try:
            user = getattr(self.app.model, "user", None)
            if user is not None:
                storage_quota = getattr(user, "storage_quota_gb", None)
                storage_used = getattr(user, "storage_used_gb", None)
        except Exception as exc:
            logma.warning(f"[accounts] storage query failed: {exc}")
        if storage_quota is None:
            storage_text = "Storage: unknown"
        else:
            used = storage_used if storage_used is not None else 0
            storage_text = f"Storage: {used:.2f} GB / {storage_quota} GB"
        cfg = {"text": storage_text, "size": ["auto", "auto"]}
        self.storage_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.storage_label)
        # Sprint 20: Document count (live). Query the
        # ``doc_media`` row count via ``model`` when available;
        # fall back to 0.
        document_count = 0
        try:
            counter = getattr(self.app.model, "get_document_count", None)
            if callable(counter):
                document_count = int(counter())
            else:
                counter = getattr(self.app.model, "documents_count", None)
                if isinstance(counter, int):
                    document_count = counter
        except Exception as exc:
            logma.warning(f"[accounts] document count query failed: {exc}")
        cfg = {"text": f"Documents: {document_count}", "size": ["auto", "auto"]}
        self.documents_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.documents_label)
        return self

    def initWidget(self) -> "NchantdOfficeAccountOverview":
        """"""
        self.initModel()
        self.initView()
        return self

    def refresh_account_info(self) -> "NchantdOfficeAccountOverview":
        """Refresh account information from server"""
        try:
            # Update account name
            if self.account_name_label:
                self.account_name_label.setText(f"Account: {self.app.model.user.name}")

            # Update account type
            if self.account_type_label:
                account_type = "Pro" if self.app.model.user.has_pro else "Free"
                self.account_type_label.setText(f"Type: {account_type}")

            # Update subscription
            if self.subscription_label:
                subscription_status = "Active" if self.app.model.user.is_paid else "Inactive"
                self.subscription_label.setText(f"Subscription: {subscription_status}")

            logma.info("Account information refreshed")
        except Exception as e:
            logma.error(f"Error refreshing account info: {e}")

        return self

    def get_account_summary(self) -> dict:
        """Get account summary as dictionary"""
        return {
            "name": self.app.model.user.name,
            "type": "Pro" if self.app.model.user.has_pro else "Free",
            "subscription": "Active" if self.app.model.user.is_paid else "Inactive",
            "has_account": self.app.model.user.has_account,
            "has_pro": self.app.model.user.has_pro,
        }


class NchantdOfficeAccountSettings(NchantdAccountSettings):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeAccountSettings").override(cfg))
        self.user = pyqt.QApplication.instance().model.user
        self.user_name = None
        self.account_status = None
        self.credits_status = None
        self.scrolling_ad = None
        self.register_button = None
        self.profile_image = None
        self.profile_label = None
        self.browser = None
        self.button = None
        # DESK T-NEW-140 v5: cookie snapshot (filled by cookieAdded
        # signal during _watch_cookie_load).
        self._known_cookies = []
        self._active_cookie_watcher = None
        self._cookie_watch_armed_at = None
        self._url_guard_busy = False

    def initModel(self) -> "NchantdOfficeAccountSettings":
        """"""
        super().initModel()
        self.account = self.app.model.settings.account_settings
        return self

    def initView(self, cfg=None) -> "NchantdOfficeAccountSettings":
        """"""
        cfg = cfg or {}
        if not cfg.get("buttons", None):
            cfg["buttons"] = {}
        cfg["buttons"][100] = "_skip"
        cfg["buttons"][101] = {"action": "refresh", "handler": self.cmd_refresh}
        super().initView(cfg)
        # T-removed: a large block of commented-out account-UI scaffolding
        # was here (L157-204). It referenced attributes that don't exist
        # (self.user.no_ads, self.scrolling_ad, NchantdEntryEditor)
        # and contained three stub-marker comments. The block was not
        # executing and obscured the actual initView flow. Removed; real
        # account UI work belongs in a follow-up sprint.
        # self.layout.addLayout(layout)
        # self.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft | pyqt.Qt.AlignmentFlag.AlignTop)

        layout = pyqt.QHBoxLayout()
        # profile_layout = pyqt.QVBoxLayout()
        # cfg = {"size": [200, 200]}
        # self.profile_image = NchantdImage(self, cfg).initWidget()
        # profile_layout.addWidget(self.profile_image)

        # cfg = {"size": [100, "auto"], "label": "Profile Details"}
        # self.profile_label = NchantdLabel(self, cfg).initWidget()
        # profile_layout.addWidget(self.profile_label)
        # profile_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
        # layout.addLayout(profile_layout)
        # DESK T-NEW-052: URLs route through the unified config
        # resolver — no hardcoded hostnames.
        from nchantdoffice.utilities import urls as _urls

        cfg = {
            "url": _urls.registration_url(),
            "size": [1600, 750],
            "is_simple": True,
        }
        if self.user is None:
            raise Exception("No User configured")
        if self.user.has_pro:
            cfg["url"] = _urls.whats_new_url()
        elif self.user.has_account:
            cfg["url"] = _urls.upgrade_compare_url()
        # DESK T-NEW-140: if a server session cookie already exists
        # in the persistent profile (the user previously logged in
        # to nchantdoffice.com in this desktop profile), route to
        # the server-rendered account page instead of the marketing
        # upsell. The cookie IS persisted (QWebEngineProfile is
        # shared across tabs/views), but the URL was always the
        # marketing page because that's what cfg["url"] was set
        # to. Routing to /user-account/home when the cookie is
        # present lets the server's session-cookie check pick up
        # the existing login and serve the dashboard.
        cfg["url"] = self._resolve_initial_url(_urls, cfg["url"])
        # If the synchronous check returned the marketing URL (cookie
        # not yet loaded into memory), arm a watcher that re-routes
        # the moment the persistent cookie store finishes streaming
        # cookies in. The watcher fires after the webview's first
        # showEvent (see initWidget → showEvent path).
        self._pending_cookie_watch_urls = _urls
        self._cookie_watch_armed_at = None
        # T-NEW-135: when the redirect_to_get_pro helper fired
        # with a reason (e.g. ``hit_100_nodes``), the model
        # stashed it on ``app.model.get_pro_redirect_reason``.
        # This widget is the destination of that redirect, so
        # we read + clear the stash here. We only append the
        # ``reason=`` query param to the *compare* URL --
        # the whats_new / registration URLs are for users
        # who haven't hit the cap and shouldn't be touched.
        try:
            stash = getattr(
                getattr(self.app, "model", None),
                "get_pro_redirect_reason",
                None,
            )
            # DESK T-NEW-052: compare URL comes from the resolver.
            from nchantdoffice.utilities import urls as _urls

            if stash and cfg["url"] == _urls.upgrade_compare_url():
                cfg["url"] = self._append_url_param(cfg["url"], "reason", str(stash))
                # Clear the stash after a successful reason-param
                # append so the param is only added once per session.
            if (
                stash
                and cfg["url"] == _urls.upgrade_compare_url()
                and hasattr(
                    getattr(self.app, "model", None),
                    "get_pro_redirect_reason",
                )
            ):
                self.app.model.get_pro_redirect_reason = None
        except Exception as e:
            logma.warning(f"[accounts] initView: reason-param append " f"failed: {e}")
        self.browser = NchantdWebViewer(self, cfg).initWidget()
        layout.addWidget(self.browser)
        self.layout.addLayout(layout)
        # DESK T-NEW-140 v3: install a standing URL guard on the
        # embedded browser. Tab re-activation re-fires
        # populate_document(active_url) with the URL recorded at
        # construction — if that was a marketing page (widget built
        # before login), every return to the Settings node reloads
        # the marketing page even though the session cookie now
        # exists. The guard redirects any marketing-URL load to the
        # account home whenever a session cookie is present.
        try:
            self.browser.engine.urlChanged.connect(
                self._make_marketing_url_guard()
            )
        except Exception as e:
            logma.warning(f"[accounts] url-guard install failed: {e}")
        return self

    def _make_marketing_url_guard(self):
        """Build the urlChanged redirect guard (DESK T-NEW-140 v5).

        Returns a callable(QUrl) that rewrites any navigation to a
        marketing page into a navigation to the account home WHEN
        the shared profile holds a session cookie. Re-entrancy is
        guarded by a flag: the guard's own redirect doesn't loop.
        """
        import nchantdoffice.utilities.urls as _urls_mod

        marketing_markers = ("/registration", "/compare", "/whats_new")

        def _guard(qurl):
            if getattr(self, "_url_guard_busy", False):
                return
            try:
                url_str = qurl.toString()
                if not any(m in url_str for m in marketing_markers):
                    return
                if not self._has_session_cookie_in_snapshot(
                    _urls_mod.server_base_url()
                ):
                    return
                # Cookie present + marketing URL -> redirect.
                self._url_guard_busy = True
                try:
                    logma.info(
                        f"[accounts] url-guard: {url_str} -> account home "
                        f"(session cookie present)"
                    )
                    self._navigate_account_home(_urls_mod)
                finally:
                    # Release on the next event-loop tick so the
                    # redirect's own urlChanged doesn't re-trigger.
                    from nchantrs.libraries import pyqt as _pyqt

                    _pyqt.QTimer.singleShot(0, lambda: setattr(self, "_url_guard_busy", False))
            except Exception as e:
                logma.warning(f"[accounts] url-guard failed: {e}")

        return _guard

    # --- Cookie snapshot (DESK T-NEW-140 v5) ---------------------------
    # PySide6's QWebEngineCookieStore has NO ``cookiesForUrl`` method.
    # The only public access is the ``cookieAdded`` signal. So we
    # maintain our own cookie snapshot populated by that signal,
    # and use it for the synchronous routing check.
    #
    # Every code path logs verbosely — v1-v4 silently fell back to
    # the marketing URL because the sync check always failed (Qt API
    # mismatch / wrong API). v5 logs every branch.
    _SESSION_COOKIE_NAMES = frozenset({
        "nchantdoffice_session_instance",  # Flask app session cookie
        "session",                         # Flask default (in case of rename)
        "remember_token",                  # flask-login "remember me" cookie
    })

    def _on_cookie_added_to_snapshot(self, cookie):
        """Append to the in-memory cookie snapshot."""
        try:
            name = cookie.name().data().decode("utf-8", "replace")
            domain = cookie.domain().data().decode("utf-8", "replace")
            path = cookie.path().data().decode("utf-8", "replace")
            self._known_cookies.append((name, domain, path))
            logma.info(
                f"[accounts] snapshot += ({name!r}, domain={domain!r}, "
                f"path={path!r}) [total={len(self._known_cookies)}]"
            )
        except Exception as e:
            logma.warning(f"[accounts] snapshot append failed: {e!r}")

    def _has_session_cookie_in_snapshot(self, server_origin: str) -> bool:
        """True if any snapshot cookie is a session cookie for the origin.

        Domain matching is suffix-based per RFC 6265 (a cookie for
        ``192.168.1.67`` matches the origin ``https://192.168.1.67``).
        """
        # Read the class attribute dynamically so subclasses can extend it.
        session_names = getattr(type(self), "_SESSION_COOKIE_NAMES", frozenset({
            "nchantdoffice_session_instance",
            "session",
            "remember_token",
        }))
        try:
            host = server_origin.split("://", 1)[-1].split("/", 1)[0].lower()
        except Exception as e:
            logma.warning(f"[accounts] origin parse failed: {e}")
            return False
        logma.info(
            f"[accounts] snapshot check: origin_host={host!r}, "
            f"snapshot size={len(self._known_cookies)}, "
            f"session_names={sorted(session_names)}"
        )
        for name, domain, _path in self._known_cookies:
            if name not in session_names:
                continue
            d = domain.lower().lstrip(".")
            if host == d or host.endswith("." + d):
                logma.info(
                    f"[accounts] snapshot MATCH: name={name!r} "
                    f"domain={domain!r} -> origin_host={host!r}"
                )
                return True
        logma.info("[accounts] snapshot: no session cookie match for origin")
        return False

    def _resolve_initial_url(self, _urls, fallback_url: str) -> str:
        """DESK T-NEW-140: pick the initial URL for the account browser.

        Decision tree (every branch logs):
          cookie present                   -> user_account_url() (logged in)
          no cookie, user.has_account=True -> login_url() (logged out, has acct)
          no cookie, !has_account           -> keep marketing URL (anon signup)
        """
        logma.info(
            f"[accounts] initView routing: fallback_url={fallback_url}, "
            f"user.has_account={getattr(self.user, 'has_account', False) if self.user else 'no_user'}, "
            f"user.has_pro={getattr(self.user, 'has_pro', False) if self.user else 'no_user'}"
        )
        try:
            profile = self._get_shared_web_profile()
            logma.info(
                f"[accounts] initView: shared profile -> "
                f"{'OK at ' + profile.storageName() if profile else 'NONE'}"
            )
            if profile is None:
                return fallback_url
            origin = _urls.server_base_url()
            if self._has_session_cookie_in_snapshot(origin):
                logma.info(
                    f"[accounts] initView -> user_account_url() (cookie present)"
                )
                return _urls.user_account_url()
            # No cookie. If the local user record says an account
            # exists, route to LOGIN (never to /registration).
            if getattr(self.user, "has_account", False):
                logma.info(
                    "[accounts] initView -> login_url() (user.has_account, "
                    "no cookie — must re-authenticate)"
                )
                return _urls.login_url()
            logma.info(
                "[accounts] initView -> keeping marketing URL "
                "(no cookie, no account)"
            )
        except Exception as e:
            logma.warning(f"[accounts] initView routing check failed: {e!r}")
        return fallback_url

    def _watch_cookie_load(self, _urls) -> None:
        """DESK T-NEW-140 v5: signal-driven cookie loader.

        1. reset the snapshot,
        2. connect cookieAdded -> snapshot.append,
        3. call loadAllCookies() to trigger the disk read,
        4. each cookieAdded fills the snapshot; we re-check after
           every add and route when the session cookie arrives.
        """
        import datetime as _dt

        try:
            profile = self._get_shared_web_profile()
            browser = getattr(self, "browser", None)
            if profile is None or browser is None:
                logma.info(
                    "[accounts] watch: profile or browser missing "
                    f"(profile={'OK' if profile else 'NONE'}, "
                    f"browser={'OK' if browser else 'NONE'})"
                )
                return
            store = profile.cookieStore()
            # Reset the snapshot so the new loadAllCookies() stream
            # produces a clean, complete snapshot (no stale entries
            # from previous calls).
            self._known_cookies = []
            logma.info("[accounts] watch: snapshot reset; connecting cookieAdded")

            def _on_cookie_added_with_route(cookie):
                self._on_cookie_added_to_snapshot(cookie)
                if self._has_session_cookie_in_snapshot(_urls.server_base_url()):
                    logma.info(
                        "[accounts] watch: session cookie arrived -> "
                        "routing to user_account_url()"
                    )
                    try:
                        store.cookieAdded.disconnect(_on_cookie_added_with_route)
                    except Exception:
                        pass
                    self._navigate_account_home(_urls)

            prev = getattr(self, "_active_cookie_watcher", None)
            if prev is not None:
                try:
                    store.cookieAdded.disconnect(prev)
                except Exception:
                    pass
            self._active_cookie_watcher = _on_cookie_added_with_route
            store.cookieAdded.connect(_on_cookie_added_with_route)
            store.loadAllCookies()
            self._cookie_watch_armed_at = _dt.datetime.now()
            logma.info(
                "[accounts] watch armed; loadAllCookies() fired "
                f"at {_dt.datetime.now().isoformat(timespec='seconds')}"
            )
        except Exception as e:
            logma.warning(f"[accounts] watch failed: {e!r}")

    def _navigate_account_home(self, _urls) -> None:
        """Navigate the embedded account browser to the account home."""
        browser = getattr(self, "browser", None)
        if browser is None:
            return
        url = _urls.user_account_url()
        # Refresh the viewer's active_url so future tab-activation
        # re-fires of populate_document(active_url) load the account
        # home, not the stale marketing URL recorded at construction.
        try:
            browser.set_url_path(url)
        except Exception as e:
            logma.warning(f"[accounts] set_url_path refresh failed: {e}")
        try:
            engine = getattr(browser, "engine", None)
            if engine is not None:
                engine.setUrl(pyqt.QUrl(url))
                logma.info(f"[accounts] routed to {url}")
                return
        except Exception as e:
            logma.warning(f"[accounts] engine.setUrl failed: {e}")
        try:
            browser.setUrl(pyqt.QUrl(url))
            logma.info(f"[accounts] routed to {url} (viewer-level)")
        except Exception as e:
            logma.warning(f"[accounts] viewer.setUrl failed: {e}")

    def _get_shared_web_profile(self):
        """Return the app-level shared QWebEngineProfile (or None).

        The profile pool lives on ``app.model.get_web_profiles()``
        (nchantrs applicationmodels). The pool's *default* profile is
        the persistent one every embedded view shares — that's where
        the server session cookie is stored.
        """
        try:
            model = getattr(getattr(self, "app", None), "model", None)
            if model is None or not hasattr(model, "get_web_profiles"):
                return None
            pool = model.get_web_profiles()
            return pool.get_default_profile()
        except Exception as e:
            logma.warning(f"[accounts] shared profile lookup failed: {e}")
            return None

    @staticmethod
    def _append_url_param(url: str, key: str, value: str) -> str:
        """T-NEW-135 helper: append ``key=value`` to ``url`` as a
        query string parameter. Preserves any existing query,
        uses stdlib ``urllib.parse`` for safe encoding.

        Returns the input URL unchanged if it doesn't parse
        cleanly -- the caller is in a best-effort UX path,
        never a security boundary.
        """
        from urllib.parse import urlencode, urlparse, urlunparse

        try:
            parsed = urlparse(url)
            existing: dict = {}
            if parsed.query:
                for kv in parsed.query.split("&"):
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        existing[k] = v
            existing[key] = value
            return urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    urlencode(existing),
                    parsed.fragment,
                )
            )
        except Exception:
            return url

    def initWidget(self) -> "NchantdOfficeAccountSettings":
        """ """
        self.initModel()
        self.initView()
        return self

    def showEvent(self, event):
        """DESK T-NEW-140: re-evaluate routing on every show.

        The tab widget is NOT destroyed when the user navigates away —
        Qt just hides it. So a tab constructed BEFORE login (no
        session cookie) keeps showing the marketing page forever,
        even after the user logs in elsewhere in the app. Re-running
        the routing decision on every showEvent fixes that.

        Also arms the async cookie-load watcher when the synchronous
        check comes back empty (persistent cookies may still be
        streaming in from disk).
        """
        super_show = getattr(super(), "showEvent", None)
        if super_show is not None:
            try:
                super_show(event)
            except Exception:
                pass
        try:
            urls = getattr(self, "_pending_cookie_watch_urls", None)
            browser = getattr(self, "browser", None)
            if urls is None or browser is None:
                return
            # Synchronous check first — cookie may already be loaded
            # (e.g. this show follows a completed login elsewhere).
            profile = self._get_shared_web_profile()
            if profile is not None and self._has_session_cookie_in_snapshot(
                urls.server_base_url()
            ):
                # Only re-route if the browser is still parked on a
                # marketing URL (user may have navigated manually).
                engine = getattr(browser, "engine", None)
                current = (
                    engine.url().toString() if engine is not None and hasattr(engine, "url") else ""
                )
                marketing_markers = (
                    "/registration", "/compare", "/whats_new",
                )
                if any(m in current for m in marketing_markers) or not current:
                    logma.info(
                        "[accounts] showEvent: session cookie present -> "
                        "routing to user-account home"
                    )
                    self._navigate_account_home(urls)
                    return
            # No cookie synchronously → arm/re-arm the watcher. The
            # watcher is one-shot per cookieAdded burst; re-arming on
            # each show covers the "logged in since last show" case
            # where cookieAdded fired while this tab was hidden and
            # the one-shot already consumed itself.
            self._watch_cookie_load(urls)
        except Exception as e:
            logma.warning(f"[accounts] showEvent cookie-watch arm failed: {e}")

    def cmd_refresh(self, event=None, *args, **kwargs):
        """"""
        super().cmd_refresh(event, args, kwargs)

    def save_account_settings(self) -> bool:
        """Save account settings to user model"""
        try:
            # Update user name if changed
            if self.user_name and self.user_name.text():
                new_name = self.user_name.text()
                if new_name != self.app.model.user.name:
                    self.app.model.user.name = new_name
                    logma.info(f"Updated user name to: {new_name}")

            # Save to persistent storage
            if hasattr(self.app.model, "save_user_settings"):
                self.app.model.save_user_settings()
                logma.info("Account settings saved")

            return True

        except Exception as e:
            logma.error(f"Error saving account settings: {e}")
            return False

    def load_account_settings(self) -> bool:
        """Load account settings from the local user model + live API.

        Two-phase load:
          1. Populate the local cached values (name, status, credits)
             from ``self.app.model.user`` so the UI is never blank.
          2. Make a live API call to nchantrs.com (via
             ``sync_with_server``) to refresh the cached values
             when an API key is configured.

        Returns ``True`` if either phase succeeded.
        """
        try:
            user = self.app.model.user
            # Phase 1 - populate from local cache
            if self.user_name:
                self.user_name.setPlaceholderText(f"{user.name}")
            if self.account_status:
                self.account_status.setPlaceholderText(f"{user.nchantrs_account_status}")
            if self.credits_status:
                self.credits_status.setPlaceholderText(f"{user.nchantrs_account_credits}")

            # Phase 2 - live API refresh (only if we have a key)
            if getattr(user, "apikey", None):
                try:
                    self.sync_with_server()
                except Exception as e:
                    logma.error(f"[accounts] load_account_settings: live refresh failed: {e}", exc_info=True)
                # Re-populate with whatever the sync updated
                if self.user_name:
                    self.user_name.setPlaceholderText(f"{user.name}")
                if self.account_status:
                    self.account_status.setPlaceholderText(f"{user.nchantrs_account_status}")
                if self.credits_status:
                    self.credits_status.setPlaceholderText(f"{user.nchantrs_account_credits}")

            logma.info("Account settings loaded")
            return True

        except Exception as e:
            logma.error(f"Error loading account settings: {e}", exc_info=True)
            return False

    def validate_account_settings(self) -> dict:
        """Validate account settings before saving"""
        errors = []

        # Validate user name
        if self.user_name and self.user_name.text():
            name = self.user_name.text().strip()
            if len(name) < 2:
                errors.append("User name must be at least 2 characters")
            if len(name) > 100:
                errors.append("User name must be less than 100 characters")

        return {"valid": len(errors) == 0, "errors": errors}

    def update_account_status(self, status: str) -> "NchantdOfficeAccountSettings":
        """Update account status display"""
        if self.account_status:
            self.account_status.setPlaceholderText(str(status))
            self.app.model.user.nchantrs_account_status = status
        return self

    def update_credits(self, credits: str) -> "NchantdOfficeAccountSettings":
        """Update credits display"""
        if self.credits_status:
            self.credits_status.setPlaceholderText(str(credits))
            self.app.model.user.nchantrs_account_credits = credits
        return self

    def refresh_browser(self) -> "NchantdOfficeAccountSettings":
        """Refresh the embedded browser with appropriate URL"""
        try:
            if not self.browser:
                return self

            # Determine appropriate URL based on user status
            # DESK T-NEW-052: URLs route through the unified config
            # resolver.
            from nchantdoffice.utilities import urls as _urls

            if self.user.has_pro:
                url = _urls.whats_new_url()
            elif self.user.has_account:
                url = _urls.upgrade_compare_url()
            else:
                url = _urls.registration_url()

            # Update browser
            if hasattr(self.browser, "load_url"):
                self.browser.load_url(url)
            elif hasattr(self.browser, "setUrl"):
                self.browser.setUrl(pyqt.QUrl(url))

            logma.info(f"Browser refreshed with URL: {url}")

        except Exception as e:
            logma.error(f"Error refreshing browser: {e}")

        return self

    def get_account_data(self) -> dict:
        """Get current account data as dictionary"""
        return {
            "name": self.user_name.text() if self.user_name and self.user_name.text() else self.app.model.user.name,
            "status": self.app.model.user.nchantrs_account_status,
            "credits": self.app.model.user.nchantrs_account_credits,
            "has_pro": self.app.model.user.has_pro,
            "has_account": self.app.model.user.has_account,
            "is_paid": self.app.model.user.is_paid,
            "apikey": self.app.model.user.apikey,
        }

    def sync_with_server(self) -> bool:
        """Issue a magic-link to claim this install.

        DESK T-NEW-049: the legacy sync-with-server flow called
        ``https://api.nchantrs.com/account`` with the user's
        ``apikey`` to refresh ``status`` / ``credits`` on the
        local user object. That endpoint is going away in favour
        of the account-claim flow (the user signs in via a
        magic-link instead of pasting an API key), so the
        sync call now delegates to :class:`ClaimFlow`.

        Behaviour
        ---------
        Reads the ``install_store`` + ``entitlement_cache`` +
        ``license_remote`` from ``self.app.model`` (these are
        populated at app start -- see DESK T-NEW-046 + 047 +
        048). Constructs a :class:`ClaimFlow` and calls
        ``request_magic_link`` with the user's account email.
        Returns ``True`` if the POST landed (200), ``False`` on
        a network error.

        Returns
        -------
        bool
            ``True`` on a successful POST, ``False`` on a
            network / import error. The legacy return contract
            is preserved -- callers (e.g. ``load_account_settings``)
            treat ``False`` as "skip the live refresh".

        Why email and not apikey
        ------------------------
        The claim flow takes an email (the user types it in the
        dialog). The legacy flow took an ``apikey`` (the user
        pasted it once at install time). For backwards
        compatibility, if the user has an ``apikey`` but no
        known email, we still call ``request_magic_link`` with
        an empty string -- the server-side enumeration-safe
        contract means this is a no-op rather than an error.
        """
        try:
            # Lazy import -- ClaimFlow is re-exported at module level
            # (above), but we also re-import here so the import stays
            # lazy and doesn't break minimal test environments that
            # don't have aiohttp on the path.
            from nchantdoffice.license.claim_flow import ClaimFlow  # noqa: F401

            app_model = getattr(self.app, "model", None)
            if app_model is None:
                logma.warning("[accounts] sync_with_server: no app.model available")
                return False

            install_store = getattr(app_model, "install_store", None)
            entitlement_cache = getattr(app_model, "entitlement_cache", None)
            license_remote = getattr(app_model, "license_remote", None)
            if install_store is None or entitlement_cache is None or license_remote is None:
                logma.warning(
                    "[accounts] sync_with_server: license plumbing missing "
                    "(install_store=%r, entitlement_cache=%r, "
                    "license_remote=%r)",
                    install_store,
                    entitlement_cache,
                    license_remote,
                )
                return False

            user = getattr(app_model, "user", None)
            # Prefer the user's email (claim flow needs it); fall
            # back to an empty string if we don't have one yet
            # (server's enumeration-safe contract will swallow
            # it). Never crash the widget for this.
            email = ""
            if user is not None:
                email = getattr(user, "email", "") or getattr(user, "name", "")

            server_base_url = getattr(app_model, "server_base_url", None)
            if not server_base_url:
                # DESK T-NEW-052: resolve from the unified URL
                # config so the operator can switch between
                # production and internal docker without code edits.
                from nchantdoffice.utilities import urls

                server_base_url = urls.server_base_url()

            flow = ClaimFlow(
                install_store=install_store,
                entitlement_cache=entitlement_cache,
                license_remote=license_remote,
                server_base_url=server_base_url,
            )
            flow.sync_request_magic_link(email=email)
            return True
        except Exception as e:
            logma.error(
                f"[accounts] sync_with_server (claim flow) failed: {e}",
                exc_info=True,
            )
            return False


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
