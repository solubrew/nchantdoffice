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

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from subtrix.utilities import uuid
from nchantrs.libraries import pyqt
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons, NchantdOkButtons
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.widgets.groups import NchantdGroup
from kahndor.logma import Logma
from nchantrs.dialogs.colors import NchantdColorSelectSigil
from nchantrs.dialogs.files import NchantdFileOpenSigil
from nchantrs.widgets.controls.button_groups import NchantdFontConfigBar
from nchantrs.widgets.tables.lists import NchantdList

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
# logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "documents.yaml")


class NchantdOfficeNodeEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeNodeEditPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {"text": "Node: "}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {
            "layout": "horizontal",
            "actions": {
                0: {"action": "duplicate_document", "type": "", "handler": self.cmd_duplicate_document},
                # 1: {"action": "import_document", "type": "", "handler": self.cmd_import_file},
                # 2: {"action": "export_document", "type": "", "handler": self.cmd_export_document},
                2: {"action": "take_snapshot", "handler": self.cmd_take_snapshot},
                3: {
                    "action": "sort_children_ascending",
                    "type": "",
                    "handler": self.cmd_sort_children,
                    "args": "ascending",
                },
                4: {
                    "action": "sort_children_descending",
                    "type": "",
                    "handler": self.cmd_sort_children,
                    "args": "descending",
                },
                5: {"action": "delete_node", "type": "", "handler": self.cmd_delete_node},
            },
            "size": ["auto", 30],
        }
        self.node_buttonbar = NchantdButtonBar(self, cfg).initWidget()
        layout.addWidget(self.node_buttonbar)

        node = self.get_node()
        # logma.info(f"Node {dir(node)} {node.name}")
        logma.info(f"Node {node.item} {node.name}")
        cfg = {"label": "Node Name: ", "value": node.item}
        if node.node_type in ("displaynode", "sysorgnode", "yearnode", "monthnode", "daynode"):
            cfg["readonly"] = True
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)

        cfg = {"label": "Node Position: ", "value": node.position}
        if node.node_type in ("displaynode", "sysorgnode", "yearnode", "monthnode", "daynode"):
            cfg["readonly"] = True
        self.position_entry = NchantdLabeledSpinBox(self, cfg).initWidget()
        layout.addWidget(self.position_entry)

        cfg = {"show_label": False, "layout": "horizontal", "two_rows": True, "size": ["auto", "auto"]}
        self.font_bar = NchantdFontConfigBar(self, cfg).initWidget()
        layout.addWidget(self.font_bar)
        cfg = {"buttons": {"ok": {"handler": self.cmd_set_node_name}}}
        self.accept_button = NchantdOkButtons(self, cfg).initWidget()
        layout.addWidget(self.accept_button)
        # self.tags = self.get_tags()
        # tags_label = NchantdLabel(self, {"text": "Tags: "}).initWidget()
        # layout.addWidget(tags_label)
        # TODO: add tag tracking
        # cfg = {"data": self.tags}
        # self.tags_list = NchantdList(self, cfg).initWidget()
        # layout.addWidget(self.tags_list)
        group.set_height(layout.sizeHint().height() * 1.2)
        self.layout.addWidget(group)

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_delete_node(self, event=None, *args, **kwargs):
        """"""
        self.app.model.delete_node(self.get_node())
        tree = self.app.view.panes["left"].tree
        tree.view.go_to_previous_node()
        tree.refresh()

        return self

    def cmd_duplicate_document(self, event=None, *args, **kwargs):
        """"""
        self.app.model.duplicate_node(self.get_node())
        return self

    def cmd_export_file(self, event=None, *args, **kwargs):
        """"""
        self.app.model.export_node(self.get_node())
        return self

    def cmd_import_file(self, event=None, *args, **kwargs):
        """"""
        cfg = {}
        self.open_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_file = self.open_file_sigil.file_selected
        if self.local_file is not None:
            if self.local_file.endswith(".ctd"):
                self.app.model.import_cherrytree(self.local_file)
        return self

    def cmd_launch_color_sigil(self, event, *args, **kwargs):
        """"""
        cfg = {}
        self.color_sigil = NchantdColorSelectSigil(self, cfg).initWidget()
        return self

    def cmd_set_node_name(self, event, *args, **kwargs):
        """"""
        logma.info(f"Name Entry {self.name_entry}")
        logma.info(f"Set Node Name {self.name_entry.textbox.entry_data}")
        node = self.get_node()
        if node.node_type in ("displaynode", "sysorgnode", "yearnode", "monthnode", "daynode"):
            self.name_entry.textbox.entry_data = node.name
            return self
        logma.info(f"Set Node Name {self.name_entry.textbox.text()}")
        try:
            node.setText(0, self.name_entry.textbox.entry_data)
        except Exception as e:
            node = self.app.model.get_current_node()
            node.setText(0, self.name_entry.textbox.entry_data)
        return self

    def cmd_set_text_bold(self):
        """"""
        return self

    def cmd_set_text_italic(self):
        """"""
        return self

    def cmd_set_text_underline(self):
        """"""
        return self

    def cmd_set_text_underline_double(self):
        """"""
        return self

    def cmd_set_text_strike(self):
        """"""
        return self

    def cmd_set_text_subscript(self):
        """"""
        return self

    def cmd_set_text_superscript(self):
        """"""
        return self

    def cmd_sort_children(self, event=None, *args, **kwargs):
        """"""
        node = self.get_node()
        node.sortChildren()
        return self

    def cmd_take_snapshot(self):
        """"""
        return self

    def get_node(self):
        """"""
        logma.info(f"Get Node")
        node = self.app.model.get_current_node()
        logma.info(f"Node {node}")
        return node

    def get_tags(self):
        """"""
        # tags = self.app.model.get_tags()
        tags = ["journal", "library"]
        return tags


class NchantdOfficeNoteEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeTagEditPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.lock_page = False

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {"text": "Note: "}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        note_id = ""
        logma.info(f"Get Note {note_id}")
        note = self.get_note(note_id)
        cfg = {"label": "Note Name: ", "value": note}
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)
        cfg = {"show_label": False, "layout": "horizontal", "two_rows": True, "size": ["auto", "auto"]}
        self.font_bar = NchantdFontConfigBar(self, cfg).initWidget()
        layout.addWidget(self.font_bar)
        cfg = {}
        self.accept_buttons = NchantdOkButtons(self, cfg).initWidget()
        layout.addWidget(self.accept_buttons)
        # cfg = {"label": "Add Tag: ", "value": ""}
        # self.tag_entry = NchantdLabeledEntry(self, cfg).initWidget()
        # layout.addWidget(self.tag_entry)
        # self.tags = self.get_tags()
        # tags_label = NchantdLabel(self, {"text": "Tags: "}).initWidget()
        # layout.addWidget(tags_label)
        # cfg = {"items": self.tags, "columns": ["Tags"]}
        # self.tags_list = NchantdList(self, cfg).initWidget()
        # layout.addWidget(self.tags_list)
        # group.set_height(layout.sizeHint().height() * 1.2)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_close_tab(self, event=None, *args, **kwargs):
        """"""
        self.app.model.close_tab()
        return self

    def cmd_create_dataset(self, event=None, *args, **kwargs):
        """Create an addressable dataset from the most prominent data within the currently selected tab
        such as a File System will create a dataset of the files/directories in the active directory
        """
        # create data source
        # add data set
        df = self.create_data_table()
        self.add_dataset()
        return self

    def cmd_delete_notes(self):
        """"""
        return self

    def cmd_duplicate_document(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_export_document(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_import_file(self, event=None, *args, **kwargs):
        """"""
        cfg = {}
        self.open_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_file = self.open_file_sigil.file_selected
        if self.local_file is not None:
            if self.local_file.endswith(".ctd"):
                self.app.model.import_cherrytree(self.local_file)
        return self

    def cmd_launch_color_sigil(self, event, *args, **kwargs):
        """"""
        cfg = {}
        self.color_sigil = NchantdColorSelectSigil(self, cfg).initWidget()
        return self

    def cmd_set_text_bold(self):
        """"""
        return self

    def cmd_set_text_italic(self):
        """"""
        return self

    def cmd_set_text_underline(self):
        """"""
        return self

    def cmd_set_text_underline_double(self):
        """"""
        return self

    def cmd_set_text_strike(self):
        """"""
        return self

    def cmd_set_text_subscript(self):
        """"""
        return self

    def cmd_set_text_superscript(self):
        """"""
        return self

    def get_tab(self):
        """"""
        tab = self.app.model.get_current_tab()
        return tab

    def cmd_take_snapshot(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_toggle_page_lock(self, event=None, *args, **kwargs):
        """"""
        return self

    def decode64(self):
        """"""
        self.content = pycrypt.base64_decode(self.content).decode("utf-8")
        return self

    def decrypt(self):
        """"""
        self.content = pycrypt.decrypt(self.content)
        return self

    def encode64(self):
        """"""
        self.content = pycrypt.base64_encode(self.content.encode("utf-8"))
        return self

    def encrypt(self):
        """"""
        self.content = pycrypt.encrypt(self.content)
        return self

    def get_finger_print(self):
        """hash the whole image, as well as sub sections like corners
        a center cross and a center square
        need some way of scalling the hashses so that the image is recognized at all scales
        also use the color palette
        """
        return self

    def get_note(self, note_id):
        """"""
        note = None
        return note

    def get_notes(self):
        """"""
        return self

    def get_tags(self):
        """"""
        # tags = self.app.model.get_tags()
        tags = ["journal", "library"]
        return tags

    def parse_document(self):
        """"""
        doc_media = [
            self.document["uuid"],
            self.file_type,
            self.document["name"],
            self.document["description"],
            self.document["meta_data"]["path"],
            self.document["meta_data"]["store_location"],
            self.document["meta_data"]["encoding"],
            self.document["meta_data"]["tags"],
            self.document["meta_data"]["context"],
            self.document["meta_data"]["version"],
            self.document["meta_data"]["hash"],
            self.document["meta_data"]["policy_fk"],
        ]
        doc_media_content = []
        page = 0
        for content in document:
            media_content = [
                content["uuid"],
                self.document["uuid"],
                media_fk,
                page,
                entry,
                version,
                hash_,
                content_enc64,
                context,
            ]
            doc_media_content.append(media_content)
            page += 1
        return doc_media, doc_media_content

    def store_document(self, doctype, name, description, meta_data, data, format_, formula):
        """"""
        app_document_types_FK = 0
        data = [[uuid(), name, description, meta_data, app_document_types_FK]]
        app_documents_FK = self.app.model._store("document", data)
        self.store_document_data(data, format_, formula, app_documents_FK)

    def store_document_data(self, data, format_, formula, app_documents_FK, version_num=0):
        """"""
        while True:
            page_num, page = next(self.split_document(data, format_, formula))
            if page_num is None:
                break
            data, format_, formula = {"rows": page[0]}, {"rows": page[1]}, {"rows": page[2]}
            data_ = [
                [uuid(), j.dumps(data), j.dumps(format_), j.dumps(formula), page_num, version_num, app_documents_FK]
            ]
            self._store("documents_data", data_)

    def read(self):
        """"""
        with open(self.path, "r") as file:
            self.file = file
            self.content = self.file.read()
            self.original_content = self.content
        return self


class NchantdOfficeTabEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeTabEditPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.lock_page = False

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {"text": " Tab: "}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {
            "layout": "horizontal",
            "actions": {
                0: {"action": "duplicate_document", "type": "", "handler": self.cmd_duplicate_document},
                1: {"action": "import_document", "type": "", "handler": self.cmd_import_file},
                2: {"action": "export_document", "type": "", "handler": self.cmd_export_document},
                # 3: {"action": "create_dataset", "type": "", "handler": self.cmd_create_dataset},
                4: {"action": "take_snapshot", "handler": self.cmd_take_snapshot},
                5: {
                    "action": "unlock_view",
                    "handler": self.lock_page,
                    "checked": {"action": "lock_view", "handler": self.cmd_toggle_page_lock},
                },
                6: {"action": "delete_tab", "type": "", "handler": self.cmd_delete_tab},
            },
        }
        self.tab_buttonbar = NchantdButtonBar(self, cfg).initWidget()
        layout.addWidget(self.tab_buttonbar)
        tab = self.get_tab()
        logma.info(f"Tab {dir(tab)}")
        logma.info(f"Tab {tab.name}")
        logma.info(f"Tab {tab.type}")
        cfg = {"label": "Tab Name: ", "value": tab.name}
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)

        cfg = {"label": "Tab Position: ", "value": tab.position}
        self.position_entry = NchantdLabeledSpinBox(self, cfg).initWidget()
        layout.addWidget(self.position_entry)

        cfg = {"text": f"Tab Type: {tab.type}"}
        self.type_label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(self.type_label)
        cfg = {"show_label": False, "layout": "horizontal", "two_rows": True, "size": ["auto", "auto"]}
        self.font_bar = NchantdFontConfigBar(self, cfg).initWidget()
        layout.addWidget(self.font_bar)
        cfg = {"buttons": {"ok": {"handler": self.cmd_set_tab_name}}}
        self.accept_buttons = NchantdOkButtons(self, cfg).initWidget()
        layout.addWidget(self.accept_buttons)
        # notes_label = NchantdLabel(self, {"text": "Notes: "}).initWidget()
        # layout.addWidget(notes_label)
        # self.notes = self.get_notes()
        # cfg = {"data": self.notes, "columns": ["Notes"]}
        # self.notes_list = NchantdList(self, cfg).initWidget()
        # layout.addWidget(self.notes_list)
        # cfg = {"label": "Add Tag: ", "value": ""}
        # self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        # layout.addWidget(self.name_entry)
        # tags_label = NchantdLabel(self, {"text": "Tags: "}).initWidget()
        # layout.addWidget(tags_label)
        # self.tags = self.get_tags()
        # cfg = {"data": self.tags, "columns": ["Tags"]}
        # self.tags_list = NchantdList(self, cfg).initWidget()
        # layout.addWidget(self.tags_list)
        group.set_height(layout.sizeHint().height() * 1.2)
        self.layout.addWidget(group)

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_create_dataset(self, event=None, *args, **kwargs):
        """Create an addressable dataset from the most prominent data within the currently selected tab
        such as a File System will create a dataset of the files/directories in the active directory
        """
        # create data source
        # add data set
        df = self.create_data_table()
        self.add_dataset()
        return self

    def cmd_delete_tab(self, event=None, *args, **kwargs):
        """"""
        self.app.model.delete_tab(self.get_tab())
        tabset = self.app.view.panes["center"]
        tabset.go_to_previous_tab()
        return self

    def cmd_duplicate_document(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_export_document(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_import_file(self, event=None, *args, **kwargs):
        """"""
        cfg = {}
        self.open_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_file = self.open_file_sigil.file_selected
        if self.local_file is not None:
            if self.local_file.endswith(".ctd"):
                self.app.model.import_cherrytree(self.local_file)
        return self

    def cmd_launch_color_sigil(self, event, *args, **kwargs):
        """"""
        cfg = {}
        self.color_sigil = NchantdColorSelectSigil(self, cfg).initWidget()
        return self

    def cmd_set_tab_name(self, event, *args, **kwargs):
        """"""
        logma.info(f"Name Entry {self.name_entry}")
        logma.info(f"Set Tab Name {self.name_entry.textbox.entry_data}")
        tab = self.get_tab()
        if tab.app_data_type == "app":
            return self
        logma.info(f"Set Tab Name {self.name_entry.textbox.text()}")
        tab.parent.setTabText(tab.position, self.name_entry.textbox.entry_data)
        return self

    def cmd_set_text_bold(self):
        """"""
        return self

    def cmd_set_text_italic(self):
        """"""
        return self

    def cmd_set_text_underline(self):
        """"""
        return self

    def cmd_set_text_underline_double(self):
        """"""
        return self

    def cmd_set_text_strike(self):
        """"""
        return self

    def cmd_set_text_subscript(self):
        """"""
        return self

    def cmd_set_text_superscript(self):
        """"""
        return self

    def cmd_take_snapshot(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_toggle_page_lock(self, event=None, *args, **kwargs):
        """"""
        tab = self.get_tab()
        tab.lock_page = not tab.lock_page
        return self

    def get_finger_print(self):
        """hash the whole image, as well as sub sections like corners
        a center cross and a center square
        need some way of scalling the hashses so that the image is recognized at all scales
        also use the color palette
        """

        return self

    def get_notes(self):
        """"""
        # notes = self.app.model.get_notes()
        notes = ["note1", "note2", "note3"]
        return notes

    def get_tab(self):
        """"""
        tab = self.app.model.get_current_tab()
        return tab

    def get_tags(self):
        """"""
        # tags = self.app.model.get_tags()
        tags = ["journal", "library"]
        return tags

    def parse_document(self):
        """"""
        doc_media = [
            self.document["uuid"],
            self.file_type,
            self.document["name"],
            self.document["description"],
            self.document["meta_data"]["path"],
            self.document["meta_data"]["store_location"],
            self.document["meta_data"]["encoding"],
            self.document["meta_data"]["tags"],
            self.document["meta_data"]["context"],
            self.document["meta_data"]["version"],
            self.document["meta_data"]["hash"],
            self.document["meta_data"]["policy_fk"],
        ]
        doc_media_content = []
        page = 0
        for content in document:
            media_content = [
                content["uuid"],
                self.document["uuid"],
                media_fk,
                page,
                entry,
                version,
                hash_,
                content_enc64,
                context,
            ]
            doc_media_content.append(media_content)
            page += 1
        return doc_media, doc_media_content

    def store_document(self, doctype, name, description, meta_data, data, format_, formula):
        """"""
        app_document_types_FK = 0
        data = [[uuid(), name, description, meta_data, app_document_types_FK]]
        app_documents_FK = self.app.model._store("document", data)
        self.store_document_data(data, format_, formula, app_documents_FK)

    def store_document_data(self, data, format_, formula, app_documents_FK, version_num=0):
        """"""
        while True:
            page_num, page = next(self.split_document(data, format_, formula))
            if page_num is None:
                break
            data, format_, formula = {"rows": page[0]}, {"rows": page[1]}, {"rows": page[2]}
            data_ = [
                [uuid(), j.dumps(data), j.dumps(format_), j.dumps(formula), page_num, version_num, app_documents_FK]
            ]
            self._store("documents_data", data_)

    # def decode64(self):
    #     """"""
    #     self.content = pycrypt.base64_decode(self.content).decode("utf-8")
    #     return self
    #
    # def decrypt(self):
    #     """"""
    #     self.content = pycrypt.decrypt(self.content)
    #     return self
    #
    # def encode64(self):
    #     """"""
    #     self.content = pycrypt.base64_encode(self.content.encode("utf-8"))
    #     return self
    #
    # def encrypt(self):
    #     """"""
    #     self.content = pycrypt.encrypt(self.content)
    #     return self
    #
    # def read(self):
    #     """"""
    #     with open(self.path, "r") as file:
    #         self.file = file
    #         self.content = self.file.read()
    #         self.original_content = self.content
    #     return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
