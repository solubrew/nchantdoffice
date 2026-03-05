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
    tab_moved = pyqtSignal(int, int)  # Emitted when tab is moved (old_index, new_index)
    tab_dropped = pyqtSignal(str, object)  # Emitted when external item dropped (source_type, data)
    
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
        
        # Enable drag and drop
        self._setup_drag_drop()
        
        # Connect tab change signal
        self._connect_tab_change_signal()
    
    def _connect_tab_change_signal(self):
        """Connect the tabset's currentChanged signal to our custom signal"""
        if hasattr(self, 'currentChanged'):
            self.currentChanged.connect(self._on_tab_changed)
    
    def _setup_drag_drop(self):
        """Setup drag and drop for tab reordering"""
        # Enable drag and drop on the tab widget
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setMovable(True)
        self.setTabsClosable(True)
        
        # Enable drag on tab bar
        tab_bar = self.tabBar()
        if tab_bar:
            tab_bar.setMovable(True)
            tab_bar.setDragEnabled(True)
            tab_bar.setAcceptDrops(True)
    
    def mousePressEvent(self, event):
        """Start drag tracking on mouse press"""
        if event.button() == pyqt.Qt.LeftButton:
            self._drag_start_pos = event.pos()
            self._drag_start_index = self.tabBar().tabAt(event.pos()) if self.tabBar() else -1
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Initiate drag if moved past threshold"""
        if event.buttons() & pyqt.Qt.LeftButton:
            if hasattr(self, '_drag_start_pos'):
                diff = event.pos() - self._drag_start_pos
                if diff.manhattanLength() > pyqt.QApplication.startDragDistance():
                    self._initiate_tab_drag()
        super().mouseMoveEvent(event)
    
    def _initiate_tab_drag(self):
        """Start tab drag operation"""
        index = getattr(self, '_drag_start_index', -1)
        if 0 <= index < self.count():
            # Emit signal that drag started
            self.tab_moved.emit(index, self.currentIndex())
            
            # Create drag object for cross-pane communication
            drag = pyqt.QDrag(self)
            mime_data = pyqt.QMimeData()
            mime_data.setData('application/x-nchantd-tab', f'{index}'.encode())
            drag.setMimeData(mime_data)
            drag.exec_(pyqt.Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        """Accept drag enter from tabs and tree items"""
        if event.mimeData().hasFormat('application/x-nchantd-tab'):
            event.acceptProposedAction()
        elif event.mimeData().hasFormat('application/x-nchantd-tree-item'):
            event.acceptProposedAction()
        elif event.mimeData().hasText():
            # Handle legacy text format
            event.acceptProposedAction()
        super().dragEnterEvent(event)
    
    def dragMoveEvent(self, event):
        """Track drag move"""
        if event.mimeData().hasFormat('application/x-nchantd-tab'):
            event.acceptProposedAction()
        elif event.mimeData().hasFormat('application/x-nchantd-tree-item'):
            event.acceptProposedAction()
        super().dragMoveEvent(event)
    
    def dropEvent(self, event):
        """Handle tab or tree item drop"""
        mime_data = event.mimeData()
        
        if mime_data.hasFormat('application/x-nchantd-tab'):
            # Tab dropped on this tabset
            try:
                source_index = int(mime_data.data('application/x-nchantd-tab').data().decode())
                target_index = self.tabBar().tabAt(event.pos()) if self.tabBar() else -1
                
                if source_index != target_index and target_index >= 0:
                    # Reorder tabs
                    self.tabBar().moveTab(source_index, target_index)
                    self.tab_moved.emit(source_index, target_index)
                
                event.acceptProposedAction()
            except Exception as e:
                logma.warning(f"Tab drop error: {e}")
                
        elif mime_data.hasFormat('application/x-nchantd-tree-item'):
            # Tree item dropped on tabs - emit signal for cross-pane handling
            item_data = mime_data.data('application/x-nchantd-tree-item').data()
            self.tab_dropped.emit('tree', item_data)
            event.acceptProposedAction()
            
        elif mime_data.hasText():
            # Legacy text format
            try:
                text = mime_data.text()
                if text.startswith('tab:'):
                    tab_data = eval(text.replace('tab:', ''))
                    if isinstance(tab_data, dict) and 'tab_index' in tab_data:
                        self.tab_dropped.emit('legacy', tab_data)
                event.acceptProposedAction()
            except Exception as e:
                logma.warning(f"Legacy drop error: {e}")
        
        super().dropEvent(event)
    
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
