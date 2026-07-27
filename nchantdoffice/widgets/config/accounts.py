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

# ====================================================================================================================||
pxcfg = join(here, "_data_", "accounts.yaml")


class NchantdOfficeAccountOverview(NchantdAccountOverview):
    """Account overview widget showing account status and key metrics"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeAccountOverview").override(cfg))
        self.account_settings = None
        self.account_name_label = None
        self.account_type_label = None
        self.subscription_label = None
        self.storage_label = None
        self.documents_label = None

    def initModel(self):
        """"""
        super().initModel()
        self.account_settings = self.app.model.settings.account_settings
        return self

    def initView(self):
        """"""
        super().initView()
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
        # Storage usage (placeholder)
        cfg = {"text": "Storage: 0 GB / 10 GB", "size": ["auto", "auto"]}
        self.storage_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.storage_label)
        # Document count (placeholder)
        cfg = {"text": "Documents: 0", "size": ["auto", "auto"]}
        self.documents_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.documents_label)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def refresh_account_info(self):
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

    def get_account_summary(self):
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

    def __init__(self, parent=None, cfg=None):
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

    def initModel(self):
        """"""
        super().initModel()
        self.account = self.app.model.settings.account_settings
        return self

    def initView(self):
        """"""
        super().initView()
        # top_layout = pyqt.QHBoxLayout()
        # cfg = {
        #     "label": "Nchantd Account",
        #     "size": ["auto", "auto"],
        #     "layout": "horizontal",
        #     "entrybox": {"size": [100, 25]},
        # }
        # self.user_name = NchantdEntryEditor(self, cfg).initWidget()
        # # TODO: get user name from account api
        # self.user_name.setPlaceholderText(f"{self.app.model.user.name}")
        # top_layout.addWidget(self.user_name)
        #
        # # status_layout = pyqt.QHBoxLayout()
        # cfg = {"label": "Status: ", "size": ["auto", "auto"], "layout": "horizontal", "entrybox": {"size": [50, 25]}}
        # self.account_status = NchantdEntryEditor(self, cfg).initWidget()
        # self.account_status.setPlaceholderText(f"{self.app.model.user.nchantrs_account_status}")
        # top_layout.addWidget(self.account_status)
        #
        # # TODO: connect to service and get details
        # cfg = {"label": "Credits: ", "size": ["auto", "auto"], "layout": "horizontal", "entrybox": {"size": [50, 25]}}
        # self.credits_status = NchantdEntryEditor(self, cfg).initWidget()
        # self.credits_status.setPlaceholderText(f"{self.app.model.user.nchantrs_account_credits}")
        # top_layout.addWidget(self.credits_status)
        # # top_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft)
        # # top_layout.addLayout(status_layout)
        # top_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft)
        #
        # layout = pyqt.QHBoxLayout()
        # # layout.addLayout(top_layout)
        # layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft)
        #
        # self.config.dikt.pop("height", None)
        # self.config.dikt.pop("width", None)
        # logma.info(f"Set Scrolling Ad")
        # if self.user.no_ads:
        #     cfg = {"text": "Bob Board Ad Sapce", "size": [800, 75]}
        #     self.scrolling_ad = NchantdLabel(self, cfg)
        #     self.scrolling_ad.initWidget()  #  Need a widget to replace this space that is useful to the user
        # else:
        #     cfg = {"text": "Bob Board Ad Sapce", "size": [800, 75]}
        #     self.scrolling_ad = NchantdLabel(self, cfg).initWidget()
        # logma.info(f"Scrolling Ad {self.scrolling_ad.size()}")
        # layout.addWidget(self.scrolling_ad)

        # if self.user.apikey is None:  # User has not registered with nchatrs.com
        #     cfg = {"text": "Register", "size": [50, 75]}  # TODO: implement a larger button graphic
        #     self.register_button = NchantdButton(self, cfg).initWidget()
        # elif self.user.is_paid is False:  # User has been registered as a free user
        #     cfg = {"text": "Start Subscription", "size": [50, 75]}
        #     self.register_button = NchantdButton(self, cfg).initWidget()
        # else:
        #     cfg = {"text": "Connect to Services", "size": [50, 75]}
        #     self.register_button = NchantdButton(self, cfg).initWidget()
        # layout.addWidget(self.register_button)
        # layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft | pyqt.Qt.AlignmentFlag.AlignTop)
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
        cfg = {
            "url": "https://www.nchantdoffice.com/registration",
            "size": [1600, 750],
            "is_simple": True,
        }
        if self.user.has_pro:
            cfg["url"] = "https://www.nchantdoffice.com/whats_new"
        elif self.user.has_account:
            cfg["url"] = "https://www.nchantdoffice.com/get_pro"
        self.browser = NchantdWebViewer(self, cfg).initWidget()
        layout.addWidget(self.browser)
        self.layout.addLayout(layout)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def save_account_settings(self):
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

    def load_account_settings(self):
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

    def validate_account_settings(self):
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

    def update_account_status(self, status):
        """Update account status display"""
        if self.account_status:
            self.account_status.setPlaceholderText(str(status))
            self.app.model.user.nchantrs_account_status = status
        return self

    def update_credits(self, credits):
        """Update credits display"""
        if self.credits_status:
            self.credits_status.setPlaceholderText(str(credits))
            self.app.model.user.nchantrs_account_credits = credits
        return self

    def refresh_browser(self):
        """Refresh the embedded browser with appropriate URL"""
        try:
            if not self.browser:
                return self

            # Determine appropriate URL based on user status
            if self.user.has_pro:
                url = "https://www.nchantdoffice.com/whats_new"
            elif self.user.has_account:
                url = "https://www.nchantdoffice.com/get_pro"
            else:
                url = "https://www.nchantdoffice.com/registration"

            # Update browser
            if hasattr(self.browser, "load_url"):
                self.browser.load_url(url)
            elif hasattr(self.browser, "setUrl"):
                self.browser.setUrl(pyqt.QUrl(url))

            logma.info(f"Browser refreshed with URL: {url}")

        except Exception as e:
            logma.error(f"Error refreshing browser: {e}")

        return self

    def get_account_data(self):
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

    def sync_with_server(self):
        """Synchronize account data with nchantrs.com server.

        Validates the API key, makes a GET request to the nchantrs
        account endpoint, parses the JSON response and writes the
        returned ``status`` and ``credits`` onto the local user
        object via ``update_account_status`` / ``update_credits``.

        Returns ``True`` on a successful sync, ``False`` on any
        validation, network, or parse failure.
        """
        try:
            user = getattr(self.app.model, "user", None)
            if not user or not getattr(user, "apikey", None):
                logma.warning("[accounts] sync_with_server: no API key configured")
                return False

            logma.info("Syncing account data with server...")
            try:
                import requests  # type: ignore
            except ImportError:
                logma.warning("[accounts] sync_with_server: requests module not installed")
                return False

            try:
                response = requests.get(
                    "https://api.nchantrs.com/account",
                    headers={"Authorization": f"Bearer {user.apikey}"},
                    timeout=10,
                )
            except Exception as e:
                logma.error(f"[accounts] sync_with_server request failed: {e}", exc_info=True)
                return False

            if response.status_code != 200:
                logma.warning(
                    f"[accounts] sync_with_server got status {response.status_code}"
                )
                return False

            try:
                data = response.json()
            except ValueError as e:
                logma.error(f"[accounts] sync_with_server parse failed: {e}", exc_info=True)
                return False

            if hasattr(self, "update_account_status") and "status" in data:
                self.update_account_status(data["status"])
            if hasattr(self, "update_credits") and "credits" in data:
                self.update_credits(data["credits"])
            return True

        except Exception as e:
            logma.error(f"[accounts] sync_with_server failed: {e}", exc_info=True)
            return False

# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
