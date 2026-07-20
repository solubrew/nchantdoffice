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
import json

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from kahndor.logma import Logma
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.tables.tables import NchantdTable
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
from nchantrs.widgets.canvases.canvases import NchantdCanvas
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocumentManager
from nchantdoffice.widgets.panes.sources import NchantdDataSetPane, NchantdSourceDefaultPane, NchantdDataSetConfigPane
from nchantdoffice.widgets.panes.sources import NchantdWhereUsedListPane, NchantdViewPane, NchantdViewEditPane
from nchantdoffice.widgets.panes.sources import NchantdOfficeEDA, NchantdSourcesListPane
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.groups import NchantdVScrollGroupBox, NchantdHGroupBox
from nchantrs.widgets.annotations import NchantdLabel

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "sources.yaml")


class NchantdOfficeDataSourcesSettings(NchantdWidget):
    """"""

    def __init__(self, parent, cfg=None):
        """"""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdDataSourcesSettingsTab").override(cfg))
        self.data_sources = self.config.get("default_sources", {}) or {}
        self.apikeys = {}

    def initModel(self):
        """"""
        super().initModel()
        self.data_sources = self.get_sources()
        return self

    def initView(self):
        """"""
        super().initView()
        # need to a scroll
        cfg = {
            "text": "Available Data Sources",
            "size": ["auto", "auto"],
        }  # TODO: build in additional controls for size ["full", "%10"]}
        title = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(title)
        logma.info(f"Data Sources {self.data_sources}")
        sources = [dict(zip(list(self.data_sources.columns), x)) for x in self.data_sources.values.tolist()]
        nchantdsource = [x for x in sources if x["value_txt"] == "NchantdOffice"]
        # TODO: implement config changes to make the pane standout
        self.build_data_source_pane(nchantdsource[0])
        sources = [x for x in sources if x["value_txt"] != "NchantdOffice"]
        for source in sources:
            self.build_data_source_pane(source)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def build_data_source_pane(self, source):
        """"""
        logma.info(f"Source {source}")
        cfg = {"text": source["value_txt"]}
        source_group = NchantdHGroupBox(self, cfg).initWidget()
        source_group.setTitle(source["value_txt"])
        full_layout = pyqt.QVBoxLayout()
        layout = pyqt.QHBoxLayout()
        apikey = False
        if not apikey:
            cfg = {
                "text": "Get API Key",
                "handler": self.cmd_launch_site,
                "url": json.loads(source["parameters_dict"]).get("url"),
            }
            button = NchantdButton(self, cfg).initWidget()
            layout.addWidget(button)
        full_layout.addLayout(layout)
        layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft)
        # TODO: get apikey from pycurity and populate using an obscured version
        # key = PYKEYSTORE.get(source["value_txt"].lower()) #need to use the overall model store mechanism
        key = None
        cfg = {"label": "Enter API Key", "layout": "horizontal"}
        if key:
            cfg["label"] = "Active API Key"
            cfg["text"] = self.obscure_key(key)
            cfg["key"] = key
        self.apikeys[source["app_option_PK"]] = NchantdLabeledEntry(self, cfg).initWidget()
        layout = pyqt.QHBoxLayout()
        layout.addWidget(self.apikeys[source["app_option_PK"]])
        cfg = {"text": "..."}
        visibility_switch = NchantdButton(self, cfg).initWidget()
        layout.addWidget(visibility_switch)
        # TODO: add a visibliity switch at the end of the entry box
        full_layout.addLayout(layout)
        source_group.layout.addLayout(full_layout)
        self.layout.addWidget(source_group)

    def cmd_launch_site(self, event, *args, **kwargs):
        """"""
        btn = self.sender()
        url = btn.config.get("url", None)
        if url is None:
            raise Exception("No URL")
        # TODO: create a new NchantdOfficeWebBrowser Document
        #  also create a popup in the webbrowser document where the api key can be pasted and saved
        #  navigate to the url
        #  switch user to the new tab

    def get_sources(self):
        """"""
        return self.app.model.get_sources()

    def obscure_key(self, key):
        """"""
        return key[:3] + "..." + key[-3:]

    def show_key(self):
        """"""
        # TODO replace obscured key with real key


