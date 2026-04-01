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
from nchantrs.libraries import pyqt
from nchantrs.widgets.config.accounts import NchantdAccountOverview
from ogma.logma import Logma
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
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeAccountOverview"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.account_settings = None

    def initModel(self):
        """"""
        super().initModel()
        self.account_settings = self.app.model.settings.account_settings
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeAccountSettings(NchantdAccountSettings):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdAccountSettings"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
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
        top_layout = pyqt.QVBoxLayout()
        cfg = {
            "label": "Nchantd Account",
            "size": ["auto", "auto"],
            "layout": "horizontal",
            "entrybox": {"size": [100, 25]},
        }
        self.user_name = NchantdEntryEditor(self, cfg).initWidget()
        self.user_name.setPlaceholderText(f"{self.app.model.user.name}")
        top_layout.addWidget(self.user_name)

        status_layout = pyqt.QHBoxLayout()
        cfg = {"label": "Status: ", "size": ["auto", "auto"], "layout": "horizontal", "entrybox": {"size": [50, 25]}}
        self.account_status = NchantdEntryEditor(self, cfg).initWidget()
        self.account_status.setPlaceholderText(f"{self.app.model.user.nchantrs_account_status}")
        status_layout.addWidget(self.account_status)

        # TODO: connect to service and get details
        cfg = {"label": "Credits: ", "size": ["auto", "auto"], "layout": "horizontal", "entrybox": {"size": [50, 25]}}
        self.credits_status = NchantdEntryEditor(self, cfg).initWidget()
        self.credits_status.setPlaceholderText(f"{self.app.model.user.nchantrs_account_credits}")
        status_layout.addWidget(self.credits_status)
        status_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft)

        top_layout.addLayout(status_layout)
        top_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft)

        layout = pyqt.QHBoxLayout()
        layout.addLayout(top_layout)
        layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft)

        self.config.dikt.pop("height", None)
        self.config.dikt.pop("width", None)
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

        if self.user.apikey is None:  # User has not registered with nchatrs.com
            cfg = {"label": "Register", "size": [50, 75]}
            self.register_button = NchantdButton(self, cfg).initWidget()
        elif self.user.is_paid is False:  # User has been registered as a free user
            cfg = {"label": "Start Subscription", "size": [50, 75]}
            self.register_button = NchantdButton(self, cfg).initWidget()
        else:
            cfg = {"text": "Connect to Services", "size": [50, 75]}
            self.register_button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.register_button)
        layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft | pyqt.Qt.AlignmentFlag.AlignTop)
        self.layout.addLayout(layout)
        self.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft | pyqt.Qt.AlignmentFlag.AlignTop)

        layout = pyqt.QHBoxLayout()
        profile_layout = pyqt.QVBoxLayout()
        cfg = {"size": [200, 200]}
        self.profile_image = NchantdImage(self, cfg).initWidget()
        profile_layout.addWidget(self.profile_image)

        cfg = {"size": [200, 680], "label": "Profile Details"}
        self.profile_label = NchantdLabel(self, cfg).initWidget()
        profile_layout.addWidget(self.profile_label)
        profile_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
        layout.addLayout(profile_layout)
        cfg = {
            "url": "https://www.nchantdoffice.com/registration",
            "size": [1200, 750],
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


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
