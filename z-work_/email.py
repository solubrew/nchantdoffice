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
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument, NchantdOfficeDocumentManager
from nchantrs.widgets.groups import NchantdVScrollGroupBox
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from pyffice.email.email import PyfficeMailBox

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "email.yaml")


class NchantdOfficeMailBox(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.Instruct(pxcfg).select("NchantdOfficeMailBox")
        if self.parent:
            self.config.override(parent.config)
        super().__init__("Nchantd Mail", self)
        self.config.override(cfg)
        self.document = PyfficeMailBox
        self.communication_important_group = None
        self.communication_accounts_group = None
        self.reader_group = None
        self.mail_toolbar = None

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        cfg = {}
        self.mail_toolbar = NchantdButtonBar(self, cfg).initWidget()
        self.layout.addWidget(self.mail_toolbar)
        self.communication_important_group = NchantdVScrollGroupBox()
        self.communication_important_group.setTitle("Important Communications")
        self.layout.addLayout(self.communication_important_group.layout)

        # # layout = pyqt.QVBoxLayout()
        # self.communication_accounts_group = NchantdVScrollGroupBox()
        # self.communication_accounts_group.setTitle("Accounts")
        # self.layout.addLayout(self.communication_accounts_group.layout)
        # self.layout.addLayout(layout)
        self.reader_group = NchantdVScrollGroupBox()
        self.reader_group.setTitle("Reader")
        self.layout.addLayout(self.reader_group.layout)
        # if there is no connection to the selected service then start with a connection pane
        # if there is a presaved connection then start with a pane of options for filtering labels/mails/etc
        # if the connection is already there and filters are already set then show the update mail selection
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeMailManager(NchantdOfficeDocumentManager):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.Instruct(pxcfg).select("Nchantd")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)

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


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
