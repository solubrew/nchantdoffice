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
from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.media.images import NchantdImage
from nchantrs.widgets.trees import NchantdApplicationTree
from nchantdoffice.widgets.items.items import NchantdOfficeTreeNode
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "trees.yaml")


class NchantdOfficeApplicationTree(NchantdWidget):
    """Left pane tree with drag-drop and document selection signals"""

    # Signal emitted when a document is selected in the tree
    document_selected = Signal(object)  # NchantdOfficeDocument

    # Signal emitted when item drag starts
    item_drag_started = Signal(object)  # tree item

    # Signal emitted when item is dropped on tree (internal reorder)
    item_dropped_on_tree = Signal(object, object)  # source, target

    # Signal emitted when item is dropped on tabs (open document)
    item_dropped_on_tabs = Signal(object)  # tree item

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeApplicationTree").override(cfg))
        self.tree = None
        self.image = None

        # Setup drag-drop
        self._setup_drag_drop()

    def _setup_drag_drop(self):
        """Setup tree drag and drop"""
        pass  # Handled by underlying NchantdApplicationTree

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        cfg = {"node_widget": NchantdOfficeTreeNode}
        self.tree = NchantdApplicationTree(self.parent, cfg).initWidget()

        # Ensure the tree maintains selection highlight when not focused
        if hasattr(self.tree, "setSelectionMode"):
            self.tree.setSelectionMode(pyqt.QAbstractItemView.SingleSelection)
        if hasattr(self.tree, "setSelectionBehavior"):
            self.tree.setSelectionBehavior(pyqt.QAbstractItemView.SelectRows)

        # TODO:2 selection issue
        # Connect tree selection to emit document_selected signal
        # if hasattr(self.tree, 'selectionChanged'):
        # self.tree.selectionChanged.connect(self._on_tree_selection_changed)

        # Setup drag on tree
        if hasattr(self.tree, "setDragEnabled"):
            self.tree.setDragEnabled(True)
        if hasattr(self.tree, "setAcceptDrops"):
            self.tree.setAcceptDrops(True)
        if hasattr(self.tree, "setDragDropMode"):
            self.tree.setDragDropMode(pyqt.QAbstractItemView.DragDrop)
        if hasattr(self.tree, "setDefaultDropAction"):
            self.tree.setDefaultDropAction(pyqt.Qt.MoveAction)

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
        return self

    def _on_tree_selection_changed(self, selected, deselected):
        """Handle tree selection change - emit document_selected signal"""
        if hasattr(self.tree, "selectedItems"):
            items = self.tree.selectedItems()
            if items:
                item = items[0]
                # Get document from tree item
                doc = item.data(0, pyqt.Qt.UserRole) if hasattr(item, "data") else None
                if doc and isinstance(doc, NchantdOfficeDocument):
                    self.document_selected.emit(doc)

    def mousePressEvent(self, event):
        """Start drag tracking"""
        if event.button() == pyqt.Qt.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Initiate tree item drag"""
        if event.buttons() & pyqt.Qt.LeftButton:
            if hasattr(self, "_drag_start_pos"):
                diff = event.pos() - self._drag_start_pos
                if diff.manhattanLength() > pyqt.QApplication.startDragDistance():
                    self._initiate_item_drag()
        super().mouseMoveEvent(event)

    def _initiate_item_drag(self):
        """Start tree item drag"""
        selected_items = self.tree.selectedItems() if hasattr(self.tree, "selectedItems") else []
        if not selected_items:
            return

        # Emit drag started signal
        self.item_drag_started.emit(selected_items[0])

        # Create drag object
        drag = pyqt.QDrag(self)
        mime_data = pyqt.QMimeData()

        # Store document IDs
        doc_ids = []
        for item in selected_items:
            doc = item.data(0, pyqt.Qt.UserRole) if hasattr(item, "data") else None
            if doc and hasattr(doc, "id"):
                doc_ids.append(str(doc.id))

        if doc_ids:
            mime_data.setData("application/x-nchantd-tree-item", ",".join(doc_ids).encode())
            drag.setMimeData(mime_data)
            drag.exec_(pyqt.Qt.MoveAction)

    def dragEnterEvent(self, event):
        """Accept drag enter"""
        mime_data = event.mimeData()
        if mime_data.hasFormat("application/x-nchantd-tree-item"):
            event.acceptProposedAction()
        elif mime_data.hasFormat("application/x-nchantd-tab"):
            event.acceptProposedAction()
        super().dragEnterEvent(event)

    def dropEvent(self, event):
        """Handle drops on tree"""
        mime_data = event.mimeData()

        if mime_data.hasFormat("application/x-nchantd-tab"):
            # Tab dropped on tree - create reference or open
            tab_data = mime_data.data("application/x-nchantd-tab")
            self.item_dropped_on_tabs.emit(tab_data)
            event.acceptProposedAction()

        elif mime_data.hasFormat("application/x-nchantd-tree-item"):
            # Tree item reordered
            event.acceptProposedAction()

        super().dropEvent(event)

    def initWidget(self, cfg=None):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
