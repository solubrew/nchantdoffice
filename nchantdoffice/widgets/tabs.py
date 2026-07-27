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
from nchantrs.libraries import pyqt
from nchantrs.libraries.pyqt import Signal, Slot

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.tabsets import NchantdTab, NchantdTabSet

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "tabs.yaml")


class NchantdOfficeTab(NchantdTab):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"[tabs] NchantdOfficeTab.__init__ parent={type(parent).__name__ if parent else None}")
        try:
            super().__init__(parent, cfg)
            self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeTab").override(cfg))
        except Exception as e:
            logma.error(f"[tabs] NchantdOfficeTab.__init__ failed: {e}", exc_info=True)
            raise

    def initModel(self, cfg=None):
        """"""
        logma.info(f"[tabs] NchantdOfficeTab.initModel cfg_provided={cfg is not None}")
        try:
            super().initModel(cfg)
        except Exception as e:
            logma.error(f"[tabs] NchantdOfficeTab.initModel failed: {e}", exc_info=True)
            raise
        return self

    def initView(self, cfg=None):
        """"""
        logma.info(f"[tabs] NchantdOfficeTab.initView cfg_provided={cfg is not None}")
        try:
            super().initView(cfg)
        except Exception as e:
            logma.error(f"[tabs] NchantdOfficeTab.initView failed: {e}", exc_info=True)
            raise
        return self

    def initWidget(self):
        """"""
        logma.info("[tabs] NchantdOfficeTab.initWidget")
        try:
            self.initModel()
            self.initView()
        except Exception as e:
            logma.error(f"[tabs] NchantdOfficeTab.initWidget failed: {e}", exc_info=True)
            raise
        return self


class NchantdOfficeTabs(NchantdTabSet):
    """Center pane tabs with drag-drop and document change signals"""

    # Signal emitted when active document changes
    current_document_changed = Signal(object)

    # Signal emitted when tab is moved
    tab_moved = Signal(int, int)  # old_index, new_index

    # Signal emitted when tab drag starts
    tab_drag_started = Signal(int)  # tab_index

    # Signal emitted when tab is dropped (from external source)
    tab_dropped = Signal(str, object)  # source, data

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"[tabs] NchantdOfficeTabs.__init__ parent={type(parent).__name__ if parent else None}")
        try:
            super().__init__(parent, cfg)
            self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeTabs").override(cfg))
            # Enable drag-drop
            self._setup_drag_drop()
            logma.info("[tabs] NchantdOfficeTabs.__init__: drag-drop enabled")
        except Exception as e:
            logma.error(f"[tabs] NchantdOfficeTabs.__init__ failed: {e}", exc_info=True)
            raise

    def _setup_drag_drop(self):
        """Setup drag and drop for tabs"""
        logma.info("[tabs] _setup_drag_drop")
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setUsesScrollButtons(True)

        # Tab bar settings for drag
        tab_bar = self.tabBar()
        if hasattr(tab_bar, "setMovable"):
            tab_bar.setMovable(True)
        if hasattr(tab_bar, "setDragable"):
            tab_bar.setDragable(True)

    def mousePressEvent(self, event):
        """Start drag tracking"""
        if event.button() == pyqt.Qt.LeftButton:
            self._drag_start_pos = event.pos()
            self._drag_start_index = self.tabBar().tabAt(event.pos()) if hasattr(self.tabBar(), "tabAt") else -1
            logma.debug(f"[tabs] mousePressEvent: drag_start index={self._drag_start_index}")
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Initiate drag if moved beyond threshold"""
        if event.buttons() & pyqt.Qt.LeftButton:
            if hasattr(self, "_drag_start_pos"):
                diff = event.pos() - self._drag_start_pos
                if diff.manhattanLength() > pyqt.QApplication.startDragDistance():
                    logma.debug("[tabs] mouseMoveEvent: drag distance exceeded - initiating drag")
                    self._initiate_tab_drag()
        super().mouseMoveEvent(event)

    def _initiate_tab_drag(self):
        """Start tab drag operation"""
        index = self._drag_start_index
        logma.info(f"[tabs] _initiate_tab_drag: index={index} tab_count={self.count()}")
        if 0 <= index < self.count():
            self.tab_drag_started.emit(index)

            # Create drag object
            drag = pyqt.QDrag(self)
            mime_data = pyqt.QMimeData()
            mime_data.setData("application/x-nchantd-tab", f"{index}".encode())
            drag.setMimeData(mime_data)

            # Execute drag
            result = drag.exec_(pyqt.Qt.MoveAction)
            if result == pyqt.Qt.MoveAction:
                logma.info(f"[tabs] drag completed: moved from {self._drag_start_index} to {self.currentIndex()}")
                self.tab_moved.emit(self._drag_start_index, self.currentIndex())
        else:
            logma.warning(f"[tabs] _initiate_tab_drag: invalid index {index} (count={self.count()})")

    def dragEnterEvent(self, event):
        """Accept drag enter from tabs and tree"""
        mime_data = event.mimeData()
        logma.debug(f"[tabs] dragEnterEvent: has_tab={mime_data.hasFormat('application/x-nchantd-tab')} has_tree={mime_data.hasFormat('application/x-nchantd-tree-item')}")
        if mime_data.hasFormat("application/x-nchantd-tab"):
            event.acceptProposedAction()
        elif mime_data.hasFormat("application/x-nchantd-tree-item"):
            event.acceptProposedAction()
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        """Track drag move"""
        if event.mimeData().hasFormat("application/x-nchantd-tab"):
            event.acceptProposedAction()
        super().dragMoveEvent(event)

    def dropEvent(self, event):
        """Handle tab/tree drops"""
        mime_data = event.mimeData()

        if mime_data.hasFormat("application/x-nchantd-tab"):
            # Tab dropped on another tab
            tab_data = mime_data.data("application/x-nchantd-tab")
            tab_index = int(tab_data.data().decode())
            target_index = self.tabBar().tabAt(event.pos()) if hasattr(self.tabBar(), "tabAt") else -1

            logma.info(f"[tabs] dropEvent (tab): source={tab_index} target={target_index}")
            if tab_index != target_index and target_index >= 0:
                self.tab_moved.emit(tab_index, target_index)

            event.acceptProposedAction()

        elif mime_data.hasFormat("application/x-nchantd-tree-item"):
            # Tree item dropped on tabs - open document
            item_data = mime_data.data("application/x-nchantd-tree-item")
            doc_id = item_data.data().decode()

            logma.info(f"[tabs] dropEvent (tree): doc_id={doc_id!r}")
            self.tab_dropped.emit("tree", doc_id)
            event.acceptProposedAction()

        super().dropEvent(event)

    def setCurrentWidget(self, widget):
        """Override to emit signal when current document changes"""
        super().setCurrentWidget(widget)
        if widget:
            logma.debug(f"[tabs] setCurrentWidget: current_document_changed emitted for {type(widget).__name__}")
            self.current_document_changed.emit(widget)

    def setCurrentIndex(self, index):
        """Override to emit signal when current index changes"""
        super().setCurrentIndex(index)
        widget = self.widget(index) if 0 <= index < self.count() else None
        if widget:
            logma.debug(f"[tabs] setCurrentIndex: index={index} emitting current_document_changed")
            self.current_document_changed.emit(widget)


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
