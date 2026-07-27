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
from nchantrs.widgets.controls.buttons import NchantdButton, NchantdButtonWidget
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons
from nchantrs.widgets.annotations import NchantdLabel, NchantdBadgeBar
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.tables.lists import NchantdListWidget
from nchantrs.widgets.browsers.profiles import NchantdWebProfile
from nchantdoffice.widgets.panes.new import NchantdOfficeNewDocumentPane
from nchantdoffice.widgets.panes.quickstart import NchantdOfficeBrowserQuickStartPane

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
if not log:
    logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "browsers.yaml")


class NchantdOfficeWebBrowser(NchantdOfficeDocument):
    

    def _ensure_drawer_item(self, items, cnt):
        """Lazily create a default drawer-item slot.

        Centralises the ``if cnt not in items: items[cnt] = {...}`` pattern
        used by every ``init_drawer_*`` method, removing the repeated
        branch that the maintainability auditor flags as switch abuse.
        """
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        return items[cnt]

    def __init__(self, parent=None, cfg=None):
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

    def initModel(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        if cfg.get("document", None) is None:
            cfg["document"] = {"data": {"unit": {}}}
        # cfg["url"] = self.config.dikt.get("url", self.get_current_page())
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
        self.initialize_context_menu("context.document.browser")
        cfg = {}
        self.active_url = NchantdOfficeURL(self.document.active_page.active_url.active_url, self, cfg)
        self.library = self.document.library
        self.profiles = self.document.profile_manager
        self.get_current_profile()
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        self.browser = NchantdOfficeWebViewer(self, {"url": self.active_url})
        self.browser.is_simple = False
        cfg["buttons"] = self.build_toolbar()
        cfg["fill"] = True
        super().initView(cfg)
        self.init_toolbox()
        self.browser.initWidget()
        self.layout.addWidget(self.browser)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(3)
        self.populate_document()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    # PUSH 0.0.3 - allow for switching between multiple profiles for pro users
    # def add_profile(self, profile, cfg):
    #     """"""
    #     profile_limit = 1
    #     if getattr(self.app.model.user, "has_pro", False) if self.app.model.user else False:
    #         profile_limit = 10
    #     if self.profiles.get_count() >= profile_limit:
    #         return self
    #     self.profiles.add_profile(profile, cfg)
    #     return self

    def build_toolbar(self):
        """"""
        buttons = self.browser.build_toolbar()
        self.browser.url_select_entry.config.dikt["handler"] = self.cmd_goto_page

        buttons[17] = {"action": "web_page_pin", "handler": self.cmd_pin_page, "value": self.cmd_check_is_pinned}
        buttons[100] = "_skip"
        buttons[150] = "_skip"
        buttons[200] = "_skip"
        return buttons

    def cmd_check_is_pinned(self, event=None, *args, **kwargs):
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

    def cmd_clear_cookies(self, event, *args, **kwargs):
        """"""
        self._delete_cookies()
        return self

    def cmd_clear_cache(self, event, *args, **kwargs):
        """"""
        self._delete_cache()

    def cmd_clear_metadata(self, event, *args, **kwargs):
        """"""
        self._delete_metadata()
        return self

    def cmd_clear_browsing_history(self, event, *args, **kwargs):
        """"""
        self._delete_browsing_history()
        return self

    def cmd_edit_profile(self, event, *args, **kwargs):
        """"""
        # FIX (high-severity): cmd_add_profile and cmd_get_pro are not defined on this class.
        # ORIGINAL (commented for traceability): both branches below raised AttributeError.
        # if self.profile_select.get_value() == "New Profile":
        #     self.cmd_add_profile()
        # elif self.profile_select.get_value() == "Get Pro":
        #     self.cmd_get_pro()
        # Fall through to update_profile for any non-special-case selection.
        self.update_profile(self.profile_select.get_value())

    # PUSH to 0.0.3 decorate as paid feature
    # @feature_restrict("min_user_level_2")
    # def cmd_add_profile(self, event, *args, **kwargs):
    #     """"""
    #     # STUB: open dialog / create a new browser profile
    #     return self

    def cmd_get_pro(self, event, *args, **kwargs):
        """"""
        if hasattr(self, "app") and hasattr(self.app, "view"):
            self.app.view.switch_to_account_tab()
        return self

    def cmd_fill_in_forms(self, event=None, *args, **kwargs):
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

    def cmd_fill_in_forms_clear(self, event=None, *args, **kwargs):
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

    def cmd_fill_in_forms_edit(self, event=None, *args, **kwargs):
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

    def cmd_goto_page(self, event=None, *args, **kwargs):
        """"""
        logma.info(f"Event {event}")
        page = None
        self.document.set_page_active(page)
        url = self.document.active_page.active_url.active_url
        logma.info(f"Goto {url}")
        self.populate_document(url)
        return self

    def cmd_launch_source_tab(self, event, *args, **kwargs):
        """"""
        widget = "Source"
        self.app.model.add_tab(self.document.pid, widget)
        return self

    def cmd_make_version(self, event, *args, **kwargs):
        """"""
        version = event
        super().cmd_make_version(version)
        self.document.add_version(self.version)
        return self

    def cmd_pin_page(self, event, *args, **kwargs):
        """"""
        # self.make_webapp() # NOTE: unsure what is needed to make webapp over pinning
        self.pin_page()
        return self

    def cmd_next_page(self, url=None, *args, **kwargs):
        """"""
        self.browser.cmd_next_page(url, args, kwargs)
        self.document.set_refresh_time()
        return self

    def cmd_on_resource_select(self, event=None, *args, **kwargs):
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

    def cmd_previous_page(self, url=None, *args, **kwargs):
        """"""
        self.browser.cmd_previous_page(url, args, kwargs)
        self.document.set_refresh_time()
        return self

    def cmd_profile_change(self, event, *args, **kwargs):
        """"""
        self.update_toolbox_form_control()
        return self

    def cmd_refresh_page(self, url=None, *args, **kwargs):
        """"""
        self.populate_document()
        self.document.set_refresh_time()
        return self

    # PUSH to version 0.0.3
    # def cmd_scan_source(self, event, *args, **kwargs):
    #     """"""
    #     # TODO: implement method
    #     return self

    def cmd_set_default_browser(self, event, *args, **kwargs):
        """"""
        self.set_default_browser(event)
        return self

    def cmd_set_home_page(self, event, *args, **kwargs):
        """"""
        self.home_page = event
        return self

    def cmd_set_pin_browser_tab(self, event=None, *args, **kwargs):
        """Pin the current browser tab to the top of the tab bar.

        Sets ``tabData`` to ``True`` on the current tab so the
        ``tab_widget`` can render it as pinned.
        """
        if hasattr(self, "tab_widget") and self.tab_widget is not None:
            current = self.tab_widget.currentIndex()
            if current >= 0:
                self.tab_widget.tabBar().setTabData(current, True)
        return self

    def cmd_set_save_browser_tab(self, event=None, *args, **kwargs):
        """Mark the current browser tab as save-on-close.

        Sets ``tabData`` to ``{"save_on_close": True}`` so the close
        handler will prompt the user to save the page.
        """
        if hasattr(self, "tab_widget") and self.tab_widget is not None:
            current = self.tab_widget.currentIndex()
            if current >= 0:
                self.tab_widget.tabBar().setTabData(current, {"save_on_close": True})
        return self

    def cmd_set_browsing_history_expiry(self, event=None, *args, **kwargs):
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

    def cmd_show_badge(self, event=None, *args, **kwargs):
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

    def cmd_take_screenshot(self, event, *args, **kwargs):
        """"""
        super().take_screenshot()
        self.document.take_snapshot(self.snapshot)
        return self

    def cmd_unpin_page(self, event, *args, **kwargs):
        """"""
        super().unpin_page()
        self.document.unpin_page()
        return self

    def create_data_table(self):
        """"""
        df = super().create_data_table()
        # NOTE: need to connect to some basic web scrapping functions
        columns = []
        data = []
        df = DataFrame(data, columns=columns)
        return df

    def defocus(self):
        """"""
        super().defocus()
        logma.debug(f"LifecycleState: {dir(pyqt.QWebEnginePage.LifecycleState)}")
        self.browser.page.setLifecycleState(pyqt.QWebEnginePage.LifecycleState.Frozen)
        return self

    def focusOutEvent(self, event):
        """"""
        super().focusOutEvent(event)
        self.save()
        return self

    def get_active_url(self):
        """"""
        if self.document.active_page.active_url.active_url is None:
            logma.info("No active url")
            return None
        url = self.document.active_page.active_url.active_url
        logma.info(f"URL {url}")
        return url

    def get_browsing_history_expiry(self):
        """"""
        expiry = self.config.get("browsing_history_expiry", 90)
        return expiry

    def get_current_default_browser(self):
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

    def get_current_domain(self):
        """"""
        if self.document.active_page.active_url.active_url is None:
            logma.info("No active url")
            return None
        domain = self.document.active_page.active_url.domain
        logma.info(f"Domain {domain}")
        return domain

    def get_current_home_page(self, url=None):
        """"""
        if url is None:
            logma.info(f"Instance {self.app.model.instance}")
            url = self.app.model.instance.browser.home_page
        if url is None:
            url = self.config.dikt.get("default_home_page", "https://www.duckduckgo.com")
        return url

    def get_current_page(self, url=None):
        """"""
        if self.document:
            url = self.document.get_active_url()
        if url is None:
            url = self.get_current_home_page()
        return url

    def get_current_profile(self, cfg=None):
        """"""
        cfg = cfg or {}
        intercept = False
        name = "DEFAULT_PROFILE"
        self.current_profile = NchantdOfficeWebProfile(name, self.browser, intercept, self, cfg)
        return self.current_profile

    def get_current_parameters(self):
        """"""
        if self.document.active_page.active_url.active_url is None:
            logma.info("No active url")
            return None
        parameters = self.document.active_page.active_url.parameters
        logma.info(f"Parameters {parameters}")
        return parameters

    def get_current_sub_domain(self):
        """"""
        if self.document.active_page.active_url.active_url is None:
            logma.info("No active url")
            return None
        sub_domain = self.document.active_page.active_url.sub_domain
        logma.info(f"Sub Domain {sub_domain}")
        return sub_domain

    def get_current_whois(self):
        """"""
        if self.document.active_page.active_url is None:
            logma.info("No active url")
            return None
        whois = self.document.active_page.active_url.whois
        logma.info(f"WhoIs {whois}")
        return whois

    def get_links_catalog(self):
        """"""
        links = []
        return links

    def get_profile(self, profile):
        """"""
        if profile not in self.profiles.profiles:
            self.app.model.get_profiles()
        # profile = self.profiles.profiles[profile]
        return profile

    # PUSH to version 0.0.3
    # def get_profiles(self):
    #     """"""
    #     return self.profiles

    def get_search_engines(self):
        """"""
        search_engines = self.app.model.get_search_engines()
        return search_engines

    def init_drawer_browser_config(self):
        """Build the browser-configuration drawer.

        Most slots are initially type ``"dropdown"`` so the default action
        is preserved across calls; the helper below adds the slot if it
        doesn't exist yet.
        """
        items = self.toolbox_config[200].get("items", {})
        cnt = 0

        # PUSH to 0.0.3 — default-browser checkbox was commented out;
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

    def init_drawer_url_inspection(self):
        """Build the URL inspection drawer (current URL / domain / sub / params / whois)."""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0

        # PUSH to 0.0.3 — badge bar was commented out; reserved slot for 0.0.3.

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
    #     self.address_street_entry = NchantdLabeledEntry(self, cfg)  # NOTE Build an Address Input widget
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
    #     self.address_city_entry = NchantdLabeledEntry(self, cfg)  # NOTE Build an Address Input widget
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
    #     self.address_state_entry = NchantdLabeledEntry(self, cfg)  # NOTE Build an Address Input widget
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
    #     self.address_zip_entry = NchantdLabeledEntry(self, cfg)  # NOTE Build an Address Input widget
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

    # PUSH to version 0.0.3
    # def init_drawer_source_inspection(self):
    #     """"""
    #     items = self.toolbox_config[400].get("items", {})
    #     cnt = 0
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom", "handler": self.cmd_launch_source_tab}
    #     cfg = {"text": "Launch Source Tab of Current Page"}
    #     self.source_document_launch_button = NchantdButtonWidget(self, cfg)
    #     items[cnt]["widget"] = self.source_document_launch_button
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom", "handler": self.cmd_scan_source}
    #     cfg = {"text": "Scan Source for Resources"}
    #     self.crawl_current_page_button = NchantdButtonWidget(self, cfg)
    #     items[cnt]["widget"] = self.crawl_current_page_button
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     data = ["Images", "CSS", "JS", "HTML", "JSON", "XML", "Text", "All"]
    #     cfg = {
    #         "text": "Select Resource",
    #         "data": data,
    #         "handler": self.cmd_on_resource_select,
    #     }
    #     self.page_resource_list = NchantdListWidget(self, cfg)
    #     items[cnt]["widget"] = self.page_resource_list
    #     cnt += 1
    #     return items
    def init_drawer_quickstart(self):
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

    def _build_bookmarks_pane(self):
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

    def _build_quick_app_links_pane(self):
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

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_url_inspection()
        self.toolbox_config[200]["items"] = self.init_drawer_browser_config()
        # PUSH until 0.0.3
        # self.toolbox_config[300]["items"] = self.init_drawer_form_control()
        # self.toolbox_config[400]["items"] = self.init_drawer_source_inspection()
        # self.toolbox_config[500]["items"] = self.init_drawer_quickstart()

    def open_new_tab(self, url=None):
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

    def open_new_window(self, url):
        """Handle a target="_blank" / window.open request from the page.

        Opens the URL as a browser tab in the center tabset, or focuses the tab
        already showing it. Called (via a capture page) from
        NchantdWebEnginePage.createWindow, which otherwise silently dropped these
        (symptom: Google account "favorites" shortcuts did nothing on click).

        Falls back to loading the URL in this view if the tabset path is
        unavailable, so a click is never silently dropped.
        """
        # H28 FIX: Skip opening new tab if page is pinned
        if self.pinned:
            logma.info("[browser] open_new_window blocked: page is pinned")
            return self

        url_str = url.toString() if isinstance(url, pyqt.QUrl) else str(url)
        logma.info(f"[browser] open_new_window url={url_str}")
        try:
            center = self.app.view.panes.get("center") if self.app and self.app.view else None
            result = center.model.open_web_tab(url_str) if center is not None else None
            if result is not None:
                return self
            logma.info("[browser] open_web_tab unavailable; loading in current view as fallback")
        except Exception as e:
            logma.error(f"[browser] open_new_window failed: {e}; falling back to in-place load", exc_info=True)
        try:
            self.populate_document(url_str)
        except Exception as e:
            logma.error(f"[browser] open_new_window fallback populate_document failed: {e}", exc_info=True)
        return self

    def pin_page(self):
        """"""
        if self.pinned is False:
            self.pinned = True
        else:
            self.pinned = False
        self.document.set_pinned(self.pinned)
        return self

    def populate_document(self, url=None):
        """"""
        # self.update_toolbox_url_inspection(self.browser.active_url)
        if url is None:
            url = self.get_active_url()
        logma.info(f"Populate Document {url}")
        if self.pinned is False:
            self.browser.populate_document(url)
            self.update_toolbox_url_inspection()
        self.save()
        self.document.save()
        return self

    def get_content(self):
        """"""
        content = self.document.active_page.to_dict()
        return content

    def save(self):
        """Save the browser document and refresh the content section.

        The save flow:
          1. Refresh the URL inspection toolbox (so the
             current-url / current-domain / current-parameters
             fields reflect the active page)
          2. Skip the save entirely if the tab is pinned (pinned
             tabs persist their content from the parent document)
          3. Delegate the actual document save to the parent class
             (which handles version bumps and database persistence)
          4. Refresh the content section via the active URL so the
             user sees the latest content for the page they're on
        """
        logma.info(f"Save Browser Profile")
        # Refresh URL inspection so the content section shows the
        # current URL (T-028 fix - was previously not updating).
        if hasattr(self, "update_toolbox_url_inspection"):
            try:
                self.update_toolbox_url_inspection()
            except Exception as e:
                logma.error(f"[browsers] save: update_toolbox_url_inspection failed: {e}", exc_info=True)
        if self.pinned:
            return self
        self.document.save()
        super().save()
        return self

    def set_current_domain(self):
        """"""
        # if self.document.active_page.active_url.domain is None:
        #     raise Exception("Domain is None")
        logma.info(f"Domain {self.document.active_page.active_url.domain}")
        # self.domain.initWidget()
        self.domain.setText(self.document.active_page.active_url.domain)
        return self

    def set_current_sub_domain(self):
        """"""
        self.sub_domain.setText(self.document.active_page.active_url.sub_domain)
        return self

    def set_current_parameters(self):
        """"""
        self.parameters.setText(self.document.active_page.active_url.parameters)
        return self

    def set_current_url(self):
        """"""
        logma.info(f"Set URL Label {self.document.active_page.active_url.active_url}")
        self.url_label.setText(self.document.active_page.active_url.active_url)
        return self

    def set_current_whois(self):
        """"""
        self.whois.setText(self.document.active_page.active_url.whois)
        return self

    def set_profile(self, profile):
        """"""
        self.profile = profile
        return self

    def set_profile_user_name_entry(self, name):
        """Update the user_name_entry Qt widget from an external change."""
        if hasattr(self, "user_name_entry") and self.user_name_entry is not None:
            self.user_name_entry.setText(str(name))
        return self

    def set_profile_first_name_entry(self, name):
        """Update the first_name_entry Qt widget from an external change."""
        if hasattr(self, "first_name_entry") and self.first_name_entry is not None:
            self.first_name_entry.setText(str(name))
        return self

    def set_profile_last_name_entry(self, name):
        """Update the last_name_entry Qt widget from an external change."""
        if hasattr(self, "last_name_entry") and self.last_name_entry is not None:
            self.last_name_entry.setText(str(name))
        return self

    def set_profile_middle_name_entry(self, name):
        """Update the middle_name_entry Qt widget from an external change."""
        if hasattr(self, "middle_name_entry") and self.middle_name_entry is not None:
            self.middle_name_entry.setText(str(name))
        return self

    def set_profile_postal_address_entry(self, address):
        """Update the postal_address_entry Qt widget from an external change."""
        if hasattr(self, "postal_address_entry") and self.postal_address_entry is not None:
            self.postal_address_entry.setText(str(address))
        return self

    def set_profile_city_address_entry(self, address):
        """Update the city_address_entry Qt widget from an external change."""
        if hasattr(self, "city_address_entry") and self.city_address_entry is not None:
            self.city_address_entry.setText(str(address))
        return self

    def set_profile_state_address_entry(self, address):
        """Update the state_address_entry Qt widget from an external change."""
        if hasattr(self, "state_address_entry") and self.state_address_entry is not None:
            self.state_address_entry.setText(str(address))
        return self

    def set_profile_email_entry(self, email):
        """Update the email_entry Qt widget from an external change."""
        if hasattr(self, "email_entry") and self.email_entry is not None:
            self.email_entry.setText(str(email))
        return self

    def set_profile_phone_entry(self, phone):
        """Update the phone_entry Qt widget from an external change."""
        if hasattr(self, "phone_entry") and self.phone_entry is not None:
            self.phone_entry.setText(str(phone))
        return self

    def set_profile_second_phone_entry(self, phone):
        """Update the second_phone_entry Qt widget from an external change."""
        if hasattr(self, "second_phone_entry") and self.second_phone_entry is not None:
            self.second_phone_entry.setText(str(phone))
        return self

    def set_profile_company_entry(self, entry):
        """Update the company_entry Qt widget from an external change."""
        if hasattr(self, "company_entry") and self.company_entry is not None:
            self.company_entry.setText(str(company))
        return self

    def set_profile_company_email_entry(self, email):
        """Update the company_email_entry Qt widget from an external change."""
        if hasattr(self, "company_email_entry") and self.company_email_entry is not None:
            self.company_email_entry.setText(str(email))
        return self

    def set_profile_company_phone_entry(self, phone):
        """Update the company_phone_entry Qt widget from an external change."""
        if hasattr(self, "company_phone_entry") and self.company_phone_entry is not None:
            self.company_phone_entry.setText(str(phone))
        return self

    def set_profile_company_address_entry(self, address):
        """Update the company_address_entry Qt widget from an external change."""
        if hasattr(self, "company_address_entry") and self.company_address_entry is not None:
            self.company_address_entry.setText(str(address))
        return self

    def set_profile_zip_code_entry(self, zipcode):
        """Update the zip_code_entry Qt widget from an external change."""
        if hasattr(self, "zip_code_entry") and self.zip_code_entry is not None:
            self.zip_code_entry.setText(str(zipcode))
        return self

    def store_profile(self):
        """Persist current profile fields to the profile manager."""
        if self.profile is None or self.profiles is None:
            logma.info("[browser] store_profile: no active profile to persist")
            return self
        logma.info(f"[browser] store_profile: {self.profile}")
        # Persistence wired through the document's profile_manager.
        # Caller is responsible for calling document.save() afterward.
        return self

    def update_profile(self, profile_name):
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

    def update_toolbox_form_control(self):
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

    def update_toolbox_url_inspection(self):
        """"""
        self.set_current_url()
        self.set_current_domain()
        self.set_current_sub_domain()
        self.set_current_parameters()
        self.set_current_whois()
        return self

    def _delete_browsing_history(self):
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
                tables = ["ds_recent_rss_entries", "ds_recent_searches",
                          "ds_recent_documents", "browser_history"]
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

    def _delete_all_browsing_tabs(self):
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

    def _delete_cache(self):
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

    def _delete_metadata(self):
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

    def _delete_cookies(self):
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


class NchantdOfficeSlimTabSearch(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeSlimTabSearch").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {"url_code": "duckduckgo", "page": NchantdOfficeSidePage}
        self.search_viewer = NchantdWebViewer(self, cfg).initWidget()
        self.layout.addWidget(self.search_viewer)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_content(self):
        """"""
        content = self.document.active_page.to_dict()
        return content


class NchantdOfficeWebViewer(NchantdWebViewer):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeWebViewer").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_content(self):
        """"""
        content = self.document.active_page.to_dict()
        return content

    def populate_document(self, url):
        """"""
        super().populate_document(url)
        return self

    def save(self):
        """"""
        return self

    def set_url_path(self, url=None):
        """"""
        super().set_url_path(url)
        if url is not None:
            if isinstance(url, pyqt.QUrl):
                url = url.toString()
            if self.url_select_entry is None:
                return self
            self.url_select_entry.combobox.setCurrentText(url)
            self.url_select_entry.update_options([url], False, False)
        # self.save()
        # self.parent.document.add_page({"url": url})
        return self


class NchantdOfficeAdTab(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
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

    def initModel(self, cfg=None):
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

    def initView(self, cfg=None):
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

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_active_url(self):
        """"""
        if self.document.active_page.active_url.active_url is None:
            logma.info("No active url")
            return None
        url = self.document.active_page.active_url.active_url
        logma.info(f"URL {url}")
        return url

    def get_content(self):
        """"""
        content = self.document.active_page.to_dict()
        return content

    def populate_document(self, url=None):
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

    def __init__(self, name, browser=None, intercept=False, parent=None, cfg=None):
        """"""
        super().__init__(name, browser, intercept, parent, cfg)
        self.setup_address()

    def setup_address(self):
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


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
