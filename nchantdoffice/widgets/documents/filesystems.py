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
from os.path import abspath, dirname, join, getsize, expanduser
import datetime as dt
from os import stat

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.libraries import pyqt
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.trees import NchantdFileSystem
from nchantrs.widgets.tables.tables import NchantdTable
from nchantrs.widgets.media.editors.entries import NchantdActivateEntry
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.tables.lists import NchantdList
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.advanced_buttons import NchantdEnableSpinBox
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.groups import NchantdGroup
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.media.editors.selectors import NchantdComboEditor
from nchantdoffice.widgets.panes.files import NchantdFileDetailsPane

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "filesystems.yaml")


class NchantdCompressPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdAlarmsListPane"))
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
        cfg = {"text": "Compress Tool:"}
        group = NchantdGroup(self, cfg)
        self.group_layout = pyqt.QVBoxLayout()
        group.setLayout(self.group_layout)
        self.set_from_folder()
        cfg = {"text": "Move Files on Compress", "size": ["auto", "auto"]}
        self.move_on_compress = NchantdCheckbox(self, cfg).initWidget()
        self.group_layout.addWidget(self.move_on_compress)
        cfg = {"text": "Rename Files on Compress", "size": ["auto", "auto"]}
        self.rename_on_compress = NchantdCheckbox(self, cfg).initWidget()
        self.group_layout.addWidget(self.rename_on_compress)
        cfg = {"text": "Delete Files on Compress", "size": ["auto", "auto"]}
        self.delete_on_compress = NchantdCheckbox(self, cfg).initWidget()
        self.group_layout.addWidget(self.delete_on_compress)
        cfg = {
            "actions": {
                0: {"action": "compress_files", "handler": self.cmd_compress_files},
                1: {"action": "automate_action", "handler": self.cmd_automate_compress},
            }
        }
        self.tool_buttons = NchantdButtonBar(self, cfg).initWidget()
        self.group_layout.addWidget(self.tool_buttons)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_automate_compress(self):
        """"""

    def cmd_compress_files(self):
        """"""
        return self

    def set_from_folder(self):
        """"""
        cfg = {
            "text": f"From Folder: \n{self.parent.fs_tree.current_level_path}",  # {self.app.active_tab.get_current_path()}",
            "size": ["auto", "auto"],
        }
        self.from_folder_label = NchantdLabel(self, cfg).initWidget()
        self.group_layout.addWidget(self.from_folder_label)
        return self


class NchantdImportPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdImportPane"))
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
        cfg = {"text": "Import Tool:", "size": ["auto", "auto"]}
        group = NchantdGroup(self, cfg)
        self.group_layout = pyqt.QVBoxLayout()
        group.setLayout(self.group_layout)
        self.set_from_folder()
        cfg = {"text": "Import Files", "size": ["auto", "auto"]}
        self.move_on_compress = NchantdCheckbox(self, cfg).initWidget()
        self.group_layout.addWidget(self.move_on_compress)
        cfg = {"text": "Rename Files on Compress", "size": ["auto", "auto"]}
        self.rename_on_compress = NchantdCheckbox(self, cfg).initWidget()
        self.group_layout.addWidget(self.rename_on_compress)
        cfg = {"text": "Delete Files on Compress", "size": ["auto", "auto"]}
        self.delete_on_compress = NchantdCheckbox(self, cfg).initWidget()
        self.group_layout.addWidget(self.delete_on_compress)
        cfg = {
            "actions": {
                0: {"action": "compress_files", "handler": self.cmd_compress_files},
                1: {"action": "automate_action", "handler": self.cmd_automate_compress},
            }
        }
        self.tool_buttons = NchantdButtonBar(self, cfg).initWidget()
        self.group_layout.addWidget(self.tool_buttons)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_automate_compress(self):
        """"""

    def cmd_compress_files(self):
        """"""
        return self

    def set_from_folder(self):
        """"""
        cfg = {
            "text": f"From Folder: \n{self.parent.fs_tree.current_level_path}",  # {self.app.active_tab.get_current_path()}",
            "size": ["auto", "auto"],
        }
        self.from_folder_label = NchantdLabel(self, cfg).initWidget()
        self.group_layout.addWidget(self.from_folder_label)
        return self


