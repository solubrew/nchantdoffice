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
from os.path import dirname, join
from copy import deepcopy
import json as j

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.managers import NchantdManager
from kahndor.logma import Logma
from nchantrs.dialogs.files import NchantdFileOpenSigil
from nchantdoffice.widgets.panes.documents import NchantdOfficeTabEditPane, NchantdOfficeNoteEditPane
from nchantdoffice.widgets.panes.documents import NchantdOfficeNodeEditPane
from nchantdoffice.widgets.tabs import NchantdOfficeTab
from pyffice.document import PyfficeDocument
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.controls.buttons import NchantdButton

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
debug = True
log = False
if not log:
    logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "documents.yaml")


class NchantdOfficeDocumentMixin:
    """Nchantd Office Document contains elements to create virtual documents to be stored. This is primarily to handle
    storage and generally will equate to what is shown in a tab"""

    def init_variables(self, name=None):
        """"""
        super().init_variables()
        # self.app = pyqt.QApplication.instance()
        self.button_bar = None
        self.context = None
        self.document = None
        self.document_name = name
        self.document_editor = None
        self.document_initialized = False
        self.document_toolbar = None
        self.document_type = "base"
        self.data = None
        self.file_path = None
        self.file_type = None
        self.toolbox = None
        self.toolbox_config = None
        self.has_pro = (
            getattr(self.app.model.user, "has_pro", False)
            if self.app and self.app.model and self.app.model.user
            else False
        )

    def initModel(self, cfg=None, objects=None):
        """"""
        super().initModel(cfg)  # Pass through usage even though the Mixin has no permeate parent class
        self.toolbox_config = self.config.dikt.get("toolbox", None)
        self.set_file_path(self.config.dikt.get("file_path", None))
        self.data = {}
        self.context_menu_name = "context.document"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        # Fix: Enable context menu policy for right-click to work
        self.setContextMenuPolicy(pyqt.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        return self

    def _show_context_menu(self, pos):
        """"""
        # Re-initialize context menu to ensure it's fresh
        if self.context_menu is None:
            self.initialize_context_menu(self.context_menu_name)
        if self.context_menu is not None:
            global_pos = self.mapToGlobal(pos)
            self.context_menu.exec(global_pos)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        if self.config.dikt.get("default_toolbar", True):
            self.init_toolbar(cfg)
        self.init_toolbox()
        return self

    def initWidget(self, pos=0):
        """ """
        self.initModel()
        self.initView()
        return self

    def align_left(self, selection=""):
        """Align text selection to the left within the document editor."""
        if self.document_editor is not None:
            cursor = self.document_editor.textCursor()
            fmt = pyqt.QTextBlockFormat()
            fmt.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft)
            cursor.mergeBlockFormat(fmt)
            self.on_document_changed()
        return self

    def align_center(self, selection=""):
        """Align text selection to the center within the document editor."""
        if self.document_editor is not None:
            cursor = self.document_editor.textCursor()
            fmt = pyqt.QTextBlockFormat()
            fmt.setAlignment(pyqt.Qt.AlignmentFlag.AlignCenter)
            cursor.mergeBlockFormat(fmt)
            self.on_document_changed()
        return self

    def align_right(self, selection=""):
        """Align text selection to the right within the document editor."""
        if self.document_editor is not None:
            cursor = self.document_editor.textCursor()
            fmt = pyqt.QTextBlockFormat()
            fmt.setAlignment(pyqt.Qt.AlignmentFlag.AlignRight)
            cursor.mergeBlockFormat(fmt)
            self.on_document_changed()
        return self

    def cmd_cancel(self):
        """Cancel current document operation and revert unsaved changes."""
        if hasattr(self, "document_editor") and self.document_editor is not None:
            self.document_editor.setText("")
        if hasattr(self, "app") and self.app:
            self.app.model.has_changed = False
        return self

    def cmd_delete_tab(self, event, *args, **kwargs):
        """"""
        self.app.model.delete_tab(self)

    def cmd_open_local_file(self, event=None, *args, **kwargs):
        """"""
        cfg = {}
        self.open_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_file = self.open_file_sigil.file_selected
        if self.local_file is not None:
            if self.local_file.endswith(".ctd"):
                self.app.model.import_cherrytree(self.local_file)
        return self

    def cmd_node_edit(self, event=None, *args, **kwargs):
        """Open the node editor for the current document's tree node."""
        if hasattr(self, "app") and self.app:
            if hasattr(self.app.view, "panes") and "left" in self.app.view.panes:
                tree = getattr(self.app.view.panes["left"], "tree", None)
                if tree and hasattr(tree, "model") and tree.model.current_node:
                    node = tree.model.current_node
                    cfg = {"node": node, "document": self.document}
                    editor = NchantdOfficeNodeEditPane(self, cfg)
                    editor.initWidget()
        return self

    def cmd_redo(self, event=None, *args, **kwargs):
        """Redo the last undone action in the document editor."""
        if self.document_editor is not None:
            doc = self.document_editor.document()
            if doc.isRedoAvailable():
                doc.redo()
        return self

    def cmd_show_pane_left(self, event=None, *args, **kwargs):
        """"""
        # NOTE flip icon
        if self.app.view.panes["left"].isHidden():
            self.app.view.panes["left"].show()
        else:
            self.app.view.panes["left"].hide()
        return self

    def cmd_show_pane_right(self, event=None, *args, **kwargs):
        """"""
        # NOTE flip icon
        if self.app.view.panes["right"].isHidden():
            self.app.view.panes["right"].show()
        else:
            self.app.view.panes["right"].hide()
        return self

    def cmd_tag_edit(self, event=None, *args, **kwargs):
        """Open tag editor for the current document."""
        if hasattr(self, "app") and self.app and hasattr(self.app, "model"):
            tags = getattr(self.document, "tags", []) if self.document else []
            cfg = {"tags": tags, "document": self.document}
            editor = NchantdOfficeNoteEditPane(self, cfg)
            editor.initWidget()
            self.on_document_changed()
        return self

    def cmd_undo(self, event=None, *args, **kwargs):
        """Undo the last action in the document editor."""
        if self.document_editor is not None:
            doc = self.document_editor.document()
            if doc.isUndoAvailable():
                doc.undo()
        return self

    def cmd_save_tab(self, event=None, *args, **kwargs):
        """"""
        self.save()

    def create_data_table(self):
        """"""
        df = DataFrame()
        return df

    def defocus(self):
        """Remove focus from the document widget and trigger save if needed."""
        if self.document_editor is not None:
            self.document_editor.clearFocus()
        self.on_lost_focus()
        return self

    def export_document(self):
        """Export a single selected document to an external file of the selected format."""
        if self.document is None:
            logma.warning("No document to export")
            return self
        file_path, selected_filter = pyqt.QFileDialog.getSaveFileName(
            self, "Export Document", "", "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            doc_data = self.document.to_dict() if hasattr(self.document, "to_dict") else str(self.document.content)
            with open(file_path, "w", encoding="utf-8") as f:
                j.dump(doc_data, f, indent=2, default=str)
            logma.info(f"Exported document to {file_path}")
        return self

    def get_bytes(self):
        """Return document content as bytes for storage or transmission."""
        if self.document is None:
            return bytes()
        content = self.document.content if hasattr(self.document, "content") else ""
        if isinstance(content, bytes):
            return content
        if isinstance(content, str):
            return content.encode("utf-8")
        return j.dumps(content, default=str).encode("utf-8")

    def get_primary_key(self):
        """"""
        self.primary_key = self.app.model.get_primary_key(self.uuid)
        return self.primary_key

    def import_document(self):
        """Import a document from an external file."""
        file_path, _ = pyqt.QFileDialog.getOpenFileName(
            self, "Import Document", "", "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = f.read()
            try:
                doc_data = j.loads(raw)
            except j.JSONDecodeError:
                doc_data = {"content": raw, "format": "text"}
            if self.document is not None and hasattr(self.document, "content"):
                self.document.content = doc_data.get("content", raw)
            self.on_document_changed()
            logma.info(f"Imported document from {file_path}")
        return self

    def init_drawer(self, name):
        """Initialize a named drawer section in the toolbox."""
        if self.toolbox_config is None:
            self.toolbox_config = {}
        drawer_id = None
        for key, drawer in self.toolbox_config.items():
            if isinstance(drawer, dict) and drawer.get("name") == name:
                drawer_id = key
                break
        if drawer_id is None:
            drawer_id = max(self.toolbox_config.keys(), default=-1) + 1
            self.toolbox_config[drawer_id] = {"name": name, "items": {}}
        drawer = self.toolbox_config[drawer_id]
        if "items" not in drawer:
            drawer["items"] = {}
        return drawer

    def init_toolbar(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        # Ensure we have app reference - try to get it from parent if not set
        # if not hasattr(self, "app") or self.app is None:
        #     if hasattr(self, "parent") and self.parent is not None:
        #         self.app = getattr(self.parent, "app", None)
        _buttons = {
            0: {"action": "show_pane_left", "handler": self.cmd_show_pane_left},
            # DEBUG the open file dialog is not respecting close/cancel commands
            100: {"action": "open_local", "handler": self.cmd_open_local_file},
            101: {"action": "save", "handler": self.cmd_save_tab},
            150: {"action": "redo", "handler": self.cmd_redo},
            200: {"action": "undo", "handler": self.cmd_undo},
            # NOTE: i'm not sure this has any other uses that arent' handled by the toolbox tab trashcan
            400: {"action": "cancel", "handler": self.cmd_delete_tab},
            1000: {"action": "show_pane_right", "handler": self.cmd_show_pane_right},
        }
        logma.info(f"CFG {cfg}")
        buttons = kahndor.Instruct(self.config.dikt.get("buttons", {})).override(cfg.get("buttons", {})).dikt
        buttons.update(_buttons)
        if self.has_pro:
            cfg = {
                "label": "Profile",
                "layout": "horizontal",
                "size": [10, 20],
                "drop_down": {"size": [100, 20]},
                "options": [
                    "default",
                ],
            }
            self.profile_select_entry = NchantdDropDown(self, cfg).initWidget()
            buttons[1] = {"name": "get_pro", "widget": self.profile_select_entry}
        else:
            cfg = {
                "text": "Get Pro",
                "handler": self.app.view.switch_to_account_tab,
                "height": 24,
                "background_color": "green",
            }
            self.profile_select_entry = NchantdButton(self, cfg).initWidget()
            buttons[1] = {"name": "get_pro_features", "widget": self.profile_select_entry}
        cfg = {"layout": "horizontal", "justify": "right"}
        buttons = {k: buttons[k] for k in sorted(buttons)}
        logma.info(f"Buttons {buttons}")
        self.document_toolbar = NchantdButtonBar(self, cfg).initWidget(buttons)
        self.document_toolbar.setFixedHeight(30)
        self.layout.addWidget(self.document_toolbar)
        return self

    def init_toolbox(self, cfg=None):
        """"""
        self.config.override(cfg)
        if self.toolbox_config is None:
            self.toolbox_config = self.app.model.toolbox_config.get("document", None)
        if self.toolbox_config is None:
            logma.warning("No toolbox config found for document, using empty default")
            self.toolbox_config = {}
        logma.info(f"Toolbox Config {self.toolbox_config.keys()}")
        self.toolbox_config[50]["items"] = self.init_drawer_file_config()
        return self

    def init_drawer_file_config(self):
        """"""
        default_action = {"action": "insert_object", "type": "custom"}
        items = self.toolbox_config[50].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"layout": "horizontal"}
        self.node_edit_pane = NchantdOfficeNodeEditPane(self, cfg)
        items[cnt]["widget"] = self.node_edit_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"layout": "horizontal"}
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

    def lock_page(self):
        """Lock the current document page to prevent editing."""
        if self.document_editor is not None:
            self.document_editor.setReadOnly(True)
        if self.document is not None and hasattr(self.document, "locked"):
            self.document.locked = True
        return self

    def on_document_changed(self):
        """

        when there is a change to the document but the changes into the local cache for easier undo/redo logic
        when a document loses focus the changes will be transferred from the local cache to the save process

        :return:
        """
        self.app.model.has_changed = True
        return self

    def on_gain_focus(self):
        """Update document when it gains focus to reflect any edits made elsewhere."""
        if self.document is not None and hasattr(self.app, "model"):
            stored = self.app.model.get_document(self.document.did) if hasattr(self.app.model, "get_document") else None
            if stored is not None and hasattr(stored, "content"):
                if self.document_editor is not None:
                    self.document_editor.setPlainText(str(stored.content))
        self.setFocus()
        return self

    def on_lost_focus(self):
        """Save document when focus is lost, based on user settings."""
        auto_save = self.config.dikt.get("auto_save_on_blur", True) if hasattr(self, "config") else True
        if auto_save and self.document is not None:
            if self.document_editor is not None and hasattr(self.document, "content"):
                self.document.content = self.document_editor.toPlainText()
            self.save_internal()
        return self

    def register(self):
        """"""
        self.app.model.store.register_document(self.document)
        return self

    def save(self, path=None, format_=None, encrypt=False):
        """
        Save method saves the current document in its most recent format ie internal or external file saving
        this can be different than a store_document command

        :return:
        """
        if self.document is None:
            return self
        logma.info(f"Save Content {self.document.content}")
        logma.info(f"Save Path {path}")
        self.set_file_path(path)
        if self.app.view.panes["left"].tree.model.current_node is None:
            return self
        pid = self.app.view.panes["left"].tree.model.current_node.nid
        logma.info(f"Save PID {pid}")
        if self.app.view.panes["center"].model.current_tab is None:
            return self
        pos = self.app.view.panes["center"].model.current_tab.position
        logma.info(f"Save Pos {pos}")
        logma.info(f"Save DID {self.document.did}")
        self.document.save()  # increments versions and (internal encryption..future)
        self.app.model.store_document(self.document)
        return self

    def save_external(self):
        """Save document to an external file path."""
        if self.document is None:
            return self
        if self.file_path is None:
            file_path, _ = pyqt.QFileDialog.getSaveFileName(
                self, "Save Document", "", "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
            )
            if not file_path:
                return self
            self.set_file_path(file_path)
        doc_data = (
            self.document.to_dict() if hasattr(self.document, "to_dict") else {"content": str(self.document.content)}
        )
        with open(self.file_path, "w", encoding="utf-8") as f:
            j.dump(doc_data, f, indent=2, default=str)
        logma.info(f"Saved external document to {self.file_path}")
        return self

    def save_internal(self):
        """"""
        doc = self.document.to_dict()
        self.app.model.store_document(doc)
        return self

    def save_as(self, name, path=None):
        """Create a copy of the document under a new name and optional path."""
        if self.document is None:
            logma.warning("save_as called with no document")
            return self
        if path is None:
            path = dirname(self.path) if self.path else getattr(self.app, "base_path", "")
        target_path = join(path, name)
        doc_dict = self.document.to_dict() if hasattr(self.document, "to_dict") else {"content": str(self.document)}
        doc_dict["path"] = target_path
        if hasattr(self.app, "model") and hasattr(self.app.model, "store_document"):
            self.app.model.store_document(doc_dict)
        logma.info(f"Document saved as {target_path}")
        self.path = target_path
        return self

    def save_copy_as(self, name, path=None):
        """Create a copy of the document without changing the current document state."""
        if self.document is None:
            logma.warning("save_copy_as called with no document")
            return self
        if path is None:
            path = dirname(self.path) if self.path else getattr(self.app, "base_path", "")
        target_path = join(path, name)
        doc_dict = self.document.to_dict() if hasattr(self.document, "to_dict") else {"content": str(self.document)}
        doc_dict["path"] = target_path
        doc_dict["did"] = None
        doc_dict.pop("uuid", None)
        if hasattr(self.app, "model") and hasattr(self.app.model, "store_document"):
            self.app.model.store_document(doc_dict)
        logma.info(f"Document copy saved as {target_path}")
        return self

    def set_file_path(self, path):
        """"""
        self.file_path = path
        return self

    def store_document(self):
        """"""
        self.app.model.store.store_document(self.document)
        return self

    def take_snapshot(self):
        """Capture a image of the current document."""
        # TODO this method is for taking visual snapshots of the document need to get the dimens of the
        #  document widget and then grab and save an image
        return self

    def unlock_page(self):
        """Unlock the current document page to allow editing."""
        if self.document_editor is not None:
            self.document_editor.setReadOnly(False)
        if self.document is not None and hasattr(self.document, "locked"):
            self.document.locked = False
        return self

    def update_document(self):
        """Refresh the current document state from the underlying store."""
        if self.document is None or not hasattr(self.document, "did"):
            return self
        if not hasattr(self.app, "model"):
            return self
        stored = self.app.model.get_document(self.document.did) if hasattr(self.app.model, "get_document") else None
        if stored is None:
            return self
        if self.document_editor is not None and hasattr(stored, "content"):
            self.document_editor.setPlainText(str(stored.content))
        if hasattr(stored, "to_dict"):
            for key, value in stored.to_dict().items():
                if hasattr(self.document, key) and key not in ("did", "uuid"):
                    setattr(self.document, key, value)
        return self

    def update_document_page(self, page_num):
        """Update display/state for a specific document page.
        NOTE: this codebase currently uses a single-page editor; multi-page support
        is a future feature. For page_num == 0 (current), we refresh from store; for
        any other page_num we log a warning until multi-page support lands.
        """
        if page_num == 0:
            return self.update_document()
        logma.warning(f"update_document_page({page_num}) called but multi-page support is not implemented")
        return self

    def _store_document(self):
        """"""
        document = self.document.to_dict()
        self.app.model.store_document(document)
        return self


class NchantdOfficeDocument(NchantdOfficeDocumentMixin, NchantdOfficeTab):
    """ ""Document base class - implements PyfficeDocument for all document types"""

    PYTYPE = "document"  # Default Pyffice type

    def __init__(self, name, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeDocument").override(cfg))
        self.name = name
        self.did = None
        self.notes = None

    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools based on Pyffice document type"""
        return []  # Override in subclasses

    def initModel(self, cfg=None):
        """"""
        self.init_variables(self.name)
        self.config.override({"settings": self.app.model.settings.document.get(self.document_type, self.get_default_settings())})
        super().initModel(cfg)
        return self

    def get_default_settings(self):
        """"""
        return {}

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        self.set_notes(self.config.dikt.get("notes", []))
        return self

    def initWidget(self, cfg=None):
        """"""
        self.initModel(cfg)
        self.initView(cfg)
        return self

    def add_automation(self):
        """"""
        super().add_automation()
        return self

    def append_note(self, note):
        """"""
        note.set_sequence(len(self.notes))
        self.notes.append(note)
        return self

    def close_tab(self, tab=None):
        """"""
        super().close_tab(tab)
        return self

    def export_file(self):
        """"""
        super().export_file()

    def get_version(self):
        """returns the current version of the document"""
        return self.config.dikt.get("version", 1)

    def get_supports_versions(self):
        """returns true if the document supports versions"""
        response = {"pyffice": self.config.dikt.get("supports_pyffice_versions", False)}
        return response

    def import_file(self):
        """"""
        super().import_file()

    def init_toolbar(self, cfg=None):
        """"""
        super().init_toolbar(cfg)
        return self

    def init_toolbox(self, cfg=None):
        """"""
        super().init_toolbox(cfg)
        return self

    def jump_to_account_tab(self):
        """"""

    def lock_view(self):
        """"""
        super().lock_view()
        return self

    def open(self):
        """Open the document for editing. If no document is set, attempt to load from the current node."""
        if self.document is None and hasattr(self, "app") and hasattr(self.app, "view"):
            tree = getattr(self.app.view.panes.get("left", {}), "tree", None)
            if tree and hasattr(tree, "model") and tree.model.current_node:
                node = tree.model.current_node
                if hasattr(node, "document") and node.document is not None:
                    self.set_document(node.document)
                    if self.document_editor is not None and hasattr(self.document, "content"):
                        self.document_editor.setPlainText(str(self.document.content))
        return self

    def open_local(self):
        """Trigger the local file open dialog."""
        return self.cmd_open_local_file()

    def open_remote(self):
        """Open a document from a remote source URL."""
        if not hasattr(self.app, "model") or not hasattr(self.app.model, "open_remote"):
            logma.warning("open_remote not available on this model")
            return self
        try:
            doc = self.app.model.open_remote()
            if doc is not None:
                self.set_document(doc)
                if self.document_editor is not None and hasattr(doc, "content"):
                    self.document_editor.setPlainText(str(doc.content))
                logma.info(f'Remote document opened: {getattr(doc, "did", "unknown")}')
        except Exception as e:
            logma.error(f"Failed to open remote document: {e}")
        return self

    def save(self):
        """"""
        super().save()
        return self

    def set_document(self, document):
        """"""
        self.document = document
        return self

    def set_notes(self, notes):
        """"""
        self.notes = [NchantdOfficeNote(self, note).initWidget() for note in notes]
        return self

    def unlock_view(self):
        """"""
        super().unlock_view()
        return self


class NchantdOfficeDocumentManager(NchantdOfficeDocumentMixin, NchantdManager):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeDocumentManager"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.name = "NchantdOfficeDocumentManager"

    def initModel(self, cfg=None):
        """"""
        self.init_variables(self.name)
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        return self

    def init_toolbox(self):
        """"""
        super().init_toolbox()


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
