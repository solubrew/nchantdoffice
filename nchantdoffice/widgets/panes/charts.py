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

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from seaborn import palettes

from nchantrs.dialogs.colors import NchantdColorSelectSigil
from nchantrs.libraries import pyqt
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox, NchantdLabeledDoubleSpinBox
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons, NchantdBorderConfigBar
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.checkboxes import NchantdCheckboxGroup, NchantdCheckbox
from nchantrs.widgets.groups import NchantdVScrollGroupBox
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.media.editors.entries import NchantdCheckboxEditor
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.groups import NchantdCollapsableGroup, NchantdGroup

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class NchantdChartConfigPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdChartConfigPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.name = None
        self.description = None
        self.type = None
        self.position = None
        self.chart_size = None
        self.origin = None
        self.axis = []
        self.data = []
        self.data_series = []
        self.background = None
        self.plotarea = self.configure_plotarea()
        self.legend = None
        self.chart_types_df = None
        self.colors_df = None
        self.trendline_formulas = None
        self.trendline_forms = None
        self.chart_type = None
        self.themes = None
        self.theme = None
        self.palettes = None
        self.palette = None
        self.border_styles = None
        self.border_style = None
        self.border_colors = None
        self.border_color = None
        self.border_thicknesses = None
        self.border_thickness = None
        self.axis_major_units = None
        self.axis_minor_units = None
        self.axis_major_color = None
        self.legends = None
        self.axes = None
        self.trendlines = None

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
        cfg = {"size": ["auto", "auto"]}
        self.left_group = NchantdVScrollGroupBox(self, cfg)
        self.left_group.layout.setSpacing(0)
        self.left_group.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        self.left_group.setTitle("Chart Configuration")
        chart_specifics_group = pyqt.QGroupBox()
        chart_specifics_group.setTitle("Chart Specifics")
        chart_specifics_layout = pyqt.QGridLayout()
        chart_specifics_group.setLayout(chart_specifics_layout)
        cfg = {
            "label": "Enter Chart Label: ",
            "size": None,
            "entrybox": {"size": ["auto", 30]},
            "handler": self.cmd_on_name_change,
        }
        self.chart_name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        chart_specifics_layout.addWidget(self.chart_name_entry)
        cfg = {
            "label": "Enter Chart Description: ",
            "size": None,
            "entrybox": {"size": ["auto", 60]},
            "handler": self.cmd_on_description_change,
        }
        self.chart_description_entry = NchantdLabeledEntry(self, cfg).initWidget()
        chart_specifics_layout.addWidget(self.chart_description_entry)
        cfg = {
            "label": "Select Chart Theme: ",
            "size": None,
            "options": self.get_themes(),
            "handler": self.cmd_on_theme_change,
        }
        self.chart_theme_select = NchantdDropDown(self, cfg).initWidget()
        chart_specifics_layout.addWidget(self.chart_theme_select)
        cfg = {
            "label": "Select Chart Palette: ",
            "size": None,
            "options": self.get_palettes(),
            "handler": self.cmd_on_palette_change,
        }
        self.chart_palette_select = NchantdDropDown(self, cfg).initWidget()
        chart_specifics_layout.addWidget(self.chart_palette_select)

        self.left_group.addWidget(chart_specifics_group)
        chart_details_group = pyqt.QGroupBox()
        chart_details_group.setTitle("Chart Details")
        chart_details_layout = pyqt.QGridLayout()
        chart_details_group.setLayout(chart_details_layout)
        cfg = {
            "label": "Select Chart Type: ",
            "combobox": {"options": self.get_types()},
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_type(),
            "handler": self.cmd_on_change_type,
        }
        self.chart_type_select = NchantdDropDown(self, cfg).initWidget()
        chart_details_layout.addWidget(self.chart_type_select)
        cfg = {
            "text": "Set Chart Background Color: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "handler": self.cmd_launch_color_sigil,
            "value": self.get_background_color(),
        }
        self.chart_area_color = NchantdButton(self, cfg).initWidget()
        chart_details_layout.addWidget(self.chart_area_color)
        cfg = {
            "text": "Set Chart Area Color: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "handler": self.cmd_launch_color_sigil,
            "value": self.get_area_color(),
        }
        self.chart_color = NchantdButton(self, cfg).initWidget()
        chart_details_layout.addWidget(self.chart_color)
        cfg = {
            "label": "Select Border Style: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.chart_border_bar = NchantdBorderConfigBar(self, cfg).initWidget()
        chart_details_layout.addWidget(self.chart_border_bar)
        # cfg = {
        #     "text": "Set Border Color: ",
        #     "handler": self.cmd_launch_color_sigil,
        #     "value": self.get_border_color(),
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        # }
        # self.chart_border_color = NchantdButton(self, cfg).initWidget()
        # chart_details_layout.addWidget(self.chart_border_color)
        # cfg = {
        #     "label": "Select Border Thickness: ",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        # }
        # self.chart_border_thickness = NchantdLabeledSpinBox(self, cfg).initWidget()
        # chart_details_layout.addWidget(self.chart_border_thickness)
        self.left_group.addWidget(chart_details_group)
        self.left_group.layout_box.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        self.layout.addLayout(self.left_group.layout)
        cfg = {"size": ["auto", 1000]}
        self.center_group = NchantdVScrollGroupBox(self, cfg)
        self.center_group.setTitle("Chart Format Configuration")
        self.center_group.layout_box.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        self.center_group.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        for axis in self.axes:
            cfg = {"label": axis, "size": ["auto", 350]}
            self.axes[axis]["widget"] = NchantdChartAxisPane(self, cfg).initWidget()
            self.center_group.addWidget(self.axes[axis]["widget"])
        cfg = {"text": "Add New Axis"}
        self.new_axis_button = NchantdButton(self, cfg).initWidget()
        self.center_group.addWidget(self.new_axis_button)
        for trendline in self.trendlines:
            cfg = {"label": trendline}
            self.trendlines[trendline]["widget"] = NchantdChartTrendlinePane(self, cfg).initWidget()
            self.center_group.addWidget(self.trendlines[trendline]["widget"])
        cfg = {"text": "Add New Trendline"}
        self.new_trendline_button = NchantdButton(self, cfg).initWidget()
        self.center_group.addWidget(self.new_trendline_button)
        for legend in self.legends:
            cfg = {}
            self.legends[legend]["widget"] = NchantdChartLegendPane(self, cfg).initWidget()
            self.center_group.addWidget(self.legends[legend]["widget"])
        cfg = {"text": "Add New Legend"}
        self.new_legend_button = NchantdButton(self, cfg).initWidget()
        self.center_group.addWidget(self.new_legend_button)
        self.layout.addLayout(self.center_group.layout)
        self.center_group.layout_box.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        cfg = {"size": ["auto", "auto"]}
        self.right_group = NchantdVScrollGroupBox(self, cfg)
        self.right_group.setTitle("Chart Data Configuration")
        for series in self.data_series:
            cfg = {}
            self.data_series[series]["widget"] = NchantdChartDataSeriesPane(self, cfg).initWidget()
            self.right_group.addWidget(self.data_series[series]["widget"])
        cfg = {"text": "Add Data Series"}
        self.new_legend_button = NchantdButton(self, cfg).initWidget()
        self.right_group.addWidget(self.new_legend_button)
        self.right_group.layout_box.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        self.layout.addLayout(self.right_group.layout)

        self.set_size()
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

    def cmd_add_data_series(self):
        """"""
        return self

    def cmd_add_legend(self):
        """"""
        return self

    def cmd_connect_data_source(self):
        """"""
        return self

    def cmd_launch_color_sigil(self, event=None, *args, **kwargs):
        """"""
        cfg = {}
        self.color_sigil = NchantdColorSelectSigil(self, cfg).initWidget()
        return self

    def cmd_set_border_color(self):
        """"""
        return self

    def cmd_set_border_style(self):
        """"""
        return self

    def cmd_set_border_thickness(self):
        """"""
        return self

    def cmd_set_name(self):
        """"""
        return self

    def cmd_set_description(self):
        """"""
        return self

    def cmd_set_color_area(self):
        """"""
        return self

    def cmd_set_color(self):
        """"""
        return self

    def cmd_on_change_type(self, event, *args, **kwargs):
        """"""
        logma.info(f"Event {event} value {args} params {kwargs}")
        self.set_type(self.chart_type_select.get_value())
        return self

    def cmd_on_name_change(self, event, *args, **kwargs):
        """"""

    def cmd_on_description_change(self, event, *args, **kwargs):
        """"""

    def cmd_on_theme_change(self, event, *args, **kwargs):
        """"""

    def cmd_on_palette_change(self, event, *args, **kwargs):
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


class NchantdChartAxisPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdChartAxisPane"))
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
        # cfg = {"size": self.config.dikt.get("size", ["auto", "auto"])}
        cfg = {"size": ["auto", "auto"], "collapsible": True, "collapsed": True}
        new_axis_group = NchantdGroup(self.parent, cfg)  # pyqt.QGroupBox()
        label = self.config.dikt.get("label", None)
        if label is None:
            label = "New Axis"
        else:
            label = f"Edit Axis: {label}"
        new_axis_group.setTitle(label)
        new_axis_layout = pyqt.QVBoxLayout()
        new_axis_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        new_axis_group.setLayout(new_axis_layout)
        cfg = {
            "label": "Show Axis Label: ",
            "layout": "horizontal",
            "size": self.config.dikt.get("size", ["auto", "auto"]),
            "entrybox": {"size": self.config.dikt.get("entrybox", {}).get("size", [50, "auto"])},
        }
        self.axis_entry = NchantdCheckboxEditor(self, cfg).initWidget()
        new_axis_layout.addWidget(self.axis_entry)
        cfg = {
            "label": "Select Axis Style: ",
            "layout": "horizontal",
            "size": self.config.dikt.get("size", ["auto", "auto"]),
        }
        self.chart_axis_bar = NchantdBorderConfigBar(self, cfg).initWidget()
        new_axis_layout.addWidget(self.chart_axis_bar)
        cfg = {
            "label": "Set Origin Cross: ",
            "layout": "horizontal",
            "size": self.config.dikt.get("size", ["auto", "auto"]),
        }
        self.origin_cross_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        new_axis_layout.addWidget(self.origin_cross_spin)
        cfg = {
            "label": "Set Axis Range: ",
            "layout": "horizontal",
            "size": self.config.dikt.get("size", ["auto", "auto"]),
        }
        self.axis_range_spin = NchantdLabeledDoubleSpinBox(self, cfg).initWidget()
        new_axis_layout.addWidget(self.axis_range_spin)
        cfg = {
            "text": "Show Major Grid Units",
            "layout": "horizontal",
            "size": self.config.dikt.get("size", ["auto", "auto"]),
        }
        self.axis_major_unit_check = NchantdCheckbox(self, cfg).initWidget()
        new_axis_layout.addWidget(self.axis_major_unit_check)
        cfg = {
            "text": "Show Minor Grid Units",
            "layout": "horizontal",
            "size": self.config.dikt.get("size", ["auto", "auto"]),
        }
        self.axis_minor_unit_check = NchantdCheckbox(self, cfg).initWidget()
        new_axis_layout.addWidget(self.axis_minor_unit_check)
        cfg = {
            "size": self.config.dikt.get("size", ["auto", 30]),
        }
        self.axis_accept_button = NchantdAcceptButtons(self, cfg).initWidget()
        new_axis_layout.addWidget(self.axis_accept_button)
        new_axis_layout.addStretch(1)
        new_axis_group.set_height(new_axis_layout.sizeHint().height() * 1.2, False)
        self.layout.addWidget(new_axis_group)
        self.setSizePolicy(pyqt.QSizePolicy.Expanding, pyqt.QSizePolicy.Expanding)
        self.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
        logma.info(f"Height {self.layout.sizeHint().height()} Width {self.layout.sizeHint().width()}")
        logma.info(f"Size {self.size().height()}")
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_axsi(self):
        """"""
        return self

    def cmd_add_axis(self):
        """"""
        return self

    def updateGeometry(self):
        """"""
        super().updateGeometry()
        self.parent.updateGeometry()
        return self


class NchantdChartDataSeriesPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdChartTrendlinePane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.color = None
        self.colors = None
        self.data_series_colors = None
        self.data_series_entry = None
        self.data_series_group = None
        self.data_series_shape_group = None
        self.data_series_shape_select = None
        self.data_series_shape_select_value = None
        self.new_series_color_select = None
        self.new_series_style_select = None
        self.new_series_shape_select = None
        self.new_series_thickness_spin = None
        self.new_data_series_connect_data_button = None

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
        new_data_group = NchantdGroup()
        new_data_group.setTitle("Edit Data Series")
        new_data_group.setCheckable(True)
        new_data_layout = pyqt.QGridLayout()
        new_data_group.setLayout(new_data_layout)
        cfg = {"label": "Enter Data Series Name: ", "size": None, "entrybox": {"size": [50, "auto"]}}
        self.data_series_entry = NchantdLabeledEntry(self, cfg).initWidget()
        new_data_layout.addWidget(self.data_series_entry)
        cfg = {
            "label": "Select Series Style: ",
            "combobox": {"options": self.get_data_series_styles()},
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_data_series_style(),
        }
        self.new_series_style_select = NchantdDropDown(self, cfg).initWidget()
        new_data_layout.addWidget(self.new_series_style_select)
        cfg = {
            "label": "Select Series Shape: ",
            "combobox": {"options": self.get_data_series_shapes()},
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_data_series_shape(),
        }
        self.new_series_shape_select = NchantdDropDown(self, cfg).initWidget()
        new_data_layout.addWidget(self.new_series_shape_select)
        cfg = {
            "label": "Select Series Color: ",
            "combobox": {"options": self.get_data_series_shapes()},
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_data_series_shape(),
        }
        self.new_series_color_select = NchantdDropDown(self, cfg).initWidget()
        new_data_layout.addWidget(self.new_series_color_select)
        cfg = {
            "label": "Select Series Thickness: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_data_series_thickness(),
        }
        self.new_series_thickness_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        new_data_layout.addWidget(self.new_series_thickness_spin)
        cfg = {"text": "Connect Data Source", "handler": self.cmd_connect_data_source}
        self.new_data_series_connect_data_button = NchantdButton(self, cfg).initWidget()
        new_data_layout.addWidget(self.new_data_series_connect_data_button)
        cfg = {}
        self.accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        new_data_layout.addWidget(self.accept_buttons)
        self.layout.addWidget(new_data_group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_color(self):
        """"""
        if self.color is None:
            self.color = self.config.dikt.get("trendline_color", "red")
        return self.color

    def get_colors(self):
        """"""
        if self.colors is None:
            self.colors = self.config.dikt.get("trendline_colors", ["red", "blue", "green", "orange", "purple"])
        return self.colors

    def get_line_marker(self):
        """"""
        return self

    def get_line_markers(self):
        """"""
        markers = []
        return markers

    def get_color(self, series=None):
        """"""
        if len(self.data_series) == 0:
            return None
        if series is None:
            series = 0
        color = self.data_series[series].color
        return color

    def get_colors(self):
        """"""
        self.data_series_colors = self.config.dikt.get("data_series_colors", [])
        return self.data_series_colors

    def get_series_data(self):
        """"""
        self.data_series = {}
        return self.data_series

    def get_series(self):
        """"""
        data_series = []
        return data_series

    def get_shape(self, series=None):
        """"""
        if len(self.data_series) == 0:
            return None
        if series is None:
            series = 0
        shape = self.data_series[series].shape
        return shape

    def get_shapes(self):
        """"""
        self.shapes = self.config.dikt.get("data_series_shapes", [])
        return self.shapes

    def get_style(self, series=None):
        """"""
        if len(self.data_series) == 0:
            return None
        if series is None:
            series = 0
        style = self.data_series[series].style
        return style

    def get_styles(self):
        """"""
        self.styles = self.config.dikt.get("data_series_styles", [])
        return self.styles

    def get_thickness(self, series=None):
        """"""
        if series is None:
            series = 0
        if len(self.data_series) == 0:
            return None
        thickness = self.data_series[series].thickness
        return thickness

    def get_thickness_range(self, series=None):
        """"""
        if series is None:
            series = 0
        if len(self.data_series) == 0:
            return None
        thickness = self.data_series[series].thickness
        return thickness


class NchantdChartLegendPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdChartTrendlinePane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.color = None
        self.colors = None
        self.trendline_formula = None
        self.trendline_formulas = None
        self.trendline_form = None
        self.trendline_forms = None

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
        new_data_group = NchantdGroup()
        new_data_group.setTitle("Edit Data Series")
        new_data_group.setCheckable(True)
        new_data_layout = pyqt.QGridLayout()
        new_data_group.setLayout(new_data_layout)
        cfg = {"label": "Enter Data Series Name: ", "size": None, "entrybox": {"size": [50, "auto"]}}
        self.data_series_entry = NchantdLabeledEntry(self, cfg).initWidget()
        new_data_layout.addWidget(self.data_series_entry)
        cfg = {
            "label": "Select Series Style: ",
            "combobox": {"options": self.get_data_series_styles()},
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_data_series_style(),
        }
        self.new_series_style_select = NchantdDropDown(self, cfg).initWidget()
        new_data_layout.addWidget(self.new_series_style_select)
        cfg = {
            "label": "Select Series Shape: ",
            "combobox": {"options": self.get_data_series_shapes()},
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_data_series_shape(),
        }
        self.new_series_shape_select = NchantdDropDown(self, cfg).initWidget()
        new_data_layout.addWidget(self.new_series_shape_select)
        cfg = {
            "label": "Select Series Color: ",
            "combobox": {"options": self.get_data_series_shapes()},
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_data_series_shape(),
        }
        self.new_series_color_select = NchantdDropDown(self, cfg).initWidget()
        new_data_layout.addWidget(self.new_series_color_select)
        cfg = {
            "label": "Select Series Thickness: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_data_series_thickness(),
        }
        self.new_series_thickness_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        new_data_layout.addWidget(self.new_series_thickness_spin)
        cfg = {"text": "Connect Data Source", "handler": self.cmd_connect_data_source}
        self.new_data_series_connect_data_button = NchantdButton(self, cfg).initWidget()
        new_data_layout.addWidget(self.new_data_series_connect_data_button)
        self.right_group.addWidget(new_data_group)
        cfg = {}
        self.accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        new_data_layout.addWidget(self.accept_buttons)
        self.layout.addWidget(new_trendline_group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_color(self):
        """"""
        if self.color is None:
            self.color = self.config.dikt.get("trendline_color", "red")
        return self.color

    def get_colors(self):
        """"""
        if self.colors is None:
            self.colors = self.config.dikt.get("trendline_colors", ["red", "blue", "green", "orange", "purple"])
        return self.colors

    def get_line_marker(self):
        """"""
        return self

    def get_line_markers(self):
        """"""
        markers = []
        return markers

    def get_thickness(self):
        """"""
        return 2

    def get_thickness_range(self):
        """"""
        return 0, 10

    def get_data_series_all(self):
        """"""
        self.data_series = {}
        return self.data_series

    def get_data_series(self):
        """"""
        data_series = []
        return data_series

    def get_data_series_color(self, series=None):
        """"""
        if len(self.data_series) == 0:
            return None
        if series is None:
            series = 0
        color = self.data_series[series].color
        return color

    def get_data_series_colors(self):
        """"""
        self.data_series_colors = self.config.dikt.get("data_series_colors", [])
        return self.data_series_colors

    def get_data_series_style(self, series=None):
        """"""
        if len(self.data_series) == 0:
            return None
        if series is None:
            series = 0
        style = self.data_series[series].style
        return style

    def get_data_series_styles(self):
        """"""
        self.styles = self.config.dikt.get("data_series_styles", [])
        return self.styles

    def get_data_series_shape(self, series=None):
        """"""
        if len(self.data_series) == 0:
            return None
        if series is None:
            series = 0
        shape = self.data_series[series].shape
        return shape

    def get_data_series_shapes(self):
        """"""
        self.shapes = self.config.dikt.get("data_series_shapes", [])
        return self.shapes

    def get_data_series_thickness(self, series=None):
        """"""
        if series is None:
            series = 0
        if len(self.data_series) == 0:
            return None
        thickness = self.data_series[series].thickness
        return thickness


class NchantdChartTrendlinePane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdChartTrendlinePane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.color = None
        self.colors = None
        self.trendline_formula = None
        self.trendline_formulas = None
        self.trendline_form = None
        self.trendline_forms = None

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
        new_trendline_group = NchantdGroup()
        label = self.config.dikt.get("label", None)
        if label is None:
            label = "Add Trend Line"
        else:
            label = f"Edit Trend Line: {label}"
        new_trendline_group.setTitle(label)
        new_trendline_layout = pyqt.QGridLayout()
        new_trendline_group.setLayout(new_trendline_layout)
        cfg = {"label": "Enter Trendline Label: ", "size": None, "entrybox": {"size": [50, "auto"]}}
        self.trendline_entry = NchantdLabeledEntry(self, cfg).initWidget()
        new_trendline_layout.addWidget(self.trendline_entry)
        cfg = {
            "text": "Show Trendline Label",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.axis_show_label_check = NchantdCheckbox(self, cfg).initWidget()
        new_trendline_layout.addWidget(self.axis_show_label_check)
        cfg = {
            "label": "Select Axis Style: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.chart_trendline_bar = NchantdBorderConfigBar(self, cfg).initWidget()
        new_trendline_layout.addWidget(self.chart_trendline_bar)
        cfg = {
            "label": "Set Start Point: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.trendline_start_point_spin = NchantdLabeledDoubleSpinBox(self, cfg).initWidget()
        new_trendline_layout.addWidget(self.trendline_start_point_spin)
        cfg = {
            "label": "Select Trend Line Formula: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "options": self.get_trendline_formulas(),
            "value": self.get_trendline_formula(),
        }
        self.trendline_formula_select = NchantdDropDown(self, cfg).initWidget()
        new_trendline_layout.addWidget(self.trendline_formula_select)
        cfg = {
            "label": "Select Trend Line Form: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "options": self.get_trendline_forms(),
            "value": self.get_trendline_form(),
        }
        self.trendline_form_select = NchantdDropDown(self, cfg).initWidget()
        new_trendline_layout.addWidget(self.trendline_form_select)
        cfg = {
            "label": "Select Trendline Color: ",
            "combobox": {"options": self.get_colors()},
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": self.get_color(),
        }
        self.trendline_color_select = NchantdDropDown(self, cfg).initWidget()
        new_trendline_layout.addWidget(self.trendline_color_select)
        cfg = {
            "label": "Select Trendline Thickness: ",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "range": self.get_thickness_range(),
            "value": self.get_thickness(),
        }
        self.new_trendline_thickness_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        new_trendline_layout.addWidget(self.new_trendline_thickness_spin)
        cfg = {}
        self.trendline_accept_button = NchantdAcceptButtons(self, cfg).initWidget()
        new_trendline_layout.addWidget(self.trendline_accept_button)
        self.layout.addWidget(new_trendline_group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_color(self):
        """"""
        if self.color is None:
            self.color = self.config.dikt.get("trendline_color", "red")
        return self.color

    def get_colors(self):
        """"""
        if self.colors is None:
            self.colors = self.config.dikt.get("trendline_colors", ["red", "blue", "green", "orange", "purple"])
        return self.colors

    def get_line_marker(self):
        """"""
        return self

    def get_line_markers(self):
        """"""
        markers = []
        return markers

    def get_thickness(self):
        """"""
        return 2

    def get_thickness_range(self):
        """"""
        return 0, 10

    def get_trendline_formulas(self):
        """"""
        if self.trendline_formulas is None:
            self.trendline_formulas = self.config.dikt.get("trendline_formulas", ["Best Fit", "Max", "Min", "Sigma"])
        return self.trendline_formulas

    def get_trendline_formula(self):
        """"""
        if self.trendline_formula is None:
            self.trendline_formula = self.config.dikt.get("trendline_formula", "Best Fit")
        return self.trendline_formula

    def get_trendline_forms(self):
        """"""
        if self.trendline_forms is None:
            self.trendline_forms = self.config.dikt.get("trendline_forms", ["Linear", "Log", "Exponential"])
        return self.trendline_forms

    def get_trendline_form(self):
        """"""
        if self.trendline_form is None:
            self.trendline_form = self.config.dikt.get("trendline_form", "Linear")
        return self.trendline_form


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
