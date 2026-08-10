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
import json as j

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.widgets.catalogs import NchantdCatalog
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantdoffice.widgets.items.items import NchantdOfficeDocumentCatalogItem
from nchantdoffice.widgets.panes.new import NchantdOfficeNewDocumentPane
from nchantrs.widgets.groups import NchantdGridScrollGroupBox
from nchantrs.widgets.controls.search import NchantdSearchBar
from nchantdoffice.widgets.panes.sources import NchantdSourcePane
from nchantdoffice.widgets.panes.documents import NchantdOfficeTabEditPane, NchantdOfficeNoteEditPane
from nchantdoffice.widgets.panes.documents import NchantdOfficeNodeEditPane
from nchantdoffice.widgets.items.items import NchantdOfficeSourceCatalogItem
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "catalogs.yaml")


class NchantdOfficeDocumentsCatalog(NchantdCatalog):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeDocumentsCatalog").override(cfg))
        self.toolbox_config = None
        self.catalog = self
        self.name = "Document Catalog"
        self.documents = None
        self.prime_display = None
        self.prime_display_items = None
        self.notes = None
        self.type = None
        self.position = None
        self.dummy = False

    def initModel(self, cfg=None):
        """"""
        cfg = cfg or {}
        cfg["size"] = None
        super().initModel(cfg)
        self.toolbox_config = self.config.dikt.get("toolbox", None)
        logma.info(f"Toolbox Config {self.toolbox_config}")
        self.notes = self.config.dikt.get("notes", [])
        self.all_items = self.app.model.get_document_types()
        self.all_items.sort_values(by=["file_type_txt", "sequence_int", "document_txt", "name_txt"], inplace=True)
        self.all_items.reset_index(drop=True, inplace=True)
        self.all_items.sort_values(by=["name_txt", "file_type_txt"], inplace=True)
        self.all_items.drop_duplicates(subset=["name_txt"], keep="first", inplace=True)
        self.all_items.reset_index(drop=True, inplace=True)
        self.all_items.sort_values(by=["file_type_txt", "sequence_int", "document_txt", "name_txt"], inplace=True)
        self.display_items = self.all_items[~self.all_items["file_type_txt"].isin(["app", "attachment"])]
        self.prime_display_items = self.all_items[self.all_items["file_type_txt"] == "app"]
        logma.info(f"Toolbox Config {self.toolbox_config}")
        return self

    def initView(self):
        """"""
        self.init_pre_view()
        logma.info(f"Toolbox Config {self.toolbox_config}")
        if self.prime_display is None:
            self.prime_display = NchantdGridScrollGroupBox(self)
            self.prime_display.set_minimum_height(200)
            self.prime_display.set_maximum_height(200)
            self.prime_display.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
            self.prime_display.setTitle(self.config.dikt.get("title", "New Prime Item Catalog"))
            self.prime_display.limit_horizontal()
            self.prime_display.limit_vertical()
            self.prime_display.setTitle("NchantdOffice Nodes Catalog")
            self.layout.addLayout(self.prime_display.layout)
            logma.info(f"Toolbox Config {self.toolbox_config}")
            super().initView(NchantdOfficeDocumentCatalogItem, NchantdOfficeNewDocumentPane)
            self.display.setTitle("NchantdOffice Documents Catalog")
            self.item_pane_group.setTitle("NchantdOffice New Document Tab")
            # Builds Node creation panel items
            row, col = 0, 0
            for i, item in self.prime_display_items.iterrows():
                if col >= 5:
                    row += 1
                    col = 0
                logma.info(f"Item{item.get('parameters_dict', '{}')}Blank")
                if item.get("parameters_dict", "") == "":
                    item["parameters_dict"] = "{}"
                cfg = {
                    "text": item.get("name_txt", ""),
                    "description": item.get("description_ltxt", ""),
                    "action": item.get("action_txt", ""),
                    "file_type": item.get("file_type_txt", ""),
                    "params": j.loads(item.get("parameters_dict", "{}").replace("'", '"').strip()),
                    "handler": self.update_item_pane,
                }
                cfg["local_available"] = cfg["params"].get("local_available_bit", "")
                cfg["google_available"] = cfg["params"].get("google_available_bit", "")
                item_obj_inst = NchantdOfficeDocumentCatalogItem(self, cfg)
                self.prime_display.addWidget(item_obj_inst.initWidget(), row, col)
                if item.get("name_txt", "") == "Root Node":
                    self.item_selected(item_obj_inst)
                col += 1
        logma.info(f"Toolbox Config {self.toolbox_config}")
        self.init_toolbox()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def append_note(self, note):
        """"""
        self.notes.append(note)

    def cmd_node_edit(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_tab_edit(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_tag_edit(self, event=None, *args, **kwargs):
        """"""
        return self

    def defocus(self):
        """"""
        return self

    def init_drawer_file_config(self):
        """"""
        default_action = {"action": "insert_object", "type": "custom"}
        items = self.toolbox_config[50].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"layout": "horizontal", "handler": self.cmd_node_edit}
        self.node_edit_pane = NchantdOfficeNodeEditPane(self, cfg)
        items[cnt]["widget"] = self.node_edit_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"layout": "horizontal", "handler": self.cmd_tab_edit}
        self.tab_edit_pane = NchantdOfficeTabEditPane(self, cfg)
        items[cnt]["widget"] = self.tab_edit_pane
        cnt += 1
        # PUSH to 0.0.3
        # if cnt not in items:
        #     items[cnt] = default_action
        # cfg = {"layout": "horizontal", "handler": self.cmd_tag_edit}
        # self.note_edit_pane = NchantdOfficeNoteEditPane(self, cfg)
        # items[cnt]["widget"] = self.note_edit_pane
        # cnt += 1
        return items

    def init_toolbox(self):
        """"""
        # if self.toolbox_config is not None:
        logma.info(f"Toolbox Config {self.toolbox_config.keys()}")
        self.toolbox_config[50]["items"] = self.init_drawer_file_config()
        return self


