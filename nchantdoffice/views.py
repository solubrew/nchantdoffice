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
from functools import lru_cache

# ======================================3rd Party Library Modules=====================================================||
# Lazy imports for heavy modules - loaded on demand
# import pandas as pd  # Lazy loaded
# import matplotlib  # Lazy loaded
# import seaborn  # Lazy loaded

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from nchantrs.views.applicationviews import NchantdCloakView
from ogma.logma import Logma

# Lazy import toolbar to avoid loading heavy widgets at startup
_toolbar_cache = None

def _get_toolbar():
    """Lazy load toolbar to improve startup performance"""
    global _toolbar_cache
    if _toolbar_cache is None:
        from nchantdoffice.widgets.controls.toolbars import NchantdNewDocumentToolBar
        _toolbar_cache = NchantdNewDocumentToolBar
    return _toolbar_cache

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "views.yaml")
pxcfg = {}


class NchantdOfficeCloakView(NchantdCloakView):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, None)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeCloakView").override(cfg))
        if self.parent:
            self.config.override(parent.config)

    def initView(self):
        """"""
        super().init_pre_view()
        cfg = {}
        # Use lazy loaded toolbar for faster startup
        ToolBar = _get_toolbar()
        self.panes["toolbar"] = ToolBar(self.parent, cfg).initWidget()
        super().initView()
        return self

    @lru_cache(maxsize=32)
    def get_theme_cache(self, theme_name):
        """Cache theme lookups for performance"""
        return self.config.dikt.get(f"themes.{theme_name}", {})

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
