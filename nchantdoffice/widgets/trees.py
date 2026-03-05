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

# ======================================3rd Party Library Modules======================================================||
from condor import condor
from ogma.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.media.images import NchantdImage
from nchantrs.widgets.trees import NchantdApplicationTree

# ======================================Solutions Brewer Library Modules==============================================||
from nchantdoffice.widgets.menus.context_manager import TreeContextMenuMixin
from nchantdoffice.widgets.items.items import NchantdOfficeTreeNode
from nchantrs.libraries import pyqt

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "trees.yaml")


class NchantdOfficeApplicationTree(TreeContextMenuMixin, NchantdWidget):
    """Application tree with context menu and document selection signals."""
    
    # PyQt Signals
    document_selected = pyqtSignal(object)  # Emitted when a document is selected in the tree
    item_drag_started = pyqtSignal(object)  # Emitted when tree item drag starts
    item_dropped = pyqtSignal(str, object)  # Emitted when item is dropped (source, data)
    
    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeApplicationTree"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.tree = None
        self.image = None
        self.tab_drop_enabled = True
        
        # Enable drag and drop
        self._enable_drag_drop()
        
        # Initialize context menu mixin for tree
        TreeContextMenuMixin.__init__(self)
    
    def _enable_drag_drop(self):
        """Enable drag and drop for tree nodes"""
        # This will be called after tree is created in initView
        pass

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        cfg = {"node_widget": NchantdOfficeTreeNode}
        self.tree = NchantdApplicationTree(self.parent, cfg).initWidget()

        # Enable drag and drop for tree node reorganization
        if self.tree:
            self._setup_tree_drag_drop()
        
        # Ensure the tree maintains selection highlight when not focused
        if self.tree:
            if hasattr(self.tree, "setSelectionMode"):
                self.tree.setSelectionMode(pyqt.QAbstractItemView.SingleSelection)
            if hasattr(self.tree, "setSelectionBehavior"):
                self.tree.setSelectionBehavior(pyqt.QAbstractItemView.SelectRows)

        self.layout.addWidget(self.tree)
        cfg = {
            "size": [250, 200],
            "path": join(self.app.view.themes_path, "_data_", "icons", "midnight_icons", "midnight-mist-headshot.svg"),
        }
        self.image = NchantdImage(self, cfg).initWidget()
        self.image.label.setFrameStyle(0)
        self.image.label.setStyleSheet("border: 0px;")
        self.layout.addWidget(self.image)
        self.layout.setAlignment(pyqt.Qt.AlignTop)
        
        # Connect tree drop handling for tab drops
        if self.tree and self.tab_drop_enabled:
            self._setup_tab_drop_handler()
        
        # Connect tree selection to emit document_selected signal
        if self.tree:
            self._connect_selection_signal()
        
        return self
    
    def _setup_tree_drag_drop(self):
        """Setup drag and drop on the tree widget"""
        if not self.tree:
            return
        
        # Enable drag
        if hasattr(self.tree, 'setDragEnabled'):
            self.tree.setDragEnabled(True)
        
        # Enable drop
        if hasattr(self.tree, 'setAcceptDrops'):
            self.tree.setAcceptDrops(True)
        
        # Show drop indicator
        if hasattr(self.tree, 'setDropIndicatorShown'):
            self.tree.setDropIndicatorShown(True)
        
        # Set drag drop mode
        if hasattr(self.tree, 'setDragDropMode'):
            self.tree.setDragDropMode(pyqt.QAbstractItemView.DragDrop)
        
        # Enable internal drag drop
        if hasattr(self.tree, 'setDefaultDropAction'):
            self.tree.setDefaultDropAction(pyqt.Qt.MoveAction)
        
        logma.info("Tree drag-drop enabled")
    
    def mousePressEvent(self, event):
        """Start drag tracking on mouse press"""
        if event.button() == pyqt.Qt.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Initiate tree item drag if moved past threshold"""
        if event.buttons() & pyqt.Qt.LeftButton:
            if hasattr(self, '_drag_start_pos'):
                diff = event.pos() - self._drag_start_pos
                if diff.manhattanLength() > pyqt.QApplication.startDragDistance():
                    self._initiate_tree_drag()
        super().mouseMoveEvent(event)
    
    def _initiate_tree_drag(self):
        """Start tree item drag operation"""
        if not self.tree:
            return
        
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        
        # Emit drag started signal
        self.item_drag_started.emit(selected_items[0])
        
        # Create drag object
        drag = pyqt.QDrag(self.tree)
        mime_data = pyqt.QMimeData()
        
        # Store document IDs
        doc_ids = []
        for item in selected_items:
            doc = item.data(0, pyqt.Qt.UserRole)
            if doc and hasattr(doc, 'did'):
                doc_ids.append(doc.did)
        
        if doc_ids:
            mime_data.setData('application/x-nchantd-tree-item', ','.join(doc_ids).encode())
            drag.setMimeData(mime_data)
            drag.exec_(pyqt.Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        """Accept drag enter from tabs and other tree items"""
        if event.mimeData().hasFormat('application/x-nchantd-tree-item'):
            event.acceptProposedAction()
        elif event.mimeData().hasFormat('application/x-nchantd-tab'):
            event.acceptProposedAction()
        super().dragEnterEvent(event)
    
    def dragMoveEvent(self, event):
        """Track drag move over tree"""
        if event.mimeData().hasFormat('application/x-nchantd-tree-item'):
            event.acceptProposedAction()
        elif event.mimeData().hasFormat('application/x-nchantd-tab'):
            event.acceptProposedAction()
        super().dragMoveEvent(event)
    
    def dropEvent(self, event):
        """Handle drops on tree"""
        mime_data = event.mimeData()
        
        if mime_data.hasFormat('application/x-nchantd-tab'):
            # Tab dropped on tree - create reference or link
            tab_data = mime_data.data('application/x-nchantd-tab').data()
            self.item_dropped.emit('tab', tab_data)
            event.acceptProposedAction()
            logma.info("Tab dropped on tree")
            
        elif mime_data.hasFormat('application/x-nchantd-tree-item'):
            # Tree item reordered - internal move
            event.acceptProposedAction()
            logma.info("Tree item reordered")
        
        super().dropEvent(event)
    
    def _connect_selection_signal(self):
        """Connect tree selection to emit document_selected signal"""
        if not self.tree:
            return
        
        # Connect to selection changed signal
        if hasattr(self.tree, 'selectionModel'):
            self.tree.selectionModel().selectionChanged.connect(self._on_selection_changed)
        elif hasattr(self.tree, 'itemSelectionChanged'):
            self.tree.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _on_selection_changed(self):
        """Handle tree selection change - emit document_selected signal"""
        selected = self.tree.selectedItems()
        if selected:
            item = selected[0]
            # Get the document from the tree item
            doc = item.data(0, pyqt.Qt.UserRole)
            if doc is not None:
                self.document_selected.emit(doc)
                logma.info(f"Tree document selected: {type(doc).__name__}")
    
    def on_document_created(self, doc_type):
        """Handle new document created from toolbar.
        
        Called when toolbar creates a new document.
        Updates tree and selects the new document.
        
        Args:
            doc_type: The type of document created
        """
        logma.info(f"Document created in tree: {doc_type}")
        # Refresh tree to show new document
        if hasattr(self, 'model') and hasattr(self.model, 'refresh'):
            self.model.refresh()
        
        # The new document will be selected via the center tab
        # Let the center tabset handle this

    def _setup_tab_drop_handler(self):
        """Setup custom drop handler for tabs"""
        if not self.tree:
            return
        
        # Store original drop event
        original_drop = self.tree.dropEvent
        
        def wrapped_drop_event(event):
            # Check if this is a tab drop
            if event.mimeData().hasFormat("application/x-tab-index"):
                self._handle_tab_drop(event)
                return
            if event.mimeData().hasText():
                try:
                    tab_data = eval(event.mimeData().text())
                    if isinstance(tab_data, dict) and "tab_index" in tab_data:
                        self._handle_tab_drop(event)
                        return
                except:
                    pass
            # Call original drop event for normal tree drops
            if original_drop:
                original_drop(event)
            else:
                super(NchantdApplicationTree, self.tree).dropEvent(event)
        
        self.tree.dropEvent = wrapped_drop_event

    def _handle_tab_drop(self, event):
        """Handle dropping a tab onto a tree node"""
        try:
            # Get tab data
            if event.mimeData().hasFormat("application/x-tab-index"):
                source_index = int(event.mimeData().data("application/x-tab-index").data().decode())
            else:
                tab_data = eval(event.mimeData().text())
                source_index = tab_data.get("tab_index", 0)
            
            # Find target tree node
            target_node = self._get_drop_target_node(event.pos())
            if target_node is None:
                event.ignore()
                return
            
            # Find source widget and transfer tab to node
            main_window = self.window()
            if hasattr(main_window, "tab_widgets"):
                for tab_widget in main_window.tab_widgets:
                    widget = tab_widget.widget(source_index)
                    if widget:
                        # Create a new node for this tab under the target
                        self._create_node_from_tab(target_node, widget, tab_widget.tabText(source_index))
                        event.acceptProposedAction()
                        logma.info(f"Dropped tab onto tree node: {target_node.name if hasattr(target_node, 'name') else 'unknown'}")
                        return
            
            event.ignore()
        except Exception as e:
            logma.info(f"Tab drop error: {e}")
            event.ignore()

    def _get_drop_target_node(self, pos):
        """Get the tree node at the drop position"""
        if not self.tree:
            return None
        index = self.tree.indexAt(pos)
        if not index.isValid():
            return None
        return self.tree.model().itemFromIndex(index)

    def _create_node_from_tab(self, parent_node, widget, tab_name):
        """Create a new tree node from a dropped tab"""
        logma.info(f"Creating node from tab: {tab_name}")
        if hasattr(self.tree.model(), "add_child_node"):
            self.tree.model().add_child_node(parent_node, tab_name, widget)
        return self

    def initWidget(self, cfg=None):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||
