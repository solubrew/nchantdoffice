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
        # Size-control selector ("Full", "50%", "10%") so the user
        # can collapse the data-source list when not in use.
        size_cfg = {
            "label": "Pane Size:",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "combobox": {
                "size": [120, 30],
                "options": ["Full", "50%", "10%"],
            },
            "value": self.config.dikt.get("data_source_pane_size", "Full"),
            "handler": self.cmd_change_data_source_pane_size,
        }
        size_row = pyqt.QHBoxLayout()
        size_label = NchantdLabel(self, size_cfg).initWidget()
        size_row.addWidget(size_label)
        self.data_source_size_combo = NchantdDropDown(self, size_cfg).initWidget()
        size_row.addWidget(self.data_source_size_combo)
        size_row.addStretch()
        self.layout.addLayout(size_row)

        # Standout title with bold accent so the pane draws the eye
        cfg = {
            "text": "Available Data Sources",
            "size": ["auto", "auto"],
            "stylesheet": "font-weight: bold; font-size: 14pt; color: #1f4e79; padding: 6px;",
        }
        title = NchantdLabel(self, cfg).initWidget()
        title.setStyleSheet(cfg["stylesheet"])
        self.layout.addWidget(title)
        logma.info(f"Data Sources {self.data_sources}")
        sources = [dict(zip(list(self.data_sources.columns), x)) for x in self.data_sources.values.tolist()]
        nchantdsource = [x for x in sources if x["value_txt"] == "NchantdOffice"]
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
        # Pull the API key from the pycurity keystore (obscured).
        # Falls back to None when pycurity isn't available or the
        # key isn't stored yet.
        key = self._load_api_key(source)
        cfg = {"label": "Enter API Key", "layout": "horizontal"}
        if key:
            cfg["label"] = "Active API Key"
            cfg["text"] = self.obscure_key(key)
            cfg["key"] = key
        self.apikeys[source["app_option_PK"]] = NchantdLabeledEntry(self, cfg).initWidget()
        layout = pyqt.QHBoxLayout()
        layout.addWidget(self.apikeys[source["app_option_PK"]])
        cfg = {
            "text": "Show",
            "handler": self.cmd_toggle_apikey_visibility,
            "apikey_id": source["app_option_PK"],
        }
        visibility_switch = NchantdButton(self, cfg).initWidget()
        layout.addWidget(visibility_switch)
        full_layout.addLayout(layout)
        source_group.layout.addLayout(full_layout)
        self.layout.addWidget(source_group)

    def cmd_launch_site(self, event=None, *args, **kwargs):
        """Open the source's API-key URL in a new WebBrowser document.

        Reads the URL from the sender widget's config, creates a new
        ``NchantdOfficeWebBrowser`` document via the application
        model (when supported), navigates the new tab to the URL,
        and switches the active tab so the user can paste the
        API key.

        Returns ``self`` for chainable call sites.
        """
        try:
            btn = self.sender() if event is None else event
            if btn is None:
                return self
            url = None
            if hasattr(btn, "config"):
                url = (btn.config or {}).get("url") if hasattr(btn.config, "get") else None
            if url is None:
                logma.warning("[config_sources] cmd_launch_site: no URL configured")
                return self

            # Create a new browser document via the app model
            model = getattr(self.app, "model", None)
            if model is None or not hasattr(model, "codex") or not hasattr(model.codex, "init_browser"):
                logma.warning("[config_sources] cmd_launch_site: app model does not support browser init")
                return self

            document_cfg = {"document": {"url": url}}
            browser = model.codex.init_browser(document_cfg)
            if browser is None:
                logma.warning("[config_sources] cmd_launch_site: browser init returned None")
                return self

            # Navigate the new browser to the URL
            if hasattr(browser, "setUrl"):
                try:
                    from PySide6 import QtCore
                    browser.setUrl(QtCore.QUrl(url))
                except Exception:
                    if hasattr(browser, "load_url"):
                        browser.load_url(url)

            # Switch the active tab to the new browser
            if hasattr(self.app, "view") and hasattr(self.app.view, "switch_to_tab"):
                try:
                    self.app.view.switch_to_tab(browser)
                except Exception as e:
                    logma.error(f"[config_sources] switch_to_tab failed: {e}", exc_info=True)
        except Exception as e:
            logma.error(f"[config_sources] cmd_launch_site failed: {e}", exc_info=True)
        return self

    def get_sources(self):
        """"""
        return self.app.model.get_sources()

    def obscure_key(self, key):
        """"""
        return key[:3] + "..." + key[-3:]

    def show_key(self, event=None, *args, **kwargs):
        """Show all API keys in plain text by iterating the apikeys dict.

        For each entry that has a ``key`` config attribute, replaces
        the obscured text with the full key. Returns ``self``.
        """
        try:
            for apikey_id, entry in self.apikeys.items():
                key = getattr(entry.config, "get", lambda k: None)("key")
                if key and hasattr(entry, "setText"):
                    entry.setText(key)
        except Exception as e:
            logma.error(f"[config_sources] show_key failed: {e}", exc_info=True)
        return self
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

    def _ensure_drawer_item(self, items, cnt):
        """Return items[cnt], lazily creating the default slot.

        Centralises the "if cnt not in items: items[cnt] = {...}`` pattern
        used by every drawer initialiser, removing the repeated branch
        that the maintainability auditor flags as switch abuse.
        """
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        return items[cnt]

    def init_drawer_exploratory_data_analysis(self):
        """Build the Exploratory Data Analysis (EDA) drawer."""
        items = self.toolbox_config[400].get("items", {})
        cnt = 0

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.data_source_select = NchantdDropDown(
            self,
            {
                "label": "Data Source",
                "layout": "horizontal",
                "size": ["auto", "auto"],
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.data_sources_edit_pane = NchantdSourceEditPane(
            self,
            {"label": "Data Preview: ", "layout": "horizontal"},
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.eda_tool_select = NchantdDropDown(
            self,
            {
                "label": "EDA",
                "layout": "horizontal",
                "options": ["Sweetviz", "Autoviz", "Pandas-Profiling", "Missingno"],
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.eda_run_button = NchantdButton(
            self,
            {
                "text": "Run Exploratory Data Analysis",
                "layout": "horizontal",
                "size": None,
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.eda_placement_checkbox = NchantdCheckbox(
            self,
            {
                "text": "Create EDA on Node Branch",
                "layout": "horizontal",
                "size": ["auto", "auto"],
            },
        )
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
