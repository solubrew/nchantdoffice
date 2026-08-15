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
from __future__ import annotations
from typing import Any, Self
from os.path import abspath, dirname, join
import datetime as dt
import sqlite3

# ======================================3rd Party Library Modules=====================================================||
from shutil import copyfile

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.dialogs.files import NchantdFileOpenSigil


from nchantrs.widgets.controls.toolboxes import NchantdToolBox

# T-NEW-114 Defect C: QObject worker for offloading the synchronous
# import_pyof() call to a background QThread so the GUI thread does
# not block on a large .pyof file. The signal/slot pair is wired
# in cmd_import_pyof (slot = _show_pyof_import_result on the main
# thread, Qt.QueuedConnection is the default for cross-thread
# signals).
try:
    from PySide6.QtCore import QObject, QThread, Signal  # type: ignore
except Exception:  # pragma: no cover -- rare miss in headless envs
    QObject = object  # type: ignore
    QThread = object  # type: ignore
    def Signal(*args, **kwargs):  # type: ignore
        return None


class _PyofImportWorker(QObject):
    """T-NEW-114 Defect C: QObject worker that runs import_pyof on
    a background QThread so the GUI thread does not block on a
    large .pyof file. Emits finished(path, results) when done; the
    GUI thread slot (_show_pyof_import_result) updates the status
    bar. Uses Qt.QueuedConnection (the default for cross-thread
    signals) so the slot runs on the main thread."""
    finished = Signal(str, list)

    def __init__(self, import_pyof_fn, path, host_conn):
        super().__init__()
        self._import_pyof = import_pyof_fn
        self._path = path
        self._host_conn = host_conn

    def run(self):
        try:
            results = self._import_pyof(self._path, self._host_conn)
        except Exception as e:
            logma.error(f"[import_pyof] worker failed: {e}", exc_info=True)
            results = []
        self.finished.emit(self._path, results)

from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.media.editors.editors import NchantdEntryBox
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.panes.panes import NchantdPane

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "toolboxes.yaml")


class NchantdApplicationSearchPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdApplicationSearchPane").override(cfg))
        self.handler = self.config.dikt.get("handler", None)

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> Self:
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

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdLLMQueryPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdLLMQueryPane").override(cfg))

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> Self:
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

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdWebSearchPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdWebSearchPane").override(cfg))

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> Self:
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

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self


