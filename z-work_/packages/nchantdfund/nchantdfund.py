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

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from nchantrs.libraries import pyqt
from nchantrs.widgets.items.catalogs import NchantdAccountCatalogItem
from nchantrs.widgets.catalogs import NchantdCatalog
from nchantrs.widgets.media.editors.editors import NchantdEntryEditor
from nchantrs.widgets.tables import NchantdTable
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.media.images import NchantdImage
from nchantrs.widgets.controls.controls import NchantdCheckboxGroup
from nchantrs.wizards.pages import NchantdWizardPage
from nchantrs.widgets.widgets import NchantdWidget
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "nchantdfund.yaml")


class NchantdNewNchantdFundApplicationPage(NchantdWizardPage):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.instruct(pxcfg).select("NchantdNewAccountNchantdFundPage")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdNewNchantdFundApplicationPage, self).__init__(self.parent, self.config)
        self.services = []

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        # ask for accounts
        # ask for interests
        # tracking projecting
        # trading
        # currencies
        # stocks
        # commodities
        # crypto
        cfg = {"options": self.services}
        self.services_selection = NchantdCheckboxGroup(self, cfg).initWidget()
        self.layout.addWidget(self.services_selection)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdFundApplicationIntegration(NchantdWidget):
    """This will interject all the components needed to make any initialized application have the same nodes and tabs
    as an intialized NchantdFund application"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.instruct(pxcfg).select("NchantdFundApplicationIntegration")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdFundApplicationIntegration, self).__init__(self.parent, self.config)

    def add_finanical_account(self):
        """"""
        return self

    def initModel(self):
        """"""
        super().initModel()
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


class NchantdFundAccounts(NchantdWidget):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = condor.instruct(pxcfg).select("NchantdFundAccounts")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdFundAccounts, self).__init__(parent, cfg)


class NchantdFundCashFlowTracker(NchantdWidget):
    """ """

    def __init__(self, parent=None, cfg={}, root=None):
        """ """
        self.parent = parent
        self.config = condor.instruct(pxcfg)
        self.config.select("NchantdFundCashFlowTrackerTab").override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdFundCashFlowTrackerTab, self).__init__(parent, cfg)

    def initWidget(self, pos=0):
        """"""

    def buildPane(self):
        """"""
        self.layout = pyqt.QHBoxLayout()
        vlayout = pyqt.QVBoxLayout()
        cnt = 0
        for account in accounts:

            entry = NchantdEntryEditor()
            self.layout.addWidget(entry)
            if cnt > 5:
                vlayout = pyqt.QVBoxLayout()
                self.layout.addWidget(vlayout)
                cnt = 0
        areas = {"Daily": "", "Weekly": "", "Monthly": "", "Yearly": ""}
        for area in areas:
            for item in items:
                pass
        levels = {"Days": 14, "Weeks": 16, "Months": 36, "Years": 20}
        for level in levels:
            for bucket in range(levels[level]):
                pass


class NchantdFundAccountsCatalog(NchantdCatalog):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.instruct(pxcfg).select("NchantdFundAccountsCatalog")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdFundAccountsCatalog, self).__init__(self.parent, self.config)
        self.accounts = self.parent.parent.model.accounts

    def initModel(self):
        """"""
        return self

    def initView(self):
        """"""
        super().initView()
        if log:
            logma.info(f"View")
        self.box.setTitle("Accounts")
        self.box.setMinimumHeight(600)
        max_rows = 4
        col = 0
        row = 0
        accounts = {}
        for account in self.accounts["name"].values.tolist():
            if log:
                logma.info(f"Account {account}")
            if account not in accounts:
                accounts[account] = {}
            accounts[account]["widget"] = NchantdAccountCatalogItem(self, self.config).initWidget()
            self.box.addWidget(accounts[account]["widget"], row, col)
            if row >= max_rows:
                col += 1
                row = 0
            row += 1
        bottom_layout = pyqt.QHBoxLayout()
        group = pyqt.QGroupBox("Account")
        group.setMinimumHeight(200)

        group_layout = pyqt.QHBoxLayout()
        group.setLayout(group_layout)

        left_layout = pyqt.QVBoxLayout()
        self.account_image = NchantdImage(self, self.config).initWidget()
        left_layout.addWidget(self.account_image)
        cfg = {}
        self.account_name = NchantdEntryEditor(self, cfg).initWidget()
        left_layout.addWidget(self.account_name)
        cfg = {}
        self.account_address = NchantdEntryEditor(self, cfg).initWidget()
        left_layout.addWidget(self.account_address)
        cfg = {}
        self.institution = NchantdEntryEditor(self, cfg).initWidget()
        left_layout.addWidget(self.institution)
        group_layout.addLayout(left_layout)
        cfg = {}
        center_layout = pyqt.QVBoxLayout()
        self.account_description = NchantdEntryEditor(self, cfg).initWidget()
        center_layout.addWidget(self.account_description)
        group_layout.addLayout(center_layout)

        right_layout = pyqt.QVBoxLayout()
        right_top_layout = pyqt.QHBoxLayout()
        cfg = {}
        self.balance = NchantdEntryEditor(self, cfg).initWidget()
        right_top_layout.addWidget(self.balance)
        cfg = {}
        self.launch_account = NchantdButton(self, cfg).initWidget()
        right_top_layout.addWidget(self.launch_account)
        right_layout.addLayout(right_top_layout)
        cfg = {}
        self.recent_transactions = NchantdTable(self, cfg).initWidget()
        right_layout.addWidget(self.recent_transactions)
        group_layout.addLayout(right_layout)

        bottom_layout.addWidget(group)
        self.layout.addLayout(bottom_layout)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeJS(NchantdJS):
    """"""

    def __init__(self, cfg=None):
        """"""
        self.config = condor.Instruct(pxcfg).select("").override(cfg)

    def add_script(self, cmd):
        """"""
        wallet_connection_script = """
        (function() {
            // Check if window.ethereum is injected by Rabby Wallet
            if (typeof window.ethereum !== "undefined") {
                console.log("Rabby Wallet is detected.");

                // Request accounts to connect to the wallet
                window.ethereum.request({ method: "eth_requestAccounts" })
                .then(accounts => {
                    console.log("Connected account:", accounts[0]);
                })
                .catch(err => {
                    console.error("Error connecting to wallet:", err);
                });
            } else {
                console.error("Rabby Wallet is not detected.");
            }
        })();
        """
        # Execute JavaScript code
        self.web_view.page().runJavaScript(wallet_connection_script)


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
