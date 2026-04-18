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
from nchantrs.widgets.widgets import NchantdWidget
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "accounts.yaml")


class NchantdNewApplicationDialog(NchantdWidget):
    """"""

    def __init__(self, parent, cfg=None):
        """"""
        self.config = kahndor.instruct(pxcfg)
        if parent is not None:
            self.config.override(parent.config)
        self.parent = parent
        self.config.override(cfg)
        super().__init__(parent, self.config)

    def initModel(self):
        """"""

    def initView(self):
        """"""

    def initWidget(self):
        """"""


class NchantdNewAccountEntry(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdNewAccountEntry")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super().__init__(self.parent, self.config)
        self.address = None
        self.description = None
        self.email = None
        self.icon = None
        self.name = None
        self.username = None
        self.uuid = None

    def initModel(self):
        """"""
        super().initModel()
        self.uuid = Thing().uuid
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self, pos=0):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdNewInstanceDialog(NchantdWidget):
    """"""

    def __init__(self, parent, cfg=None):
        """"""
        self.config = kahndor.instruct(pxcfg)
        if parent is not None:
            self.config.override(parent.config)
        self.parent = parent
        self.config.override(cfg)
        super(NchantdNewInstanceDialog, self).__init__(parent, self.config)

    def initModel(self):
        """"""

    def initView(self):
        """"""

    def initWidget(self):
        """"""


class NchantdSelectInstanceDialog(NchantdWidget):
    def __init__(self, parent, cfg=None):
        """"""
        self.config = kahndor.instruct(pxcfg)
        if parent is not None:
            self.config.override(parent.config)
        self.parent = parent
        self.config.override(cfg)
        super(NchantdSelectInstanceDialog, self).__init__(parent, self.config)

    def initModel(self):
        """"""

    def initView(self):
        """"""

    def initWidget(self):
        """"""


class NchantdNewNchantrsAccount(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("Nchantd")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super().__init__(self.parent, self.config)

    def initModel(self):
        """"""
        return self

    def initView(self):
        """"""
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
