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
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.groups import NchantdGroup
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.dialogs.colors import NchantdColorSelectSigil
from nchantrs.dialogs.files import NchantdFileOpenSigil
from nchantrs.widgets.controls.button_groups import NchantdFontConfigBar
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons, NchantdOkButtons
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.media.editors.editors import NchantdEntryBox
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.controls.buttons import NchantdButton

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class NchantdOfficeSearchPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeNodeEditPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {"text": "Node: "}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {
            "layout": "horizontal",
            "actions": {
                0: {"action": "duplicate_document", "type": "", "handler": self.cmd_duplicate_document},
                # 1: {"action": "import_document", "type": "", "handler": self.cmd_import_file},
                # 2: {"action": "export_document", "type": "", "handler": self.cmd_export_document},
                2: {"action": "take_snapshot", "handler": self.cmd_take_snapshot},
                3: {
                    "action": "sort_children_ascending",
                    "type": "",
                    "handler": self.cmd_sort_children,
                    "args": "ascending",
                },
                4: {
                    "action": "sort_children_descending",
                    "type": "",
                    "handler": self.cmd_sort_children,
                    "args": "descending",
                },
                5: {"action": "delete_node", "type": "", "handler": self.cmd_delete_node},
            },
            "size": ["auto", 30],
        }
        self.node_buttonbar = NchantdButtonBar(self, cfg).initWidget()
        layout.addWidget(self.node_buttonbar)

        node = self.get_node()
        # logma.info(f"Node {dir(node)} {node.name}")
        logma.info(f"Node {node.item} {node.name}")
        cfg = {"label": "Node Name: ", "value": node.item}
        if node.node_type in ("displaynode", "sysorgnode", "yearnode", "monthnode", "daynode"):
            cfg["readonly"] = True
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)

        cfg = {"label": "Node Position: ", "value": node.position}
        if node.node_type in ("displaynode", "sysorgnode", "yearnode", "monthnode", "daynode"):
            cfg["readonly"] = True
        self.position_entry = NchantdLabeledSpinBox(self, cfg).initWidget()
        layout.addWidget(self.position_entry)

        cfg = {"show_label": False, "layout": "horizontal", "two_rows": True, "size": ["auto", "auto"]}
        self.font_bar = NchantdFontConfigBar(self, cfg).initWidget()
        layout.addWidget(self.font_bar)
        cfg = {"buttons": {"ok": {"handler": self.cmd_set_node_name}}}
        self.accept_button = NchantdOkButtons(self, cfg).initWidget()
        layout.addWidget(self.accept_button)
        # self.tags = self.get_tags()
        # tags_label = NchantdLabel(self, {"text": "Tags: "}).initWidget()
        # layout.addWidget(tags_label)
        # TODO: add tag tracking
        # cfg = {"data": self.tags}
        # self.tags_list = NchantdList(self, cfg).initWidget()
        # layout.addWidget(self.tags_list)
        group.set_height(layout.sizeHint().height() * 1.2)
        self.layout.addWidget(group)

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdApplicationSearchPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdApplicationSearchPane").override(cfg))
        self.handler = self.config.dikt.get("handler", None)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        options = ["This Tab", "This Node", "This Instance", "Journal", "Web", "LLM"]
        cfg = {"label": "Search Focus", "layout": "horizontal", "options": options}
        self.search_area_select = NchantdDropDown(self, cfg).initWidget()
        self.layout.addWidget(self.search_area_select)
        cfg = {
            "layout": "vertical",
            "size": ["auto", 100],
        }
        self.application_search_entry = NchantdEntryBox(self, cfg).initWidget()
        logma.info(f"application_search_entry {self.application_search_entry.size().height()}")
        self.application_search_entry.setMinimumHeight(self.application_search_entry.size().height())
        self.layout.addWidget(self.application_search_entry)
        cfg = {"text": "Run Search", "layout": "horizontal"}
        self.search_button = NchantdButton(self, cfg).initWidget()
        self.layout.addWidget(self.search_button)
        cfg = {
            "layout": "vertical",
            "size": ["auto", 450],
        }
        self.application_response_area = NchantdEntryBox(self, cfg).initWidget()
        self.application_response_area.setMinimumHeight(cfg["size"][1])
        self.layout.addWidget(self.application_response_area)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdLLMQueryPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdLLMQueryPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        options = ["Open Ai", "Grok", "Gemini", "Claude"]
        cfg = {"label": "Set Default LLM", "layout": "horizontal", "options": options}
        self.default_llm_engine_select = NchantdDropDown(self, cfg).initWidget()
        self.layout.addWidget(self.default_llm_engine_select)
        cfg = {
            "label": "Query Model: ",
            "layout": "vertical",
            "options": options,
            "size": ["auto", 150],
        }
        self.llm_query_entry = NchantdEntryBox(self, cfg).initWidget()
        self.layout.addWidget(self.llm_query_entry)
        cfg = {"text": "Query", "layout": "horizontal"}
        self.search_llm_button = NchantdButton(self, cfg).initWidget()
        self.layout.addWidget(self.search_llm_button)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdWebSearchPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdWebSearchPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        options = ["Google", "DuckDuckGo", "Bing", "Yahoo", "Yandex", "PreSearch", "Shodan"]
        cfg = {"label": "Set Default Search", "layout": "horizontal", "options": options}
        self.default_search_engine_select = NchantdDropDown(self, cfg).initWidget()
        self.layout.addWidget(self.default_search_engine_select)
        cfg = {
            "label": "Search Web: ",
            "layout": "vertical",
            "options": options,
            "size": ["auto", 50],
        }
        self.application_search_entry = NchantdEntryBox(self, cfg).initWidget()
        self.layout.addWidget(self.application_search_entry)
        cfg = {"text": "Search Web", "layout": "horizontal"}
        self.search_web_button = NchantdButton(self, cfg).initWidget()
        self.layout.addWidget(self.search_web_button)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
