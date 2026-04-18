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
from nchantrs.libraries import pyqt
from kahndor.logma import Logma
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.media.editors.entries import NchantdActivateEntry
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.tables.lists import NchantdList
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.groups import NchantdGroup
from nchantrs.widgets.groups import NchantdVScrollGroupBox
from nchantrs.dialogs.colors import NchantdColorSelectSigil
from nchantrs.widgets.widgets import NchantdWidget

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "sources.yaml")


class NchantdSourceEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdSourceEditPane"))
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
        cfg = {"text": self.config.dikt.get("label", "Data Set: ")}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"label": "Table: "}
        self.table_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.table_select)
        self.data_filters = [{"label": "field = 'information'", "description": "filter Field by Information"}]
        for filter in self.data_filters:
            label = NchantdLabel(self, filter).initWidget()
            layout.addWidget(label)
        cfg = {"text": "+ Add Filter"}
        self.add_filter_button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.add_filter_button)
        cfg = {}
        self.accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        layout.addWidget(self.accept_buttons)
        self.layout.addWidget(group)
        self.layout.addStretch()
        # self.spacer = pyqt.QSpacerItem(20, 40, pyqt.QSizePolicy.Minimum, pyqt.QSizePolicy.Expanding)
        # self.layout.addItem(self.spacer)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdSourcesListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(self)
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


class NchantdWhereUsedListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(self)
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
        cfg = {"text": "Where Used:"}
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


class NchantdOfficeEDA(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.Instruct(pxcfg).select("NchantdOfficeEDA")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)
        self.slim_tab = True

    def initModel(self):
        """"""
        super().initModel()
        self.slim_tab = self.config.dikt.get("slim_tab", True)
        return self

    def initView(self):
        """
        Have a slim version to show on the right side and a full version to show in the center tabset
        """
        super().initView()
        if self.slim_tab is True:
            pass
        else:
            pass
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def set_slim_tab(self, slim_tab=False):
        """"""
        self.slim_tab = slim_tab
        return self


class NchantdSourcePane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdSourcePane"))
        if self.parent:
            self.config.override(parent.config)
            self.catalog = self.parent.catalog
        self.config.override(cfg)
        self.accept_buttons_layout = None
        self.accept_buttons = None
        self.data_source_entry = None
        self.active_item = None

    def initModel(self):
        """"""
        super().initModel()
        self.active_item = self.catalog.selected_item
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        cfg = {
            "label": "Document Sources: ",
            "size": None,
            "combobox": {"options": self.config.dikt.get("options", []), "size": [200, 20]},
            "layout": "horizontal",
        }
        logma.info("Data Source Pane:")
        self.data_source_entry = NchantdDropDown(self, cfg).initWidget()
        self.left_side_layout.addWidget(self.data_source_entry)
        cfg = {
            "text": "Set Data Source as Available",
            "value": self.get_data_source_availability(),
            "handler": self.cmd_on_change_data_source_availability,
            "size": ["auto", 30],
        }
        self.datasource_available_check = NchantdCheckbox(self, cfg).initWidget()
        self.left_side_layout.addWidget(self.datasource_available_check)
        self.left_side_layout.addStretch()
        # need a status on wether the data service needs an API key
        if self.active_item is not None:
            logma.info(f"Active Item: {self.active_item}")
            if self.active_item.requires_api_key is True:
                if self.app.model.user.check_has_api(self.active_item.slug):
                    cfg = {"text": "API Key Already Stored", "color": "green", "size": [500, 40]}
                    self.data_source_api_required_status = NchantdLabel(self, cfg).initWidget()
                    self.left_side_layout.addWidget(self.data_source_api_required_status)
                    cfg = {
                        "action": "show_api_key",
                        "readonly": True,
                        "size": ["auto", 30],
                        "layout": "horizontal",
                        "handler": self.cmd_show_api_key,
                    }
                    self.data_source_api_required_status = NchantdActivateEntry(self, cfg).initWidget()
                    self.left_side_layout.addWidget(self.data_source_api_required_status)
                else:
                    cfg = {"text": "API Key Not Stored", "color": "green", "size": [500, 40]}
                    self.data_source_api_required_status = NchantdLabel(self, cfg).initWidget()
                    self.left_side_layout.addWidget(self.data_source_api_required_status)
                    cfg = {
                        "action": "get_api_key",
                        "text": "Get API Key:",
                        "layout": "horizontal",
                        "size": ["auto", 30],
                        "readonly": False,
                        "handler": self.cmd_launch_source,
                        "value": "Enter API Key",
                    }
                    self.data_source_api_entry = NchantdActivateEntry(self, cfg).initWidget()
                    self.left_side_layout.addWidget(self.data_source_api_entry)
                # need a status on if the user has an API key
                # need an entry for an api key
                # need a launch button to get an api key
            else:
                cfg = {"text": "No API Key Required", "color": "green", "size": [1000, 200]}
                self.data_source_api_required_status = NchantdLabel(self, cfg).initWidget()
                self.left_side_layout.addWidget(self.data_source_api_required_status)
                # have an add service checkbox?
            # need a save and a cancel button

        self.accept_buttons_layout = pyqt.QHBoxLayout()
        cfg = {"action": None, "handler": self.accept}
        self.accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        self.accept_buttons_layout.addWidget(self.accept_buttons)
        self.accept_buttons_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignBottom | pyqt.Qt.AlignmentFlag.AlignRight)
        self.setSizePolicy(pyqt.QSizePolicy.Expanding, pyqt.QSizePolicy.Expanding)
        self.layout.addStretch()
        self.layout.addLayout(self.accept_buttons_layout)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_launch_data_source(self):
        """"""

    def cmd_on_change_data_source_availability(self, event=None, *args, **kwargs):
        """"""
        # update database to show that data source is available

    def cmd_show_api_key(self):
        """"""

    def get_data_source_availability(self):
        """"""
        return self.active_item.is_data_source_available

    def store_active_source(self):
        """

        :return:
        """
        if self.active_item.requires_api_key is True:
            data = {"key": key, "value": value}
            self.app.model.store.store_secure_data(data)
        data = {
            "uuid": uuid(),
            "key": self.active_item.slug,
            "label": "api_key",
            "value": self.active_item.secure_stored_key,
            "description": self.active_item.description,
        }
        self.app.model.store.store_app_option(data)
        return self

    def update_pane(self):
        """"""
        super().update_pane()

        return self


class NchantdDataSetPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(self)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("Nchantd"))
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
        cfg = {"text": "Data Set", "size": [100, 200]}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"text": self.config.dikt.get("text", "Missing Label")}
        self.label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(self.label)
        cfg = {"data": self.get_data_view_fields()}
        self.fields_list = NchantdList(self, cfg).initWidget()
        layout.addWidget(self.fields_list)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_data_view_fields(self):
        """"""
        fields = self.parent.get_data_view_fields()
        return fields


class NchantdViewPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdViewPane"))
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
        cfg = {"collapsible": True, "collapsed": False, "text": "View"}
        view_group = NchantdGroup(self.parent, cfg)
        layout = pyqt.QVBoxLayout()
        view_group.setLayout(layout)
        scroll = pyqt.QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        cfg = {"text": "View"}
        self.edit_pane = NchantdViewEditPane(self.parent, cfg).initWidget()
        scroll.setWidget(self.edit_pane)
        view_group.set_height(layout.sizeHint().height() + 10)
        self.layout.addWidget(view_group)
        # self.layout.addStretch()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdViewEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdViewEditGroup"))
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
        cfg["layout"] = "vertical"
        super().initView(cfg)

        cfg = {
            "collapsible": True,
            "collapsed": False,
            "text": "Field Selection",
            "layout": "horizontal",
            "show_size": ["auto", 100],
        }
        self.fields_group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        fields_layout = pyqt.QHBoxLayout()
        self.fields_group.setLayout(layout)
        cfg = {"text": "Field", "size": ["auto", 30]}
        self.field_check = NchantdCheckbox(self, cfg).initWidget()
        fields_layout.addWidget(self.field_check)

        layout.addLayout(fields_layout)
        accpet_layout = pyqt.QVBoxLayout()
        cfg = {"text": "Add Field"}
        self.add_field_button = NchantdButton(self, cfg).initWidget()
        accpet_layout.addWidget(self.add_field_button)
        layout.addLayout(accpet_layout)
        self.fields_group.set_height(layout.sizeHint().height() * 1.5)
        self.layout.addWidget(self.fields_group)

        cfg = {
            "collapsible": True,
            "collapsed": False,
            "text": "Filter Configuration",
            "layout": "horizontal",
            "show_size": ["auto", 100],
        }
        self.filter_group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        filter_layout = pyqt.QHBoxLayout()
        self.filter_group.setLayout(layout)
        cfg = {"text": "Select Field", "options": self.get_fields(), "size": ["auto", 30], "layout": "horizontal"}
        self.fields_select = NchantdDropDown(self, cfg).initWidget()
        filter_layout.addWidget(self.fields_select)
        cfg = {
            "text": "Operator",
            "options": ["==", "!=", ">", "<", ">=", "<=", "[=]", "[!=]", "]=[", "]!=[", "=[]="],
            "size": ["auto", 30],
            "layout": "horizontal",
        }
        self.operator_select = NchantdDropDown(self, cfg).initWidget()
        filter_layout.addWidget(self.operator_select)
        cfg = {"label": "Value", "size": ["auto", 30], "layout": "horizontal"}
        self.value_entry = NchantdLabeledEntry(self, cfg).initWidget()
        filter_layout.addWidget(self.value_entry)
        self.filter_edit_accept_button = NchantdAcceptButtons(self, cfg).initWidget()
        filter_layout.addWidget(self.filter_edit_accept_button)
        layout.addLayout(filter_layout)
        accpet_layout = pyqt.QVBoxLayout()
        cfg = {"text": "Add Filter"}
        self.add_filter_button = NchantdButton(self, cfg).initWidget()
        accpet_layout.addWidget(self.add_filter_button)
        layout.addLayout(accpet_layout)
        self.filter_group.set_height(layout.sizeHint().height() * 1.5)
        self.layout.addWidget(self.filter_group)

        cfg = {
            "collapsible": True,
            "collapsed": False,
            "text": "Summary Configuration",
            "layout": "horizontal",
            "show_size": ["auto", 100],
        }
        self.summary_group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        summary_layout = pyqt.QHBoxLayout()
        self.summary_group.setLayout(layout)
        cfg = {"label": "Select Field", "options": self.get_fields(), "size": ["auto", 30]}
        self.fields_select = NchantdDropDown(self, cfg).initWidget()
        summary_layout.addWidget(self.fields_select)
        cfg = {
            "label": "Select Operator",
            "options": ["==", "!=", ">", "<", ">=", "<=", "[=]", "[!=]", "]=[", "]!=[", "=[]="],
            "size": ["auto", 30],
        }
        self.operator_select = NchantdDropDown(self, cfg).initWidget()
        summary_layout.addWidget(self.operator_select)
        cfg = {"label": "Enter Value", "size": ["auto", 30]}
        self.value_entry = NchantdLabeledEntry(self, cfg).initWidget()
        summary_layout.addWidget(self.value_entry)
        layout.addLayout(filter_layout)
        accpet_layout = pyqt.QVBoxLayout()
        cfg = {"text": "Add Summarization Field"}
        self.add_summary_button = NchantdButton(self, cfg).initWidget()
        accpet_layout.addWidget(self.add_summary_button)
        layout.addLayout(accpet_layout)
        self.summary_group.set_height(layout.sizeHint().height() + 10)
        self.layout.addWidget(self.summary_group)
        self.summary_group.set_height(layout.sizeHint().height() * 1.5)
        self.spacer = pyqt.QSpacerItem(20, 40, pyqt.QSizePolicy.Minimum, pyqt.QSizePolicy.Expanding)
        self.layout.addItem(self.spacer)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_fields(self):
        """"""
        fields = self.parent.parent.get_data_view_fields()
        return fields


class NchantdDataSetConfigPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdSourceConfigPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.name = None
        self.description = None
        self.type = None
        self.position = None
        self.origin = None
        self.data = []
        self.data_series = []
        self.background = None
        self.plotarea = self.configure_plotarea()
        self.legend = None
        self.chart_types_df = None
        self.colors_df = None
        self.themes = None
        self.theme = None
        self.palettes = None
        self.palette = None

    def initModel(self):
        """"""
        super().initModel()
        self.get_types()
        self.get_colors()
        self.data_series = []
        self.axes = self.config.dikt.get("axes", {})
        self.axes["X"] = {}
        self.axes["Y"] = {}
        self.legends = self.config.dikt.get("legends", {})
        self.trendlines = self.config.dikt.get("trendlines", {})
        self.data_series = self.config.dikt.get("data_series", {})
        return self

    def initView(self):
        """"""
        super().initView()
        self.source_width = self.config.dikt.get("source_width", 350)
        cfg = {"size": [self.source_width, "auto"]}
        self.left_group = NchantdVScrollGroupBox(self, cfg)
        self.left_group.layout.setSpacing(0)
        self.left_group.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        self.left_group.setTitle("Data Source Configuration")
        self.left_group.layout_box.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        cfg = {"collapsable": False}
        chart_specifics_group = NchantdGroup(self, cfg)
        chart_specifics_group.setTitle("Data Source Specifics")
        chart_specifics_layout = pyqt.QGridLayout()
        chart_specifics_layout.setSpacing(3)
        chart_specifics_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        chart_specifics_group.setLayout(chart_specifics_layout)
        cfg = {
            "label": "Enter Data Source Name",
            "entrybox": {"size": ["auto", 30]},
            "handler": self.cmd_on_name_change,
            "size": ["auto", 30],
        }
        self.chart_name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        chart_specifics_layout.addWidget(self.chart_name_entry)
        cfg = {
            "label": "Enter Data Source Description",
            "size": ["auto", 30],
            "entrybox": {"size": ["auto", 60]},
            "handler": self.cmd_on_description_change,
        }
        self.chart_description_entry = NchantdLabeledEntry(self, cfg).initWidget()
        chart_specifics_layout.addWidget(self.chart_description_entry)
        chart_specifics_group.set_height(chart_specifics_layout.sizeHint().height() * 1.2)
        self.left_group.addWidget(chart_specifics_group)
        self.left_group.layout_box.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        self.layout.addLayout(self.left_group.layout)
        logma.info(f"Port Size {self.size()} {self.parent.size()}")
        cfg = {"size": [self.parent.size().width() - self.source_width - 20, 350]}
        self.center_group = NchantdVScrollGroupBox(self, cfg)
        self.center_group.setTitle("Data Source Views")
        # cfg = {"text": "Add New View"}
        self.new_view_config_pane = NchantdViewPane(self, cfg).initWidget()
        self.center_group.addWidget(self.new_view_config_pane)
        self.center_group.layout.setSpacing(3)
        self.center_group.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        self.center_group.layout_box.setSpacing(3)
        self.center_group.layout_box.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        self.center_group.group.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
        self.center_group.layout.addStretch()
        self.center_group.layout_box.addStretch()
        self.layout.addLayout(self.center_group.layout)
        self.center_group.layout_box.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        self.set_size()
        self.setMinimumHeight(self.config.dikt.get("size", ["auto", 350])[1])
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def add_axis(self):
        """"""
        return self

    def add_data_series(self):
        """"""
        return self

    def add_legend(self, legend):
        """"""
        return self

    def configure_background(self):
        """"""
        return self

    def configure_legend(self):
        """"""
        return self

    def configure_plotarea(self):
        """"""
        return self

    def cmd_add_data_series(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_add_legend(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_connect_source(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_launch_color_sigil(self, event=None, *args, **kwargs):
        """"""
        cfg = {}
        self.color_sigil = NchantdColorSelectSigil(self, cfg).initWidget()
        return self

    def cmd_set_border_color(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_set_border_style(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_set_border_thickness(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_set_name(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_set_description(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_set_color_area(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_set_color(self, event=None, *args, **kwargs):
        """"""
        return self

    def cmd_on_change_type(self, event=None, *args, **kwargs):
        """"""
        logma.info(f"Event {event} value {args} params {kwargs}")
        self.set_type(self.chart_type_select.get_value())
        return self

    def cmd_on_name_change(self, event=None, *args, **kwargs):
        """"""

    def cmd_on_description_change(self, event=None, *args, **kwargs):
        """"""

    def cmd_on_theme_change(self, event=None, *args, **kwargs):
        """"""

    def cmd_on_palette_change(self, event=None, *args, **kwargs):
        """"""

    def set_type(self, value):
        """"""
        self.parent.chart_type = value
        self.update_chart()
        return self

    def cmd_set_data_series_color(self):
        """"""
        return self

    def cmd_set_data_series_name(self):
        """"""
        return self

    def cmd_set_data_series_shape(self):
        """"""
        return self

    def cmd_set_data_series_style(self):
        """"""
        return self

    def cmd_set_data_series_thickness(self):
        """"""
        return self

    def get_border_color(self):
        """"""
        self.border_color = self.config.dikt.get("border_color", "")
        return self.border_color

    def get_border_colors(self):
        """"""
        self.border_colors = self.config.dikt.get("border_colors", [])
        return self.border_colors

    def get_border_style(self):
        """"""
        return self.border_style

    def get_border_styles(self):
        """"""
        self.border_styles = self.config.dikt.get("border_styles", [])
        return self.border_styles

    def get_border_thickness(self):
        """"""
        if self.border_thickness is None:
            self.border_thickness = self.config.dikt.get("border_thickness", 1)
        return self.border_thickness

    def get_background_color(self):
        """"""
        self.chart_color = self.config.dikt.get("chart_color", "")
        return self.chart_color

    def get_area_color(self):
        """"""
        self.chart_color = self.config.dikt.get("chart_color", "")
        return self.chart_color

    def get_border_color(self):
        """"""
        self.chart_color = self.config.dikt.get("chart_color", "")
        return self.chart_color

    def get_colors(self):
        """"""
        if self.colors_df is None:
            self.load_colors()
        self.chart_colors = self.colors_df["value_txt"].tolist()
        return self.chart_colors

    def get_area_color(self):
        """"""
        self.chart_color = self.config.dikt.get("chart_color", "")
        return self.chart_color

    def get_area_colors(self):
        """"""
        if self.colors_df is None:
            self.load_colors()
        self.chart_colors = self.colors_df["value_txt"].tolist()
        return self.chart_colors

    def get_palette(self):
        """"""
        if self.palette is None:
            self.palette = self.config.dikt.get("chart_palette", "Dark")
        return self.palette

    def get_palettes(self):
        """"""
        if self.palettes is None:
            self.palettes = self.config.dikt.get(
                "chart_palettes", ["Dark", "DarkGrid", "Dark_background", "Dark2", "Dark2_5"]
            )
        return self.palettes

    def get_theme(self):
        """"""
        if self.theme is None:
            self.theme = self.config.dikt.get("chart_theme", "DarkGrid")
        return self.theme

    def get_themes(self):
        """"""
        if self.themes is None:
            self.themes = self.config.dikt.get("themes", ["DarkGrid", "Dark", "White", "WhiteGrid"])
        return self.themes

    def get_type(self):
        """"""
        if self.parent.chart_type is None:
            self.parent.chart_type = self.config.dikt.get("chart_type", "Line")
        return self.parent.chart_type

    def get_types(self):
        """"""
        if self.chart_types_df is None:
            self.load_types()
        self.chart_types = self.chart_types_df["value_txt"].tolist()
        return self.chart_types

    def get_legend(self):
        """"""
        return self

    def get_legends(self):
        """"""
        return self

    def load_types(self):
        """"""
        table = "vw_chart_types"
        cfg = {}
        self.chart_types_df = self.app.model.store.get_table(table, cfg)
        return self

    def load_colors(self):
        """"""
        table = "vw_colors"
        cfg = {}
        self.colors_df = self.app.model.store.get_table(table, cfg)
        return self

    def update_chart(self):
        """"""
        logma.info(f"Update Chart to {self.get_type()}")
        self.parent.set_type(self.get_type())
        return self


class NchantdSourceDefaultPane(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdSourceDefaultPane"))
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
        cfg = {"label": "Default Source Details:"}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {
            "label": "Set Default Source: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_sources()},
            "value": self.get_source(),
            "handler": self.cmd_on_source_change,
        }
        self.source_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.source_select)
        cfg = {
            "label": "Set Default Table: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_source_tables(self.get_source())},
            "value": self.get_source_table(),
            "handler": self.cmd_on_data_table_change,
        }
        self.table_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.table_select)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_on_data_table_change(self, event):
        """"""

    def cmd_on_source_change(self, event=None, *args, **kwargs):
        """"""

    def get_source(self, event=None, *args, **kwargs):
        """"""
        return self.app.active_tab.get_source()

    def get_sources(self):
        """"""
        return self.app.active_tab.get_sources()

    def get_source_table(self):
        """"""
        table = ""  # self.app.active_tab.get_source_table(source)
        return table

    def get_source_tables(self, source):
        """"""
        # tables = self.app.active_tab.get_source_tables()
        tables = []
        return tables


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
