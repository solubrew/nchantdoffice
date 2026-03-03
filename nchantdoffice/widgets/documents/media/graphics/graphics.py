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
from condor import condor
from ogma.logma import Logma
from nchantrs.libraries import pyqt
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.canvases.canvases import NchantdCanvas
from nchantrs.widgets.media.palettes import NchantdPalette
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.tables.lists import NchantdList
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledDoubleSpinBox
from nchantdoffice.widgets.panes.objects import NchantdNewObjectPane
from nchantrs.widgets.tables.lists import NchantdListEditor
from nchantrs.widgets.groups import NchantdCollapsableGroup, NchantdGroup
from nchantrs.dialogs.colors import NchantdColorSelectSigil

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "graphics.yaml")


class NchantdLayersListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(self)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdLayersListPane"))
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
        cfg = {"text": "Layers", "layout": "vertical", "collapsible": False}
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


class NchantdEditLayerPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(self)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdEditorLayerPane"))
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
        cfg = {"text": self.config.dikt.get("label", "Edit Layer: ")}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"label": "Layer Name: "}
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)
        cfg = {"label": "Transparency: "}
        self.transparency_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.transparency_entry)
        cfg = {"label": "Size: "}
        self.size_set = NchantdLabeledDoubleSpinBox(self, cfg).initWidget()
        layout.addWidget(self.size_set)
        cfg = {}
        self.accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        layout.addWidget(self.accept_buttons)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdObjectsPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(self)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdObjectsPane"))
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
        cfg = {"label": "Objects: "}
        self.group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        self.group.setLayout(layout)
        cfg = {}
        self.objects_list = NchantdListEditor(self, cfg).initWidget()
        layout.addWidget(self.objects_list)
        self.layout.addWidget(self.group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdLineToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdLineToolPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Line Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = True
        cfg["collapsed"] = True
        group = NchantdGroup(self, cfg).set_open(False)
        group_layout = pyqt.QVBoxLayout()
        group.setLayout(group_layout)
        cfg = {"label": "Line Style: ", "layout": "horizontal", "options": ["Solid", "Dashed", "Dotted", "Dash Dotted"]}
        self.line_style_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_style_select)
        cfg = {"label": "Thickness: ", "layout": "horizontal"}
        self.line_thickness_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        group_layout.addWidget(self.line_thickness_spin)
        cfg = {"label": "Color: ", "layout": "horizontal"}
        self.line_color_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_color_select)
        cfg = {"label": "End Type One: ", "layout": "horizontal"}
        self.line_end_one_type_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_end_one_type_select)
        cfg = {"label": "End Type Two: ", "layout": "horizontal"}
        self.line_end_two_type_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_end_two_type_select)
        group.set_height(group_layout.sizeHint().height())
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdCurveToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdLineToolPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Curve Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = True
        cfg["collapsed"] = True
        group = NchantdGroup(self, cfg)
        group_layout = pyqt.QVBoxLayout()
        group.setLayout(group_layout)
        cfg = {"label": "Line Style: ", "layout": "horizontal", "options": ["Solid", "Dashed", "Dotted", "Dash Dotted"]}
        self.line_style_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_style_select)
        cfg = {"label": "Thickness: ", "layout": "horizontal"}
        self.line_thickness_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        group_layout.addWidget(self.line_thickness_spin)
        cfg = {"label": "Color: ", "layout": "horizontal"}
        self.line_color_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_color_select)
        cfg = {"label": "End Type One: ", "layout": "horizontal"}
        self.line_end_one_type_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_end_one_type_select)
        cfg = {"label": "End Type Two: ", "layout": "horizontal"}
        self.line_end_two_type_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_end_two_type_select)
        group.set_height(group_layout.sizeHint().height())
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdSplineToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdLineToolPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Spline Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = True
        cfg["collapsed"] = True
        group = NchantdGroup(self, cfg)
        group_layout = pyqt.QVBoxLayout()
        group.setLayout(group_layout)
        cfg = {"label": "Line Style: ", "layout": "horizontal", "options": ["Solid", "Dashed", "Dotted", "Dash Dotted"]}
        self.line_style_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_style_select)
        cfg = {"label": "Thickness: ", "layout": "horizontal"}
        self.line_thickness_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        group_layout.addWidget(self.line_thickness_spin)
        cfg = {"label": "Color: ", "layout": "horizontal"}
        self.line_color_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_color_select)
        cfg = {"label": "End Type One: ", "layout": "horizontal"}
        self.line_end_one_type_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_end_one_type_select)
        cfg = {"label": "End Type Two: ", "layout": "horizontal"}
        self.line_end_two_type_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_end_two_type_select)
        group.set_height(group_layout.sizeHint().height())
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdPolygonToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdLineToolPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Polygon Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = True
        cfg["collapsed"] = True
        group = NchantdGroup(self, cfg)
        group_layout = pyqt.QVBoxLayout()
        group.setLayout(group_layout)
        cfg = {"label": "Line Style: ", "layout": "horizontal", "options": ["Solid", "Dashed", "Dotted", "Dash Dotted"]}
        self.line_style_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_style_select)
        cfg = {"label": "Thickness: ", "layout": "horizontal"}
        self.line_thickness_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        group_layout.addWidget(self.line_thickness_spin)
        cfg = {"label": "Color: ", "layout": "horizontal"}
        self.line_color_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_color_select)
        group.set_height(group_layout.sizeHint().height())
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdCircleToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdLineToolPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Circle Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = True
        cfg["collapsed"] = True
        group = NchantdGroup(self, cfg)
        group_layout = pyqt.QVBoxLayout()
        group.setLayout(group_layout)
        cfg = {"label": "Line Style: ", "layout": "horizontal", "options": ["Solid", "Dashed", "Dotted", "Dash Dotted"]}
        self.line_style_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_style_select)
        cfg = {"label": "Thickness: ", "layout": "horizontal"}
        self.line_thickness_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        group_layout.addWidget(self.line_thickness_spin)
        cfg = {"label": "Color: ", "layout": "horizontal"}
        self.line_color_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_color_select)
        group.set_height(group_layout.sizeHint().height())
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdObjectToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdLineToolPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Object Tool"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = True
        cfg["collapsed"] = True
        group = NchantdGroup(self, cfg)
        group_layout = pyqt.QVBoxLayout()
        group.setLayout(group_layout)
        cfg = {"label": "Color: ", "layout": "horizontal"}
        self.line_color_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_color_select)
        group.set_height(group_layout.sizeHint().height())
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdFillToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdLineToolPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Fill Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = True
        cfg["collapsed"] = True
        group = NchantdGroup(self, cfg)
        group_layout = pyqt.QVBoxLayout()
        group.setLayout(group_layout)
        cfg = {"label": "Color: ", "layout": "horizontal"}
        self.line_color_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_color_select)
        group.set_height(group_layout.sizeHint().height())
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeSketch(NchantdOfficeDocument):
    """
    Diagram editor to create a directed graph with nodes and edges.
    """

    def __init__(self, parent=None, cfg=None):
        """"""
        super().__init__("NchantdOfficeSketch", parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeSketch"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.canvas = None
        self.layers = None
        self.setMouseTracking(True)
        # Variables to store the start and end points of the line
        self.start_point = None
        self.end_point = None
        self.drawing = False  # Flag to indicate whether drawing is in progress

    def initModel(self):
        """"""
        super().initModel()
        cfg = {}
        self.document = self.app.model.codex.init_sketch(cfg)
        self.document.load_document()
        self.context_menu_name = "context.document.sketch"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        self.layers = self.get_layers()
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["buttons"] = {}
        cfg["buttons"][10] = {"action": "add_1d_line", "handler": self.cmd_add_1d_line}
        cfg["buttons"][11] = {"action": "add_1d_curve", "handler": self.cmd_add_1d_curve}
        cfg["buttons"][12] = {"action": "add_1d_spline", "handler": self.cmd_add_1d_spline}
        cfg["buttons"][13] = {"action": "add_2d_polygon", "handler": self.cmd_add_2d_polygon}
        cfg["buttons"][14] = {"action": "add_2d_ellipse", "handler": self.cmd_add_2d_ellipse}
        cfg["buttons"][15] = {"action": "insert_object", "handler": self.cmd_insert_object}
        cfg["buttons"][16] = {"action": "fill_color", "handler": self.cmd_fill_color}
        cfg["buttons"][49] = "_insert_stretch"
        super().initView(cfg)
        cfg = {"size": ["auto", self.size().height() + self.parent.size().height()]}
        self.canvas = NchantdCanvas(self, cfg).initWidget()
        self.canvas.setSizePolicy(pyqt.QSizePolicy.Expanding, pyqt.QSizePolicy.MinimumExpanding)
        self.layout.addWidget(self.canvas)
        # self.setSizePolicy(pyqt.QSizePolicy.Expanding, pyqt.QSizePolicy.Expanding)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_add_1d_line(self, checked=None, handler=None, params=None):
        """"""
        return self

    def cmd_add_1d_curve(self, checked=None, handler=None, params=None):
        """"""
        return self

    def cmd_add_1d_spline(self, checked=None, handler=None, params=None):
        """"""
        return self

    def cmd_add_2d_polygon(self, checked=None, handler=None, params=None):
        """"""
        return self

    def cmd_add_2d_ellipse(self, checked=None, handler=None, params=None):
        """"""
        return self

    def cmd_insert_object(self, checked=None, handler=None, params=None):
        """"""
        return self

    def cmd_fill_color(self, checked=None, handler=None, params=None):
        """"""
        return self

    def cmd_launch_color_sigil(self, event, *args, **kwargs):
        """"""
        cfg = {}
        self.color_sigil = NchantdColorSelectSigil(self, cfg).initWidget()
        return self

    def cmd_set_layer_name(self):
        """"""
        return self

    def cmd_set_layer_transparency(self):
        """"""
        return self

    def cmd_set_layer_color(self):
        """"""
        return self

    def cmd_set_layer_size(self):
        """"""
        return self

    def get_layers(self):
        """"""
        layers = self.layers
        if layers is None:
            layers = None  # self.app.model.store.get_document(self.did)
        if layers is None:
            layers = ["Layer 0 - Canvas Layer"]
        self.layers = layers
        if "New Layer" not in layers:
            layers += ["New Layer"]
        return layers

    def get_canvas_color(self):
        """"""

    def get_canvas_colors(self):
        options = ["Black", "Grey", "White", "Blue", "Red", "Green", "Yellow", "Magenta", "Cyan", "Orange", "Violet"]
        return options

    def get_canvas_size(self):
        """"""
        return self

    def init_canvas_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        cfg = {
            "text": "Canvas Color",
            "layout": "horizontal",
            "handler": self.cmd_launch_color_sigil,
        }
        self.canvas_color_sigil_button = NchantdButton(self, cfg)
        items[cnt]["widget"] = self.canvas_color_sigil_button
        cnt += 1
        cfg = {"label": "Canvas Size", "layout": "horizontal"}
        self.canvas_size_set = NchantdLabeledDoubleSpinBox(self, cfg)
        items[cnt]["widget"] = self.canvas_size_set
        cnt += 1
        self.get_layers()
        cfg = {
            "label": "Active Layer",
            "layout": "horizontal",
            "options": self.layers,
        }
        self.canvas_layer_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.canvas_layer_select
        cnt += 1
        cfg = {"layout": "horizontal", "data": self.layers}
        logma.info(f"Layers {self.layers}")
        self.layers_list_pane = NchantdLayersListPane(self, cfg)
        items[cnt]["widget"] = self.layers_list_pane
        cnt += 1
        cfg = {"layout": "horizontal"}
        self.layers_select = NchantdEditLayerPane(self, cfg)
        items[cnt]["widget"] = self.layers_select
        cnt += 1
        return items

    def init_sketch_tools(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Line Tool",
            "layout": "horizontal",
            "actions": self.config.dikt.get("buttons", {}),
        }
        self.line_tools_group = NchantdLineToolPane(self, cfg)
        items[cnt]["widget"] = self.line_tools_group
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Curve Tool",
            "layout": "horizontal",
            "actions": self.config.dikt.get("buttons", {}),
        }
        self.curve_tool_pane = NchantdCurveToolPane(self, cfg)
        items[cnt]["widget"] = self.curve_tool_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Spline Tool",
            "layout": "horizontal",
            "actions": self.config.dikt.get("buttons", {}),
        }
        self.splineline_tool_pane = NchantdSplineToolPane(self, cfg)
        items[cnt]["widget"] = self.splineline_tool_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Polygon Tool",
            "layout": "horizontal",
            "actions": self.config.dikt.get("buttons", {}),
        }
        self.polygon_tool_pane = NchantdPolygonToolPane(self, cfg)
        items[cnt]["widget"] = self.polygon_tool_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Circle Tool",
            "layout": "horizontal",
            "actions": self.config.dikt.get("buttons", {}),
        }
        self.circle_tool_pane = NchantdCircleToolPane(self, cfg)
        items[cnt]["widget"] = self.circle_tool_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Insert Object: ",
            "layout": "horizontal",
            "actions": self.config.dikt.get("buttons", {}),
        }
        self.object_tool_pane = NchantdObjectToolPane(self, cfg)
        items[cnt]["widget"] = self.object_tool_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Fill Color: ",
            "layout": "horizontal",
            "actions": self.config.dikt.get("buttons", {}),
        }
        self.fill_tool_pane = NchantdFillToolPane(self, cfg)
        items[cnt]["widget"] = self.fill_tool_pane

        return items

    def init_object_config(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        cfg = {
            "label": "Select Canvas Color",
            "layout": "horizontal",
            "actions": self.config.dikt.get("buttons", {}),
        }
        self.new_object_group_pane = NchantdNewObjectPane(self, cfg)
        items[cnt]["widget"] = self.new_object_group_pane
        cnt += 1

        return items

    def init_drawer_quickstart(self):
        """"""
        items = self.toolbox_config[400].get("items", {})
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_canvas_config()
        self.toolbox_config[200]["items"] = self.init_sketch_tools()
        self.toolbox_config[300]["items"] = self.init_object_config()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def mousePressEvent(self, event):
        """"""
        if event.button() == pyqt.Qt.LeftButton:
            # Start drawing: record the starting point
            self.start_point = event.pos()
            self.end_point = self.start_point
            self.drawing = True
            self.update()  # Request a repaint

    def mouseMoveEvent(self, event):
        """"""
        if self.drawing and event.buttons() & pyqt.Qt.LeftButton:
            # While the mouse moves, update the endpoint dynamically
            self.end_point = event.pos()
            self.update()  # Request a repaint

    def mouseReleaseEvent(self, event):
        """"""
        if event.button() == pyqt.Qt.LeftButton:
            # Finish drawing: finalize the end point and disable drawing
            self.end_point = event.pos()
            self.drawing = False
            self.update()  # Request final repaint

    def new_layer(self, name=None):
        """"""
        if self.layers is None:
            self.get_layers()
        if name is None:
            name = f"Layer {len(self.layers)}"
        self.layers.append(f"{len(self.layers)}: {name}")

    def paintEvent(self, event):
        painter = pyqt.QPainter(self)
        painter.setRenderHint(pyqt.QPainter.Antialiasing)

        # Draw the line only if start and end points are defined
        if self.start_point and self.end_point:
            pen = pyqt.QPen(pyqt.Qt.black, 3)  # Set pen with black color and thickness 3
            painter.setPen(pen)
            painter.drawLine(self.start_point, self.end_point)


class NchantdOfficePalette(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Nchantd Palette", parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficePalette"))
        # if self.parent:
        #     self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        cfg = {}
        self.palette = NchantdPalette(self, cfg).initWidget()
        self.layout.addWidget(self.palette)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def init_content_selection(self):
        """"""
        items = {}
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        options = ["Black", "Grey", "White", "Blue", "Red", "Green", "Yellow", "Magenta", "Cyan", "Orange", "Violet"]
        cfg = {"label": "Select Canvas Color", "layout": "horizontal", "options": options}
        self.canvas_color_select = NchantdDropDown
        items[cnt]["widget"] = self.canvas_color_select
        return items

    def init_palette_tools(self):
        """"""
        items = {}
        return items

    def init_drawer_quickstart(self):
        """"""
        items = {}
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_content_selection()
        self.toolbox_config[200]["items"] = self.init_palette_tools()
        self.toolbox_config[300]["items"] = self.init_drawer_quickstart()


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
