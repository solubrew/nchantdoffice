# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid:
        name: NchantdOffice Configuration Module
        description: >
            Centralized configuration management for NchantdOffice.
            Provides constants, defaults, and configuration utilities.
        version: 0.0.0.0.0.0
        authority: filesystem
        security: seclvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*-
from __future__ import annotations
# ======================================Standard Library Modules======================================================||
from os.path import dirname, join
from typing import Any, Dict, Optional, Self

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


# class NchantdOfficeConfigStoreDocument(NchantdConfigStoreDocument):
#     """"""
#
#     def __init__(self, cfg=None):
#         """"""
#         super().__init__(cfg)
#         self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeConfigStoreDocument")).override(cfg)
#
#     def load_document(self, document=None):
#         """"""
#         super().load_document(document)
#         return self
#
#     def set_settings_accounts(self, settings):
#         """"""
#         super().set_settings_accounts(settings)
#         return self
#
#     def set_settings_journal(self, settings):
#         """"""
#         self.today_tabled_enable = True
#         self.daily_headlines_enable = True
#         self.weekly_weather_enable = True
#         self.store_journal_entries_betweeen_sessions = True
#         self.expire_history = True
#         self.expire_history_days = 30
#         self.journal_editor_enable = True
#         self.insert_date_per_focus = True
#         self.allow_edit_entry = True
#         self.allow_reedit_entry = True
#         return self
#
#     def to_dict(self):
#         """"""
#         doc = super().to_dict()
#         doc["today_tabled_enable"] = self.today_tabled_enable
#         doc["daily_headlines_enable"] = self.daily_headlines_enable
#         doc["weekly_weather_enable"] = self.weekly_weather_enable
#         doc["store_journal_entries_betweeen_sessions"] = self.store_journal_entries_betweeen_sessions
#         doc["expire_history"] = self.expire_history
#         doc["expire_history_days"] = self.expire_history_days
#         doc["journal_editor_enable"] = self.journal_editor_enable
#         doc["insert_date_per_focus"] = self.insert_date_per_focus
#         doc["allow_edit_entry"] = self.allow_edit_entry
#         doc["allow_reedit_entry"] = self.allow_reedit_entry
#         return doc


class NchantdOfficeBrowserConfig(PyfficeConfig):
    """"""

    def __init__(self, cfg=None, parent=None) -> None:
        """"""
        super().__init__(cfg, parent)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeBrowserConfig").override(cfg))
        self.home_page = self.config.get("home_page", "https://www.nchantdoffice.com")
        logma.info(f"[config] NchantdOfficeBrowserConfig.__init__: home_page={self.home_page!r}")

    def get_home_page(self) -> Optional[str]:
        """"""
        logma.info(f"[config] NchantdOfficeBrowserConfig.get_home_page: returning {getattr(self, 'home_page', None)!r}")
        return getattr(self, "home_page", None)


class PyfficeApplicationConfig(PyfficeConfig):
    """Define and control Pyffice Codex and ohter Pyffice Document Settings"""

    def __init__(self, cfg=None, parent=None) -> None:
        """"""
        super().__init__(cfg, parent)
        try:
            self.app = self.parent.app
        except Exception as e:
            logma.warning(f"[config] PyfficeApplicationConfig.__init__: parent has no app ({e}) - app=None")
            self.app = None
        self.config.override(kahndor.Instruct(pxcfg).select("PyfficeApplicationConfig").override(cfg))
        self.account_settings = {}
        self.interface_settings = {}
        self.journal_settings = {}
        self.security_settings = {}
        self.storage_settings = {}
        self.theme_settings = {}
        logma.info("[config] PyfficeApplicationConfig.__init__: section dicts initialised")

    def load_document(self, document=None) -> Self:
        """"""
        logma.info(f"[config] PyfficeApplicationConfig.load_document: document_provided={document is not None}")
        try:
            if document is None:
                document = self.config.dikt.get("document", {})
                if document is None:
                    logma.warning("[config] PyfficeApplicationConfig.load_document: config.dikt['document'] is None - using empty dict")
                    document = {}
            super().load_document(document)
            logma.info("[config] PyfficeApplicationConfig.load_document: super().load_document complete")
        except Exception as e:
            logma.error(f"[config] PyfficeApplicationConfig.load_document failed: {e}", exc_info=True)
            raise
        return self

    def set_settings_journal(self, settings) -> Self:
        """"""
        logma.info("[config] PyfficeApplicationConfig.set_settings_journal: enabling all journal flags")
        self.today_tabled_enable = True
        self.daily_headlines_enable = True
        self.weekly_weather_enable = True
        self.store_journal_entries_betweeen_sessions = True
        self.expire_history = True
        self.expire_history_days = 30
        self.journal_editor_enable = True
        self.insert_date_per_focus = True
        self.allow_edit_entry = True
        self.allow_reedit_entry = True
        logma.debug(f"[config] set_settings_journal: applied settings={settings!r}")
        return self

    def to_dict(self) -> Dict[str, Any]:
        """"""
        logma.debug("[config] PyfficeApplicationConfig.to_dict: serialising all settings sections")
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
        doc["today_tabled_enable"] = self.today_tabled_enable
        doc["daily_headlines_enable"] = self.daily_headlines_enable
        doc["weekly_weather_enable"] = self.weekly_weather_enable
        doc["store_journal_entries_betweeen_sessions"] = self.store_journal_entries_betweeen_sessions
        doc["expire_history"] = self.expire_history
        doc["expire_history_days"] = self.expire_history_days
        doc["journal_editor_enable"] = self.journal_editor_enable
        doc["insert_date_per_focus"] = self.insert_date_per_focus
        doc["allow_edit_entry"] = self.allow_edit_entry
        doc["allow_reedit_entry"] = self.allow_reedit_entry
        return doc


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