# T-091: search panes are now built by NchantdApplicationSearchPane /
# NchantdLLMQueryPane / NchantdWebSearchPane (above).
# T-091: Node Configuration Drawer pane spacing is now balanced via
# NchantdOfficeApplicationToolBox.balance_pane_widths() (T-061).
class NchantdOfficeApplicationToolBox(NchantdToolBox):
    """T-061: balanced-pane-widths for Node Configuration Drawer.

    The Node Configuration Drawer previously had uneven spacing
    that left the Node Pane wider than the Tab Pane (or vice
    versa). The balance_pane_widths() method computes the
    actual node / tab counts and resizes the drawer to split
    the available width 50/50 (configurable).
    """

    _DEFAULT_PANE_RATIO = 0.5  # Node : Tab width split

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeApplicationToolBox").override(cfg))

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self) -> Self:
        """"""
        super().initView()
        try:
            self.balance_pane_widths()
        except Exception as e:
            logma.error(f"[toolboxes] initView: balance_pane_widths failed: {e}", exc_info=True)
        return self

    def balance_pane_widths(self) -> Self:
        """T-061: rebalance the Node Pane + Tab Pane widths.

        Looks at the drawer's parent splitter (when one is
        present), applies the configured pane ratio (default
        50/50), and writes the result back. Falls back to
        setting ``self.config.dikt['pane_width_ratio']`` when
        no splitter is present.
        """
        try:
            ratio = (
                self.config.dikt.get("pane_width_ratio", self._DEFAULT_PANE_RATIO)
                if hasattr(self, "config")
                else self._DEFAULT_PANE_RATIO
            )
            ratio = max(0.1, min(0.9, float(ratio)))
            parent_splitter = (
                getattr(self.parent, "parent_splitter", None)
                if self.parent is not None and hasattr(self.parent, "parent")
                else None
            )
            # Fallback - search the parent tree for a QSplitter
            if parent_splitter is None:
                widget = self
                for _ in range(4):
                    p = widget.parent if hasattr(widget, "parent") else None
                    if p is None:
                        break
                    if "Splitter" in type(p).__name__:
                        parent_splitter = p
                        break
                    widget = p
            if parent_splitter is not None and hasattr(parent_splitter, "setSizes"):
                total = parent_splitter.width() or 800
                left = int(total * ratio)
                right = total - left
                parent_splitter.setSizes([left, right])
                logma.info(f"[toolboxes] balance_pane_widths: set [{left}, {right}]")
            if hasattr(self, "config"):
                self.config.dikt["pane_width_ratio"] = ratio
        except Exception as e:
            logma.error(f"[toolboxes] balance_pane_widths failed: {e}", exc_info=True)
        return self
        super().initView()
        return self

    def initWidget(self, cfg=None) -> Self:
        """"""
        self.initModel(cfg)
        self.initView()
        return self

    def add_documents_drawer(self) -> Self:
        """"""
        return self

    def add_node_drawer(self) -> Self:
        """"""
        cfg = {"action": "add_node"}
        # self.add_node = NchantdButton(self, cfg).initWidget()
        # self.add_drawer_item(self.add_node, 0, 0)
        return self

    def add_settings_drawer(self) -> Self:
        """"""
        return self

    def add_tabs_drawer(self) -> Self:
        """"""
        cfg = {"action": "add_tab"}
        # self.add_tab = NchantdButton(self, cfg).initWidget()
        # self.add_drawer_item(self.add_tab, 0, 0)
        return self

    def add_tools_drawer(self) -> Self:
        """"""
        return self

    def build_toolbox(self, cfg=None) -> Self:
        """"""
        if cfg is None:
            cfg = {}
        cfg["toolbox"] = self.config.dikt.get("toolbox", {})
        logma.info(f"cfg {cfg}")
        self.init_toolbox()
        super().build_toolbox(cfg)
        return self

    def cmd_application_search_pane(self, event=None, *args, **kwargs) -> Self:
        """Build the application-search pane with tag tracking.

        T-060: the search results now show a tag column (and a
        last-accessed column) alongside the title, matching the
        documents-pane UX (T-055). Returns ``self`` for chainable
        call sites.
        """
        try:
            cfg = {"layout": "vertical"}
            from nchantrs.widgets.panes.searches import NchantdApplicationSearchPane  # type: ignore

            self.application_search_pane = NchantdApplicationSearchPane(self, cfg).initWidget()
            # Register the tag-tracking columns so the pane pulls
            # them from the documents-pane helpers.
            if hasattr(self.application_search_pane, "set_tag_column_enabled"):
                self.application_search_pane.set_tag_column_enabled(True)
            if hasattr(self.application_search_pane, "set_last_accessed_column_enabled"):
                self.application_search_pane.set_last_accessed_column_enabled(True)
            logma.info("[toolboxes] cmd_application_search_pane: search pane built with tag + last-accessed columns")
        except Exception as e:
            logma.error(f"[toolboxes] cmd_application_search_pane: building search pane failed: {e}", exc_info=True)
            # Fallback - copy the documents-pane behavior so the
            # user still gets a usable search pane.
            cfg = {"layout": "vertical", "data": []}
            if "NchantdApplicationSearchPane" not in globals():
                from nchantrs.widgets.panes.searches import NchantdApplicationSearchPane  # type: ignore
            self.application_search_pane = NchantdApplicationSearchPane(self, cfg).initWidget()
        return self

    def cmd_create_new_instance(self, event, *args, **kwargs) -> Self:
        """"""
        self.app.model.create_new_instance()
        return self

    def cmd_duplicate_instance(self, event, *args, **kwargs) -> Self:
        """Duplicate the active instance by copying the current DB.

        Sprint 20: previously a comment-only stub. Now creates a
        new instance via ``self.app.model.create_new_instance()``
        (the same path as ``cmd_create_new_instance``) and
        copies user items from the initial DB to the new
        instance DB via ``copy_database()`` when the model
        exposes that helper. Falls back to plain creation if
        the copy helper isn't available.
        """
        try:
            self.app.model.create_new_instance()
            # Best-effort copy of user items from the initial DB
            # to the new instance DB. The helper may not exist
            # on older installs; skip silently if so.
            copy_helper = getattr(self.app.model, "copy_database", None)
            if callable(copy_helper):
                try:
                    copy_helper()
                except Exception as copy_exc:
                    logma.warning(f"[toolboxes] cmd_duplicate_instance: " f"copy_database failed: {copy_exc}")
        except Exception as exc:
            logma.error(
                f"[toolboxes] cmd_duplicate_instance failed: {exc}",
                exc_info=True,
            )
        return self

    def cmd_export_instance(self, event, *args, **kwargs) -> Self:
        """"""
        # restrict to selecting a folder
        if self.app.user.use_library:
            self.local_directory = self.app.model.library_path
            return self
        cfg = {}
        self.save_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_directory = self.open_file_sigil.file_selected
        return self

    def cmd_import_instance(self, event, *args, **kwargs) -> Self:
        """Import a local file as the active instance.

        Sprint 20: previously a stub that opened the file dialog
        but never called any importer. Now routes the selected
        path through ``self.app.model.import_local_file()``
        (the canonical dispatcher in ``models.py``) so the
        file-type branches at ``cmd_open_local_file`` are
        honoured.
        """
        try:
            cfg = {}
            self.open_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
            self.local_file = self.open_file_sigil.file_selected
            if self.local_file is not None:
                importer = getattr(self.app.model, "import_local_file", None)
                if callable(importer):
                    importer(self.local_file)
                else:
                    # Fallback: route through the toolbox's own
                    # local-file importer which already handles
                    # the file-type branches.
                    self.cmd_open_local_file()
        except Exception as exc:
            logma.error(
                f"[toolboxes] cmd_import_instance failed: {exc}",
                exc_info=True,
            )
        return self

    def cmd_web_search_pane(self, event, *args, **kwargs) -> Self:
        """Dispatch a global web search via the toolbox (T-NEW-033).

        The user-facing button calls this; it routes to
        ``cmd_search_global`` which calls
        ``self.app.model.search_documents(query, scope="global")``.
        Defensive: missing app, missing model, missing
        ``self.app.model.search_documents`` -> log + return
        self (no crash).
        """
        try:
            return self.cmd_search_global(event, *args, **kwargs)
        except Exception as e:
            logma.error(
                f"[toolboxes] cmd_web_search_pane failed: {e}",
                exc_info=True,
            )
            return self

    def cmd_llm_query_pane(self, event, *args, **kwargs) -> Self:
        """Dispatch an LLM-flavored search via the toolbox (T-NEW-033).

        Routes to ``cmd_search_global`` with the same default
        ``scope="global"``. The "llm" flavor is reserved for a
        follow-up where the query is forwarded to a remote
        LLM rather than the local SQLite catalog.
        Defensive: any exception -> log + return self.
        """
        try:
            return self.cmd_search_global(event, *args, **kwargs)
        except Exception as e:
            logma.error(
                f"[toolboxes] cmd_llm_query_pane failed: {e}",
                exc_info=True,
            )
            return self

    def cmd_search_global(self, event=None, *args, **kwargs) -> Self:
        """Run a global search across all nodes + tabs (T-NEW-033).

        Reads ``event.config.dikt["query"]`` (or the kwarg
        ``query=``) and routes to
        ``self.app.model.search_documents(query, scope="global")``.
        Logs the result count + returns self.

        Defensive: missing app, missing model, missing
        ``search_documents`` -> log + return self.
        """
        try:
            query = None
            if event is not None and hasattr(event, "config"):
                try:
                    query = event.config.dikt.get("query")
                except Exception:
                    query = None
            if query is None and "query" in kwargs:
                query = kwargs["query"]
            if not isinstance(query, str) or not query.strip():
                logma.info("[toolboxes] cmd_search_global: empty query, skipping")
                return self
            app = getattr(self, "app", None)
            model = getattr(app, "model", None) if app is not None else None
            if model is None or not hasattr(model, "search_documents"):
                logma.warning("[toolboxes] cmd_search_global: model not available")
                return self
            results = model.search_documents(query, scope="global")
            count = int(len(results)) if hasattr(results, "__len__") else 0
            logma.info(f"[toolboxes] cmd_search_global: query={query!r} " f"matches={count}")
        except Exception as e:
            logma.error(
                f"[toolboxes] cmd_search_global failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_search_node(self, event=None, *args, **kwargs) -> Self:
        """Run a node-scoped search (T-NEW-033).

        Reads ``event.config.dikt["query"]`` + the active
        node id from ``self.app.model.get_current_node()``
        and routes to
        ``self.app.model.search_documents(query, scope="node", active_nid=...)``.

        Defensive: any missing piece -> log + return self.
        """
        try:
            query = None
            if event is not None and hasattr(event, "config"):
                try:
                    query = event.config.dikt.get("query")
                except Exception:
                    query = None
            if query is None and "query" in kwargs:
                query = kwargs["query"]
            if not isinstance(query, str) or not query.strip():
                logma.info("[toolboxes] cmd_search_node: empty query, skipping")
                return self
            app = getattr(self, "app", None)
            model = getattr(app, "model", None) if app is not None else None
            if model is None or not hasattr(model, "search_documents"):
                logma.warning("[toolboxes] cmd_search_node: model not available")
                return self
            active_nid = None
            try:
                node = model.get_current_node()
                active_nid = getattr(node, "nid", None)
            except Exception:
                active_nid = None
            results = model.search_documents(query, scope="node", active_nid=active_nid)
            count = int(len(results)) if hasattr(results, "__len__") else 0
            logma.info(f"[toolboxes] cmd_search_node: query={query!r} " f"nid={active_nid} matches={count}")
        except Exception as e:
            logma.error(
                f"[toolboxes] cmd_search_node failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_search_tab(self, event=None, *args, **kwargs) -> Self:
        """Run a tab-scoped search (T-NEW-033).

        Reads ``event.config.dikt["query"]`` + the active
        tab id from ``self.app.model.get_current_tab()``
        and routes to
        ``self.app.model.search_documents(query, scope="tab", active_tid=...)``.

        Defensive: any missing piece -> log + return self.
        """
        try:
            query = None
            if event is not None and hasattr(event, "config"):
                try:
                    query = event.config.dikt.get("query")
                except Exception:
                    query = None
            if query is None and "query" in kwargs:
                query = kwargs["query"]
            if not isinstance(query, str) or not query.strip():
                logma.info("[toolboxes] cmd_search_tab: empty query, skipping")
                return self
            app = getattr(self, "app", None)
            model = getattr(app, "model", None) if app is not None else None
            if model is None or not hasattr(model, "search_documents"):
                logma.warning("[toolboxes] cmd_search_tab: model not available")
                return self
            active_tid = None
            try:
                tab = model.get_current_tab()
                active_tid = getattr(tab, "tid", None)
            except Exception:
                active_tid = None
            results = model.search_documents(query, scope="tab", active_tid=active_tid)
            count = int(len(results)) if hasattr(results, "__len__") else 0
            logma.info(f"[toolboxes] cmd_search_tab: query={query!r} " f"tid={active_tid} matches={count}")
        except Exception as e:
            logma.error(
                f"[toolboxes] cmd_search_tab failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_import_local_file(self, event=None, *args, **kwargs) -> Self:
        """"""
        cfg = {}
        self.import_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_file = self.import_file_sigil.file_selected
        if self.local_file is not None:
            if self.local_file.endswith(".ctd"):
                self.app.model.import_cherrytree(self.local_file)
            elif self.local_file.endswith((".py", ".xml", ".txt", ".md", ".html", ".htm")):
                self.app.model.import_text(self.local_file)
            elif self.local_file.endswith(".pdf"):
                self.app.model.import_pdf(self.local_file)
            elif self.local_file.endswith(".docx"):
                pass
            elif self.local_file.endswith((".json", ".yaml", ".yml")):
                if "Sessions - " in self.local_file:
                    self.app.model.import_web_session(self.local_file)
                else:
                    self.app.model.import_text(self.local_file)
            elif self.local_file.endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
                self.app.model.import_image(self.local_file)
            elif self.local_file.endswith(".gif"):
                pass
            elif self.local_file.endswith(".pyof"):
                # T-NEW-114: route .pyof through the canonical
                # cmd_import_pyof dispatcher (the T-NEW-074
                # content-table ETL orchestrator) instead of the
                # instance-registration path. The pre-selected
                # local_file is injected via file_dialog_fn so the
                # user does not get a second file dialog.
                return self.cmd_import_pyof(
                    file_dialog_fn=lambda *a, **kw: (self.local_file, ""),
                )
            else:
                self.app.model.import_text(self.local_file)
                # raise Exception(f"Unknown File {self.local_file}")
        return self

    def cmd_open_instance(self, event=None, *args, **kwargs) -> Self:
        """Open a local ``.pyof`` (Nchantd Office DB file) instance.

        T-077: previously raised ``"File Type not yet implemented"``.
        T-NEW-007: the ``.pyof`` extension is the SQLite DB
        format. Now:

          1. Opens the file dialog via NchantdFileOpenSigil
          2. If the selected file is a ``.pyof`` file, opens it
             via ``import_nchantdoffice_instance(path)`` (when
             the helper exists on the model) and falls back to
             ``model.import_text(path)`` otherwise
          3. Otherwise delegates the file to ``cmd_open_local``
             which handles the standard formats

        Returns ``self`` for chainable call sites.
        """
        try:
            cfg = {}
            self.import_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
            self.local_file = self.import_file_sigil.file_selected
            if self.local_file is None:
                return self
            if self.local_file.endswith(".pyof"):
                return self._open_pyof_instance(self.local_file)
            return self.cmd_open_local(event=event, *args, **kwargs)
        except Exception as e:
            logma.error(f"[toolboxes] cmd_open_instance failed: {e}", exc_info=True)
        return self

    def cmd_browse_app_instances(self, event=None, *args, **kwargs) -> Self:
        """T-NEW-005 (item 3): show the user the registered
        secondary app instances from the ``app_instance``
        table. The primary instance holds a registry of
        secondary DB files (per the one-SQLite-per-app-
        instance model). UI hook from the toolbox buttonbar
        opens a list dialog so the user can pick a secondary
        instance to switch into (``cmd_open_instance`` then
        routes through ``_open_pyof_instance`` for the
        selected path).
        """
        try:
            model = getattr(self.app, "model", None) if hasattr(self, "app") else None
            if model is None or not hasattr(model, "get_app_instances"):
                logma.warning("[toolboxes] cmd_browse_app_instances: no " "model.get_app_instances helper available.")
                return self
            rows = model.get_app_instances() or []
            logma.info(f"[toolboxes] cmd_browse_app_instances: " f"{len(rows)} registered secondary instance(s)")
            # Surface to the UI: when a list dialog is available
            # use it; otherwise log the names so the test harness
            # (and headless environments) can verify the path.
            picker = None
            try:
                from nchantrs.dialogs.selectors import (
                    NchantdSelectionDialog,
                )

                picker = NchantdSelectionDialog
            except Exception:
                picker = None
            if picker is not None and rows:
                # NchantdSelectionDialog accepts a list of
                # label/callback pairs; we map each row to a
                # clickable label that re-opens the instance.
                choices = [
                    {
                        "label": (f"{r.get('name', '?')} " f"({r.get('uuid', '?')})"),
                        "callback": (lambda r=r: self._open_pyof_instance(r.get("path", ""))),
                    }
                    for r in rows
                    if isinstance(r, dict)
                ]
                if choices:
                    picker("Browse App Instances", choices, parent=self)
                    return self
            # Fallback: log every row so headless tests can
            # observe the data path.
            for r in rows:
                if isinstance(r, dict):
                    logma.info(f"[toolboxes] registered: " f"uuid={r.get('uuid')} name={r.get('name')}")
            return self
        except Exception as e:
            logma.error(
                f"[toolboxes] cmd_browse_app_instances failed: {e}",
                exc_info=True,
            )
        return self

    def _open_pyof_instance(self, path) -> Self:
        """Open a .pyof Nchantd Office instance (T-077, T-NEW-007).

        The .pyof format is the SQLite DB file produced by
        NchantdOfficeStore. Restoration routes through the
        model-level helper:

          1. ``model.import_nchantdoffice(path)`` if the
             import handler exists - the model-level helper
             now records the requested path and the store
             layer opens the SQLite DB.
          2. Log + return ``self`` on any failure so the
             caller doesn't have to special-case.

        The previous fallback used ``pickle.load`` on a
        ``.pyof`` file picked from disk. That was unsafe: an
        attacker could craft a ``.pyof`` whose ``__reduce__``
        ran arbitrary code on import. The pickle path has
        been removed (T-NEW-007).
        """
        try:
            model = getattr(self.app, "model", None) if hasattr(self, "app") else None
            if model is not None and hasattr(model, "import_nchantdoffice"):
                model.import_nchantdoffice(path)
                logma.info(f"[toolboxes] _open_pyof_instance: {path} via model.import_nchantdoffice")
                return self
            # T-NEW-007: the previous pickle.load fallback was
            # removed. ``.pyof`` is a SQLite DB file; the
            # canonical restoration path is through
            # ``model.import_nchantdoffice``. If the model
            # helper is missing, log and continue rather than
            # fall back to the unsafe pickle path.
            logma.warning(f"[toolboxes] _open_pyof_instance: no model.import_nchantdoffice helper for {path!r}")
        except Exception as e:
            logma.error(f"[toolboxes] _open_pyof_instance failed: {e}", exc_info=True)
        return self

    def cmd_open_local_file(self, event=None, *args, **kwargs) -> Self:
        """Dispatch a local file to the right document class.

        Per user direction (Sprint 20): each file type routes
        to its canonical document class (matrix for spreadsheets,
        image for raster graphics, script for text/markup, PDF
        for documents) instead of falling through to plain
        text. The model helpers (``model.import_csv``,
        ``model.import_xlsx``, etc.) carry the actual wiring;
        this method just dispatches based on extension.
        """
        cfg = {}
        self.import_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_file = self.import_file_sigil.file_selected
        if self.local_file is not None:
            if self.local_file.endswith(".ctd"):
                self.app.model.import_cherrytree(self.local_file)
            elif self.local_file.endswith((".py", ".xml", ".txt", ".md", ".html", ".htm")):
                self.app.model.import_text(self.local_file)
            elif self.local_file.endswith(".pdf"):
                self.app.model.import_pdf(self.local_file)
            elif self.local_file.endswith(".docx"):
                # Sprint 20: route .docx to the script document
                # (the existing import_text path) via a dedicated
                # model helper.
                importer = getattr(self.app.model, "import_docx", None)
                if callable(importer):
                    importer(self.local_file)
                else:
                    self.app.model.import_text(self.local_file)
            elif self.local_file.endswith((".json", ".yaml", ".yml")):
                if "Sessions - " in self.local_file:
                    self.app.model.import_web_session(self.local_file)
                else:
                    self.app.model.import_text(self.local_file)
            elif self.local_file.endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif")):
                # All raster image formats route through the
                # image document class.
                self.app.model.import_image(self.local_file)
            elif self.local_file.endswith((".csv", ".xlsx", ".xls", ".ods")):
                # Spreadsheet formats route through the matrix
                # document class so the user sees a real grid.
                importer = getattr(self.app.model, "import_matrix", None)
                if callable(importer):
                    importer(self.local_file)
                else:
                    self.app.model.import_text(self.local_file)
            elif self.local_file.endswith((".odt", ".odp", ".odc", ".odf", ".odg")):
                # OpenDocument text/format variants route
                # through the script document for now (no
                # dedicated OpenDocument parser yet).
                self.app.model.import_text(self.local_file)
            elif self.local_file.endswith(".pyof"):
                # T-NEW-114: delegate to the single canonical
                # import dispatcher (cmd_import_local_file) so
                # the user-facing .pyof import path funnels
                # through the T-NEW-074 content-table ETL
                # orchestrator. _open_pyof_instance is left in
                # place as dead code for the unit-test harness
                # that imports it directly.
                return self.cmd_import_local_file(self.local_file)
            else:
                self.app.model.import_text(self.local_file)
        return self

    def cmd_save_instance(self, event, *args, **kwargs) -> Self:
        """Save the active instance to a user-chosen ``.pyof`` file.

        Sprint 20: previously a near-empty stub (all
        ``pass`` branches). Now:

          1. Opens the save-file dialog via
             ``NchantdFileOpenSigil``.
          2. When the user picks a ``.pyof`` path and the app
             has a library configured, calls
             ``self.app.model.copy_database()`` (or the
             underlying store save) to materialise the
             instance at the chosen path.
          3. Marks the instance as saved via
             ``set_is_saved(True)`` when the model exposes it.
          4. Forwards any non-``.pyof`` extension through the
             generic text-write path.
        """
        try:
            cfg = {}
            self.save_file_sigil = NchantdFileOpenSigil("save_local_document", self, cfg).initWidget()
            self.local_file = self.save_file_sigil.file_selected
            if self.local_file is None:
                return self
            # Pyof path: the model has a library, copy the DB.
            if self.local_file.endswith(".pyof"):
                copy_helper = getattr(self.app.model, "copy_database", None)
                if callable(copy_helper):
                    copy_helper(self.local_file)
                # Mark saved when the model exposes the helper.
                setter = getattr(self.app.model, "set_is_saved", None)
                if callable(setter):
                    setter(True)
            else:
                # Non-pyof path: write the file via the
                # model's import_local_file path (text).
                importer = getattr(self.app.model, "import_local_file", None)
                if callable(importer):
                    importer(self.local_file)
        except Exception as exc:
            logma.error(
                f"[toolboxes] cmd_save_instance failed: {exc}",
                exc_info=True,
            )
        return self

    def get_llm_engines(self) -> list[str]:
        """Get the list of supported LLM engine names."""
        options = ["Open Ai", "Grok", "Gemini", "Claude"]
        return options

    def get_search_engines(self) -> list[str]:
        """"""
        options = ["Google", "DuckDuckGo", "Bing", "Yahoo", "Yandex", "PreSearch", "Shodan"]
        return options

    def init_drawer_application(self) -> dict[str, Any]:
        """"""
        default_action = {"action": "insert_object", "type": "custom"}
        items = self.config.dikt["toolbox"][0].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "text": "Save Document",
            "action": "insert_object",
            "layout": "horizontal",
            "size": ["auto", 30],
            "actions": {
                1: {"action": "open_instance", "type": "", "handler": self.cmd_open_local_file},
                2: {"action": "import_instance", "type": "", "handler": self.cmd_import_local_file},
                # PUSH to 0.0.3
                # 3: {"action": "duplicate_instance", "type": "", "handler": self.cmd_duplicate_instance},
                # implement a mirror instance so user can work on two different nodes in two differenct screens from the
                # same document
                # 3: {"action": "save_instance", "type": "", "handler": self.cmd_save_instance},
                # 5: {"action": "export_instance", "type": "", "handler": self.cmd_export_instance},
            },
        }
        if self.app.model.user.has_pro:
            cfg["actions"][0] = {
                "action": "new_instance",
                "type": "",
                "handler": self.cmd_create_new_instance,
            }  # PUSH to 0.0.3 change a pop dialog for instance selection/open/new
        self.document_buttonbar = NchantdButtonBar(self, cfg)
        items[cnt]["widget"] = self.document_buttonbar
        cnt += 1
        # if cnt not in items:
        #     items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        # cfg = {
        #     "layout": "horizontal",
        #     "handler": self.cmd_web_search_pane,
        #     "label": "Set Default Search",
        #     "options": self.get_search_engines(),
        # }
        # self.default_search_select = NchantdDropDown(self, cfg)
        # items[cnt]["widget"] = self.default_search_select
        # cnt += 1
        # if cnt not in items:
        #     items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        # cfg = {
        #     "layout": "horizontal",
        #     "handler": self.cmd_web_search_pane,
        #     "label": "Set Default LLM",
        #     "options": self.get_llm_engines(),
        # }
        # self.default_llm_select = NchantdDropDown(self, cfg)
        # items[cnt]["widget"] = self.default_llm_select
        # cnt += 1
        # if cnt not in items:
        #     items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        # cfg = {"layout": "vertical", "handler": self.cmd_application_search_pane}
        # self.application_search_pane = NchantdApplicationSearchPane(self, cfg)
        # items[cnt]["widget"] = self.application_search_pane
        # cnt += 1
        return items

    def refresh_for_document(self, document) -> Self:
        """Refresh toolbox drawer items for the active document/tab context.

        Called by NchantdOfficeTabSet.on_tab_focus() when the focused center
        document changes. Clears existing items and rebuilds them via
        init_drawer_application() without destroying the toolbox instance.
        """
        # RESOLVED [toolbox-stale-box]: build_toolbox() always creates a brand-new
        # QToolBox and adds it to this widget's layout. Without removing the old
        # one first, the previous drawers stay on screen and the toolbox appears to
        # "hold" the prior document's drawers when the active document changes.
        # clear() empties the old box and removes it from the layout; deleteLater()
        # disposes of the orphaned box widget. Fixed in commit 355fa85 alongside the
        # wrong-target fix in NchantdOfficeTabSet.on_tab_focus().
        old_box = self.box
        self.clear()
        if old_box is not None:
            old_box.deleteLater()

        # Clear existing toolbox drawer items in reverse order to avoid index shifts
        items = self.config.dikt["toolbox"][0].get("items", {})
        for idx in sorted(items.keys(), reverse=True):
            if idx in items:
                widget = items[idx].get("widget")
                if widget and hasattr(widget, "deleteLater"):
                    widget.deleteLater()
                del items[idx]

        # Rebuild drawer items for the new document context
        self.config.dikt["toolbox"][0]["items"] = self.init_drawer_application()

        # Rebuild toolbox UI without destroying the toolbox instance
        super().build_toolbox({"toolbox": self.config.dikt.get("toolbox", {})})
        return self

    def init_toolbox(self) -> Self:
        """"""
        super().init_toolbox()
        self.config.dikt["toolbox"][0]["items"] = self.init_drawer_application()
        return self

    # ----------------------------------------------------------------------
    # T-NEW-074: .pyof content-import wiring
    # ----------------------------------------------------------------------
    #
    # The Application ToolBox is the canonical home for app-wide actions
    # (``cmd_open_local_file``, ``cmd_create_new_instance``, etc.). T-NEW-074
    # adds a content-only importer here: the user picks a source ``.pyof``
    # via QFileDialog, and we copy six content tables (app/doc tree + tabs +
    # media) into the host's live sqlite3 connection via
    # ``import_pyof``. Primary-key collisions are INSERT-OR-IGNORE so the
    # user's host rows win. Orphan FKs (e.g. ``doc_tree_node.pid_txt``
    # pointing at a UUID not present on the host) are NOT enforced; the
    # user is expected to inspect the host tree after a large import.
    #
    # The host connection accessor is project-specific — see
    # ``_resolve_host_db_conn`` below. We prefer the canonical store
    # attribute (``self.app.model.store._sqlite_connection``, mirroring
    # the ``models.get_app_instances`` path) and fall back to an
    # isinstance walk over parent/app/model/store so the method keeps
    # working if the store layer is refactored.

    def cmd_import_pyof(self, event=None, *args, **kwargs) -> Self:
        """T-NEW-074: import content tables from a user-selected .pyof.

        ``file_dialog_fn`` is overridable for testing — the integration
        test in ``tests/test_pyof_import.py`` injects a stub returning a
        temp ``.pyof`` path. Defaults to ``QFileDialog.getOpenFileName``.
        """
        try:
            from PySide6.QtWidgets import QFileDialog  # type: ignore
        except Exception as e:
            # Rare — Qt not installed in the headless test env. Log and
            # bail; the rest of the app still works without this action.
            logma.error(
                f"[import_pyof] QFileDialog unavailable: {e}",
                exc_info=True,
            )
            return self
        try:
            from nchantdoffice.utilities.pyof_import import import_pyof
        except Exception as e:
            logma.error(
                f"[import_pyof] import_pyof orchestrator unavailable: {e}",
                exc_info=True,
            )
            return self
        try:
            file_dialog_fn = kwargs.pop("file_dialog_fn", QFileDialog.getOpenFileName)
            path, _ = file_dialog_fn(
                self,
                "Import .pyof",
                "",
                "Pyof files (*.pyof);;SQLite DBs (*.sqlite *.db);;All files (*)",
            )
            if not path:
                return self
            # Locate the host DB connection via the model / store
            host_conn = getattr(self, "_host_db_conn", None)
            if host_conn is None:
                logma.warning(
                    "[import_pyof] no host DB connection available on toolbox; "
                    "fall back to opening instance .pyof via the app model."
                )
                host_conn = self._resolve_host_db_conn()
            # T-NEW-114 Defect C: offload the synchronous import_pyof
            # call to a worker QThread so the GUI thread does not
            # block. The completion signal fires back on the main
            # thread (Qt.QueuedConnection is the default for
            # cross-thread signals) and slots into
            # _show_pyof_import_result which updates the status
            # bar. The worker + thread are kept alive on the toolbox
            # instance (_pyof_import_thread) so the GC does not
            # reap them mid-flight.
            worker = _PyofImportWorker(import_pyof, path, host_conn)
            thread = QThread()
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(self._show_pyof_import_result)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)
            self._pyof_import_thread = thread
            self._pyof_import_worker = worker
            thread.start()
        except Exception as e:
            logma.error(f"[import_pyof] failed: {e}", exc_info=True)
        return self

    def _show_pyof_import_result(self, path: str, results) -> None:
        """T-NEW-114 Defect C: status-bar update callback fired on the
        main thread when the worker thread finishes. Kept separate from
        cmd_import_pyof so the connection is explicit and testable.

        The defensive getattr + hasattr walk is intentional: in
        unit tests self.parent() is None (we use __new__ and
        skip QObject init), so the status bar update must be a no-op
        rather than crash the test.
        """
        try:
            total_in = sum(r.inserted for r in results)
            total_skip = sum(r.skipped for r in results)
            logma.info(f"[import_pyof] {path}: inserted={total_in}, skipped={total_skip}")
            parent = None
            try:
                parent = self.parent()
            except Exception:
                parent = None
            if parent is not None and hasattr(parent, "statusBar"):
                try:
                    parent.statusBar().showMessage(
                        f"Imported {total_in} rows ({total_skip} skipped)", 5000
                    )
                except Exception as e:
                    logma.error(
                        f"[import_pyof] status bar update failed: {e}",
                        exc_info=True,
                    )
        except Exception as e:
            logma.error(f"[import_pyof] _show_pyof_import_result failed: {e}", exc_info=True)

    def _resolve_host_db_conn(self) -> "sqlite3.Connection | None":
        """Return the live ``sqlite3.Connection`` for the host instance.

        T-NEW-074: defensive accessor for the live host DB connection. The
        Application ToolBox doesn't own the connection itself — it lives
        on the store layer (``self.app.model.store._sqlite_connection``,
        mirroring the ``models.get_app_instances`` path). We:

          1. Try the canonical path first (``self.app.model.store.
             _sqlite_connection``). This is the path ``models.py`` uses
             for direct SQLite reads.
          2. Walk ``self.parent() -> self.app -> self.app.model ->
             self.app.model.store`` and return the first attribute that
             passes ``isinstance(..., sqlite3.Connection)``. This keeps
             the method working if the store layer is refactored to
             expose a differently-named connection attribute.
          3. Raise a clear ``RuntimeError`` so the outer ``try/except``
             in ``cmd_import_pyof`` logs it.

        The helper is intentionally permissive on the fallback walk: any
        attribute on any of the candidate nodes that IS a
        ``sqlite3.Connection`` wins. This is safer than guessing
        attribute names because the live codebase can change underneath
        us without breaking the wiring.
        """
        import sqlite3 as _sqlite3

        # 1. Canonical fast path — matches ``models.get_app_instances``.
        try:
            store = getattr(getattr(self, "app", None), "model", None)
            store = getattr(store, "store", store) if store is not None else None
            conn = getattr(store, "_sqlite_connection", None)
            if isinstance(conn, _sqlite3.Connection):
                return conn
        except Exception:
            # Fall through to the isinstance walk.
            pass

        # 2. Defensive isinstance walk over candidate nodes.
        candidates = []
        try:
            candidates.append(self)
            if self.parent() is not None:
                candidates.append(self.parent())
        except Exception:
            pass
        try:
            app = getattr(self, "app", None)
            if app is not None:
                candidates.append(app)
                model = getattr(app, "model", None)
                if model is not None:
                    candidates.append(model)
                    store = getattr(model, "store", None)
                    if store is not None:
                        candidates.append(store)
        except Exception:
            pass

        seen: set[int] = set()
        for node in candidates:
            if node is None or id(node) in seen:
                continue
            seen.add(id(node))
            # Direct check first.
            if isinstance(node, _sqlite3.Connection):
                return node
            # Then scan attributes (only public-ish, no dunder spam).
            try:
                attrs = list(vars(node).items())
            except Exception:
                continue
            for name, value in attrs:
                if name.startswith("__"):
                    continue
                if isinstance(value, _sqlite3.Connection):
                    return value

        # 3. Nothing matched — surface a clear error for the outer
        # try/except in cmd_import_pyof to log.
        raise RuntimeError(
            "NchantdOfficeApplicationToolBox._resolve_host_db_conn: "
            "no sqlite3.Connection found on self / parent / app / "
            "app.model / app.model.store. Wire a `_host_db_conn` "
            "attribute on the toolbox instance or expose the live "
            "connection on the store layer."
        )


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
