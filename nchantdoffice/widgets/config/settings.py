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
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.config.settings import NchantdInterfaceSettings, NchantdSettingsWidget, NchantdThemeSettings
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledDoubleSpinBox, NchantdLabeledSpinBox
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.media.editors.editors import NchantdEntryEditor
from nchantrs.widgets.media.editors.selectors import NchantdDropDown, NchantdComboBox
from nchantrs.widgets.media.images import NchantdImage
from nchantrs.widgets.tables.lists import NchantdList
from nchantrs.widgets.tabsets import NchantdTab
from nchantrs.widgets.groups import NchantdGridScrollGroupBox, NchantdVScrollGroupBox, NchantdHScrollGroupBox
from nchantrs.widgets.groups import NchantdHGroupBox, NchantdGroup
from nchantrs.widgets.config.config import NchantdConfigStoreDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "settings.yaml")


class NchantdOfficeSettingsWidget(NchantdSettingsWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeSettingsWidget"))
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
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeInterfaceSettings(NchantdInterfaceSettings):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("Nchantd"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.primary_settings_group = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        self.document_types_df = self.app.model.get_document_types()
        settings = self.document.get_settings()
        self.enable_journal_focus_bit = (
            None  # settings[settings["label_txt"] == "enable_journal_focus"].values.tolist()[0]
        )
        self.enable_journal_focus_bit_change = False
        self.enable_settings_focus_bit = (
            None  # settings[settings["label_txt"] == "enable_settings_focus"].values.tolist()[0]
        )
        self.enable_settings_focus_bit_change = False
        self.enable_automation_bit = None  # settings[settings["label_txt"] == "enable_automation"].values.tolist()[0]
        self.enable_automation_bit_change = False
        self.enable_data_sources_bit = (
            None  # settings[settings["label_txt"] == "enable_data_sources"].values.tolist()[0]
        )
        self.enable_data_sources_bit_change = False
        self.show_left_pane = None  # settings[settings["label_txt"] == "show_left_pane"].values.tolist()[0]
        self.show_quick_toolbar = None  # settings[settings["label_txt"] == "show_quick_toolbar"].values.tolist()[0]
        self.show_document_catalog = (
            None  # settings[settings["label_txt"] == "show_document_catalog"].values.tolist()[0]
        )
        self.create_default_tab = None  # settings[settings["label_txt"] == "create_default_tab"].values.tolist()[0]
        self.default_tab_select_value = (
            None  # settings[settings["label_txt"] == "default_tab_select_value"].values.tolist()[0]
        )
        self.refocus_right_side_tab = (
            None  # settings[settings["label_txt"] == "refocus_right_side_tab"].values.tolist()[0]
        )
        self.default_right_side_tab = (
            None  # settings[settings["label_txt"] == "default_right_side_tab"].values.tolist()[0]
        )
        self.show_right_side_tab = None  # settings[settings["label_txt"] == "show_right_side_tab"].values.tolist()[0]
        self.quick_launch_toolbar_change = False
        self.quick_launch_document_types_change = False
        self.document_launch_tab_change = False
        self.default_tab_change = False
        self.refocus_setting_change = False
        self.refocus_default_document_change = False
        self.right_side_pane_change = False
        self.tab_entry_change = False
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)

        self.primary_settings_group = pyqt.QGroupBox()
        self.primary_settings_group.setTitle("Interface Settings")
        primary_layout = pyqt.QHBoxLayout()
        self.primary_settings_group.setLayout(primary_layout)

        # Left Side Settings Group
        left_side_settings_group = NchantdGridScrollGroupBox()
        left_side_settings_group.scroll.setHorizontalScrollBarPolicy(pyqt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_side_settings_group.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
        left_side_settings_group.setTitle("Left Pane Settings")
        primary_layout.addLayout(left_side_settings_group.layout)
        cnt = 0
        # cfg = {
        #     "text": "Show Journal Node",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.enable_journal_focus_bit,
        #     "handler": self.cmd_on_change_journal_focus,
        # }
        # self.enable_journal_focus_entry = NchantdCheckbox(self, cfg).initWidget()
        # left_side_settings_group.addWidget(self.enable_journal_focus_entry, cnt, 0)
        # cnt += 1
        # cfg = {
        #     "text": "Show Settings Node",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.enable_settings_focus_bit,
        #     "handler": self.cmd_on_change_settings_focus,
        # }
        # self.settings_node = NchantdCheckbox(self, cfg).initWidget()
        # left_side_settings_group.addWidget(self.settings_node, cnt, 0)
        # cnt += 1
        # HOLD
        # cfg = {
        #     "text": "Enable Automation",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.enable_automation_bit,
        #     "handler": self.cmd_on_change_automation,
        # }
        # self.automation_enable = NchantdCheckbox(self, cfg).initWidget()
        # left_side_settings_group.addWidget(self.automation_enable, cnt, 0)
        # cnt += 1
        # cfg = {
        #     "text": "Enable Data Sources",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.enable_data_sources_bit,
        #     "handler": self.cmd_on_change_data_source,
        # }
        # self.data_source_enable = NchantdCheckbox(self, cfg).initWidget()
        # left_side_settings_group.addWidget(self.data_source_enable, cnt, 0)
        # cnt += 1
        # cfg = {
        #     "text": "On Startup Show Left Side Pane",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.show_left_pane,
        #     "handler": self.cmd_on_change_show_left_side_pane,
        # }
        # self.left_side_pane = NchantdCheckbox(self, cfg).initWidget()
        # left_side_settings_group.addWidget(self.left_side_pane, cnt, 0)
        # cnt += 1
        # cfg = {
        #     "text": "On Startup Show Quick Launch Toolbar",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.show_quick_toolbar,
        #     "handler": self.cmd_on_change_quicklaunch,
        # }
        # self.quick_launch_toolbar = NchantdCheckbox(self, cfg).initWidget()
        if self.config.dikt.get("has_quick_launch_toolbar", False) is True:
            self.quick_launch_toolbar.setChecked(True)
        # left_side_settings_group.addWidget(self.quick_launch_toolbar, cnt, 0)
        # cnt += 1
        document_group = pyqt.QGroupBox()
        document_group.setTitle("Quick launch Documents")
        document_group_layout = pyqt.QVBoxLayout()
        document_group_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignRight)
        document_group.setLayout(document_group_layout)
        self.quick_launch_document_types = {}
        for i, document in self.document_types_df.iterrows():
            cfg = {"text": document["name_txt"], "layout": "horizontal", "size": ["auto", "auto"]}
            self.quick_launch_document_types[document["name_txt"]] = NchantdCheckbox(self, cfg).initWidget()
            # if not self.quick_launch_toolbar.isChecked():
            #     self.quick_launch_document_types[document["name_txt"]].setDisabled(True)
            if document["quick_launch_bit"] == 1:
                self.quick_launch_document_types[document["name_txt"]].setChecked(True)
            document_group_layout.addWidget(self.quick_launch_document_types[document["name_txt"]])
        left_side_settings_group.addWidget(document_group, cnt, 0)

        # Center Settings Group
        center_settings_group = NchantdGridScrollGroupBox()
        center_settings_group.scroll.setHorizontalScrollBarPolicy(pyqt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        center_settings_group.setTitle("Center Pane Settings")
        primary_layout.addLayout(center_settings_group.layout)
        # cfg = {
        #     "text": "Show Document Launch Catalog",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.show_document_catalog,
        #     "handler": self.cmd_on_change_document_catalog,
        # }
        # self.document_launch_tab = NchantdCheckbox(self, cfg).initWidget()
        # TODO: possiblly only allow pro users to turn off
        #  center_settings_group.addWidget(self.document_launch_tab, 0, 0)
        # cfg = {
        #     "text": "Create Default Tab",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.create_default_tab,
        #     "handler": self.cmd_on_change_default_tab_bit,
        # }
        # self.default_tab = NchantdCheckbox(self, cfg).initWidget()
        # if self.config.dikt.get("has_default_tab", False) is True:
        #     self.default_tab.setChecked(True)
        # center_settings_group.addWidget(self.default_tab, 1, 0)
        # options = self.document_types_df["name_txt"].tolist()
        # cfg = {
        #     "label": "Select Default Tab",
        #     "layout": "horizontal",
        #     "options": options,
        #     "value": self.default_tab_select_value,
        #     "handler": self.cmd_on_change_default_tab_select,
        # }
        # self.default_tab_switch = NchantdDropDown(self, cfg).initWidget()
        # center_settings_group.addWidget(self.default_tab_switch, 2, 0)
        # if not self.default_tab.isChecked():
        #     self.default_tab_switch.setDisabled(True)
        # else:
        #     pass  # TODO set current default tab
        center_settings_group.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)

        # Right Side Settings Group
        right_side_settings_group = NchantdGridScrollGroupBox()
        right_side_settings_group.scroll.setHorizontalScrollBarPolicy(pyqt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_side_settings_group.setTitle("Right Pane Settings")
        primary_layout.addLayout(right_side_settings_group.layout)
        # cfg = {
        #     "text": "Always Refocus Right Side Tabs to",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.refocus_right_side_tab,
        #     "handler": self.cmd_on_change_right_side_focus,
        # }
        # self.refocus_setting = NchantdCheckbox(self, cfg).initWidget()
        # # TODO add a drop down to replace the word toolbox with alist of right pane tabs
        # right_side_settings_group.addWidget(self.refocus_setting, 0, 0)
        # TODO pull from database combine sequence with name to get a proper sort in the visual and control the actual sequenc of the right side tabs
        # TODO change right selector to a position changer put a spinbox on each tab
        cfg = {
            "label": "Selected Right Side Tab",
            "layout": "horizontal",
            "combobox": {"options": ["0 - Journal", "1 - ToolBox", "2 - Calendar", "3 - Calculator"]},
            "value": self.default_right_side_tab,
            "handler": self.cmd_on_change_right_side_tab_select,
        }
        self.refocus_default_document = NchantdDropDown(self, cfg).initWidget()
        right_side_settings_group.addWidget(self.refocus_default_document, 1, 0)
        # cfg = {
        #     "text": "On Startup Show Right Side Pane",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.show_right_side_tab,
        #     "handler": self.cmd_on_change_show_right_side_pane,
        # }
        # self.right_side_pane = NchantdCheckbox(self, cfg).initWidget()
        # right_side_settings_group.addWidget(self.right_side_pane, 2, 0)

        # group = pyqt.QGroupBox("Right Side Tabs List")
        # layout = pyqt.QVBoxLayout()
        # group.setLayout(layout)
        # data = ["Journal", "ToolBox", "Calendar", "Calculator"]
        # cfg = {"text": "Right Side Tabs List", "layout": "horizontal", "data": data}
        # self.right_side_pane_tabs_list = NchantdList(self, cfg).initWidget()
        # layout.addWidget(self.right_side_pane_tabs_list)
        # cfg = {"label": "Tab Name: ", "layout": "horizontal"}
        # self.tab_entry = NchantdEntryEditor(self, cfg).initWidget()
        # layout.addWidget(self.tab_entry)
        # cfg = {"label": "Tab Type: ", "layout": "horizontal"}
        # self.tab_type_entry = NchantdDropDown(self, cfg).initWidget()
        # layout.addWidget(self.tab_type_entry)
        # cfg = {"label": "Sequence: ", "layout": "horizontal"}
        # self.tab_sequence_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        # layout.addWidget(self.tab_sequence_spin)
        # cfg = {"text": "Accept Buttons: ", "layout": "horizontal"}
        # self.new_tab_accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        # layout.addWidget(self.new_tab_accept_buttons)
        # right_side_settings_group.addWidget(group, 3, 0)

        right_side_settings_group.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.primary_settings_group)
        # self.layout.addLayout(self.primary_settings_group.layout)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_on_change_journal_focus(self):
        """"""
        # TODO implement method
        return self

    def cmd_on_change_settings_focus(self):
        """"""
        # TODO implement method
        return self

    def cmd_on_change_automation(self):
        """"""
        # TODO implement method
        return self

    def cmd_on_change_data_source(self):
        """"""
        # TODO implement method
        return self

    def cmd_on_change_show_left_side_pane(self):
        """"""
        # TODO implement method
        return self

    def cmd_on_change_show_right_side_pane(self):
        """"""
        # TODO implement method
        return self

    def cmd_on_change_quicklaunch(self):
        """"""
        # TODO implement method
        return self

    def cmd_on_change_document_catalog(self):
        """"""
        # TODO implement method
        return self

    def cmd_on_change_default_tab_bit(self):
        """"""
        # TODO implement method
        return self

    def cmd_on_change_default_tab_select(self):
        """"""
        # TODO implement method
        return self

    def cmd_on_change_right_side_focus(self):
        """"""
        # TODO implement method
        return self

    def cmd_on_change_right_side_tab_select(self):
        """"""
        # TODO implement method
        return self

    def get_settings(self):
        """"""
        return super().get_settings("interface")

    def on_data_changed(self):
        """"""
        # create a new data entry
        # connect with the old data entry
        # when save is called replace it in the database

    def save(self):
        """"""
        super().save()
        data = []
        # if self.enable_journal_focus_bit.changed:
        #     data.append([self.journal_node.isChecked()])
        # if self.enable_settings_focus_bit.changed:
        #     data.append([self.settings_node.isChecked()])
        # if self.enable_automation_bit.changed:
        #     data.append([self.automation_enable.isChecked()])
        # if self.enable_data_sources_bit.changed:
        #     data.append([self.data_source_enable.isChecked()])
        # if self.enable_journal_focus_bit.changed:
        #     data.append([self.left_side_pane.isChecked()])
        # if self.enabel_quick_launch_toolbar_bit.changed:
        #     data.append([self.quick_launch_toolbar.isChecked()])
        #
        #     for document in self.document_types.iterrows():
        #         data.append([document["name_txt"], self.quick_launch_document_types[document["name_txt"]].isChecked()])
        # if self.enable_journal_focus_bit.changed:
        #     data.append([self.document_launch_tab.isChecked()])
        # if self.enable_journal_focus_bit.changed:
        #     data.append([self.default_tab_switch.currentText()])
        return self


class NchantdOfficeThemeSettings(NchantdThemeSettings):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeThemeSettings").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