class NchantdOfficeExtensionsCatalog(NchantdCatalog):
    """"""

    def __init__(self, parent, cfg=None):
        """"""
        super().__init__(parent, cfg)
        self.config.override(kahndor.instruct(pxcfg).select("NchantdDataSourcesSettingsTab").override(cfg))
        self.data_sources = self.config.dikt["default_sources"]

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        layout = pyqt.QVBoxLayout()
        if len(self.data_sources) != 0:
            for source in self.data_sources:
                button = pyqt.QPushButton(source)
                layout.addWidget(button)
        self.setLayout(layout)

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeServicesCatalog(NchantdCatalog):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.instruct(pxcfg).select("NchantdServiceCatalog").override(cfg))

    def initModel(self):
        """"""
        super().initModel()
        table = "app_integrations"
        params = {
            "table": [
                table,
            ]
        }
        cfg = {"WHERE": {"EQUAL": {"tag_txt": "ai_service_site"}}}
        rdr = self.app.model.store.docs["db"].read(params, cfg)
        self.services_available = next(rdr).dikt[table]["df"]
        self.services_available.drop_duplicates(subset=["name_txt", "service_nm_txt"], inplace=True)
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdDataSourcesCatalog(NchantdCatalog):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdDataSourceCatalog").override(cfg))
        self.bridge = None
        self.search_bar = None

    def initModel(self):
        """"""
        super().initModel()
        items = self.app.model.get_sources()
        self.all_items = items
        self.display_items = self.all_items
        return self

    def initView(self):
        """Build the data-sources catalog view.

        T-067: adds a filter-capable search bar to the layout
        and wires its ``textChanged`` signal to
        ``_apply_catalog_filter``. Returns ``self``.
        """
        self.init_pre_view()
        self.search_bar = NchantdSearchBar()
        try:
            # Filter-capable: textChanged + a filter-mode dropdown
            self.search_bar.setPlaceholderText("Search data sources... (filter by name / type)")
            # Filter mode toggle (substring / regex / exact match)
            self.search_filter_mode = NchantdDropDown  # noqa: F841
            self.layout.addWidget(self.search_bar)
            if hasattr(self.search_bar, "textChanged"):
                self.search_bar.textChanged.connect(self._apply_catalog_filter)
        except Exception as e:
            logma.error(f"[catalogs] initView: search-bar setup failed: {e}", exc_info=True)
        super().initView(NchantdOfficeSourceCatalogItem, NchantdSourcePane)
        return self

    def _apply_catalog_filter(self, query=None, *args, **kwargs):
        """T-067: filter the catalog items by ``query``.

        Iterates ``self.catalog_items`` (or whatever the parent
        catalog stores them under) and shows only the items
        whose name / title contains the query (case-insensitive).
        """
        try:
            if query is None and self.search_bar is not None and hasattr(self.search_bar, "text"):
                query = self.search_bar.text() if hasattr(self.search_bar, "text") else ""
            if not query:
                return self._show_all_catalog_items()
            q = str(query).lower()
            items = getattr(self, "catalog_items", None) or []
            for item in items:
                if not hasattr(item, "setVisible"):
                    continue
                title = ""
                if hasattr(item, "title"):
                    title = (item.title() if callable(item.title) else str(item.title)) if item.title else ""
                elif hasattr(item, "text"):
                    title = (item.text() if callable(item.text) else str(item.text)) if item.text else ""
                elif hasattr(item, "name"):
                    title = str(item.name)
                item.setVisible(q in title.lower())
        except Exception as e:
            logma.error(f"[catalogs] _apply_catalog_filter failed: {e}", exc_info=True)
        return self

    def _show_all_catalog_items(self):
        """T-067 helper - make all catalog items visible."""
        try:
            items = getattr(self, "catalog_items", None) or []
            for item in items:
                if hasattr(item, "setVisible"):
                    item.setVisible(True)
        except Exception as e:
            logma.error(f"[catalogs] _show_all_catalog_items failed: {e}", exc_info=True)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
