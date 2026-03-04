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
from os.path import abspath, dirname, join, exists
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||
# import numpy as np
# from scipy import sparse as sp

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from nchantrs.libraries import pyqt
from ogma.logma import Logma
from pyffice.charts.charts import PyfficeChart
from nchantdoffice.widgets.panes.charts import NchantdChartConfigPane
from nchantrs.widgets.media.charts.charts import NchantdChart
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.tables.lists import NchantdList
from nchantdoffice.widgets.panes.objects import NchantdNewObjectPane
from nchantrs.widgets.tables.tables import NchantdTable
from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
from nchantrs.widgets.groups import NchantdGroup

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
# logma.off()  # Disabled - causes dialog issues (P0 fix)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "charts.yaml")
pxcfg = {}


class NchantdSourcesListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdAlarmsListPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)

        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {"text": "Sources List:"}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"data": self.config.dikt.get("data", [])}
        self.layers_list = NchantdList(self, cfg).initWidget()
        layout.addWidget(self.layers_list)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdWhereUsedListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(self)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdAlarmsListPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {"text": "Where Used:"}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"data": self.config.dikt.get("data", [])}
        self.layers_list = NchantdList(self, cfg).initWidget()
        layout.addWidget(self.layers_list)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeChart(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Nchantd Chart", parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeChart"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.chart = None
        self.chart_type = None
        self.chart_config_pane = None
        self.data_source = None
        self.chart_types_df = None
        self.colors_df = None

    def initModel(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        super().initModel(cfg)
        cfg = {}
        self.document = self.app.model.codex.init_chart(cfg)
        self.document.load_document()
        self.context_menu.get_menu("document_chart_context")
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        dss_cfg = {
            "label": "Data Set: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_data_sources()},
        }
        self.chart_data_set_select = NchantdDropDown(self, dss_cfg).initWidget()
        dsvs_cfg = {
            "label": "Data View: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_data_views()},
        }
        self.chart_data_view_select = NchantdDropDown(self, dsvs_cfg).initWidget()
        if cfg.get("buttons", None) is None:
            cfg["buttons"] = {}
        cfg["buttons"][0] = {"action": "show_config_pane", "type": "custom", "handler": self.cmd_toggle_config_pane}
        cfg["buttons"][1] = {"action": "show_data_pane", "type": "custom", "handler": self.cmd_toggle_data_pane}
        cfg["buttons"][2] = {
            "action": "show_full_chart_pane",
            "type": "custom",
            "handler": self.cmd_toggle_full_screen_pane,
        }
        cfg["buttons"][3] = {
            "action": "insert_generic_action",
            "type": "custom",
            "widget": self.chart_data_set_select,
        }
        cfg["buttons"][4] = {
            "action": "insert_generic_action",
            "type": "custom",
            "widget": self.chart_data_view_select,
        }
        cfg["buttons"][5] = {
            "action": "add_data_view",
        }
        cfg["buttons"][49] = "_insert_stretch"
        super().initView(cfg)
        cfg = {}
        self.chart = NchantdChart(self, cfg).initWidget()
        self.layout.addWidget(self.chart)
        cfg = {"size": ["auto", 350]}
        self.chart_config_pane = NchantdChartConfigPane(self, cfg).initWidget()
        self.layout.addWidget(self.chart_config_pane)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_toggle_config_pane(self, event, *args, **kwargs):
        """"""
        self.set_pane("config")
        return self

    def cmd_toggle_data_pane(self, event, *args, **kwargs):
        """"""
        self.set_pane("data")
        return self

    def cmd_toggle_full_screen_pane(self, event, *args, **kwargs):
        """"""
        self.set_pane("full")
        return self

    def get_data_sources(self):
        """"""
        return ["Supermarket", "CoinGecko"]

    def get_data_views(self):
        """"""
        return ["Supermarket", "CoinGecko"]

    def get_themes(self):
        """"""
        return ["Light", "Dark"]

    def get_palettes(self):
        """"""
        return ["Default", "Dark"]

    def get_border_styles(self):
        """"""
        return ["Solid", "Dashed", "Dotted", "Double"]

    def get_types(self):
        """"""
        if self.chart_types_df is None:
            self.load_types()
        self.chart_types = self.chart_types_df["value_txt"].tolist()
        return self.chart_types

    def init_drawer_chart_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        options = ["Excel", "OpenOffice", "Nchantd Office", "Superset", "Plotly"]
        items[cnt]["widget_parameters"] = {
            "label": "Chart Compatibility: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
        }
        self.compatibility_select = NchantdDropDown
        items[cnt]["widget"] = self.compatibility_select
        cnt += 1

        if cnt not in items:
            items[cnt] = default_action
        items[cnt]["widget_parameters"] = {
            "label": "Select Default Chart Theme: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_themes()},
        }
        self.default_theme_select = NchantdDropDown
        items[cnt]["widget"] = self.default_theme_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        items[cnt]["widget_parameters"] = {
            "label": "Select Default Chart Palette: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_palettes()},
        }
        self.default_palette_select = NchantdDropDown
        items[cnt]["widget"] = self.default_palette_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        items[cnt]["widget_parameters"] = {
            "label": "Select Default Chart Type: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_types()},
        }
        self.default_type_select = NchantdDropDown
        items[cnt]["widget"] = self.default_type_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        items[cnt]["widget_parameters"] = {"layout": "horizontal"}
        self.chart_insert_object_pane = NchantdNewObjectPane
        items[cnt]["widget"] = self.chart_insert_object_pane
        cnt += 1
        return items

    def init_drawer_data_sources(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        options = ["Supermarket", "CoinGecko"]
        items[cnt]["widget_parameters"] = {
            "label": "Data Source: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
        }
        self.chart_data_sources_select = NchantdDropDown
        items[cnt]["widget"] = self.chart_data_sources_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        options = ["Supermarket", "CoinGecko"]
        items[cnt]["widget_parameters"] = {
            "label": "Data Source: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
        }
        self.chart_data_sources_edit_pane = NchantdSourceEditPane
        items[cnt]["widget"] = self.chart_data_sources_edit_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        data = [["SuperMarket"]]
        items[cnt]["widget_parameters"] = {"label": "Data Preview: ", "layout": "horizontal", "data": data}
        self.chart_sample_data = NchantdTable
        items[cnt]["widget"] = self.chart_sample_data
        cnt += 1
        return items

    def init_drawer_connections(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        options = ["Node: Name"]
        items[cnt]["widget_parameters"] = {
            "label": "Chart Where Used: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
        }
        self.chart_where_used_list = NchantdWhereUsedListPane
        items[cnt]["widget"] = self.chart_where_used_list
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        options = ["Node: Name"]
        items[cnt]["widget_parameters"] = {
            "label": "Chart Where Used: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
        }
        self.chart_sources_list = NchantdSourcesListPane
        items[cnt]["widget"] = self.chart_sources_list
        cnt += 1
        return items

    def init_drawer_quickstart(self):
        """"""
        items = {}
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_chart_config()
        self.toolbox_config[200]["items"] = self.init_drawer_data_sources()
        self.toolbox_config[300]["items"] = self.init_drawer_connections()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def load_types(self):
        """"""
        table = "vw_chart_types"
        cfg = {}
        self.chart_types_df = self.app.model.store.get_table(table, cfg)
        return self

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

    # ====================================================================================================================||


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
