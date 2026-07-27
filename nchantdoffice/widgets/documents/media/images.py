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
from os.path import dirname, join, exists
from os import listdir
from copy import deepcopy

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from ogma.logma import Logma
from nchantrs.widgets.managers import NchantdBasketManager
from nchantrs.widgets.media.images import NchantdImage
from nchantrs.widgets.media.palettes import NchantdPaletteTable
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.controls.buttons import NchantdButton, NchantdButtonWidget
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.groups import NchantdGroup
from nchantdoffice.widgets.panes.files import NchantdFileDetailsPane
from nchantrs.widgets.annotations import NchantdLabel

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
debug = True
logma = Logma(__name__)
if not log:
    logma.off()
# ====================================================================================================================||
pxcfg = join(here, "_data_", "images.yaml")


class NchantdOfficeLightTable(NchantdBasketManager):
    """A thumbnail dispositioning and tagging tool for images"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeLightTable").override(cfg))
        self.image_viewer = None
        self.path = self.config.dikt.get("path", None)
        self.tag_bar = None

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView({"layout": "horizontal"})

        layout = pyqt.QVBoxLayout()
        # create a tag bar to show often used tags and the ability to create new tags
        # a tag creator will have a ... button to expand options allowing for a tag action to be connected to the tag
        # tags can be added to images or baskets a tag added to a basket will add it to each
        # image that goes in the basket
        # add tools like find duplicates
        # add a color palette tool...of all images in the directory...view...basket
        # add a remove back ground tool from all thumbnails
        #
        cfg = {}
        self.tag_bar = NchantdButtonBar(self, cfg).initWidget()
        layout.addWidget(self.tag_bar)
        cfg = {"path": self.path}
        self.image_viewer = NchantdImageThumbnailViewer(self, cfg).initWidget()
        layout.addWidget(self.image_viewer)
        self.layout.addLayout(layout)
        cfg = {}
        self.baskets = NchantdBasketManager(self, cfg).initWidget()
        self.layout.addWidget(self.baskets)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdColorShiftPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdColorShiftPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        cfg = cfg or {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg = {"text": "Shift Color: "}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"text": "Select Image Color", "layout": "horizontal", "handler": self.cmd_image_color_change}
        self.image_color_button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.image_color_button)
        cfg = {"text": "Selected Color: \n RGB: \n HEX:", "size": ["auto", 50], "justify": "left"}
        self.image_color_label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(self.image_color_label)
        cfg = {
            "text": "Select New Image Color",
            "layout": "horizontal",
            "options": self.get_image_formats(),
            "handler": self.cmd_select_new_image_color_change,
        }
        self.image_color_conversion_button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.image_color_conversion_button)
        cfg = {"text": "Selected New Color: \n RGB: \n HEX:", "size": ["auto", 50], "justify": "left"}
        self.image_new_color_label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(self.image_new_color_label)
        cfg = {"text": "Convert", "layout": "horizontal", "handler": self.cmd_convert_color}
        self.convert_button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.convert_button)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_image_color_change(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_image_color_change invoked (stub)")
        return self
    def cmd_select_new_image_color(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_select_new_image_color invoked (stub)")
        return self
    def cmd_select_new_image_color_change(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_select_new_image_color_change invoked (stub)")
        return self
    def cmd_convert_color(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_convert_color invoked (stub)")
        return self
    def get_image_formats(self):
        """"""
        formats = []
        return formats


class NchantdConvertFormatPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdConvertFormatPane").override(cfg))

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
        cfg = {"text": "Convert Format: "}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {
            "label": "Current Format:",
            "layout": "horizontal",
            "handler": self.cmd_current_format_change,
            "value": self.get_current_format(),
        }
        self.image_format_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.image_format_entry)
        cfg = {
            "label": "Convert to Format",
            "layout": "horizontal",
            "options": self.get_image_formats(),
            "handler": self.cmd_convert_to_format_change,
            "value": self.get_convert_to_format(),
        }
        self.image_conversion_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.image_conversion_select)
        cfg = {"text": "Convert", "layout": "horizontal", "handler": self.cmd_convert_format}
        self.convert_button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.convert_button)
        self.layout.addWidget(group)
        return self

    def cmd_current_format_change(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_current_format_change invoked (stub)")
        return self
    def cmd_convert_format(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_convert_format invoked (stub)")
        return self
    def cmd_convert_to_format(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_convert_to_format invoked (stub)")
        return self
    def cmd_convert_to_format_change(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_convert_to_format_change invoked (stub)")
        return self
    def get_current_format(self):
        """Return None as a default value.

        Stub implementation of get_current_format.
        """
        logma.info(f"[images] {self.__class__.__name__}.get_current_format (stub returning None)")
        return None
    def get_convert_to_format(self):
        """Return None as a default value.

        Stub implementation of get_convert_to_format.
        """
        logma.info(f"[images] {self.__class__.__name__}.get_convert_to_format (stub returning None)")
        return None
    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_image_formats(self):
        """"""
        formats = []
        return formats


class NchantdConvertSizePane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdConvertSizePane").override(cfg))

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
        cfg = {"text": "Resize Image:"}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {
            "text": "Maintain Aspect Ratio",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "value": True,
            "handler": self.cmd_image_maintain_ratio_change,
        }
        self.image_maintain_ratio_checkbox = NchantdCheckbox(self, cfg).initWidget()
        layout.addWidget(self.image_maintain_ratio_checkbox)
        cfg = {"label": f"Current Width: {self.get_image_width()}", "layout": "horizontal"}
        self.image_width_label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(self.image_width_label)
        cfg = {"label": "Set Width", "layout": "horizontal"}
        self.image_width_select = NchantdLabeledSpinBox(self, cfg).initWidget()
        layout.addWidget(self.image_width_select)
        cfg = {"label": f"Current Height: {self.get_image_height()}", "layout": "horizontal"}
        self.image_height_label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(self.image_height_label)
        cfg = {
            "label": "Set Height",
            "layout": "horizontal",
            "handler": self.cmd_image_height_change,
            "value": self.get_image_height(),
        }
        self.image_height_select = NchantdLabeledSpinBox(self, cfg).initWidget()
        layout.addWidget(self.image_height_select)
        cfg = {"text": "Resize", "layout": "horizontal"}
        self.convert_button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.convert_button)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_select_new_image_color_change(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_select_new_image_color_change invoked (stub)")
        return self
    def cmd_image_maintain_ratio_change(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_image_maintain_ratio_change invoked (stub)")
        return self
    def cmd_image_height_change(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_image_height_change invoked (stub)")
        return self
    def get_image_height(self):
        """"""
        return 100

    def get_image_width(self):
        """"""
        return 100


class NchantdImageCropPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdImageCropPane").override(cfg))

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
        cfg = {"text": "Crop Image:"}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {
            "action": "select_screen_area",
            "layout": "horizontal",
            "handler": self.cmd_activate_image_section_selection,
        }
        self.image_section_selection_activator = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.image_section_selection_activator)
        cfg = {"text": "Cut", "layout": "horizontal", "handler": self.cmd_cut_selection}
        self.cut_button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.cut_button)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_activate_image_section_selection(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_activate_image_section_selection invoked (stub)")
        return self
    def get_image_height(self):
        """"""
        return 100

    def get_image_width(self):
        """"""
        return 100


class NchantdImageGeneratorPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdConvertSizePane").override(cfg))

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
        cfg = {"text": "Generate Image:"}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {
            "label": "Set Width",
            "layout": "horizontal",
            "handler": self.cmd_image_width_select_change,
            "value": self.get_image_width(),
        }
        self.image_width_select = NchantdLabeledSpinBox(self, cfg).initWidget()
        layout.addWidget(self.image_width_select)
        cfg = {
            "label": "Set Height",
            "layout": "horizontal",
            "handler": self.cmd_image_height_select_change,
            "value": self.get_image_height(),
        }
        self.image_height_select = NchantdLabeledSpinBox(self, cfg).initWidget()
        layout.addWidget(self.image_height_select)
        cfg = {
            "text": "Select Palette",
            "layout": "horizontal",
            "handler": self.cmd_palette_select_change,
            "value": self.get_palette(),
        }
        self.palette_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.palette_select)
        cfg = {"text": "Generate Image", "layout": "horizontal", "handler": self.cmd_generate_image}
        self.generate_button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.generate_button)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_image_width_select_change(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_image_width_select_change invoked (stub)")
        return self
    def cmd_image_height_select_change(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_image_height_select_change invoked (stub)")
        return self
    def cmd_generate_image(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_generate_image invoked (stub)")
        return self
    def get_palette(self):
        """Return None as a default value.

        Stub implementation of get_palette.
        """
        logma.info(f"[images] {self.__class__.__name__}.get_palette (stub returning None)")
        return None
    def cmd_palette_select_change(self):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_palette_select_change invoked (stub)")
        return self
    def get_image_height(self):
        """"""
        return 100

    def get_image_width(self):
        """"""
        return 100


class NchantdOfficeImage(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Nchantd Image", parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeImage").override(cfg))

    def initModel(self):
        """"""
        super().initModel()
        document = {"document": self.config.get("document", {})}

        self.document = self.app.model.codex.init_image(document)
        self.document.load_document()
        self.context_menu_name = "context.document.image"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        return self

    def initView(self, cfg=None):
        """"""
        cfg = {
            "buttons": {
                10: {"action": "convert_format", "handler": self.cmd_convert_format},
                11: {"action": "convert_size", "handler": self.cmd_convert_size},
                12: {"action": "convert_color", "handler": self.cmd_convert_color},
                13: {"action": "crop_image", "handler": self.cmd_crop_image},
                14: {"action": "generate_image", "handler": self.cmd_generate_image},
                15: {
                    "action": "add_palette_document_nchantdpalette",
                    "handler": self.cmd_add_palette_document_nchantdpalette,
                },
                49: "_insert_stretch",
            }
        }
        super().initView(cfg)
        # self.document.file_path = self.document.content.get("file_path")
        # logma.info(f"File Path: {self.document.file_path}")
        cfg = {
            "size": ["auto", "auto"],
            "document": self.document,
            "path": self.document.file_path,
        }
        logma.info(f"Content {self.document.content}")
        self.file_path = self.document.content.get("file_path")
        if self.file_path is None:
            self.file_path = self.document.content.get("content", {}).get("file_path")
        if self.document.content is not None:
            cfg["image_data"] = self.document.content.get("L0", {}).get("bytes", None)
            logma.info(f"Image Data: {cfg['image_data']}")
        self.image = NchantdImage(self, cfg).initWidget()
        self.populate_document()
        self.layout.addWidget(self.image)
        self.layout.setSpacing(3)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_add_palette_document_nchantdpalette(self, event=None, *args, **kwargs):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_add_palette_document_nchantdpalette invoked (stub)")
        return self
    def cmd_convert_color(self, event=None, *args, **kwargs):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_convert_color invoked (stub)")
        return self
    def cmd_convert_format(self, event=None, *args, **kwargs):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_convert_format invoked (stub)")
        return self
    def cmd_convert_size(self, event=None, *args, **kwargs):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_convert_size invoked (stub)")
        return self
    def cmd_crop_image(self, event=None, *args, **kwargs):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_crop_image invoked (stub)")
        return self
    def cmd_generate_image(self, event=None, *args, **kwargs):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_generate_image invoked (stub)")
        return self
    def cmd_image_height_change(self, event=None, *args, **kwargs):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_image_height_change invoked (stub)")
        return self
    def cmd_open_local_file(self, event=None, *args, **kwargs):
        """"""
        super().cmd_open_local_file(event, *args, **kwargs)
        if self.local_file is not None:
            if exists(self.local_file):
                self.open_file(self.local_file)
        return self

    def cmd_run_palette_scan(self, event=None, *args, **kwargs):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_run_palette_scan invoked (stub)")
        return self
    def cmd_image_width_change(self, event=None, *args, **kwargs):
        """Log the invocation and return self for method chaining.

        Stub implementation; the underlying UI handler this wraps
        is not yet wired up. See H## tracker for follow-up work.
        """
        logma.info(f"[images] {self.__class__.__name__}.cmd_image_width_change invoked (stub)")
        return self
    def get_binary(self):
        """Return None as a default value.

        Stub implementation of get_binary.
        """
        logma.info(f"[images] {self.__class__.__name__}.get_binary (stub returning None)")
        return None
    def get_content(self):
        """"""
        logma.info(f"File Path {self.file_path}")
        return {"content": {"file_path": self.file_path}}

    def get_image_height(self):
        """Return None as a default value.

        Stub implementation of get_image_height.
        """
        logma.info(f"[images] {self.__class__.__name__}.get_image_height (stub returning None)")
        return None
    def get_image_width(self):
        """Return None as a default value.

        Stub implementation of get_image_width.
        """
        logma.info(f"[images] {self.__class__.__name__}.get_image_width (stub returning None)")
        return None
    def init_drawer_document_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "File Name: ", "layout": "horizontal"}
        self.file_pane = NchantdFileDetailsPane(self, cfg)
        items[cnt]["widget"] = self.file_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Image Width: ",
            "layout": "horizontal",
            "handler": self.cmd_image_width_change,
            "value": self.get_image_width() or "",
        }
        self.image_size_width_editor = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.image_size_width_editor
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Image Height: ",
            "layout": "horizontal",
            "handler": self.cmd_image_height_change,
            "value": self.get_image_height() or "",
        }
        self.image_size_height_editor = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.image_size_height_editor
        cnt += 1
        return items

    def init_drawer_image_tools(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"text": ""}
        self.image_format_conversion_pane = NchantdConvertFormatPane(self, cfg)
        items[cnt]["widget"] = self.image_format_conversion_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"text": ""}
        self.image_size_conversion_pane = NchantdConvertSizePane(self, cfg)
        items[cnt]["widget"] = self.image_size_conversion_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"text": ""}
        self.image_color_shift_pane = NchantdColorShiftPane(self, cfg)
        items[cnt]["widget"] = self.image_color_shift_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"text": ""}
        self.image_crop_pane = NchantdImageCropPane(self, cfg)
        items[cnt]["widget"] = self.image_crop_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"text": ""}
        self.image_generator_pane = NchantdImageGeneratorPane(self, cfg)
        items[cnt]["widget"] = self.image_generator_pane
        cnt += 1
        return items

    # PUSH to 0.0.3
    # def init_drawer_palette(self):
    #     """"""
    #     items = self.toolbox_config[300].get("items", {})
    #     cnt = 0
    #     default_action = {"action": "insert_generic_action", "type": "custom"}
    #     if cnt not in items:
    #         items[cnt] = deepcopy(default_action)
    #     cfg = {"text": "Scan to Extract Palette", "handler": self.cmd_run_palette_scan}
    #     self.image_scan_palette_button = NchantdButtonWidget(self, cfg)
    #     items[cnt]["widget"] = self.image_scan_palette_button
    #     cnt += 1
    #     if cnt not in items:
    #         items[cnt] = deepcopy(default_action)
    #     cfg = {
    #         "text": "Modify Palette: ",
    #         "num_columns": 3,
    #         "num_rows": 10,
    #         "columns": ["Color", "Hex", "Usage %"],
    #         "column_width": 10,
    #     }
    #     self.image_palette = NchantdPaletteTable(self, cfg)
    #     items[cnt]["widget"] = self.image_palette
    #     cnt += 1
    #     return items

    # PUSH to 0.0.3
    # def init_drawer_quickstart(self):
    #     """"""
    #     items = self.toolbox_config[400].get("items", {})
    #     cnt = 0
    #     default_action = {"action": "insert_generic_action", "type": "custom"}
    #
    #     return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_image_tools()
        # self.toolbox_config[300]["items"] = self.init_drawer_palette()
        # self.toolbox_config[400]["items"] = self.init_drawer_quickstart()
        return self

    def open_file(self, file=None):
        """"""
        logma.info(file)
        try:
            self.set_file_path(file)
            if file is not None:
                self.document.open_file(file)
        except Exception as e:
            logma.warning(e)
            if debug:
                raise e
        self.document.set_location("external")
        self.populate_document()
        return self

    def populate_document(self):
        """"""
        # TODO we really should open from binary data that is already opened in the PyfficeDocument
        logma.info(f"Populate worksheet {self.file_path}")
        self.image.load_image(self.file_path)
        return self

    def save(self):
        """"""
        super().save()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
