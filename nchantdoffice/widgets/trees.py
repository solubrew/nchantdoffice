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
    document_selected = pyqt.Signal(object)  # NchantdOfficeDocument

    # Signal emitted when item drag starts
    item_drag_started = pyqt.Signal(object)  # tree item

    # Signal emitted when item is dropped on tree (internal reorder)
    item_dropped_on_tree = pyqt.Signal(object, object)  # source, target

    # Signal emitted when item is dropped on tabs (open document)
    item_dropped_on_tabs = pyqt.Signal(object)  # tree item

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"[trees] NchantdOfficeApplicationTree.__init__ parent={type(parent).__name__ if parent else None}")
        try:
            super().__init__(parent, cfg)
            self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeApplicationTree").override(cfg))
            self.tree = None
            self.image = None
            # Setup drag-drop
            self._setup_drag_drop()
        except Exception as e:
            logma.error(f"[trees] NchantdOfficeApplicationTree.__init__ failed: {e}", exc_info=True)
            raise

    def _setup_drag_drop(self):
        """Setup tree drag and drop"""
        logma.debug("[trees] _setup_drag_drop: delegated to underlying NchantdApplicationTree")
        pass  # Handled by underlying NchantdApplicationTree

    def initModel(self):
        """"""
        logma.info("[trees] initModel")
        try:
            super().initModel()
        except Exception as e:
            logma.error(f"[trees] initModel failed: {e}", exc_info=True)
            raise
        return self

    def initView(self):
        """"""
        logma.info("[trees] initView")
        try:
            super().initView()
            cfg = {"node_widget": NchantdOfficeTreeNode}
            self.tree = NchantdApplicationTree(self.parent, cfg).initWidget()
            logma.debug("[trees] initView: NchantdApplicationTree built")

            # Ensure the tree maintains selection highlight when not focused
            if hasattr(self.tree, "setSelectionMode"):
                self.tree.setSelectionMode(pyqt.QAbstractItemView.SingleSelection)
            if hasattr(self.tree, "setSelectionBehavior"):
                self.tree.setSelectionBehavior(pyqt.QAbstractItemView.SelectRows)

            # Connect tree selection to emit document_selected signal
            if hasattr(self.tree, 'selectionModel'):
                self.tree.selectionModel().selectionChanged.connect(self._on_tree_selection_changed)

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
            logma.info("[trees] initView: complete (tree + headshot image added)")
        except Exception as e:
            logma.error(f"[trees] initView failed: {e}", exc_info=True)
            raise
        return self

    def _on_tree_selection_changed(self, selected, deselected):
        """Handle tree selection change - emit document_selected signal"""
        if not hasattr(self.tree, "selectedItems"):
            return
        items = self.tree.selectedItems()
        if not items:
            return
        item = items[0]
        # Get document from tree item
        doc = item.data(0, pyqt.Qt.UserRole) if hasattr(item, "data") else None
        # [H32 2026-07-13] Safe None check: UserRole stores the node dict
        # (or a pandas Series from df.iterrows()), NOT a NchantdOfficeDocument.
        # The truthy `if doc` short-circuit raised ValueError on Series.
        # Documents are looked up via the tree model elsewhere; this signal
        # path won't emit from UserRole, but no longer crashes.
        logma.debug(f"[trees] _on_tree_selection_changed: doc_type={type(doc).__name__}")
        if doc is not None and isinstance(doc, NchantdOfficeDocument):
            logma.info(f"[trees] _on_tree_selection_changed: emitting document_selected for {doc}")
            self.document_selected.emit(doc)

    def mousePressEvent(self, event):
        """Start drag tracking"""
        if event.button() == pyqt.Qt.LeftButton:
            self._drag_start_pos = event.pos()
            logma.debug(f"[trees] mousePressEvent: drag_start pos={event.pos().x()},{event.pos().y()}")
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Initiate tree item drag"""
        if event.buttons() & pyqt.Qt.LeftButton:
            if hasattr(self, "_drag_start_pos"):
                diff = event.pos() - self._drag_start_pos
                if diff.manhattanLength() > pyqt.QApplication.startDragDistance():
                    logma.debug("[trees] mouseMoveEvent: drag distance exceeded")
                    self._initiate_item_drag()
        super().mouseMoveEvent(event)

    def _initiate_item_drag(self):
        """Start tree item drag"""
        selected_items = self.tree.selectedItems() if hasattr(self.tree, "selectedItems") else []
        if not selected_items:
            logma.debug("[trees] _initiate_item_drag: no selected items - skipping")
            return

        logma.info(f"[trees] _initiate_item_drag: {len(selected_items)} item(s)")

        # Emit drag started signal
        self.item_drag_started.emit(selected_items[0])

        # Create drag object
        drag = pyqt.QDrag(self)
        mime_data = pyqt.QMimeData()

        # [H29 2026-07-11] NchantdTreeNode.initModel now stores self.node dict
        # in UserRole. Nodes don't have .id — they have nid_txt. Read that
        # directly instead of chasing a non-existent attribute through doc.
        nids = []
        for item in selected_items:
            node_dict = item.data(0, pyqt.Qt.UserRole)
            if isinstance(node_dict, dict) and "nid_txt" in node_dict:
                nids.append(str(node_dict["nid_txt"]))

        if nids:
            mime_data.setData("application/x-nchantd-tree-item", ",".join(nids).encode())
            drag.setMimeData(mime_data)
            logma.debug(f"[trees] drag started with nids={nids}")
            drag.exec_(pyqt.Qt.MoveAction)
        else:
            logma.warning("[trees] _initiate_item_drag: no nid_txt in selected items - drag aborted")

    def dragEnterEvent(self, event):
        """Accept drag enter"""
        mime_data = event.mimeData()
        logma.debug(f"[trees] dragEnterEvent: has_tab={mime_data.hasFormat('application/x-nchantd-tab')} has_tree_item={mime_data.hasFormat('application/x-nchantd-tree-item')}")
        if mime_data.hasFormat("application/x-nchantd-tree-item"):
            event.acceptProposedAction()
        elif mime_data.hasFormat("application/x-nchantd-tab"):
            event.acceptProposedAction()
        super().dragEnterEvent(event)

    def dropEvent(self, event):
        """Handle drops on tree

        T-NEW-030: when a tab is dropped on a tree node, persist
        the new parent via ``cmd_set_tab_parent``. The target
        tree index is resolved via ``self.tree.indexAt(event.pos())``
        and the source tab's ``tid`` is recovered from the mime
        payload (the mime carries the source tab position; we
        look up the row in the tab model to get the ``tid_txt``).
        """
        mime_data = event.mimeData()

        if mime_data.hasFormat("application/x-nchantd-tab"):
            # Tab dropped on tree - persist the new parent.
            # Resolve the target tree item (new parent).
            target_index = self.tree.indexAt(event.pos()) if hasattr(self, "tree") else None
            target_nid = None
            if target_index is not None and target_index.isValid():
                # Look up the underlying data via the tree model.
                # The tree model exposes ``getNodeData(index)`` --
                # the row carries ``nid_txt`` as its primary key.
                try:
                    if hasattr(self.tree.model(), "getNodeData"):
                        data = self.tree.model().getNodeData(target_index)
                        target_nid = (
                            data.get("nid_txt")
                            if isinstance(data, dict)
                            else getattr(data, "nid", None)
                        )
                except Exception as e:
                    logma.warning(
                        f"[trees] dropEvent: target-node lookup "
                        f"failed ({type(e).__name__}: {e})"
                    )
            # Resolve the source tab's tid from the source position.
            tab_data = mime_data.data("application/x-nchantd-tab")
            try:
                source_index = int(tab_data.data().decode())
            except Exception:
                source_index = -1
            logma.info(
                f"[trees] dropEvent (tab): source_pos={source_index} "
                f"target_nid={target_nid!r}"
            )
            # Persist the new parent via the canonical model method
            # (records + columns dict shape, not the silent-no-op
            # "data" shape). Only call when both the source tid and
            # the target nid are available.
            self._handle_tab_dropped_on_node(source_index, target_nid)
            event.acceptProposedAction()

        elif mime_data.hasFormat("application/x-nchantd-tree-item"):
            logma.info("[trees] dropEvent (tree-item): reorder accepted")
            # Tree item reordered
            event.acceptProposedAction()

        super().dropEvent(event)

    def _handle_tab_dropped_on_node(self, source_tab_pos, target_nid):
        """T-NEW-030: persist the new parent for a tab dropped on
        a tree node. Resolves the source tab's ``tid_txt`` from
        the source position via the tab model, then calls
        ``cmd_set_tab_parent`` on the application model.

        Args:
            source_tab_pos: int -- the source tab's position in
                the tab model (from the mime payload). -1 if
                unparseable.
            target_nid: str -- the new parent node's ``nid_txt``.
                None if the drop landed on empty space (no target
                node) -- in that case the call is a no-op.
        """
        if source_tab_pos < 0 or target_nid is None:
            logma.debug(
                f"[trees] _handle_tab_dropped_on_node: skipping "
                f"(source_tab_pos={source_tab_pos} target_nid={target_nid!r})"
            )
            return
        # Resolve the source tab's tid from the tab model.
        # The app model exposes get_tab_documents or
        # current_tab; the tab itself has a tid_txt attribute.
        source_tid = None
        try:
            tab_model = None
            app = getattr(self, "app", None)
            if app is not None:
                view = getattr(app, "view", None)
                if view is not None and hasattr(view, "panes"):
                    for pane_key in ("center", "right"):
                        pane = view.panes.get(pane_key) if isinstance(view.panes, dict) else None
                        if pane is not None:
                            tm = getattr(pane, "model", None)
                            if tm is not None and hasattr(tm, "tabs"):
                                tab_model = tm
                                break
            if tab_model is not None and hasattr(tab_model, "tabs"):
                tabs = tab_model.tabs
                if 0 <= source_tab_pos < len(tabs):
                    tab_obj = tabs[source_tab_pos]
                    source_tid = (
                        tab_obj.get("tid_txt")
                        if isinstance(tab_obj, dict)
                        else getattr(tab_obj, "tid_txt", None) or getattr(tab_obj, "tid", None)
                    )
        except Exception as e:
            logma.warning(
                f"[trees] _handle_tab_dropped_on_node: source-tab "
                f"lookup failed ({type(e).__name__}: {e})"
            )
        if not source_tid:
            logma.debug(
                f"[trees] _handle_tab_dropped_on_node: could not "
                f"resolve source tab tid (source_tab_pos={source_tab_pos})"
            )
            return
        # Call the canonical model method (T-NEW-030).
        try:
            app = getattr(self, "app", None)
            model = getattr(app, "model", None) if app is not None else None
            if model is not None and hasattr(model, "cmd_set_tab_parent"):
                model.cmd_set_tab_parent(
                    {"tid_txt": source_tid},
                    {"nid_txt": target_nid},
                )
                logma.debug(
                    f"[trees] _handle_tab_dropped_on_node: persisted "
                    f"tab={source_tid!r} new_parent={target_nid!r}"
                )
        except Exception as e:
            logma.error(
                f"[trees] _handle_tab_dropped_on_node: persist failed "
                f"({type(e).__name__}: {e})",
                exc_info=True,
            )

    def initWidget(self, cfg=None):
        """"""
        logma.info("[trees] initWidget")
        try:
            self.initModel()
            self.initView()
        except Exception as e:
            logma.error(f"[trees] initWidget failed: {e}", exc_info=True)
            raise
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
