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

    def initModel(self) -> "NchantdOfficeAccountSettings":
        """ """
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
            "size": [1600, 750],
            "is_simple": True,
        }
        if self.user is None:
            raise Exception("No User configured")
        # DESK T-NEW-140 v6: route through the SERVER, which owns the
        # session state. /user-account/home renders the dashboard when
        # the embedded browser's session cookie is valid and 302s to
        # /auth/login?next=/user-account/home when it is not. The
        # login page links to registration for brand-new users. This
        # replaces v1-v5 desktop-side cookie introspection — the
        # QtWebEngine cookie store has no public synchronous read API,
        # and the signal-based snapshot never reliably captured the
        # session cookie before the tab reactivated.
        #
        # Pro users keep whats_new (deliberate changelog view, no
        # upsell); every other tier lands on the server router.
        if self.user.has_pro:
            cfg["url"] = _urls.whats_new_url()
        else:
            cfg["url"] = _urls.user_account_url()
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
        # DESK T-NEW-140 v6: no client-side URL guard. The browser
        # navigates to /user-account/home, and the server decides
        # what the user sees (dashboard or login redirect) based on
        # the embedded browser's session cookie. The v3-v5 cookie
        # signal/snapshot logic was dropped — QtWebEngineCookieStore
        # has no public synchronous read API, the cookieAdded signal
        # never reliably fired before tab reactivation, and the server
        # route already does the right thing.
        return self

    def initWidget(self) -> "NchantdOfficeAccountSettings":
        """ """
        self.initModel()
        self.initView()
        return self

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