class NchantdMovePane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdAlarmsListPane"))
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
        cfg = {"text": "Move Tool:"}
        group = NchantdGroup(self, cfg)
        self.group_layout = pyqt.QVBoxLayout()
        group.setLayout(self.group_layout)
        self.set_from_folder()

        cfg = {"action": "open_local_folder", "label": "Open Folder:", "layout": "horizontal"}
        self.open_to_folder_entry = NchantdActivateEntry(self, cfg).initWidget()
        self.group_layout.addWidget(self.open_to_folder_entry)
        cfg = {"text": "Rename Files on Move", "size": ["auto", "auto"]}
        self.rename_on_move = NchantdCheckbox(self, cfg).initWidget()
        self.group_layout.addWidget(self.rename_on_move)
        cfg = {
            "actions": {
                0: {"action": "move_files", "handler": self.cmd_move_files},
                1: {"action": "automate_action", "handler": self.cmd_automate_move},
            }
        }
        self.tool_buttons = NchantdButtonBar(self, cfg).initWidget()
        self.group_layout.addWidget(self.tool_buttons)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_automate_move(self):
        """"""
        return self

    def cmd_move_files(self):
        """"""
        return self

    def set_from_folder(self):
        """"""
        cfg = {
            "text": f"From Folder: \n{self.parent.fs_tree.current_level_path}",  # {self.app.active_tab.get_current_path()}",
            "size": ["auto", "auto"],
        }
        self.from_folder_label = NchantdLabel(self, cfg).initWidget()
        self.group_layout.addWidget(self.from_folder_label)
        return self


class NchantdRenamePane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdAlarmsListPane"))
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
        cfg = {"text": "Rename Tool:"}
        group = NchantdGroup(self, cfg)
        group_layout = pyqt.QVBoxLayout()
        group.setLayout(group_layout)
        cfg = {"text": "Rename Format", "options": self.get_file_rename_formats()}
        self.rename_format_select = NchantdComboEditor(self, cfg).initWidget()
        group_layout.addWidget(self.rename_format_select)
        cfg = {
            "actions": {
                0: {"action": "rename_files", "handler": self.cmd_rename_files},
                1: {"action": "automate_action", "handler": self.cmd_automate_rename},
            }
        }
        self.tool_buttons = NchantdButtonBar(self, cfg).initWidget()
        group_layout.addWidget(self.tool_buttons)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_automate_rename(self):
        """"""
        return self

    def cmd_rename_files(self):
        """"""
        return self

    def get_file_rename_formats(self):
        """"""
        formats = []
        return formats


class NchantdStorageEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdAlarmsListPane"))
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
        cfg = {"text": "Sources List:"}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"data": self.config.dikt.get("data", [])}
        self.layers_list = NchantdList(self, cfg).initWidget()
        layout.addWidget(self.layers_list)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeFileSystem(NchantdOfficeDocument):
    """""File system document - implements PyfficeFileSystem"""
    
    PYTYPE = 'filesystem'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for filesystem documents"""
        return [
            {'id': 'browse', 'icon': 'folder', 'label': 'Browse', 'method': 'browse_files'},
            {'id': 'search', 'icon': 'search', 'label': 'Search', 'method': 'search_files'},
            {'id': 'filter', 'icon': 'filter', 'label': 'Filter', 'method': 'filter_files'},
            {'id': 'sort', 'icon': 'sort', 'label': 'Sort', 'method': 'sort_files'},
            {'id': 'import', 'icon': 'import', 'label': 'Import', 'method': 'import_files'},
            {'id': 'export', 'icon': 'export', 'label': 'Export', 'method': 'export_files'},
        ]
    
    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Nchantd Files", parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeFileSystem"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.cloud_toolbar = None
        self.compare_fs = False
        self.show_automations = False
        self.fs_tree = None
        self.file_table_one = None
        self.file_table_one_changed = True
        self.file_table_two = None
        self.file_table_two_changed = True
        self.clouds = {}

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        document = {"document": self.config.dikt.get("document", {})}
        self.document = self.app.model.codex.init_files(document)
        self.document.load_document()
        self.context_menu_name = "context.document.files"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["buttons"] = {
            10: {"action": "set_home_fs", "handler": self.cmd_go_home},
            11: {"action": "show_compare_directory", "handler": self.cmd_toggle_compare_directory},
            12: {"action": "set_root", "handler": self.cmd_set_root},
            # add flatten option with a depth control to show all files flattened to a specific depth
            49: "_insert_stretch",
        }
        ffes_cfg = {"handler": self.cmd_on_file_search_method_change, "action": "select_file_method"}
        self.flatten_files_enable_spin = NchantdEnableSpinBox(self, ffes_cfg)
        # cfg["buttons"][13] = {
        #     "label": "Flatten Files",
        #     "action": "flatten_files",
        #     "handler": self.cmd_flatten_files,
        #     "widget": self.flatten_files_enable_spin,
        # }
        fsms_cfg = {"label": "Search Method", "options": self.get_file_search_methods(), "layout": "horizontal"}
        self.file_search_method_select = NchantdComboEditor(self, fsms_cfg)
        # cfg["buttons"][14] = {
        #     "action": "select_file_method",
        #     "widget": self.file_search_method_select,
        #     "handler": self.cmd_on_file_search_method_change,
        # }
        super().initView(cfg)
        self.table_layout = pyqt.QHBoxLayout()
        cfg = {}
        logma.info(f"Initialize File System")
        self.fs_tree = NchantdFileSystem(self, cfg).initWidget()
        self.fs_tree.itemExpanded.connect(self.cmd_on_node_expansion)
        self.fs_tree.itemPressed.connect(self.cmd_on_node_selection)  # may need to move to the underlieing widget
        self.fs_tree.setFixedWidth(self.width() * 0.15)
        self.fs_tree.setMinimumWidth(200)
        self.table_layout.addWidget(self.fs_tree)
        self.show_tree(self.document.file_path)
        self.layout.addLayout(self.table_layout)
        self.cmd_on_node_selection()
        return self

    def initWidget(self, cfg=None):
        """"""
        self.initModel(cfg)
        self.initView(cfg)
        return self

    def cmd_display_file_info(self, event=None, *args, **kwargs):
        """"""
        logma.info(f"Command Display File Info")
        name = self.file_table_one.get_cell_value()
        self.file_pane.set_file_name(name)
        path = join(self.fs_tree.current_level_path, name)
        self.file_pane.set_file_path(path)
        # self.file_pane.get_file_type(path)
        self.file_pane.get_file_size(path)
        self.file_pane.get_access_date(path)
        self.file_pane.get_created_date(path)
        self.file_pane.get_modified_date(path)

        self.import_pane.set_file_path(path)

        self.rename_pane.set_file_path(path)

        self.move_pane.set_file_path(path)

        self.compress_pane.set_file_path(path)

        return self

    def cmd_flatten_files(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_file_search_method_change(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_file_search_edit(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_file_search_clear(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_node_expansion(self, event=None, *args, **kwargs):
        """"""

        return self

    def cmd_on_node_selection(self, event=None, *args, **kwargs):
        """"""
        if event is not None:
            self.fs_tree.on_item_expanded(event)
        self.file_table_one_changed = True
        if self.file_table_one_changed is True:
            self.populate_table_one()
        if self.compare_fs:
            self.file_table_two_changed = True
            if self.file_table_two_changed is True:
                self.populate_table_two()
        return self

    def cmd_go_home(self, event=None, *args, **kwargs):
        """"""
        self.fs_tree.current_level_path = expanduser("~")
        return self.cmd_set_root()

    def cmd_set_root(self, event=None, *args, **kwargs):
        """"""
        logma.info(f"Command Set Root")
        self.show_tree(self.fs_tree.current_level_path)
        return self

    def cmd_toggle_compare_directory(self, event=None, *args, **kwargs):
        """"""
        self.compare_fs = not self.compare_fs
        return self

    def create_data_source(self):
        """"""
        self.app.model.add_datasource(self.name, self.create_data_table())
        return self

    def create_data_table(self):
        """"""
        df = super().create_data_table()
        columns = ["path", "type", "name", "size", "last_access"]
        data = self.file_table_one.get_data()
        ndata = []
        for row in data:
            if row[1] == "-":
                nrow = [self.path, "directory"] + row
            else:
                nrow = [self.path, "file"] + row
            ndata.append(nrow)
        if self.file_table_two is not None:
            data = self.file_table_two.get_data()
            ndata = [x.insert(0, "table1") for x in ndata]
            columns = columns.insert(0, "table")
            for row in data:
                nrow = ["table2", self.path, "file"] + row
                ndata.append(nrow)
        df = DataFrame(ndata, columns=columns)
        return df

    def get_file_search_methods(self):
        """"""
        methods = ["Search", "Filter"]
        return methods

    def get_children_google_drive(self):
        """"""
        return self

    def get_children_dropbox(self):
        """"""
        return self

    def get_current_path(self):
        """"""
        return self.fs_tree.current_level_path

    def get_table_one(self):
        """"""
        if self.file_table_one is not None:
            self.table_layout.removeWidget(self.file_table_one)
            self.file_table_one.deleteLater()
            self.file_table_one = None
        cfg = {
            "num_columns": 3,
            "columns": {
                "Name": {"handler": self.cmd_display_file_info},
                "Size": {"handler": self.cmd_display_file_info},
                "Last Access": {"handler": self.cmd_display_file_info},
            },
        }
        self.file_table_one = NchantdTable(self, cfg).initWidget()
        self.table_layout.addWidget(self.file_table_one)
        return self

    def get_table_two(self):
        """"""
        if self.file_table_two is not None:
            self.table_layout.removeWidget(self.file_table_two)
            self.file_table_two.deleteLater()
            self.file_table_two = None
        cfg = {"num_columns": 3, "columns": ["Name", "Size", "Last Access"]}
        self.file_table_two = NchantdTable(self, cfg).initWidget()
        self.table_layout.addWidget(self.file_table_two)
        return self

    def init_drawer_document_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "File Name: ", "layout": "horizontal"}
        self.file_pane = NchantdFileDetailsPane(self, cfg)
        items[cnt]["widget"] = self.file_pane
        cnt += 1
        return items

    def init_drawer_storage_config(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "Storage List", "layout": "vertical"}
        self.storage_list = NchantdList(self, cfg)
        items[cnt]["widget"] = self.storage_list
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "Add Storage"}
        self.storage_edit_pane = NchantdStorageEditPane(self, cfg)
        items[cnt]["widget"] = self.storage_edit_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "Add Storage"}
        self.add_storage_button = NchantdButton(self, cfg)
        items[cnt]["widget"] = self.add_storage_button
        cnt += 1
        return items

    def init_drawer_tools_config(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "Import Tool", "layout": "vertical"}
        self.import_pane = NchantdImportPane(self, cfg)
        items[cnt]["widget"] = self.import_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "Rename Tool", "layout": "vertical"}
        self.rename_pane = NchantdRenamePane(self, cfg)
        items[cnt]["widget"] = self.rename_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "Move Tool", "layout": "vertical"}
        self.move_pane = NchantdMovePane(self, cfg)
        items[cnt]["widget"] = self.move_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "Compress Tool", "layout": "vertical"}
        self.compress_pane = NchantdCompressPane(self, cfg)
        items[cnt]["widget"] = self.compress_pane
        cnt += 1
        return items

    def init_drawer_quickstart(self):
        """"""
        items = {}
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_tools_config()
        # self.toolbox_config[300]["items"] = self.init_drawer_storage_config()
        # self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def populate_document(self):
        """"""
        self.populate_table_one()
        if self.compare_fs:
            self.populate_table_two()
        return self

    def populate_table_one(self):
        """"""
        self.get_table_one()
        data = []
        for item in self.fs_tree.get_current_level_files():
            last_access = dt.datetime.fromtimestamp(stat(item).st_atime)
            data.append([item.name, getsize(item) / (1024 * 1024), last_access])
        for item in self.fs_tree.get_current_level_directories():
            last_access = dt.datetime.fromtimestamp(stat(item).st_atime)
            data.append([item.name, "-", last_access])
        self.file_table_one.update_data(data)
        return self

    def populate_table_two(self):
        """"""
        self.get_table_two()
        data = []
        for item in self.fs_tree.get_current_level_files():
            path = join(self.fs_tree.current_level_path, item.name)
            last_access = dt.datetime.fromtimestamp(stat(path).st_atime)
            data.append([item.name, getsize(path) / (1024 * 1024), last_access])
        for item in self.fs_tree.get_current_level_directories():
            path = join(self.fs_tree.current_level_path, item.name)
            last_access = dt.datetime.fromtimestamp(stat(path).st_atime)
            data.append([item.name, "-", last_access])
        self.file_table_two.update_data(data)

    def save(self):
        """"""
        logma.info(f"Saving document")
        if self.document.location is None:
            self.document.set_location("external")
        if self.document.location == "external":
            content = self.document.content
            if content is None:
                content = {}
            if isinstance(content, dict):
                content["file_path"] = self.document.file_path
            logma.info(f"File Path {self.document.file_path}")
            logma.info(f"DID {self.document.did}")
        elif self.document.location == "internal":
            content = self.get_binary()
        else:
            raise Exception(f"Unknown storage location {self.document.location}")
        logma.info(f"Location {self.document.location}")
        logma.info(f"Content {content}")
        logma.info(f"Content {self.document.content}")
        if content != self.document.content:
            self.document.set_content(content)
            logma.info(f"Content {self.document.content}")
        logma.info(f"Document {self.document.to_dict()}")
        super().save()
        return self

    def show_tree(self, file=None):
        """"""
        if file is None or file == "":
            file = self.file_path
        if file == "":
            file = None
        logma.info(f"File Path {file}")
        self.document.open_file(file)
        self.fs_tree.set_root(file)
        self.populate_document()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
