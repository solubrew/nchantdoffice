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
from condor import condor
from ogma.logma import Logma
from nchantrs.widgets.tabsets import NchantdTab, NchantdTabSet

# ======================================Solutions Brewer Library Modules==============================================||
from nchantdoffice.widgets.menus.context_manager import TabContextMenuMixin
from nchantrs.libraries import pyqt

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")
pxcfg = {}


class NchantdOfficeTab(NchantdTab):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeTab"))
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

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeTabSet(TabContextMenuMixin, NchantdTabSet):
    """Tab set with right-click context menu support and document change signals."""
    
    # PyQt Signals
    current_document_changed = pyqtSignal(object)  # Emitted when current tab/document changes
    
    def __init__(self, parent=None, cfg=None):
        """Initialize tab set with context menu mixin"""
        self.parent = parent
        self.config = condor.Instruct(pxcfg)
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        
        # Initialize mixin first, then call parent
        TabContextMenuMixin.__init__(self)
        super().__init__(parent, self.config.instruct)
        
        # Set pane position for context menu type
        self.pane_position = cfg.get('pane_position', 'center') if cfg else 'center'
        
        # Connect tab change signal
        self._connect_tab_change_signal()
    
    def _connect_tab_change_signal(self):
        """Connect the tabset's currentChanged signal to our custom signal"""
        if hasattr(self, 'currentChanged'):
            self.currentChanged.connect(self._on_tab_changed)
    
    def _on_tab_changed(self, index):
        """Handle tab change - emit current_document_changed signal"""
        if index >= 0:
            widget = self.widget(index)
            if widget:
                self.current_document_changed.emit(widget)
                logma.info(f"Tab changed to: {type(widget).__name__}")
    
    def on_document_selected(self, document):
        """Handle document selected from tree.
        
        Args:
            document: The NchantdOfficeDocument to display
        """
        # Find and set the current tab to this document
        for i in range(self.count()):
            widget = self.widget(i)
            if widget == document or (hasattr(widget, 'did') and hasattr(document, 'did') and widget.did == document.did):
                self.setCurrentIndex(i)
                logma.info(f"Opened document from tree: {type(document).__name__}")
                return
        
        # If document not found as tab, add it
        if hasattr(document, 'initWidget'):
            document.initWidget()
        self.addTab(document, getattr(document, 'name', 'Untitled'))
        self.setCurrentWidget(document)


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
