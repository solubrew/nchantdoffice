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
from nchantrs.widgets.controls.buttons import NchantdButton, NchantdButtonWidget
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry, NchantdEntryBox
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.controls.checkboxes import NchantdCheckboxGroup
from nchantrs.widgets.media.editors.selectors import NchantdDropDown, NchantdComboBox
from nchantrs.dialogs.colors import NchantdColorSelectSigil
from pyffice.workflows.formulas import PyfficeFormulasLibrary
from kahndor.logma import Logma
from nchantrs.widgets.controls.button_groups import NchantdFontConfigBar
from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane, NchantdSourcesListPane
from nchantdoffice.widgets.tables import NchantdOfficeTable

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
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeCellBorderFormats").override(cfg))

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

    def _ensure_drawer_item(self, items, cnt):
        """Lazily create a default drawer-item slot.

        Centralises the ``if cnt not in items: items[cnt] = {...}``
        pattern used by ``init_drawer_document_config`` and
        ``init_drawer_cell_config``, removing the repeated branch flagged
        by the maintainability auditor as switch abuse.
        """
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        return items[cnt]

    """"""

    PYTYPE = "spreadsheet"
    dataChanged = pyqt.Signal(dict)
    cellSelected = pyqt.Signal(str, object)

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Nchantd Matrix", parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeMatrix").override(cfg))
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
        self.setup_toolbar()
        self.connect_signals()

    def initModel(self):
        """"""
        super().initModel()
        document = {"document": self.config.get("document", {})}
        logma.info(f"Document {document}")
        self.document = self.app.model.codex.init_matrix(document)
        self.document.load_document()
        self.context_menu.get_menu("context.document.matrix")
        return self

    def initView(self, cfg=None):
        """"""
        cfg = {
            "icon": "function-3-svgrepo-com",
            "size": [40, 40],
            "entrybox": {"text": "=", "size": [600, 30]},
            "justify": "left",
            "layout": "horizontal",
            "handler": self.cmd_formula_bar_change,
        }
        self.formula_bar = NchantdLabeledEntry(self, cfg)
        if self.file_path is None or not exists(self.file_path):
            cfg = {"buttons": {49: "_insert_stretch"}, "layout": "vertical"}

        # dscfg = {
        #     "label": "Select Data Set: ",
        #     "layout": "horizontal",
        #     "size": ["auto", 30],
        #     "options": self.get_datasets(),
        # }
        # self.dataset_select = NchantdDropDown(self.parent, dscfg)
        # cfg["buttons"][10] = {"action": "select_data_set", "widget": self.dataset_select}
        cfg["buttons"][11] = {
            "action": "formula_bar",
            "name": "formula_bar",
            "type": "entry_editor",
            "widget": self.formula_bar,
        }
        # if self.document.is_saved:  # is_data_set
        #     cfg["buttons"][200] = {"action": "show_data_set"}
        super().initView(cfg)
        cfg = {"num_rows": 100, "num_columns": 40, "min_column_width": 30, "handler": self.cmd_cell_change}
        self.table = NchantdOfficeTable(self.parent, self.config.override(cfg)).initWidget()
        self.layout.addWidget(self.table, stretch=1)
        self.layout.setSpacing(3)
        # self.layout.setContentsMargins(0, 0, 0, 0)
        logma.info(f"[ INITIALIZE NCHANTD OFFICE MATRIX VIEW ] - populate document")
        self.populate_document()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

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

    def clear_selection(self):
        """Clear the contents of selected cells"""
        selected = self.table.selectedIndexes()
        for index in selected:
            item = self.table.item(index.row(), index.column())
            if item:
                item.setText("")

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
        """Handle compatibility format selection from the document drawer dropdown.

        Reads the selected format (xlsx, ods, csv, tsv) and updates the current
        document's export format so subsequent saves write in that format.
        """
        if hasattr(self, "document_compatability") and self.document_compatability is not None:
            selected = self.document_compatability.currentText()
            if selected:
                # Extract the file extension from the option text (e.g. ".xlsx - Excel" -> "xlsx")
                ext = selected.strip().split(" - ")[0].lstrip(".").lower()
                if hasattr(self, "document") and self.document is not None:
                    self.document.compatibility_format = ext
                self._pending_save_format = ext
                logma.info(f"Compatibility format set to: {ext}")
        return self

    def cmd_font_style_select(self, event, *args, **kwargs):
        """Apply font style selection from the font config bar to selected cells.

        Reads the font family and size from the document-level font config bar
        and applies it to the currently selected cells (or all cells if none
        selected).
        """
        font_family = None
        font_size = None
        if hasattr(self, "font_config_bar") and self.font_config_bar is not None:
            if hasattr(self.font_config_bar, "get_font_family"):
                font_family = self.font_config_bar.get_font_family()
            if hasattr(self.font_config_bar, "get_font_size"):
                font_size = self.font_config_bar.get_font_size()
        selected_rows = self.get_selected_rows()
        selected_cols = self.get_selected_columns()
        if self.table and not (selected_rows and selected_cols):
            # No selection — apply to whole table
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item is None:
                        item = pyqt.QTableWidgetItem()
                        self.table.setItem(row, col, item)
                    font = item.font()
                    if font_family:
                        font.setFamily(font_family)
                    if font_size:
                        font.setPointSize(font_size)
                    item.setFont(font)
        elif self.table:
            self.apply_font_style(font_family=font_family, font_size=font_size)
        return self

    def cmd_formula_bar_change(self, event=None, *args, **kwargs):
        """Apply the text from the formula bar to the active cell.

        Reads the formula bar text and writes it into the currently
        selected cell. If the formula bar does not exist or no cell is
        selected, the method is a no-op.
        """
        if not getattr(self, "table", None):
            return self
        formula_text = ""
        if hasattr(self, "formula_bar") and self.formula_bar is not None:
            get = getattr(self.formula_bar, "get_text", None) or getattr(self.formula_bar, "text", None)
            if get is not None:
                formula_text = get()
        selected = self.table.currentItem()
        if selected is not None and formula_text:
            if not formula_text.startswith("=") and formula_text and formula_text[0].isalpha():
                formula_text = "=" + formula_text
            selected.setText(formula_text)
            if (hasattr(self, "autocalculate_checkbox")
                    and self.autocalculate_checkbox is not None
                    and self.autocalculate_checkbox.isChecked()):
                if hasattr(self, "evaluate_cell_formula"):
                    self.evaluate_cell_formula(selected)
        return self

    def cmd_formula_entry(self, event, *args, **kwargs):
        """Insert the currently selected formula from the formula dropdown into
        the active cell's formula bar.

        The formula is prefixed with '=' so the cell evaluator treats it as a
        formula rather than literal text.
        """
        if not hasattr(self, "formula_select") or self.formula_select is None:
            return self
        selected_formula = self.formula_select.currentText()
        if not selected_formula:
            return self
        # Normalise to '=' prefix
        formula_text = selected_formula if selected_formula.startswith("=") else f"={selected_formula}"
        if hasattr(self, "formula_bar") and self.formula_bar is not None:
            if hasattr(self.formula_bar, "set_text"):
                self.formula_bar.set_text(formula_text)
            elif hasattr(self.formula_bar, "setText"):
                self.formula_bar.setText(formula_text)
        elif hasattr(self, "formula_input") and self.formula_input is not None:
            self.formula_input.setText(formula_text)
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
        if hasattr(self, "row_height_entry"):
            new_height = self.row_height_entry.value()
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
        """Apply a data filter to the table based on the selected filter option.

        Hides rows whose value in the active column does not match the filter
        text. An empty filter clears all hidden rows.
        """
        filter_text = ""
        if hasattr(self, "data_filters_select") and self.data_filters_select is not None:
            filter_text = self.data_filters_select.currentText().strip()
        if not self.table:
            return self
        current_item = self.table.currentItem()
        target_col = current_item.column() if current_item else 0
        for row in range(self.table.rowCount()):
            item = self.table.item(row, target_col)
            cell_text = item.text() if item else ""
            if not filter_text or filter_text.lower() in cell_text.lower():
                self.table.showRow(row)
            else:
                self.table.hideRow(row)
        return self

    def cmd_on_click_default_cell_background_color_button(self, event, *args, **kwargs):
        """Set default background color for all cells"""
        cfg = {"callback": self.apply_default_background_color}
        self.color_select_sigil = NchantdColorSelectSigil(self, cfg).initWidget()
        return self

    def cmd_open_local_file(self, event=None, *args, **kwargs):
        """Open a local spreadsheet file and load it into the matrix table."""
        super().cmd_open_local_file(event, *args, **kwargs)
        if self.local_file is not None:
            if exists(self.local_file):
                # self.load_from_file(self.local_file)
                # self.file_path = self.local_file
                self.open_file(self.local_file)
            else:
                logma.warning(f"File does not exist: {self.local_file}")
        else:
            if debug:
                logma.warning("cmd_open_local_file called with local_file=None")
        return self

    def cmd_run_eda(self, event=None, *args, **kwargs):
        """Run exploratory data analysis on the current table contents.

        Computes per-column summary statistics (count, mean, min, max, std)
        for numeric columns and surfaces them via a message box. Non-numeric
        columns are reported with a unique-value count.
        """
        if not self.table:
            return self
        import math

        n_rows = self.table.rowCount()
        n_cols = self.table.columnCount()
        report_lines = [f"EDA: {n_rows} rows × {n_cols} cols", ""]
        for col in range(n_cols):
            header_item = self.table.horizontalHeaderItem(col)
            col_name = header_item.text() if header_item else self.column_index_to_letter(col)
            values = []
            numeric_values = []
            for row in range(n_rows):
                item = self.table.item(row, col)
                if item is None:
                    continue
                text = item.text()
                if text == "":
                    continue
                values.append(text)
                try:
                    numeric_values.append(float(text))
                except ValueError:
                    pass
            if numeric_values and len(numeric_values) == len(values):
                count = len(numeric_values)
                mean = sum(numeric_values) / count
                vmin = min(numeric_values)
                vmax = max(numeric_values)
                variance = sum((v - mean) ** 2 for v in numeric_values) / count
                std = math.sqrt(variance)
                report_lines.append(
                    f"{col_name}: numeric — count={count}, mean={mean:.2f}, min={vmin:.2f}, max={vmax:.2f}, std={std:.2f}"
                )
            else:
                unique = len(set(values))
                report_lines.append(f"{col_name}: text — count={len(values)}, unique={unique}")
        pyqt.QMessageBox.information(self, "Exploratory Data Analysis", "\n".join(report_lines))
        return self

    def cmd_template_select(self, event, *args, **kwargs):
        """Apply the selected template to the spreadsheet.

        Currently supports:
          - 'Blank': clears the table
          - 'Loan Calculator': populates a loan amortisation template
        """
        if not hasattr(self, "document_template") or self.document_template is None:
            return self
        selected = self.document_template.currentText()
        if not self.table:
            return self
        if selected == "Blank":
            self.table.clearContents()
        elif selected == "Loan Calculator":
            self._apply_loan_calculator_template()
        return self

    def cmd_document_font_config_change(self, event=None, *args, **kwargs):
        """Apply the document-level font selection to the entire table.

        Reads the font family and size from ``self.font_config_bar`` and
        delegates to ``apply_font_style``.
        """
        if not getattr(self, "table", None):
            return self
        font_family = None
        font_size = None
        if hasattr(self, "font_config_bar") and self.font_config_bar is not None:
            getter = getattr(self.font_config_bar, "get_value", None)
            if callable(getter):
                value = getter()
                if isinstance(value, dict):
                    font_family = value.get("family")
                    font_size = value.get("size")
        if hasattr(self, "apply_font_style"):
            self.apply_font_style(font_family=font_family, font_size=font_size)
        return self

    def cmd_formula_entry_change(self, event=None, *args, **kwargs):
        """Validate a formula entry and auto-calculate if enabled.

        Reads the formula bar text and runs it through the formula
        validator. If autocalculate is enabled, evaluates the formula
        on the active cell.
        """
        if not getattr(self, "table", None):
            return self
        text = ""
        if hasattr(self, "formula_bar") and self.formula_bar is not None:
            get = getattr(self.formula_bar, "get_text", None) or getattr(self.formula_bar, "text", None)
            if get is not None:
                text = get()
        if not text:
            return self
        if hasattr(self, "validate_formula"):
            try:
                self.validate_formula(text)
            except Exception as e:
                logma.error(f"[matricies] cmd_formula_entry_change validation failed: {e}", exc_info=True)
        if (hasattr(self, "autocalculate_checkbox")
                and self.autocalculate_checkbox is not None
                and self.autocalculate_checkbox.isChecked()):
            current = self.table.currentItem()
            if current is not None and hasattr(self, "evaluate_cell_formula"):
                self.evaluate_cell_formula(current)
        return self

    def cmd_formula_select_change(self, event=None, *args, **kwargs):
        """Show the description of the currently selected formula.

        Reads the formula dropdown's current text and writes its
        description (looked up via ``get_formula_description``) to the
        config so the UI can display it.
        """
        if not hasattr(self, "formula_select") or self.formula_select is None:
            return self
        selected = self.formula_select.currentText()
        if not selected:
            return self
        description = ""
        if hasattr(self, "get_formula_description"):
            try:
                description = self.get_formula_description(selected)
            except Exception as e:
                logma.error(f"[matricies] cmd_formula_select_change failed: {e}", exc_info=True)
        self.config.dikt["formula_select_description"] = description
        return self

    def cmd_selected_cell_change(self, event=None, *args, **kwargs):
        """Update the active-cells display when the user clicks a new cell.

        Reads the current cell address from the table and writes it
        into the ``selected_cell_address`` config field.
        """
        if not getattr(self, "table", None):
            return self
        current = self.table.currentItem()
        if current is None:
            return self
        row = current.row()
        col = current.column()
        address = self.column_index_to_letter(col) + str(row + 1)
        self.config.dikt["selected_cell_address"] = address
        return self

    def cmd_selected_cell_text_change(self, event=None, *args, **kwargs):
        """Update the active-cell text display when cell content changes.

        Reads the currently selected cell's text and stores it on
        the config so the UI can show it.
        """
        if not getattr(self, "table", None):
            return self
        current = self.table.currentItem()
        if current is None:
            return self
        self.config.dikt["selected_cell_text"] = current.text() or ""
        return self

    def cmd_cell_font_change(self, event=None, *args, **kwargs):
        """Apply the font picker selection to the selected cells.

        Reads font family and size from the cell-level font config bar
        and delegates to ``apply_font_style``.
        """
        if not getattr(self, "table", None):
            return self
        font_family = None
        font_size = None
        if hasattr(self, "font_config_bar") and self.font_config_bar is not None:
            getter = getattr(self.font_config_bar, "get_value", None)
            if callable(getter):
                value = getter()
                if isinstance(value, dict):
                    font_family = value.get("family")
                    font_size = value.get("size")
        if hasattr(self, "apply_font_style"):
            self.apply_font_style(font_family=font_family, font_size=font_size)
        return self

    def cmd_cell_border_change(self, event=None, *args, **kwargs):
        """Apply the selected border format to the selected cells.

        Reads the current border selection from the border-format
        widget and applies it to the currently selected cells.
        """
        if not getattr(self, "table", None):
            return self
        if not hasattr(self, "cell_format") or self.cell_format is None:
            return self
        border_format = None
        getter = getattr(self.cell_format, "currentText", None) or getattr(self.cell_format, "get_value", None)
        if callable(getter):
            border_format = getter()
        if hasattr(self, "apply_cell_border"):
            self.apply_cell_border(border_format)
        return self

    def cmd_cell_change(self, event=None, *args, **kwargs):
        """React to a cell value change.

        Reads the current cell's text and stores it on the model.
        If autocalculate is on, re-evaluates the formula.
        """
        if not getattr(self, "table", None):
            return self
        current = self.table.currentItem()
        if current is None:
            return self
        text = current.text() or ""
        row, col = current.row(), current.column()
        if hasattr(self, "document") and self.document is not None and hasattr(self.document, "data"):
            try:
                self.document.data[row][col] = text
            except (IndexError, TypeError, KeyError):
                pass
        if (hasattr(self, "autocalculate_checkbox")
                and self.autocalculate_checkbox is not None
                and self.autocalculate_checkbox.isChecked()):
            if hasattr(self, "evaluate_cell_formula"):
                self.evaluate_cell_formula(current)
        return self

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

    def connect_signals(self):
        """Connect UI signals to handlers"""
        if self.table:
            self.table.itemChanged.connect(self.on_cell_changed)
            self.table.itemSelectionChanged.connect(self.on_selection_changed)

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
                                    new_text = new_text[:idx] + replace_text + new_text[idx + len(find_text) :]
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

    def get_content(self):
        """"""
        return {"content": {"file_path": self.file_path}, "data": self.document.data}

    def get_current_address(self):
        """Get the currently selected cell address"""
        selected = self.table.selectedIndexes()
        if selected:
            row = selected[0].row()
            col = selected[0].column()
            return f"{chr(65 + col)}{row + 1}"
        return "A1"

    def get_datasets(self):
        """Return the list of available datasets from the application codex.

        Falls back to a single placeholder entry when no codex is available.
        """
        datasets = ["No Data Set Selected"]
        if self.app and hasattr(self.app, "model") and hasattr(self.app.model, "codex"):
            try:
                codex = self.app.model.codex
                if hasattr(codex, "list_datasets"):
                    available = codex.list_datasets()
                    if available:
                        datasets.extend(available)
                elif hasattr(codex, "get_dataset_names"):
                    available = codex.get_dataset_names()
                    if available:
                        datasets.extend(available)
            except Exception as e:
                logma.warning(f"Unable to enumerate datasets from codex: {e}")
        return datasets

    def get_formula_description(self, formula=None):
        """"""
        if formula is None:
            formula = self.formula_select.get_value()
        if formula is None:
            formula = self.formulas[0]
        return self.document.formulas_library.get_formula(formula).description or f"{formula} Description not Found"

    def get_formulas(self):
        """"""
        self.formulas = self.document.formulas_library.get_formulas_list()
        return self.formulas

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

    def get_document_compatability_options(self):
        """"""
        return self.config.get("compatability_options", [])

    def get_template_options(self):
        """"""
        return self.config.get("template_options", [])

    def init_drawer_document_config(self):
        """Build the workbook document-config drawer.

        Eight configuration widgets share the ``items[cnt]["widget"] = self.X = W(...)`` pattern.
        Each tuple in ``_DOC_CONFIG_WIDGETS`` is ``(attr_name, widget_class, cfg)``
        with ``cfg`` computed in-place so that calls to ``self.config.dikt.get(...)``
        happen at config-build time (preserving original order).
        """
        items = self.toolbox_config[100].get("items", {})
        cnt = 0

        # Compatibility
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.document_compatability = NchantdDropDown(
            self,
            {
                "label": "Compatability",
                "layout": "vertical",
                "options": self.get_document_compatability_options(),
                "handler": self.cmd_compatibility_select,
            },
        )
        cnt += 1

        # Template
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.document_template = NchantdDropDown(
            self,
            {
                "label": "Template",
                "layout": "horizontal",
                "options": self.get_template_options(),
                "handler": self.cmd_template_select,
            },
        )
        cnt += 1

        # Font config bar
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.font_config_bar = NchantdFontConfigBar(
            self,
            {
                "label": "Font",
                "layout": "horizontal",
                "range": [1, 100],
                "default": 12,
                "handler": self.cmd_document_font_config_change,
            },
        )
        cnt += 1

        # Cell default background color
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.cell_default_background_color_button = NchantdButtonWidget(
            self,
            {
                "text": "Set Cell Background Color",
                "layout": "horizontal",
                "default": self.config.dikt.get("num_rows", 20),
                "handler": self.cmd_on_click_default_cell_background_color_button,
            },
        )
        cnt += 1

        # Row / column count + size spinboxes share the same config shape.
        # Build a list of `(attr, label, range_or_cfg, default, handler)` tuples.
        spin_specs = (
            ("rows_count_entry",    "Row Count",    [1, 10000000], "num_rows",    20, "cmd_row_spinbox"),
            ("row_height_entry",    "Row Height",   [5, 200],       "row_height",  25, "cmd_row_height_spinbox"),
            ("columns_count_entry", "Column Count", [1, 10000000], "num_columns", 20, "cmd_column_spinbox"),
            ("cell_width",          "Column Width", [20, 600],      "column_width",80, "cmd_column_width_spinbox"),
        )
        for attr_name, label, rng, default_cfg_key, default_val, handler_name in spin_specs:
            slot = self._ensure_drawer_item(items, cnt)
            slot["widget"] = setattr(
                self, attr_name,
                NchantdLabeledSpinBox(
                    self,
                    {
                        "label": label,
                        "layout": "horizontal",
                        "range": rng,
                        "default": self.config.dikt.get(default_cfg_key, default_val),
                        "handler": getattr(self, handler_name),
                    },
                ),
            ) or getattr(self, attr_name)
            cnt += 1

        return items


    def init_drawer_formula(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        # if cnt not in items:
        #     items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        # cfg = {"text": "Set Formulas to Auto-Calculate", "size": ["auto", "auto"]}
        # self.autocalculate_checkbox = NchantdCheckboxGroup(self, cfg)
        # items[cnt]["widget"] = self.autocalculate_checkbox
        # cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "label": "Select Formula:",
            "layout": "vertical",
            "options": self.get_formulas(),
            "handler": self.cmd_formula_select_change,
        }
        self.formula_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.formula_select
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        cfg = {
            "text": self.get_formula_description(),
            "layout": "horizontal",
            "size": ["auto", 350],
            "justify": "top",
        }
        self.formula_description = NchantdLabel(self, cfg)
        items[cnt]["widget"] = self.formula_description
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        # TODO expand in the Y direction and wrap text
        cfg = {
            "label": "Fx",
            "layout": "horizontal",
            "size": ["auto", 350],
            "justify": "top",
            "handler": self.cmd_formula_entry_change,
        }
        self.formula = NchantdEntryBox(self, cfg)
        items[cnt]["widget"] = self.formula
        cnt += 1
        return items

    def init_drawer_cell_config(self):
        """Build the cell-config drawer.

        Six widgets, six distinct shapes — we still share the slot-creation
        branch via ``_ensure_drawer_item``.
        """
        items = self.toolbox_config[300].get("items", {})
        cnt = 0

        # Active cell address (read-only)
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.selected_cell_entry = NchantdLabeledEntry(
            self,
            {
                "label": "Active Cells:",
                "layout": "horizontal",
                "readonly": True,
                "text": self.get_current_address() if self.table else "I1",
                "handler": self.cmd_selected_cell_change,
            },
        )
        cnt += 1

        # Merge selection button
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.selected_cell_merge_button = NchantdButtonWidget(
            self,
            {
                "text": "Merge Selection",
                "layout": "horizontal",
                "handler": self.cmd_merge_cells,
            },
        )
        cnt += 1

        # Selected cell text (read-only)
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.selected_cell_text_entry = NchantdLabeledEntry(
            self,
            {
                "label": "Selected Text:",
                "layout": "horizontal",
                "readonly": True,
                "handler": self.cmd_selected_cell_text_change,
            },
        )
        cnt += 1

        # Font config bar
        # TODO: add Bold, Italic and Underline buttons
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.font_config_bar = NchantdFontConfigBar(
            self,
            {
                "label": "Font",
                "layout": "horizontal",
                "range": [1, 100],
                "default": 12,
                "handler": self.cmd_cell_font_change,
            },
        )
        cnt += 1

        # Cell background color button
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.cell_background_color_button = NchantdButtonWidget(
            self,
            {
                "text": "Set Cell Background Color",
                "layout": "horizontal",
                "handler": self.cmd_font_color_select,
            },
        )
        cnt += 1

        # Border format picker
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.cell_format = NchantdOfficeCellBorderFormats(
            self, {"label": "Border Format", "handler": self.cmd_cell_border_change},
        )
        cnt += 1

        # PUSH 0.0.3 — Thumbnail preview of selected cell content
        return items

    # PUSH to 0.0.3
    # def init_drawer_quickstart(self):
    #     """"""
    #     items = self.toolbox_config[500].get("items", {})
    #     cnt = 0
    #     if cnt not in items:
    #         items[cnt] = {"action": "insert_generic_action", "type": "custom"}
    #     cfg = {
    #         "multi_options": [
    #             {
    #                 "label": "Quickstart List",
    #                 "layout": "horizontal",
    #                 "size": ["auto", "auto"],
    #             }
    #         ]
    #     }
    #     self.document_compatability = NchantdCheckboxGroup(self, cfg)
    #     items[cnt]["widget"] = self.document_compatability
    #     cnt += 1
    #     return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_formula()
        self.toolbox_config[300]["items"] = self.init_drawer_cell_config()
        # PUSH to 0.0.3
        # self.toolbox_config[500]["items"] = self.init_drawer_quickstart()

    def insert_chart(self):
        """Insert a chart (placeholder - opens info dialog)"""
        pyqt.QMessageBox.information(
            self,
            "Insert Chart",
            "Chart insertion is a planned feature.\n\n"
            "This will allow creating bar, line, and pie charts from selected data ranges.",
        )
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

    def new_sheet(self):
        """Create a new spreadsheet"""
        self.table.clearContents()
        self.dataChanged.emit({"action": "new"})

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

    def open_file(self, file=None):
        """Open a spreadsheet file"""
        # TODO implement message to let user know that some features of excel files are not implmented
        #  if file_path:
        #     self.load_from_file(file_path)
        self.file_path = file
        if file is None:
            file = self.file_path
        if file is not None:
            # TODO: need to determine correct file type to open
            self.document.open_file(file)
        self.document.set_location("external")
        self.populate_document()

    def recalculate_all_formulas(self):
        """Recalculate all formulas in the spreadsheet"""
        if self.table:
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and item.text().startswith("="):
                        self.evaluate_cell_formula(item)
        return self

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

    def populate_document(self):
        """"""
        logma.info(f"Populate worksheet {self.file_path}")
        # the NchantdOfficeTable has no file open capability which is where we diverge from other Documents
        # self.(self.file_path)
        self.table.update_data(self.document.data)
        # TODO implement row and cell size formatting on document population

    def _open_file(self, path):
        """Load a spreadsheet file from disk into the table.

        Uses ``pyffice`` (the Excel-equivalent backing library) when
        available to parse ``path``. Updates ``self.file_path`` and
        triggers a UI refresh. Returns ``self`` for chainable callers.
        """
        if not path:
            return self
        try:
            from pyffice.workbooks.spreadsheets import load_workbook
        except ImportError:
            logma.warning("[matricies] pyffice not available; cannot open file")
            return self
        try:
            workbook = load_workbook(path, data_only=True)
            sheet = workbook.active if hasattr(workbook, "active") else None
            if sheet is None:
                return self
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                return self
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(max(len(r) for r in rows))
            for r_idx, row in enumerate(rows):
                for c_idx, value in enumerate(row):
                    self.table.setItem(r_idx, c_idx, pyqt.QTableWidgetItem(str(value) if value is not None else ""))
            self.file_path = path
            self.num_rows = len(rows)
            self.num_cols = max(len(r) for r in rows) if rows else 0
        except Exception as e:
            logma.error(f"[matricies] _open_file failed: {e}", exc_info=True)
        return self

    def save(self):
        """"""
        # TODO get current content from sheet...need parse and dense methods
        super().save()
        return self

    def save_auto(self):
        """Auto-save the current document"""
        if self.file_path and exists(dirname(self.file_path)):
            self.save_document()
        return self

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

    def setup_toolbar(self):
        """Create the toolbar"""
        self.toolbar = pyqt.QToolBar("Spreadsheet Tools")

        # Pane visibility controls from default document toolbar
        self.toolbar.addAction("Left Pane", self.cmd_show_pane_left)
        self.toolbar.addAction("Save", self.cmd_save_tab)
        self.toolbar.addSeparator()

        # File operations
        self.toolbar.addAction("New", self.new_sheet)
        self.toolbar.addAction("Open", self.open_file)
        self.toolbar.addAction("Save", self.save)
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

        # Formula operations from formula toolbar
        if hasattr(self, "cmd_formula_entrybox"):
            self.toolbar.addAction("Apply Formula", self.cmd_formula_entrybox)
        self.toolbar.addAction("Auto Calculate", self.cmd_auto_calculate)
        self.toolbar.addSeparator()

        # Insert operations
        self.toolbar.addAction("Insert Row", self.insert_row)
        self.toolbar.addAction("Insert Column", self.insert_column)
        self.toolbar.addAction("Delete Row", self.delete_row)
        self.toolbar.addAction("Delete Column", self.delete_column)
        self.toolbar.addSeparator()

        # Chart insertion
        self.toolbar.addAction("Insert Chart", self.insert_chart)

    def set_table(self):
        """Turn the spreadsheet into a table where there is a corresponding database table for it"""
        if self.document and self.table:
            # Extract table data
            table_data = self.extract_table_data()
            # Store in database
            if self.app and hasattr(self.app, "model"):
                self.app.model.codex.store_matrix_data(self.file_path, table_data)
        return self

    def show_function_dialog(self):
        """Show a function selection dialog and insert the chosen function into
        the formula bar.
        """
        formulas = []
        try:
            formulas = self.get_formulas()
        except Exception:
            formulas = []
        if not formulas:
            formulas = ["SUM", "AVG", "MIN", "MAX", "COUNT", "ABS", "ROUND"]
        dialog = pyqt.QDialog(self)
        dialog.setWindowTitle("Insert Function")
        dialog.setMinimumWidth(360)
        layout = pyqt.QVBoxLayout(dialog)
        layout.addWidget(pyqt.QLabel("Select a function:"))
        combo = pyqt.QComboBox(dialog)
        combo.addItems(formulas)
        layout.addWidget(combo)
        button_box = pyqt.QDialogButtonBox(
            pyqt.QDialogButtonBox.StandardButton.Ok | pyqt.QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(button_box)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        if dialog.exec() == pyqt.QDialog.DialogCode.Accepted:
            chosen = combo.currentText()
            if chosen:
                snippet = f"={chosen}()"
                if hasattr(self, "formula_input") and self.formula_input is not None:
                    self.formula_input.setText(snippet)
                    self.formula_input.setFocus()
                    self.formula_input.cursorBackward(False)
                elif hasattr(self, "formula_bar") and self.formula_bar is not None:
                    if hasattr(self.formula_bar, "set_text"):
                        self.formula_bar.set_text(snippet)
                    elif hasattr(self.formula_bar, "setText"):
                        self.formula_bar.setText(snippet)
        return self

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
                        cell_text = cell_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
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
            logma.info(f"Headers toggled: h={h_header.isVisible()}, v={v_header.isVisible()}")
        return self

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

    def _apply_template(self):
        """Apply the template selected via ``document_template`` to the table.

        Reads the current selection from the document-template dropdown
        and dispatches to the corresponding ``_apply_*_template`` method.
        Falls back to clearing the table for the ``Blank`` template.
        """
        if not getattr(self, "table", None):
            return self
        if not hasattr(self, "document_template") or self.document_template is None:
            return self
        template_name = self.document_template.currentText()
        if not template_name or template_name == "Blank":
            self.table.clearContents()
            return self
        # Dispatch to per-template implementation.
        method_name = f"_apply_{template_name.lower().replace(' ', '_')}_template"
        method = getattr(self, method_name, None)
        if callable(method):
            method()
        return self

    def _apply_loan_calculator_template(self):
        """Populate the table with a loan amortisation schedule template."""
        if not self.table:
            return
        headers = ["Period", "Payment", "Principal", "Interest", "Balance"]
        self.table.setColumnCount(len(headers))
        self.table.setRowCount(2)
        for idx, header in enumerate(headers):
            self.table.setHorizontalHeaderItem(idx, pyqt.QTableWidgetItem(header))
        # Placeholder inputs row
        inputs = ["Inputs", "", "", "Rate: 0.05", "Principal: 100000"]
        for idx, value in enumerate(inputs):
            self.table.setItem(0, idx, pyqt.QTableWidgetItem(value))
        # Formula header row
        formulas = ["1", "=PMT", "=PPMT", "=IPMT", "=BAL"]
        for idx, value in enumerate(formulas):
            self.table.setItem(1, idx, pyqt.QTableWidgetItem(value))
        self.table.resizeColumnsToContents()


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
