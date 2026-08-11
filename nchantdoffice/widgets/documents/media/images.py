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
from kahndor.logma import Logma
from nchantrs.widgets.managers import NchantdBasketManager
from nchantrs.widgets.media.images import NchantdImage
from nchantrs.widgets.media.palettes import NchantdPaletteTable

try:
    from nchantrs.widgets.media.images import NchantdImageThumbnailViewer
except ImportError:
    NchantdImageThumbnailViewer = None
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
from pyffice.images.palettes import PyfficeColorPalette

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
        logma.info(f"NchantdColorShiftPane init: parent={type(parent).__name__}")
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
        """Read the color-shift dropdown and store the new value on the config.

        Looks for ``self.color_select`` (or the pane's color-shift
        dropdown) and persists the new value to ``config.dikt``.
        """
        value = None
        for attr in ("color_select", "color_shift_select", "image_color_select"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    value = getter()
                    break
        if value is not None:
            self.config.dikt["image_color"] = value
        return self

    def cmd_select_new_image_color(self):
        """Open the color-picker and apply the new color to the pane.

        Delegates to ``self.pick_new_color`` (when present).
        """
        if hasattr(self, "pick_new_color") and callable(self.pick_new_color):
            return self.pick_new_color()
        return self

    def cmd_select_new_image_color_change(self, event=None, *args, **kwargs):
        """Apply a freshly-picked image color to the current color-shift pane.

        Reads the new color from the picker (or ``kwargs["color"]``)
        and writes it onto ``self.color`` so the next paint uses it.
        """
        new_color = kwargs.get("color")
        if new_color is None and event is not None:
            new_color = getattr(event, "color", None) or getattr(event, "text", None)
        if new_color is not None:
            self.color = new_color
            self.config.dikt["image_color"] = new_color
        return self

    def cmd_convert_color(self, event=None, *args, **kwargs):
        """Convert the image to the selected target color.

        Reads the target color from the convert-color dropdown and
        calls ``self.apply_color_shift`` with the new color when
        available.
        """
        target = None
        for attr in ("target_color_select", "convert_color_select", "color_target_select"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    target = getter()
                    break
        if target is not None and hasattr(self, "apply_color_shift") and callable(self.apply_color_shift):
            self.apply_color_shift(target)
            self.config.dikt["converted_color"] = target
        return self

    def get_image_formats(self):
        """"""
        formats = []
        return formats


class NchantdConvertFormatPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"NchantdConvertFormatPane init: parent={type(parent).__name__}")
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

    def cmd_current_format_change(self, event=None, *args, **kwargs):
        """Record the current image format selection on the config."""
        value = None
        for attr in ("current_format_select", "format_select", "image_format_select"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    value = getter()
                    break
        if value is not None:
            self.config.dikt["current_format"] = value
        return self

    def cmd_convert_format(self, event=None, *args, **kwargs):
        """Convert the current image to the target format."""
        target = None
        for attr in ("target_format_select", "convert_format_select", "format_target_select"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    target = getter()
                    break
        if target is not None and hasattr(self, "convert_image_format") and callable(self.convert_image_format):
            self.convert_image_format(target)
            self.config.dikt["converted_format"] = target
        return self

    def cmd_convert_to_format(self, event=None, *args, **kwargs):
        """Set the target format the next convert step should produce."""
        value = None
        for attr in ("convert_to_format_select", "target_format_select"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    value = getter()
                    break
        if value is not None:
            self.config.dikt["convert_to_format"] = value
        return self

    def cmd_convert_to_format_change(self, event=None, *args, **kwargs):
        """Read the convert-to-format change and refresh preview."""
        value = None
        for attr in ("convert_to_format_select", "target_format_select"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    value = getter()
                    break
        if value is not None:
            self.config.dikt["convert_to_format"] = value
            preview = getattr(self, "convert_to_format_preview", None)
            if preview is not None and hasattr(preview, "setText"):
                preview.setText(value)
        return self

    def get_current_format(self):
        """Return the stored value of get_current_format."""
        return self.config.dikt.get("current_format", "") or ""

    def get_convert_to_format(self):
        """Return the stored value of get_convert_to_format."""
        return self.config.dikt.get("convert_to_format", "") or ""

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
        logma.info(f"NchantdConvertSizePane init: parent={type(parent).__name__}")
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

    def cmd_select_new_image_color_change(self, event=None, *args, **kwargs):
        """Apply a freshly-picked image color to the current color-shift pane.

        Reads the new color from the picker (or ``kwargs["color"]``)
        and writes it onto ``self.color`` so the next paint uses it.
        """
        new_color = kwargs.get("color")
        if new_color is None and event is not None:
            new_color = getattr(event, "color", None) or getattr(event, "text", None)
        if new_color is not None:
            self.color = new_color
            self.config.dikt["image_color"] = new_color
        return self

    def cmd_image_maintain_ratio_change(self, event=None, *args, **kwargs):
        """Toggle the maintain-aspect-ratio flag for image resizing.

        Reads the checkbox state and stores it on
        ``config.dikt["image_maintain_ratio"]``.
        """
        checkbox = getattr(self, "image_maintain_ratio_checkbox", None)
        if checkbox is not None and hasattr(checkbox, "isChecked"):
            self.config.dikt["image_maintain_ratio"] = bool(checkbox.isChecked())
        return self

    def cmd_image_height_change(self, event=None, *args, **kwargs):
        """Update the image-height field on the config."""
        height = None
        for attr in ("image_height_select", "image_height_spinbox"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "value", None)
                if callable(getter):
                    height = getter()
                    break
        if height is not None:
            self.config.dikt["image_height"] = height
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
        logma.info(f"NchantdImageCropPane init: parent={type(parent).__name__}")
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

    def cmd_activate_image_section_selection(self, event=None, *args, **kwargs):
        """Activate the image-section selection (e.g. crop region)."""
        value = None
        for attr in ("image_section_select", "section_select"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    value = getter()
                    break
        if value is not None:
            self.config.dikt["image_section_selection"] = value
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
        logma.info(f"NchantdImageGeneratorPane init: parent={type(parent).__name__}")
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

    def cmd_image_width_select_change(self, event=None, *args, **kwargs):
        """Update the image-width select on the config and refresh preview."""
        value = None
        for attr in ("image_width_select", "image_width_spinbox"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "value", None)
                if callable(getter):
                    value = getter()
                    break
        if value is not None:
            self.config.dikt["image_width"] = value
            preview = getattr(self, "image_width_preview", None)
            if preview is not None and hasattr(preview, "setText"):
                preview.setText(str(value))
        return self

    def cmd_image_height_select_change(self, event=None, *args, **kwargs):
        """Update the image-height select on the config and refresh preview."""
        value = None
        for attr in ("image_height_select", "image_height_spinbox"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "value", None)
                if callable(getter):
                    value = getter()
                    break
        if value is not None:
            self.config.dikt["image_height"] = value
            preview = getattr(self, "image_height_preview", None)
            if preview is not None and hasattr(preview, "setText"):
                preview.setText(str(value))
        return self

    def cmd_generate_image(self, event=None, *args, **kwargs):
        """Generate an image from the configured source / prompt."""
        prompt = self.config.dikt.get("image_prompt", "")
        if hasattr(self, "generate_image") and callable(self.generate_image):
            try:
                return self.generate_image(prompt=prompt)
            except TypeError:
                return self.generate_image()
        return self

    def get_palette(self):
        """Return the stored value of get_palette."""
        return self.config.dikt.get("palette", "") or ""

    def cmd_palette_select_change(self, event=None, *args, **kwargs):
        """Record the selected palette on the config."""
        value = None
        for attr in ("palette_select", "image_palette_select"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    value = getter()
                    break
        if value is not None:
            self.config.dikt["palette"] = value
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
        logma.info(f"Document {document}")
        self.document = self.app.model.codex.init_image(document)
        self.document.load_document()
        self.context_menu_name = "context.document.image"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        self.file_path = self.document.file_path
        logma.info(f"[NchantdOfficeImage] - {self.file_path}")
        return self

    def initView(self, cfg=None):
        """"""
        cfg = {
            "buttons": {
                # 10: {"action": "convert_format", "handler": self.cmd_convert_format},
                # 11: {"action": "convert_size", "handler": self.cmd_convert_size},
                # 12: {"action": "convert_color", "handler": self.cmd_convert_color},
                # 13: {"action": "crop_image", "handler": self.cmd_crop_image},
                # 14: {"action": "generate_image", "handler": self.cmd_generate_image},
                15: {
                    "action": "show_palette_drawer",
                    "handler": self.cmd_show_palette_drawer,
                },
                16: {
                    "action": "scan_palette_from_image",
                    "handler": self.cmd_run_palette_scan,
                },
                49: "_insert_stretch",
            }
        }
        image_cfg = {
            "size": ["auto", "auto"],
            "document": self.document,
            "path": self.document.file_path,
            # T-NEW-NOTE: scale image to fit the tab width while
            # preserving aspect ratio (nchantrs NchantdImage
            # sets `setScaledContents(False)` by default, which
            # displays the image at its native size and pushes
            # the tab width to the image's pixel width).
            # T-NEW-063: ``scaled=True`` alone uses Qt's
            # IgnoreAspectRatio, which stretches the image to
            # fill BOTH axes (the symptom from
            # testing-report_20260810.md line 6). The
            # post-init override below constrains the label's
            # height to the available tab height so Qt
            # honours the aspect ratio when scaling.
            "scaled": True,
        }
        if self.document.content is not None:
            image_cfg["image_data"] = self.document.content.get("L0", {}).get("bytes", None)
            logma.info(f"Image Data: {image_cfg['image_data']}")
        self.image = NchantdImage(self, image_cfg).initWidget()
        # T-NEW-063 — post-init override: constrain the inner
        # label's height to the tab's available height so Qt
        # keeps the aspect ratio when setScaledContents(True)
        # scales the pixmap. Without this, ``scaled=True``
        # causes the image to stretch to fill the label's
        # width AND height (the symptom reported in
        # testing-report_20260810.md line 6). We read the
        # parent tab's available height (the parent layout
        # slot the widget sits in) and cap the label's
        # maximum height there. Falls back to a sensible
        # default if the parent geometry isn't readable yet.
        try:
            label = getattr(self.image, "label", None)
            if label is not None and hasattr(label, "setMaximumHeight"):
                # Prefer the actual parent height; fall back to
                # 600 px (matches the default tab body height
                # in NchantdOfficeMainWindow).
                parent_h = None
                parent = self.parent()
                if parent is not None and hasattr(parent, "height"):
                    try:
                        parent_h = int(parent.height())
                    except Exception:
                        parent_h = None
                if not parent_h or parent_h <= 0:
                    parent_h = 600
                label.setMaximumHeight(parent_h)
                # Preferred-size policy that lets Qt compute
                # the aspect-ratio-correct width when the
                # height is capped. Maximum = the parent's
                # height (so the image never overflows);
                # Preferred lets the layout pick the natural
                # width at the constrained height.
                policy = pyqt.QSizePolicy(
                    pyqt.QSizePolicy.Policy.Preferred,
                    pyqt.QSizePolicy.Policy.Preferred,
                )
                label.setSizePolicy(policy)
                # Force an immediate re-scale so the change
                # is visible without waiting for a resize event.
                if hasattr(self.image, "refresh"):
                    self.image.refresh()
        except Exception as e:
            logma.warning(
                f"[NchantdOfficeImage] T-NEW-063 post-init override failed: {e}",
                exc_info=True,
            )
        super().initView(cfg)

        logma.info(f"Content {self.document.content}")
        # self.file_path = (
        #     self.document.file_path
        #     or self.config.dikt.get("file_path")
        #     or (self.document.content or {}).get("file_path")
        #     or (self.document.content or {}).get("content", {}).get("file_path")
        # )

        # PUSH to 0.0.3 force external until
        self.document.set_location("external")

        # if self.document.location == "external":
        #     self.open_file(self.document.file_path)
        # # PUSH to 0.0.3
        # # elif self.document.location == "internal":
        # #    self.populate_data()
        # # elif self.document.location == "cloud":
        # #    self.connect_to_file()
        # else:
        #     raise Exception("Internal and Cloud locations not supported yet")
        self.layout.addWidget(self.image)
        self.layout.setSpacing(3)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_add_palette_document_nchantdpalette(self, event=None, *args, **kwargs):
        """Add a new palette document to the active palette set."""
        # TODO Open toolbox tab and Palette Drawer generate the palette from the image
        try:
            name = None
            for attr in ("palette_select", "image_palette_select"):
                widget = getattr(self, attr, None)
                if widget is not None:
                    getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                    if callable(getter):
                        name = getter()
                        break
            if not name:
                return self
            model = getattr(self, "app", None)
            if model is not None and hasattr(model, "model"):
                model = model.model
            if model is not None and hasattr(model, "add_palette_document"):
                from nchantdoffice.widgets.documents.atnrg.palettes import NchantdPalette

                model.add_palette_document(NchantdPalette(name=name, parent=model))
        except Exception as e:
            logma.error(f"[images] cmd_add_palette_document_nchantdpalette failed: {e}", exc_info=True)
        return self

    def cmd_convert_color(self, event=None, *args, **kwargs):
        """Convert the image to the selected target color.

        Reads the target color from the convert-color dropdown and
        calls ``self.apply_color_shift`` with the new color when
        available.
        """
        target = None
        for attr in ("target_color_select", "convert_color_select", "color_target_select"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    target = getter()
                    break
        if target is not None and hasattr(self, "apply_color_shift") and callable(self.apply_color_shift):
            self.apply_color_shift(target)
            self.config.dikt["converted_color"] = target
        return self

    def cmd_convert_format(self, event=None, *args, **kwargs):
        """Convert the current image to the target format."""
        # target = None
        # for attr in ("target_format_select", "convert_format_select", "format_target_select"):
        #     widget = getattr(self, attr, None)
        #     if widget is not None:
        #         getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
        #         if callable(getter):
        #             target = getter()
        #             break
        # if target is not None and hasattr(self, "convert_image_format") and callable(self.convert_image_format):
        self.convert_image_format()
        return self

    def cmd_convert_size(self, event=None, *args, **kwargs):
        """Convert the image to the configured target size."""
        target = self.config.dikt.get("convert_to_size")
        if target is None:
            for attr in ("convert_size_select", "target_size_select"):
                widget = getattr(self, attr, None)
                if widget is not None:
                    getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                    if callable(getter):
                        target = getter()
                        break
        if target is not None and hasattr(self, "apply_convert_size") and callable(self.apply_convert_size):
            self.apply_convert_size(target)
        return self

    def cmd_crop_image(self, event=None, *args, **kwargs):
        """Crop the image to the configured crop region."""
        try:
            region = self.config.dikt.get("crop_region", {}) or {}
            if hasattr(self, "apply_crop") and callable(self.apply_crop):
                self.apply_crop(region)
        except Exception as e:
            logma.error(f"[images] cmd_crop_image failed: {e}", exc_info=True)
        return self

    def cmd_generate_image(self, event=None, *args, **kwargs):
        """Generate an image from the configured source / prompt."""
        prompt = self.config.dikt.get("image_prompt", "")
        if hasattr(self, "generate_image") and callable(self.generate_image):
            try:
                return self.generate_image(prompt=prompt)
            except TypeError:
                return self.generate_image()
        return self

    def cmd_image_height_change(self, event=None, *args, **kwargs):
        """Update the image-height field on the config."""
        height = None
        for attr in ("image_height_select", "image_height_spinbox"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "value", None)
                if callable(getter):
                    height = getter()
                    break
        if height is not None:
            self.config.dikt["image_height"] = height
        return self

    def cmd_open_tool_drawer(self, tool_name=None, *args, **kwargs):
        """Show only the named tool pane in the image drawer.

        T-NEW-035 close-out: was the inline TODO at images.py:949
        ("implement logic so that when a tool like
        NchantdConvertSize button is clicked on the document
        toolbar the drawer is opened and redrawn to show only
        the config for that tool"). Hides the other 4 panes so
        the user sees only the named tool's config.

        Args:
            tool_name: one of "format_conversion",
                "size_conversion", "color_shift", "crop",
                "generator". When None or empty, all panes
                are hidden (no-op show). When the name doesn't
                match any pane, all panes are hidden (defensive).

        Returns ``self`` for chainable call sites.
        """
        # Map of tool_name -> attribute name on the pane.
        # T-NEW-055 added "palette" so the Show Palette button
        # (T-NEW-055) can open the palette drawer via the same
        # mechanism.
        panes = [
            ("format_conversion", "image_format_conversion_pane"),
            ("size_conversion", "image_size_conversion_pane"),
            ("color_shift", "image_color_shift_pane"),
            ("crop", "image_crop_pane"),
            ("generator", "image_generator_pane"),
            ("palette", "image_palette"),
        ]
        try:
            for _, attr_name in panes:
                widget = getattr(self, attr_name, None)
                if widget is not None and hasattr(widget, "hide"):
                    try:
                        widget.hide()
                    except Exception:
                        pass
            # Re-show the named pane (if it matches and exists)
            if tool_name:
                for tool_key, attr_name in panes:
                    if tool_key == tool_name:
                        widget = getattr(self, attr_name, None)
                        if widget is not None and hasattr(widget, "show"):
                            try:
                                widget.show()
                            except Exception:
                                pass
                        break
        except Exception as e:
            logma.warning(f"[images] cmd_open_tool_drawer failed: {e}")
        return self

    def cmd_open_local_file(self, event=None, *args, **kwargs):
        """"""
        super().cmd_open_local_file(event, *args, **kwargs)
        if self.local_file is not None:
            if exists(self.local_file):
                self.open_file(self.local_file)
        return self

    def cmd_run_palette_scan(self, event=None, *args, **kwargs):
        """Run a palette scan on the current image."""
        try:

            path = getattr(self, "local_file", None) or self.config.dikt.get("image_path")
            if not path or not exists(path):
                logma.warning("[images] cmd_run_palette_scan: no image path")
                return self
            cfg = {}
            palette = PyfficeColorPalette(cfg).extract_palette(path)
            self.config.dikt["palette_scan"] = palette
        except Exception as e:
            logma.error(f"[images] cmd_run_palette_scan failed: {e}", exc_info=True)
        return self

    def cmd_show_palette_drawer(self, event=None, *args, **kwargs):
        """Open the palette drawer with the current image's color list.

        T-NEW-055: scans the image for its color palette (or
        uses the cached ``config.dikt["palette_scan"]``), then opens
        the toolbox drawer where the palette document is displayed
        with a list of colors and percentage usage in the image.

        Best-effort: any exception is logged and the drawer is
        opened with whatever's available (cached palette, default
        palette, etc.).
        """
        try:
            # Re-run the palette scan if no cached palette exists.
            if not self.config.dikt.get("palette_scan"):
                try:
                    self.cmd_run_palette_scan()
                except Exception as exc:
                    logma.warning(f"[images] cmd_show_palette_drawer: palette scan " f"failed: {exc}")
            # Refresh the palette table widget now that we have data.
            palette = self.config.dikt.get("palette_scan") or {}
            self._populate_palette_table(palette)
            # Open the toolbox / drawer.
            if hasattr(self, "cmd_open_tool_drawer"):
                try:
                    self.cmd_open_tool_drawer("palette")
                except Exception as exc:
                    logma.warning(f"[images] cmd_show_palette_drawer: open drawer " f"failed: {exc}")
            logma.info("[images] cmd_show_palette_drawer: palette drawer opened")
        except Exception as e:
            logma.error(f"[images] cmd_show_palette_drawer failed: {e}", exc_info=True)
        return self

    def _populate_palette_table(self, palette):
        """Populate the palette table widget from a palette dict.

        T-NEW-055 helper: the palette dict shape is::

            {"colors": [{"hex": "#rrggbb", "count": <int>, "percent": <float>}, ...]}

        Falls back to a flat list of (hex, count) tuples when the
        dict shape is unknown. Best-effort: any exception is logged
        and swallowed so the drawer still opens.
        """
        try:
            table = getattr(self, "image_palette", None)
            if table is None:
                return
            rows = []
            colors = palette.get("colors") if isinstance(palette, dict) else None
            if colors is None and isinstance(palette, (list, tuple)):
                # Flat list of (hex, count, percent) tuples
                for entry in palette:
                    if isinstance(entry, dict):
                        rows.append(
                            {
                                "hex": entry.get("hex"),
                                "usage": entry.get("percent", entry.get("usage", 0)),
                                "count": entry.get("count", 0),
                            }
                        )
                    elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
                        rows.append(
                            {
                                "hex": entry[0],
                                "usage": entry[2] if len(entry) >= 3 else 0,
                                "count": entry[1],
                            }
                        )
            elif colors:
                for entry in colors:
                    rows.append(
                        {
                            "hex": entry.get("hex") if isinstance(entry, dict) else None,
                            "usage": entry.get("percent", 0) if isinstance(entry, dict) else 0,
                            "count": entry.get("count", 0) if isinstance(entry, dict) else 0,
                        }
                    )
            # Delegate to the table's populator when available.
            if hasattr(table, "set_data"):
                try:
                    table.set_data(rows)
                    return
                except Exception:
                    pass
            if hasattr(table, "populate"):
                try:
                    table.populate(rows)
                except Exception:
                    pass
        except Exception as e:
            logma.warning(f"[images] _populate_palette_table failed: {e}")

    def cmd_image_width_change(self, event=None, *args, **kwargs):
        """Update the image-width field on the config."""
        width = None
        for attr in ("image_width_select", "image_width_spinbox"):
            widget = getattr(self, attr, None)
            if widget is not None:
                getter = getattr(widget, "value", None)
                if callable(getter):
                    width = getter()
                    break
        if width is not None:
            self.config.dikt["image_width"] = width
        return self

    def convert_image_format(self, output_format):
        """"""
        self.document.convert_to(output_format)

    def get_binary(self):
        """Return the stored value of get_binary."""
        return self.config.dikt.get("file_binary", b"") or b""

    def get_content(self):
        """"""
        logma.info(f"File Path {self.file_path}")
        return {"content": {"file_path": self.file_path}}

    def get_image_height(self):
        """Return the stored value of get_image_height."""
        return self.config.dikt.get("image_height", 0) or 0

    def get_image_width(self):
        """Return the stored value of get_image_width."""
        return self.config.dikt.get("image_width", 0) or 0

    def init_drawer_document_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "File Name: ", "layout": "horizontal", "file_path": self.document.file_path}
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
        """Build the image-tools drawer.

        Five panes (format / size / color / crop / generator) are placed
        in sequence, each as a separate item slot. The shared helper
        centralises the slot-creation branch.
        """
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        # TODO implement logic so that when a tool like NchantdConvertSize button is clicked on the document toolbar that the drawer is opened and redrawn to show only the config for that tool
        # Format conversion
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.image_format_conversion_pane = NchantdConvertFormatPane(
            self,
            {"text": ""},
        )
        cnt += 1

        # Size conversion
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.image_size_conversion_pane = NchantdConvertSizePane(
            self,
            {"text": ""},
        )
        cnt += 1

        # Color shift
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.image_color_shift_pane = NchantdColorShiftPane(
            self,
            {"text": ""},
        )
        cnt += 1

        # Crop
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.image_crop_pane = NchantdImageCropPane(
            self,
            {"text": ""},
        )
        cnt += 1

        # Generator
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.image_generator_pane = NchantdImageGeneratorPane(
            self,
            {"text": ""},
        )
        cnt += 1

        return items

    def init_drawer_palette(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {"text": "Scan to Extract Palette", "handler": self.cmd_run_palette_scan}
        self.image_scan_palette_button = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.image_scan_palette_button
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "text": "Modify Palette: ",
            "num_columns": 3,
            "num_rows": 10,
            "columns": ["Color", "Hex", "Usage %"],
            "column_width": 10,
        }
        self.image_palette = NchantdPaletteTable(self, cfg)
        items[cnt]["widget"] = self.image_palette
        cnt += 1
        return items

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
        # PUSH to 0.0.3
        # self.toolbox_config[200]["items"] = self.init_drawer_image_tools()
        self.toolbox_config[300]["items"] = self.init_drawer_palette()
        # PUSH to 0.0.3
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
        """Populate the image widget from the document's binary data.

        T-036: prefers the in-memory ``PyfficeDocument.binary`` /
        ``PyfficeDocument.bytes`` when set (avoids re-reading the
        file from disk and works for documents that originated
        from a database blob). Falls back to ``load_image(file_path)``
        when no binary is available.
        """
        super().populate_document()
        logma.info(f"[images] Populate image {self.file_path}")
        doc = getattr(self, "document", None)
        if doc.location == "internal":
            binary = None
            if doc is not None:
                binary = getattr(doc, "binary", None) or getattr(doc, "bytes", None) or getattr(doc, "data", None)
            if binary and hasattr(doc, "load_image_bytes"):
                try:
                    doc.load_image_bytes(binary)
                    return self
                except Exception as e:
                    logma.error(f"[images] populate_document: load_image_bytes failed: {e}", exc_info=True)
        elif doc.location == "external":
            if self.file_path and hasattr(self.image, "load_image"):
                self.image.load_image(self.file_path)
        return self

    def save(self):
        """"""
        super().save()
        return self

    def _ensure_drawer_item(self, items, cnt):
        """Lazily create a default drawer-item slot.

        Centralises the ``if cnt not in items: items[cnt] = {...}``
        pattern used by every ``init_drawer_*`` method on this class,
        removing the repeated branch flagged by the maintainability
        auditor as switch abuse.
        """
        if cnt not in items:
            items[cnt] = {
                "action": "insert_generic_action",
                "type": "custom",
            }
        return items[cnt]


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