class NchantdOfficeSourceManager(NchantdOfficeDocumentManager):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.name = "Nchantd Data Source Manager"
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeDataSourceManager").override(cfg))
        self.canvas = None
        self.data_series = None
        self.source_select = None
        self.source_table_select = None
        self.data_pane = None
        self.source_config_pane = None

    def initModel(self):
        """"""
        super().initModel()
        self.document = self.app.model.codex.init_source_manager()
        self.document.load_document()
        self.context_menu.get_menu("document_data_context")
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        dss_cfg = {
            "label": "Source: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_sources()},
        }
        self.source_select = NchantdDropDown(self, dss_cfg).initWidget()
        dsvs_cfg = {
            "label": "Data Table: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_source_tables(self.get_source())},
        }
        self.source_table_select = NchantdDropDown(self, dsvs_cfg).initWidget()
        if cfg.get("buttons", None) is None:
            cfg["buttons"] = {}
        cfg["buttons"][0] = {"action": "show_config_pane", "type": "custom", "handler": self.cmd_toggle_config_pane}
        cfg["buttons"][1] = {
            "action": "insert_generic_action",
            "type": "custom",
            "widget": self.source_select,
        }
        cfg["buttons"][2] = {
            "action": "insert_generic_action",
            "type": "custom",
            "widget": self.source_table_select,
        }
        cfg["buttons"][3] = {"action": "add_source", "handler": self.cmd_add_dataset}
        cfg["buttons"][49] = "_insert_stretch"
        super().initView(cfg)
        cfg = {"size": ["auto", self.size().height() * (2 / 3) - 18]}
        self.canvas = NchantdCanvas(self, cfg).initWidget()
        self.layout.addWidget(self.canvas)
        self.add_dataset()
        cfg = {"size": ["auto", self.size().height() / 3 - 18]}
        self.source_config_pane = NchantdDataSetConfigPane(self, cfg).initWidget()
        self.layout.addWidget(self.source_config_pane)
        self.layout.setSpacing(3)
        self.layout.setContentsMargins(0, 0, 0, 0)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def add_dataset(self):
        """"""
        source = self.get_source()
        table = self.get_source_table()
        cfg = {
            "size": ["auto", 250],
            "datasource": source,
            "data_table": table,
            "fields": table,
        }  # NOTE: get table fields
        self.data_pane = NchantdDataSetPane(self, cfg).initWidget()
        self.canvas.add_item(self.data_pane, [50, 50])

    def cmd_add_dataset(self, event=None, *args, **kwargs):
        """"""
        self.add_dataset()
        return self

    def cmd_on_source_change(self, event=None, *args, **kwargs):
        """"""
        # TODO implement method
        return self

    def cmd_on_data_table_change(self, event=None, *args, **kwargs):
        """"""
        # TODO implement method
        return self

    def cmd_toggle_config_pane(self, event=None, *args, **kwargs):
        """"""
        self.set_pane("config")
        return self

    def cmd_toggle_full_screen_pane(self, event=None, *args, **kwargs):
        """"""
        self.set_pane("full")
        return self

    def cmd_toggle_data_pane(self, event=None, *args, **kwargs):
        """"""
        self.set_pane("data")
        return self

    def get_source(self):
        """"""
        self.source = "DictionaryAPI"
        return self.source

    def get_sources(self, full=False):
        """"""
        self.sources = self.app.model.get_sources()
        if full:
            return self.sources
        # ls = self.sources["name_txt"].tolist()
        #TODO fix
        # logma.info(f"List {ls}")
        ls = []
        return ls

    def get_source_table(self):
        """"""
        table = ""
        # TODO implement method
        return table

    def get_source_tables(self, source):
        """"""
        # TODO implement method
        return ["Supermarket", "CoinGecko"]

    def get_data_view(self):
        """"""
        # TODO implement method
        self.data_view = ""
        return self.data_view

    def get_data_view_fields(self):
        """"""
        fields = ["UUID", "Name", "Description", "Value", "CREON_DTTM", "MODON_DTTM", "CREBY_INT", "MODBY_INT"]
        return fields

    def init_drawer_source_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Set Default Source: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_sources()},
            "value": self.get_source(),
            "handler": self.cmd_on_source_change,
        }
        self.source_select = NchantdSourceDefaultPane(self, cfg)
        items[cnt]["widget"] = self.source_select
        cnt += 1
        # if cnt not in items:
        #     items[cnt] = default_action
        # cfg = {
        #     "label": "Set Default Table: ",
        #     "layout": "horizontal",
        #     "combobox": {"size": ["auto", "auto"], "options": self.get_source_tables(self.get_source())},
        #     "value": self.get_source_table(),
        #     "handler": self.cmd_on_data_table_change,
        # }
        # self.default_type_select = NchantdDropDown
        # items[cnt]["widget"] = self.default_type_select
        # cnt += 1
        return items

    def init_drawer_sources(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        # add a list of available sources with information on the api status of the source
        return items

    def init_drawer_connections(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        options = ["Node: Name"]
        cfg = {
            "label": "Chart Where Used: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
        }
        self.chart_where_used_list = NchantdWhereUsedListPane(self, cfg)
        items[cnt]["widget"] = self.chart_where_used_list
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        options = ["Node: Name"]
        cfg = {
            "label": "Chart Where Used: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
        }
        self.chart_sources_list = NchantdSourcesListPane(self, cfg)
        items[cnt]["widget"] = self.chart_sources_list
        cnt += 1
        return items

    def init_drawer_exploratory_data_analysis(self):
        """"""
        items = self.toolbox_config[400].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Data Source",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.data_source_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.data_source_select
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {"label": "Data Preview: ", "layout": "horizontal"}
        self.data_sources_edit_pane = NchantdSourceEditPane(self, cfg)
        items[cnt]["widget"] = self.data_sources_edit_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        options = ["Sweetviz", "Autoviz", "Pandas-Profiling", "Missingno"]
        cfg = {"label": "EDA", "layout": "horizontal", "options": options}
        self.eda_tool_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.eda_tool_select
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "text": "Run Exploratory Data Analysis",
            "layout": "horizontal",
            "size": None,
        }
        self.eda_run_button = NchantdButton(self, cfg)
        items[cnt]["widget"] = self.eda_run_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "text": "Create EDA on Node Branch",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.eda_placement_checkbox = NchantdCheckbox(self, cfg)
        items[cnt]["widget"] = self.eda_placement_checkbox
        cnt += 1
        return items

    def init_drawer_quickstart(self):
        """"""
        items = {}
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_source_config()
        self.toolbox_config[200]["items"] = self.init_drawer_sources()
        self.toolbox_config[300]["items"] = self.init_drawer_connections()
        self.toolbox_config[400]["items"] = self.init_drawer_exploratory_data_analysis()
        self.toolbox_config[500]["items"] = self.init_drawer_quickstart()


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
