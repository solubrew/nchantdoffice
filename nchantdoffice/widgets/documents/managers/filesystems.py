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
from os.path import dirname, join, getsize, expanduser
import datetime as dt
from os import stat

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
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
from nchantrs.widgets.media.editors.selectors import NchantdComboEditor, NchantdDropDown
from nchantdoffice.widgets.panes.files import NchantdFileDetailsPane

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
debug = False
# ====================================================================================================================||
pxcfg = join(here, "_data_", "filesystems.yaml")


class NchantdCompressPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdCompressPane").override(cfg))

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
        cfg = {"text": "Move Files on Compress", "size": ["auto", "auto"], "handler": self.cmd_move_files_on_compress}
        self.move_on_compress = NchantdCheckbox(self, cfg).initWidget()
        self.group_layout.addWidget(self.move_on_compress)
        cfg = {"text": "Rename Files on Compress", "size": ["auto", "auto"], "handler": self.cmd_rename_on_compress}
        self.rename_on_compress = NchantdCheckbox(self, cfg).initWidget()
        self.group_layout.addWidget(self.rename_on_compress)
        cfg = {
            "text": "Delete Files on Compress",
            "size": ["auto", "auto"],
            "handler": self.cmd_delete_files_on_compress,
        }
        self.delete_on_compress = NchantdCheckbox(self, cfg).initWidget()
        self.group_layout.addWidget(self.delete_on_compress)
        cfg = {
            "actions": {
                0: {"action": "compress_files", "handler": self.cmd_compress_files},
                1: {"action": "automate_action", "handler": self.cmd_automate_compress},
            },
            "layout": "horizontal",
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

    def cmd_automate_compress(self, event=None, *args, **kwargs):
        """Set up automated compression rules"""
        logma.info("Setting up compression automation...")
        # NOTE: Implement automation rules
        return self

    def cmd_delete_files_on_compress(self, event=None, *args, **kwargs):
        """Toggle whether files are deleted after compression"""
        self.delete_on_compress_enabled = self.delete_on_compress.isChecked() if hasattr(self, 'delete_on_compress') else True
        logma.info(f"Delete on compress: {self.delete_on_compress_enabled}")
        return self

    def cmd_compress_files(self, event=None, *args, **kwargs):
        """Compress selected files"""
        import zipfile
        from os.path import basename, exists
        from os import remove

        try:
            source_path = self.parent.fs_tree.current_level_path
            # Get selected files from table if selection exists
            selected_files = []
            if hasattr(self.parent, "file_table_one") and self.parent.file_table_one:
                # Get all files from current directory
                for item in self.parent.fs_tree.get_current_level_files():
                    selected_files.append(item.name)

            if not selected_files:
                logma.warning("No files selected for compression")
                return self

            # Create archive name based on folder
            archive_name = f"{basename(source_path)}_archive.zip"
            archive_path = join(source_path, archive_name)

            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_name in selected_files:
                    file_path = join(source_path, file_name)
                    if exists(file_path):
                        zipf.write(file_path, basename(file_path))
                        logma.info(f"Added to archive: {file_name}")

                        # Handle options
                        if self.delete_on_compress.isChecked():
                            remove(file_path)
                            logma.info(f"Deleted: {file_name}")

            logma.info(f"Created archive: {archive_path}")
            if hasattr(self.parent, "populate_table_one"):
                self.parent.populate_table_one()

        except Exception as e:
            logma.error(f"Error compressing files: {e}")

        return self

    def cmd_move_files_on_compress(self, event, *args, **kwargs):
        """"""
        # TODO: implement method

    def cmd_rename_on_compress(self, event, *args, **kwargs):
        """Toggle whether files are renamed after compression"""
        self.rename_on_compress_enabled = self.rename_on_compress.isChecked() if hasattr(self, 'rename_on_compress') else True
        logma.info(f"Rename on compress: {self.rename_on_compress_enabled}")
        return self

    def cmd_delete_files_on_selection(self, event, *args, **kwargs):
        """Delete files that are currently selected in the file table"""
        from os import remove
        from os.path import exists, join

        try:
            if not hasattr(self.parent, "file_table_one") or self.parent.file_table_one is None:
                logma.warning("No file table available")
                return self

            selected_files = []
            try:
                selected_items = self.parent.file_table_one.selectedItems()
                for item in selected_items:
                    selected_files.append(item.text())
            except Exception:
                logma.warning("Unable to retrieve selected items")
                return self

            source_path = self.parent.fs_tree.current_level_path
            for file_name in selected_files:
                file_path = join(source_path, file_name)
                if exists(file_path):
                    remove(file_path)
                    logma.info(f"Deleted file: {file_name}")

            if hasattr(self.parent, "populate_table_one"):
                self.parent.populate_table_one()
        except Exception as e:
            logma.error(f"Error deleting files on selection: {e}")
        return self

    def set_from_folder(self):
        """"""
        # if self.parent.fs_tree is None:
        #    self.parent.fs_tree =
        try:
            cfg = {
                "text": f"From Folder: \n{self.parent.fs_tree.current_level_path}",  # {self.app.active_tab.get_current_path()}",
                "size": ["auto", "auto"],
            }
        except Exception as e:
            logma.warning(e)
            if debug:
                raise e
            cfg = {"text": "", "size": ["auto", "auto"]}
        self.from_folder_label = NchantdLabel(self, cfg).initWidget()
        self.group_layout.addWidget(self.from_folder_label)
        return self


class NchantdImportPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdImportPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {"text": "Import Tool:"}
        group = NchantdGroup(self, cfg)
        group_layout = pyqt.QVBoxLayout()
        group.setLayout(group_layout)
        cfg = {
            "text": "Import File",
            "options": self.get_file_options() or [],
            "handler": self.cmd_file_change,
            "value": self.get_file() or "",
        }
        self.rename_format_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.rename_format_select)
        cfg = {
            "actions": {
                0: {"action": "rename_files", "handler": self.cmd_import_file},
                1: {"action": "automate_action", "handler": self.cmd_automate_import},
            },
            "layout": "horizontal",
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

    def cmd_automate_import(self, event=None, *args, **kwargs):
        """"""
        # TODO implement method

    def cmd_file_change(self, event=None, *args, **kwargs):
        """"""
        # TODO implement method

    def cmd_import_file(self, event=None, *args, **kwargs):
        """"""
        # TODO implement method

    def get_file(self):
        """"""
        # TODO implement method

    def get_file_options(self):
        """"""
        # TODO implement method

    def set_file(self, path):
        """"""
        # TODO implement method


class NchantdMovePane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdAlarmsListPane"))
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
            },
            "layout": "horizontal",
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

    def cmd_automate_move(self, event=None, *args, **kwargs):
        """"""
        # TODO: implement method

    def cmd_move_files(self, event=None, *args, **kwargs):
        """"""
        # TODO: implement method

    def set_from_folder(self):
        """"""
        # TODO: implement method


