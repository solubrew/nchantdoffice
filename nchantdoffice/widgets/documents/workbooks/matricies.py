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
from os.path import abspath, dirname, join, exists
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.controls.advanced_buttons import NchantdNumberWheelButton, NchantdLabeledSpinBox, NchantdSpinBox
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.tables.tables import NchantdDataFrameTable, NchantdTable
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry, NchantdEntryBox
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.media.editors.selectors import NchantdDropDown, NchantdComboBox
from nchantrs.dialogs.colors import NchantdColorSelectSigil
from pyffice.matrix.spreadsheet import PyfficeMatrix
from pyffice.workflows.formulas import PyfficeFormulasLibrary
from kahndor.logma import Logma
from nchantrs.widgets.controls.button_groups import NchantdFontConfigBar

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
debug = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "matricies.yaml")


class NchantdOfficeCellBorderFormats(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeCellBorderFormats"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "grid"
        super().initView(cfg)
        cnt = 0
        cfg = {"text": self.config.dikt.get("label", "Missing Label")}
        label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(label, cnt, 0, 1, 4)
        cnt += 1
        self.layout.addWidget(NchantdLabel(self, {"text": "Top"}).initWidget(), cnt, 0)
        cfg = {
            "action": "insert_generic_action",
            "type": "custom",
            "label": "Select Cell Border Style",
            "layout": "horizontal",
            "options": self.get_border_styles(),
        }
        self.cell_border_style_top_select = NchantdComboBox(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_style_top_select, cnt, 1)
        cfg = {
            "action": "set_text_font_color",
            "type": "custom",
        }
        self.cell_border_thickness_top_spin = NchantdSpinBox(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_thickness_top_spin, cnt, 2)
        cfg = {
            "action": "set_text_font_color",
            "type": "custom",
            "layout": "horizontal",
        }
        self.cell_border_color_top_select = NchantdButton(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_color_top_select, cnt, 3)
        cnt += 1
        self.layout.addWidget(NchantdLabel(self, {"text": "Left"}).initWidget(), cnt, 0)
        cfg = {
            "label": "",
            "action": "insert_generic_action",
            "type": "custom",
            "options": self.get_border_styles(),
        }
        self.cell_border_style_left_select = NchantdComboBox(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_style_left_select, cnt, 1)
        cfg = {
            "action": "set_text_font_color",
            "type": "custom",
        }
        self.cell_border_thickness_left_spin = NchantdSpinBox(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_thickness_left_spin, cnt, 2)
        cfg = {
            "action": "set_text_font_color",
            "type": "custom",
        }
        self.cell_border_color_left_select = NchantdButton(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_color_left_select, cnt, 3)
        cnt += 1
        self.layout.addWidget(NchantdLabel(self, {"text": "Right"}).initWidget(), cnt, 0)
        cfg = {
            "label": "",
            "action": "insert_generic_action",
            "type": "custom",
            "options": self.get_border_styles(),
        }
        self.cell_border_style_right_select = NchantdComboBox(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_style_right_select, cnt, 1)
        cfg = {
            "action": "set_text_font_color",
            "type": "custom",
        }
        self.cell_border_thickness_right_spin = NchantdSpinBox(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_thickness_right_spin, cnt, 2)
        cfg = {
            "action": "set_text_font_color",
            "type": "custom",
        }
        self.cell_border_color_right_select = NchantdButton(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_color_right_select, cnt, 3)
        cnt += 1
        self.layout.addWidget(NchantdLabel(self, {"text": "Bottom"}).initWidget(), cnt, 0)
        cfg = {
            "label": "",
            "action": "insert_generic_action",
            "type": "custom",
            "options": self.get_border_styles(),
        }
        self.cell_border_style_bottom_select = NchantdComboBox(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_style_bottom_select, cnt, 1)
        cfg = {
            "action": "set_text_font_color",
            "type": "custom",
        }
        self.cell_border_thickness_bottom_spin = NchantdSpinBox(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_thickness_bottom_spin, cnt, 2)
        cfg = {
            "action": "set_text_font_color",
            "type": "custom",
        }
        self.cell_border_color_bottom_select = NchantdButton(self, cfg).initWidget()
        self.layout.addWidget(self.cell_border_color_bottom_select, cnt, 3)
        self.layout.setSpacing(3)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignCenter)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_border_styles(self):
        """"""
        options = ["Solid", "Dashed", "Dotted", "Double"]
        return options


