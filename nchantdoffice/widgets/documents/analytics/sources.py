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
from nchantrs.libraries import pyqt
from ogma.logma import Logma
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

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "sources.yaml")
pxcfg = {}


class NchantdOfficeSourceManager(NchantdOfficeDocumentManager):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.name = "Nchantd Data Source"
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeDataSourceManager"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
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
        }  # TODO: get table fields
        self.data_pane = NchantdDataSetPane(self, cfg).initWidget()
        self.canvas.add_item(self.data_pane, [50, 50])

    def cmd_add_dataset(self, event=None, *args, **kwargs):
        """"""
        self.add_dataset()
        return self

    def cmd_on_source_change(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_data_table_change(self, event=None, *args, **kwargs):
        """"""
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
        ls = self.sources["name_txt"].tolist()
        logma.info(f"List {ls}")
        return ls

    def get_source_table(self):
        """"""
        table = ""
        return table

    def get_source_tables(self, source):
        """"""
        return ["Supermarket", "CoinGecko"]

    def get_data_view(self):
        """"""
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

    def load_types(self):
        """"""
        table = "vw_chart_types"
        cfg = {}
        self.chart_types_df = self.app.model.store.get_table(table, cfg)
        return self

    def set_pane(self, pane=None):
        """"""
        if self.chart_config_pane is not None:
            widget = self.chart_config_pane
            self.layout.removeWidget(widget)
            widget.deleteLater()
            self.chart_config_pane = None
        if pane is None:
            pane = self.pane_type
        logma.info(f"Set Pane: {pane}")
        if pane == "config":
            cfg = {}
            self.chart_config_pane = NchantdChartConfigPane(self, cfg).initWidget()
        elif pane == "data":
            cfg = {}
            self.chart_config_pane = NchantdTable(self, cfg).initWidget()
        else:
            logma.info(f"Set Full Screen Chart")
        if self.chart_config_pane is not None:
            self.layout.insertWidget(2, self.chart_config_pane)
        self.update()

    def set_type(self, chart_type=None):
        """Switch between different chart types based on the selected option."""
        # # Remove the current chart
        # for i in reversed(range(self.chart_layout.count())):
        #     widget = self.chart_layout.itemAt(i).widget()
        #     self.chart_layout.removeWidget(widget)
        #     widget.deleteLater()
        # widget = self.layout.itemAt().widget()
        if self.chart is not None:
            widget = self.chart
            self.layout.removeWidget(widget)
            widget.deleteLater()
            self.chart = None
        # Add and display the selected chart
        if chart_type is None:
            chart_type = self.chart_type
        cfg = {"width": 6, "height": 5, "dpi": 100, "chart_type": chart_type}
        self.chart = NchantdChart(self, cfg).initWidget()
        self.layout.insertWidget(1, self.chart)
        self.update()

    # ====================================================================================================================||


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
