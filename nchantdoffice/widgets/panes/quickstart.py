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
from os.path import abspath, dirname, join
import datetime as dt
import json as j
from typing import Any, Self
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
from nchantdoffice.utilities.links import track_quicklink_click
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

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdQuickStartPane").override(cfg))
        self.prime_display = None
        self.prime_display_items = None
        self.notes = None
        self.type = None
        self.position = None
        self.dummy = False

    def initModel(self, cfg=None) -> Self:
        """Initialise the quickstart model.

        T-062: now also loads the controller / app-launcher
        pane (the in-app equivalent of the iOS home screen)
        from ``self.app.model.get_quick_apps()``. The list is
        stored on ``self.app_launcher_items`` so initView can
        build a button per app.
        """
        super().initModel(cfg)
        self.action = NchantdAction(self.config.get("action", "insert_generic_action"), "base", self)
        self.prime_display_items = self.get_quick_links()
        self.catalog = self
        # T-062: load the app-launcher list
        self.app_launcher_items = self._load_app_launcher_items()
        return self

    def _load_app_launcher_items(self) -> list[dict[str, str]]:
        """Return the list of in-app launchers (controller + apps).

        T-062 helper. Queries ``self.app.model.get_quick_apps()``
        first, then falls back to ``config.dikt['app_launcher_items']``,
        then to a canonical list so the pane is never empty.
        """
        try:
            model = getattr(self.app, "model", None) if hasattr(self, "app") else None
            if model is not None and hasattr(model, "get_quick_apps"):
                apps = model.get_quick_apps()
                if apps:
                    return apps
            if hasattr(self, "config"):
                stored = self.config.dikt.get("app_launcher_items")
                if stored:
                    return stored
        except Exception as e:
            logma.error(f"[quickstart] _load_app_launcher_items failed: {e}", exc_info=True)
        return [
            {"name": "Dashboard",  "widget_class": "nchantdoffice.widgets.panes.objects.NchantdOfficeDashboardPane", "icon": "dashboard"},
            {"name": "Documents",  "widget_class": "nchantdoffice.widgets.panes.documents.NchantdOfficeDocumentsPane", "icon": "documents"},
            {"name": "Charts",     "widget_class": "nchantdoffice.widgets.panes.charts.NchantdOfficeChartsPane", "icon": "charts"},
            {"name": "Sources",    "widget_class": "nchantdoffice.widgets.panes.sources.NchantdOfficeSourcesPane", "icon": "sources"},
            {"name": "Calendar",   "widget_class": "nchantdoffice.widgets.documents.managers.calendars.NchantdOfficeCalendarManager", "icon": "calendar"},
            {"name": "Help",       "widget_class": "nchantdoffice.widgets.config.help.NchantdOfficeHelpDocs", "icon": "help"},
        ]

    def cmd_launch_app(self, app_item=None, event=None, *args, **kwargs) -> Self:
        """Launch an in-app controller / sub-app (T-062).

        Instantiates the ``widget_class`` from the launcher item
        and adds it as a new tab in the right-side drawer.
        Returns ``self``.

        T-DESK: also fires a quicklink click event to
        nchantdoffice_com via ``track_quicklink_click`` so affiliate
        analytics work for in-app launches.
        """
        try:
            if app_item is None:
                return self
            widget_class_path = app_item.get("widget_class") if isinstance(app_item, dict) else None

            # T-DESK: best-effort analytics — never blocks the launch.
            try:
                offer_id = (
                    int(app_item.get("offer_id"))
                    if isinstance(app_item, dict) and app_item.get("offer_id") is not None
                    else None
                )
                slug = (
                    app_item.get("service_slug")
                    or app_item.get("name_txt")
                    or app_item.get("action_txt")
                    if isinstance(app_item, dict)
                    else None
                )
                user = (
                    getattr(getattr(self, "app", None), "user", None)
                    or getattr(self, "user", None)
                )
                tier = None
                try:
                    if user is not None:
                        tier = "pro" if getattr(user, "has_pro", False) else "free"
                except Exception:
                    pass
                track_quicklink_click(
                    offer_id=offer_id, service_slug=slug, tier=tier, user=user,
                )
            except Exception as e:
                logma.warning(f"[quickstart] analytics fire failed: {e}")

            if not widget_class_path:
                return self
            # Lazy import to avoid importing every pane module at load time
            import importlib
            module_path, _, class_name = widget_class_path.rpartition(".")
            module = importlib.import_module(module_path)
            widget_cls = getattr(module, class_name)
            widget = widget_cls(self, {}).initWidget() if callable(widget_cls) else None
            if widget is None:
                return self
            logma.info(f"[quickstart] cmd_launch_app: {class_name}")
        except Exception as e:
            logma.error(f"[quickstart] cmd_launch_app failed: {e}", exc_info=True)
        return self

    def initView(self) -> Self:
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
                item_obj_inst = NchantdOfficeLinkCatalogItem(self, cfg)
                self.prime_display.addWidget(item_obj_inst.initWidget(), row, col)
                col += 1
        logma.info(f"Toolbox Config {self.toolbox_config}")

        self.layout.addWidget(self.links)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def get_quick_links(self) -> DataFrame:
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