class NchantdRenamePane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdAlarmsListPane").override(cfg))

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
        cfg = {
            "text": "Rename Format",
            "options": self.get_file_rename_formats(),
            "handler": self.cmd_format_change,
            "value": self.get_file_rename_format(),
        }
        self.rename_format_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.rename_format_select)
        cfg = {
            "actions": {
                0: {"action": "rename_files", "handler": self.cmd_rename_files},
                1: {"action": "automate_action", "handler": self.cmd_automate_rename},
            },
            "layout": "horizontal",
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

    def cmd_format_change(self, event=None, *args, **kwargs):
        """"""
        # TODO implement method

    def cmd_automate_rename(self, event=None, *args, **kwargs):
        """Set up automated file renaming rules"""
        logma.info("Setting up rename automation...")
        return self

    def cmd_rename_files(self, event=None, *args, **kwargs):
        """Rename files based on selected format"""
        from os import rename as os_rename

        try:
            source_path = self.parent.fs_tree.current_level_path
            rename_format = self.rename_format_select.currentText()

            # Get files from current directory
            files = [item.name for item in self.parent.fs_tree.get_current_level_files()]

            for idx, file_name in enumerate(files):
                old_path = join(source_path, file_name)
                new_name = self.apply_rename_format(file_name, idx, rename_format)
                new_path = join(source_path, new_name)

                if old_path != new_path:
                    os_rename(old_path, new_path)
                    logma.info(f"Renamed: {file_name} -> {new_name}")

            if hasattr(self.parent, "populate_table_one"):
                self.parent.populate_table_one()

        except Exception as e:
            logma.error(f"Error renaming files: {e}")

        return self

    def apply_rename_format(self, filename, index, format_pattern):
        """Apply rename format pattern to filename"""
        from os.path import splitext
        import datetime as dt

        name, ext = splitext(filename)

        if format_pattern == "Add Prefix":
            return f"prefix_{filename}"
        elif format_pattern == "Add Suffix":
            return f"{name}_suffix{ext}"
        elif format_pattern == "Sequential Numbers":
            return f"{index+1:03d}{ext}"
        elif format_pattern == "Date Prefix":
            date_str = dt.datetime.now().strftime("%Y%m%d")
            return f"{date_str}_{filename}"
        elif format_pattern == "Lowercase":
            return filename.lower()
        elif format_pattern == "Uppercase":
            return filename.upper()
        elif format_pattern == "Remove Spaces":
            return filename.replace(" ", "_")
        else:
            return filename

    def get_file_rename_formats(self):
        """Get available rename format patterns"""
        formats = [
            "Add Prefix",
            "Add Suffix",
            "Sequential Numbers",
            "Date Prefix",
            "Lowercase",
            "Uppercase",
            "Remove Spaces",
        ]
        return formats

    def get_file_rename_format(self):
        """"""
        # TODO implement method

    def set_file(self, path):
        """"""
        # TODO implement method


class NchantdStorageEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdStorageEditPane").override(cfg))

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

    def set_file(self, path):
        """"""
        # TODO implement method


class NchantdOfficeFileSystem(NchantdOfficeDocument):
    """ ""File system document - implements PyfficeFileSystem"""

    PYTYPE = "filesystem"

    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for filesystem documents"""
        return [
            {"id": "browse", "icon": "folder", "label": "Browse", "method": "browse_files"},
            {"id": "search", "icon": "search", "label": "Search", "method": "search_files"},
            {"id": "filter", "icon": "filter", "label": "Filter", "method": "filter_files"},
            {"id": "sort", "icon": "sort", "label": "Sort", "method": "sort_files"},
            {"id": "import", "icon": "import", "label": "Import", "method": "import_files"},
            {"id": "export", "icon": "export", "label": "Export", "method": "export_files"},
        ]

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Nchantd Files", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeFileSystem").override(cfg))
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
            100: "_skip",  # PUSH to 0.0.3 Sketch not compatible to any outside protocol
        }
        ffes_cfg = {"handler": self.cmd_on_file_search_method_change, "action": "select_file_method"}
        self.flatten_files_enable_spin = NchantdEnableSpinBox(self, ffes_cfg)
        cfg["buttons"][13] = {
            "label": "Flatten Files",
            "action": "flatten_files",
            "handler": self.cmd_flatten_files,
            "widget": self.flatten_files_enable_spin,
        }
        fsms_cfg = {"label": "Search Method", "options": self.get_file_search_methods(), "layout": "horizontal"}
        self.file_search_method_select = NchantdComboEditor(self, fsms_cfg)
        cfg["buttons"][14] = {
            "action": "select_file_method",
            "widget": self.file_search_method_select,
            "handler": self.cmd_on_file_search_method_change,
        }
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
        # TODO implement method
        return self

    def cmd_on_file_search_method_change(self, event=None, *args, **kwargs):
        """"""
        # TODO implement method
        return self

    def cmd_on_file_search_edit(self, event=None, *args, **kwargs):
        """"""
        # TODO implement method
        return self

    def cmd_on_file_search_clear(self, event=None, *args, **kwargs):
        """"""
        # TODO implement method
        return self

    def cmd_on_node_expansion(self, event=None, *args, **kwargs):
        """"""
        # TODO implement method
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
        # NOTE needs to be implemented
        self.compare_fs = not self.compare_fs
        return self

    def cmd_add_storage(self, event=None, *args, **kwargs):
        """Add cloud storage configuration"""
        try:
            # Get storage configuration from storage_edit_pane
            if not hasattr(self, "storage_edit_pane"):
                logma.warning("Storage edit pane not initialized")
                return self

            # NOTE: Implement actual storage configuration
            # This would involve:
            # 1. Get storage type (Google Drive, Dropbox, OneDrive, etc.)
            # 2. Get authentication credentials
            # 3. Test connection
            # 4. Save configuration to self.clouds dictionary
            # 5. Update storage_list widget

            logma.info("Adding cloud storage configuration...")

            # Example placeholder structure:
            # storage_config = {
            #     'type': 'google_drive',  # or 'dropbox', 'onedrive', etc.
            #     'name': 'My Google Drive',
            #     'credentials': {...},
            #     'root_path': '/',
            # }
            # self.clouds[storage_config['type']] = storage_config
            # self.storage_list.add_item(storage_config['name'])

            logma.info("Cloud storage configuration requires API setup")

        except Exception as e:
            logma.error(f"Error adding storage: {e}")

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
            # FIX (was column mutation bug):
            #   - list.insert(idx, x) returns None (mutates in place),
            #     which would have made `columns` None on second call.
            #   - x.insert(0, "table1") in a comprehension produces a list of
            #     Nones (since each x[i].insert returns None).
            # Use list concatenation to create new lists safely.
            data = self.file_table_two.get_data()
            ndata = [["table1"] + x for x in ndata]
            columns = ["table"] + columns
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
        """Get files from Google Drive"""
        try:
            # Check if Google Drive is configured
            if "google_drive" not in self.clouds:
                logma.warning("Google Drive not configured")
                return self

            # NOTE: Implement actual Google Drive API integration
            # This would require google-api-python-client library
            # from googleapiclient.discovery import build
            # from google.oauth2.credentials import Credentials

            logma.info("Fetching Google Drive files...")
            # service = build('drive', 'v3', credentials=self.clouds['google_drive']['credentials'])
            # results = service.files().list(pageSize=100, fields="files(id, name, mimeType)").execute()
            # items = results.get('files', [])

            # For now, return empty placeholder
            logma.info("Google Drive integration requires API setup")

        except Exception as e:
            logma.error(f"Error accessing Google Drive: {e}")

        return self

    def get_children_dropbox(self):
        """Get files from Dropbox"""
        try:
            # Check if Dropbox is configured
            if "dropbox" not in self.clouds:
                logma.warning("Dropbox not configured")
                return self

            # NOTE: Implement actual Dropbox API integration
            # This would require dropbox library
            # import dropbox

            logma.info("Fetching Dropbox files...")
            # dbx = dropbox.Dropbox(self.clouds['dropbox']['access_token'])
            # result = dbx.files_list_folder('')
            # entries = result.entries

            # For now, return empty placeholder
            logma.info("Dropbox integration requires API setup")

        except Exception as e:
            logma.error(f"Error accessing Dropbox: {e}")

        return self

    def get_content(self):
        """"""
        return {"content": {"file_path": self.file_path}}

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
            items[cnt] = default_action.copy()
        cfg = {"label": "File Name: ", "layout": "horizontal"}
        self.file_pane = NchantdFileDetailsPane(self, cfg).initWidget()
        items[cnt]["widget"] = self.file_pane
        cnt += 1
        return items

    def init_drawer_storage_config(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"label": "Storage List", "layout": "vertical"}
        self.storage_list = NchantdList(self, cfg).initWidget()
        items[cnt]["widget"] = self.storage_list
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"label": "Add Storage"}
        self.storage_edit_pane = NchantdStorageEditPane(self, cfg).initWidget()
        items[cnt]["widget"] = self.storage_edit_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "Add Storage", "handler": self.cmd_add_storage}
        self.add_storage_button = NchantdButton(self, cfg).initWidget()
        items[cnt]["widget"] = self.add_storage_button
        cnt += 1
        return items

    def init_drawer_tools_config(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"label": "Import Tool", "layout": "vertical"}
        self.import_pane = NchantdImportPane(self, cfg).initWidget()
        items[cnt]["widget"] = self.import_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"label": "Rename Tool", "layout": "vertical"}
        self.rename_pane = NchantdRenamePane(self, cfg).initWidget()
        items[cnt]["widget"] = self.rename_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"label": "Move Tool", "layout": "vertical"}
        self.move_pane = NchantdMovePane(self, cfg).initWidget()
        items[cnt]["widget"] = self.move_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"label": "Compress Tool", "layout": "vertical"}
        self.compress_pane = NchantdCompressPane(self, cfg).initWidget()
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
        # PUSH to 0.0.3
        # self.toolbox_config[200]["items"] = self.init_drawer_tools_config()
        # self.toolbox_config[300]["items"] = self.init_drawer_storage_config()
        # self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def open_file(self, file=None):
        """"""
        # TODO not sure this fits as the whole document is basically a file nav window
        #  there is no real open of the file but we need to align the populate and config
        logma.info(file)
        # if self.file_path is None:
        self.file_path = file
        if file is None:
            file = self.file_path
        if file is not None:
            self.document.open_file(file)
        self.document.set_location("external")
        self.populate_document()
        return self

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
        # TODO test and refactor
        # if self.document.location is None:
        #     self.document.set_location("external")
        # if self.document.location == "external":
        #     content = self.document.content
        #     if content is None:
        #         content = {}
        #     if isinstance(content, dict):
        #         content["file_path"] = self.document.file_path
        #     logma.info(f"File Path {self.document.file_path}")
        #     logma.info(f"DID {self.document.did}")
        # elif self.document.location == "internal":
        #     content = self.get_binary()
        # else:
        #     raise Exception(f"Unknown storage location {self.document.location}")
        # logma.info(f"Location {self.document.location}")
        # logma.info(f"Content {content}")
        # logma.info(f"Content {self.document.content}")
        # if content != self.document.content:
        #     self.document.set_content(content)
        #     logma.info(f"Content {self.document.content}")
        # logma.info(f"Document {self.document.to_dict()}")
        super().save()
        return self

    def get_binary(self):
        """"""
        # TODO implement method

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
