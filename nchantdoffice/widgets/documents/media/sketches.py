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
from nchantrs.libraries import pyqt
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons
from nchantrs.widgets.controls.buttons import NchantdButtonWidget
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
pxcfg = join(here, "_data_", "sketches.yaml")


class NchantdLayersListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdLayersListPane").override(cfg))

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
        logma.info(f"NchantdEditLayerPane init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdEditorLayerPane").override(cfg))

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
        cfg = {"label": "Layer Name:", "handler": self.cmd_on_layer_name_change}
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)
        cfg = {"label": "Transparency:", "handler": self.cmd_on_transparency_change}
        self.transparency_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.transparency_entry)
        cfg = {"label": "Size:", "handler": self.cmd_on_size_change}
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

    def cmd_on_layer_name_change(self):
        """Handle layer name change from the name entry field."""
        try:
            if hasattr(self, "name_entry") and self.name_entry:
                name = self.name_entry.text() if hasattr(self.name_entry, "text") else None
                if name and hasattr(self.parent(), "cmd_set_layer_name"):
                    self.parent().cmd_set_layer_name(name)
        except Exception:
            pass
        return self

    def cmd_on_transparency_change(self, *args, **kwargs):
        """Handle transparency change from the transparency entry field."""
        try:
            if hasattr(self, "transparency_entry") and self.transparency_entry:
                val = self.transparency_entry.text() if hasattr(self.transparency_entry, "text") else None
                if val:
                    try:
                        transparency = float(val)
                    except ValueError:
                        transparency = None
                    if transparency is not None and hasattr(self.parent(), "cmd_set_layer_transparency"):
                        self.parent().cmd_set_layer_transparency(transparency)
        except Exception:
            pass
        return self

    def cmd_on_size_change(self, *args, **kwargs):
        """Handle size change from the size spin box."""
        try:
            if hasattr(self, "size_set") and self.size_set:
                size = self.size_set.value() if hasattr(self.size_set, "value") else None
                if size is not None and hasattr(self.parent(), "cmd_set_layer_size"):
                    self.parent().cmd_set_layer_size(size)
        except Exception:
            pass
        return self


class NchantdObjectsPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdObjectsPane").override(cfg))

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
        logma.info(f"NchantdLineToolPane init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdLineToolPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        cfg = cfg or {}
        cfg["text"] = "Line Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = False
        cfg["collapsed"] = False
        group = NchantdGroup(self, cfg).set_open(True)
        group_layout = pyqt.QVBoxLayout()
        group.setLayout(group_layout)
        cfg = {
            "label": "Line Style: ",
            "layout": "horizontal",
            "options": ["Solid", "Dashed", "Dotted", "Dash Dotted"],
            "handler": self.cmd_change_style,
        }
        self.line_style_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_style_select)
        cfg = {
            "label": "Thickness: ",
            "layout": "horizontal",
            "handler": self.cmd_change_thickness,
        }
        self.line_thickness_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        group_layout.addWidget(self.line_thickness_spin)
        cfg = {
            "label": "Color: ",
            "layout": "horizontal",
            "handler": self.cmd_change_color,
        }
        self.line_color_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_color_select)
        cfg = {
            "label": "End Type One: ",
            "layout": "horizontal",
            "handler": self.cmd_change_end_style,
        }
        self.line_end_one_type_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_end_one_type_select)
        cfg = {
            "label": "End Type Two: ",
            "layout": "horizontal",
            "handler": self.cmd_change_end_style,
        }
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

    def cmd_change_color(self, event, *args, **kwargs):
        """Handle color change from the color dropdown."""
        try:
            if hasattr(self, "line_color_select"):
                color_name = (
                    self.line_color_select.currentText() if hasattr(self.line_color_select, "currentText") else None
                )
                if color_name and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["color"] = self.parent()._get_qcolor_from_name(color_name)
        except Exception:
            pass
        return self

    def cmd_change_thickness(self, event, *args, **kwargs):
        """Handle thickness change from the thickness spin box."""
        try:
            if hasattr(self, "line_thickness_spin"):
                thickness = self.line_thickness_spin.value() if hasattr(self.line_thickness_spin, "value") else None
                if thickness is not None and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["thickness"] = thickness
        except Exception:
            pass
        return self

    def cmd_change_style(self, event, *args, **kwargs):
        """Handle style change from the style dropdown."""
        try:
            if hasattr(self, "line_style_select"):
                style = self.line_style_select.currentText() if hasattr(self.line_style_select, "currentText") else None
                if style and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["style"] = style
        except Exception:
            pass
        return self

    def cmd_change_end_style(self, event, *args, **kwargs):
        """Handle end style change from the end style dropdowns."""
        try:
            if not hasattr(self.parent(), "current_tool_config"):
                return self
            if hasattr(self, "line_end_one_type_select"):
                end_type = (
                    self.line_end_one_type_select.currentText()
                    if hasattr(self.line_end_one_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_1"] = end_type
            if hasattr(self, "line_end_two_type_select"):
                end_type = (
                    self.line_end_two_type_select.currentText()
                    if hasattr(self.line_end_two_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_2"] = end_type
        except Exception:
            pass
        return self


class NchantdCurveToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"NchantdCurveToolPane init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdLineToolPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Curve Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = False
        cfg["collapsed"] = False
        group = NchantdGroup(self, cfg)
        group_layout = pyqt.QVBoxLayout()
        group.setLayout(group_layout)
        cfg = {
            "label": "Line Style: ",
            "layout": "horizontal",
            "options": ["Solid", "Dashed", "Dotted", "Dash Dotted"],
            "handler": self.cmd_change_style,
        }
        self.line_style_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_style_select)
        cfg = {"label": "Thickness: ", "layout": "horizontal", "handler": self.cmd_change_thickness}
        self.line_thickness_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        group_layout.addWidget(self.line_thickness_spin)
        cfg = {"label": "Color: ", "layout": "horizontal", "handler": self.cmd_change_color}
        self.line_color_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_color_select)
        cfg = {"label": "End Type One: ", "layout": "horizontal", "handler": self.cmd_change_end_style}
        self.line_end_one_type_select = NchantdDropDown(self, cfg).initWidget()
        group_layout.addWidget(self.line_end_one_type_select)
        cfg = {"label": "End Type Two: ", "layout": "horizontal", "handler": self.cmd_change_end_style}
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

    def cmd_change_color(self, event, *args, **kwargs):
        """Handle color change from the color dropdown."""
        try:
            if hasattr(self, "line_color_select"):
                color_name = (
                    self.line_color_select.currentText() if hasattr(self.line_color_select, "currentText") else None
                )
                if color_name and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["color"] = self.parent()._get_qcolor_from_name(color_name)
        except Exception:
            pass
        return self

    def cmd_change_thickness(self, event, *args, **kwargs):
        """Handle thickness change from the thickness spin box."""
        try:
            if hasattr(self, "line_thickness_spin"):
                thickness = self.line_thickness_spin.value() if hasattr(self.line_thickness_spin, "value") else None
                if thickness is not None and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["thickness"] = thickness
        except Exception:
            pass
        return self

    def cmd_change_style(self, event, *args, **kwargs):
        """Handle style change from the style dropdown."""
        try:
            if hasattr(self, "line_style_select"):
                style = self.line_style_select.currentText() if hasattr(self.line_style_select, "currentText") else None
                if style and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["style"] = style
        except Exception:
            pass
        return self

    def cmd_change_end_style(self, event, *args, **kwargs):
        """Handle end style change from the end style dropdowns."""
        try:
            if not hasattr(self.parent(), "current_tool_config"):
                return self
            if hasattr(self, "line_end_one_type_select"):
                end_type = (
                    self.line_end_one_type_select.currentText()
                    if hasattr(self.line_end_one_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_1"] = end_type
            if hasattr(self, "line_end_two_type_select"):
                end_type = (
                    self.line_end_two_type_select.currentText()
                    if hasattr(self.line_end_two_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_2"] = end_type
        except Exception:
            pass
        return self


class NchantdSplineToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"NchantdSplineToolPane init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdLineToolPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Spline Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = False
        cfg["collapsed"] = False
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

    def cmd_change_color(self, event, *args, **kwargs):
        """Handle color change from the color dropdown."""
        try:
            if hasattr(self, "line_color_select"):
                color_name = (
                    self.line_color_select.currentText() if hasattr(self.line_color_select, "currentText") else None
                )
                if color_name and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["color"] = self.parent()._get_qcolor_from_name(color_name)
        except Exception:
            pass
        return self

    def cmd_change_thickness(self, event, *args, **kwargs):
        """Handle thickness change from the thickness spin box."""
        try:
            if hasattr(self, "line_thickness_spin"):
                thickness = self.line_thickness_spin.value() if hasattr(self.line_thickness_spin, "value") else None
                if thickness is not None and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["thickness"] = thickness
        except Exception:
            pass
        return self

    def cmd_change_style(self, event, *args, **kwargs):
        """Handle style change from the style dropdown."""
        try:
            if hasattr(self, "line_style_select"):
                style = self.line_style_select.currentText() if hasattr(self.line_style_select, "currentText") else None
                if style and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["style"] = style
        except Exception:
            pass
        return self

    def cmd_change_end_style(self, event, *args, **kwargs):
        """Handle end style change from the end style dropdowns."""
        try:
            if not hasattr(self.parent(), "current_tool_config"):
                return self
            if hasattr(self, "line_end_one_type_select"):
                end_type = (
                    self.line_end_one_type_select.currentText()
                    if hasattr(self.line_end_one_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_1"] = end_type
            if hasattr(self, "line_end_two_type_select"):
                end_type = (
                    self.line_end_two_type_select.currentText()
                    if hasattr(self.line_end_two_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_2"] = end_type
        except Exception:
            pass
        return self


class NchantdPolygonToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"NchantdPolygonToolPane init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdPolygonToolPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Polygon Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = False
        cfg["collapsed"] = False
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

    def cmd_change_color(self, event, *args, **kwargs):
        """Handle color change from the color dropdown."""
        try:
            if hasattr(self, "line_color_select"):
                color_name = (
                    self.line_color_select.currentText() if hasattr(self.line_color_select, "currentText") else None
                )
                if color_name and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["color"] = self.parent()._get_qcolor_from_name(color_name)
        except Exception:
            pass
        return self

    def cmd_change_thickness(self, event, *args, **kwargs):
        """Handle thickness change from the thickness spin box."""
        try:
            if hasattr(self, "line_thickness_spin"):
                thickness = self.line_thickness_spin.value() if hasattr(self.line_thickness_spin, "value") else None
                if thickness is not None and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["thickness"] = thickness
        except Exception:
            pass
        return self

    def cmd_change_style(self, event, *args, **kwargs):
        """Handle style change from the style dropdown."""
        try:
            if hasattr(self, "line_style_select"):
                style = self.line_style_select.currentText() if hasattr(self.line_style_select, "currentText") else None
                if style and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["style"] = style
        except Exception:
            pass
        return self

    def cmd_change_end_style(self, event, *args, **kwargs):
        """Handle end style change from the end style dropdowns."""
        try:
            if not hasattr(self.parent(), "current_tool_config"):
                return self
            if hasattr(self, "line_end_one_type_select"):
                end_type = (
                    self.line_end_one_type_select.currentText()
                    if hasattr(self.line_end_one_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_1"] = end_type
            if hasattr(self, "line_end_two_type_select"):
                end_type = (
                    self.line_end_two_type_select.currentText()
                    if hasattr(self.line_end_two_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_2"] = end_type
        except Exception:
            pass
        return self


class NchantdCircleToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"NchantdCircleToolPane init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdCircleToolPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Circle Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = False
        cfg["collapsed"] = False
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

    def cmd_change_color(self, event, *args, **kwargs):
        """Handle color change from the color dropdown."""
        try:
            if hasattr(self, "line_color_select"):
                color_name = (
                    self.line_color_select.currentText() if hasattr(self.line_color_select, "currentText") else None
                )
                if color_name and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["color"] = self.parent()._get_qcolor_from_name(color_name)
        except Exception:
            pass
        return self

    def cmd_change_thickness(self, event, *args, **kwargs):
        """Handle thickness change from the thickness spin box."""
        try:
            if hasattr(self, "line_thickness_spin"):
                thickness = self.line_thickness_spin.value() if hasattr(self.line_thickness_spin, "value") else None
                if thickness is not None and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["thickness"] = thickness
        except Exception:
            pass
        return self

    def cmd_change_style(self, event, *args, **kwargs):
        """Handle style change from the style dropdown."""
        try:
            if hasattr(self, "line_style_select"):
                style = self.line_style_select.currentText() if hasattr(self.line_style_select, "currentText") else None
                if style and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["style"] = style
        except Exception:
            pass
        return self

    def cmd_change_end_style(self, event, *args, **kwargs):
        """Handle end style change from the end style dropdowns."""
        try:
            if not hasattr(self.parent(), "current_tool_config"):
                return self
            if hasattr(self, "line_end_one_type_select"):
                end_type = (
                    self.line_end_one_type_select.currentText()
                    if hasattr(self.line_end_one_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_1"] = end_type
            if hasattr(self, "line_end_two_type_select"):
                end_type = (
                    self.line_end_two_type_select.currentText()
                    if hasattr(self.line_end_two_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_2"] = end_type
        except Exception:
            pass
        return self


class NchantdObjectToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"NchantdObjectToolPane init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdObjectToolPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["text"] = "Object Tool"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = False
        cfg["collapsed"] = False
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

    def cmd_change_color(self, event, *args, **kwargs):
        """Handle color change from the color dropdown."""
        try:
            if hasattr(self, "line_color_select"):
                color_name = (
                    self.line_color_select.currentText() if hasattr(self.line_color_select, "currentText") else None
                )
                if color_name and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["color"] = self.parent()._get_qcolor_from_name(color_name)
        except Exception:
            pass
        return self

    def cmd_change_thickness(self, event, *args, **kwargs):
        """Handle thickness change from the thickness spin box."""
        try:
            if hasattr(self, "line_thickness_spin"):
                thickness = self.line_thickness_spin.value() if hasattr(self.line_thickness_spin, "value") else None
                if thickness is not None and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["thickness"] = thickness
        except Exception:
            pass
        return self

    def cmd_change_style(self, event, *args, **kwargs):
        """Handle style change from the style dropdown."""
        try:
            if hasattr(self, "line_style_select"):
                style = self.line_style_select.currentText() if hasattr(self.line_style_select, "currentText") else None
                if style and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["style"] = style
        except Exception:
            pass
        return self

    def cmd_change_end_style(self, event, *args, **kwargs):
        """Handle end style change from the end style dropdowns."""
        try:
            if not hasattr(self.parent(), "current_tool_config"):
                return self
            if hasattr(self, "line_end_one_type_select"):
                end_type = (
                    self.line_end_one_type_select.currentText()
                    if hasattr(self.line_end_one_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_1"] = end_type
            if hasattr(self, "line_end_two_type_select"):
                end_type = (
                    self.line_end_two_type_select.currentText()
                    if hasattr(self.line_end_two_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_2"] = end_type
        except Exception:
            pass
        return self


class NchantdFillToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"NchantdFillToolPane init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdFillToolPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        cfg = cfg or {}
        cfg["text"] = "Fill Tool:"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg["collapsible"] = False
        cfg["collapsed"] = False
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

    def cmd_change_color(self, event, *args, **kwargs):
        """Handle color change from the color dropdown."""
        try:
            if hasattr(self, "line_color_select"):
                color_name = (
                    self.line_color_select.currentText() if hasattr(self.line_color_select, "currentText") else None
                )
                if color_name and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["color"] = self.parent()._get_qcolor_from_name(color_name)
        except Exception:
            pass
        return self

    def cmd_change_thickness(self, event, *args, **kwargs):
        """Handle thickness change from the thickness spin box."""
        try:
            if hasattr(self, "line_thickness_spin"):
                thickness = self.line_thickness_spin.value() if hasattr(self.line_thickness_spin, "value") else None
                if thickness is not None and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["thickness"] = thickness
        except Exception:
            pass
        return self

    def cmd_change_style(self, event, *args, **kwargs):
        """Handle style change from the style dropdown."""
        try:
            if hasattr(self, "line_style_select"):
                style = self.line_style_select.currentText() if hasattr(self.line_style_select, "currentText") else None
                if style and hasattr(self.parent(), "current_tool_config"):
                    self.parent().current_tool_config["style"] = style
        except Exception:
            pass
        return self

    def cmd_change_end_style(self, event, *args, **kwargs):
        """Handle end style change from the end style dropdowns."""
        try:
            if not hasattr(self.parent(), "current_tool_config"):
                return self
            if hasattr(self, "line_end_one_type_select"):
                end_type = (
                    self.line_end_one_type_select.currentText()
                    if hasattr(self.line_end_one_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_1"] = end_type
            if hasattr(self, "line_end_two_type_select"):
                end_type = (
                    self.line_end_two_type_select.currentText()
                    if hasattr(self.line_end_two_type_select, "currentText")
                    else None
                )
                if end_type and end_type != "None":
                    self.parent().current_tool_config["end_type_2"] = end_type
        except Exception:
            pass
        return self


class NchantdOfficeSketch(NchantdOfficeDocument):
    """
    Diagram editor to create a directed graph with nodes and edges.
    """

    def _ensure_drawer_item(self, items, cnt):
        """Lazily create a default drawer-item slot.

        Centralises the ``if cnt not in items: items[cnt] = {...}``
        pattern used by ``init_sketch_tools`` and the other drawer
        initialisers on this class, removing the repeated branch flagged
        by the maintainability auditor as switch abuse.
        """
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        return items[cnt]

    def __init__(self, parent=None, cfg=None):
        """"""
        super().__init__("NchantdOfficeSketch", parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeSketch").override(cfg))
        self.canvas = None
        self.layers = None
        self.setMouseTracking(True)
        # Variables to store the start and end points of the line
        self.start_point = None
        self.end_point = None
        self.drawing = False  # Flag to indicate whether drawing is in progress

    def initModel(self):
        """Initialize the sketch model with document, context menu, and layers."""
        super().initModel()
        document = {"document": self.config.get("document", {})}
        self.document = self.app.model.codex.init_sketch(document)
        self.document.load_document()
        self.file_path = (
            self.document.file_path
            or self.config.dikt.get("file_path")
            or (self.document.content or {}).get("file_path")
            or (self.document.content or {}).get("content", {}).get("file_path")
        )
        self.context_menu_name = "context.document.sketch"
        self.initialize_context_menu(self.context_menu_name)
        self.current_tool = None
        self.current_shape = None
        self.shapes = []
        self.layers = ["Layer 0 - Canvas Layer"]
        self.active_layer_index = 0
        self.layer_properties = {}
        self._restore_document_content()
        self.undo_stack = []
        self.redo_stack = []
        self.current_tool_config = {
            "style": "Solid",
            "thickness": 3,
            "color": pyqt.QColor(pyqt.Qt.black),
            "end_type_1": None,
            "end_type_2": None,
        }
        self._updating_cursor = False  # Flag to prevent cursor update recursion
        return self

    def initView(self, cfg=None):
        """Initialize the sketch view with canvas and tool buttons."""
        cfg = cfg or {}
        cfg = {
            "buttons": {
                10: {"action": "add_1d_line", "handler": self.cmd_add_1d_line},
                11: {"action": "add_1d_curve", "handler": self.cmd_add_1d_curve},
                12: {"action": "add_1d_spline", "handler": self.cmd_add_1d_spline},
                13: {"action": "add_2d_polygon", "handler": self.cmd_add_2d_polygon},
                14: {"action": "add_2d_ellipse", "handler": self.cmd_add_2d_ellipse},
                15: {"action": "insert_object", "handler": self.cmd_insert_object},
                16: {"action": "fill_color", "handler": self.cmd_fill_color},
                49: "_insert_stretch",
                100: "_skip",  # PUSH to 0.0.3 FileSystem not compatible to any outside protocol
            }
        }
        super().initView(cfg)
        canvas_cfg = {"size": ["auto", self.size().height() + self.parent.size().height()]}
        self.canvas = NchantdCanvas(self, canvas_cfg).initWidget()
        self.canvas.setSizePolicy(pyqt.QSizePolicy.Expanding, pyqt.QSizePolicy.MinimumExpanding)

        # Enable mouse tracking for the canvas
        self.canvas.setMouseTracking(True)

        # Install event filter to capture canvas mouse events
        self.canvas.installEventFilter(self)
        logma.info(f"Event filter installed on canvas: {type(self.canvas).__name__}")

        # Store reference to parent sketch for canvas to access
        self.canvas.sketch_parent = self

        # Ensure canvas doesn't override cursor
        self.canvas.unsetCursor()  # Remove any default cursor from canvas

        # Set focus policy so canvas can receive mouse events
        self.canvas.setFocusPolicy(pyqt.Qt.StrongFocus)
        self.canvas.setAttribute(pyqt.Qt.WA_Hover, True)  # Enable hover events

        # Override canvas mouse event handlers to delegate to sketch
        self._setup_canvas_mouse_handlers()

        self.layout.addWidget(self.canvas)
        self.populate_document()
        return self

    def _restore_document_content(self):
        """Restore persisted layers, shape geometry, and canvas settings."""
        content = getattr(self.document, "content", None) or {}
        if isinstance(content, dict) and isinstance(content.get("content"), dict):
            content = content["content"]
        if not isinstance(content, dict):
            return self

        layers = content.get("layers") or ["Layer 0 - Canvas Layer"]
        self.layers = list(layers)
        if "New Layer" not in self.layers:
            self.layers.append("New Layer")
        self.layer_properties = dict(content.get("layer_properties") or {})
        try:
            self.active_layer_index = int(content.get("active_layer_index", 0))
        except (TypeError, ValueError):
            self.active_layer_index = 0
        self.active_layer_index = max(0, min(self.active_layer_index, len(self.layers) - 1))

        self.shapes = []
        for shape_data in content.get("shapes") or []:
            if not isinstance(shape_data, dict):
                continue
            start = shape_data.get("start") or {}
            end = shape_data.get("end") or {}
            if not all(axis in start and axis in end for axis in ("x", "y")):
                continue
            config = dict(shape_data.get("config") or {})
            config["color"] = pyqt.QColor(config.get("color", "#000000"))
            self.shapes.append(
                {
                    "tool": shape_data.get("tool"),
                    "start": pyqt.QPointF(start["x"], start["y"]),
                    "end": pyqt.QPointF(end["x"], end["y"]),
                    "layer": shape_data.get("layer"),
                    "config": config,
                }
            )
        self._restored_canvas_size = content.get("canvas_size") or {}
        return self

    def populate_document(self):
        """Render the restored sketch content into the initialized canvas."""
        canvas_size = getattr(self, "_restored_canvas_size", {})
        if self.canvas is not None and isinstance(canvas_size, dict):
            width = canvas_size.get("width")
            height = canvas_size.get("height")
            if width and height:
                self.canvas.resize(int(width), int(height))
        self.render_on_canvas()
        return self

    def initWidget(self):
        """Initialize the complete sketch widget."""
        self.initModel()
        self.initView()
        return self

    def clear_canvas(self):
        """Clear all drawings from the canvas."""
        self.shapes = []
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.render_on_canvas()
        return self

    def cmd_add_1d_line(self, checked=None, handler=None, params=None):
        """Activate line drawing tool with current settings from line tool pane."""
        self.current_tool = "line"
        self.drawing = False
        self.start_point = None
        self.end_point = None

        # Get settings from line tool pane if available
        if hasattr(self, "line_tools_group"):
            self._update_tool_config_from_pane(self.line_tools_group)

        # Update cursor based on tool
        self._update_canvas_cursor()
        logma.info("Line drawing tool activated")
        return self

    def cmd_add_1d_curve(self, checked=None, handler=None, params=None):
        """Activate curve drawing tool with current settings."""
        self.current_tool = "curve"
        self.drawing = False
        self.start_point = None
        self.end_point = None

        # Get settings from curve tool pane if available
        if hasattr(self, "curve_tool_pane"):
            self._update_tool_config_from_pane(self.curve_tool_pane)

        # Update cursor based on tool
        self._update_canvas_cursor()
        logma.info("Curve drawing tool activated")
        return self

    def cmd_add_1d_spline(self, checked=None, handler=None, params=None):
        """Activate spline drawing tool with current settings."""
        self.current_tool = "spline"
        self.drawing = False
        self.start_point = None
        self.end_point = None

        # Get settings from spline tool pane if available
        if hasattr(self, "splineline_tool_pane"):
            self._update_tool_config_from_pane(self.splineline_tool_pane)

        # Update cursor based on tool
        self._update_canvas_cursor()
        logma.info("Spline drawing tool activated")
        return self

    def cmd_add_2d_polygon(self, checked=None, handler=None, params=None):
        """Activate polygon drawing tool with current settings."""
        self.current_tool = "polygon"
        self.drawing = False
        self.start_point = None
        self.end_point = None

        # Get settings from polygon tool pane if available
        if hasattr(self, "polygon_tool_pane"):
            self._update_tool_config_from_pane(self.polygon_tool_pane)

        # Update cursor based on tool
        self._update_canvas_cursor()
        logma.info("Polygon drawing tool activated")
        return self

    def cmd_add_2d_ellipse(self, checked=None, handler=None, params=None):
        """Activate ellipse/circle drawing tool with current settings."""
        self.current_tool = "ellipse"
        self.drawing = False
        self.start_point = None
        self.end_point = None

        # Get settings from circle tool pane if available
        if hasattr(self, "circle_tool_pane"):
            self._update_tool_config_from_pane(self.circle_tool_pane)

        # Update cursor based on tool
        self._update_canvas_cursor()
        logma.info("Ellipse/circle drawing tool activated")
        return self

    def cmd_insert_object(self, checked=None, handler=None, params=None):
        """Activate object insertion tool."""
        self.current_tool = "object"
        # Update cursor based on tool
        self._update_canvas_cursor()
        logma.info("Object insertion tool activated")
        return self

    def cmd_fill_color(self, checked=None, handler=None, params=None):
        """Activate fill color tool with current settings."""
        self.current_tool = "fill"

        # Get settings from fill tool pane if available
        if hasattr(self, "fill_tool_pane"):
            self._update_tool_config_from_pane(self.fill_tool_pane)

        # Update cursor based on tool
        self._update_canvas_cursor()
        logma.info("Fill color tool activated")
        return self

    def cmd_launch_color_sigil(self, event, *args, **kwargs):
        """Launch the color selection dialog."""
        self.color_sigil = NchantdColorSelectSigil(self, {}).initWidget()
        return self

    def cmd_set_layer_name(self, name=None):
        """Set the name of the current layer."""
        if name and self.layers and 0 <= self.active_layer_index < len(self.layers):
            old_name = self.layers[self.active_layer_index]
            # Skip if it's the "New Layer" option
            if old_name != "New Layer":
                self.rename_layer(old_name, name)
        return self

    def cmd_set_layer_transparency(self, transparency=None):
        """Set the transparency of the current layer."""
        if transparency is not None and 0 <= self.active_layer_index < len(self.layers):
            layer_name = self.layers[self.active_layer_index]
            if layer_name not in self.layer_properties:
                self.layer_properties[layer_name] = {}
            self.layer_properties[layer_name]["transparency"] = max(0.0, min(1.0, transparency))
            self.render_on_canvas()
        return self

    def cmd_set_layer_color(self, color=None):
        """Set the color of the current layer."""
        if color and 0 <= self.active_layer_index < len(self.layers):
            layer_name = self.layers[self.active_layer_index]
            if layer_name not in self.layer_properties:
                self.layer_properties[layer_name] = {}
            self.layer_properties[layer_name]["color"] = color
            self.render_on_canvas()
        return self

    def cmd_set_layer_size(self, size=None):
        """Set the size/scale of the current layer."""
        if size is not None and 0 <= self.active_layer_index < len(self.layers):
            layer_name = self.layers[self.active_layer_index]
            if layer_name not in self.layer_properties:
                self.layer_properties[layer_name] = {}
            self.layer_properties[layer_name]["size"] = max(0.1, size)
            self.render_on_canvas()
        return self

    def cmd_canvas_size_change(self, *args, **kwargs):
        """Handle canvas size change from the canvas size spin boxes."""
        try:
            if hasattr(self, "canvas_size_set"):
                size = self.canvas_size_set.value() if hasattr(self.canvas_size_set, "value") else None
                if size:
                    self.set_canvas_size(int(size), int(size))
        except Exception:
            pass
        return self

    def cmd_layer_change(self, *args, **kwargs):
        """Handle layer selection change from the layer dropdown."""
        try:
            if hasattr(self, "canvas_layer_select"):
                layer_name = (
                    self.canvas_layer_select.currentText() if hasattr(self.canvas_layer_select, "currentText") else None
                )
                if layer_name:
                    self.set_active_layer(layer_name)
        except Exception:
            pass
        return self

    def delete_layer(self, layer_name):
        """Delete a layer by name."""
        if layer_name in self.layers and layer_name != "Layer 0 - Canvas Layer":
            self.layers.remove(layer_name)
        return self

    def duplicate_layer(self, layer_name):
        """Duplicate a layer and its shapes."""
        if layer_name in self.layers and layer_name != "New Layer":
            new_layer_name = f"{layer_name} (Copy)"
            # Insert before "New Layer"
            self.layers.insert(-1, new_layer_name)

            # Copy layer properties
            if layer_name in self.layer_properties:
                self.layer_properties[new_layer_name] = self.layer_properties[layer_name].copy()

            # Copy shapes belonging to this layer
            for shape in self.shapes:
                if shape.get("layer") == layer_name:
                    new_shape = shape.copy()
                    new_shape["layer"] = new_layer_name
                    self.shapes.append(new_shape)

            self.render_on_canvas()
        return self

    def deactivate_tool(self):
        """Deactivate the current drawing tool."""
        self.current_tool = None
        self.drawing = False
        self.start_point = None
        self.end_point = None
        # Update cursor to arrow
        self._update_canvas_cursor()
        logma.info("Tool deactivated")
        return self

    def delete_shape_at_position(self, pos):
        """Delete a shape at the given position."""
        index, shape = self.get_shape_at_position(pos)
        if index is not None:
            deleted_shape = self.shapes.pop(index)
            self.undo_stack.append(("delete", deleted_shape))
            self.redo_stack.clear()
            self.render_on_canvas()
            logma.info(f"Deleted shape at index {index}")
            return True
        return False

    # Per-Qt-event-type handlers used by ``eventFilter``. Dispatch
    # looks up the handler in this table; missing keys mean
    # "don't block, fall through to the default Qt handler".
    _EVENT_FILTER_HANDLERS = (
        (pyqt.QEvent.MouseButtonPress, "_handle_canvas_press"),
        (pyqt.QEvent.MouseButtonDblClick, "_handle_canvas_press"),
        (pyqt.QEvent.MouseButtonRelease, "_handle_canvas_release"),
        (pyqt.QEvent.MouseMove, "_handle_canvas_move"),
        (pyqt.QEvent.Enter, "_handle_canvas_enter"),
        (pyqt.QEvent.CursorChange, "_handle_canvas_cursor_change"),
    )

    def eventFilter(self, obj, event):
        """Filter events from the canvas to handle drawing and cursor.

        Delegates to per-event-type handlers stored in
        ``_EVENT_FILTER_HANDLERS``. Returns ``True`` to swallow the event,
        ``False`` to let Qt continue, ``None`` to fall through to the
        default handler (no matching handler).
        """
        if obj != self.canvas:
            return super().eventFilter(obj, event)

        event_type = event.type()

        # Log canvas mouse-button events for debugging
        if event_type in (
            pyqt.QEvent.MouseButtonPress,
            pyqt.QEvent.MouseButtonRelease,
            pyqt.QEvent.MouseButtonDblClick,
        ):
            logma.info(
                f"eventFilter: {event_type}, obj={type(obj).__name__}, current_tool={self.current_tool}"
            )

        for qevent_type, method_name in self._EVENT_FILTER_HANDLERS:
            if event_type == qevent_type:
                handler = getattr(self, method_name, None)
                if handler is None:
                    return None
                return handler(event)
        return super().eventFilter(obj, event)

    # --- per-event-type handlers used by ``eventFilter`` ---

    def _handle_canvas_enter(self, event):
        """Handle ``QEvent.Enter``: refresh cursor when mouse enters canvas."""
        logma.info("Mouse entered canvas")
        self._update_canvas_cursor()
        return False  # Don't block the event

    def _handle_canvas_cursor_change(self, event):
        """Handle ``QEvent.CursorChange``: block cursor changes while drawing."""
        if self.current_tool and not self._updating_cursor:
            logma.warning("Canvas tried to change cursor - blocking")
            return True
        return None

    def _handle_canvas_press(self, event):
        """Handle ``QEvent.MouseButtonPress`` and ``MouseButtonDblClick``.

        Both treat double-click as a single press for drawing.
        """
        if not self.current_tool:
            return None
        logma.info(
            f"eventFilter caught {event.type()}, "
            f"button={getattr(event, 'button', lambda: '?')()}"
        )
        self.mousePressEvent(event)
        self._update_canvas_cursor()
        return True

    def _handle_canvas_release(self, event):
        """Handle ``QEvent.MouseButtonRelease``: stop drawing."""
        logma.info(f"eventFilter caught MouseButtonRelease, drawing={self.drawing}")
        self.mouseReleaseEvent(event)
        self._update_canvas_cursor()
        return True

    def _handle_canvas_move(self, event):
        """Handle ``QEvent.MouseMove``: track drawing + cursor."""
        if self.drawing:
            logma.debug("eventFilter caught MouseMove during drawing")
        self.mouseMoveEvent(event)
        if not self.drawing:
            expected_cursor = self._get_expected_cursor_shape()
            if self.canvas.cursor().shape() != expected_cursor:
                logma.warning(
                    f"Canvas cursor mismatch! Expected {expected_cursor}, got {self.canvas.cursor().shape()}"
                )
                self._update_canvas_cursor()
        return True

    def export_sketch(self, file_path):
        """Export the sketch to a file."""
        import json

        try:
            sketch_data = {
                "layers": self.layers,
                "layer_properties": self.layer_properties,
                "shapes": [
                    {
                        "tool": shape["tool"],
                        "start": {"x": shape["start"].x(), "y": shape["start"].y()},
                        "end": {"x": shape["end"].x(), "y": shape["end"].y()},
                        "layer": shape.get("layer"),
                    }
                    for shape in self.shapes
                ],
                "canvas_size": {
                    "width": self.canvas.width() if self.canvas else 0,
                    "height": self.canvas.height() if self.canvas else 0,
                },
            }

            with open(file_path, "w") as f:
                json.dump(sketch_data, f, indent=2)

            logma.info(f"Sketch exported to {file_path}")
        except Exception as e:
            logma.error(f"Failed to export sketch: {e}")
        return self

    def get_layers(self):
        """Get all available layers, creating default if none exist."""
        if self.layers is None:
            # Try to load from document store
            # layers = self.app.model.store.get_document(self.did)
            self.layers = ["Layer 0 - Canvas Layer"]

        if "New Layer" not in self.layers:
            self.layers.append("New Layer")

        return self.layers

    def get_canvas_color(self):
        """Get the current canvas background color."""
        if self.canvas:
            return self.canvas.palette().color(self.canvas.backgroundRole())
        return None

    def get_canvas_colors(self):
        """Get available canvas color options."""
        return ["Black", "Grey", "White", "Blue", "Red", "Green", "Yellow", "Magenta", "Cyan", "Orange", "Violet"]

    def get_canvas_layer(self):
        """Get the currently selected canvas layer name."""
        if self.layers and 0 <= self.active_layer_index < len(self.layers):
            return self.layers[self.active_layer_index]
        return None

    def get_canvas_size(self):
        """Get the current canvas size."""
        if self.canvas:
            return self.canvas.size()
        return self.size()

    def get_content(self):
        """Return sketch content for serialization - file path, layers, shapes, canvas config."""
        content = {"file_path": self.file_path}
        content["layers"] = self.layers if self.layers else []
        content["active_layer_index"] = self.active_layer_index
        content["layer_properties"] = self.layer_properties
        content["shapes"] = []
        for shape in self.shapes:
            shape_dict = {
                "tool": shape.get("tool"),
                "layer": shape.get("layer"),
                "start": {"x": shape["start"].x(), "y": shape["start"].y()},
                "end": {"x": shape["end"].x(), "y": shape["end"].y()},
            }
            config = shape.get("config", {})
            shape_dict["config"] = {
                "style": config.get("style", "Solid"),
                "thickness": config.get("thickness", 3),
                "color": config["color"].name() if config.get("color") else "#000000",
                "end_type_1": config.get("end_type_1"),
                "end_type_2": config.get("end_type_2"),
            }
            content["shapes"].append(shape_dict)
        if self.canvas:
            content["canvas_size"] = {"width": self.canvas.width(), "height": self.canvas.height()}
        return content

    def get_active_layer(self):
        """Get the currently active layer."""
        if self.layers and 0 <= self.active_layer_index < len(self.layers):
            return self.layers[self.active_layer_index]
        return None

    def get_layer_properties(self, layer_name):
        """Get properties for a specific layer."""
        return self.layer_properties.get(layer_name, {})

    def get_shape_at_position(self, pos):
        """Get the shape at the given position (for selection)."""
        # Search in reverse order (top to bottom)
        for i in range(len(self.shapes) - 1, -1, -1):
            shape = self.shapes[i]
            if self._is_point_in_shape(pos, shape):
                return i, shape
        return None, None

    def import_sketch(self, file_path):
        """Import a sketch from a file."""
        import json

        try:
            with open(file_path, "r") as f:
                sketch_data = json.load(f)

            # Restore layers
            self.layers = sketch_data.get("layers", ["Layer 0 - Canvas Layer"])
            self.layer_properties = sketch_data.get("layer_properties", {})

            # Restore shapes
            self.shapes = []
            for shape_data in sketch_data.get("shapes", []):
                shape = {
                    "tool": shape_data["tool"],
                    "start": pyqt.QPointF(shape_data["start"]["x"], shape_data["start"]["y"]),
                    "end": pyqt.QPointF(shape_data["end"]["x"], shape_data["end"]["y"]),
                    "layer": shape_data.get("layer"),
                }
                self.shapes.append(shape)

            # Restore canvas size if available
            canvas_size = sketch_data.get("canvas_size")
            if canvas_size and self.canvas:
                self.canvas.resize(canvas_size["width"], canvas_size["height"])

            self.render_on_canvas()
            logma.info(f"Sketch imported from {file_path}")
        except Exception as e:
            logma.error(f"Failed to import sketch: {e}")
        return self

    def init_canvas_config(self):
        """"""
        items = self.toolbox_config.get(100, {}).get("items", {})
        cnt = 0
        items[cnt] = {}
        cfg = {
            "text": "Canvas Color",
            "layout": "horizontal",
            "handler": self.cmd_launch_color_sigil,
        }
        self.canvas_color_sigil_button = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.canvas_color_sigil_button
        cnt += 1
        # items[cnt] = {}
        # cfg = {
        #     "label": "Canvas Size",
        #     "layout": "horizontal",
        #     "handler": self.cmd_canvas_size_change,
        #     "value": self.get_canvas_size(),
        # }
        # self.canvas_size_set = NchantdLabeledDoubleSpinBox(self, cfg)
        # items[cnt]["widget"] = self.canvas_size_set
        # cnt += 1
        items[cnt] = {}
        self.get_layers()
        cfg = {
            "label": "Active Layer",
            "layout": "horizontal",
            "options": self.layers,
            "handler": self.cmd_layer_change,
            "value": self.get_canvas_layer(),
        }
        self.canvas_layer_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.canvas_layer_select
        cnt += 1
        items[cnt] = {}
        cfg = {"layout": "horizontal", "data": self.layers}
        self.layers_list_pane = NchantdLayersListPane(self, cfg)
        items[cnt]["widget"] = self.layers_list_pane
        cnt += 1
        items[cnt] = {}
        cfg = {"layout": "horizontal"}
        self.layers_select = NchantdEditLayerPane(self, cfg)
        items[cnt]["widget"] = self.layers_select
        return items

    # Tool-pane definitions used by ``init_sketch_tools``. Each tuple is
    # ``(widget_attr_name, pane_class, label)``. Adding a new drawing tool
    # means appending one tuple here; no editor branch to update.
    _SKETCH_TOOLPANES = (
        ("line_tools_group",    "NchantdLineToolPane",    "Line Tool"),
        ("curve_tool_pane",     "NchantdCurveToolPane",   "Curve Tool"),
        ("splineline_tool_pane", "NchantdSplineToolPane",  "Spline Tool"),
        ("polygon_tool_pane",   "NchantdPolygonToolPane", "Polygon Tool"),
        ("circle_tool_pane",     "NchantdCircleToolPane",  "Circle Tool"),
        ("object_tool_pane",     "NchantdObjectToolPane",  "Insert Object: "),
        ("fill_tool_pane",      "NchantdFillToolPane",   "Fill Color: "),
    )

    def _build_sketch_tool_pane(self, attr_name, pane_class_name, label):
        """Instantiate one sketch tool pane and store it on self."""
        pane_class = globals().get(pane_class_name) or globals().get(
            "Nchantd" + pane_class_name.removeprefix("Nchantd")
        )
        if pane_class is None:
            # Fall back to module-level lookup if globals doesn't have it
            import sys
            for name, obj in list(sys.modules.items()):
                if pane_class_name in name:
                    pass
            pane_class = globals()[pane_class_name]
        pane = pane_class(
            self,
            {
                "label": label,
                "layout": "horizontal",
                "actions": self.config.dikt.get("buttons", {}),
            },
        )
        setattr(self, attr_name, pane)
        return pane

    def init_sketch_tools(self):
        """Build the sketch-tools drawer (line/curve/spline/polygon/circle/object/fill)."""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        for attr_name, pane_class_name, label in self._SKETCH_TOOLPANES:
            slot = self._ensure_drawer_item(items, cnt)
            slot["widget"] = self._build_sketch_tool_pane(attr_name, pane_class_name, label)
            cnt += 1
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

    # def init_drawer_quickstart(self):
    #     """"""
    #     items = self.toolbox_config[400].get("items", {})
    #     return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        logma.info(f"Toolbox Config {self.toolbox_config}")
        logma.info(f"Config {self.config.dikt}")
        self.toolbox_config[100]["items"] = self.init_canvas_config()
        self.toolbox_config[200]["items"] = self.init_sketch_tools()
        self.toolbox_config[300]["items"] = self.init_object_config()
        # self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def merge_layers(self, layer1, layer2):
        """Merge two layers into one (placeholder for advanced functionality)."""
        logma.info(f"Merging layers: {layer1} and {layer2}")
        return self

    def mousePressEvent(self, event):
        """Handle mouse press events for drawing."""
        if event.button() == pyqt.Qt.LeftButton and self.current_tool:
            logma.info(f"Mouse press with tool: {self.current_tool}")
            # Get position relative to canvas
            if hasattr(event, "pos"):
                pos = event.pos()
            else:
                pos = event.position().toPoint() if hasattr(event, "position") else event.pos()

            self.start_point = pos
            self.end_point = self.start_point
            self.drawing = True

            # Ensure cursor stays correct during drawing
            self._update_canvas_cursor()

            self.render_on_canvas()

    def mouseMoveEvent(self, event):
        """Handle mouse move events for dynamic drawing preview."""
        if self.drawing and (event.buttons() & pyqt.Qt.LeftButton):
            # Get position relative to canvas
            if hasattr(event, "pos"):
                pos = event.pos()
            else:
                pos = event.position().toPoint() if hasattr(event, "position") else event.pos()

            self.end_point = pos

            # Keep cursor correct during drawing
            self._update_canvas_cursor()

            self.render_on_canvas()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events to finalize the drawn shape."""
        if event.button() == pyqt.Qt.LeftButton and self.drawing:
            logma.info(f"Mouse release, saving shape: {self.current_tool}")
            # Get position relative to canvas
            if hasattr(event, "pos"):
                pos = event.pos()
            else:
                pos = event.position().toPoint() if hasattr(event, "position") else event.pos()

            self.end_point = pos
            self.save_shape()
            self.drawing = False
            self.start_point = None
            self.end_point = None
            self.render_on_canvas()

    def new_layer(self, name=None):
        """Create a new layer with the specified name."""
        if self.layers is None:
            self.get_layers()

        if name is None:
            layer_count = len([l for l in self.layers if not l.startswith("New Layer")])
            name = f"Layer {layer_count}"

        layer_name = f"{len(self.layers) - 1}: {name}"
        # Insert before "New Layer" option
        self.layers.insert(-1, layer_name)
        return self

    def paintEvent(self, event):
        """Paint event handler - delegate rendering to render_on_canvas."""
        super().paintEvent(event)
        self.render_on_canvas()

    def render_on_canvas(self):
        """Render all shapes on the canvas using a pixmap for double buffering."""
        if not self.canvas:
            logma.warning("render_on_canvas: No canvas available")
            return

        # Get canvas size
        canvas_size = self.canvas.size()
        if canvas_size.width() <= 0 or canvas_size.height() <= 0:
            logma.warning(f"render_on_canvas: Invalid canvas size {canvas_size.width()}x{canvas_size.height()}")
            return

        logma.info(f"render_on_canvas called: {len(self.shapes)} shapes, drawing={self.drawing}")

        # Create a pixmap to draw on
        pixmap = pyqt.QPixmap(canvas_size)
        pixmap.fill(pyqt.Qt.white)  # Fill with white background

        # Create painter for the pixmap
        painter = pyqt.QPainter(pixmap)
        if not painter.isActive():
            logma.warning("Failed to create active painter for pixmap")
            return

        painter.setRenderHint(pyqt.QPainter.Antialiasing)

        try:
            # Draw all saved shapes
            for i, shape in enumerate(self.shapes):
                logma.info(f"Drawing saved shape {i}: {shape.get('tool')}")
                self._setup_painter_for_shape(painter, shape)
                self._draw_shape(painter, shape)

            # Draw current shape being drawn
            if self.drawing and self.start_point and self.end_point:
                logma.info(f"Drawing current shape: {self.current_tool} from {self.start_point} to {self.end_point}")
                shape_data = {
                    "tool": self.current_tool,
                    "start": self.start_point,
                    "end": self.end_point,
                    "config": self.current_tool_config,
                }
                self._setup_painter_for_shape(painter, shape_data)
                self._draw_shape(painter, shape_data)
        except Exception as e:
            logma.error(f"Error rendering shapes: {e}", exc_info=True)
        finally:
            painter.end()

        # Update canvas with the pixmap using the new setDisplayPixmap method
        try:
            self.canvas.setDisplayPixmap(pixmap)
            logma.info(f"Pixmap set on canvas successfully, size: {pixmap.size()}")
        except Exception as e:
            logma.error(f"Error setting canvas pixmap: {e}", exc_info=True)

    def rename_layer(self, old_name, new_name):
        """Rename an existing layer."""
        if old_name in self.layers:
            index = self.layers.index(old_name)
            self.layers[index] = new_name
        return self

    def redo_shape(self):
        """Redo the last undone shape."""
        if self.redo_stack:
            action, shape = self.redo_stack.pop()
            if action == "add":
                self.shapes.append(shape)
                self.undo_stack.append((action, shape))
                self.render_on_canvas()
        return self

    def select_shape_at_position(self, pos):
        """Select a shape at the given position."""
        index, shape = self.get_shape_at_position(pos)
        if index is not None:
            self.current_shape = shape
            logma.info(f"Selected shape: {shape.get('tool')}")
            return shape
        return None

    def save(self):
        """"""
        if self.document is None:
            self.new_document()
        content = self.get_content()
        if content != self.document.content:
            self.document.set_content(content)
        super().save()
        return self

    def save_shape(self):
        """Save the current shape to the shapes list and clear redo stack."""
        if self.start_point and self.end_point and self.current_tool:
            shape_data = {
                "tool": self.current_tool,
                "start": self.start_point,
                "end": self.end_point,
                "layer": (
                    self.layers[self.active_layer_index] if 0 <= self.active_layer_index < len(self.layers) else None
                ),
                "config": {
                    "style": self.current_tool_config.get("style", "Solid"),
                    "thickness": self.current_tool_config.get("thickness", 3),
                    "color": self.current_tool_config.get("color", pyqt.QColor(pyqt.Qt.black)),
                    "end_type_1": self.current_tool_config.get("end_type_1"),
                    "end_type_2": self.current_tool_config.get("end_type_2"),
                },
            }
            self.shapes.append(shape_data)
            # Add to undo stack
            self.undo_stack.append(("add", shape_data))
            # Clear redo stack when new action is performed
            self.redo_stack.clear()
        return self

    def set_active_layer(self, layer_name):
        """Set the active layer by name."""
        if layer_name in self.layers:
            self.active_layer_index = self.layers.index(layer_name)
        return self

    def set_active_layer_by_index(self, index):
        """Set the active layer by index."""
        if 0 <= index < len(self.layers):
            self.active_layer_index = index
        return self

    def set_canvas_color(self, color):
        """Set the canvas background color."""
        if self.canvas and color:
            self.canvas.setStyleSheet(f"background-color: {color};")
        return self

    def set_canvas_size(self, width, height):
        """Set the canvas size."""
        if self.canvas:
            self.canvas.resize(width, height)
        return self

    def undo_last_shape(self):
        """Remove the last drawn shape and add to redo stack."""
        if self.shapes:
            shape = self.shapes.pop()
            self.redo_stack.append(("add", shape))
            if self.undo_stack:
                self.undo_stack.pop()
            self.render_on_canvas()
        return self

    def _setup_painter_for_shape(self, painter, shape_data):
        """Setup painter with the appropriate pen and brush for the shape."""
        config = shape_data.get("config", {})

        # Get color
        color = config.get("color", pyqt.QColor(pyqt.Qt.black))
        if not isinstance(color, pyqt.QColor):
            color = pyqt.QColor(pyqt.Qt.black)

        # Get thickness
        thickness = config.get("thickness", 3)

        # Get style
        style_str = config.get("style", "Solid")
        pen_style = self._get_pen_style_from_string(style_str)

        # Create and set pen
        pen = pyqt.QPen(color, thickness, pen_style)
        pen.setCapStyle(pyqt.Qt.RoundCap)
        pen.setJoinStyle(pyqt.Qt.RoundJoin)
        painter.setPen(pen)

        # Set brush for filled shapes
        if shape_data.get("tool") in ["polygon", "ellipse", "fill"]:
            brush = pyqt.QBrush(color, pyqt.Qt.SolidPattern)
            painter.setBrush(brush)

    def _draw_line_shape(self, painter, start, end, config):
        """Draw a straight line + any configured end decorations."""
        painter.drawLine(start, end)
        self._draw_line_ends(painter, start, end, config)

    def _draw_curve_shape(self, painter, start, end, config):
        """Draw a quadratic Bezier curve (control point above the midpoint)."""
        path = pyqt.QPainterPath(start)
        mid_x = (start.x() + end.x()) / 2
        mid_y = (start.y() + end.y()) / 2
        offset = 50
        control = pyqt.QPointF(mid_x, mid_y - offset)
        path.quadTo(control, end)
        painter.drawPath(path)

    def _draw_spline_shape(self, painter, start, end, config):
        """Draw a smooth cubic Bezier spline between two points."""
        path = pyqt.QPainterPath(start)
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        control1 = pyqt.QPointF(start.x() + dx / 3, start.y() + dy / 4)
        control2 = pyqt.QPointF(start.x() + 2 * dx / 3, end.y() - dy / 4)
        path.cubicTo(control1, control2, end)
        painter.drawPath(path)

    def _draw_polygon_shape(self, painter, start, end, config):
        """Draw a rectangle. (Placeholder for n-sided polygon support.)"""
        painter.drawRect(pyqt.QRectF(start, end).normalized())

    def _draw_ellipse_shape(self, painter, start, end, config):
        """Draw an ellipse or circle inscribed in the start-end rect."""
        painter.drawEllipse(pyqt.QRectF(start, end).normalized())

    def _draw_fill_shape(self, painter, start, end, config):
        """Fill the start-end rect with the current brush colour."""
        painter.fillRect(pyqt.QRectF(start, end).normalized(), painter.brush().color())

    # Dispatch table mapping tool name → drawing method. Adding a new
    # tool means appending one entry here, no switch needed.
    _SHAPE_DRAWERS = {
        "line":    "_draw_line_shape",
        "curve":   "_draw_curve_shape",
        "spline":  "_draw_spline_shape",
        "polygon": "_draw_polygon_shape",
        "ellipse": "_draw_ellipse_shape",
        "fill":    "_draw_fill_shape",
    }

    def _draw_shape(self, painter, shape_data):
        """Draw a shape based on its tool type via the ``_SHAPE_DRAWERS`` dispatch."""
        start = shape_data.get("start")
        end = shape_data.get("end")
        if not start or not end:
            return

        config = shape_data.get("config", {})
        method_name = self._SHAPE_DRAWERS.get(shape_data.get("tool"))
        if method_name is None:
            return
        getattr(self, method_name)(painter, start, end, config)

    def _draw_line_ends(self, painter, start, end, config):
        """Draw decorative ends for lines (arrows, circles, etc.)."""
        end_type_1 = config.get("end_type_1")
        end_type_2 = config.get("end_type_2")

        if end_type_1 and end_type_1 != "None":
            self._draw_line_end_decoration(painter, end, start, end_type_1)

        if end_type_2 and end_type_2 != "None":
            self._draw_line_end_decoration(painter, start, end, end_type_2)

    def _draw_line_end_decoration(self, painter, from_point, to_point, decoration_type):
        """Draw a specific decoration at a line end."""
        import math

        # Calculate angle
        dx = to_point.x() - from_point.x()
        dy = to_point.y() - from_point.y()
        angle = math.atan2(dy, dx)

        if decoration_type == "Arrow":
            # Draw arrow head
            arrow_size = 10
            angle1 = angle + math.pi * 0.85
            angle2 = angle - math.pi * 0.85

            arrow_p1 = pyqt.QPointF(
                to_point.x() + arrow_size * math.cos(angle1), to_point.y() + arrow_size * math.sin(angle1)
            )
            arrow_p2 = pyqt.QPointF(
                to_point.x() + arrow_size * math.cos(angle2), to_point.y() + arrow_size * math.sin(angle2)
            )

            painter.drawLine(to_point, arrow_p1)
            painter.drawLine(to_point, arrow_p2)

        elif decoration_type == "Circle":
            # Draw circle at end
            radius = 5
            painter.drawEllipse(to_point, radius, radius)

        elif decoration_type == "Square":
            # Draw square at end
            size = 8
            rect = pyqt.QRectF(to_point.x() - size / 2, to_point.y() - size / 2, size, size)
            painter.drawRect(rect)

    def _get_expected_cursor_shape(self):
        """Get the expected cursor shape based on current tool."""
        if self.current_tool in ["line", "curve", "spline", "polygon", "ellipse"]:
            return pyqt.Qt.CrossCursor
        elif self.current_tool in ["object", "fill"]:
            return pyqt.Qt.PointingHandCursor
        else:
            return pyqt.Qt.ArrowCursor

    def _get_qcolor_from_name(self, color_name):
        """Convert color name to QColor."""
        color_map = {
            "Black": pyqt.Qt.black,
            "Grey": pyqt.Qt.gray,
            "White": pyqt.Qt.white,
            "Blue": pyqt.Qt.blue,
            "Red": pyqt.Qt.red,
            "Green": pyqt.Qt.green,
            "Yellow": pyqt.Qt.yellow,
            "Magenta": pyqt.Qt.magenta,
            "Cyan": pyqt.Qt.cyan,
            "Orange": pyqt.QColor(255, 165, 0),
            "Violet": pyqt.QColor(138, 43, 226),
        }
        return pyqt.QColor(color_map.get(color_name, pyqt.Qt.black))

    def _get_pen_style_from_string(self, style_string):
        """Convert style string to Qt pen style."""
        style_map = {
            "Solid": pyqt.Qt.SolidLine,
            "Dashed": pyqt.Qt.DashLine,
            "Dotted": pyqt.Qt.DotLine,
            "Dash Dotted": pyqt.Qt.DashDotLine,
        }
        return style_map.get(style_string, pyqt.Qt.SolidLine)

    def _is_point_in_shape(self, pos, shape):
        """Check if a point is within a shape's bounds."""
        start = shape.get("start")
        end = shape.get("end")
        tool = shape.get("tool")

        if not start or not end:
            return False

        tolerance = 5  # Click tolerance in pixels

        if tool in ["line", "curve", "spline"]:
            # For lines, check if point is near the line
            # Simple bounding box check
            rect = pyqt.QRectF(start, end).normalized()
            expanded = rect.adjusted(-tolerance, -tolerance, tolerance, tolerance)
            return expanded.contains(pos)

        elif tool in ["polygon", "ellipse", "fill"]:
            # For filled shapes, check if point is inside
            rect = pyqt.QRectF(start, end).normalized()
            return rect.contains(pos)

        return False

    def _setup_canvas_mouse_handlers(self):
        """Override canvas mouse handlers to delegate to sketch widget."""
        # Save original handlers
        self._original_canvas_mouse_press = self.canvas.mousePressEvent
        self._original_canvas_mouse_move = self.canvas.mouseMoveEvent
        self._original_canvas_mouse_release = self.canvas.mouseReleaseEvent

        # Replace with our handlers
        def canvas_mouse_press(event):
            if self.current_tool:
                logma.info(f"Canvas mousePressEvent intercepted, tool={self.current_tool}")
                self.mousePressEvent(event)
            else:
                self._original_canvas_mouse_press(event)

        def canvas_mouse_move(event):
            if self.current_tool:
                self.mouseMoveEvent(event)
            else:
                self._original_canvas_mouse_move(event)

        def canvas_mouse_release(event):
            if self.current_tool:
                logma.info(f"Canvas mouseReleaseEvent intercepted, tool={self.current_tool}")
                self.mouseReleaseEvent(event)
            else:
                self._original_canvas_mouse_release(event)

        self.canvas.mousePressEvent = canvas_mouse_press
        self.canvas.mouseMoveEvent = canvas_mouse_move
        self.canvas.mouseReleaseEvent = canvas_mouse_release

    def _update_canvas_cursor(self):
        """Update the canvas cursor based on the current tool."""
        if not self.canvas or self._updating_cursor:
            return

        # Set flag to prevent recursion
        self._updating_cursor = True

        try:
            cursor = None
            if self.current_tool in ["line", "curve", "spline", "polygon", "ellipse"]:
                cursor = pyqt.Qt.CrossCursor
                logma.info(f"Setting CrossCursor on canvas for tool: {self.current_tool}")
            elif self.current_tool in ["object", "fill"]:
                cursor = pyqt.Qt.PointingHandCursor
                logma.info(f"Setting PointingHandCursor on canvas for tool: {self.current_tool}")
            else:
                cursor = pyqt.Qt.ArrowCursor
                logma.info("Setting ArrowCursor on canvas (no tool active)")

            # Set cursor on canvas directly
            self.canvas.setCursor(pyqt.QCursor(cursor))

            # If canvas has a viewport (for scroll areas), set it there too
            if hasattr(self.canvas, "viewport"):
                self.canvas.viewport().setCursor(pyqt.QCursor(cursor))

            # Force update
            self.canvas.update()
            logma.info(
                f"Canvas cursor set successfully. Canvas visible: {self.canvas.isVisible()}, cursor shape: {self.canvas.cursor().shape()}"
            )
        except Exception as e:
            logma.error(f"Failed to set canvas cursor: {e}")
        finally:
            # Always reset flag
            self._updating_cursor = False

    def _update_tool_config_from_pane(self, tool_pane):
        """Update current tool configuration from the tool pane settings."""
        try:
            # Update line style
            if hasattr(tool_pane, "line_style_select"):
                style = (
                    tool_pane.line_style_select.currentText()
                    if hasattr(tool_pane.line_style_select, "currentText")
                    else "Solid"
                )
                self.current_tool_config["style"] = style

            # Update thickness
            if hasattr(tool_pane, "line_thickness_spin"):
                thickness = (
                    tool_pane.line_thickness_spin.value() if hasattr(tool_pane.line_thickness_spin, "value") else 3
                )
                self.current_tool_config["thickness"] = thickness

            # Update color
            if hasattr(tool_pane, "line_color_select"):
                color_name = (
                    tool_pane.line_color_select.currentText()
                    if hasattr(tool_pane.line_color_select, "currentText")
                    else "black"
                )
                self.current_tool_config["color"] = self._get_qcolor_from_name(color_name)

            # Update end types for line tools
            if hasattr(tool_pane, "line_end_one_type_select"):
                end_type_1 = (
                    tool_pane.line_end_one_type_select.currentText()
                    if hasattr(tool_pane.line_end_one_type_select, "currentText")
                    else None
                )
                self.current_tool_config["end_type_1"] = end_type_1

            if hasattr(tool_pane, "line_end_two_type_select"):
                end_type_2 = (
                    tool_pane.line_end_two_type_select.currentText()
                    if hasattr(tool_pane.line_end_two_type_select, "currentText")
                    else None
                )
                self.current_tool_config["end_type_2"] = end_type_2

        except Exception as e:
            logma.warning(f"Could not update tool config from pane: {e}")


class NchantdOfficePalette(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"NchantdOfficePalette init: parent={type(parent).__name__}")
        super().__init__("Nchantd Palette", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficePalette"))
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
        self.canvas_color_select = NchantdDropDown(self, cfg).initWidget()
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
