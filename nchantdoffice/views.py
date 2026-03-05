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
        
        # Enable drag and drop for center app tabs
        center_tabset = self.panes.get("center")
        if center_tabset and hasattr(center_tabset, 'init_drag_drop'):
            center_tabset.init_drag_drop()
        
        # Enable drag and drop for right pane (toolbox)
        right_tabset = self.panes.get("right")
        if right_tabset and hasattr(right_tabset, 'init_drag_drop'):
            right_tabset.init_drag_drop()
        
        super().initView()
        
        # Connect signals for toolbar → tree → tabs → toolbox flow
        self._connect_pane_signals()
        
        return self
    
    def _connect_pane_signals(self):
        """Connect signals between panes for document flow.
        
        Flow: toolbar (new document) → tree (document selected) → tabs (document open) → toolbox (tools update)
        """
        toolbar = self.panes.get("toolbar")
        tree = self.panes.get("left")
        center = self.panes.get("center")
        toolbox = self.panes.get("right")
        
        # Connect toolbar document_created to tree
        if toolbar and hasattr(toolbar, 'document_created'):
            if tree and hasattr(tree, 'on_document_created'):
                toolbar.document_created.connect(tree.on_document_created)
            logma.info("Connected toolbar.document_created")
        
        # Connect tree document_selected to center tabs
        if tree and hasattr(tree, 'document_selected'):
            if center and hasattr(center, 'on_document_selected'):
                tree.document_selected.connect(center.on_document_selected)
            logma.info("Connected tree.document_selected")
        
        # Connect center tab change to toolbox
        if center and hasattr(center, 'current_document_changed'):
            if toolbox and hasattr(toolbox, 'on_document_changed'):
                center.current_document_changed.connect(toolbox.on_document_changed)
            logma.info("Connected center.current_document_changed")
        
        # Also connect tree selection to toolbox directly
        if tree and hasattr(tree, 'document_selected'):
            if toolbox and hasattr(toolbox, 'on_document_changed'):
                tree.document_selected.connect(toolbox.on_document_changed)
        
        # Connect toolbar directly to toolbox for new documents
        if toolbar and hasattr(toolbar, 'document_created'):
            if toolbox and hasattr(toolbox, 'on_document_created'):
                toolbar.document_created.connect(toolbox.on_document_created)
        
        logma.info("All pane signals connected")
    
    def init_drag_drop(self):
        """Initialize drag and drop for tabset widgets"""
        if hasattr(self, 'setAcceptDrops'):
            self.setAcceptDrops(True)
        if hasattr(self, 'setMovable'):
            self.setMovable(True)
        if hasattr(self, 'setDragEnabled'):
            self.setDragEnabled(True)
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
