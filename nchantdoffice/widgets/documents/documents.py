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
        self.document_nm = name
        self.document_editor = None
        self.document_initialized = False
        self.document_toolbar = None
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
        """"""
        return self

    def align_center(self, selection=""):
        """"""
        return self

    def align_right(self, selection=""):
        """"""
        return self

    def cmd_cancel(self):
        """"""
        pass

    def cmd_delete_tab(self):
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
        """"""
        return self

    def cmd_redo(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_show_toolbox(self, event=None, *args, **kwargs):
        """"""
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
        """"""
        return self

    def cmd_undo(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_save_tab(self, event=None, *args, **kwargs):
        """"""
        self.save()

    def create_data_table(self):
        """"""
        df = DataFrame()
        return df

    def defocus(self):
        """"""
        return self

    def export_document(self):
        """Export a single selected document to an external file of the selected format"""
        return self

    def get_bytes(self):
        """"""
        return bytes()

    def get_primary_key(self):
        """"""
        self.primary_key = self.app.model.get_primary_key(self.uuid)
        return self.primary_key

    def import_document(self):
        """"""
        return self

    def init_drawer(self, name):
        """"""
        return self

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
                "options": ["default"],
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
        logma.warning(f"Buttons {buttons}")
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
        # if cnt not in items:
        #     items[cnt] = default_action
        # cfg = {"layout": "horizontal", "handler": self.cmd_tag_edit}
        # self.note_edit_pane = NchantdOfficeNoteEditPane(self, cfg)
        # items[cnt]["widget"] = self.note_edit_pane
        # cnt += 1
        return items

    def lock_page(self):
        """"""

    def launch_toolbox(self):
        """"""

    def on_document_changed(self):
        """

        when there is a change to the document but the changes into the local cache for easier undo/redo logic
        when a document loses focus the changes will be transferred from the local cache to the save process

        :return:
        """
        self.app.model.has_changed = True
        return self

    def on_gain_focus(self):
        """
            update document when it gains focus to ensure any edits made elsewhere are reflected here
        :return:
        """

    def on_lost_focus(self):
        """
        Save based on user settings
        default is to save work when the user moves focus from the document widget

        :return:
        """
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
        # logma.warning("Saving Document")
        if self.document is None:
            return self
        logma.info(f"Save Content {self.document.content}")
        # self.document.save()  # increments versions and (internal encryption..future)
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
        # logma.json(self.document.to_dict())
        self.app.model.store_document(self.document)
        return self

    def save_external(self):
        """"""
        return self

    def save_internal(self):
        """"""
        doc = self.document.to_dict()
        self.app.model.store_document(doc)
        return self

    def save_as(self, name, path=None):
        """"""
        if self.parent:
            logma.warning(f"Save As method not usable if document has a parent")
            raise NotImplementedError
        if path is None:
            path = self.path
        self.path = join(path, name)
        self.save()
        return self

    def save_copy_as(self, name, path=None):
        """"""
        if self.parent:
            logma.warning(f"Save Copy As method not usable if document has a parent")
            raise NotImplementedError
        self.save_as(name, path)
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
        """"""
        return self

    def unlock_page(self):
        """"""
        return self

    def update_document(self):
        """"""
        return self

    def update_document_page(self, page_num):
        """"""
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
        if cfg is not None:
            logma.info(f"Document Config {cfg.get('toolbox', None)}")
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
        super().initModel(cfg)
        return self

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
        """"""
        return self

    def open_local(self):
        """"""
        return self

    def open_remote(self):
        """"""
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
