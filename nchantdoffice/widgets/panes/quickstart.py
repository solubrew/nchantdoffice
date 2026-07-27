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
from kahndor.logma import Logma
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.tables.lists import NchantdList
from nchantdoffice.widgets.panes.new import NchantdOfficeNewDocumentPane
from nchantrs.widgets.catalogs import NchantdCatalog
from nchantrs.libraries import pyqt
from nchantrs.widgets.groups import NchantdGridScrollGroupBox
from nchantdoffice.widgets.items.items import NchantdOfficeLinkCatalogItem
from nchantrs.widgets.widgets import NchantdAction
# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "quickstart.yaml")


class NchantdOfficeBrowserQuickStartPane(NchantdCatalog):
    """
    show a list of links for basic interactions
    when clicked launch a tab under the help node with structured nodes and tabs
    this way the user gets the help but only what they ask for easier revisiting
    """

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdQuickStartPane").override(cfg))
        self.prime_display = None
        self.prime_display_items = None
        self.notes = None
        self.type = None
        self.position = None
        self.dummy = False

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        self.action = NchantdAction(self.config.get("action", "insert_generic_action"), "base", self)
        self.prime_display_items = self.get_quick_links()
        self.catalog = self
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
            super().initView()
            self.display.setTitle("NchantdOffice Documents Catalog")
            row, col = 0, 0
            for i, item in self.prime_display_items.iterrows():
                if col >= 3:
                    row += 1
                    col = 0
                logma.info(f"Item{item.get("parameters_dict", "{}")}Blank")
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
                item_obj_inst = NchantdOfficeLinkCatalogItem(self, cfg)
                self.prime_display.addWidget(item_obj_inst.initWidget(), row, col)
                col += 1
        logma.info(f"Toolbox Config {self.toolbox_config}")

        self.layout.addWidget(self.links)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_quick_links(self):
        """Return the quick-start links DataFrame from the database.

        T-059: previously returned a hard-coded 2-row stub. Now:

          1. Queries the ``app_quick_start_links`` table (when the
             store is reachable) for the user's saved quick-start
             links.
          2. Falls back to ``config.dikt['quick_start_links']`` so
             tests / first-launch users can supply a static list
             without touching the DB.
          3. Final fallback: the canonical default list
             (google.com / yahoo.com) so the widget is never empty.

        Returns a pandas DataFrame with a single ``site_link``
        column.
        """
        try:
            model = getattr(self.app, "model", None) if hasattr(self, "app") else None
            if model is not None and hasattr(model, "store") and model.store is not None:
                try:
                    df = model.store.get_table(
                        "app_quick_start_links",
                        {"WHERE": {"EQUAL": {"active_bit": 1}}},
                    )
                    if df is not None and not getattr(df, "empty", True):
                        # Normalise to a DataFrame with a 'site_link' column
                        if "site_link" not in df.columns:
                            df = df.rename(columns={df.columns[0]: "site_link"})
                        return df
                except Exception as e:
                    logma.error(f"[quickstart] get_quick_links DB load failed: {e}", exc_info=True)
            fallback = (
                self.config.dikt.get("quick_start_links") if hasattr(self, "config") else None
            )
            if fallback:
                return DataFrame(list(fallback), columns=["site_link"])
        except Exception as e:
            logma.error(f"[quickstart] get_quick_links outer failed: {e}", exc_info=True)
        return DataFrame([["google.com"], ["yahoo.com"]], columns=["site_link"])


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
