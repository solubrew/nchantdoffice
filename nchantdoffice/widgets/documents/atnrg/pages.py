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

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
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

    def __init__(self, parent=None, profile=None, intercept=False, cfg=None):
        """Initialize the NchantdOfficeWebPage."""
        super().__init__(parent, profile, intercept, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeWebPage"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self):
        """Initialize the model and return self for method chaining."""
        super().initModel()
        return self

    def initView(self):
        """Initialize the view and return self for method chaining."""
        super().initView()
        return self

    def initWidget(self):
        """Initialize the widget by setting up model and view."""
        self.initModel()
        self.initView()
        return self

    def acceptNavigationRequest(self, url, request_type, is_main_frame):
        """Handle navigation requests."""
        # self.load_url(url)
        # self.parent.update_toolbox_url_inspection()
        return super().acceptNavigationRequest(url, request_type, is_main_frame)

    def _execute_javascript(self, script, success_message=None):
        """Execute JavaScript code in the web page.

        Args:
            script (str): JavaScript code to execute
            success_message (str, optional): Message to log on successful execution
        """
        self.page().runJavaScript(script)
        if success_message:
            print(success_message)

    def autofill_form(self):
        """Inject JavaScript to autofill HTML form fields with predefined data."""
        self._execute_javascript(self.AUTOFILL_SCRIPT, "Form autofilled successfully")

    def clear_form(self):
        """Inject JavaScript to clear all form input fields."""
        self._execute_javascript(self.CLEAR_FORM_SCRIPT, "Form cleared successfully")

    def open_new_tab(self):
        """Open a new browser tab."""
        super().open_new_tab()
        cfg = {}
        self.parent.app.model.codex.init_browser(cfg).load_document()
        return self

    def submit_text_to_webpage(self, element_name: str = "input"):
        """Submit text from QLineEdit to a specific webpage element.

        Args:
            element_name (str): ID of the target HTML element (defaults to 'input')
        """
        input_text = self.text_input.text()
        js_code = f"document.getElementById('{element_name}').value = '{input_text}';"
        self._execute_javascript(js_code, f"Text submitted to element '{element_name}'")


# class NchantdOfficeWebPage(NchantdWebPage):
#     """"""
#
#     def __init__(self, parent=None, profile=None, intercept=False, cfg=None):
#         """ """
#         super().__init__(parent, profile, intercept, cfg)
#         self.parent = parent
#         self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeWebPage"))
#         if self.parent:
#             self.config.override(parent.config)
#         self.config.override(cfg)
#
#     def initModel(self):
#         """"""
#         super().initModel()
#         return self
#
#     def initView(self):
#         """"""
#         super().initView()
#         return self
#
#     def initWidget(self):
#         """"""
#         self.initModel()
#         self.initView()
#         return self
#
#     def acceptNavigationRequest(self, url, request_type, is_main_frame):
#         """"""
#         # self.load_url(url)
#         # self.parent.update_toolbox_url_inspection()
#         return super().acceptNavigationRequest(url, request_type, is_main_frame)
#
#     def autofill_form(self):
#         """
#         Injects JavaScript into the page to autofill the HTML form.
#         """
#         autofill_script = """
#         const autofillData = {
#             name: "<[name]>",
#             email: "<[email]>",
#             number: "<[number]>",
#             street: "<[street]>",
#             city: "<[city]>",
#             state: "<[state]>",
#             zip: "<[zipcode]>",
#             phone: "<[phone]>",
#             website: "<[website]>"
#         };
#
#         for (let field in autofillData) {
#             const inputField = document.querySelector(
#                 `#${field}, [name=${field}], [placeholder*=${field}]`
#             );
#             if (inputField) inputField.value = autofillData[field];
#         }
#         console.log("Form Auto-Filled Successfully!");
#         """
#         # Execute the JavaScript in the web page
#         self.page().runJavaScript(autofill_script)
#
#     def clear_form(self):
#         """
#         Injects JavaScript into the page to clear the form fields.
#         """
#         clear_script = """
#         const inputs = document.querySelectorAll('input');
#         inputs.forEach(input => input.value = "");
#         console.log("Form Cleared!");
#         """
#         # Execute the JavaScript in the web page
#         self.page().runJavaScript(clear_script)
#
#     def open_new_tab(self):
#         """"""
#         super().open_new_tab()
#         cfg = {}
#         self.parent.app.model.codex.init_browser(cfg).load_document()
#         return self
#
#     def submit_text_to_webpage(self, element_name: str = "input"):
#         """
#         Takes input from QLineEdit and submits it to the webpage in the QWebEngineView.
#         """
#         # Get the text from the QTextWidget (QLineEdit in this case)
#         input_text = self.text_input.text()
#         # Run JavaScript on the webpage to set the input field's value
#         js_code = f"document.getElementById('{element_name}').value = '{input_text}';"
#         self.web_view.page().runJavaScript(js_code)  # Inject JavaScript


class NchantdOfficeDevPage(NchantdOfficeWebPage):
    """Development page with relaxed security for local development environments."""

    # Local development configuration constants
    LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0", "192.168.1.1"}
    LOCAL_IP_PREFIXES = ("192.168.", "10.", "172.")
    LOCAL_DOMAIN_SUFFIXES = (".local", ".localhost")

    def __init__(self, parent=None, profile=None, intercept=False, cfg=None):
        """Initialize development page with local security overrides."""
        super().__init__(parent, profile, intercept, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeDevPage"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """Initialize the model component."""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """Initialize the view component."""
        super().initView(cfg)
        return self

    def initWidget(self):
        """Initialize the complete widget by setting up model and view."""
        self.initModel()
        self.initView()
        return self

    def certificateError(self, error):
        """Accept certificate errors for local development hosts."""
        url = pyqt.QUrl(error.url())
        host = url.host()

        if self._is_local_host(host) and error.isOverridable():
            print(f"Accepting certificate error for local dev: {host}:{url.port()}")
            return True
        return super().certificateError(error)

    def _is_local_host(self, host):
        """Check if host is a local development address."""
        if host in self.LOCAL_HOSTS:
            return True

        if host.startswith(self.LOCAL_IP_PREFIXES):
            return True

        if host.endswith(self.LOCAL_DOMAIN_SUFFIXES):
            return True

        return False

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        """Handle navigation requests with debugging information."""
        logma.info(f"Navigation to: {url.toString()}")
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class NchantdOfficeSidePage(NchantdWebEnginePage):
    """"""

    def __init__(self, parent=None, profile=None, intercept=None, cfg=None):
        """ """
        super().__init__(parent, profile, intercept, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeSidePage"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.form_factor_script = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
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

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        # Print JavaScript console messages to Python console for debugging
        print(f"JS Message: {message} (Line: {line_number}, Source: {source_id})")

    def on_load_finished(self):
        if self.form_factor_script is not None:
            # Inject the form factor simulation script into the web page
            self.runJavaScript(self.form_factor_script)
            print("JavaScript injected to simulate form factor.")


class NchantdOfficeURL(NchantdURL):
    """"""

    def __init__(self, url, parent=None, cfg=None):
        """ """
        super().__init__(url, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeURL"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.set_url(self.config.dikt.get("url", None))


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
