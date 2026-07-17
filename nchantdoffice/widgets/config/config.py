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
from nchantrs.widgets.config.config import NchantdConfigStoreDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "config.yaml")


class NchantdOfficeConfigStoreDocument(NchantdConfigStoreDocument):
    """"""

    def __init__(self, cfg=None):
        """"""
        super().__init__(cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeConfigStoreDocument")).override(cfg)

    def load_document(self, document=None):
        """"""
        super().load_document(document)
        return self

    def set_settings_accounts(self, settings):
        """"""
        super().set_settings_accounts(settings)
        return self

    def set_settings_journal(self, settings):
        """"""
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
        return self

    def to_dict(self):
        """"""
        doc = super().to_dict()
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
