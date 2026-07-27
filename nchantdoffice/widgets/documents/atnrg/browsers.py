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
    """"""

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

    def cmd_check_is_pinned(self, event, *args, **kwargs):
        """Stub implementation of cmd_check_is_pinned."""
        logma.info(f"[browsers] {self.__class__.__name__}.cmd_check_is_pinned invoked (stub)")
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

    def cmd_fill_in_forms(self, event, *args, **kwargs):
        """Stub implementation of cmd_fill_in_forms."""
        logma.info(f"[browsers] {self.__class__.__name__}.cmd_fill_in_forms invoked (stub)")
        return self

    def cmd_fill_in_forms_clear(self, event, *args, **kwargs):
        """Stub implementation of cmd_fill_in_forms_clear."""
        logma.info(f"[browsers] {self.__class__.__name__}.cmd_fill_in_forms_clear invoked (stub)")
        return self

    def cmd_fill_in_forms_edit(self, event, *args, **kwargs):
        """Stub implementation of cmd_fill_in_forms_edit."""
        logma.info(f"[browsers] {self.__class__.__name__}.cmd_fill_in_forms_edit invoked (stub)")
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

    def cmd_on_resource_select(self, event, *args, **kwargs):
        """Stub implementation of cmd_on_resource_select."""
        logma.info(f"[browsers] {self.__class__.__name__}.cmd_on_resource_select invoked (stub)")
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

    def cmd_set_pin_browser_tab(self, event, *args, **kwargs):
        """Stub implementation of cmd_set_pin_browser_tab."""
        logma.info(f"[browsers] {self.__class__.__name__}.cmd_set_pin_browser_tab invoked (stub)")
        return self

    def cmd_set_save_browser_tab(self, event, *args, **kwargs):
        """Stub implementation of cmd_set_save_browser_tab."""
        logma.info(f"[browsers] {self.__class__.__name__}.cmd_set_save_browser_tab invoked (stub)")
        return self

    def cmd_set_browsing_history_expiry(self, event, *args, **kwargs):
        """Stub implementation of cmd_set_browsing_history_expiry."""
        logma.info(f"[browsers] {self.__class__.__name__}.cmd_set_browsing_history_expiry invoked (stub)")
        return self

    def cmd_show_badge(self, event, *args, **kwargs):
        """Stub implementation of cmd_show_badge."""
        logma.info(f"[browsers] {self.__class__.__name__}.cmd_show_badge invoked (stub)")
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
        """"""
        # TODO: get information from application config...is this configurable by instance?
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
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        # PUSH to 0.0.3 requires logic to register application as default browser
        # cfg = {
        #     "text": "Is Default Browser",
        #     "handler": self.cmd_set_default_browser,
        #     "value": self.get_current_default_browser(),
        #     "size": ["auto", "auto"],
        # }
        # self.default_browser_checkbox = NchantdCheckboxWidget(self, cfg)
        # items[cnt]["widget"] = self.default_browser_checkbox
        # cnt += 1
        # Home Page & Search Section
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Home Page",
            "layout": "horizontal",
            "handler": self.cmd_set_home_page,
            "value": self.get_current_home_page(),
            "size": ["auto", "auto"],
        }
        self.default_home_page_entry = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.default_home_page_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Actions taken here will affect all browser tabs related to the current active profile",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.notification_label = NchantdLabel(self, cfg)
        items[cnt]["widget"] = self.notification_label
        cnt += 1
        # Privacy Controls Section
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "text": "Clear Cookies",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "handler": self.cmd_clear_cookies,
        }
        self.clear_cookies_button = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.clear_cookies_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "text": "Clear Cache",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "handler": self.cmd_clear_cache,
        }
        self.clear_cache_button = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.clear_cache_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "text": "Clear MetaData",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "handler": self.cmd_clear_metadata,
        }
        self.clear_metadata_button = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.clear_metadata_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "text": "Clear Browsing History",
            "layout": "horizontal",
            "handler": self.cmd_clear_browsing_history,
        }
        self.browsing_history_clear_button = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.browsing_history_clear_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Browsing History Expiry (Days)",
            "layout": "horizontal",
            "handler": self.cmd_set_browsing_history_expiry,
            "value": self.get_browsing_history_expiry(),
            "size": None,
            "stretch": True,
        }
        self.browsing_history_policy_spinbox = NchantdLabeledSpinBox(self, cfg)
        items[cnt]["widget"] = self.browsing_history_policy_spinbox
        cnt += 1
        return items

    def init_drawer_url_inspection(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        # PUSH to 0.0.3
        # if cnt not in items:
        #     items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        # cfg = {
        #     "layout": "horizontal",
        #     "actions": {0: "show_badge_secure", 1: "show_badge_wot", 2: "show_badge_2fdns"},
        #     "handler": self.cmd_show_badge,
        # }
        # items[cnt]["widget"] = NchantdBadgeBar(self, cfg)
        # cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Current URL",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_active_url() or "",
        }
        self.url_label = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.url_label
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Current Domain",
            "readonly": True,
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_current_domain() or "",
        }
        self.domain = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.domain
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Sub Domain",
            "readonly": True,
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_current_sub_domain() or "",
        }
        self.sub_domain = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.sub_domain
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Parameters",
            "readonly": True,
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_current_parameters() or "",
        }
        self.parameters = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.parameters
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "WhoIs",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_current_whois() or "",
        }
        self.whois = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.whois
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
    # PUSH to version 0.0.3
    # def init_drawer_quickstart(self):
    #     """"""
    #     items = self.toolbox_config[500].get("items", {})
    #     cnt = 0
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {"text": "Bookmarks List"}
    #     # TODO: build out using quick app links like a mini catalog
    #     #
    #     self.quick_start_list = NchantdOfficeBrowserQuickStartPane(self, cfg).initWidget()
    #     items[cnt]["widget"] = self.quick_start_list
    #     cnt += 1
    #     return items

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
        """"""
        # TODO DEBUG document is not updating the active url in the content section
        #  not sure if the page section is needed
        #  remove the caller key/value
        #  versioning of content not happening in all cases
        #  probably a save that is not reloading the version after
        logma.info(f"Save Browser Profile")
        # DEBUG this should be standard but it creates an issue here
        # if self.document is None:
        #     self.new_document()
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
        """"""
        profile = self.document.profile_manager.get_current_profile()
        # TODO delete all browsing history for this profile on disk and in database non-history
        logma.info(f"Non Functional")
        return self

    def _delete_all_browsing_tabs(self):
        """"""
        profile = self.document.profile_manager.get_current_profile()
        # TODO delete all browsing history for this profile on disk and in database non-history
        logma.info(f"Non Functional")
        return self

    def _delete_cache(self):
        profile = self.document.profile_manager.get_current_profile()
        # TODO delete all cache for this profile on disk and in database non-history
        logma.info(f"Non Functional")
        return self

    def _delete_metadata(self):
        """"""
        profile = self.document.profile_manager.get_current_profile()
        # TODO delete all metadata for this profile on disk and in database non-history
        logma.info(f"Non Functional")
        return self

    def _delete_cookies(self):
        """"""
        profile = self.document.profile_manager.get_current_profile()
        # TODO delete all cookies for this profile on disk and in database non-history
        logma.info(f"Non Functional")
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
        self.contact.emergency_phone = None  # self.contact.phones[0]#TODO implement data sourcing


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
