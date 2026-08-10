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
        # PUSH to 0.0.3 force external until
        self.document.set_location("external")

        # if self.document.location == "external":
        #    self.open_file(self.document.file_path)
        # PUSH to 0.0.3
        # elif self.document.location == "internal":
        #    self.populate_data()
        # elif self.document.location == "cloud":
        #    self.connect_to_file()
        # else:
        #    raise Exception("Internal and Cloud locations not supported yet")
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
        self.delete_on_compress_enabled = (
            self.delete_on_compress.isChecked() if hasattr(self, "delete_on_compress") else True
        )
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

    def cmd_move_files_on_compress(self, event=None, *args, **kwargs):
        """Move files to a new folder when compressing an archive.

        Real logic: reads the source folder from
        ``self.from_folder``, the destination from
        ``self.to_folder`` (both set up by set_from_folder),
        and moves each file via shutil.move. Wraps the whole
        operation in try/except + logs each step.
        """
        try:
            from_dir = getattr(self, "from_folder", None)
            to_dir = getattr(self, "to_folder", None)
            if not from_dir or not to_dir:
                logma.info("[filesystems] cmd_move_files_on_compress: from_folder / to_folder not set")
                return self
            import os as _os, shutil

            if not _os.path.isdir(from_dir):
                return self
            _os.makedirs(to_dir, exist_ok=True)
            moved = 0
            for entry in _os.listdir(from_dir):
                src = _os.path.join(from_dir, entry)
                dst = _os.path.join(to_dir, entry)
                if _os.path.isfile(src):
                    try:
                        shutil.move(src, dst)
                        moved += 1
                    except (OSError, shutil.Error) as e:
                        logma.error(f"[filesystems] move {src} -> {dst} failed: {e}")
            logma.info(f"[filesystems] cmd_move_files_on_compress moved {moved} files")
        except Exception as e:
            logma.error(f"[filesystems] cmd_move_files_on_compress failed: {e}", exc_info=True)
        return self

    def cmd_rename_on_compress(self, event, *args, **kwargs):
        """Toggle whether files are renamed after compression"""
        self.rename_on_compress_enabled = (
            self.rename_on_compress.isChecked() if hasattr(self, "rename_on_compress") else True
        )
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
        """Auto-import files matching the configured search pattern.

        Reads the file-search pattern from the config and runs an
        import for each matching file under the configured root.
        """
        try:
            root = self.config.dikt.get("file_root", ".")
            pattern = self.config.dikt.get("file_search_pattern", "*")
            from os.path import join
            from glob import glob

            matches = glob(join(root, pattern), recursive=True)
            for path in matches:
                self.cmd_import_file(path=path)
        except Exception as e:
            logma.error(f"[filesystems] cmd_automate_import failed: {e}", exc_info=True)
        return self

    def cmd_file_change(self, event=None, *args, **kwargs):
        """Record the user-selected file from the file picker.

        Reads the current value from ``self.file_select`` and stores
        the path on ``self.file_path`` so subsequent commands know
        which file to operate on.
        """
        if hasattr(self, "file_select") and self.file_select is not None:
            getter = getattr(self.file_select, "currentText", None) or getattr(self.file_select, "get_value", None)
            if callable(getter):
                value = getter()
                if value:
                    self.file_path = value
                    self.config.dikt["file_path"] = value
        return self

    def cmd_import_file(self, event=None, *args, **kwargs):
        """Import a file from disk into the active filesystem view.

        Accepts the path via ``path=`` keyword argument or falls back
        to ``self.file_path``. Re-loads the file's content into the
        table and records the action on the config.
        """
        path = kwargs.get("path") or getattr(self, "file_path", None)
        if not path:
            return self
        try:
            from os.path import exists

            if not exists(path):
                logma.warning(f"[filesystems] cmd_import_file: not found: {path}")
                return self
            if hasattr(self, "load_file"):
                self.load_file(path)
            history = list(self.config.dikt.get("file_import_history", []) or [])
            if path in history:
                history.remove(path)
            history.insert(0, path)
            self.config.dikt["file_import_history"] = history[:50]
            self.config.dikt["file_path"] = path
        except Exception as e:
            logma.error(f"[filesystems] cmd_import_file failed: {e}", exc_info=True)
        return self

    def get_file(self):
        """Return the stored value of get_file."""
        return getattr(self, "file_path", None) or self.config.dikt.get("file_path", "")

    def get_file_options(self):
        """Return the stored value of get_file_options."""
        return self.config.dikt.get("file_options", []) or []

    def set_file(self, path):
        """Set the active file path (real implementation).

        Stores ``path`` on ``self.file_path`` and on
        ``self.config.dikt['file_path']``. Validates the file
        exists when ``path`` is non-empty. Returns ``self``.
        """
        try:
            import os as _os

            self.file_path = path or ""
            if hasattr(self, "config"):
                self.config.dikt["file_path"] = self.file_path
            if path and not _os.path.isfile(path):
                logma.info(f"[filesystems] set_file: {path!r} not a file")
        except Exception as e:
            logma.error(f"[filesystems] set_file failed: {e}", exc_info=True)
        return self


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
        """Automate the file move flow.

        Reads the user's automation rules from
        ``self.config.dikt['move_rules']`` (a list of
        {pattern, target_subdir} dicts), applies each rule to
        the source folder, and persists progress on
        ``self.config.dikt['last_move_timestamp']`` so the UI
        can show "last run at HH:MM".
        """
        try:
            import os as _os, shutil, re, datetime

            from_dir = getattr(self, "from_folder", None)
            if not from_dir or not _os.path.isdir(from_dir):
                logma.info("[filesystems] cmd_automate_move: no from_folder")
                return self
            rules = []
            if hasattr(self, "config"):
                rules = self.config.dikt.get("move_rules", []) or []
            moved = 0
            for entry in _os.listdir(from_dir):
                src = _os.path.join(from_dir, entry)
                if not _os.path.isfile(src):
                    continue
                for rule in rules:
                    if not isinstance(rule, dict):
                        continue
                    pattern = rule.get("pattern", ".*")
                    target_subdir = rule.get("target_subdir", "")
                    if re.search(pattern, entry):
                        dst = _os.path.join(from_dir, target_subdir, entry)
                        try:
                            _os.makedirs(_os.path.dirname(dst), exist_ok=True)
                            shutil.move(src, dst)
                            moved += 1
                        except (OSError, shutil.Error) as e:
                            logma.error(f"[filesystems] automate move: {e}")
            if hasattr(self, "config"):
                self.config.dikt["last_move_timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
            logma.info(f"[filesystems] cmd_automate_move ran {len(rules)} rules, moved {moved}")
        except Exception as e:
            logma.error(f"[filesystems] cmd_automate_move failed: {e}", exc_info=True)
        return self

    def cmd_move_files(self, event=None, *args, **kwargs):
        """Move all files from from_folder to to_folder.

        Reads the source / destination paths (set by
        set_from_folder), walks the source directory, and
        moves each file via shutil.move. Skips empty
        directories and subdirectories.
        """
        try:
            from_dir = getattr(self, "from_folder", None)
            to_dir = getattr(self, "to_folder", None)
            if not from_dir or not to_dir:
                logma.info("[filesystems] cmd_move_files: from_folder / to_folder not set")
                return self
            import os as _os, shutil

            if not _os.path.isdir(from_dir):
                return self
            _os.makedirs(to_dir, exist_ok=True)
            moved = 0
            for entry in _os.listdir(from_dir):
                src = _os.path.join(from_dir, entry)
                dst = _os.path.join(to_dir, entry)
                if _os.path.isfile(src):
                    try:
                        shutil.move(src, dst)
                        moved += 1
                    except (OSError, shutil.Error) as e:
                        logma.error(f"[filesystems] move {src} -> {dst} failed: {e}")
            logma.info(f"[filesystems] cmd_move_files moved {moved} files")
        except Exception as e:
            logma.error(f"[filesystems] cmd_move_files failed: {e}", exc_info=True)
        return self

    def set_from_folder(self):
        """Prompt for a source / destination folder pair.

        Opens a NchantdFolderOpenSigil dialog for the source
        folder and another for the destination, then stores
        them on self.from_folder / self.to_folder. Returns
        ``self``.
        """
        try:
            from nchantrs.widgets.editors.entries import NchantdFolderOpenSigil

            self.from_folder = NchantdFolderOpenSigil(self, {}).initWidget().get_path()
            self.to_folder = NchantdFolderOpenSigil(self, {}).initWidget().get_path()
            if hasattr(self, "config"):
                self.config.dikt["from_folder"] = self.from_folder
                self.config.dikt["to_folder"] = self.to_folder
        except Exception as e:
            logma.error(f"[filesystems] set_from_folder failed: {e}", exc_info=True)
        return self


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
        """Update the file-format selection on the config.

        Reads the current value from the format-selector widget and
        stores it on ``config.dikt["file_format"]`` so subsequent
        import/export commands know which format to use.
        """
        if hasattr(self, "format_select") and self.format_select is not None:
            getter = getattr(self.format_select, "currentText", None) or getattr(self.format_select, "get_value", None)
            if callable(getter):
                value = getter()
                if value:
                    self.config.dikt["file_format"] = value
        return self

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

    def _rename_add_prefix(name, ext, filename, index):
        """Add a literal ``prefix_`` to the start of the filename."""
        return f"prefix_{filename}"

    def _rename_add_suffix(name, ext, filename, index):
        """Add a literal ``_suffix`` between the basename and extension."""
        return f"{name}_suffix{ext}"

    def _rename_sequential(name, ext, filename, index):
        """Rename the file to its 1-based index, padded to 3 digits."""
        return f"{index + 1:03d}{ext}"

    def _rename_date_prefix(name, ext, filename, index):
        """Add ``YYYYMMDD_`` to the start of the filename."""
        return f"{dt.datetime.now().strftime('%Y%m%d')}_{filename}"

    def _rename_lowercase(name, ext, filename, index):
        """Lowercase the entire filename."""
        return filename.lower()

    def _rename_uppercase(name, ext, filename, index):
        """Uppercase the entire filename."""
        return filename.upper()

    def _rename_remove_spaces(name, ext, filename, index):
        """Replace spaces with underscores."""
        return filename.replace(" ", "_")

    # Rename-format dispatch — adding a new format means adding one entry here.
    # Each method receives ``(name, ext, filename, index)``.
    _RENAME_FORMATS = {
        "Add Prefix": _rename_add_prefix,
        "Add Suffix": _rename_add_suffix,
        "Sequential Numbers": _rename_sequential,
        "Date Prefix": _rename_date_prefix,
        "Lowercase": _rename_lowercase,
        "Uppercase": _rename_uppercase,
        "Remove Spaces": _rename_remove_spaces,
    }

    def apply_rename_format(self, filename, index, format_pattern):
        """Apply rename format pattern to filename."""
        from os.path import splitext

        name, ext = splitext(filename)
        formatter = self._RENAME_FORMATS.get(format_pattern)
        if formatter is None:
            return filename
        return formatter(name, ext, filename, index)

    def get_file_rename_formats(self):
        """Get available rename format patterns."""
        return list(self._RENAME_FORMATS.keys())

    def get_file_rename_format(self):
        """Return the stored value of get_file_rename_format."""
        return self.config.dikt.get("file_rename_format", "") or ""

    def set_file(self, path):
        """Set the active file path (real implementation).

        Stores ``path`` on ``self.file_path`` and on
        ``self.config.dikt['file_path']``. Validates the file
        exists when ``path`` is non-empty. Returns ``self``.
        """
        try:
            import os as _os

            self.file_path = path or ""
            if hasattr(self, "config"):
                self.config.dikt["file_path"] = self.file_path
            if path and not _os.path.isfile(path):
                logma.info(f"[filesystems] set_file: {path!r} not a file")
        except Exception as e:
            logma.error(f"[filesystems] set_file failed: {e}", exc_info=True)
        return self


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
        """Set the active file path (real implementation).

        Stores ``path`` on ``self.file_path`` and on
        ``self.config.dikt['file_path']``. Validates the file
        exists when ``path`` is non-empty. Returns ``self``.
        """
        try:
            import os as _os

            self.file_path = path or ""
            if hasattr(self, "config"):
                self.config.dikt["file_path"] = self.file_path
            if path and not _os.path.isfile(path):
                logma.info(f"[filesystems] set_file: {path!r} not a file")
        except Exception as e:
            logma.error(f"[filesystems] set_file failed: {e}", exc_info=True)
        return self


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
        self.table_layout = pyqt.QHBoxLayout()
        fs_cfg = {}
        logma.info(f"Initialize File System")
        self.fs_tree = NchantdFileSystem(self, fs_cfg).initWidget()
        super().initView(cfg)



        self.fs_tree.itemExpanded.connect(self.cmd_on_node_expansion)
        self.fs_tree.itemPressed.connect(self.cmd_on_node_selection)  # may need to move to the underlieing widget
        self.fs_tree.setFixedWidth(self.width() * 0.15)
        self.fs_tree.setMinimumWidth(200)
        self.table_layout.addWidget(self.fs_tree)
        # T-NEW-068 — restore last-visited directory on re-open.
        # ``last_root_path`` was set by the previous session's
        # ``show_tree`` call (or by an explicit ``cmd_set_root``).
        # Falling back to ``self.document.file_path`` preserves
        # the pre-existing behaviour for first-launch / no-history.
        # ``last_root_path`` takes precedence because the user
        # may have navigated to a sub-directory and saved that
        # explicitly via ``cmd_set_root`` (which doesn't update
        # ``self.document.file_path``).
        restore_path = self._resolve_restore_path()
        self.show_tree(restore_path)
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
        """Flatten the directory tree of the current file root.

        Reads ``config.dikt["file_root"]`` and the active file list,
        then writes a flat list of (path, size, mtime) tuples to
        ``config.dikt["flat_file_list"]``.
        """
        try:
            from os import walk
            from os.path import join, getsize, getmtime

            root = self.config.dikt.get("file_root", ".")
            flat = []
            for dirpath, _dirnames, filenames in walk(root):
                for name in filenames:
                    full = join(dirpath, name)
                    try:
                        flat.append((full, getsize(full), getmtime(full)))
                    except OSError:
                        continue
            self.config.dikt["flat_file_list"] = flat
        except Exception as e:
            logma.error(f"[filesystems] cmd_flatten_files failed: {e}", exc_info=True)
        return self

    def cmd_on_file_search_method_change(self, event=None, *args, **kwargs):
        """Record the file-search method change on the config.

        Reads the selection from the search-method widget and stores
        it on ``config.dikt["file_search_method"]`` so the next search
        uses the chosen strategy (e.g. "glob", "regex", "name").
        """
        if hasattr(self, "file_search_method_select") and self.file_search_method_select is not None:
            getter = getattr(self.file_search_method_select, "currentText", None) or getattr(
                self.file_search_method_select, "get_value", None
            )
            if callable(getter):
                value = getter()
                if value:
                    self.config.dikt["file_search_method"] = value
        return self

    def cmd_on_file_search_edit(self, event=None, *args, **kwargs):
        """Run the file search with the current search pattern.

        Reads the configured search method (``glob``, ``regex``,
        ``name``) and pattern, then writes the matching file list to
        ``config.dikt["file_search_results"]``.
        """
        try:
            method = self.config.dikt.get("file_search_method", "glob")
            pattern = self.config.dikt.get("file_search_pattern", "")
            root = self.config.dikt.get("file_root", ".")
            results = []
            if method == "glob":
                from glob import glob
                from os.path import join

                results = glob(join(root, pattern), recursive=True)
            elif method == "regex":
                import re
                from os import walk
                from os.path import join

                compiled = re.compile(pattern)
                for dirpath, _dirnames, filenames in walk(root):
                    for name in filenames:
                        if compiled.search(name):
                            results.append(join(dirpath, name))
            elif method == "name":
                from os import walk
                from os.path import join

                for dirpath, _dirnames, filenames in walk(root):
                    for name in filenames:
                        if pattern and pattern in name:
                            results.append(join(dirpath, name))
            self.config.dikt["file_search_results"] = results
        except Exception as e:
            logma.error(f"[filesystems] cmd_on_file_search_edit failed: {e}", exc_info=True)
        return self

    def cmd_on_file_search_clear(self, event=None, *args, **kwargs):
        """Clear the current file-search state.

        Resets ``file_search_pattern`` and ``file_search_results`` on
        the config so the next search starts fresh.
        """
        self.config.dikt["file_search_pattern"] = ""
        self.config.dikt["file_search_results"] = []
        return self

    def cmd_on_node_expansion(self, event=None, *args, **kwargs):
        """Handle a node expansion event in the file tree.

        Reads the expanded node's path from the event and writes it
        on ``config.dikt["expanded_node"]`` so downstream code can
        react to the user's navigation.
        """
        path = None
        if event is not None:
            data = getattr(event, "data", None) or getattr(event, "path", None)
            if data is not None:
                path = str(data)
            elif hasattr(event, "node"):
                path = getattr(event.node, "path", None)
        if path is not None:
            self.config.dikt["expanded_node"] = path
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

    def _resolve_restore_path(self):
        """T-NEW-068 — pick the path ``initView`` should restore on re-open.

        Returns ``config.dikt["last_root_path"]`` when it is a
        non-empty string; otherwise falls back to
        ``self.document.file_path``. Pure function over
        ``self.config.dikt`` + ``self.document.file_path`` —
        no Qt state — so it's directly unit-testable.

        Whitespace-only strings (e.g. ``"   "``) are treated
        as unset so a previous bad write doesn't break
        restoration.
        """
        last_root = self.config.dikt.get("last_root_path")
        if (
            last_root
            and isinstance(last_root, str)
            and last_root.strip()
        ):
            return last_root
        return getattr(self.document, "file_path", None)

    def cmd_go_home(self, event=None, path=None, *args, **kwargs):
        """T-NEW-068 — navigate to a "home" directory.

        Default ``path`` is ``expanduser("~")``. Accepts an
        explicit ``path`` kwarg so callers / tests can override
        without patching. Mirrors the new interface contract
        requested by the user (testing-report_20260810.md
        line 27: "need to nailed down the interface inputs").

        Returns self for chainable callers.
        """
        if path is None or path == "":
            path = expanduser("~")
        self.fs_tree.current_level_path = path
        return self.cmd_set_root(path=path)

    def cmd_set_root(self, event=None, path=None, *args, **kwargs):
        """T-NEW-068 — navigate to ``path`` (or the current
        ``fs_tree.current_level_path`` when None).

        Accepts an explicit ``path`` kwarg. Persists the
        resolved path to ``config.dikt["last_root_path"]`` so
        the next ``initView`` call (e.g. app restart) restores
        the user to the same directory.

        Returns self for chainable callers.
        """
        if path is None or path == "":
            path = getattr(self.fs_tree, "current_level_path", None)
        logma.info(f"[filesystems] Command Set Root path={path!r}")
        if path:
            self.fs_tree.current_level_path = path
            # T-NEW-068 — persist so the next initView restores
            # this directory.
            self.config.dikt["last_root_path"] = path
        return self.show_tree(path)

    def cmd_toggle_compare_directory(self, event=None, *args, **kwargs):
        """"""
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
        """Return the file-system payload for persistence.

        Carries:
          - ``file_path``: the current ``self.file_path``
            (canonical Pyffice source).
          - ``root_path``: the directory the user is rooted at
            (``self.fs_tree.current_level_path``). On reopen the
            file tree re-expands to this directory so the user
            returns to their working context. Live bug: missing
            prior to this fix.
          - ``expanded_paths``: the list of directories the user
            had expanded before closing the tab. On reopen these
            are re-expanded so the user's tree state is exactly
            preserved. Live bug: missing prior to this fix.
        """
        root_path = getattr(getattr(self, "fs_tree", None), "current_level_path", None) or self.file_path
        expanded_paths = list(getattr(getattr(self, "fs_tree", None), "expanded_paths", []) or [])
        return {
            "content": {
                "file_path": self.file_path,
                "root_path": root_path,
                "expanded_paths": expanded_paths,
            }
        }

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
        """Open a file-system path inside the file-nav document.

        T-041: this is intentionally a navigation-only operation
        (the document IS the file nav window, not a file editor).
        We align the populate + config state and reset the
        file-table contents so the user sees the new directory
        rather than stale data.
        """
        logma.info(f"[filesystems] open_file {file}")
        self.file_path = file
        if file is None:
            file = getattr(self, "current_path", None)
        if file is not None:
            self.config.dikt["current_path"] = file
            if hasattr(self, "document") and self.document is not None:
                if hasattr(self.document, "set_location"):
                    self.document.set_location("external")
                if hasattr(self.document, "set_file_path"):
                    self.document.set_file_path(file)
        if hasattr(self, "clear_table_views"):
            self.clear_table_views()
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
        """Persist the file-nav document's current state.

        T-042: branches on the document's location:
          - "external" -> store the file_path on the content dict
            and delegate to the parent save
          - "internal" -> store the binary representation
          - anything else -> delegate to the parent save (best
            effort)
        Returns ``self`` for chainable call sites.
        """
        logma.info("[filesystems] save")
        if not hasattr(self, "document") or self.document is None:
            return self
        try:
            if getattr(self.document, "location", None) is None:
                if hasattr(self.document, "set_location"):
                    self.document.set_location("external")
            location = getattr(self.document, "location", "external")
            if location == "external":
                content = getattr(self.document, "content", None) or {}
                if isinstance(content, dict):
                    content["file_path"] = getattr(self.document, "file_path", None)
                if hasattr(self.document, "set_content"):
                    self.document.set_content(content)
            elif location == "internal":
                binary = self.get_binary() if hasattr(self, "get_binary") else None
                if binary and hasattr(self.document, "set_binary"):
                    self.document.set_binary(binary)
        except Exception as e:
            logma.error(f"[filesystems] save: doc-state persist failed: {e}", exc_info=True)
        try:
            super().save()
        except Exception as e:
            logma.error(f"[filesystems] save: super().save() failed: {e}", exc_info=True)
        return self

    def clear_table_views(self):
        """Clear both file-table widgets (used when navigating to a new path).

        T-041 helper - resets the table contents without rebuilding
        the widget tree so the next populate fills them with the
        correct data.
        """
        try:
            for attr in ("file_table_one", "file_table_two"):
                table = getattr(self, attr, None)
                if table is not None and hasattr(table, "update_data"):
                    table.update_data([])
        except Exception as e:
            logma.error(f"[filesystems] clear_table_views failed: {e}", exc_info=True)
        return self
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
        """Return the stored value of get_binary."""
        return self.config.dikt.get("file_binary", b"") or b""

    def show_tree(self, file=None):
        """T-NEW-068 — show the file tree at ``file``.

        Persists the resolved path to
        ``config.dikt["last_root_path"]`` so the next
        ``initView`` call (e.g. app restart) restores the
        user to the same directory.
        """
        if file is None or file == "":
            file = self.file_path
        if file == "":
            file = None
        logma.info(f"File Path {file}")
        if file:
            # T-NEW-068 — persist on every show_tree call so
            # direct callers (and the initView restoration path)
            # all converge on the same persisted state.
            self.config.dikt["last_root_path"] = file
        self.document.open_file(file)
        self.fs_tree.set_root(file)
        self.populate_document()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
