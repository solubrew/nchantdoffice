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
from condor import condor
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
from pyffice.spreadsheet.spreadsheet import PyfficeMatrix
from pyffice.workflows.formulas import PyfficeFormulasLibrary
from ogma.logma import Logma
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
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeCellBorderFormats"))
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

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Nchantd Matrix", parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeMatrix"))
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
        """"""
        return self

    def cmd_cell_background_color_select(self, event, *args, **kwargs):
        """"""
        cfg = {}
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
        """"""
        cfg = {}
        self.color_select_sigil = NchantdColorSelectSigil(self, cfg).initWidget()
        return self

    def cmd_row_spinbox(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_row_height_spinbox(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_column_spinbox(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_column_width_spinbox(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_formula_entrybox(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_merge_cells(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_data_source_select(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_data_filters_select(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_on_click_default_cell_background_color_button(self, event, *args, **kwargs):
        """"""
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
        """Move the cell within a worksheet"""

        targetrow = (self.row + addrow) % self.num_rows
        targetcol = (self.col + addcol) % self.num_cols

        # def focus(event):
        # 	targetwidget = self.siblings[cellname(targetrow, targetcol)].widget
        # 	targetwidget.focus()

        return focus

    def populate_document(self):
        """"""
        logma.info(f"Populate worksheet {self.document.data}")
        logma.info(f"Populate worksheet {type(self.document.data)}")
        self.table.update_data(self.document.data)

    def set_table(self):
        """turn the spreadsheet into a table where there is a corresponding database table for it"""


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
