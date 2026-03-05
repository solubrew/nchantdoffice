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

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "trees.yaml")


class NchantdOfficeApplicationTree(TreeContextMenuMixin, NchantdWidget):
    """"""

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
        
        # Initialize context menu mixin for tree
        TreeContextMenuMixin.__init__(self)

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
        if self.tree and hasattr(self.tree, 'setDragEnabled'):
            self.tree.setDragEnabled(True)
        if self.tree and hasattr(self.tree, 'setAcceptDrops'):
            self.tree.setAcceptDrops(True)
        if self.tree and hasattr(self.tree, 'setDropIndicatorShown'):
            self.tree.setDropIndicatorShown(True)
        if self.tree and hasattr(self.tree, 'setDragDropMode'):
            self.tree.setDragDropMode(pyqt.QAbstractItemView.DragDrop)
        
        # Ensure the tree maintains selection highlight when not focused
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
        
        return self

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
