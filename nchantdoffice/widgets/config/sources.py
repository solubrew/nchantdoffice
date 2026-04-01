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
from nchantrs.widgets.config.settings import NchantdSettingsWidget
from nchantrs.widgets.groups import NchantdHScrollGroupBox, NchantdVScrollGroupBox
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "sources.yaml")


class NchantdDataSourcesSettings(NchantdSettingsWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdDataSourcesSettings"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.primary_settings_group = None

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        cfg = {"size": ["auto", "auto"]}
        self.primary_settings_group = NchantdVScrollGroupBox(self, cfg)
        self.primary_settings_group.setTitle("Configure Data Sources")
        self.layout.addLayout(self.primary_settings_group.layout)
        # have a button for a file launch to mass load api keys from a file
        # have an import and an export button at top
        # then have apis list underneath that and remove the APIs tab
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
