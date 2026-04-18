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
from nchantrs.libraries import pyqt

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from pyffice.document import PyfficeContact

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "../_data_", "contacts.yaml")


class NchantdOfficeContact(NchantdOfficeDocument, PyfficeContact):
    """Contact document - implements PyfficeContact"""

    PYTYPE = "contact"

    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for contact documents"""
        return [
            {"id": "add", "icon": "user-plus", "label": "Add Contact", "method": "add_contact"},
            {"id": "edit", "icon": "edit", "label": "Edit", "method": "edit_contact"},
            {"id": "delete", "icon": "trash", "label": "Delete", "method": "delete_contact"},
            {"id": "group", "icon": "users", "label": "Group", "method": "manage_groups"},
            {"id": "search", "icon": "search", "label": "Search", "method": "search_contacts"},
        ]

    def __init__(self, name="Nchantd Contact", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeContact"))
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
        return self

    def initWidget(self, cfg=None):
        """"""
        self.initModel(cfg)
        self.initView(cfg)
        return self

    def add_contact(self):
        """Add contact"""
        logma.info("Adding contact...")
        return self

    def edit_contact(self):
        """Edit contact"""
        logma.info("Editing contact...")
        return self

    def delete_contact(self):
        """Delete contact"""
        logma.info("Deleting contact...")
        return self

    def manage_groups(self):
        """Manage groups"""
        logma.info("Managing groups...")
        return self

    def search_contacts(self):
        """Search contacts"""
        logma.info("Searching contacts...")
        return self


# ====================================================================================================================||
