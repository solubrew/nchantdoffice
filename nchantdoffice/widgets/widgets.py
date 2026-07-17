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
                logma.info(f"Loading Lazy Tab {tabn}")
                self.model.load_tab(self.model.tabsdata[tabn], tabn, self.pane_position)
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

        # Ensure tabn is valid for super class to avoid IndexError in set_focus
        # TODO BUG [off-by-one]: tabset tab selection is off by one in certain sequences.
        # NOTE: keep this TODO OPEN for user to debug.
        # Suspect area: the boundary check above uses `<= len(...)` here while the
        # earlier `tabn < len(self.model.tabsdata)` uses strict `<`. The asymmetry
        # can shift selection by one when tabs are added/removed or when the
        # " + " dummy tab is at index len(tabsdata). Reproduce by:
        #   1) open N tabs, 2) click the " + " tab to add a new doc, 3) close it,
        #   4) observe selection lands on tabn-1 instead of the previously active tab.
        # Do NOT change the comparison operator until the sequence is reproduced
        # under logma debug capture from on_tab_focus and load_tab.
        if tabn >= 0 and tabn <= len(self.model.tabsdata) - 1:
            super().on_tab_focus(tabn)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
