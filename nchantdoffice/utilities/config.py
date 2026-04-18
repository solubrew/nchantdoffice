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
from pyffice.config.config import PyfficeConfig

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "config.yaml")


class PyfficeApplicationConfig(PyfficeConfig):
    """"""

    def __init__(self, cfg=None):
        """"""
        super().__init__(cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("PyfficeApplicationConfig")).override(cfg)
        self.interface_settings = None
        self.account_settings = None
        self.security_settings = None
        self.journal_settings = None
        self.storage_settings = None
        self.theme_settings = None

    def load_document(self, document=None):
        """"""
        if document is None:
            document = self.config.dikt.get("document", {})
            if document is None:
                document = {}
        super().load_document(document)
        self.set_interface_settings(document.get("interface_settings", {}))
        self.set_account_settings(document.get("account_settings", {}))
        self.set_security_settings(document.get("security_settings", {}))
        self.set_journal_settings(document.get("journal_settings", {}))
        self.set_storage_settings(document.get("storage_settings", {}))
        self.set_theme_settings(document.get("theme_settings", {}))
        return self

    def set_interface_settings(self, settings):
        """"""
        if settings != self.interface_settings:
            self.add_change("interface_settings", self.interface_settings, settings)
            self.interface_settings = settings
        return self

    def set_account_settings(self, settings):
        """"""
        if settings != self.account_settings:
            self.add_change("account_settings", self.account_settings, settings)
            self.account_settings = settings
        return self

    def set_security_settings(self, settings):
        """"""
        if settings != self.security_settings:
            self.add_change("security_settings", self.security_settings, settings)
            self.security_settings = settings
        return self

    def set_journal_settings(self, settings):
        """"""
        if settings != self.interface_settings:
            self.add_change("journal_settings", self.interface_settings, settings)
            self.interface_settings = settings
        return self

    def set_storage_settings(self, settings):
        """"""
        if settings != self.storage_settings:
            self.add_change("storage_settings", self.storage_settings, settings)
            self.storage_settings = settings
        return self

    def set_theme_settings(self, settings):
        """"""
        if settings != self.theme_settings:
            self.add_change("theme_settings", self.theme_settings, settings)
            self.theme_settings = settings
        return self

    def to_dict(self):
        """"""
        doc = super().to_dict()
        doc["data"] = {
            "content": {
                "interface_settings": self.interface_settings,
                "account_settings": self.account_settings,
                "security_settings": self.security_settings,
                "journal_settings": self.journal_settings,
                "storage_settings": self.storage_settings,
                "theme_settings": self.theme_settings,
            },
        }
        return doc


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
