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
from nchantrs.widgets.tabsets import NchantdTabSet
from nchantrs.libraries.pyqt import QTimer
from nchantdoffice.models import NchantdOfficeTabSetModel
from nchantdoffice.widgets.controls.toolboxes import NchantdOfficeApplicationToolBox

# from nchantdoffice.widgets.documents.media.notes import NchantdOfficeNote

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = False
logma = Logma(__name__)
if not log:
    logma.off()
# ====================================================================================================================||
pxcfg = join(here, "_data_", "widgets.yaml")


class NchantdOfficeTabSet(NchantdTabSet):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeTabSet").override(cfg))
        self.model = NchantdOfficeTabSetModel(self, self.config)

    def initModel(self, create_objects=True):
        """"""
        super().initModel(create_objects)
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        self.initModel(cfg.get("create_objects", True))
        self.initView()
        return self

    # PUSH to 0.0.3
    # def launch_note(self, cfg=None):
    #     """"""
    #     if cfg is None:
    #         cfg = {}
    #     # TODO BUG FIX: need to fix the Note object
    #     # note = NchantdOfficeNote(self.app.main, cfg).initWidget()
    #     note = NchantdOfficeNote(self, cfg).initWidget()
    #     self.app.view.panes["center"].model.current_tab.append_note(note)
    #     return self

    def create_toolbox(self, parent=None, cfg=None):
        """"""
        toolbox = NchantdOfficeApplicationToolBox(parent, cfg)
        toolbox.initWidget()
        return toolbox

    def go_to_previous_tab(self):
        """"""
        # TODO implement method

    def setTabText(self, position, text, store=True):
        """"""
        super().setTabText(position, text)
        if store:
            cfg = {"name_txt": text}
            self.app.model.update_tab(self.app.model.get_current_tab(), cfg)

    def on_tab_focus(self, tabn=None):
        """"""
        logma.inspect_caller()
        if tabn is None:
            tabn = self.currentIndex()

        logma.info(f"on_tab_focus: tabn={tabn}, pane={self.pane_position}")

        # check if it's the " + " tab (it won't be in model.tabsdata)
        if tabn >= 0 and tabn < len(self.model.tabsdata):
            widget = self.widget(tabn)
            if hasattr(widget, "dummy") and widget.dummy:
                # [off-by-one FIX] Materializing a lazy tab replaces the dummy via
                # removeTab(tabn)+insertTab(tabn, real_widget) (QTabWidget has no
                # replace-in-place). Two Qt side effects broke first-click focus:
                #   1) insertTab at an index <= the current index increments Qt's
                #      currentIndex, shifting the visible page off the clicked tab.
                #   2) base removeTab() unblocks signals at its end, so the shift in
                #      (1) re-fires currentChanged -> re-enters on_tab_focus for the
                #      wrong (shifted) index, lazily loading a tab nobody clicked.
                # This is why the first click landed one tab away and only the second
                # click (dummy already materialized) showed the right tab.
                # The guard swallows the re-entrant signal; the outer call restores
                # the current index (signals blocked) to the tab the user clicked.
                if getattr(self, "_materializing_tab", False):
                    return self
                logma.info(f"Loading Lazy Tab {tabn}")
                self._materializing_tab = True
                try:
                    self.model.load_tab(self.model.tabsdata[tabn], tabn, self.pane_position)
                    if self.currentIndex() != tabn:
                        self.blockSignals(True)
                        self.setCurrentIndex(tabn)
                        self.blockSignals(False)
                finally:
                    self._materializing_tab = False
                widget = self.widget(tabn)

            # Persist last selected tab
            # if self.model.current_node:
            #     self.model.current_node.parameters["active_tab_position"] = tabn
            #     import json
            #
            #     try:
            #         self.app.model.update_node(
            #             self.model.current_node, {"parameters_dict": json.dumps(self.model.current_node.parameters)}
            #         )
            #     except Exception as e:
            #         logma.error(f"Failed to persist active tab position: {e}")

            # H24 FIX: Lazy-init toolbox — create once, reuse on subsequent tab switches.
            # Previously this block ran unconditionally, destroying toolbox state
            # (search queries, filter results, selected items) on every tab switch.
            right_pane = self.app.view.panes.get("right")
            if not hasattr(right_pane, "toolbox") or right_pane.toolbox is None:
                logma.info("Creating toolbox in right pane")
                right_pane.toolbox = self.create_toolbox(right_pane)
                logma.info("Building toolbox")
                right_pane.toolbox.build_toolbox()
            else:
                logma.info("Reusing existing toolbox in right pane")
                # H24 FIX: Deferred refresh using QTimer.singleShot to ensure widget is fully initialized
                # before updating toolbox drawer items for the active document context
                QTimer.singleShot(0, lambda: right_pane.toolbox.refresh_for_document(widget))

            # H24 FIX: Wire toolbox to current_document_changed signal for automatic refresh
            # when document changes via other mechanisms (drag-drop, API calls)
            if not hasattr(right_pane, "toolbox_signal_connected") or not right_pane.toolbox_signal_connected:
                if hasattr(self.parent, "current_document_changed"):
                    self.parent.current_document_changed.connect(
                        lambda doc: QTimer.singleShot(0, lambda: right_pane.toolbox.refresh_for_document(doc))
                    )
                    right_pane.toolbox_signal_connected = True
                    logma.info("Wired toolbox to current_document_changed signal")

        # Ensure tabn is valid for super class to avoid IndexError in set_focus.
        # RESOLVED [off-by-one]: the first-click-off-by-one on center/right tabsets
        # was caused by lazy-tab materialization shifting Qt's currentIndex (see the
        # restore in the dummy-load branch above), NOT by this boundary check. The
        # `<= len - 1` guard below is equivalent to the earlier strict `<` check and
        # is intentionally kept.
        if tabn >= 0 and tabn <= len(self.model.tabsdata) - 1:
            super().on_tab_focus(tabn)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
