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
from kahndor import kahndor
from nchantrs.views.applicationviews import NchantdCloakView
from nchantdoffice.widgets.controls.toolbars import (
    NchantdNewDocumentToolBar,
)
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "views.yaml")


class NchantdOfficeCloakView(NchantdCloakView):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, None)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeCloakView").override(cfg))

    def initView(self, cfg=None):
        """"""
        super().init_pre_view(cfg)
        cfg = {}
        self.panes["toolbar"] = NchantdNewDocumentToolBar(self.parent, cfg).initWidget()
        super().initView(cfg)
        return self

    def switch_to_account_tab(self):
        """"""
        return self

    def on_window_move(self, event):
        """"""
        # need to move any visible notes at the same time as the main application
        # self.panes["center"].model.current_tab.on_window_move(event)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
