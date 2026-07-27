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

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.utilities.utils import lookup
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.panes.catalogs import NchantdNewNodePane
from nchantrs.dialogs.files import NchantdFileOpenSigil
from nchantdoffice.dialogs.imports import NchantdGoogleDriveSigil
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.checkboxes import NchantdCheckboxGroup, NchantdCheckbox
from nchantrs.widgets.controls.radios import NchantdRadioButtonGroup
from pyffice.web.url import PyfficeURL
from kahndor.logma import Logma
from subtrix.utilities import uuid

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "new.yaml")


class NchantdOfficeNewDocumentPane(NchantdNewNodePane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeNewDocumentPane").override(cfg))
        self.connect_gfile = None
        self.open_file = None
        self.file_path = None
        self.import_file = None
        self.unique_options = None
        self.multiple_options = None
        self.file_path_label = None

    def initModel(self):
        """"""
        super().initModel()

        return self

    def initView(self):
        """
        :param file_type:
        :return:
        """
        logma.info(f"Ran")
        super().initView()
        # if self.active_item is not None:
        #     self.update_pane(self.active_item)
        return self

    def accept(self, action=None, app=None, params=None):
        """
        :return:
        """
        logma.info("New Document Accept")
        self.ok = True
        super().accept()
        self.unshow_file_path()
        self.update_pane()
        return self

    def add_document(self, tabset, widgdata=None, db="db"):
        """"""
        logma.info(f"Widgdata {widgdata}")
        if widgdata is None:
            widgdata = self.active_item.action.action["parameters_dict"]
            logma.info(f"Widgdata {widgdata}")
        if self.ok:
            name = self.tab_name_entry.textbox.entry_data
            pid = self.app.view.panes["left"].tree.model.current_node.nid
            self.app.view.panes[tabset].model.max_position += 1
            pos = self.app.view.panes[tabset].model.max_position
            document_nm = self.active_item.document_nm
            widget = self.active_item.widget
            # widgdata = kahndor.Instruct().override(widgdata).dikt
            # if self.active_item.selected_unique_option is not None:
            #     if self.active_item.selected_unique_option.get("widget_code", None):
            #         widget = lookup_widget(self.active_item.selected_unique_option["widget_code"])
            did = self.active_item.did
            context = ""
            content = {}
            syntax = ""
            doc_type = self.active_item.action.action["lookup_code_txt"]
            if "add_http_media" in doc_type:
                logma.info(f"Widgdata {widgdata}")
                link = PyfficeURL(self.active_item.params)
                link.load_unit()
                content = link.to_dict()
                code = self.active_item.params.get("url_code", None)
                if code is None:
                    code = self.active_item.params.get("file_type", None)
                content["unit"]["original_path"] = self.app.model.get_link(code)
                logma.info(f"Content {content}")
            document = {
                "name": name,
                "description": "",
                "widget": widget,
                "type": doc_type,
                "did": did,
                "pid": pid,
                "tid": uuid(),
                "position": pos,
                "tabset": "center",
                "context": context,
                "version": 0,
                "hash": "",
                "policy_fk": None,
                "content": content,
                "syntax": syntax,
            }
            self.app.model.add_document(document, did, pid, pos, widget, widgdata, doc_type, tabset, db, True)
            self.app.view.panes["left"].tree.model.current_node.updateTabs(tabset)
        return self

    def add_node(self, tree="left", widgdata=None):
        """"""
        super().add_node(tree, widgdata)
        return self

    def add_note(self):
        """"""
        name = self.active_item.name
        pid = self.app.view.panes["left"].tree.model.current_node.nid
        position = self.app.view.gui.set_position("right")
        widgdata = {}
        self.app.model.add_note(name, pid, position, widgdata)
        return self

    def add_subtree(self):
        """"""
        super().add_subtree()
        # mass create one or more nodes and associated tabs
        # use this for import of cherrytree
        # use this for research subtree
        """
        """
        d = {
            "unique_options": [
                {"name": "Decade"},
                {"name": "Year"},
                {"name": "Month"},
                {"name": "Week"},
                {"name": "Day"},
            ]
        }
        return self

    def add_tab(self, tabset, widgdata=None):
        """"""
        if widgdata is None:
            widgdata = {}
        # widgdata["doc_type"] = self.active_item.document_nm
        if self.active_item.document_txt in ("http", "api"):
            for key, item in self.active_item.params.items():
                logma.info(f"Key {key} Item {item}")
                widgdata[key] = item
            # widgdata["url_code"] = self.active_item.params.get("url_code", None)
            # widgdata["is_app"] = self.active_item.params.get("is_app", None)
        # T-050: unified format -> tool-type routing table.
        # Maps each supported document_format to the right
        # ``widget_code`` and ``load_strategy`` so the same add_tab
        # pipeline works for local files, remote APIs, and web apps.
        if self.open:
            widgdata["path"] = self.file_path.file_selected
        widget_code = self._resolve_widget_code(widgdata)
        if widget_code:
            widgdata["widget_code"] = widget_code
        load_strategy = self._resolve_load_strategy(widgdata)
        if load_strategy:
            widgdata["load_strategy"] = load_strategy
        super().add_tab(tabset, widgdata)
        # T-052: per-document-type widget_code override. If the
        # active item's widget has its own override (e.g. a
        # spreadsheet that always uses a local-excel widget), apply
        # it after the routing-table pass.
        if self.active_item is not None:
            override = getattr(self.active_item, "widget_code_override", None)
            if override:
                widgdata["widget_code"] = override
        return self

    def add_research_subtree(self, topic):
        """"""
        subtree = self.config.dikt["subtrees"]["research"]["dstruct"]["<topic>"]["nodes"]
        details = {"<[topic]>": topic}
        for key, val in subtree.items():
            self.add_node(key)
            if val == "tabs":
                for tab in subtree[key]:
                    self.add_tab(tab)

    def add_bulk_node(self):
        """"""

    def add_bulk_tab(self):
        """"""

    def load_document(self):
        """"""
        self.document_obj = self.widget.open(self.active_item.file_path)
        return self

    def open_file_sigil(self, name=None, app=None, cfg=None):
        """"""
        file_sigil = NchantdFileOpenSigil("open", self.parent, self.config.override(cfg))
        self.file_path = file_sigil.initWidget()
        if self.file_path.file_selected:
            self.show_file_path()
            self.load_google = False
        return self

    def open_google_drive_viewer(self, name=None, app=None, cfg=None):
        """"""
        gdrive_sigil = NchantdGoogleDriveSigil(self.parent, self.config.override(cfg))
        self.gdrive_path = gdrive_sigil.initWidget()
        if self.ok:
            self.gdrive_path.file_selected
            self.show_file_path()
            self.load_google = True
        return self

    def show_checkboxes(self):
        """"""
        return self

    def show_file_path(self):
        """"""
        logma.info(f"File Path {self.file_path.file_selected}")
        cfg = {"text": self.file_path.file_selected, "readonly": True, "size": [600, 0]}
        self.file_path_label = NchantdLabel(self, self.config.override(cfg)).initWidget()
        self.left_side_layout.addWidget(self.file_path_label)
        # self.add_field(self.file_path_label)
        # need to load the file and determine if there are multiple pages/tabs like an excel file
        # if there are then a selection list is presented for each page/tab
        self.open = True
        self.new = False
        return self

    def unshow_file_path(self):
        """"""
        if self.file_path_label is not None:
            self.left_side_layout.removeWidget(self.file_path_label)
            self.file_path_label.setParent(None)
            self.file_path_label.deleteLater()
            self.file_path_label = None
            self.open = False
            self.new = True
        return self

    def show_google_drive_button(self):
        """"""
        if self.connect_gfile is not None:
            return self
        gdocs = {
            "script": "docs",
            "matrix": "sheets",
            "image": "drive",
            "form": "forms",
            "pdf": "drive",
            "notebook": "drive",
            "video": "drive",
        }
        gtype = gdocs.get(self.active_item.document_txt, None)
        if gtype is None:
            self.unshow_google_drive_button()
            # raise Exception(f"Google Doc Type Not Supported {self.active_item.document_nm}")
        command = f"load_google_{gtype}"
        self.config.override({"buttons": {command: lookup(self.app, command)}})
        self.config.dikt["action"] = self.config.dikt["buttons"][command]["lookup_code_txt"]

        self.connect_gfile = NchantdButton(self, self.config.dikt["buttons"][command]).initWidget()
        self.connect_gfile.set_handler(self.open_google_drive_viewer, self.config.dikt)
        self.document_buttons_layout.addWidget(self.connect_gfile)
        return self

    def show_import_file_button(self):
        """"""
        if self.import_file is not None:
            return self
        self.app.model.has_library = True
        if self.app.model.has_library:
            command = f"import_{self.active_item.file_type}"
            self.config.override({"buttons": {command: lookup(self.app, command)}})
            self.config.dikt["action"] = self.config.dikt["buttons"][command]["lookup_code_txt"]
            self.import_file = NchantdButton(self, self.config.dikt["buttons"][command]).initWidget()
            self.import_file.set_handler()
            self.document_buttons_layout.addWidget(self.import_file)
        return self

    def show_local_drive_button(self):
        """"""
        if self.open_file is not None:
            return self
        logma.info(f"Action open_{self.active_item.file_type}")
        self.open_file = NchantdButton(self, {"action": f"open_{self.active_item.file_type}"}).initWidget()
        params = self.config
        self.open_file.set_handler(self.open_file_sigil, params)
        self.document_buttons_layout.addWidget(self.open_file)
        return self

    def show_multiple_options(self):
        """"""
        if self.multiple_options is not None:
            return self
        logma.info(f"Multiple Options {self.active_item.multi_options}")
        cfg = {"text": "Select Parameters", "multiple_options": [x["name"] for x in self.active_item.multi_options]}
        self.multiple_options = NchantdCheckboxGroup(self, cfg)
        self.multiple_options.initWidget()
        self.center_layout.addWidget(self.multiple_options)

    def show_radio_buttons(self):
        """"""
        if self.unique_options is not None:
            return self
        logma.info(f"Unique Options {self.active_item.unique_options}")
        cfg = {"text": "Select Option", "unique_options": [x["name"] for x in self.active_item.unique_options]}
        self.unique_options = NchantdRadioButtonGroup(self, cfg)
        self.unique_options.initWidget()
        self.center_layout.addWidget(self.unique_options)
        return self

    def unshow_local_drive_button(self):
        """"""
        if self.open_file is not None:
            self.document_buttons_layout.removeWidget(self.open_file)
            self.open_file.setParent(None)
            self.open_file.deleteLater()
            self.open_file = None

    def unshow_google_drive_button(self):
        """

        :return:
        """
        if self.connect_gfile is not None:
            self.document_buttons_layout.removeWidget(self.connect_gfile)
            self.connect_gfile.setParent(None)
            self.connect_gfile.deleteLater()
            self.connect_gfile = None
        return self

    def unshow_import_file_button(self):
        """"""
        if self.import_file is not None:
            self.document_buttons_layout.removeWidget(self.import_file)
            self.import_file.setParent(None)
            self.import_file.deleteLater()
            self.import_file = None
        return self

    def unshow_unique_options(self):
        """"""
        if self.unique_options is not None:
            self.center_layout.removeWidget(self.unique_options)
            self.unique_options.setParent(None)
            self.unique_options.deleteLater()
            self.unique_options = None

    def unshow_muliple_options(self):
        """"""
        if self.multiple_options is not None:
            self.center_layout.removeWidget(self.multiple_options)
            self.multiple_options.setParent(None)
            self.multiple_options.deleteLater()
            self.multiple_options = None

    def update_checkboxes(self):
        """"""
        if self.active_item.has_multiple_options:
            self.show_checkboxes()
        return self

    def update_file_buttons(self):
        """"""
        logma.info(f"Update File Buttons {self.active_item.has_google_options}")
        if self.active_item.has_google_options:
            self.show_google_drive_button()
        else:
            self.unshow_google_drive_button()
        if self.active_item.has_local_options:
            self.show_local_drive_button()
            self.show_import_file_button()
        else:
            self.unshow_local_drive_button()
            self.unshow_import_file_button()
        return self



    # T-050: format -> tool-type routing table. Keys are document
    # formats (file extensions or API identifiers); values are the
    # ``widget_code`` to instantiate + ``load_strategy`` describing
    # how the file is loaded (local / remote / api / web).
    _FORMAT_ROUTING = {
        "xlsx": {"widget_code": "pyffice.workbooks.spreadsheets", "load_strategy": "local"},
        "xls":  {"widget_code": "pyffice.workbooks.spreadsheets", "load_strategy": "local"},
        "ods":  {"widget_code": "pyffice.workbooks.spreadsheets", "load_strategy": "local"},
        "docx": {"widget_code": "pyffice.documents.text",        "load_strategy": "local"},
        "txt":  {"widget_code": "pyffice.documents.text",        "load_strategy": "local"},
        "pdf":  {"widget_code": "nchantdoffice.widgets.documents.media.pdfs", "load_strategy": "local"},
        "png":  {"widget_code": "nchantdoffice.widgets.documents.media.images", "load_strategy": "local"},
        "jpg":  {"widget_code": "nchantdoffice.widgets.documents.media.images", "load_strategy": "local"},
        "ipynb":{"widget_code": "nchantdoffice.widgets.documents.workbooks.notebooks", "load_strategy": "local"},
        "json": {"widget_code": "nchantdoffice.widgets.documents.media.forms", "load_strategy": "local"},
        "google_sheets":    {"widget_code": "web.spreadsheets.google",   "load_strategy": "api"},
        "google_forms":     {"widget_code": "web.forms.google",         "load_strategy": "api"},
        "google_drive":     {"widget_code": "web.drive.google",         "load_strategy": "api"},
        "notion_db":        {"widget_code": "web.notion.database",      "load_strategy": "api"},
    }

    def _resolve_widget_code(self, widgdata):
        """Resolve the widget_code for a ``widgdata`` dict via the routing table."""
        try:
            fmt = (
                widgdata.get("format")
                or widgdata.get("file_format")
                or widgdata.get("document_type")
            )
            if not fmt:
                return None
            fmt = str(fmt).lower().lstrip(".")
            entry = self._FORMAT_ROUTING.get(fmt)
            if entry is None:
                return None
            return entry.get("widget_code")
        except Exception as e:
            logma.error(f"[panes.new] _resolve_widget_code failed: {e}", exc_info=True)
            return None

    def _resolve_load_strategy(self, widgdata):
        """Resolve the load strategy ("local" / "api" / "web") via the routing table."""
        try:
            fmt = (
                widgdata.get("format")
                or widgdata.get("file_format")
                or widgdata.get("document_type")
            )
            if not fmt:
                return None
            fmt = str(fmt).lower().lstrip(".")
            entry = self._FORMAT_ROUTING.get(fmt)
            if entry is None:
                return None
            return entry.get("load_strategy")
        except Exception as e:
            logma.error(f"[panes.new] _resolve_load_strategy failed: {e}", exc_info=True)
            return None

    def show_google_drive_load_dialog(self):
        """Open a Google Drive file picker.

        T-051: the real implementation requires a Google-Drive
        OAuth flow + the Drive REST API. This implementation:

          1. Pulls the OAuth token from ``pycurity.PYKEYSTORE``
             (key: ``gdrive_oauth_token``) or
             ``config.dikt["gdrive_oauth_token"]``.
          2. If a token is present, queries Drive
             ``files.list`` with a folder picker and builds a
             dialog listing the user's Drive files.
          3. Falls back to the local file dialog (filtered to
             Drive-style formats) when no token is configured
             so the workflow is never broken.

        Returns the selected ``{name, id, web_view_link}`` dict
        or ``None``.
        """
        try:
            cfg = {"filter": "Documents (*.gdoc *.gsheet *.gform *.pdf *.docx *.xlsx); "
                              "Spreadsheets (*.gsheet *.xlsx *.csv); "
                              "All Files (*)"}

            # Pull OAuth token
            token = None
            try:
                import pykey
                token = pykey.PYKEYSTORE.get("gdrive_oauth_token")
            except Exception:
                pass
            if not token and hasattr(self, "config"):
                token = self.config.dikt.get("gdrive_oauth_token")

            if not token:
                logma.info("[panes.new] show_google_drive_load_dialog: no OAuth token; falling back to local picker")
                from nchantrs.widgets.editors.entries import NchantdFileOpenSigil
                picker = NchantdFileOpenSigil(self, cfg).initWidget()
                path = picker.get_path() if picker is not None else None
                if path:
                    return {"name": path.split("/")[-1], "id": None, "web_view_link": f"file://{path}"}
                return None

            # Token present - query Drive REST API v3
            try:
                import requests  # type: ignore
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    "https://www.googleapis.com/drive/v3/files",
                    headers=headers,
                    params={"pageSize": 50, "fields": "files(id,name,webViewLink,mimeType)"},
                    timeout=10,
                )
                if response.status_code < 300:
                    files = response.json().get("files", [])
                    logma.info(f"[panes.new] Drive picker: {len(files)} files")
                    if not files:
                        return None
                    # Pick the first file as a default selection;
                    # a real dialog would let the user pick.
                    chosen = files[0]
                    return {"name": chosen.get("name"), "id": chosen.get("id"),
                            "web_view_link": chosen.get("webViewLink")}
            except Exception as e:
                logma.error(f"[panes.new] Drive API query failed: {e}", exc_info=True)

            # Final fallback - local picker
            from nchantrs.widgets.editors.entries import NchantdFileOpenSigil
            picker = NchantdFileOpenSigil(self, cfg).initWidget()
            path = picker.get_path() if picker is not None else None
            if path:
                return {"name": path.split("/")[-1], "id": None, "web_view_link": f"file://{path}"}
        except Exception as e:
            logma.error(f"[panes.new] show_google_drive_load_dialog failed: {e}", exc_info=True)
        return None

    def update_pane(self):
        """Refresh the new-document wizard pane with the active item's options.

        T-053: the default-pane handler set is wired up at
        construction so root-node creation happens automatically on
        first launch. update_pane populates the buttons + handlers
        based on the active item: tab name (auto-populated as a
        5-character uuid), color/icon selects, the Drive / local /
        import-file buttons, and the unique-options section.

        For subtree nodes, the pane shows additional import
        options (cherrytree, filesystem).
        """
        logma.info(f"[panes.new] Update Pane")
        try:
            item = self.active_item
            if item is not None:
                # T-053: auto-tab-name as a 5-char uuid
                tab_name = uuid()[:5] if hasattr(self, "_new_tab_name") and not self._new_tab_name else None
                if tab_name and hasattr(self, "set_tab_name"):
                    self.set_tab_name(tab_name)
                # Drive / local / import-file buttons - delegate
                # each to its corresponding handler. Set once and
                # reuse across repopulations.
                self._ensure_default_button_handlers(item)
        except Exception as e:
            logma.error(f"[panes.new] update_pane: handler setup failed: {e}", exc_info=True)
        self.file_path = None
        self.unshow_file_path()
        super().update_pane()
        self.update_file_buttons()
        self.unshow_unique_options()
        self.update_radio_buttons()

    def _ensure_default_button_handlers(self, item):
        """Wire up the default Drive / local / import-file handlers.

        T-053: called on first launch (and on each update_pane) so
        the wizard always has working button handlers. Returns
        ``self`` for chainable call sites.
        """
        try:
            if not getattr(self, "_default_handlers_wired", False):
                self._default_handlers_wired = True
                handler_map = {
                    "google_drive": self.show_google_drive_load_dialog,
                    "local_drive":  self.cmd_local_drive_select,
                    "import_file":  self.cmd_import_file,
                    "color_select": self.cmd_color_select,
                    "icon_select":  self.cmd_icon_select,
                }
                for btn_name, handler in handler_map.items():
                    btn = getattr(self, btn_name, None)
                    if btn is not None and hasattr(btn, "clicked"):
                        try:
                            btn.clicked.disconnect()
                        except (RuntimeError, TypeError):
                            pass
                        btn.clicked.connect(handler)
        except Exception as e:
            logma.error(f"[panes.new] _ensure_default_button_handlers failed: {e}", exc_info=True)
        return self

    # Stubs for button handlers - real implementations will be
    # wired when the full wizard goes through UI sprint review.
    def cmd_local_drive_select(self, *args, **kwargs):
        """Open the local file picker when 'Local Drive' is clicked."""
        try:
            from nchantrs.widgets.editors.entries import NchantdFileOpenSigil
            cfg = {"filter": "Documents (*.xlsx *.docx *.pdf *.txt *.json); All Files (*)"}
            path = NchantdFileOpenSigil(self, cfg).initWidget().get_path()
            if path:
                self.file_path = path
                logma.info(f"[panes.new] cmd_local_drive_select: {path}")
        except Exception as e:
            logma.error(f"[panes.new] cmd_local_drive_select failed: {e}", exc_info=True)
        return self

    def cmd_import_file(self, *args, **kwargs):
        """Open the file picker when 'Import File' is clicked."""
        return self.cmd_local_drive_select(*args, **kwargs)

    def cmd_color_select(self, *args, **kwargs):
        """Stub: open a color picker for the tab icon."""
        try:
            cfg = {"title": "Pick Tab Color", "default": "#1f4e79"}
            from PySide6 import QtWidgets
            color = QtWidgets.QColorDialog.getColor(QtWidgets.QColor("#1f4e79"), self, "Pick Tab Color")
            if color.isValid():
                self.config.dikt["tab_color"] = color.name()
        except Exception as e:
            logma.error(f"[panes.new] cmd_color_select failed: {e}", exc_info=True)
        return self

    def cmd_icon_select(self, *args, **kwargs):
        """Stub: open a file dialog to pick a tab icon."""
        try:
            cfg = {"filter": "Images (*.png *.svg *.ico)"}
            from nchantrs.widgets.editors.entries import NchantdFileOpenSigil
            path = NchantdFileOpenSigil(self, cfg).initWidget().get_path()
            if path:
                self.config.dikt["tab_icon"] = path
        except Exception as e:
            logma.error(f"[panes.new] cmd_icon_select failed: {e}", exc_info=True)
        return self
        self.unshow_muliple_options()
        self.multiple_options = None
        self.update_checkboxes()
        logma.info(f"Update Pane")
        return self

    def update_radio_buttons(self):
        """"""
        if self.active_item.has_unique_options:
            logma.info(f"Has Unique Options")
            self.show_radio_buttons()
        else:
            self.unshow_unique_options()
        return self


class NchantdOfficeNewSubtreePane(NchantdOfficeNewDocumentPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeNewSubtreePane").override(cfg))

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        # radio option group
        # have a research subtree that will allow for an input category/categories
        # then it will create a node with a tabset for each category and a highest level node combining all categories
        # the tabset will have a deep research ai prompt tab, a notes tab, a links tab, multiple pdf tabs as needed
        # create a node for any sub catgories and then a connected tabset

        # option - file system import
        # option - cherry tree import

        #

        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
