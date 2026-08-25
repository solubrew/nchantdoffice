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

# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
from __future__ import annotations
from typing import Any, Dict, Self

from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.browsers.pages import NchantdWebEnginePage
from nchantrs.widgets.browsers.utilities import NchantdURL
from pyffice.web.url import PyfficeURL

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "pages.yaml")
# DESK T-NEW-052: route through the unified URL config so the
# operator can point the embedded browser at an internal site.
from nchantdoffice.utilities.urls import home_page as _home_page
HOMEPAGE = {"url": _home_page()}
HOMEURL = HOMEPAGE.get("url")


class NchantdOfficeWebPage(NchantdWebEnginePage):
    """"""

    # JavaScript constants for form operations
    AUTOFILL_SCRIPT = """
        const autofillData = {
            name: "<[name]>",
            email: "<[email]>",
            number: "<[number]>",
            street: "<[street]>",
            city: "<[city]>",
            state: "<[state]>",
            zip: "<[zipcode]>",
            phone: "<[phone]>",
            website: "<[website]>"
        };

        for (let field in autofillData) {
            const inputField = document.querySelector(
                `#${field}, [name=${field}], [placeholder*=${field}]`
            );
            if (inputField) inputField.value = autofillData[field];
        }
        console.log("Form Auto-Filled Successfully!");
    """

    CLEAR_FORM_SCRIPT = """
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => input.value = "");
        console.log("Form Cleared!");
    """

    def __init__(self, parent=None, profile=None, intercept=False, cfg=None) -> None:
        """Initialize the NchantdOfficeWebPage."""
        super().__init__(parent, profile, intercept, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeWebPage").override(cfg))
        self.document = None

    def initModel(self, cfg=None) -> Self:
        """Initialize the model and return self for method chaining."""
        super().initModel(cfg)
        document = {"document": self.config.override(cfg).get("document", {})}
        self.document = self.app.model.codex.init_web_page(document)
        self.document.load_document()
        self.initialize_context_menu("context.document.browser.page")
        return self

    def initView(self) -> Self:
        """Initialize the view and return self for method chaining."""
        super().initView()
        return self

    def initWidget(self) -> Self:
        """Initialize the widget by setting up model and view."""
        self.initModel()
        self.initView()
        return self

    def acceptNavigationRequest(self, url, request_type, is_main_frame) -> bool:
        """Handle navigation requests."""
        # self.load_url(url)
        # self.parent.update_toolbox_url_inspection()
        return super().acceptNavigationRequest(url, request_type, is_main_frame)

    def autofill_form(self) -> None:
        """Inject JavaScript to autofill HTML form fields with predefined data."""
        self._execute_javascript(self.AUTOFILL_SCRIPT, "Form autofilled successfully")
        return self

    def clear_form(self) -> None:
        """Inject JavaScript to clear all form input fields."""
        self._execute_javascript(self.CLEAR_FORM_SCRIPT, "Form cleared successfully")
        return self

    def get_active_url(self) -> NchantdURL:
        """"""
        cfg = {}
        url = None
        url = NchantdURL(url, self, cfg).initModel()
        return url

    def open_new_tab(self) -> Self:
        """Open a new browser tab."""
        super().open_new_tab()
        cfg = {}
        self.parent.app.model.codex.init_browser(cfg).load_document()
        return self

    def submit_text_to_webpage(self, element_name: str = "input") -> None:
        """Submit text from QLineEdit to a specific webpage element.

        Args:
            element_name (str): ID of the target HTML element (defaults to 'input')
        """
        input_text = self.text_input.text()
        js_code = f"document.getElementById('{element_name}').value = '{input_text}';"
        self._execute_javascript(js_code, f"Text submitted to element '{element_name}'")
        return self

    def _execute_javascript(self, script, success_message=None) -> None:
        """Execute JavaScript code in the web page.

        Args:
            script (str): JavaScript code to execute
            success_message (str, optional): Message to log on successful execution
        """
        self.page().runJavaScript(script)
        if success_message:
            logma.info(f"JS success: {success_message}")


class NchantdOfficeDevPage(NchantdOfficeWebPage):
    """Development page with relaxed security for local development environments."""

    # Local development configuration constants
    LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0", "192.168.1.1"}
    LOCAL_IP_PREFIXES = ("192.168.", "10.", "172.")
    LOCAL_DOMAIN_SUFFIXES = (".local", ".localhost")

    def __init__(self, parent=None, profile=None, intercept=False, cfg=None) -> None:
        """Initialize development page with local security overrides."""
        super().__init__(parent, profile, intercept, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeDevPage").override(cfg))

    def initModel(self, cfg=None) -> Self:
        """Initialize the model component."""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> Self:
        """Initialize the view component."""
        super().initView(cfg)
        return self

    def initWidget(self) -> Self:
        """Initialize the complete widget by setting up model and view."""
        self.initModel()
        self.initView()
        return self

    def certificateError(self, error) -> bool:
        """Accept certificate errors for local development hosts."""
        url = pyqt.QUrl(error.url())
        host = url.host()

        if self._is_local_host(host) and error.isOverridable():
            logma.info(f"Accepting certificate error for local dev: {host}:{url.port()}")
            return True
        return super().certificateError(error)

    def _is_local_host(self, host) -> bool:
        """Check if host is a local development address."""
        if host in self.LOCAL_HOSTS:
            return True

        if host.startswith(self.LOCAL_IP_PREFIXES):
            return True

        if host.endswith(self.LOCAL_DOMAIN_SUFFIXES):
            return True

        return False

    def acceptNavigationRequest(self, url, nav_type, is_main_frame) -> bool:
        """Handle navigation requests with debugging information."""
        logma.info(f"Navigation to: {url.toString()}")
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class NchantdOfficeSidePage(NchantdWebEnginePage):
    """"""

    def __init__(self, parent=None, profile=None, intercept=None, cfg=None) -> None:
        """ """
        super().__init__(parent, profile, intercept, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeSidePage").override(cfg))
        self.form_factor_script = None

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> Self:
        """"""
        super().initView(cfg)
        self.form_factor_script = """
             Object.defineProperty(window, 'innerWidth', { value: 375 });
             Object.defineProperty(window, 'innerHeight', { value: 812 });
             Object.defineProperty(window.screen, 'width', { value: 375 });
             Object.defineProperty(window.screen, 'height', { value: 812 });

             console.log('Form factor set to 375x812 (iPhone X).');
         """
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def javaScriptConsoleMessage(self, level, message, line_number, source_id) -> None:
        # Print JavaScript console messages to Python console for debugging
        logma.info(f"JS Message: {message} (Line: {line_number}, Source: {source_id})")

    def on_load_finished(self) -> None:
        if self.form_factor_script is not None:
            # Inject the form factor simulation script into the web page
            self.runJavaScript(self.form_factor_script)
            logma.info("JavaScript injected to simulate form factor.")


class NchantdOfficeURL(NchantdURL):
    """"""

    def __init__(self, url, parent=None, cfg=None) -> None:
        """ """
        super().__init__(url, parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeURL").override(cfg))
        self.set_url(self.config.get("url", self.config.get("homepage", HOMEURL)))
        self.unit = None

    def init_unit(self, cfg=None) -> None:
        """"""
        cfg = cfg or {}
        self.config.override(cfg)
        self.unit = self.app.model.codex.init_url({"document": self.config.get("document", {})})
        self.unit.load_unit()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
