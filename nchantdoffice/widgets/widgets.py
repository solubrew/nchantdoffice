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
from condor import condor
from ogma.logma import Logma
from nchantrs.widgets.tabsets import NchantdTabSet
from nchantdoffice.models import NchantdOfficeTabSetModel
from nchantdoffice.widgets.controls.toolboxes import NchantdOfficeApplicationToolBox
from nchantdoffice.widgets.documents.media.notes import NchantdOfficeNote

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "widgets.yaml")


class NchantdOfficeTabSet(NchantdTabSet):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeTabSet")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
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

    def launch_note(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        note = NchantdOfficeNote(self.app.main, cfg).initWidget()
        self.app.view.panes["center"].model.current_tab.append_note(note)
        return self

    def create_toolbox(self, parent=None, cfg=None):
        """"""
        toolbox = NchantdOfficeApplicationToolBox(parent, cfg)
        toolbox.initWidget()
        return toolbox

    def setTabText(self, position, text, store=True):
        """"""
        super().setTabText(position, text)
        if store:
            cfg = {"name_txt": text}
            self.app.model.update_tab(self.app.model.get_current_tab(), cfg)

    def on_tab_focus(self, tabn=None):
        """"""
        if tabn is None:
            tabn = self.currentIndex()

        # check if it's the " + " tab (it won't be in model.tabsdata)
        if tabn >= 0 and tabn < len(self.model.tabsdata):
            widget = self.widget(tabn)
            if hasattr(widget, "dummy") and widget.dummy:
                logma.info(f"Loading Lazy Tab {tabn}")
                self.model.load_tab(self.model.tabsdata[tabn], tabn, self.pane_position)
                widget = self.widget(tabn)

            # Persist last selected tab
            if self.model.current_node:
                self.model.current_node.parameters["active_tab_position"] = tabn
                import json

                try:
                    self.app.model.update_node(
                        self.model.current_node, {"parameters_dict": json.dumps(self.model.current_node.parameters)}
                    )
                except Exception as e:
                    logma.error(f"Failed to persist active tab position: {e}")

            # WE want it to break if the toolbox is not in the right pane
            # this is a required functionality
            if self.app.view.panes["right"].toolbox is None:
                # TODO: this should be happening at this point
                self.app.view.panes["right"].toolbox = self.create_toolbox(self.app.view.panes["right"])
            self.app.view.panes["right"].toolbox.build_toolbox()

        # Ensure tabn is valid for super class to avoid IndexError in set_focus
        if tabn >= 0 and tabn <= len(self.model.tabsdata):
            super().on_tab_focus(tabn)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
