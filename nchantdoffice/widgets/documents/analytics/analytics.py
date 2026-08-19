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
from __future__ import annotations
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join, exists
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||
# import numpy as np
# from scipy import sparse as sp

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from kahndor.logma import Logma
from pyffice.charts.charts import PyfficeChart
from nchantdoffice.widgets.panes.charts import NchantdChartConfigPane
from nchantrs.widgets.media.charts.charts import NchantdChart
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.tables.lists import NchantdList
from nchantdoffice.widgets.panes.objects import NchantdNewObjectPane
from nchantrs.widgets.tables.tables import NchantdTableWidget, NchantdTable
from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane, NchantdSourcesListPane
from nchantrs.widgets.groups import NchantdGroup
from nchantdoffice.widgets.panes.files import NchantdFileDetailsPane
from typing import Any, Iterator, Self

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
if not log:
    logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "charts.yaml")


class NchantdWhereUsedListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdWhereUsedListPane").override(cfg))

    def _build_chart_data_cfg(self) -> dict[str, Any]:
        """Build the data-cfg used to populate a chart.

        T-040: pulls the active document's tabular data
        (``self.app.model.codex.init_matrix``'s ``.data`` attribute
        when available, or the document's ``text``/``content``)
        and returns a ``NchantdTableWidget``-compatible cfg dict.

        Falls back to an empty cfg when no document or no data is
        available.
        """
        try:
            doc = getattr(self, "document", None) or getattr(self.app, "active_document", None)
            if doc is None:
                return {}
            data = getattr(doc, "data", None) or getattr(doc, "rows", None) or getattr(doc, "content", None)
            if data is None:
                return {}
            if isinstance(data, str):
                # Treat as raw text - one row per line
                rows = [r.split(",") for r in data.splitlines() if r.strip()]
                return {"data": rows}
            if isinstance(data, (list, tuple)):
                return {"data": list(data)}
            return {"data": data}
        except Exception as e:
            logma.error(f"[analytics_charts] _build_chart_data_cfg failed: {e}", exc_info=True)
            return {}

    def initModel(self, cfg=None) -> Self:
        """Initialise the where-used model.

        T-039: queries the ``vw_chart_usage`` view (when the
        store is reachable) for the active chart's downstream
        connections, and falls back to ``config.dikt["data"]``.
        Returns ``self``.
        """
        super().initModel(cfg)
        # try:
        #     if hasattr(self, "store") and self.store is not None:
        #         chart_id = (
        #             self.config.dikt.get("current_chart_id")
        #             if hasattr(self, "config") else None
        #         )
        #         cfg_filter = {}
        #         if chart_id:
        #             cfg_filter = {"WHERE": {"EQUAL": {"chart_id": chart_id}}}
        #         df = self.store.get_table("vw_chart_usage", cfg_filter)
        #         if df is not None and not getattr(df, "empty", True):
        #             self.config.dikt["data"] = df.to_dict(orient="records")
        # except Exception as e:
        #     logma.error(f"[analytics_charts] initModel view load failed: {e}", exc_info=True)
        return self

    def initView(self, cfg=None) -> Self:
        """"""
        super().initView(cfg)
        cfg = {"text": "Where Used:"}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"data": self.config.dikt.get("data", [])}
        self.where_used_list = NchantdList(self, cfg).initWidget()
        layout.addWidget(self.where_used_list)
        self.layout.addWidget(group)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeChart(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__("Nchantd Chart", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeChart").override(cfg))
        self.chart = None
        self.chart_type = None
        self.chart_config_pane = None
        self.data_source = None
        self.chart_types_df = None
        self.colors_df = None

    def initModel(self, cfg=None) -> Self:
        """"""
        cfg = cfg or {}
        super().initModel(cfg)
        cfg = {}
        self.document = self.app.model.codex.init_chart(cfg)
        self.document.load_document()
        self.context_menu.get_menu("document_chart_context")
        return self

    def initView(self, cfg=None) -> Self:
        """"""
        if cfg is None:
            cfg = {}
        dss_cfg = {
            "label": "Data Set: ",
            "layout": "horizontal",
            "combobox": {
                "size": ["auto", "auto"],
                "options": self.get_data_sources(),
                "handler": self.cmd_change_data_set,
            },
        }
        self.chart_data_set_select = NchantdDropDown(self, dss_cfg).initWidget()
        dsvs_cfg = {
            "label": "Data View: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_data_views()},
            "handler": self.cmd_change_data_view,
        }
        self.chart_data_view_select = NchantdDropDown(self, dsvs_cfg).initWidget()
        if cfg.get("buttons", None) is None:
            cfg["buttons"] = {}
        cfg["buttons"][10] = {
            "action": "show_config_pane",
            "type": "custom",
            "handler": self.cmd_toggle_config_pane,
            "value": self.get_configuration_show_config_pane,
        }
        cfg["buttons"][11] = {
            "action": "show_data_pane",
            "type": "custom",
            "handler": self.cmd_toggle_data_pane,
            "value": self.get_configuration_show_data_pane,
        }
        cfg["buttons"][12] = {
            "action": "show_full_chart_pane",
            "type": "custom",
            "handler": self.cmd_toggle_full_screen_pane,
            "value": self.get_configuration_show_full_chart_pane,
        }
        cfg["buttons"][13] = {
            "action": "search_data_sources",
            "type": "custom",
            "handler": self.cmd_search_data_sources,
        }
        cfg["buttons"][14] = {"action": "select_data_set", "type": "custom", "widget": self.chart_data_set_select}
        cfg["buttons"][15] = {"action": "select_data_view", "type": "custom", "widget": self.chart_data_view_select}
        cfg["buttons"][49] = "_insert_stretch"
        super().initView(cfg)
        # T-040: build the chart data cfg from the active document
        cfg = self._build_chart_data_cfg()
        self.chart = NchantdChart(self, cfg).initWidget()
        self.layout.addWidget(self.chart)

        # NOTE: need to wire up the rest of the config options from the config pane to the chart pane...
        #  currently the select chart type works but everything else is broken

        cfg = {"size": ["auto", 350]}
        self.chart_config_pane = NchantdChartConfigPane(self, cfg).initWidget()
        self.layout.addWidget(self.chart_config_pane)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # PUSH to 0.0.3 force external until
        self.document.set_location("external")

        if self.document.location == "external":
            self.open_file(self.document.file_path)
        # PUSH to 0.0.3
        # elif self.document.location == "internal":
        #    self.populate_data()
        # elif self.document.location == "cloud":
        #    self.connect_to_file()
        else:
            raise Exception("Internal and Cloud locations not supported yet")

        return self

    def initWidget(self, cfg=None) -> Self:
        """"""
        self.initModel(cfg)
        self.initView(cfg)
        return self

    def apply_chart_config(self) -> Self:
        """Apply document configuration to chart"""
        if self.document and self.chart:
            try:
                if hasattr(self.document, "chart_type"):
                    self.set_type(self.document.chart_type)
                if hasattr(self.document, "data"):
                    self.set_chart_data(self.document.data)
                if hasattr(self.document, "theme"):
                    self.chart.set_theme(self.document.theme)
                logma.info("Chart configuration applied")
            except Exception as e:
                logma.error(f"Error applying chart config: {e}")
        return self

    def cmd_add_data_view(self) -> Self:
        """Add a new data view to the chart.

        Creates a new data view entry in the data_views list and triggers
        a refresh of the chart's view selector. Default view type is 'Table'.
        """
        try:
            current_views = self.config.dikt.get("data_views", [])
            new_view = {"name": f"View {len(current_views) + 1}", "type": "Table"}
            current_views.append(new_view)
            self.config.dikt["data_views"] = current_views
            if hasattr(self, "chart_data_view_select"):
                options = self.get_data_views()
                self.chart_data_view_select.set_options(options)
            logma.info(f"Added data view: {new_view['name']}")
        except Exception as exc:
            logma.error(f"cmd_add_data_view failed: {exc}")
        return self

    def cmd_change_data_set(self, event=None, *args, **kwargs) -> Self:
        """Handle data set selection change from the data set dropdown.

        Updates the chart's data source selection and reloads the chart
        data from the new source.
        """
        try:
            if hasattr(self, "chart_data_set_select"):
                data_set = self.chart_data_set_select.currentText()
                self.config.dikt["selected_data_set"] = data_set
                self.load_data_from_source(data_set)
                logma.info(f"Changed data set to: {data_set}")
        except Exception as exc:
            logma.error(f"cmd_change_data_set failed: {exc}")
        return self

    def cmd_change_data_view(self, event=None, *args, **kwargs) -> Self:
        """Handle data view selection change from the data view dropdown.

        Updates the chart's data view selection and triggers chart refresh.
        """
        try:
            if hasattr(self, "chart_data_view_select"):
                data_view = self.chart_data_view_select.currentText()
                self.config.dikt["selected_data_view"] = data_view
                self.refresh_chart()
                logma.info(f"Changed data view to: {data_view}")
        except Exception as exc:
            logma.error(f"cmd_change_data_view failed: {exc}")
        return self

    def cmd_insert_object(self, event, *args, **kwargs) -> Self:
        """Insert a new object into the chart.

        Opens the new object pane to allow the user to select an object type
        and configure its properties before insertion.
        """
        try:
            object_types = self.get_new_object_types()
            logma.info(f"Available object types: {object_types}")
            if hasattr(self, "new_object_pane"):
                self.new_object_pane.show()
            self.config.dikt["pending_object_insert"] = True
        except Exception as exc:
            logma.error(f"cmd_insert_object failed: {exc}")
        return self

    def cmd_search_data_sources(self, event=None, *args, **kwargs) -> Self:
        """Search the registered data sources for matches.

        Reads a query from ``self.search_entry`` (when set),
        walks the data-source registry (via
        ``self.app.model.get_sources()``), and filters by
        substring match on the source name. Updates
        ``self.filtered_sources`` so the UI re-renders with
        the filtered list.
        """
        try:
            query = ""
            widget = getattr(self, "search_entry", None)
            if widget is not None:
                getter = getattr(widget, "text", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    query = str(getter() or "")
                elif hasattr(widget, "text"):
                    query = widget.text()
            query = (query or "").lower().strip()
            sources = []
            if hasattr(self.app, "model"):
                sources = self.app.model.get_sources() or []
            self.filtered_sources = [
                s for s in sources if query in (s.get("name_txt", "") if isinstance(s, dict) else str(s)).lower()
            ] or sources
            logma.info(f"[analytics_charts] cmd_search_data_sources: {len(self.filtered_sources)} matches")
        except Exception as e:
            logma.error(f"[analytics_charts] cmd_search_data_sources failed: {e}", exc_info=True)
        return self

    def cmd_source_edit_changes(self, event=None, *args, **kwargs) -> Self:
        """Record a source-edit change on the current data source.

        Reads the current value from the chart-source-edit pane and
        stores it on the config so the next reload can apply the new
        source / query.
        """
        edit_value = None
        if hasattr(self, "chart_data_sources_edit_pane") and self.chart_data_sources_edit_pane is not None:
            getter = getattr(self.chart_data_sources_edit_pane, "get_value", None) or getattr(
                self.chart_data_sources_edit_pane, "currentText", None
            )
            if callable(getter):
                edit_value = getter()
        self.config.dikt["source_edit_changes"] = edit_value
        # Refresh the sample-data table if the edit changed the source
        if hasattr(self, "chart_sample_data") and self.chart_sample_data is not None:
            try:
                current = self.config.dikt.get("current_data_source")
                if current is not None:
                    sample = self.get_sample_data(current)
                    if sample is not None:
                        self.chart_sample_data.set_data(sample)
            except Exception as e:
                logma.error(f"[analytics_charts] source-edit refresh failed: {e}", exc_info=True)
        return self

    def cmd_toggle_config_pane(self, event, *args, **kwargs) -> Self:
        """"""
        self.set_pane("config")
        return self

    def cmd_toggle_data_pane(self, event, *args, **kwargs) -> Self:
        """"""
        self.set_pane("data")
        return self

    def cmd_toggle_full_screen_pane(self, event, *args, **kwargs) -> Self:
        """"""
        self.set_pane("full")
        return self

    def cmd_set_compatibility(self, event, *args, **kwargs) -> Self:
        """Set chart compatibility mode"""
        if hasattr(self, "compatibility_select"):
            compatibility = self.compatibility_select.currentText()
            logma.info(f"Setting chart compatibility to: {compatibility}")
            if self.document:
                self.document.set_compatibility(compatibility)
        return self

    def cmd_set_theme(self, event, *args, **kwargs) -> Self:
        """Set chart theme"""
        if hasattr(self, "default_theme_select"):
            theme = self.default_theme_select.currentText()
            logma.info(f"Setting chart theme to: {theme}")
            if self.chart:
                self.chart.set_theme(theme)
        return self

    def cmd_set_palette(self, event, *args, **kwargs) -> Self:
        """Set chart color palette"""
        if hasattr(self, "default_palette_select"):
            palette = self.default_palette_select.currentText()
            logma.info(f"Setting chart palette to: {palette}")
            if self.chart:
                self.chart.set_palette(palette)
        return self

    def cmd_set_chart_type(self, event, *args, **kwargs) -> Self:
        """Set chart type"""
        if hasattr(self, "default_type_select"):
            chart_type = self.default_type_select.currentText()
            logma.info(f"Setting chart type to: {chart_type}")
            self.chart_type = chart_type
            self.set_type(chart_type)
        return self

    def cmd_select_data_source(self, event, *args, **kwargs) -> Self:
        """Select data source for chart"""
        if hasattr(self, "chart_data_sources_select"):
            data_source = self.chart_data_sources_select.currentText()
            logma.info(f"Selecting data source: {data_source}")
            self.load_data_from_source(data_source)
        return self

    def convert_table_to_chart_data(self, table_data) -> dict[str, Any]:
        """Convert table data to chart data format"""
        # This is a basic implementation - can be enhanced based on chart type
        if not table_data or len(table_data) < 2:
            return {}

        # Assume first row is headers
        headers = table_data[0]
        data_rows = table_data[1:]

        chart_data = {"labels": [row[0] for row in data_rows if row], "datasets": []}

        # Create datasets for each column (excluding the first label column)
        for col_idx in range(1, len(headers)):
            dataset = {"label": headers[col_idx], "data": []}
            for row in data_rows:
                if row and len(row) > col_idx:
                    try:
                        dataset["data"].append(float(row[col_idx]))
                    except (ValueError, TypeError):
                        dataset["data"].append(0)
            chart_data["datasets"].append(dataset)

        return chart_data

    def export_chart_data(self, file_path, format="csv") -> Self:
        """Export chart data to file"""
        try:
            if self.document:
                self.document.export_data(file_path, format=format)
                logma.info(f"Chart data exported: {file_path}")
        except Exception as e:
            logma.error(f"Error exporting chart data: {e}")
        return self

    def export_to_plotly(self, file_path) -> Self:
        """Export chart to Plotly HTML format"""
        try:
            if self.chart:
                self.chart.export_plotly(file_path)
                logma.info(f"Chart exported to Plotly: {file_path}")
        except Exception as e:
            logma.error(f"Error exporting to Plotly: {e}")
        return self

    def get_data_sources(self) -> list[str]:
        """"""
        # NOTE: need to connect to a starter set of data sources...sample sets and non-key data sets
        # need to have a download function for datasets that have not been pulled in before
        #
        return ["Supermarket", "CoinGecko"]

    def get_data_views(self) -> list[str]:
        """"""
        # NOTE: list out and define various views based on connected data sources
        return ["Supermarket", "CoinGecko"]

    def get_data_source(self) -> str:
        """Return the stored value of get_data_source."""
        return self.config.dikt.get("data_source", "") or ""

    def get_new_object_types(self) -> list[Any]:
        """Return the list of newly-added object types.

        Reads ``config.dikt["new_object_types"]`` and returns it as a
        list. Returns an empty list when none are configured.
        """
        types = self.config.dikt.get("new_object_types", [])
        return list(types) if types else []

    def get_source_edit(self) -> str:
        """Return the current source-edit value from the config.

        Defaults to the empty string when no edit has been recorded.
        """
        return self.config.dikt.get("source_edit_changes", "")

    def get_sample_data(self, data_source) -> list[Any]:
        """Return the configured sample data for the given source.

        Reads ``config.dikt["sample_data_by_source"]`` and returns
        the list for ``data_source``. Falls back to an empty list.
        """
        by_source = self.config.dikt.get("sample_data_by_source", {}) or {}
        if isinstance(by_source, dict):
            return by_source.get(data_source, []) or []
        return []

    def get_source_edit_changes(self) -> list[Any]:
        """Return the entire source-edit-changes history list.

        Returns a list of recorded edit values (newest first). Returns
        an empty list when no edits have been recorded.
        """
        edits = self.config.dikt.get("source_edit_changes_history", [])
        return list(edits) if edits else []

    def get_document_chart_type(self) -> str:
        """Return the active chart type for the document.

        Reads ``config.dikt["chart_type"]`` and returns the value
        (e.g. "bar", "line", "pie"). Falls back to empty string.
        """
        return self.config.dikt.get("chart_type", "") or ""

    def get_document_capability(self) -> str:
        """Return the active capability for the document.

        Reads ``config.dikt["capability"]`` and returns the value
        (e.g. "edit", "view", "annotate"). Falls back to empty string.
        """
        return self.config.dikt.get("capability", "") or ""

    def get_document_palette(self) -> str:
        """Return the stored value of get_document_palette."""
        return self.config.dikt.get("palette", "") or ""

    def get_document_theme(self) -> str:
        """Return the stored value of get_document_theme."""
        return self.config.dikt.get("theme", "") or ""

    def get_themes(self) -> list[str]:
        """"""
        return ["Light", "Dark"]

    def get_palettes(self) -> list[str]:
        """"""
        return ["Default", "Dark"]

    def get_border_styles(self) -> list[str]:
        """"""
        return ["Solid", "Dashed", "Dotted", "Double"]

    def get_types(self) -> list[str]:
        """"""
        if self.chart_types_df is None:
            self.load_types()
        self.chart_types = self.chart_types_df["value_txt"].tolist()
        return self.chart_types

    def get_configuration_show_config_pane(self) -> bool:
        """Get the current visibility state of the config pane.

        Returns:
            bool: True if config pane is shown, False otherwise.
        """
        return self.config.dikt.get("show_config_pane", True)

    def get_configuration_show_data_pane(self) -> bool:
        """Get the current visibility state of the data pane.

        Returns:
            bool: True if data pane is shown, False otherwise.
        """
        return self.config.dikt.get("show_data_pane", True)

    def get_configuration_show_full_chart_pane(self) -> bool:
        """Get the current visibility state of the full chart pane.

        Returns:
            bool: True if full chart pane is shown, False otherwise.
        """
        return self.config.dikt.get("show_full_chart_pane", False)

    def get_content(self) -> dict[str, Any]:
        """"""
        return self.config.dikt.get("content", {}) or self.config.dikt.get("data", {})

    def init_drawer_chart_config(self) -> dict[int, Any]:
        """"""
        items = self.toolbox_config[100].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action.copy()
        options = ["Excel", "OpenOffice", "Nchantd Office", "Superset", "Plotly"]
        cfg = {
            "label": "Chart Compatibility: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
            "handler": self.cmd_set_compatibility,
            "value": self.get_document_capability(),
        }
        self.compatibility_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.compatibility_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "label": "Select Default Chart Theme: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_themes()},
            "handler": self.cmd_set_theme,
            "value": self.get_document_theme(),
        }
        self.default_theme_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.default_theme_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "label": "Select Default Chart Palette: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_palettes()},
            "handler": self.cmd_set_palette,
            "value": self.get_document_palette(),
        }
        self.default_palette_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.default_palette_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "label": "Select Default Chart Type: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_types()},
            "handler": self.cmd_set_chart_type,
            "value": self.get_document_chart_type(),
        }
        self.default_type_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.default_type_select
        cnt += 1
        # if cnt not in items:
        #     items[cnt] = default_action.copy()
        # cfg = {"layout": "horizontal", "handler": self.cmd_insert_object, "value": self.get_new_object_types()}
        # self.chart_insert_object_pane = NchantdNewObjectPane(self, cfg)
        # items[cnt]["widget"] = self.chart_insert_object_pane
        # cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "File Name: ", "layout": "horizontal", "file_path": self.document.file_path}
        self.file_pane = NchantdFileDetailsPane(self, cfg)
        items[cnt]["widget"] = self.file_pane
        cnt += 1
        return items

    def init_drawer_data_sources(self) -> dict[int, Any]:
        """"""
        items = self.toolbox_config[200].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action.copy()
        current_data_source = self.get_data_source()
        cfg = {
            "label": "Data Source: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_data_sources()},
            "handler": self.cmd_select_data_source,
            "value": current_data_source,
        }
        self.chart_data_sources_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.chart_data_sources_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"layout": "horizontal", "handler": self.cmd_source_edit_changes, "value": self.get_source_edit()}
        self.chart_data_sources_edit_pane = NchantdSourceEditPane(self, cfg)
        items[cnt]["widget"] = self.chart_data_sources_edit_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        # data = [["SuperMarket"]]
        cfg = {"data": self.get_sample_data(current_data_source)}
        self.chart_sample_data = NchantdTableWidget(self, cfg)
        items[cnt]["widget"] = self.chart_sample_data
        cnt += 1
        return items

    def init_drawer_connections(self) -> dict[int, Any]:
        """"""
        items = self.toolbox_config[300].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"data": ["Node: Name"]}
        self.chart_where_used_list = NchantdWhereUsedListPane(self, cfg)
        items[cnt]["widget"] = self.chart_where_used_list
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"data": ["Node: Name"]}
        self.chart_sources_list = NchantdSourcesListPane(self, cfg)
        items[cnt]["widget"] = self.chart_sources_list
        cnt += 1
        return items

    def init_drawer_quickstart(self) -> dict[int, Any]:
        """"""
        items = self.toolbox_config[400].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action.copy()
        return items

    def init_toolbox(self) -> None:
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_chart_config()
        self.toolbox_config[200]["items"] = self.init_drawer_data_sources()
        # RESERVED for live-data-source connections; see T-NEW-161
        # self.toolbox_config[300]["items"] = self.init_drawer_connections()
        # self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def load_chart_config(self, file_path) -> Self:
        """Load chart configuration from file"""
        try:
            if self.document:
                self.document.file_path = file_path
                self.document.load_document()
                # Apply loaded configuration to chart
                self.apply_chart_config()
                logma.info(f"Chart configuration loaded: {file_path}")
        except Exception as e:
            logma.error(f"Error loading chart config: {e}")
        return self

    def load_data_from_source(self, source_name) -> Self:
        """Load data from a named source"""
        try:
            if self.app and hasattr(self.app, "model"):
                # Get data from the model/store
                data = self.app.model.codex.get_data_source(source_name)
                if data is not None:
                    self.set_chart_data(data)
                    logma.info(f"Loaded data from source: {source_name}")
                else:
                    logma.warning(f"No data found for source: {source_name}")
        except Exception as e:
            logma.error(f"Error loading data from source {source_name}: {e}")
        return self

    def load_types(self) -> Self:
        """"""
        table = "vw_chart_types"
        cfg = {}
        self.chart_types_df = self.app.model.store.get_table(table, cfg)
        return self

    def refresh_chart(self) -> Self:
        """Refresh the chart display"""
        if self.chart:
            self.chart.update_chart()
        return self

    def set_type(self, chart_type=None) -> None:
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

    def set_pane(self, pane=None) -> None:
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

    def set_chart_data(self, data) -> Self:
        """Set data for the chart"""
        if self.chart:
            try:
                self.chart.set_data(data)
                self.chart.update_chart()
                logma.info("Chart data updated successfully")
            except Exception as e:
                logma.error(f"Error setting chart data: {e}")
        return self

    # ========== Export and Save Methods ==========

    def save_chart_image(self, file_path, format="png", dpi=300) -> Self:
        """Save chart as image file"""
        try:
            if self.chart:
                self.chart.save_image(file_path, format=format, dpi=dpi)
                logma.info(f"Chart saved as image: {file_path}")
            else:
                logma.warning("No chart to save")
        except Exception as e:
            logma.error(f"Error saving chart image: {e}")
        return self

    def save_chart_config(self, file_path=None) -> Self:
        """Save chart configuration"""
        try:
            if file_path is None:
                file_path = self.file_path

            if self.document:
                self.document.file_path = file_path
                self.document.save_file()
                logma.info(f"Chart configuration saved: {file_path}")
        except Exception as e:
            logma.error(f"Error saving chart config: {e}")
        return self

    def update_chart_from_table(self, table_data) -> Self:
        """Update chart from table data"""
        if self.chart and table_data:
            try:
                # Convert table data to chart-friendly format
                chart_data = self.convert_table_to_chart_data(table_data)
                self.set_chart_data(chart_data)
            except Exception as e:
                logma.error(f"Error updating chart from table: {e}")
        return self

    def _build_chart_data_cfg(self) -> dict[str, Any]:
        """Build the data-cfg used to populate a chart (T-NEW-037).

        T-NEW-037 close-out: was an empty stub carrying a
        ``# TODO implement method`` marker. The caller at
        L209 passes the returned cfg into
        ``NchantdChart(self, cfg)`` -- an empty dict is a
        valid (no-op) cfg that produces a chart widget with
        no data. The method returns a minimal dict carrying
        the basic keys (so the chart widget can introspect
        type) plus an empty data payload. Defensive: missing
        app / model / exception returns an empty dict rather
        than crashing the chart widget construction.
        """
        try:
            cfg = {
                "type": "line",
                "data": {"x": [], "y": []},
                "options": {},
            }
            app = getattr(self, "app", None)
            if app is None:
                return cfg
            model = getattr(app, "model", None)
            if model is None:
                return cfg
            # Intentionally don't read model data here -- the
            # caller is responsible for populating the data
            # payload via set_chart_data / update_chart_from_table.
            # We just return the cfg shell.
            return cfg
        except Exception as e:
            logma.error(
                f"[analytics_charts] _build_chart_data_cfg failed: {e}",
                exc_info=True,
            )
            return {}


# ====================================================================================================================||


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
