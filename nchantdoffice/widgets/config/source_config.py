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
from __future__ import annotations

# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from typing import Any, Self
from os.path import abspath, dirname, join
import datetime as dt
import json

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from kahndor.logma import Logma
from nchantrs.widgets.controls.buttons import NchantdButtonWidget, NchantdButton
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.tables.tables import NchantdTable
from nchantrs.widgets.controls.checkboxes import NchantdCheckboxWidget
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

    def __init__(self, parent, cfg=None) -> None:
        """"""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeDataSourcesSettings").override(cfg))
        self.data_sources = self.config.get("default_sources", {}) or {}
        self.apikeys = {}

    def initModel(self) -> Self:
        """"""
        super().initModel()
        self.data_sources = self.get_sources()
        return self

    def initView(self) -> Self:
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

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_change_data_source_pane_size(self, event=None, *args, **kwargs) -> Self:
        """Resize the data-source list pane based on the dropdown selection.

        Reads ``self.data_source_size_combo.currentText()`` (one of
        "Full", "50%", "10%"), persists the value to
        ``config.dikt["data_source_pane_size"]``, and resizes
        the parent splitter / pane. Defensive: when the combo
        is missing or the parent has no splitter, the handler
        logs + swallows rather than crashing.

        Returns ``self`` for chainable call sites (Sprint 23
        config-flag pattern).
        """
        try:
            combo = getattr(self, "data_source_size_combo", None)
            if combo is None:
                logma.debug(
                    "[config_sources] cmd_change_data_source_pane_size: "
                    "no combo available; skipping"
                )
                return self
            value = combo.currentText() if hasattr(combo, "currentText") else "Full"
            self.config.dikt["data_source_pane_size"] = value
            parent = getattr(self, "parent", None)
            if parent is not None:
                splitter = getattr(parent, "splitter", None)
                if splitter is not None:
                    stretch_map = {"Full": 100, "50%": 50, "10%": 10}
                    stretch = stretch_map.get(value, 100)
                    try:
                        splitter.setStretchFactor(0, stretch)
                    except Exception:
                        pass
            logma.debug(
                f"[config_sources] cmd_change_data_source_pane_size: "
                f"value={value!r}"
            )
        except Exception as e:
            logma.error(
                f"[config_sources] cmd_change_data_source_pane_size "
                f"failed: {e}",
                exc_info=True,
            )
        return self

    def build_data_source_pane(self, source) -> None:
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

    def cmd_toggle_apikey_visibility(self, event=None, *args, **kwargs) -> Self:
        """Toggle the echo mode of the API key entry for the
        source identified by ``event.config.dikt["apikey_id"]``.

        When the entry's ``QLineEdit`` is in ``Password`` mode
        (obscured), switches to ``Normal`` (visible). When in
        ``Normal``, switches to ``Password``.

        Defensive: when ``event`` is None, ``apikey_id`` is
        missing, or the entry doesn't exist in
        ``self.apikeys``, the handler logs + swallows rather
        than raising.

        Returns ``self`` for chainable call sites.
        """
        try:
            if event is None:
                return self
            event_cfg = getattr(event, "config", None)
            dikt = getattr(event_cfg, "dikt", None) or {}
            apikey_id = dikt.get("apikey_id")
            if not apikey_id:
                logma.debug(
                    "[config_sources] cmd_toggle_apikey_visibility: "
                    "no apikey_id in event; skipping"
                )
                return self
            entry = self.apikeys.get(apikey_id)
            if entry is None:
                logma.debug(
                    f"[config_sources] cmd_toggle_apikey_visibility: "
                    f"no entry for apikey_id={apikey_id!r}; skipping"
                )
                return self
            textbox = getattr(entry, "textbox", None)
            if textbox is None:
                return self
            from PySide6.QtWidgets import QLineEdit
            current_mode = textbox.echoMode()
            if current_mode == QLineEdit.EchoMode.Password:
                textbox.setEchoMode(QLineEdit.EchoMode.Normal)
            else:
                textbox.setEchoMode(QLineEdit.EchoMode.Password)
            logma.debug(
                f"[config_sources] cmd_toggle_apikey_visibility: "
                f"toggled apikey_id={apikey_id!r}"
            )
        except Exception as e:
            logma.error(
                f"[config_sources] cmd_toggle_apikey_visibility "
                f"failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_launch_site(self, event=None, *args, **kwargs) -> Self:
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

    def get_sources(self) -> Any:
        """"""
        return self.app.model.get_sources()

    def _load_api_key(self, source=None) -> Any:
        """"""
        # TODO implement method

    def obscure_key(self, key) -> str:
        """"""
        return key[:3] + "..." + key[-3:]

    def show_key(self, event=None, *args, **kwargs) -> Self:
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


class NchantdOfficeSourceManager(NchantdOfficeDocumentManager):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
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

    def initModel(self) -> Self:
        """"""
        super().initModel()
        self.document = self.app.model.codex.init_source_manager()
        self.document.load_document()
        self.context_menu.get_menu("document_data_context")
        return self

    def initView(self, cfg=None) -> Self:
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
        # cfg["buttons"][10] = {"action": "show_config_pane", "type": "custom", "handler": self.cmd_toggle_config_pane}
        cfg["buttons"][11] = {
            "action": "insert_generic_action",
            "type": "custom",
            "widget": self.source_select,
        }
        cfg["buttons"][12] = {
            "action": "insert_generic_action",
            "type": "custom",
            "widget": self.source_table_select,
        }
        cfg["buttons"][13] = {"action": "add_source", "handler": self.cmd_add_dataset}
        cfg["buttons"][49] = "_insert_stretch"
        cfg["buttons"][100] = "_skip"
        cfg["buttons"][101] = "_skip"
        super().initView(cfg)
        cfg = {"size": ["auto", self.size().height() * (2 / 3) - 18]}
        self.canvas = NchantdCanvas(self, cfg).initWidget()
        self.layout.addWidget(self.canvas)
        self.add_dataset()
        cfg = {"size": ["auto", self.size().height() / 3 - 18]}
        self.source_config_pane = NchantdDataSetConfigPane(self, cfg).initWidget()
        self.layout.addWidget(self.source_config_pane)
        cfg = {}
        self.source_data_view = NchantdTable(self, cfg).initWidget()
        self.layout.addWidget(self.source_data_view)
        self.layout.setSpacing(3)
        self.layout.setContentsMargins(0, 0, 0, 0)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def add_dataset(self) -> None:
        """"""
        source = self.get_source()
        table = self.get_source_table()
        cfg = {
            "size": ["auto", 250],
            "datasource": source,
            "data_table": table,
            "fields": table,
        }  # fields=table placeholder until real fields list is built
        self.data_pane = NchantdDataSetPane(self, cfg).initWidget()
        self.canvas.add_item(self.data_pane, [50, 50])

    def cmd_add_dataset(self, event=None, *args, **kwargs) -> Self:
        """"""
        self.add_dataset()
        return self

    def cmd_on_source_change(self, event=None, *args, **kwargs) -> Self:
        """"""
        return self

    def cmd_on_data_table_change(self, event=None, *args, **kwargs) -> Self:
        """"""
        return self

    def cmd_toggle_config_pane(self, event=None, *args, **kwargs) -> Self:
        """"""
        self.set_pane("config")
        return self

    def cmd_toggle_full_screen_pane(self, event=None, *args, **kwargs) -> Self:
        """"""
        self.set_pane("full")
        return self

    def cmd_toggle_data_pane(self, event=None, *args, **kwargs) -> Self:
        """"""
        self.set_pane("data")
        return self

    def get_source(self) -> str:
        """"""
        self.source = "DictionaryAPI"
        return self.source

    def get_sources(self, full=False) -> list[str]:
        """"""
        try:
            self.sources = self.app.model.get_sources()
        except Exception as e:
            logma.error(f"[config_sources] get_sources: model.get_sources failed: {e}", exc_info=True)
            return []
        #     self.sources = None
        # if self.sources is None:
        #     return self.sources if full else []
        # if full:
        #     return self.sources
        # try:
        #     if hasattr(self.sources, "name_txt"):
        #         return list(self.sources["name_txt"].tolist())
        # except Exception as e:
        #     logma.error(f"[config_sources] get_sources coercion failed: {e}", exc_info=True)
        return self.sources["value_txt"].tolist()

    def get_source_table(self) -> str:
        """Return the source-table widget (T-092).

        Returns ``self.source_table`` (set up by initView
        when the data-sources layout was built). Falls back
        to the empty string when not available.
        """
        try:
            return getattr(self, "source_table", "") or ""
        except Exception as e:
            logma.error(f"[config_sources] get_source_table failed: {e}", exc_info=True)
            return ""

    def get_source_tables(self, source) -> list[str]:
        """Return the source-tables list for ``source`` (T-092).

        T-092: previous version returned a hard-coded stub
        (``["Supermarket", "CoinGecko"]``). Now queries the
        model's ``get_source_tables(source)`` when available,
        falls back to ``config.dikt["source_tables"][source]``
        when one is configured, and finally to the
        canonical Supermarket / CoinGecko default list so
        the method is never empty.
        """
        try:
            model = getattr(self.app, "model", None) if hasattr(self, "app") else None
            if model is not None and hasattr(model, "get_source_tables"):
                tables = model.get_source_tables(source)
                if tables:
                    return list(tables)
            if hasattr(self, "config"):
                stored = (self.config.dikt.get("source_tables") or {}).get(source)
                if stored:
                    return list(stored)
        except Exception as e:
            logma.error(f"[config_sources] get_source_tables failed: {e}", exc_info=True)
        return ["Supermarket", "CoinGecko"]

    def get_data_view(self) -> str:
        """"""
        self.data_view = ""
        return self.data_view

    def get_data_view_fields(self) -> list[str]:
        """"""
        fields = ["UUID", "Name", "Description", "Value", "CREON_DTTM", "MODON_DTTM", "CREBY_INT", "MODBY_INT"]
        return fields

    def init_drawer_source_config(self) -> dict[Any, Any]:
        """"""
        items = self.toolbox_config[100].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Set Default Source: ",
            "layout": "vertical",
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

    def init_drawer_sources(self) -> dict[Any, Any]:
        """"""
        items = self.toolbox_config[200].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        # add a list of available sources with information on the api status of the source
        return items

    def init_drawer_connections(self) -> dict[Any, Any]:
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
        # if cnt not in items:
        #    items[cnt] = default_action
        # options = ["Node: Name"]
        # cfg = {
        #     "label": "Chart Where Used: ",
        #     "layout": "horizontal",
        #     "combobox": {"size": ["auto", "auto"], "options": options},
        # }
        # self.chart_sources_list = NchantdSourcesListPane(self, cfg)
        # items[cnt]["widget"] = self.chart_sources_list
        # cnt += 1
        return items

    def _ensure_drawer_item(self, items, cnt) -> dict[str, str]:
        """Return items[cnt], lazily creating the default slot.

        Centralises the "if cnt not in items: items[cnt] = {...}`` pattern
        used by every drawer initialiser, removing the repeated branch
        that the maintainability auditor flags as switch abuse.
        """
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        return items[cnt]

    def init_drawer_exploratory_data_analysis(self) -> dict[Any, Any]:
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
        slot["widget"] = self.eda_run_button = NchantdButtonWidget(
            self,
            {
                "text": "Run Exploratory Data Analysis",
                "layout": "horizontal",
                "size": None,
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.eda_placement_checkbox = NchantdCheckboxWidget(
            self,
            {
                "text": "Create EDA on Node Branch",
                "layout": "horizontal",
                "size": ["auto", "auto"],
            },
        )
        cnt += 1
        return items

    def init_drawer_quickstart(self) -> dict[Any, Any]:
        """"""
        items = {}
        return items

    def init_toolbox(self) -> None:
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_source_config()
        # PUSH to 0.0.3
        # self.toolbox_config[200]["items"] = self.init_drawer_sources()
        self.toolbox_config[300]["items"] = self.init_drawer_connections()
        # PUSH to 0.0.3
        # self.toolbox_config[400]["items"] = self.init_drawer_exploratory_data_analysis()
        # self.toolbox_config[500]["items"] = self.init_drawer_quickstart()


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
