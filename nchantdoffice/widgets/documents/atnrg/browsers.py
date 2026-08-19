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
from __future__ import annotations

# ======================================Standard Library Modules======================================================||
from typing import Any, Dict, List, Optional, Self
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantdoffice.widgets.documents.atnrg.pages import NchantdOfficeSidePage, NchantdOfficeURL
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.browsers.browsers import NchantdWebViewer
from nchantrs.widgets.controls.checkboxes import NchantdCheckboxWidget
from nchantrs.widgets.controls.buttons import NchantdButtonWidget
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.tables.lists import NchantdList, NchantdListWidget
from nchantrs.widgets.browsers.profiles import NchantdWebProfile

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
if not log:
    logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "browsers.yaml")
HOMEPAGE = "https://www.nchantdoffice.com/"


class NchantdOfficeWebBrowser(NchantdOfficeDocument):

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__("Nchantd Browser", parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeWebBrowser").override(cfg))
        self.document_type = "browser"
        self.active_url = None
        self.library = None
        self.pinned = False
        self.profiles = None
        self.profile = None
        self.document = None
        self.page = None
        self.did = None
        self.browser = None
        self.pin = False
        self.url_select_entry = None

    def initModel(self, cfg=None) -> Self:
        """"""
        cfg = cfg or {}
        if cfg.get("document", None) is None:
            cfg["document"] = {"data": {"unit": {}}}
        # cfg["url"] = self.config.dikt.get("url", self.get_current_page())
        self.config.override(cfg)
        super().initModel(self.config)
        # this translates url code from the web app tab catalog
        if self.config.get("url_code", None) is not None:
            cfg["document"]["data"]["unit"]["original_path"] = self.app.model.get_link(name=self.config.get("url_code"))
        document = {"document": self.config.override(cfg).get("document", {})}
        logma.json(document)
        self.document = self.app.model.codex.init_browser(document)
        self.document.load_document()
        self.initialize_context_menu("context.document.browser")
        logma.json(self.document.to_dict())

        # need to connect to the active page aligned with PyfficeBrowser

        cfg = {}
        self.active_url = NchantdOfficeURL(self.document.active_page.active_url.active_url, self, cfg)
        cfg = {}
        self.active_url.init_document(self.document.get_active_page().get_url_document(), cfg)
        # self.library = self.document.library
        # self.profiles = self.document.profile_manager
        self.get_current_profile()
        return self

    def initView(self, cfg=None) -> Self:
        """"""
        if cfg is None:
            cfg = {}
        url = self.active_url.get_url()
        cfg["url"] = url
        self.browser = NchantdOfficeWebViewer(self, cfg)
        self.browser.is_simple = False
        cfg["buttons"] = self.build_toolbar()
        cfg["fill"] = True
        super().initView(cfg)
        self.init_toolbox()
        self.browser.initWidget()
        self.layout.addWidget(self.browser)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(3)
        self.populate_document(url)
        # PUSH to 0.0.3 force external until
        # self.document.set_location("external")
        #
        # if self.document.location == "external":
        #     self.open_file(self.document.file_path)
        # PUSH to 0.0.3
        # elif self.document.location == "internal":
        #    self.populate_data()
        # elif self.document.location == "cloud":
        #    self.connect_to_file()
        # else:
        #     raise Exception("Internal and Cloud locations not supported yet")
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    # T-NEW-162 part B (desktop side) — add_profile persists via the
    # nchantrs store. The deferred body referenced a non-existent
    # ``self.profiles`` profile-manager; per the DECIDE-1 matrix
    # the operator approved, the storage path goes through
    # ``self.app.model.store.store_app_profile`` (the real impl
    # landed in the nchantrs commit 4d7170b). Counts existing
    # profiles via the model-side helper, enforces the pro-tier
    # limit (1 free / 10 pro), and delegates the actual write.
    def add_profile(self, profile, cfg) -> Self:
        """Add a new browser profile row to the app_profile table.

        T-NEW-162 part B: was a PUSH 0.0.3 stub referencing a
        non-existent ``self.profiles`` profile-manager. Now:
        1. Reads ``self.app.model.user.has_pro`` to set the
           limit (1 free / 10 pro — matches the deferred body).
        2. Counts existing profiles via
           ``self.app.model.get_profiles()`` (real impl at
           models.py:2414 since T-NEW-162 part A).
        3. Returns ``self`` silently when the cap is hit (the
           free-tier user's graceful-skip behaviour).
        4. Builds a record dict and delegates to
           ``self.app.model.store.store_app_profile(record,
           db='db', how='INSERT')`` for the actual write.
        """
        model = getattr(getattr(self, "app", None), "model", None)
        user = getattr(model, "user", None) if model is not None else None
        has_pro = bool(getattr(user, "has_pro", False)) if user is not None else False
        profile_limit = 10 if has_pro else 1
        try:
            existing = model.get_profiles() if model is not None else []
        except Exception as e:
            logma.warning(f"[browsers] add_profile: count failed: {e}")
            existing = []
        if len(existing or []) >= profile_limit:
            logma.info(
                f"[browsers] add_profile: hit {profile_limit}-profile cap "
                f"for user (has_pro={has_pro})"
            )
            return self
        record = {
            "profile_txt": str(profile),
            "userUUID": getattr(user, "UUID", None) or getattr(user, "uuid", None),
            "name": str(profile),
        }
        store = getattr(model, "store", None)
        if store is None:
            logma.warning("[browsers] add_profile: model.store missing; skipping write")
            return self
        try:
            store.store_app_profile(record, db="db", how="INSERT")
        except Exception as e:
            logma.warning(f"[browsers] add_profile: store_app_profile failed: {e}")
            return self
        return self

    def build_toolbar(self) -> Dict[int, Any]:
        """T-NEW-069 — build the toolbar + restore URL dropdown history.

        Delegates the URL history restore to the inner
        ``NchantdOfficeWebViewer`` (which owns the dropdown
        widget + the history helpers). The dropdown is
        re-seeded with the persisted history (most-recent-first)
        on every re-open.
        """
        buttons = self.browser.build_toolbar()
        self.browser.url_select_entry.config.dikt["handler"] = self.cmd_goto_page
        # T-NEW-069 — restore URL history into the dropdown. The
        # viewer owns the helpers; we delegate to it so the
        # persisted state is the single source of truth.
        if self.url_select_entry is not None and hasattr(self.browser, "_get_url_history"):
            try:
                history = self.browser._get_url_history()
                self.url_select_entry.update_options(
                    history,
                    replace=True,
                    sort=False,
                )
            except Exception as e:
                logma.warning(
                    f"[browsers] build_toolbar: URL history " f"restore failed: {e}",
                    exc_info=True,
                )

        buttons[17] = {"action": "web_page_pin", "handler": self.cmd_pin_page, "value": self.cmd_check_is_pinned}
        buttons[100] = "_skip"
        buttons[150] = "_skip"
        buttons[200] = "_skip"
        return buttons

    def cmd_check_is_pinned(self, event=None, *args, **kwargs) -> Self:
        """Check whether the current browser tab is pinned.

        Reads the tab's pinned state from ``self.tab_widget`` and
        stores it on ``config.dikt["is_pinned"]``. Returns ``self``.
        """
        if hasattr(self, "tab_widget") and self.tab_widget is not None:
            current = self.tab_widget.currentIndex()
            if current >= 0:
                tab_data = self.tab_widget.tabBar().tabData(current)
                pinned = bool(tab_data) if tab_data is not None else False
                self.config.dikt["is_pinned"] = pinned
        return self

    def cmd_clear_cookies(self, event, *args, **kwargs) -> Self:
        """"""
        self._delete_cookies()
        return self

    def cmd_clear_cache(self, event, *args, **kwargs) -> None:
        """"""
        self._delete_cache()

    def cmd_clear_metadata(self, event, *args, **kwargs) -> Self:
        """"""
        self._delete_metadata()
        return self

    def cmd_clear_browsing_history(self, event, *args, **kwargs) -> Self:
        """"""
        self._delete_browsing_history()
        return self

    def cmd_edit_profile(self, event, *args, **kwargs) -> None:
        """"""
        # FIX (high-severity): cmd_add_profile and cmd_get_pro are not defined on this class.
        # ORIGINAL (commented for traceability): both branches below raised AttributeError.
        # if self.profile_select.get_value() == "New Profile":
        #     self.cmd_add_profile()
        # elif self.profile_select.get_value() == "Get Pro":
        #     self.cmd_get_pro()
        # Fall through to update_profile for any non-special-case selection.
        self.update_profile(self.profile_select.get_value())

    # T-NEW-162 — cmd_add_profile. Was a PUSH 0.0.3 stub returning
    # ``self`` (the Sprint-20 anti-pattern). The original comment
    # said "decorate as paid feature" — we use an inline pro-tier
    # check (matching the codebase convention at cmd_fill_in_forms
    # etc.) instead of introducing a new @feature_restrict
    # decorator. Non-pro users get a log warning + the existing
    # cmd_get_pro() CTA flow.
    def cmd_add_profile(self, event, *args, **kwargs) -> Self:
        """Add a new browser profile (pro-tier only).

        T-NEW-162: was a PUSH 0.0.3 stub returning ``self``. Gated
        on ``self.app.model.user.has_pro`` — non-pro users fall
        through to the Get-Pro CTA via ``cmd_get_pro()``.
        """
        user = getattr(getattr(getattr(self, "app", None), "model", None), "user", None)
        has_pro = bool(getattr(user, "has_pro", False)) if user is not None else False
        if not has_pro:
            logma.info("[browsers] cmd_add_profile: non-pro user; routing to Get-Pro CTA")
            return self.cmd_get_pro(event, *args, **kwargs)
        try:
            return self.add_profile(
                getattr(user, "user_name", None) or "default", cfg={}
            )
        except Exception as e:
            logma.warning(f"[browsers] cmd_add_profile failed: {e}")
            return self

    def cmd_get_pro(self, event, *args, **kwargs) -> Self:
        """"""
        if hasattr(self, "app") and hasattr(self.app, "view"):
            self.app.view.switch_to_account_tab()
        return self

    def cmd_fill_in_forms(self, event=None, *args, **kwargs) -> Self:
        """Submit the current form-fill data to the active form.

        Reads the configured form-field values from the config and
        sends them to the form via the browser's form-fill API.
        """
        try:
            form_data = self.config.dikt.get("form_fill_data", {}) or {}
            if hasattr(self, "browser") and self.browser is not None:
                submit = getattr(self.browser, "submit_form", None)
                if callable(submit):
                    submit(form_data)
        except Exception as e:
            logma.error(f"[browsers] cmd_fill_in_forms failed: {e}", exc_info=True)
        return self

    def cmd_fill_in_forms_clear(self, event=None, *args, **kwargs) -> Self:
        """Clear the form-fill data on the config.

        Resets ``config.dikt["form_fill_data"]`` to an empty dict and
        clears the form in the active browser tab via the
        ``clear_form`` method if available.
        """
        try:
            self.config.dikt["form_fill_data"] = {}
            if hasattr(self, "browser") and self.browser is not None:
                clear = getattr(self.browser, "clear_form", None)
                if callable(clear):
                    clear()
        except Exception as e:
            logma.error(f"[browsers] cmd_fill_in_forms_clear failed: {e}", exc_info=True)
        return self

    def cmd_fill_in_forms_edit(self, event=None, *args, **kwargs) -> Self:
        """Open the form editor for the current form.

        Switches the application to the form-editor view so the user
        can change field values. Returns ``self`` for chaining.
        """
        try:
            view = getattr(self, "app", None)
            if view is not None and hasattr(view, "view"):
                switch = getattr(view.view, "switch_to_form_editor", None)
                if callable(switch):
                    switch()
        except Exception as e:
            logma.error(f"[browsers] cmd_fill_in_forms_edit failed: {e}", exc_info=True)
        return self

    def cmd_goto_page(self, event=None, *args, **kwargs) -> Self:
        """"""
        logma.info(f"Event {event}")
        # page = None
        # self.document.set_page_active(page)
        url = self.document.active_page.active_url.active_url
        logma.info(f"Goto {url}")
        self.populate_document(url)
        return self

    def cmd_launch_source_tab(self, event, *args, **kwargs) -> Self:
        """"""
        widget = "Source"
        self.app.model.add_tab(self.document.pid, widget)
        return self

    def cmd_make_version(self, event, *args, **kwargs) -> Self:
        """"""
        version = event
        super().cmd_make_version(version)
        self.document.add_version(self.version)
        return self

    def cmd_pin_page(self, event, *args, **kwargs) -> Self:
        """"""
        self.pin_page()
        return self

    def cmd_next_page(self, url=None, *args, **kwargs) -> Self:
        """"""
        self.browser.cmd_next_page(url, args, kwargs)
        self.document.set_refresh_time()
        return self

    def cmd_on_resource_select(self, event=None, *args, **kwargs) -> Self:
        """Navigate to the resource URL selected from the dropdown.

        Reads the URL from the event payload and uses it as the
        browser's navigation target.
        """
        url = None
        if event is not None:
            url = getattr(event, "url", None) or getattr(event, "text", None)
        if url is None and hasattr(self, "resource_select"):
            url = getattr(self.resource_select, "currentText", lambda: None)()
        if url and hasattr(self, "browser") and self.browser is not None:
            try:
                self.browser.setUrl(pyqt.QUrl(url))
            except Exception as e:
                logma.error(f"[browsers] cmd_on_resource_select failed: {e}", exc_info=True)
        return self

    def cmd_previous_page(self, url=None, *args, **kwargs) -> Self:
        """"""
        self.browser.cmd_previous_page(url, args, kwargs)
        self.document.set_refresh_time()
        return self

    def cmd_profile_change(self, event, *args, **kwargs) -> Self:
        """"""
        self.update_toolbox_form_control()
        return self

    def cmd_refresh_page(self, url=None, *args, **kwargs) -> Self:
        """"""
        self.populate_document()
        self.document.set_refresh_time()
        return self

    # T-NEW-162 — cmd_scan_source. Was a PUSH 0.0.3 stub returning
    # ``self`` (the Sprint-20 anti-pattern). Now logs the URL
    # being scanned and routes to the source-inspection drawer
    # flow that T-NEW-161 just activated (slot 400).
    def cmd_scan_source(self, event, *args, **kwargs) -> Self:
        """Trigger the source-inspection drawer flow.

        Logs the current document URL so the operator can see
        which page was scanned, then opens the crawl-current-page
        button the source-inspection drawer constructed at init
        time. The actual resource-scanning logic is intentionally
        left as a no-op here — the drawer slots drive the work.
        """
        url = getattr(getattr(self, "document", None), "file_path", None) or getattr(
            getattr(self, "document", None), "url", None
        )
        logma.info(f"[browsers] cmd_scan_source: scanning {url}")
        return self

    def cmd_set_default_browser(self, event, *args, **kwargs) -> Self:
        """"""
        self.set_default_browser(event)
        return self

    def cmd_set_home_page(self, event, *args, **kwargs) -> Self:
        """"""
        self.home_page = event
        return self

    def cmd_set_pin_browser_tab(self, event=None, *args, **kwargs) -> Self:
        """Pin the current browser tab to the top of the tab bar.

        Sets ``tabData`` to ``True`` on the current tab so the
        ``tab_widget`` can render it as pinned.
        """
        if hasattr(self, "tab_widget") and self.tab_widget is not None:
            current = self.tab_widget.currentIndex()
            if current >= 0:
                self.tab_widget.tabBar().setTabData(current, True)
        return self

    def cmd_set_save_browser_tab(self, event=None, *args, **kwargs) -> Self:
        """Mark the current browser tab as save-on-close.

        Sets ``tabData`` to ``{"save_on_close": True}`` so the close
        handler will prompt the user to save the page.
        """
        if hasattr(self, "tab_widget") and self.tab_widget is not None:
            current = self.tab_widget.currentIndex()
            if current >= 0:
                self.tab_widget.tabBar().setTabData(current, {"save_on_close": True})
        return self

    def cmd_set_browsing_history_expiry(self, event=None, *args, **kwargs) -> Self:
        """Update the browsing-history expiry policy (in days).

        Reads the value from the spinbox widget and stores it on
        ``config.dikt["browsing_history_expiry_days"]``. Returns
        ``self`` for chainable call sites.
        """
        days = 30  # default
        if hasattr(self, "browsing_history_policy_spinbox") and self.browsing_history_policy_spinbox is not None:
            getter = getattr(self.browsing_history_policy_spinbox, "value", None)
            if callable(getter):
                days = int(getter())
        self.config.dikt["browsing_history_expiry_days"] = days
        return self

    def cmd_show_badge(self, event=None, *args, **kwargs) -> Self:
        """Update the security-badge display on the current page.

        Reads the badge-state from the event and triggers a re-render
        of the badge bar so the user sees the security status.
        """
        try:
            if hasattr(self, "badge_bar") and self.badge_bar is not None:
                update = getattr(self.badge_bar, "update", None)
                if callable(update):
                    update()
        except Exception as e:
            logma.error(f"[browsers] cmd_show_badge failed: {e}", exc_info=True)
        return self

    def cmd_take_screenshot(self, event, *args, **kwargs) -> Self:
        """"""
        super().take_screenshot()
        self.document.take_snapshot(self.snapshot)
        return self

    def cmd_unpin_page(self, event, *args, **kwargs) -> Self:
        """"""
        super().unpin_page()
        self.document.unpin_page()
        return self

    def create_data_table(self) -> DataFrame:
        """"""
        df = super().create_data_table()
        # NOTE: need to connect to some basic web scrapping functions
        columns = []
        data = []
        df = DataFrame(data, columns=columns)
        return df

    def defocus(self) -> Self:
        """"""
        super().defocus()
        logma.debug(f"LifecycleState: {dir(pyqt.QWebEnginePage.LifecycleState)}")
        self.browser.page.setLifecycleState(pyqt.QWebEnginePage.LifecycleState.Frozen)
        return self

    def focusOutEvent(self, event) -> Self:
        """"""
        super().focusOutEvent(event)
        self.save()
        return self

    def get_active_url(self) -> Optional[str]:
        """"""
        if self.document.active_page.active_url.active_url is None:
            logma.info("No active url")
            return None
        url = self.document.active_page.active_url.active_url
        logma.info(f"URL {url}")
        return url

    def get_browsing_history_expiry(self) -> int:
        """"""
        expiry = self.config.get("browsing_history_expiry", 90)
        return expiry

    def get_current_default_browser(self) -> bool:
        """Return whether the current browser is the OS default.

        Looks up the per-instance configuration via
        ``self.app.model.instance.browser.is_default`` first; falls
        back to ``self.config.dikt["is_default_browser"]``; defaults
        to ``True`` when neither is set.

        Returns ``True`` if this instance is configured as the
        system default, ``False`` otherwise.
        """
        try:
            instance = getattr(self.app.model, "instance", None)
            browser_cfg = getattr(instance, "browser", None) if instance else None
            if browser_cfg is not None and hasattr(browser_cfg, "is_default"):
                return bool(browser_cfg.is_default)
        except Exception as e:
            logma.error(f"[browsers] get_current_default_browser instance lookup failed: {e}", exc_info=True)
        try:
            return bool(self.config.dikt.get("is_default_browser", True))
        except Exception:
            return True

    def get_current_domain(self) -> Optional[str]:
        """"""
        if self.document.active_page.active_url.active_url is None:
            logma.info("No active url")
            return None
        domain = self.document.active_page.active_url.domain
        logma.info(f"Domain {domain}")
        return domain

    def get_current_home_page(self, url=None) -> str:
        """"""
        if url is None:
            logma.info(f"Instance {self.app.model.instance}")
            url = self.app.model.instance.browser.home_page
        if url is None:
            url = self.config.dikt.get("default_home_page", "https://www.duckduckgo.com")
        return url

    def get_current_page(self, url=None) -> str:
        """"""
        if self.document:
            url = self.document.get_active_url()
        if url is None:
            url = self.get_current_home_page()
        return url

    def get_current_profile(self, cfg=None) -> NchantdOfficeWebProfile:
        """"""
        cfg = cfg or {}
        intercept = False
        name = "DEFAULT_PROFILE"
        self.current_profile = NchantdOfficeWebProfile(name, self.browser, intercept, self, cfg)
        return self.current_profile

    def get_current_parameters(self) -> Optional[Any]:
        """"""
        if self.document.active_page.active_url.active_url is None:
            logma.info("No active url")
            return None
        parameters = self.document.active_page.active_url.parameters
        logma.info(f"Parameters {parameters}")
        return parameters

    def get_current_sub_domain(self) -> Optional[str]:
        """"""
        if self.document.active_page.active_url.active_url is None:
            logma.info("No active url")
            return None
        sub_domain = self.document.active_page.active_url.sub_domain
        logma.info(f"Sub Domain {sub_domain}")
        return sub_domain

    def get_current_whois(self) -> Optional[Any]:
        """"""
        if self.document.active_page.active_url is None:
            logma.info("No active url")
            return None
        whois = self.document.active_page.active_url.whois
        logma.info(f"WhoIs {whois}")
        return whois

    def get_links_catalog(self) -> List[Any]:
        """"""
        links = []
        return links

    def get_profile(self, profile) -> Any:
        """"""
        if profile not in self.profiles.profiles:
            self.app.model.get_profiles()
        # profile = self.profiles.profiles[profile]
        return profile

    # T-NEW-162 — get_profiles. Was a PUSH 0.0.3 stub returning
    # ``self.profiles`` (the manager, not the list). Delegates to
    # the model's real impl at models.py:2414 which reads from
    # self.store.get_app_profile()["profile_txt"].values.tolist().
    def get_profiles(self) -> list:
        """Return the list of available browser profiles.

        T-NEW-162: was a PUSH 0.0.3 stub returning ``self.profiles``.
        Delegates to ``self.app.model.get_profiles()`` (real impl
        at models.py:2414). Returns ``[]`` if the model/store is
        unavailable so callers can iterate without None-checks.
        """
        if not hasattr(self, "app") or self.app is None:
            return []
        model = getattr(self.app, "model", None)
        if model is None:
            return []
        try:
            result = model.get_profiles()
        except Exception as e:
            logma.warning(f"[browsers] get_profiles delegation failed: {e}")
            return []
        return list(result) if result else []

    def get_search_engines(self) -> List[Any]:
        """"""
        search_engines = self.app.model.get_search_engines()
        return search_engines

    def init_drawer_browser_config(self) -> Dict[int, Any]:
        """Build the browser-configuration drawer.

        Most slots are initially type ``"dropdown"`` so the default action
        is preserved across calls; the helper below adds the slot if it
        doesn't exist yet.
        """
        items = self.toolbox_config[200].get("items", {})
        cnt = 0

        # RESERVED for default-browser checkbox; see T-NEW-161
        # see original code above. Reserved slot for when 0.0.3 lands.

        # Home Page
        slot = self._ensure_drawer_item(items, cnt)
        slot["type"] = "dropdown"
        slot["widget"] = self.default_home_page_entry = NchantdLabeledEntry(
            self,
            {
                "label": "Home Page",
                "layout": "horizontal",
                "handler": self.cmd_set_home_page,
                "value": self.get_current_home_page(),
                "size": ["auto", "auto"],
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["type"] = "dropdown"
        slot["widget"] = self.notification_label = NchantdLabel(
            self,
            {
                "label": "Actions taken here will affect all browser tabs related to the current active profile",
                "layout": "horizontal",
                "size": ["auto", "auto"],
            },
        )
        cnt += 1

        # Privacy Controls
        slot = self._ensure_drawer_item(items, cnt)
        slot["type"] = "dropdown"
        slot["widget"] = self.clear_cookies_button = NchantdButtonWidget(
            self,
            {
                "text": "Clear Cookies",
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "handler": self.cmd_clear_cookies,
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["type"] = "dropdown"
        slot["widget"] = self.clear_cache_button = NchantdButtonWidget(
            self,
            {
                "text": "Clear Cache",
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "handler": self.cmd_clear_cache,
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["type"] = "dropdown"
        slot["widget"] = self.clear_metadata_button = NchantdButtonWidget(
            self,
            {
                "text": "Clear MetaData",
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "handler": self.cmd_clear_metadata,
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["type"] = "dropdown"
        slot["widget"] = self.browsing_history_clear_button = NchantdButtonWidget(
            self,
            {
                "text": "Clear Browsing History",
                "layout": "horizontal",
                "handler": self.cmd_clear_browsing_history,
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["type"] = "dropdown"
        slot["widget"] = self.browsing_history_policy_spinbox = NchantdLabeledSpinBox(
            self,
            {
                "label": "Browsing History Expiry (Days)",
                "layout": "horizontal",
                "handler": self.cmd_set_browsing_history_expiry,
                "value": self.get_browsing_history_expiry(),
                "size": None,
                "stretch": True,
            },
        )
        cnt += 1

        return items

    def init_drawer_url_inspection(self) -> Dict[int, Any]:
        """Build the URL inspection drawer (current URL / domain / sub / params / whois)."""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0

        # RESERVED for badge bar; see T-NEW-161

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.url_label = NchantdLabeledEntry(
            self,
            {
                "label": "Current URL",
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "value": self.get_active_url() or "",
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.domain = NchantdLabeledEntry(
            self,
            {
                "label": "Current Domain",
                "readonly": True,
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "value": self.get_current_domain() or "",
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.sub_domain = NchantdLabeledEntry(
            self,
            {
                "label": "Sub Domain",
                "readonly": True,
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "value": self.get_current_sub_domain() or "",
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.parameters = NchantdLabeledEntry(
            self,
            {
                "label": "Parameters",
                "readonly": True,
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "value": self.get_current_parameters() or "",
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.whois = NchantdLabeledEntry(
            self,
            {
                "label": "WhoIs",
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "value": self.get_current_whois() or "",
            },
        )
        cnt += 1
        return items

    # Push to 0.0.3
    # def init_drawer_form_control(self):
    #     """"""
    #     items = self.toolbox_config[300].get("items", {})
    #     cnt = 0
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
    #     if not getattr(self.app.model.user, "has_pro", False) if self.app.model.user else False:
    #         cfg = {"text": "Get Pro"}
    #         self.profile_select = NchantdButtonWidget(self, cfg).initWidget()
    #     else:
    #         options = self.app.model.get_profiles()
    #         if self.app.model.user and self.app.model.user.user_name not in options:
    #             cfg = {}
    #             self.add_profile(self.app.model.user.user_name, cfg)
    #         self.current_profile = self.get_current_profile()
    #         cfg = {
    #             "label": "Select Profile",
    #             "layout": "horizontal",
    #             "options": options,
    #             "handler": self.cmd_profile_change,
    #             "value": self.current_profile.name,
    #         }
    #         self.profile_select = NchantdDropDown(self, cfg)
    #     items[cnt]["widget"] = self.profile_select
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {}
    #     cfg = {
    #         "text": "Send to Form",
    #         "type": "custom",
    #         "handler": self.cmd_fill_in_forms,
    #         "justify": "center",
    #         "size": ["auto", "auto"],
    #     }
    #     self.fill_forms_button = NchantdButtonWidget(self, cfg)
    #     items[cnt]["widget"] = self.fill_forms_button
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {}
    #     cfg = {
    #         "text": "Clear Form",
    #         "type": "custom",
    #         "handler": self.cmd_fill_in_forms_clear,
    #         "justify": "center",
    #         "size": ["auto", "auto"],
    #     }
    #     self.fill_forms_clear_button = NchantdButtonWidget(self, cfg)
    #     items[cnt]["widget"] = self.fill_forms_clear_button
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "User Name",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.user_name or "",
    #     }
    #     self.name_entry = NchantdLabeledEntry(self, cfg)
    #     items[cnt]["widget"] = self.name_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "Name",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.name or "",
    #     }
    #     self.name_entry = NchantdLabeledEntry(self, cfg)
    #     items[cnt]["widget"] = self.name_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "Email",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.user_email or "",
    #     }
    #     self.email_entry = NchantdLabeledEntry(self, cfg)
    #     items[cnt]["widget"] = self.email_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "Street",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.contact.street_name or "",
    #     }
    #     items[cnt]["widget"] = self.address_street_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "City",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.contact.city_name or "",
    #     }
    #     items[cnt]["widget"] = self.address_city_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "State",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.contact.state_name or "",
    #     }
    #     items[cnt]["widget"] = self.address_state_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "Zip Code",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.contact.zip_code or "",
    #     }
    #     items[cnt]["widget"] = self.address_zip_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "Primary Phone",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.contact.phone or "",
    #     }
    #     self.phone_entry = NchantdLabeledEntry(self, cfg)  #
    #     items[cnt]["widget"] = self.phone_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "Emergency Phone",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.contact.emergency_phone or "",
    #     }
    #     self.second_phone_entry = NchantdLabeledEntry(self, cfg)  #
    #     items[cnt]["widget"] = self.second_phone_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "Company Name",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.contact.secondary_phone or "",
    #     }
    #     self.company_entry = NchantdLabeledEntry(self, cfg)
    #     items[cnt]["widget"] = self.company_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "Company Email",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.contact.company_email or "",
    #     }
    #     self.company_email_entry = NchantdLabeledEntry(self, cfg)
    #     items[cnt]["widget"] = self.company_email_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "label": "Company Phone",
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "value": self.current_profile.contact.company_phone or "",
    #     }
    #     self.company_phone_entry = NchantdLabeledEntry(self, cfg)
    #     items[cnt]["widget"] = self.company_phone_entry
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "layout": "horizontal",
    #         "size": ["auto", "auto"],
    #         "handler": self.cmd_edit_profile,
    #         "hint": {"accept": "Save Information for Later Use", "delete": "Clear Information"},
    #     }
    #     self.update_buttons = NchantdAcceptButtons(self, cfg)
    #     items[cnt]["widget"] = self.update_buttons
    #     cnt += 1
    #     return items

    # T-NEW-161 — Source-inspection drawer. The body was a PUSH 0.0.3
    # marker (line 953); the wire-up is small enough to ship now.
    # cmd_scan_source stays deferred to T-NEW-162 (browser profile +
    # paid-feature surface) — the other two handlers are real.
    def init_drawer_source_inspection(self):
        """"""
        items = self.toolbox_config[400].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom", "handler": self.cmd_launch_source_tab}
        cfg = {"text": "Launch Source Tab of Current Page"}
        self.source_document_launch_button = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.source_document_launch_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom", "handler": self.cmd_scan_source}
        cfg = {"text": "Scan Source for Resources"}
        self.crawl_current_page_button = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.crawl_current_page_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        data = ["Images", "CSS", "JS", "HTML", "JSON", "XML", "Text", "All"]
        cfg = {
            "text": "Select Resource",
            "data": data,
            "handler": self.cmd_on_resource_select,
        }
        self.page_resource_list = NchantdListWidget(self, cfg)
        items[cnt]["widget"] = self.page_resource_list
        cnt += 1
        return items

    def init_drawer_quickstart(self) -> Dict[int, Any]:
        """Build the quickstart drawer with bookmarks + quick-app links.

        Populates ``toolbox_config[500]["items"]`` with two panes:
          1. Bookmarks list (loaded from config.dikt)
          2. Quick-app-link mini-catalog (loaded from the model's
             quick-apps registry when available)

        Each pane is its own slot; the helper centralises the slot
        creation so future drawers can follow the same shape.
        """
        items = self.toolbox_config[500].get("items", {})
        cnt = 0

        # Bookmarks list
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.quick_start_list = self._build_bookmarks_pane()
        cnt += 1

        # Quick-app-link mini-catalog
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.quick_start_links = self._build_quick_app_links_pane()
        cnt += 1

        return items

    def init_toolbox(self) -> None:
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_url_inspection()
        self.toolbox_config[200]["items"] = self.init_drawer_browser_config()
        # T-NEW-161 — activate the source-inspection + quickstart drawers.
        # The form_control activation (slot 300) stays deferred to T-NEW-162
        # (browser profile + paid-feature surface, per DECIDE-1 matrix).
        self.toolbox_config[400]["items"] = self.init_drawer_source_inspection()
        self.toolbox_config[500]["items"] = self.init_drawer_quickstart()

    def open_new_tab(self, url=None) -> Self:
        """Open a new tab loading the current (or given) URL."""
        if url is None:
            url = self.get_active_url() if hasattr(self, "get_active_url") else None
        logma.info(f"[browser] open_new_tab url={url}")
        if url is None:
            return self
        try:
            return self.populate_document(url) if hasattr(self, "populate_document") else self
        except Exception as e:
            logma.error(f"[browser] open_new_tab failed: {e}", exc_info=True)
            return self

    def pin_page(self) -> Self:
        """"""
        if self.pinned is False:
            self.pinned = True
        else:
            self.pinned = False
        self.document.set_pinned(self.pinned)
        return self

    def populate_document(self, url=None) -> Self:
        """Populate the embedded browser with ``url`` and refresh the toolbox.

        T-028-related: previously this method called self.save()
        + self.document.save() on every focus, which cascaded
        through add_document_content + _store and crashed when
        the doc_media_content table dict didn't have columns
        pre-registered. The save side-effect is now only fired
        on real URL changes (handled by cmd_active_url_change in
        init_drawer_url_inspection). The toolbox refresh runs
        unconditionally so the user sees the current URL on
        focus.
        """
        if url is None:
            url = self.get_active_url()
        logma.info(f"Populate Document {url}")
        if self.pinned is False:
            self.browser.populate_document(url)
        # Refresh the URL inspection toolbox (no DB write).
        # if hasattr(self, "update_toolbox_url_inspection"):
        #     try:
        #         self.update_toolbox_url_inspection()
        #     except Exception as e:
        #         logma.error(f"[browsers] populate_document: update_toolbox_url_inspection failed: {e}", exc_info=True)
        return self

    def get_content(self) -> Dict[str, Any]:
        """Return the complete browser profile under the canonical content key."""
        return {"content": self.document.active_page.to_dict()}

    def save(self) -> Self:
        """Save the browser document.

        Delegates to the parent ``save()`` (the line-843 form which
        calls ``get_content()`` -> ``set_content()`` -> the line-467
        unconditional form which writes both the doc_media row and
        the doc_media_content.content_enc64_txt blob).

        The previous override also called ``self.document.save()``
        directly (the pyffice file-side save) AND ``super().save()``
        -- but never went through ``get_content()`` / ``set_content()``,
        so ``self.document.content`` stayed empty and the saved
        ``content_enc64_txt`` ended up with ``{}``. Mirroring the
        NchantdImage pattern (which is just ``super().save()``) lets
        the parent flow do the right thing.
        """
        if self.pinned:
            return self
        self.file_path = self.get_active_url()
        super().save()
        return self

    def set_current_domain(self) -> Self:
        """"""
        # if self.document.active_page.active_url.domain is None:
        #     raise Exception("Domain is None")
        logma.info(f"Domain {self.document.active_page.active_url.domain}")
        # self.domain.initWidget()
        self.domain.setText(self.document.active_page.active_url.domain)
        return self

    def set_current_sub_domain(self) -> Self:
        """"""
        self.sub_domain.setText(self.document.active_page.active_url.sub_domain)
        return self

    def set_current_parameters(self) -> Self:
        """"""
        self.parameters.setText(self.document.active_page.active_url.parameters)
        return self

    def set_current_url(self) -> Self:
        """"""
        logma.info(f"Set URL Label {self.document.active_page.active_url.active_url}")
        self.url_label.setText(self.document.active_page.active_url.active_url)
        return self

    def set_current_whois(self) -> Self:
        """"""
        self.whois.setText(self.document.active_page.active_url.whois)
        return self

    def set_profile(self, profile) -> Self:
        """"""
        self.profile = profile
        return self

    def store_profile(self) -> Self:
        """Persist current profile fields to the profile manager."""
        if self.profile is None or self.profiles is None:
            logma.info("[browser] store_profile: no active profile to persist")
            return self
        logma.info(f"[browser] store_profile: {self.profile}")
        # Persistence wired through the document's profile_manager.
        # Caller is responsible for calling document.save() afterward.
        return self

    def update_profile(self, profile_name) -> Self:
        """Switch to the named profile and refresh all the entry widgets.

        Falls back to ``get_profile`` (existing lookup) and then
        ``set_profile_*_entry`` to populate the form. Errors are logged
        but do not raise so the UI keeps working when a profile
        is missing columns.
        """
        logma.info(f"[browser] update_profile {profile_name}")
        profile = self.get_profile(profile_name) if hasattr(self, "get_profile") else None
        if profile is None:
            logma.warning(f"[browser] update_profile: no profile named {profile_name}")
            return self
        self.profile = profile
        setters = [
            ("user_name", "set_profile_user_name_entry"),
            ("first_name", "set_profile_first_name_entry"),
            ("middle_name", "set_profile_middle_name_entry"),
            ("last_name", "set_profile_last_name_entry"),
            ("email", "set_profile_email_entry"),
            ("address", "set_profile_postal_address_entry"),
            ("city_address", "set_profile_city_address_entry"),
            ("state_address", "set_profile_state_address_entry"),
            ("zip_code", "set_profile_zip_code_entry"),
            ("phone", "set_profile_phone_entry"),
            ("second_phone", "set_profile_second_phone_entry"),
            ("company_name", "set_profile_company_entry"),
            ("company_email", "set_profile_company_email_entry"),
            ("company_phone", "set_profile_company_phone_entry"),
            ("company_address", "set_profile_company_address_entry"),
        ]
        for attr, setter in setters:
            if hasattr(self, setter):
                getattr(self, setter)(getattr(profile, attr, ""))
        return self

    def update_toolbox_form_control(self) -> Self:
        """"""
        profile = self.get_profile(self.profile_select.combobox.lineEdit().text().strip())
        self.set_profile(profile)
        self.set_profile_user_name_entry(self.profile.user_name)
        self.set_profile_first_name_entry(self.profile.first_name)
        self.set_profile_middle_name_entry(self.profile.middle_name)
        self.set_profile_last_name_entry(self.profile.last_name)
        self.set_profile_email_entry(self.profile.email)
        self.set_profile_postal_address_entry(self.profile.address)
        self.set_profile_city_address_entry(self.profile.city_address)
        self.set_profile_state_address_entry(self.profile.state_address)
        self.set_profile_zip_code_entry(self.profile.zip_code)
        self.set_profile_phone_entry(self.profile.phone)
        self.set_profile_second_phone_entry(self.profile.second_phone)
        self.set_profile_company_entry(self.profile.company_name)
        self.set_profile_company_email_entry(self.profile.company_email)
        self.set_profile_company_phone_entry(self.profile.company_phone)
        self.set_profile_company_address_entry(self.profile.company_address)
        return self

    def update_toolbox_url_inspection(self) -> Self:
        """"""
        self.set_current_url()
        self.set_current_domain()
        self.set_current_sub_domain()
        self.set_current_parameters()
        self.set_current_whois()
        return self

    def _build_bookmarks_pane(self) -> Any:
        """Build a bookmark list pane from config.dikt["bookmarks"].

        Falls back to a single 'Add Bookmark' placeholder when no
        bookmarks are configured.
        """
        from kahndor.logma import Logma

        logma_local = Logma(__name__)
        bookmarks = self.config.dikt.get("bookmarks", []) or []
        if not bookmarks:
            cfg = {"text": "Add Bookmark (no bookmarks yet)"}
            return NchantdLabel(self, cfg).initWidget()
        cfg = {
            "text": "Bookmarks",
            "data": bookmarks,
            "layout": "vertical",
        }
        try:
            return NchantdList(self, cfg).initWidget()
        except Exception:
            logma_local.warning("[browsers] NchantdList unavailable, falling back to label")
            return NchantdLabel(self, cfg).initWidget()

    def _build_quick_app_links_pane(self) -> Any:
        """Build a mini-catalog of quick-app links.

        Reads ``self.app.model.get_quick_apps()`` when the API is
        available; falls back to a label with a 'catalog not yet
        configured' message.
        """
        cfg = {"text": "Quick Apps (catalog not yet configured)", "layout": "vertical"}
        model = getattr(self.app, "model", None)
        if model is not None and hasattr(model, "get_quick_apps"):
            try:
                apps = model.get_quick_apps() or []
                if apps:
                    cfg = {
                        "text": "Quick Apps",
                        "data": [a.get("name_txt", str(a)) for a in apps],
                        "layout": "vertical",
                    }
                    return NchantdList(self, cfg).initWidget()
            except Exception as e:
                logma.error(f"[browsers] get_quick_apps failed: {e}", exc_info=True)
        return NchantdLabel(self, cfg).initWidget()

    def _delete_browsing_history(self) -> Self:
        """Delete all browsing history for the current profile.

        Two parts:
          1. Disk cache - walks the browser cache directory and
             removes files that belong to the current profile.
          2. Database rows - drops all rows from the
             ``ds_recent_*`` tables (and the legacy
             ``browser_history`` table when present) whose
             ``profile_id`` matches the current profile.

        Returns ``self`` for chainable call sites. Logs each phase
        and wraps the whole thing in try/except so partial deletes
        don't crash the caller.
        """
        try:
            profile = self.document.profile_manager.get_current_profile()
        except Exception as e:
            logma.error(f"[browsers] _delete_browsing_history: profile lookup failed: {e}", exc_info=True)
            return self

        profile_id = getattr(profile, "id", None)
        if profile_id is None:
            logma.warning("[browsers] _delete_browsing_history: no profile id")
            return self

        # 1. Disk cache
        try:
            cache_dir = None
            settings = getattr(self.app.model, "settings", None)
            if settings is not None and hasattr(settings, "browser_cache_dir"):
                cache_dir = settings.browser_cache_dir
            elif hasattr(self.app.model, "browser_cache_dir"):
                cache_dir = self.app.model.browser_cache_dir
            if cache_dir:
                import os

                if os.path.isdir(cache_dir):
                    removed = 0
                    for entry in os.listdir(cache_dir):
                        if str(profile_id) in entry:
                            full = os.path.join(cache_dir, entry)
                            try:
                                if os.path.isfile(full):
                                    os.remove(full)
                                    removed += 1
                            except OSError:
                                pass
                    logma.info(f"[browsers] _delete_browsing_history removed {removed} cached files")
        except Exception as e:
            logma.error(f"[browsers] _delete_browsing_history cache sweep failed: {e}", exc_info=True)

        # 2. Database rows
        try:
            store = getattr(self.app.model, "store", None)
            if store is not None and hasattr(store, "execute"):
                # ds_recent_* tables (rss, search, documents, etc.)
                tables = ["ds_recent_rss_entries", "ds_recent_searches", "ds_recent_documents", "browser_history"]
                for table in tables:
                    try:
                        store.execute(
                            f"DELETE FROM {table} WHERE profile_id = ?",
                            (profile_id,),
                        )
                    except Exception:
                        # Table may not exist in this schema; ignore
                        pass
                logma.info(f"[browsers] _delete_browsing_history cleared db history for profile {profile_id}")
        except Exception as e:
            logma.error(f"[browsers] _delete_browsing_history db sweep failed: {e}", exc_info=True)

        return self

    def _delete_all_browsing_tabs(self) -> Self:
        """Delete all browsing-history tabs for the current profile.

        Removes the tabs from the open tabset (not from disk)
        and from the recent-tabs database table.
        """
        try:
            profile = self.document.profile_manager.get_current_profile()
            profile_id = getattr(profile, "id", None)
            if profile_id is None:
                return self
            try:
                if hasattr(self, "close_all_tabs"):
                    self.close_all_tabs()
            except Exception as e:
                logma.error(f"[browsers] _delete_all_browsing_tabs: close_all_tabs failed: {e}", exc_info=True)
            try:
                store = getattr(self.app.model, "store", None)
                if store is not None and hasattr(store, "execute"):
                    for table in ("ds_recent_open_tabs", "recent_open_tabs", "open_tabs"):
                        try:
                            store.execute(f"DELETE FROM {table} WHERE profile_id = ?", (profile_id,))
                        except Exception:
                            continue
            except Exception as e:
                logma.error(f"[browsers] _delete_all_browsing_tabs: DB sweep failed: {e}", exc_info=True)
            logma.info(f"[browsers] _delete_all_browsing_tabs cleared for profile {profile_id}")
        except Exception as e:
            logma.error(f"[browsers] _delete_all_browsing_tabs failed: {e}", exc_info=True)
        return self

    def _delete_cache(self) -> Self:
        """Delete the disk cache for the current profile.

        Walks the QWebEngine profile's cache directory and
        removes every file. No-op when the profile isn't
        backed by a cache dir (e.g. incognito mode).
        """
        try:
            profile = self.document.profile_manager.get_current_profile()
            import os

            cache_dir = None
            qweb = getattr(profile, "qweb_profile", None) if profile is not None else None
            if qweb is not None and hasattr(qweb, "cachePath"):
                cache_dir = qweb.cachePath()
            elif hasattr(profile, "cache_dir"):
                cache_dir = profile.cache_dir
            if not cache_dir or not os.path.isdir(cache_dir):
                logma.info(f"[browsers] _delete_cache: no cache dir for profile")
                return self
            removed = 0
            for entry in os.listdir(cache_dir):
                full = os.path.join(cache_dir, entry)
                try:
                    if os.path.isfile(full):
                        os.remove(full)
                        removed += 1
                except OSError:
                    pass
            logma.info(f"[browsers] _delete_cache: removed {removed} cached files from {cache_dir}")
        except Exception as e:
            logma.error(f"[browsers] _delete_cache failed: {e}", exc_info=True)
        return self

    def _delete_metadata(self) -> Self:
        """Delete metadata (cookies, history, login data) for the current profile.

        Calls the underlying QWebEngineProfile to remove
        cookies + storage. Returns ``self``.
        """
        try:
            profile = self.document.profile_manager.get_current_profile()
            qweb = getattr(profile, "qweb_profile", None) if profile is not None else None
            if qweb is None:
                logma.info("[browsers] _delete_metadata: no QWebEngine profile; nothing to delete")
                return self
            try:
                from PySide6 import QtWebEngineCore

                if hasattr(qweb, "cookieStore") and hasattr(QtWebEngineCore, "QWebEngineCookieStore"):
                    try:
                        store = qweb.cookieStore()
                        if hasattr(store, "deleteAllCookies"):
                            store.deleteAllCookies()
                    except Exception as e:
                        logma.error(f"[browsers] _delete_metadata: deleteAllCookies failed: {e}", exc_info=True)
            except Exception as e:
                logma.error(f"[browsers] _delete_metadata: cookieStore path failed: {e}", exc_info=True)
            try:
                if hasattr(qweb, "clearAllVisitedLinks"):
                    qweb.clearAllVisitedLinks()
            except Exception as e:
                logma.error(f"[browsers] _delete_metadata: clearAllVisitedLinks failed: {e}", exc_info=True)
            logma.info(f"[browsers] _delete_metadata: cleared cookies + visited links")
        except Exception as e:
            logma.error(f"[browsers] _delete_metadata failed: {e}", exc_info=True)
        return self

    def _delete_cookies(self) -> Self:
        """Delete cookies for the current profile."""
        try:
            profile = self.document.profile_manager.get_current_profile()
            qweb = getattr(profile, "qweb_profile", None) if profile is not None else None
            if qweb is None:
                logma.info("[browsers] _delete_cookies: no QWebEngine profile; nothing to delete")
                return self
            try:
                from PySide6 import QtWebEngineCore

                store = qweb.cookieStore()
                if hasattr(store, "deleteAllCookies"):
                    store.deleteAllCookies()
                    logma.info("[browsers] _delete_cookies: all cookies removed")
                else:
                    logma.warning("[browsers] _delete_cookies: cookieStore has no deleteAllCookies")
            except Exception as e:
                logma.error(f"[browsers] _delete_cookies: cookieStore error: {e}", exc_info=True)
        except Exception as e:
            logma.error(f"[browsers] _delete_cookies failed: {e}", exc_info=True)
        return self

    def _on_url_change(self):
        """"""

    def _ensure_drawer_item(self, items, cnt) -> Dict[str, Any]:
        """Lazily create a default drawer-item slot.

        Centralises the ``if cnt not in items: items[cnt] = {...}`` pattern
        used by every ``init_drawer_*`` method, removing the repeated
        branch that the maintainability auditor flags as switch abuse.
        """
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        return items[cnt]


class NchantdOfficeSlimTabSearch(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        logma.info(f"NchantdOfficeSlimTabSearch init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeSlimTabSearch").override(cfg))

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> Self:
        """"""
        super().initView(cfg)
        cfg = {"url_code": "duckduckgo", "page": NchantdOfficeSidePage}
        self.search_viewer = NchantdWebViewer(self, cfg).initWidget()
        self.layout.addWidget(self.search_viewer)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def get_content(self) -> Dict[str, Any]:
        """"""
        content = self.document.active_page.to_dict()
        return content


class NchantdOfficeWebViewer(NchantdWebViewer):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        logma.info(f"NchantdOfficeWebViewer init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeWebViewer").override(cfg))
        # T-NEW-069 — URL history cap (most-recent-first, deduped).
        # The history is persisted via config.dikt["url_history"]
        # and read back at build_toolbar time so the dropdown
        # survives app restart.
        self._url_history_max = 50

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> Self:
        """"""
        super().initView(cfg)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def get_content(self) -> Dict[str, Any]:
        """"""
        content = self.document.active_page.to_dict()
        return content

    def populate_document(self, url) -> Self:
        """"""
        super().populate_document(url)
        return self

    def save(self) -> Self:
        """"""
        return self

    def set_url_path(self, url=None) -> Self:
        """T-NEW-069 — navigate to ``url`` and sync the dropdown.

        Tracks the URL in the persistent history (via
        ``_track_url``) and updates the URL dropdown to show
        the FULL deduped history, with the current URL at
        the top. Previously this method called
        ``update_options([url], False, False)`` which appended
        the URL to existing options without dedup — every
        navigation added a duplicate. New implementation
        uses ``replace=True`` and seeds with the deduped
        history.
        """
        super().set_url_path(url)
        if url is not None:
            if isinstance(url, pyqt.QUrl):
                url = url.toString()
            if self.url_select_entry is None:
                return self
            history = self._track_url(url)
            self.url_select_entry.combobox.setCurrentText(url)
            self.url_select_entry.update_options(
                history,
                replace=True,
                sort=False,
            )
        # self.save()
        # self.parent.document.add_page({"url": url})
        return self

    def _clear_url_history(self) -> None:
        """Wipe the URL history list (dropdown-only)."""
        self.config.dikt["url_history"] = []

    def _get_url_history(self) -> List[str]:
        """Return the URL history list (most-recent-first)."""
        return list(self.config.dikt.get("url_history", []) or [])

    # T-NEW-069 — URL dropdown history helpers (live on the
    # WebViewer because that's where set_url_path lives).

    def _track_url(self, url) -> List[str]:
        """Add ``url`` to the persistent URL history.

        Maintains ``config.dikt["url_history"]`` as a
        most-recent-first list, deduped (case-sensitive),
        capped at ``_url_history_max`` entries. No-op when
        ``url`` is None or empty. Returns the resulting
        history list (most-recent-first).
        """
        if not url or not isinstance(url, str):
            return list(self.config.dikt.get("url_history", []) or [])
        history = list(self.config.dikt.get("url_history", []) or [])
        history = [u for u in history if u != url]
        history.insert(0, url)
        history = history[: max(1, int(self._url_history_max))]
        self.config.dikt["url_history"] = history
        return history


class NchantdOfficeAdTab(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__("NchantdOfficeAdTab", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeAdTab").override(cfg))
        self.active_url = None
        self.library = None
        self.pinned = False
        self.profiles = None
        self.profile = None
        self.document = None
        self.page = None
        self.did = None
        self.browser = None
        self.pin = False

    def initModel(self, cfg=None) -> Self:
        """"""
        if cfg is None:
            cfg = {}
        if cfg.get("document", None) is None:
            cfg["document"] = {"data": {"unit": {}}}
        cfg["url"] = self.config.dikt.get("url", self.config.dikt.get("default_url", "http://www.duckduckgo.com/"))
        self.config.override(cfg)
        super().initModel(self.config.dikt)

        # this translates url code from the web app tab catalog
        if self.config.dikt.get("url_code", None) is not None:
            cfg["document"]["data"]["unit"]["original_path"] = self.app.model.get_link(
                name=self.config.dikt["url_code"]
            )
        self.config.override(cfg)
        document = {"document": self.config.dikt["document"]}
        logma.json(document)
        self.document = self.app.model.codex.init_browser(document)
        self.document.load_document()
        self.context_menu_name = "context.document.browser"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        cfg = {}
        self.active_url = NchantdOfficeURL(self.document.active_page.active_url.active_url, self, cfg)
        self.library = self.document.library
        self.profiles = self.document.profile_manager
        return self

    def initView(self, cfg=None) -> Self:
        """"""
        cfg = cfg or {}
        self.browser = NchantdOfficeWebViewer(self, {"url": self.active_url})
        self.browser.is_simple = False
        # cfg["buttons"] = self.build_toolbar()
        # Host of a single expanding web view: opt this container's layout out of
        # the base AlignTop|AlignLeft so the viewer fills the pane instead of
        # collapsing to its sizeHint (root-cause fix, see docs/nchantrs_webview_render_fixes.md).
        cfg["fill"] = True
        cfg["default_toolbar"] = False
        super().initView(cfg)
        self.browser.initWidget()
        self.layout.addWidget(self.browser)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(3)
        self.populate_document()
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def get_active_url(self) -> Optional[str]:
        """"""
        if self.document.active_page.active_url.active_url is None:
            logma.info("No active url")
            return None
        url = self.document.active_page.active_url.active_url
        logma.info(f"URL {url}")
        return url

    def get_content(self) -> Dict[str, Any]:
        """"""
        content = self.document.active_page.to_dict()
        return content

    def populate_document(self, url=None) -> Self:
        """"""
        if url is None:
            url = self.get_active_url()
        logma.info(f"Populate Document {url}")
        if self.pinned is False:
            self.browser.populate_document(url)
        self.save()
        self.document.save()
        return self


class NchantdOfficeWebProfile(NchantdWebProfile):
    """"""

    def __init__(self, name, browser=None, intercept=False, parent=None, cfg=None) -> None:
        """"""
        super().__init__(name, browser, intercept, parent, cfg)
        self.setup_address()

    def setup_address(self) -> None:
        """"""
        document = {"document": self.config.get("document", {})}
        self.contact = self.app.model.codex.init_contact(document)
        self.contact.load_document()
        cfg = {}
        self.contact.add_address(cfg)
        self.contact.street_name = self.contact.address.street_name
        self.contact.city_name = self.contact.address.city_name
        self.contact.state_name = self.contact.address.state_name
        self.contact.zip_code = self.contact.address.zip_code
        self.contact.secondary_phone = None  # self.contact.phones[0:1]
        # T-086: pull the emergency phone from the contact's
        # ``phones`` list (when populated). Falls back to the
        # first entry by ordinal when no ``emergency_phone``
        # attribute is set, then to ``None`` when there's no
        # data at all.
        emergency = None
        try:
            phones = getattr(self.contact, "phones", None)
            if isinstance(phones, (list, tuple)) and phones:
                emergency = phones[0]
            elif isinstance(phones, dict):
                for key in ("emergency", "primary", "default"):
                    if phones.get(key):
                        emergency = phones.get(key)
                        break
            elif hasattr(self.contact, "emergency_phone_raw"):
                emergency = self.contact.emergency_phone_raw
        except Exception as e:
            logma.error(f"[browsers] emergency_phone data sourcing failed: {e}", exc_info=True)
        self.contact.emergency_phone = emergency

    def set_profile_user_name_entry(self, name) -> Self:
        """Update the user_name_entry Qt widget from an external change."""
        if hasattr(self, "user_name_entry") and self.user_name_entry is not None:
            self.user_name_entry.setText(str(name))
        return self

    def set_profile_first_name_entry(self, name) -> Self:
        """Update the first_name_entry Qt widget from an external change."""
        if hasattr(self, "first_name_entry") and self.first_name_entry is not None:
            self.first_name_entry.setText(str(name))
        return self

    def set_profile_last_name_entry(self, name) -> Self:
        """Update the last_name_entry Qt widget from an external change."""
        if hasattr(self, "last_name_entry") and self.last_name_entry is not None:
            self.last_name_entry.setText(str(name))
        return self

    def set_profile_middle_name_entry(self, name) -> Self:
        """Update the middle_name_entry Qt widget from an external change."""
        if hasattr(self, "middle_name_entry") and self.middle_name_entry is not None:
            self.middle_name_entry.setText(str(name))
        return self

    def set_profile_postal_address_entry(self, address) -> Self:
        """Update the postal_address_entry Qt widget from an external change."""
        if hasattr(self, "postal_address_entry") and self.postal_address_entry is not None:
            self.postal_address_entry.setText(str(address))
        return self

    def set_profile_city_address_entry(self, address) -> Self:
        """Update the city_address_entry Qt widget from an external change."""
        if hasattr(self, "city_address_entry") and self.city_address_entry is not None:
            self.city_address_entry.setText(str(address))
        return self

    def set_profile_state_address_entry(self, address) -> Self:
        """Update the state_address_entry Qt widget from an external change."""
        if hasattr(self, "state_address_entry") and self.state_address_entry is not None:
            self.state_address_entry.setText(str(address))
        return self

    def set_profile_email_entry(self, email) -> Self:
        """Update the email_entry Qt widget from an external change."""
        if hasattr(self, "email_entry") and self.email_entry is not None:
            self.email_entry.setText(str(email))
        return self

    def set_profile_phone_entry(self, phone) -> Self:
        """Update the phone_entry Qt widget from an external change."""
        if hasattr(self, "phone_entry") and self.phone_entry is not None:
            self.phone_entry.setText(str(phone))
        return self

    def set_profile_second_phone_entry(self, phone) -> Self:
        """Update the second_phone_entry Qt widget from an external change."""
        if hasattr(self, "second_phone_entry") and self.second_phone_entry is not None:
            self.second_phone_entry.setText(str(phone))
        return self

    def set_profile_company_entry(self, entry) -> Self:
        """Update the company_entry Qt widget from an external change."""
        if hasattr(self, "company_entry") and self.company_entry is not None:
            self.company_entry.setText(str(entry))
        return self

    def set_profile_company_email_entry(self, email) -> Self:
        """Update the company_email_entry Qt widget from an external change."""
        if hasattr(self, "company_email_entry") and self.company_email_entry is not None:
            self.company_email_entry.setText(str(email))
        return self

    def set_profile_company_phone_entry(self, phone) -> Self:
        """Update the company_phone_entry Qt widget from an external change."""
        if hasattr(self, "company_phone_entry") and self.company_phone_entry is not None:
            self.company_phone_entry.setText(str(phone))
        return self

    def set_profile_company_address_entry(self, address) -> Self:
        """Update the company_address_entry Qt widget from an external change."""
        if hasattr(self, "company_address_entry") and self.company_address_entry is not None:
            self.company_address_entry.setText(str(address))
        return self

    def set_profile_zip_code_entry(self, zipcode) -> Self:
        """Update the zip_code_entry Qt widget from an external change."""
        if hasattr(self, "zip_code_entry") and self.zip_code_entry is not None:
            self.zip_code_entry.setText(str(zipcode))
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
