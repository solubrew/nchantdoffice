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
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.managers import NchantdManager
from nchantrs.widgets.groups import NchantdHScrollGroupBox, NchantdVScrollGroupBox
from pyffice.contacts.contacts import PyfficeContact, PyfficeRolodex

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "contacts.yaml")


class NchantdOfficeContact(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeContact")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)
        self.document = PyfficeContact()

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


class NchantdOfficeRolodex(NchantdManager):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        icfg = {}
        super().__init__(parent, icfg)
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeRolodex").override(cfg)
        self.contacts_group = None
        self.contact_likely_group = None

    def initModel(self):
        """"""
        super().initModel()
        self.document = PyfficeRolodex()  # self.app.model.store)
        return self

    def initView(self):
        """"""
        super().initView()
        self.contact_likely_group = NchantdHScrollGroupBox()
        self.contact_likely_group.setTitle(f"Most Likely Contacts")
        self.layout.addLayout(self.contact_likely_group.layout)
        self.contacts_group = NchantdVScrollGroupBox(self)
        self.contacts_group.setTitle(f"All Contacts")
        self.layout.addLayout(self.contacts_group.layout)
        if self.document.contacts is not None:
            for contact in self.document.contacts:
                contact_pane = self.add_contact(contact)
                self.contacts_group.addWidget(contact_pane)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def add_contact(self, contact):
        """"""
        contact_pane = NchantdOfficeContactPane(self).initWidget()
        return contact_pane


class NchantdOfficeContactPane(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeContactPane")
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
