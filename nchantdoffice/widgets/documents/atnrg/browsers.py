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
from os.path import abspath, dirname, join
import datetime as dt
import json as j

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantdoffice.widgets.documents.atnrg.pages import NchantdOfficeSidePage, NchantdOfficeURL
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.browsers.browsers import NchantdWebViewer
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons
from nchantrs.widgets.annotations import NchantdLabel, NchantdBadgeBar
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry, NchantdLabeledSpinBox
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.tables.lists import NchantdList

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "browsers.yaml")


class NchantdOfficeWebBrowser(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Nchantd Browser", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeWebBrowser").override(cfg))
        logma.json(self.config.dikt.get("document", {}))
        # FIX (high-severity): Initialize toolbox_config so init_drawer_* methods can index it.
        # ORIGINAL: no toolbox_config initialization → every init_drawer_url_inspection / init_drawer_browser_config
        # call inside init_toolbox() raised AttributeError on first tab open (same bug class as matricies.py).
        # Matches the pattern used in NchantdOfficeCloakModel (commit f67dab5).
        self.toolbox_config = self.config.dikt.get("toolbox", {})
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
        if cfg is None:
            cfg = {}
        self.browser = NchantdOfficeWebViewer(self, {"url": self.active_url})
        self.browser.is_simple = False
        cfg["buttons"] = self.build_toolbar()
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

    def add_profile(self, profile, cfg):
        """"""
        profile_limit = 1
        if getattr(self.app.model.user, "has_pro", False) if self.app.model.user else False:
            profile_limit = 10
        if self.profiles.get_count() >= profile_limit:
            return self
        self.profiles.add_profile(profile, cfg)
        return self

    def build_toolbar(self):
        """"""
        logma.info(f"Build toolbar")
        buttons = self.browser.build_toolbar()
        self.browser.url_select_entry.config.dikt["handler"] = self.cmd_goto_page
        buttons[17] = {"action": "web_page_pin", "handler": self.cmd_pin_page, "value": self.cmd_check_is_pinned}
        buttons[100] = "_skip"
        buttons[150] = "_skip"
        buttons[200] = "_skip"
        return buttons

    def cmd_check_is_pinned(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_clear_cookies(self, event, *args, **kwargs):
        """"""
        self.app.model.delete_cookies(self.document.profile_manager.get_current_profile())
        return self

    def cmd_clear_cache(self, event, *args, **kwargs):
        """"""
        self.app.model.delete_cache(self.document.profile_manager.get_current_profile())
        return self

    def cmd_clear_metadata(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_clear_browsing_history(self, event, *args, **kwargs):
        """"""
        self.app.model.clear_browsing_history(self.document.profile_manager.get_current_profile())
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

    def cmd_add_profile(self, event, *args, **kwargs):
        """""
        # STUB: open dialog / create a new browser profile
        return self

    def cmd_get_pro(self, event, *args, **kwargs):
        """""
        # STUB: redirect user to upgrade to Pro plan
        if hasattr(self, 'app') and hasattr(self.app, 'view'):
            self.app.view.switch_to_account_tab()
        return self

    def cmd_add_profile(self, event, *args, **kwargs):
        """""
        # STUB: open dialog / create a new browser profile
        return self

    def cmd_get_pro(self, event, *args, **kwargs):
        """""
        # STUB: redirect user to upgrade to Pro plan
        if hasattr(self, 'app') and hasattr(self.app, 'view'):
            self.app.view.switch_to_account_tab()
        return self

    def cmd_fill_in_forms(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_fill_in_forms_clear(self, event, *args, **kwargs):
        """will ask for delete in dialog"""
        return self

    def cmd_fill_in_forms_edit(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_goto_page(self, event=None, *args, **kwargs):
        """"""
        logma.info(f"Event {event}")
        url = self.browser.url_select_entry.combobox.lineEdit().text().strip()
        # page = self.add_page(url)
        page = None
        self.document.set_page_active(page)
        url = self.document.active_page.active_url.active_url
        logma.info(f"Goto {url}")
        # self.browser.cmd_goto_page(url, args, kwargs)
        self.populate_document(url)
        # # need to check if url inspection drawer has been initialized or not?
        # self.update_toolbox_url_inspection(self.browser.active_url)
        # self.document.set_refresh_time()
        # self.populate_document(url)
        return self

    def cmd_launch_source_tab(self, event, *args, **kwargs):
        """"""
        widget = "Source"
        self.app.model.add_tab(self.document.pid, widget)
        return self

    def cmd_make_version(self, event, *args, **kwargs):
        """"""
        version = event
        super().make_version(version)
        self.document.add_version(self.version)
        return self

    def cmd_pin_page(self, event, *args, **kwargs):
        """"""
        self.make_webapp()
        self.pin_page()
        return self

    def cmd_next_page(self, url=None, *args, **kwargs):
        """"""
        self.browser.cmd_next_page(url, args, kwargs)
        # self.update_toolbox_url_inspection(self.browser.active_url)
        self.document.set_refresh_time()
        return self

    def cmd_on_resource_select(self, event, *args, **kwargs):
        """"""
        return self

    # OLD-DELETE-ME: cmd_pin_page dead-overwrites the earlier definition above. Kept as a commented stub.
    # def cmd_pin_page(self, event, *args, **kwargs):
    #     """"""
    #     self.pin_page()
    #     return self

    def cmd_previous_page(self, url=None, *args, **kwargs):
        """"""
        self.browser.cmd_previous_page(url, args, kwargs)
        # self.update_toolbox_url_inspection(self.browser.active_url)
        self.document.set_refresh_time()
        return self

    def cmd_profile_change(self, event, *args, **kwargs):
        """"""
        self.update_toolbox_form_control()
        return self

    def cmd_refresh_page(self, url=None, *args, **kwargs):
        """"""
        # self.browser.cmd_refresh_page()
        # self.update_toolbox_url_inspection(self.browser.active_url)
        self.populate_document()
        self.document.set_refresh_time()
        return self

    def cmd_scan_source(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_set_default_browser(self, event, *args, **kwargs):
        """"""
        self.set_default_browser(event)
        return self

    def cmd_set_home_page(self, event, *args, **kwargs):
        """"""
        self.home_page = event
        return self

    def cmd_set_pin_browser_tab(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_set_save_browser_tab(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_set_browsing_history_expiry(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_show_badge(self, event, *args, **kwargs):
        """"""
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
        # TODO: need to connect to some basic web scrapping functions
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
        expiry = self.config.dikt.get("browsing_history_expiry", 90)
        return expiry

    def get_current_default_browser(self):
        """"""
        return None

    def get_current_domain(self):
        """"""
        if self.document.active_page.active_url.active_url is None:
            logma.info("No active url")
            return None
        domain = self.document.active_page.active_url.domain
        logma.info(f"Domain {domain}")
        return domain

    def get_current_home_page(self, home_page=None):
        """"""
        # home_page = self.document.home_url
        if home_page is None:
            home_page = self.config.dikt.get("default_home_page", "duckduckgo.com")
        return home_page

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

    def get_profile(self, profile):
        """"""
        if profile not in self.profiles.profiles:
            self.app.model.get_profiles()
        # profile = self.profiles.profiles[profile]
        return profile

    def get_profiles(self):
        """"""
        return self.profiles

    def get_search_engines(self):
        """"""
        search_engines = [
            "Google",
        ]
        return search_engines

    def init_drawer_browser_config(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "text": "Set as Default Browser",
            "handler": self.cmd_set_default_browser,
            "value": self.get_current_default_browser(),
            "size": [300, "auto"],
        }
        self.default_browser_checkbox = NchantdCheckbox(self, cfg)
        items[cnt]["widget"] = self.default_browser_checkbox
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
        self.clear_cookies_button = NchantdButton(self, cfg)
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
        self.clear_cache_button = NchantdButton(self, cfg)
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
        self.clear_metadata_button = NchantdButton(self, cfg)
        items[cnt]["widget"] = self.clear_metadata_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "text": "Clear Browsing History",
            "layout": "horizontal",
            "handler": self.cmd_clear_browsing_history,
        }
        self.browsing_history_clear_button = NchantdButton(self, cfg)
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
        # Home Page & Search Section
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Home Page",
            "layout": "horizontal",
            "handler": self.cmd_set_home_page,
            "value": self.get_current_home_page(),
            "options": self.get_search_engines(),
            "size": None,
        }
        self.default_home_page_entry = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.default_home_page_entry
        cnt += 1
        return items

    def init_drawer_url_inspection(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "layout": "horizontal",
            "actions": {0: "show_badge_secure", 1: "show_badge_wot", 2: "show_badge_2fdns"},
            "handler": self.cmd_show_badge,
        }
        items[cnt]["widget"] = NchantdBadgeBar(self, cfg)
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Current URL",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_active_url(),
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
            "value": self.get_current_domain(),
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
            "value": self.get_current_sub_domain(),
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
            "value": self.get_current_parameters(),
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
            "value": self.get_current_whois(),
        }
        self.whois = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.whois
        cnt += 1
        # use this as a basis to build up a interface for 2FDNS
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {"text": "2FDNS"}
        items[cnt]["widget"] = NchantdLabel(self, cfg)
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {"text": "Site Settings"}
        items[cnt]["widget"] = NchantdLabel(self, cfg)
        cnt += 1
        return items

    def init_drawer_form_control(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        options = self.app.model.get_profiles()
        if self.app.model.user and self.app.model.user.user_name not in options:
            cfg = {}
            self.add_profile(self.app.model.user.user_name, cfg)
        if not getattr(self.app.model.user, "has_pro", False) if self.app.model.user else False:
            options += ["Get Pro"]
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Select Profile",
            "layout": "horizontal",
            "options": options,
            "handler": self.cmd_profile_change,
        }
        self.profile_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.profile_select
        cnt += 1
        if cnt not in items:
            items[cnt] = {}
        cfg = {
            "text": "Fill-In Forms",
            "type": "custom",
            "handler": self.cmd_fill_in_forms,
            "justify": "center",
            "size": ["auto", "auto"],
        }
        self.fill_forms_button = NchantdButton(self, cfg)
        items[cnt]["widget"] = self.fill_forms_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "User Name",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.name_entry = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.name_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Name",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.name_entry = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.name_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Email",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.email_entry = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.email_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Street",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.address_street_entry = NchantdLabeledEntry(self, cfg)  # TODO Build an Address Input widget
        items[cnt]["widget"] = self.address_street_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "City",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.address_city_entry = NchantdLabeledEntry(self, cfg)  # TODO Build an Address Input widget
        items[cnt]["widget"] = self.address_city_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "State",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.address_state_entry = NchantdLabeledEntry(self, cfg)  # TODO Build an Address Input widget
        items[cnt]["widget"] = self.address_state_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Zip Code",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.address_zip_entry = NchantdLabeledEntry(self, cfg)  # TODO Build an Address Input widget
        items[cnt]["widget"] = self.address_zip_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Primary Phone",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.phone_entry = NchantdLabeledEntry(self, cfg)  #
        items[cnt]["widget"] = self.phone_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Emergency Phone",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.second_phone_entry = NchantdLabeledEntry(self, cfg)  #
        items[cnt]["widget"] = self.second_phone_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Company Name",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.company_entry = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.company_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Company Email",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.company_email_entry = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.company_email_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Company Phone",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.company_phone_entry = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.company_phone_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "handler": self.cmd_edit_profile,
        }
        self.update_buttons = NchantdAcceptButtons(self, cfg)
        items[cnt]["widget"] = self.update_buttons
        cnt += 1
        return items

    def init_drawer_source_inspection(self):
        """"""
        items = self.toolbox_config[400].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {"text": "Launch Source Tab of Current Page"}
        self.source_document_launch_button = NchantdButton(self, cfg)
        items[cnt]["widget"] = self.source_document_launch_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {"text": "Scan Source for Resources"}
        self.crawl_current_page_button = NchantdButton(self, cfg)
        items[cnt]["widget"] = self.crawl_current_page_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        data = ["Images", "CSS", "JS", "HTML", "JSON", "XML", "Text", "All"]
        cfg = {
            "text": "Set as Default Browser",
            "data": data,
            "handler": self.cmd_on_resource_select,
        }
        self.page_resource_list = NchantdList(self, cfg)
        items[cnt]["widget"] = self.page_resource_list
        cnt += 1
        return items

    def init_drawer_quickstart(self):
        """"""
        items = self.toolbox_config[500].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {"text": "Set as Default Browser"}
        self.quick_start_list = NchantdList(self, cfg)
        items[cnt]["widget"] = self.quick_start_list
        cnt += 1
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_url_inspection()
        # TODO: seems something related to having buttons in the drawer?
        #  need to only be rendered on draw selection anyway
        self.toolbox_config[200]["items"] = self.init_drawer_browser_config()
        # self.toolbox_config[300]["items"] = self.init_drawer_form_control()
        # self.toolbox_config[400]["items"] = self.init_drawer_source_inspection()
        # self.toolbox_config[500]["items"] = self.init_drawer_quickstart()

    def open_new_tab(self):
        """"""
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
        if url is None:
            url = self.get_active_url()
        logma.info(f"Populate Document {url}")
        if self.pinned is False:
            self.browser.populate_document(url)
            self.update_toolbox_url_inspection()
        self.save()
        self.document.save()
        return self

    def save(self):
        """"""
        logma.info(f"Save Browser Profile")
        # url = self.browser.url_select_entry.combobox.lineEdit().text().strip()
        # if url == "about:blank":
        #    url = None
        # logma.info(f"URL: {url}")
        # self.document.set_url_active(url)
        self.document.save()
        if self.pin is True:
            return self
        # self.document.set_url_active(self.active_url.url)
        content = self.document.active_page.to_dict()
        logma.info(f"Content: {content}")
        if content != self.document.content:
            self.document.set_content(content)
        super().save()
        self.document.save()
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
        """"""
        return self

    def set_profile_first_name_entry(self, name):
        """"""
        return self

    def set_profile_last_name_entry(self, name):
        """"""
        return self

    def set_profile_middle_name_entry(self, name):
        """"""
        return self

    def set_profile_postal_address_entry(self, address):
        """"""
        return self

    def set_profile_city_address_entry(self, address):
        """"""
        return self

    def set_profile_state_address_entry(self, address):
        """"""
        return self

    def set_profile_email_entry(self, email):
        """"""
        return self

    def set_profile_zip_code_entry(self, zipcode):
        """"""
        return self

    def store_profile(self):
        """"""
        return self

    def update_profile(self, profile_name):
        """"""
        return self

    def update_toolbox_form_control(self):
        """"""
        profile = self.get_profile(self.profile_select.combobox.lineEdit().text().strip())
        self.set_profile(profile)
        # self.set_profile_user_name_entry(self.profile.user_name)
        # self.set_profile_first_name_entry(self.profile.first_name)
        # self.set_profile_middle_name_entry(self.profile.middle_name)
        # self.set_profile_last_name_entry(self.profile.last_name)
        # self.set_profile_email_entry(self.profile.email)
        # self.set_profile_postal_address_entry(self.profile.address)
        # self.set_profile_city_address_entry(self.profile.city_address)
        # self.set_profile_state_address_entry(self.profile.state_address)
        # self.set_profile_zip_code_entry(self.profile.zip_code)
        # self.set_profile_phone_entry(self.profile.phone)
        # self.set_profile_second_phone_entry(self.profile.second_phone)
        # self.set_profile_company_entry(self.profile.company_name)
        # self.set_profile_company_email_entry(self.profile.company_email)
        # self.set_profile_company_phone_entry(self.profile.company_phone)
        # self.set_profile_company_address_entry(self.profile.company_address)
        return self

    def update_toolbox_url_inspection(self):
        """"""
        self.set_current_url()
        self.set_current_domain()
        self.set_current_sub_domain()
        self.set_current_parameters()
        self.set_current_whois()
        return self


class NchantdOfficeSlimTabSearch(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
class NchantdOfficeSlimTabSearch(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        # FIX (critical): pass `parent` to Qt base, not `self` (self-as-parent produces an
        # orphan widget chain — parent() returns None, lifecycle/cleanup walking breaks).
        # ORIGINAL (commented for traceability):
        #     super().__init__(self)
        super().__init__(parent) if parent is not None else super().__init__()
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeSlimTabSearch"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

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


class NchantdOfficeWebViewer(NchantdWebViewer):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
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
            self.url_select_entry.combobox.setCurrentText(url)
            self.url_select_entry.update_options([url], False, False)
        # self.save()
        # self.parent.document.add_page({"url": url})
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