class NchantdOfficeMatrix(NchantdOfficeDocument):
    """"""

    VERSION = "0.0.1.0.0.0"

    # Signals
    dataChanged = pyqt.Signal(dict)
    cellSelected = pyqt.Signal(str, object)

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Nchantd Matrix", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeMatrix"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.document = None
        self.table = None
        self.toolbar = None
        self.button_bar = None
        self.formula_bar = None
        self.formula_button_bar = None
        self.model = None
        self.datao = None
        self.num_rows = 0
        self.num_cols = 0
        self.cfg = cfg or {}
        self.parent_window = parent
        self.app = pyqt.QApplication.instance()

        # Spreadsheet state
        self.current_sheet = None
        self.selected_range = None
        self.clipboard = None
        self.is_workbook = self.cfg.get("is_workbook", False)

        # UI Components
        self.table = None
        self.toolbar = None
        self.formula_bar = None
        self.sheet_tabs = None

        self.setup_ui()
        self.setup_toolbar()
        self.connect_signals()

    def initModel(self):
        """"""
        super().initModel()
        cfg = {"file_path": self.file_path}
        # self.document = PyfficeMatrix(cfg)
        self.document = self.app.model.codex.init_matrix(cfg)
        self.document.load_document()
        self.context_menu.get_menu("context.document.matrix")
        # write document data to database if it is not already stored there
        # this logic seems like it should be in the same place as the tab creator but then
        # how does that work with the single document apps
        return self

    def initView(self, cfg=None):
        """"""
        cfg = {
            "icon": "function-3-svgrepo-com",
            "size": [40, 40],
            "entrybox": {"text": "=", "size": [600, 30]},
            "justify": "left",
            "layout": "horizontal",
        }
        self.formula_bar = NchantdLabeledEntry(self, cfg)
        if self.file_path is None or not exists(self.file_path):
            cfg = {"buttons": {49: "_insert_stretch"}, "layout": "vertical"}
        cfg["buttons"][0] = {"name": "formula_bar", "type": "entry_editor", "widget": self.formula_bar}
        dscfg = {
            "label": "Select Data Set: ",
            "layout": "horizontal",
            "size": ["auto", 30],
            "options": self.get_datasets(),
        }
        self.dataset_select = NchantdDropDown(self.parent, dscfg)
        cfg["buttons"][1] = {"action": "select_data_set", "widget": self.dataset_select}
        if self.document.is_saved:  # is_data_set
            cfg["buttons"][200] = {"action": "show_data_set"}
        super().initView(cfg)
        cfg = {"num_rows": 100, "num_columns": 40, "min_column_width": 30}
        self.table = NchantdTable(self.parent, self.config.override(cfg)).initWidget()
        self.layout.addWidget(self.table, stretch=1)
        self.layout.setSpacing(3)
        self.layout.setContentsMargins(0, 0, 0, 0)
        return self

    def initWidget(self, pos=0):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_auto_calculate(self, event, *args, **kwargs):
        """Enable or disable automatic formula calculation"""
        if hasattr(self, "autocalculate_checkbox"):
            auto_calc = self.autocalculate_checkbox.isChecked()
            if self.document:
                self.document.set_auto_calculate(auto_calc)
                if auto_calc:
                    self.recalculate_all_formulas()
        return self

    def cmd_cell_background_color_select(self, event, *args, **kwargs):
        """Select background color for selected cells"""
        cfg = {"callback": self.apply_cell_background_color}
        self.color_select_sigil = NchantdColorSelectSigil(self, cfg).initWidget()
        return self

    def cmd_compatibility_select(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_font_style_select(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_formula_entry(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_font_color_select(self, event, *args, **kwargs):
        """Select font color for selected cells"""
        cfg = {"callback": self.apply_font_color}
        self.color_select_sigil = NchantdColorSelectSigil(self, cfg).initWidget()
        return self

    def cmd_row_spinbox(self, event, *args, **kwargs):
        """Handle row count change"""
        if hasattr(self, "rows_count_entry"):
            new_row_count = self.rows_count_entry.value()
            if self.table:
                self.table.setRowCount(new_row_count)
                self.num_rows = new_row_count
        return self

    def cmd_row_height_spinbox(self, event, *args, **kwargs):
        """Handle row height change"""
        if hasattr(self, "row_height_spin"):
            new_height = self.row_height_spin.value()
            if self.table:
                selected_rows = self.get_selected_rows()
                if selected_rows:
                    for row in selected_rows:
                        self.table.setRowHeight(row, new_height)
                else:
                    # Apply to all rows
                    for row in range(self.table.rowCount()):
                        self.table.setRowHeight(row, new_height)
        return self

    def cmd_column_spinbox(self, event, *args, **kwargs):
        """Handle column count change"""
        if hasattr(self, "columns_count_entry"):
            new_col_count = self.columns_count_entry.value()
            if self.table:
                self.table.setColumnCount(new_col_count)
                self.num_cols = new_col_count
        return self

    def cmd_column_width_spinbox(self, event, *args, **kwargs):
        """Handle column width change"""
        if hasattr(self, "cell_width"):
            new_width = self.cell_width.value()
            if self.table:
                selected_cols = self.get_selected_columns()
                if selected_cols:
                    for col in selected_cols:
                        self.table.setColumnWidth(col, new_width)
                else:
                    # Apply to all columns
                    for col in range(self.table.columnCount()):
                        self.table.setColumnWidth(col, new_width)
        return self

    def cmd_formula_entrybox(self, event, *args, **kwargs):
        """Handle formula entry"""
        if hasattr(self, "formula_bar"):
            formula_text = self.formula_bar.get_text()
            selected_cell = self.table.currentItem()
            if selected_cell and formula_text:
                # Set formula to selected cell
                selected_cell.setText(formula_text)
                # Evaluate if auto-calculate is enabled
                if hasattr(self, "autocalculate_checkbox") and self.autocalculate_checkbox.isChecked():
                    self.evaluate_cell_formula(selected_cell)
        return self

    def cmd_merge_cells(self, event, *args, **kwargs):
        """Merge selected cells"""
        if self.table:
            selected_ranges = self.table.selectedRanges()
            if selected_ranges:
                for cell_range in selected_ranges:
                    top_row = cell_range.topRow()
                    left_col = cell_range.leftColumn()
                    row_count = cell_range.rowCount()
                    col_count = cell_range.columnCount()
                    self.table.setSpan(top_row, left_col, row_count, col_count)
        return self

    def cmd_data_source_select(self, event, *args, **kwargs):
        """Handle data source selection"""
        if hasattr(self, "dataset_select"):
            dataset_name = self.dataset_select.currentText()
            if dataset_name and dataset_name != "No Data Set Selected":
                # Load data from selected dataset
                self.load_dataset(dataset_name)
        return self

    def cmd_data_filters_select(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_on_click_default_cell_background_color_button(self, event, *args, **kwargs):
        """Set default background color for all cells"""
        cfg = {"callback": self.apply_default_background_color}
        self.color_select_sigil = NchantdColorSelectSigil(self, cfg).initWidget()
        return self

    def cmd_open_local_file(self, event=None, *args, **kwargs):
        """"""
        super().cmd_open_local_file(event, *args, **kwargs)
        if self.local_file is not None:
            if exists(self.local_file):
                cfg = {"file_path": self.local_file}
                self.document = PyfficeMatrix(cfg)
                self.document.open_file()
            self.populate_document()
        else:
            if debug:
                raise Exception(f"local_file is None: {self.local_file}")
        return self

    def cmd_run_eda(self):
        """"""
        return self

    def cmd_template_select(self, event, *args, **kwargs):
        """"""
        return self

    def get_datasets(self):
        """"""
        datasets = ["No Data Set Selected"]
        return datasets

    def get_formulas(self):
        """"""
        formulas = PyfficeFormulasLibrary().get_formulas_list()
        return formulas

    def init_drawer_document_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        options = [".xlsx - Excel", ".ods - OpenOffice", ".csv - Comma-Separated Values", ".tsv - Tab-Separated Values"]
        cfg = {
            "label": "Compatability",
            "layout": "horizontal",
            "options": options,
            "handler": self.cmd_compatibility_select,
        }
        self.document_compatability = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.document_compatability
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        options = ["Blank", "Loan Calculator"]
        cfg = {
            "label": "Template",
            "layout": "horizontal",
            "options": options,
            "handler": self.cmd_template_select,
        }
        self.document_template = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.document_template
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Font",
            "layout": "horizontal",
            "range": [1, 100],
            "default": 12,
        }
        self.font_config_bar = NchantdFontConfigBar(self, cfg)
        items[cnt]["widget"] = self.font_config_bar
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "text": "Set Cell Background Color",
            "layout": "horizontal",
            "default": self.config.dikt.get("num_rows", 20),
            "handler": self.cmd_on_click_default_cell_background_color_button,
        }
        self.cell_default_background_color_button = NchantdButton(self, cfg)
        items[cnt]["widget"] = self.cell_default_background_color_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Row Count",
            "layout": "horizontal",
            "range": [1, 10000000],
            "default": self.config.dikt.get("num_rows", 20),
            "handler": self.cmd_row_spinbox,
        }
        self.rows_count_entry = NchantdLabeledSpinBox(self, cfg)
        items[cnt]["widget"] = self.rows_count_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Row Height",
            "layout": "horizontal",
            "range": [1, 10000000],
            "default": self.config.dikt.get("num_rows", 20),
            "handler": self.cmd_row_spinbox,
        }
        self.rows_count_entry = NchantdLabeledSpinBox(self, cfg)
        items[cnt]["widget"] = self.rows_count_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Column Count",
            "layout": "horizontal",
            "range": [1, 10000000],
            "default": self.config.dikt.get("num_columns", 20),
            "handler": self.cmd_column_spinbox,
        }
        self.columns_count_entry = NchantdLabeledSpinBox(self, cfg)
        items[cnt]["widget"] = self.columns_count_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Column Width",
            "layout": "horizontal",
            "range": [10, 600],
            "default": self.config.dikt.get("min_column_width", 30),
            "handler": self.cmd_column_width_spinbox,
        }
        self.cell_width = NchantdLabeledSpinBox(self, cfg)
        items[cnt]["widget"] = self.cell_width
        cnt += 1
        return items

    def init_drawer_formula(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Fx",
            "layout": "horizontal",
            "size": ["auto", 350],
            "justify": "top",
        }
        self.formula = NchantdEntryBox(self, cfg)
        items[cnt]["widget"] = self.formula
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {"text": "Set Formulas to Auto-Calculate", "size": ["auto", "auto"]}
        self.autocalculate_checkbox = NchantdCheckbox(self, cfg)
        items[cnt]["widget"] = self.autocalculate_checkbox
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Select Formula: ",
            "layout": "horizontal",
            "options": self.get_formulas(),
        }
        self.formula_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.formula_select
        cnt += 1
        return items

    def init_drawer_cell_config(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Active Cell: ",
            "layout": "horizontal",
        }  # TODO readonly and fill in data
        self.selected_cell_entry = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.selected_cell_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "text": "Merge Cells: ",
            "layout": "horizontal",
            "handler": self.cmd_merge_cells,
        }  #
        self.selected_cell_merge_button = NchantdButton(self, cfg)
        items[cnt]["widget"] = self.selected_cell_merge_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Selected Text: ",
            "layout": "horizontal",
        }  # TODO readonly and fill in data
        self.selected_cell_text_entry = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.selected_cell_text_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Font",
            "layout": "horizontal",
            "range": [1, 100],
            "default": 12,
        }
        self.font_config_bar = NchantdFontConfigBar(self, cfg)
        items[cnt]["widget"] = self.font_config_bar
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "text": "Set Cell Background Color",
            "layout": "horizontal",
            "handler": self.cmd_font_color_select,
        }
        self.cell_background_color_button = NchantdButton(self, cfg)
        items[cnt]["widget"] = self.cell_background_color_button
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {"label": "Border Format"}
        self.cell_format = NchantdOfficeCellBorderFormats(self, cfg)
        items[cnt]["widget"] = self.cell_format
        cnt += 1
        # TODO show a thumbail of the object
        return items

    def init_drawer_quickstart(self):
        """"""
        items = self.toolbox_config[500].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Quickstart List",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.document_compatability = NchantdCheckbox(self, cfg)
        items[cnt]["widget"] = self.document_compatability
        cnt += 1

        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_formula()
        self.toolbox_config[300]["items"] = self.init_drawer_cell_config()
        self.toolbox_config[500]["items"] = self.init_drawer_quickstart()

    def move_cell(self, addrow, addcol):
        """Move the active cell within the worksheet"""
        if self.table:
            current_item = self.table.currentItem()
            if current_item:
                current_row = current_item.row()
                current_col = current_item.column()

                # Calculate target position with wrapping
                target_row = (current_row + addrow) % self.table.rowCount()
                target_col = (current_col + addcol) % self.table.columnCount()

                # Set the new current cell
                target_item = self.table.item(target_row, target_col)
                if not target_item:
                    target_item = pyqt.QTableWidgetItem()
                    self.table.setItem(target_row, target_col, target_item)
                self.table.setCurrentItem(target_item)
        return self

    def populate_document(self):
        """"""
        logma.info(f"Populate worksheet {self.document.data}")
        logma.info(f"Populate worksheet {type(self.document.data)}")
        self.table.update_data(self.document.data)

    def set_table(self):
        """Turn the spreadsheet into a table where there is a corresponding database table for it"""
        if self.document and self.table:
            # Extract table data
            table_data = self.extract_table_data()
            # Store in database
            if self.app and hasattr(self.app, "model"):
                self.app.model.codex.store_matrix_data(self.file_path, table_data)
        return self

    # ========== Cell Manipulation Methods ==========

    def copy_cells(self):
        """Copy selected cells to clipboard"""
        if self.table:
            selected_ranges = self.table.selectedRanges()
            if selected_ranges:
                clipboard_data = []
                for cell_range in selected_ranges:
                    for row in range(cell_range.topRow(), cell_range.bottomRow() + 1):
                        row_data = []
                        for col in range(cell_range.leftColumn(), cell_range.rightColumn() + 1):
                            item = self.table.item(row, col)
                            row_data.append(item.text() if item else "")
                        clipboard_data.append("\t".join(row_data))
                pyqt.QApplication.clipboard().setText("\n".join(clipboard_data))
        return self

    def cut_cells(self):
        """Cut selected cells to clipboard"""
        self.copy_cells()
        if self.table:
            selected_ranges = self.table.selectedRanges()
            if selected_ranges:
                for cell_range in selected_ranges:
                    for row in range(cell_range.topRow(), cell_range.bottomRow() + 1):
                        for col in range(cell_range.leftColumn(), cell_range.rightColumn() + 1):
                            item = self.table.item(row, col)
                            if item:
                                item.setText("")
        return self

    def paste_cells(self):
        """Paste cells from clipboard"""
        if self.table:
            clipboard_text = pyqt.QApplication.clipboard().text()
            if clipboard_text:
                current_item = self.table.currentItem()
                if current_item:
                    start_row = current_item.row()
                    start_col = current_item.column()
                    rows = clipboard_text.split("\n")
                    for r_idx, row_text in enumerate(rows):
                        cols = row_text.split("\t")
                        for c_idx, cell_text in enumerate(cols):
                            target_row = start_row + r_idx
                            target_col = start_col + c_idx
                            if target_row < self.table.rowCount() and target_col < self.table.columnCount():
                                item = self.table.item(target_row, target_col)
                                if not item:
                                    item = pyqt.QTableWidgetItem()
                                    self.table.setItem(target_row, target_col, item)
                                item.setText(cell_text)
        return self

    def delete_cells(self):
        """Delete content of selected cells"""
        if self.table:
            selected_ranges = self.table.selectedRanges()
            if selected_ranges:
                for cell_range in selected_ranges:
                    for row in range(cell_range.topRow(), cell_range.bottomRow() + 1):
                        for col in range(cell_range.leftColumn(), cell_range.rightColumn() + 1):
                            item = self.table.item(row, col)
                            if item:
                                item.setText("")
        return self

    # ========== Helper Methods ==========

    def get_selected_rows(self):
        """Get list of selected row indices"""
        if self.table:
            selected_ranges = self.table.selectedRanges()
            rows = set()
            for cell_range in selected_ranges:
                for row in range(cell_range.topRow(), cell_range.bottomRow() + 1):
                    rows.add(row)
            return sorted(list(rows))
        return []

    def get_selected_columns(self):
        """Get list of selected column indices"""
        if self.table:
            selected_ranges = self.table.selectedRanges()
            cols = set()
            for cell_range in selected_ranges:
                for col in range(cell_range.leftColumn(), cell_range.rightColumn() + 1):
                    cols.add(col)
            return sorted(list(cols))
        return []

    def extract_table_data(self):
        """Extract all data from table"""
        data = []
        if self.table:
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
        return data

    # ========== Formatting Methods ==========

    def apply_cell_background_color(self, color):
        """Apply background color to selected cells"""
        if self.table and color:
            selected_ranges = self.table.selectedRanges()
            if selected_ranges:
                for cell_range in selected_ranges:
                    for row in range(cell_range.topRow(), cell_range.bottomRow() + 1):
                        for col in range(cell_range.leftColumn(), cell_range.rightColumn() + 1):
                            item = self.table.item(row, col)
                            if not item:
                                item = pyqt.QTableWidgetItem()
                                self.table.setItem(row, col, item)
                            item.setBackground(pyqt.QColor(color))
        return self

    def apply_font_color(self, color):
        """Apply font color to selected cells"""
        if self.table and color:
            selected_ranges = self.table.selectedRanges()
            if selected_ranges:
                for cell_range in selected_ranges:
                    for row in range(cell_range.topRow(), cell_range.bottomRow() + 1):
                        for col in range(cell_range.leftColumn(), cell_range.rightColumn() + 1):
                            item = self.table.item(row, col)
                            if not item:
                                item = pyqt.QTableWidgetItem()
                                self.table.setItem(row, col, item)
                            item.setForeground(pyqt.QColor(color))
        return self

    def apply_default_background_color(self, color):
        """Apply background color to all cells"""
        if self.table and color:
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if not item:
                        item = pyqt.QTableWidgetItem()
                        self.table.setItem(row, col, item)
                    item.setBackground(pyqt.QColor(color))
        return self

    def apply_font_style(self, font_family=None, font_size=None, bold=None, italic=None, underline=None):
        """Apply font styling to selected cells"""
        if self.table:
            selected_ranges = self.table.selectedRanges()
            if selected_ranges:
                for cell_range in selected_ranges:
                    for row in range(cell_range.topRow(), cell_range.bottomRow() + 1):
                        for col in range(cell_range.leftColumn(), cell_range.rightColumn() + 1):
                            item = self.table.item(row, col)
                            if not item:
                                item = pyqt.QTableWidgetItem()
                                self.table.setItem(row, col, item)
                            font = item.font()
                            if font_family:
                                font.setFamily(font_family)
                            if font_size:
                                font.setPointSize(font_size)
                            if bold is not None:
                                font.setBold(bold)
                            if italic is not None:
                                font.setItalic(italic)
                            if underline is not None:
                                font.setUnderline(underline)
                            item.setFont(font)
        return self

    def apply_cell_border(self, side, style, thickness, color):
        """Apply border to selected cells

        Args:
            side: 'top', 'left', 'right', 'bottom', or 'all'
            style: 'solid', 'dashed', 'dotted', 'double'
            thickness: border thickness in pixels
            color: border color
        """
        # Note: PyQt QTableWidget doesn't have built-in per-cell borders
        # This would require custom item delegates or stylesheets
        # Placeholder for future implementation
        logma.info(f"Apply border: {side} {style} {thickness} {color}")
        return self

    # ========== Row/Column Operations ==========

    def insert_row(self, position=None):
        """Insert a new row at the specified position or at current selection"""
        if self.table:
            if position is None:
                current_item = self.table.currentItem()
                position = current_item.row() if current_item else 0
            self.table.insertRow(position)
            self.num_rows = self.table.rowCount()
        return self

    def insert_rows(self, count, position=None):
        """Insert multiple rows at the specified position"""
        for i in range(count):
            self.insert_row(position)
        return self

    def delete_row(self, row_index=None):
        """Delete a row at the specified index or current selection"""
        if self.table:
            if row_index is None:
                current_item = self.table.currentItem()
                row_index = current_item.row() if current_item else 0
            self.table.removeRow(row_index)
            self.num_rows = self.table.rowCount()
        return self

    def delete_selected_rows(self):
        """Delete all selected rows"""
        if self.table:
            selected_rows = self.get_selected_rows()
            # Delete in reverse order to avoid index shifting
            for row in reversed(selected_rows):
                self.table.removeRow(row)
            self.num_rows = self.table.rowCount()
        return self

    def insert_column(self, position=None):
        """Insert a new column at the specified position or at current selection"""
        if self.table:
            if position is None:
                current_item = self.table.currentItem()
                position = current_item.column() if current_item else 0
            self.table.insertColumn(position)
            self.num_cols = self.table.columnCount()
        return self

    def insert_columns(self, count, position=None):
        """Insert multiple columns at the specified position"""
        for i in range(count):
            self.insert_column(position)
        return self

    def delete_column(self, col_index=None):
        """Delete a column at the specified index or current selection"""
        if self.table:
            if col_index is None:
                current_item = self.table.currentItem()
                col_index = current_item.column() if current_item else 0
            self.table.removeColumn(col_index)
            self.num_cols = self.table.columnCount()
        return self

    def delete_selected_columns(self):
        """Delete all selected columns"""
        if self.table:
            selected_cols = self.get_selected_columns()
            # Delete in reverse order to avoid index shifting
            for col in reversed(selected_cols):
                self.table.removeColumn(col)
            self.num_cols = self.table.columnCount()
        return self

    def resize_row(self, row_index, height):
        """Resize a specific row to the given height"""
        if self.table and 0 <= row_index < self.table.rowCount():
            self.table.setRowHeight(row_index, height)
        return self

    def resize_column(self, col_index, width):
        """Resize a specific column to the given width"""
        if self.table and 0 <= col_index < self.table.columnCount():
            self.table.setColumnWidth(col_index, width)
        return self

    def auto_resize_columns(self):
        """Auto-resize all columns to fit content"""
        if self.table:
            for col in range(self.table.columnCount()):
                self.table.resizeColumnToContents(col)
        return self

    def auto_resize_rows(self):
        """Auto-resize all rows to fit content"""
        if self.table:
            for row in range(self.table.rowCount()):
                self.table.resizeRowToContents(row)
        return self

    # ========== Formula Evaluation and Calculation ==========

    def evaluate_cell_formula(self, cell_item):
        """Evaluate formula in a cell and update its display value"""
        if not cell_item:
            return self

        cell_text = cell_item.text()
        if cell_text.startswith("="):
            try:
                # Get the formula (without the = sign)
                formula = cell_text[1:]
                # Evaluate the formula
                result = self.calculate_formula(formula)
                # Store the result (keep original formula in data)
                cell_item.setData(pyqt.Qt.ItemDataRole.DisplayRole, str(result))
                cell_item.setData(pyqt.Qt.ItemDataRole.UserRole, cell_text)  # Store original formula
            except Exception as e:
                logma.error(f"Formula evaluation error: {e}")
                cell_item.setData(pyqt.Qt.ItemDataRole.DisplayRole, f"#ERROR: {e}")
        return self

    def calculate_formula(self, formula):
        """Calculate the result of a formula string

        Supports:
        - Basic arithmetic: +, -, *, /
        - Cell references: A1, B2, etc.
        - Functions: SUM, AVG, MIN, MAX, COUNT
        """
        # Replace cell references with their values
        formula = self.replace_cell_references(formula)

        # Handle common spreadsheet functions
        formula = self.replace_spreadsheet_functions(formula)

        # Evaluate the expression
        try:
            # Use safe evaluation (limited to mathematical operations)
            result = eval(
                formula,
                {"__builtins__": {}},
                {"abs": abs, "min": min, "max": max, "sum": sum, "round": round, "pow": pow, "len": len},
            )
            return result
        except Exception as e:
            raise ValueError(f"Invalid formula: {e}")

    def replace_cell_references(self, formula):
        """Replace cell references (like A1, B2) with their actual values"""
        import re

        # Match cell references like A1, AB12, etc.
        pattern = r"\b([A-Z]+)(\d+)\b"

        def replace_ref(match):
            col_letter = match.group(1)
            row_num = int(match.group(2)) - 1  # Convert to 0-based index
            col_num = self.column_letter_to_index(col_letter)

            if self.table and 0 <= row_num < self.table.rowCount() and 0 <= col_num < self.table.columnCount():
                item = self.table.item(row_num, col_num)
                if item:
                    value = item.text()
                    # If the cell contains a number, return it; otherwise return 0
                    try:
                        return str(float(value))
                    except ValueError:
                        return "0"
            return "0"

        return re.sub(pattern, replace_ref, formula)

    def replace_spreadsheet_functions(self, formula):
        """Replace spreadsheet functions with Python equivalents"""
        import re

        # SUM(A1:A10) -> sum([...])
        def replace_sum(match):
            range_str = match.group(1)
            values = self.get_range_values(range_str)
            return f"sum([{','.join(map(str, values))}])"

        # AVG(A1:A10) -> sum([...])/len([...])
        def replace_avg(match):
            range_str = match.group(1)
            values = self.get_range_values(range_str)
            values_str = ",".join(map(str, values))
            return f"(sum([{values_str}])/len([{values_str}]) if len([{values_str}]) > 0 else 0)"

        # COUNT(A1:A10) -> len([...])
        def replace_count(match):
            range_str = match.group(1)
            values = self.get_range_values(range_str)
            return f"len([{','.join(map(str, values))}])"

        # MIN(A1:A10) -> min([...])
        def replace_min(match):
            range_str = match.group(1)
            values = self.get_range_values(range_str)
            return f"min([{','.join(map(str, values))}])"

        # MAX(A1:A10) -> max([...])
        def replace_max(match):
            range_str = match.group(1)
            values = self.get_range_values(range_str)
            return f"max([{','.join(map(str, values))}])"

        formula = re.sub(r"SUM\(([^)]+)\)", replace_sum, formula, flags=re.IGNORECASE)
        formula = re.sub(r"AVG\(([^)]+)\)", replace_avg, formula, flags=re.IGNORECASE)
        formula = re.sub(r"COUNT\(([^)]+)\)", replace_count, formula, flags=re.IGNORECASE)
        formula = re.sub(r"MIN\(([^)]+)\)", replace_min, formula, flags=re.IGNORECASE)
        formula = re.sub(r"MAX\(([^)]+)\)", replace_max, formula, flags=re.IGNORECASE)

        return formula

    def get_range_values(self, range_str):
        """Get values from a cell range like 'A1:A10'"""
        parts = range_str.split(":")
        if len(parts) != 2:
            return []

        # Parse start and end cells
        import re

        start_match = re.match(r"([A-Z]+)(\d+)", parts[0].strip())
        end_match = re.match(r"([A-Z]+)(\d+)", parts[1].strip())

        if not start_match or not end_match:
            return []

        start_col = self.column_letter_to_index(start_match.group(1))
        start_row = int(start_match.group(2)) - 1
        end_col = self.column_letter_to_index(end_match.group(1))
        end_row = int(end_match.group(2)) - 1

        values = []
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                if self.table and 0 <= row < self.table.rowCount() and 0 <= col < self.table.columnCount():
                    item = self.table.item(row, col)
                    if item:
                        try:
                            values.append(float(item.text()))
                        except ValueError:
                            pass  # Skip non-numeric values
        return values

    def column_letter_to_index(self, letter):
        """Convert column letter (A, B, AA, etc.) to 0-based index"""
        index = 0
        for char in letter:
            index = index * 26 + (ord(char.upper()) - ord("A") + 1)
        return index - 1

    def column_index_to_letter(self, index):
        """Convert 0-based column index to letter (A, B, AA, etc.)"""
        letter = ""
        index += 1  # Convert to 1-based
        while index > 0:
            index -= 1
            letter = chr(ord("A") + index % 26) + letter
            index //= 26
        return letter

    def recalculate_all_formulas(self):
        """Recalculate all formulas in the spreadsheet"""
        if self.table:
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and item.text().startswith("="):
                        self.evaluate_cell_formula(item)
        return self

    def load_dataset(self, dataset_name):
        """Load data from a named dataset into the table"""
        if self.app and hasattr(self.app, "model"):
            try:
                dataset = self.app.model.codex.get_dataset(dataset_name)
                if dataset and self.table:
                    # Clear existing data
                    self.table.clearContents()
                    # Load new data
                    if hasattr(dataset, "values"):
                        data = dataset.values
                    else:
                        data = dataset

                    for row_idx, row_data in enumerate(data):
                        if row_idx >= self.table.rowCount():
                            self.table.setRowCount(row_idx + 1)
                        for col_idx, cell_value in enumerate(row_data):
                            if col_idx >= self.table.columnCount():
                                self.table.setColumnCount(col_idx + 1)
                            item = pyqt.QTableWidgetItem(str(cell_value))
                            self.table.setItem(row_idx, col_idx, item)
            except Exception as e:
                logma.error(f"Error loading dataset {dataset_name}: {e}")
        return self

    # ========== Save and Export Methods ==========

    def save_document(self, file_path=None):
        """Save the current spreadsheet to a file"""
        if file_path is None:
            file_path = self.file_path

        if file_path is None:
            logma.warning("No file path specified for saving")
            return self

        # Determine file format from extension
        file_ext = file_path.split(".")[-1].lower()

        if file_ext in ["xlsx", "xls"]:
            self.save_as_excel(file_path)
        elif file_ext == "ods":
            self.save_as_ods(file_path)
        elif file_ext == "csv":
            self.save_as_csv(file_path)
        elif file_ext == "tsv":
            self.save_as_tsv(file_path)
        else:
            logma.warning(f"Unsupported file format: {file_ext}")

        return self

    def save_as_excel(self, file_path):
        """Save as Excel file (.xlsx)"""
        try:
            if self.document:
                # Update document data from table
                self.document.data = self.extract_table_data()
                # Save using PyfficeMatrix
                self.document.file_path = file_path
                self.document.save_file()
            else:
                # Fallback: save using basic method
                import openpyxl

                wb = openpyxl.Workbook()
                ws = wb.active
                data = self.extract_table_data()
                for row_idx, row_data in enumerate(data, start=1):
                    for col_idx, cell_value in enumerate(row_data, start=1):
                        ws.cell(row=row_idx, column=col_idx, value=cell_value)
                wb.save(file_path)
            logma.info(f"Saved Excel file: {file_path}")
        except Exception as e:
            logma.error(f"Error saving Excel file: {e}")
        return self

    def save_as_ods(self, file_path):
        """Save as OpenDocument Spreadsheet (.ods)"""
        try:
            if self.document:
                # Update document data from table
                self.document.data = self.extract_table_data()
                # Save using PyfficeMatrix
                self.document.file_path = file_path
                self.document.save_as_ods()
            else:
                logma.warning("ODS export requires PyfficeMatrix document")
        except Exception as e:
            logma.error(f"Error saving ODS file: {e}")
        return self

    def save_as_csv(self, file_path, delimiter=","):
        """Save as CSV file"""
        try:
            import csv

            data = self.extract_table_data()
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerows(data)
            logma.info(f"Saved CSV file: {file_path}")
        except Exception as e:
            logma.error(f"Error saving CSV file: {e}")
        return self

    def save_as_tsv(self, file_path):
        """Save as TSV (Tab-Separated Values) file"""
        return self.save_as_csv(file_path, delimiter="\t")

    def export_to_format(self, format_type, file_path=None):
        """Export spreadsheet to specified format

        Args:
            format_type: 'xlsx', 'ods', 'csv', 'tsv'
            file_path: optional file path, otherwise uses current path with new extension
        """
        if file_path is None and self.file_path:
            # Change extension of current file path
            base_path = ".".join(self.file_path.split(".")[:-1])
            file_path = f"{base_path}.{format_type}"

        if file_path:
            self.save_document(file_path)
        return self

    def auto_save(self):
        """Auto-save the current document"""
        if self.file_path and exists(dirname(self.file_path)):
            self.save_document()
        return self

    def setup_ui(self):
        """Initialize the user interface"""
        main_layout = pyqt.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sheet tabs (for workbook mode)
        if self.is_workbook:
            self.sheet_tabs = pyqt.QTabWidget()
            self.sheet_tabs.setTabsClosable(False)
            main_layout.addWidget(self.sheet_tabs)

        # Formula bar
        self.formula_bar = self.create_formula_bar()
        main_layout.addWidget(self.formula_bar)

        # Table widget
        self.table = pyqt.QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(pyqt.QTableWidget.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(pyqt.QTableWidget.SelectionMode.ExtendedSelection)

        # Configure headers
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(pyqt.QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

        # Set default size
        self.table.setRowCount(100)
        self.table.setColumnCount(26)  # A-Z

        # Add column headers (A-Z)
        for i in range(26):
            self.table.setHorizontalHeaderItem(i, pyqt.QTableWidgetItem(chr(65 + i)))

        # Add row headers (1-100)
        for i in range(100):
            self.table.setVerticalHeaderItem(i, pyqt.QTableWidgetItem(str(i + 1)))

        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

    def create_formula_bar(self):
        """Create the formula bar widget"""
        bar = pyqt.QWidget()
        layout = pyqt.QHBoxLayout(bar)
        layout.setContentsMargins(5, 5, 5, 5)

        # Cell reference label
        self.cell_ref_label = pyqt.QLabel("A1")
        self.cell_ref_label.setMinimumWidth(60)
        layout.addWidget(pyqt.QLabel("Cell:"))
        layout.addWidget(self.cell_ref_label)

        # Function button
        self.func_button = pyqt.QPushButton("fx")
        self.func_button.setMaximumWidth(30)
        self.func_button.clicked.connect(self.show_function_dialog)
        layout.addWidget(self.func_button)

        # Formula input
        self.formula_input = pyqt.QLineEdit()
        self.formula_input.setPlaceholderText("Enter value or formula (e.g., =SUM(A1:A10))")
        self.formula_input.returnPressed.connect(self.on_formula_entered)
        layout.addWidget(self.formula_input)

        layout.addStretch()
        return bar

    def setup_toolbar(self):
        """Create the toolbar"""
        self.toolbar = pyqt.QToolBar("Spreadsheet Tools")

        # File operations
        self.toolbar.addAction("New", self.new_sheet)
        self.toolbar.addAction("Open", self.open_file)
        self.toolbar.addAction("Save", self.save_file)
        self.toolbar.addSeparator()

        # Edit operations
        self.toolbar.addAction("Cut", self.cut)
        self.toolbar.addAction("Copy", self.copy)
        self.toolbar.addAction("Paste", self.paste)
        self.toolbar.addSeparator()

        # Format operations
        self.toolbar.addAction("Bold", self.toggle_bold)
        self.toolbar.addAction("Italic", self.toggle_italic)
        self.toolbar.addSeparator()

        # Insert operations
        self.toolbar.addAction("Insert Row", self.insert_row)
        self.toolbar.addAction("Insert Column", self.insert_column)
        self.toolbar.addAction("Delete Row", self.delete_row)
        self.toolbar.addAction("Delete Column", self.delete_column)
        self.toolbar.addSeparator()

        # Chart insertion
        self.toolbar.addAction("Insert Chart", self.insert_chart)

    def connect_signals(self):
        """Connect UI signals to handlers"""
        self.table.itemChanged.connect(self.on_cell_changed)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

    # ================================ Data Loading ================================

    def load_from_config(self, cfg):
        """Load spreadsheet data from configuration"""
        if "data" in cfg:
            self.load_data(cfg["data"])
        if "sheets" in cfg:
            for sheet_name, sheet_data in cfg["sheets"].items():
                self.add_sheet(sheet_name, sheet_data)

    def load_data(self, data):
        """Load data into the spreadsheet"""
        if isinstance(data, dict):
            # Load from cell dictionary
            for address, value in data.items():
                self.set_cell_value(address, value)
        elif isinstance(data, list):
            # Load from list (rows)
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    address = f"{chr(65 + col_idx)}{row_idx + 1}"
                    self.set_cell_value(address, value)

    def set_cell_value(self, address, value):
        """Set value at specified cell address (e.g., 'A1')"""
        if not address or len(address) < 2:
            return

        col = ord(address[0].upper()) - 65  # A=0, B=1, etc.
        row = int(address[1:]) - 1  # 1-indexed

        if 0 <= col < self.table.columnCount() and row >= 0:
            # Ensure row exists
            while row >= self.table.rowCount():
                self.table.insertRow(self.table.rowCount())

            item = self.table.item(row, col)
            if item is None:
                item = pyqt.QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)
            else:
                item.setText(str(value))

    def get_cell_value(self, address):
        """Get value from specified cell address"""
        if not address or len(address) < 2:
            return None

        col = ord(address[0].upper()) - 65
        row = int(address[1:]) - 1

        if 0 <= col < self.table.columnCount() and 0 <= row < self.table.rowCount():
            item = self.table.item(row, col)
            return item.text() if item else ""
        return None

    def get_current_address(self):
        """Get the currently selected cell address"""
        selected = self.table.selectedIndexes()
        if selected:
            row = selected[0].row()
            col = selected[0].column()
            return f"{chr(65 + col)}{row + 1}"
        return "A1"

    def get_selection_range(self):
        """Get the selected cell range"""
        selected = self.table.selectedIndexes()
        if not selected:
            return None, None

        rows = sorted(set(index.row() for index in selected))
        cols = sorted(set(index.column() for index in selected))

        if not rows or not cols:
            return None, None

        start_cell = f"{chr(65 + cols[0])}{rows[0] + 1}"
        end_cell = f"{chr(65 + cols[-1])}{rows[-1] + 1}"

        return start_cell, end_cell

    # ================================ Event Handlers ================================

    def on_cell_changed(self, item):
        """Handle cell value change"""
        address = f"{chr(65 + item.column())}{item.row() + 1}"
        value = item.text()

        # Emit signal
        self.dataChanged.emit({"address": address, "value": value})

    def on_selection_changed(self):
        """Handle selection change"""
        address = self.get_current_address()
        value = self.get_cell_value(address)

        # Update formula bar
        self.cell_ref_label.setText(address)
        self.formula_input.setText(value or "")

        # Emit signal
        self.cellSelected.emit(address, value)

    def on_formula_entered(self):
        """Handle formula input submission"""
        address = self.get_current_address()
        formula = self.formula_input.text()

        self.set_cell_value(address, formula)

    def show_function_dialog(self):
        """Show function selection dialog"""
        # TODO: Implement function dialog
        pyqt.QMessageBox.information(self, "Functions", "Function dialog not yet implemented")

    # ================================ Toolbar Actions ================================

    def new_sheet(self):
        """Create a new spreadsheet"""
        self.table.clearContents()
        self.dataChanged.emit({"action": "new"})

    def open_file(self):
        """Open a spreadsheet file"""
        file_path, _ = pyqt.QFileDialog.getOpenFileName(
            self, "Open Spreadsheet", "", "Spreadsheet Files (*.csv *.xlsx *.xls);;All Files (*)"
        )

        if file_path:
            self.load_from_file(file_path)

    def load_from_file(self, file_path):
        """Load spreadsheet from file"""
        try:
            if file_path.endswith(".csv"):
                self.load_csv(file_path)
            elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
                self.load_excel(file_path)
            else:
                pyqt.QMessageBox.warning(self, "Error", "Unsupported file format")
        except Exception as e:
            pyqt.QMessageBox.warning(self, "Error", f"Failed to load file: {e}")

    def load_csv(self, file_path):
        """Load CSV file into spreadsheet"""
        import csv

        self.table.clearContents()
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                for col_idx, value in enumerate(row):
                    if col_idx >= self.table.columnCount():
                        self.table.insertColumn(col_idx)
                        self.table.setHorizontalHeaderItem(col_idx, pyqt.QTableWidgetItem(chr(65 + col_idx)))
                    item = pyqt.QTableWidgetItem(value)
                    self.table.setItem(row_idx, col_idx, item)

                if row_idx >= self.table.rowCount() - 1:
                    self.table.insertRow(row_idx + 1)

    def load_excel(self, file_path, sheet_name=None):
        """Load Excel file into spreadsheet with formula preservation

        Args:
            file_path: Path to the Excel file
            sheet_name: Optional specific sheet to load. If None, loads active sheet.
        """
        try:
            import openpyxl
            from openpyxl.utils import get_column_letter

            # Load workbook WITHOUT data_only to preserve formulas
            wb = openpyxl.load_workbook(file_path, data_only=False)

            # Select sheet
            if sheet_name and sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
            else:
                ws = wb.active

            self.table.clearContents()

            # Track workbook data for multi-sheet support
            self._excel_workbook = wb
            self._excel_sheets = list(wb.sheetnames)

            # Get dimensions
            max_row = ws.max_row or 100
            max_col = ws.max_column or 26

            # Ensure we have enough rows/columns
            self.table.setRowCount(max(max_row, 100))
            self.table.setColumnCount(max(max_col, 26))

            # Update column headers for columns beyond Z (AA, AB, etc.)
            for col_idx in range(26, max_col):
                self.table.setHorizontalHeaderItem(col_idx, pyqt.QTableWidgetItem(get_column_letter(col_idx + 1)))

            # Load cells with formulas preserved
            for row_idx, row in enumerate(ws.iter_rows()):
                for col_idx, cell in enumerate(row):
                    value = None

                    # Get formula or value - key for H1: preserve formulas!
                    if cell.data_type == "f":  # Formula cell
                        value = cell.value  # Returns the formula string
                    elif cell.value is not None:
                        value = cell.value

                    # Set cell value (formula or plain value)
                    if value is not None:
                        item = pyqt.QTableWidgetItem(str(value))

                        # Preserve number format
                        if cell.number_format and cell.number_format != "General":
                            item.setData(
                                pyqt.Qt.ItemDataRole.UserRole,
                                {
                                    "number_format": cell.number_format,
                                    "font_bold": cell.font.bold if cell.font else False,
                                    "font_italic": cell.font.italic if cell.font else False,
                                    "fill_color": cell.fill.fgColor.rgb if cell.fill and cell.fill.fgColor else None,
                                },
                            )

                        self.table.setItem(row_idx, col_idx, item)

                    # Preserve column widths
                    if col_idx < max_col:
                        col_dim = ws.column_dimensions.get(get_column_letter(col_idx + 1))
                        if col_dim and col_dim.width:
                            self.table.setColumnWidth(col_idx, int(col_dim.width * 7))

            # Update sheet tabs if in workbook mode
            if self.is_workbook and self.sheet_tabs:
                self._setup_sheet_tabs()

            self.current_sheet = ws.title

        except ImportError:
            pyqt.QMessageBox.warning(self, "Error", "openpyxl not installed. Please install: pip install openpyxl")
        except Exception as e:
            pyqt.QMessageBox.warning(self, "Error", f"Failed to load Excel: {e}")

    def save_file(self):
        """Save spreadsheet to file"""
        file_path, _ = pyqt.QFileDialog.getSaveFileName(
            self, "Save Spreadsheet", "", "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )

        if file_path:
            self.save_to_file(file_path)

    def save_to_file(self, file_path):
        """Save spreadsheet to file"""
        try:
            if file_path.endswith(".csv") or not file_path.endswith(".xlsx"):
                self.save_csv(file_path if file_path.endswith(".csv") else file_path + ".csv")
            elif file_path.endswith(".xlsx"):
                self.save_excel(file_path)

            pyqt.QMessageBox.information(self, "Success", f"File saved: {file_path}")
        except Exception as e:
            pyqt.QMessageBox.warning(self, "Error", f"Failed to save file: {e}")

    def save_csv(self, file_path):
        """Save spreadsheet to CSV file"""
        import csv

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for row in range(self.table.rowCount()):
                row_data = []
                has_data = False
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    value = item.text() if item else ""
                    row_data.append(value)
                    if value:
                        has_data = True
                if has_data:
                    writer.writerow(row_data)

    def save_excel(self, file_path):
        """Save spreadsheet to Excel file"""
        try:
            import openpyxl

            wb = openpyxl.Workbook()
            ws = wb.active

            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    value = item.text() if item else ""
                    if value:
                        ws.cell(row=row + 1, column=col + 1, value=value)

            wb.save(file_path)
        except ImportError:
            pyqt.QMessageBox.warning(self, "Error", "openpyxl not installed")

    # ================================ Clipboard Operations ================================

    def cut(self):
        """Cut selected cells"""
        self.copy()
        self.clear_selection()

    def copy(self):
        """Copy selected cells"""
        selected = self.table.selectedIndexes()
        if not selected:
            return

        # Get selection range
        rows = sorted(set(index.row() for index in selected))
        cols = sorted(set(index.column() for index in selected))

        # Copy to clipboard
        clipboard_data = []
        for row in rows:
            row_data = []
            for col in cols:
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            clipboard_data.append("\t".join(row_data))

        self.clipboard = "\n".join(clipboard_data)
        clipboard = pyqt.QApplication.clipboard()
        clipboard.setText(self.clipboard)

    def paste(self):
        """Paste from clipboard"""
        clipboard = pyqt.QApplication.clipboard()
        text = clipboard.text()

        if not text:
            return

        selected = self.table.selectedIndexes()
        if not selected:
            return

        start_row = selected[0].row()
        start_col = selected[0].column()

        # Parse clipboard data
        rows = text.split("\n")
        for row_idx, row_data in enumerate(rows):
            cols = row_data.split("\t")
            for col_idx, value in enumerate(cols):
                target_row = start_row + row_idx
                target_col = start_col + col_idx

                # Ensure rows exist
                while target_row >= self.table.rowCount():
                    self.table.insertRow(self.table.rowCount())

                # Ensure columns exist
                while target_col >= self.table.columnCount():
                    self.table.insertColumn(self.table.columnCount())
                    self.table.setHorizontalHeaderItem(
                        self.table.columnCount() - 1,
                        pyqt.QTableWidgetItem(self.column_index_to_letter(self.table.columnCount() - 1)),
                    )

                # Set the cell value
                item = self.table.item(target_row, target_col)
                if item is None:
                    item = pyqt.QTableWidgetItem(value)
                    self.table.setItem(target_row, target_col, item)
                else:
                    item.setText(value)

    def clear_selection(self):
        """Clear the contents of selected cells"""
        selected = self.table.selectedIndexes()
        for index in selected:
            item = self.table.item(index.row(), index.column())
            if item:
                item.setText("")

    # ================================ View / Display Toggles ================================

    def toggle_gridlines(self):
        """Toggle grid lines on/off in the spreadsheet table"""
        if self.table:
            current = self.table.showGrid()
            self.table.setShowGrid(not current)
            logma.info(f"Gridlines toggled: {not current}")
        return self

    def toggle_headers(self):
        """Toggle row/column headers on/off"""
        if self.table:
            h_header = self.table.horizontalHeader()
            v_header = self.table.verticalHeader()
            h_header.setVisible(not h_header.isVisible())
            v_header.setVisible(not v_header.isVisible())
            logma.info(
                f"Headers toggled: h={h_header.isVisible()}, v={v_header.isVisible()}"
            )
        return self

    def fullscreen_mode(self):
        """Toggle fullscreen mode for the parent window"""
        window = self.window()
        if window:
            if window.isFullScreen():
                window.showNormal()
                logma.info("Exited fullscreen mode")
            else:
                window.showFullScreen()
                logma.info("Entered fullscreen mode")
        return self

    # ================================ Find / Replace ================================

    def find_replace(self):
        """Open a find and replace dialog"""
        dialog = pyqt.QDialog(self)
        dialog.setWindowTitle("Find and Replace")
        dialog.setMinimumWidth(400)

        layout = pyqt.QFormLayout(dialog)

        find_input = pyqt.QLineEdit()
        replace_input = pyqt.QLineEdit()
        layout.addRow("Find:", find_input)
        layout.addRow("Replace with:", replace_input)

        case_check = pyqt.QCheckBox("Match case")
        layout.addRow(case_check)

        status_label = pyqt.QLabel("")
        layout.addRow(status_label)

        def do_replace_all():
            find_text = find_input.text()
            replace_text = replace_input.text()
            if not find_text:
                status_label.setText("Enter text to find.")
                return

            count = 0
            match_case = case_check.isChecked()
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        text = item.text()
                        if not match_case:
                            lower_find = find_text.lower()
                            lower_text = text.lower()
                            if lower_find in lower_text:
                                new_text = text
                                # Case-insensitive replace
                                idx = lower_text.find(lower_find)
                                while idx != -1:
                                    new_text = (
                                        new_text[:idx] + replace_text + new_text[idx + len(find_text):]
                                    )
                                    lower_text = new_text.lower()
                                    idx = lower_text.find(lower_find, idx + len(replace_text))
                                item.setText(new_text)
                                count += 1
                        else:
                            if find_text in text:
                                item.setText(text.replace(find_text, replace_text))
                                count += 1
            status_label.setText(f"Replaced in {count} cell(s).")

        def do_find_next():
            find_text = find_input.text()
            if not find_text:
                status_label.setText("Enter text to find.")
                return

            match_case = case_check.isChecked()
            current = self.table.currentItem()
            start_row = current.row() if current else 0
            start_col = (current.column() + 1) if current else 0

            total_rows = self.table.rowCount()
            total_cols = self.table.columnCount()

            for row_offset in range(total_rows):
                row = (start_row + row_offset) % total_rows
                for col_offset in range(total_cols):
                    if row_offset == 0 and col_offset < start_col:
                        continue
                    col = (start_col + col_offset) % total_cols
                    if row_offset > 0 and col == 0:
                        pass
                    item = self.table.item(row, col)
                    if item:
                        text = item.text()
                        compare_text = text if match_case else text.lower()
                        search_text = find_text if match_case else find_text.lower()
                        if search_text in compare_text:
                            self.table.setCurrentCell(row, col)
                            self.table.setFocus()
                            status_label.setText(f"Found at {self.column_index_to_letter(col)}{row + 1}")
                            return
            status_label.setText("Not found.")

        btn_layout = pyqt.QHBoxLayout()
        find_btn = pyqt.QPushButton("Find Next")
        find_btn.clicked.connect(do_find_next)
        replace_all_btn = pyqt.QPushButton("Replace All")
        replace_all_btn.clicked.connect(do_replace_all)
        close_btn = pyqt.QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)

        btn_layout.addWidget(find_btn)
        btn_layout.addWidget(replace_all_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addRow(btn_layout)

        dialog.exec()
        return self

    # ================================ Print ================================

    def print_document(self):
        """Print the spreadsheet using QPrinter"""
        try:
            printer = pyqt.QPrinter(pyqt.QPrinter.PrinterMode.HighResolution)
            print_dialog = pyqt.QPrintDialog(printer, self)

            if print_dialog.exec() == pyqt.QDialog.DialogCode.Accepted:
                # Render the table to a QTextDocument for printing
                doc = pyqt.QTextDocument()
                cursor = pyqt.QTextCursor(doc)

                cursor.insertHtml("<table border='1' cellspacing='0' cellpadding='4'>")

                # Add header row
                cursor.insertHtml("<tr>")
                cursor.insertHtml("<th></th>")
                for col in range(self.table.columnCount()):
                    header_item = self.table.horizontalHeaderItem(col)
                    header_text = header_item.text() if header_item else ""
                    cursor.insertHtml(f"<th>{header_text}</th>")
                cursor.insertHtml("</tr>")

                # Add data rows
                for row in range(self.table.rowCount()):
                    row_has_data = False
                    row_html = "<tr>"
                    # Row header
                    v_header = self.table.verticalHeaderItem(row)
                    v_header_text = v_header.text() if v_header else str(row + 1)
                    row_html += f"<td><b>{v_header_text}</b></td>"
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        cell_text = item.text() if item else ""
                        if cell_text:
                            row_has_data = True
                        # Escape HTML special chars
                        cell_text = (
                            cell_text.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;")
                        )
                        row_html += f"<td>{cell_text}</td>"
                    row_html += "</tr>"
                    if row_has_data:
                        cursor.insertHtml(row_html)

                cursor.insertHtml("</table>")
                doc.print_(printer)
                logma.info("Document sent to printer.")
        except Exception as e:
            logma.error(f"Print error: {e}")
            pyqt.QMessageBox.warning(self, "Print Error", f"Failed to print: {e}")
        return self

    # ================================ Font Toggles (Toolbar Fixes) ================================

    def toggle_bold(self):
        """Toggle bold font on selected cells"""
        if self.table:
            selected = self.table.selectedIndexes()
            if not selected:
                return
            # Determine current bold state from first selected cell
            first_item = self.table.item(selected[0].row(), selected[0].column())
            if first_item:
                is_bold = first_item.font().bold()
            else:
                is_bold = False
            self.apply_font_style(bold=not is_bold)
        return self

    def toggle_italic(self):
        """Toggle italic font on selected cells"""
        if self.table:
            selected = self.table.selectedIndexes()
            if not selected:
                return
            first_item = self.table.item(selected[0].row(), selected[0].column())
            if first_item:
                is_italic = first_item.font().italic()
            else:
                is_italic = False
            self.apply_font_style(italic=not is_italic)
        return self

    def insert_chart(self):
        """Insert a chart (placeholder - opens info dialog)"""
        pyqt.QMessageBox.information(
            self,
            "Insert Chart",
            "Chart insertion is a planned feature.\n\n"
            "This will allow creating bar, line, and pie charts from selected data ranges.",
        )
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
