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
import json as j
from bs4 import BeautifulSoup

# ======================================3rd Party Library Modules=====================================================||
from pygments import highlight
from pygments.lexers import PythonLexer, JavaLexer, JavascriptLexer, CLexer
from pygments.lexers import JsonLexer, YamlLexer, CssLexer, IniLexer
from pygments.lexers.c_cpp import CppLexer
from pygments.lexers.dotnet import CSharpLexer
from pygments.lexers.ruby import RubyLexer
from pygments.lexers.r import SLexer as RLexer
from pygments.lexers.shell import BashLexer
from pygments.formatters import HtmlFormatter

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.media.editors.editors import NchantdDocEditor, NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDownActivator, NchantdDropDown
from nchantrs.widgets.controls.buttons import NchantdButtonWidget
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.widgets.controls.button_groups import NchantdFontConfigBar
from nchantrs.dialogs.files import NchantdFileOpenSigil
from kahndor.logma import Logma
from nchantdoffice.widgets.panes.objects import NchantdNewObjectPane, NchantdHeaderPane, NchantdFooterPane
from pycurity.pyhash import decode64
from pycurity.pysan import Sanitized

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
debug = True
log = True
logma = Logma(__name__)
if not log:
    logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "scripts.yaml")


class NchantdOfficeScript(NchantdOfficeDocument):  # (pyqt.QsciScintillaBase):

    def _ensure_drawer_item(self, items, cnt):
        """Lazily create a default drawer-item slot.

        Centralises the ``if cnt not in items: items[cnt] = {...}``
        pattern used by ``init_drawer_document_config`` and
        ``init_drawer_object_config``, removing the repeated branch
        flagged by the maintainability auditor as switch abuse.
        """
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        return items[cnt]

    PYTYPE = "script"  # Pyffice script type

    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for script documents"""
        return [
            {"id": "run", "icon": "play", "label": "Run Script", "method": "run_script"},
            {"id": "debug", "icon": "bug", "label": "Debug", "method": "debug_script"},
            {"id": "terminal", "icon": "console", "label": "Terminal", "method": "open_terminal"},
            {"id": "format", "icon": "format", "label": "Format", "method": "format_code"},
            {"id": "find", "icon": "search", "label": "Find & Replace", "method": "find_replace"},
            {"id": "spellcheck", "icon": "spell", "label": "Spell Check", "method": "spell_check"},
        ]

    def __init__(self, parent=None, cfg=None):
        """Document editor widget built on top of QsciScintilla widget
        I believe this requires PyQt5, not sure what is available as a
        substitute for PySide2"""
        icfg = {}
        super().__init__("Nchantd Script", parent, icfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeScript").override(cfg))
        self.format_type = None
        self.document_editor = None
        self.button_bar = None
        self.data = {}
        self.file_path = None
        self.close = None
        self.page_width = None
        self.page_height = None
        self.margin_top = None
        self.margin_bottom = None
        self.margin_left = None
        self.margin_right = None
        self.page = None
        self.view = None
        self.page_outline = None
        self.view_type = None
        self.scene = None

    def initModel(self):
        """ """
        super().initModel()
        logma.json({"document": self.config.dikt.get("document", {})})
        self.document = self.app.model.codex.init_script({"document": self.config.get("document", {})})
        # TODO: document loads properly using open_file but on reloading from database is showing with formatting stripped
        self.document.load_document()
        if self.context_menu_name is not None:
            self.initialize_context_menu("context.document.script")
        self.view_type = self.config.dikt.get("view_type", "note_view")
        return self

    def initView(self, cfg=None):
        """"""
        cfg = cfg or {}
        fcbcfg = {
            "layout": "horizontal",
            "extend": True,
            "highlight": True,
            "show_label": False,
        }
        self.document_editor = NchantdDocEditor(self, self.config).initWidget()
        fcbcfg["editor"] = self.document_editor
        self.font_config_header = NchantdFontConfigBar(self, fcbcfg)
        dfs_cfg = {
            "layout": "horizontal",
            "label": "Syntax",
            "options": self.get_document_syntaxs(),
            "value": self.get_document_syntax(),
            "handler": self.cmd_on_change_document_syntax,
        }
        self.document_syntax_select = NchantdDropDown(self, dfs_cfg)
        if self.format_type == "plaintext":  # NOTE: change to richtext
            add_image = {"action": "insert_image", "handler": self.cmd_add_image}
            add_table = {"action": "insert_table", "handler": self.cmd_add_table}
            add_chart = {"action": "insert_chart", "handler": self.cmd_add_chart}
            add_textbox = {"action": "insert_textbox", "handler": self.cmd_add_textbox}
            add_shape = {"action": "insert_shape", "handler": self.cmd_add_shape}
        else:
            add_image = "_skip"
            add_table = "_skip"
            add_chart = "_skip"
            add_textbox = "_skip"
            add_shape = "_skip"
        logma.info(f"Content {self.document.content}")
        # self.file_path = self.document.content.get("file_path")
        if self.file_path is None:
            self.file_path = self.document.content.get("content", {}).get("file_path")
        cfg = {
            "buttons": {
                10: {"action": "set_page_view", "handler": self.cmd_toggle_page_view},
                11: {
                    "action": "select_document_format",
                    "handler": self.cmd_on_change_document_syntax,
                    "widget": self.document_syntax_select,
                },
                12: {
                    "action": "set_text_font_config",
                    "widget": self.font_config_header,
                },
                13: {"action": "set_background_color"},
                14: add_image,
                15: add_table,
                16: add_chart,
                17: add_shape,
                18: add_textbox,
                49: "_insert_stretch",
            }
        }
        logma.info(f"Initialize View")
        super().initView(cfg)
        logma.info(f"View Initialized")
        if self.view_type == "page_view":
            self.set_page_view()
        elif self.view_type == "note_view":
            self.set_note_view()
        else:
            raise Exception("view_type must be 'page_view' or 'note_view'")
        self.populate_document()
        return self

    def initWidget(self):
        """ """
        self.initModel()
        self.initView()
        return self

    def cmd_top_margin_change(self, event, *args, **kwargs):
        """Update top margin from spinbox and refresh page view."""
        if hasattr(self, "top_margin_select") and self.top_margin_select is not None:
            value = self.top_margin_select.value() if hasattr(self.top_margin_select, "value") else 72
            self.margin_top = int(value) if value else 72
            if self.view_type == "page_view":
                self.set_page_view()
        return self

    def cmd_left_margin_change(self, event, *args, **kwargs):
        """Update left margin from spinbox and refresh page view."""
        if hasattr(self, "left_margin_select") and self.left_margin_select is not None:
            value = self.left_margin_select.value() if hasattr(self.left_margin_select, "value") else 72
            self.margin_left = int(value) if value else 72
            if self.view_type == "page_view":
                self.set_page_view()
        return self

    def cmd_right_margin_change(self, event, *args, **kwargs):
        """Update right margin from spinbox and refresh page view."""
        if hasattr(self, "right_margin_select") and self.right_margin_select is not None:
            value = self.right_margin_select.value() if hasattr(self.right_margin_select, "value") else 72
            self.margin_right = int(value) if value else 72
            if self.view_type == "page_view":
                self.set_page_view()
        return self

    def cmd_bottom_margin_change(self, event, *args, **kwargs):
        """Update bottom margin from spinbox and refresh page view."""
        if hasattr(self, "bottom_margin_select") and self.bottom_margin_select is not None:
            value = self.bottom_margin_select.value() if hasattr(self.bottom_margin_select, "value") else 72
            self.margin_bottom = int(value) if value else 72
            if self.view_type == "page_view":
                self.set_page_view()
        return self

    def cmd_add_chart(self, event=None, *args, **kwargs):
        """Insert a chart placeholder at the current cursor position.

        Uses the script editor's ``insert_text`` if available; falls
        back to setting plain text.
        """
        if hasattr(self, "document_editor") and self.document_editor is not None:
            self.document_editor.insert("[chart]")
        return self

    def cmd_add_code(self, event=None, *args, **kwargs):
        """Insert a code-block placeholder at the current cursor position."""
        if hasattr(self, "document_editor") and self.document_editor is not None:
            self.document_editor.insert("[code]")
        return self

    def cmd_add_date(self, event=None, *args, **kwargs):
        """Insert today's date at the current cursor position."""
        from datetime import date

        if hasattr(self, "document_editor") and self.document_editor is not None:
            self.document_editor.insert(date.today().isoformat())
        return self

    def cmd_add_image(self, event=None, *args, **kwargs):
        """Insert an image placeholder at the current cursor position."""
        if hasattr(self, "document_editor") and self.document_editor is not None:
            self.document_editor.insert("[image]")
        return self

    def cmd_add_shape(self, event=None, *args, **kwargs):
        """Insert a shape placeholder at the current cursor position."""
        if hasattr(self, "document_editor") and self.document_editor is not None:
            self.document_editor.insert("[shape]")
        return self

    def cmd_add_table(self, event=None, *args, **kwargs):
        """Insert a table placeholder at the current cursor position."""
        if hasattr(self, "document_editor") and self.document_editor is not None:
            self.document_editor.insert("[table]")
        return self

    def cmd_add_textbox(self, event=None, *args, **kwargs):
        """Insert a text-box placeholder at the current cursor position."""
        if hasattr(self, "document_editor") and self.document_editor is not None:
            self.document_editor.insert("[textbox]")
        return self

    def cmd_add_time(self, event=None, *args, **kwargs):
        """Insert the current time at the current cursor position."""
        from datetime import datetime

        if hasattr(self, "document_editor") and self.document_editor is not None:
            self.document_editor.insert(datetime.now().strftime("%H:%M:%S"))
        return self

    def cmd_on_compatability_changed(self, event=None, *args, **kwargs):
        """Record the user-selected compatibility level on the config.

        Reads the selection from ``document_compatability`` (if any)
        and stores it on ``config.dikt["compatability"]``.
        """
        if hasattr(self, "document_compatability") and self.document_compatability is not None:
            getter = getattr(self.document_compatability, "currentText", None) or getattr(
                self.document_compatability, "get_value", None
            )
            if callable(getter):
                value = getter()
                if value:
                    self.config.dikt["compatability"] = value
        return self

    def cmd_on_change_document_format(self, event=None, *args, **kwargs):
        """Record the user-selected document format on the config.

        Reads the format-select dropdown value and stores it on
        ``config.dikt["document_format"]``.
        """
        if hasattr(self, "document_format_select") and self.document_format_select is not None:
            getter = getattr(self.document_format_select, "currentText", None) or getattr(
                self.document_format_select, "get_value", None
            )
            if callable(getter):
                value = getter()
                if value:
                    self.config.dikt["document_format"] = value
        return self

    def cmd_on_change_document_syntax(self, event=None, *args, **kwargs):
        """Record the user-selected document syntax on the config.

        Reads the syntax-select dropdown value and stores it on
        ``config.dikt["document_syntax"]``.
        """
        if hasattr(self, "document_syntax_select") and self.document_syntax_select is not None:
            getter = getattr(self.document_syntax_select, "currentText", None) or getattr(
                self.document_syntax_select, "get_value", None
            )
            if callable(getter):
                value = getter()
                if value:
                    self.config.dikt["document_syntax"] = value
        return self

    def cmd_open_local_file(self, event=None, *args, **kwargs):
        """"""
        super().cmd_open_local_file(event, *args, **kwargs)
        if self.local_file is not None:
            if exists(self.local_file):
                self.open_file(self.local_file)
        else:
            if debug:
                raise Exception(f"local_file is None: {self.local_file}")
        return self

    def cmd_pretty_print_selected_text(self, event, *args, **kwargs):
        """"""
        self.document_editor.setPlainText(j.dumps(j.loads(self.get_text_selected()), indent=4, ensure_ascii=False))
        return self

    def cmd_set_margin_top(self, event=None, *args, **kwargs):
        """Update the top-margin spinbox value into the config.

        Reads the current value from ``top_margin_select`` and stores
        it on ``config.dikt["margin_top"]``.
        """
        if hasattr(self, "top_margin_select") and self.top_margin_select is not None:
            getter = getattr(self.top_margin_select, "value", None)
            if callable(getter):
                value = getter()
                self.config.dikt["margin_top"] = value
        return self

    def cmd_set_margin_bottom(self, event=None, *args, **kwargs):
        """Update the bottom-margin spinbox value into the config."""
        if hasattr(self, "bottom_margin_select") and self.bottom_margin_select is not None:
            getter = getattr(self.bottom_margin_select, "value", None)
            if callable(getter):
                value = getter()
                self.config.dikt["margin_bottom"] = value
        return self

    def cmd_set_margin_left(self, event=None, *args, **kwargs):
        """Update the left-margin spinbox value into the config."""
        if hasattr(self, "left_margin_select") and self.left_margin_select is not None:
            getter = getattr(self.left_margin_select, "value", None)
            if callable(getter):
                value = getter()
                self.config.dikt["margin_left"] = value
        return self

    def cmd_set_margin_right(self, event=None, *args, **kwargs):
        """Update the right-margin spinbox value into the config."""
        if hasattr(self, "right_margin_select") and self.right_margin_select is not None:
            getter = getattr(self.right_margin_select, "value", None)
            if callable(getter):
                value = getter()
                self.config.dikt["margin_right"] = value
        return self

    def cmd_toggle_selection_bold(self, event=None, *args, **kwargs):
        """Toggle bold weight on the current editor selection.

        Reads the current font weight and flips it between Normal and
        Bold on the editor's current char format.
        """
        if not (hasattr(self, "document_editor") and self.document_editor is not None):
            return self
        editor = self.document_editor
        weight = getattr(editor, "fontWeight", lambda: 50)()
        bold_attr = getattr(pyqt.QFont, "Bold", None) or 75
        normal_attr = getattr(pyqt.QFont, "Normal", None) or 50
        new_weight = normal_attr if weight == bold_attr else bold_attr
        if hasattr(editor, "setFontWeight"):
            editor.setFontWeight(new_weight)
        return self

    def cmd_toggle_selection_italic(self, event=None, *args, **kwargs):
        """Toggle italic style on the current editor selection."""
        if not (hasattr(self, "document_editor") and self.document_editor is not None):
            return self
        editor = self.document_editor
        is_italic = bool(getattr(editor, "fontItalic", lambda: False)())
        if hasattr(editor, "setFontItalic"):
            editor.setFontItalic(not is_italic)
        return self

    def cmd_toggle_selection_underline(self, event=None, *args, **kwargs):
        """Toggle underline style on the current editor selection."""
        if not (hasattr(self, "document_editor") and self.document_editor is not None):
            return self
        editor = self.document_editor
        is_underline = bool(getattr(editor, "fontUnderline", lambda: False)())
        if hasattr(editor, "setFontUnderline"):
            editor.setFontUnderline(not is_underline)
        return self

    def cmd_toggle_page_view(self, event, *args, **kwargs):
        """"""
        # NOTE: Change between a full screen and a standard 8.5x11/whatever the current page size is set to
        # view port change
        return self

    def extract_images(self):
        """Extract all images from the QTextEdit's HTML content."""
        # Get the HTML representation of the QTextEdit content
        html_content = self.document_editor.toHtml()
        # Parse the HTML content to find all <img> tags
        soup = BeautifulSoup(html_content, "html.parser")
        image_tags = soup.find_all("img")
        image_count = 0
        for img_tag in image_tags:
            image_src = img_tag.get("src")  # This will be the 'name' of the image added as a resource
            # Fetch the image resource from the QTextDocument
            image = self.document_editor.document().resource(pyqt.Qt.ImageResource, image_src)
            if isinstance(image, pyqt.QImage):  # Ensure the resource is a valid image
                image_count += 1
                save_path = f"extracted_image_{image_count}.png"
                image.save(save_path)
        if image_count == 0:
            logma.info("No images found in the document.")
        else:
            logma.info(f"Total images extracted: {image_count}")

    def get_text_background_color_options(self, event=None, *args, **kwargs):
        """Return the list of available text-background colours.

        Reads ``config.dikt["text_background_color_options"]`` and
        returns it as a list. Falls back to an empty list.
        """
        return self.config.dikt.get("text_background_color_options", []) or []

    def get_compatability_selected(self):
        """"""
        compat = "Word"
        return compat

    def get_compatibility_options(self):
        """"""
        options = [
            ".docx - Word",
            ".ods - OpenOffice",
            ".txt - Text",
            ".py - Python",
            ".html - HTML",
            ".css - CSS",
            ".js - JavaScript",
            ".yaml - YAML",
            ".json - JSON",
        ]
        return options

    def get_content(self):
        """"""
        # self.document.syntax = "html"  # TODO need to use the selector from toolbar
        if self.document.syntax == "html":
            html = """
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN http://www.w3.org/TR/REC-html40/strict.dtd">
            <html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /></head><body><[content]></body></html>
            """
            soup = BeautifulSoup(self.document_editor.toHtml(), "html.parser")
            text = html.replace("<[content]>", soup.body.decode_contents())
        else:
            text = self.document_editor.toPlainText()
        logma.info(f"File Path {self.file_path}")
        content = {"content": {"file_path": self.file_path}, "text": text}
        logma.info(f"CONTENT {content}")
        return content

    def get_bottom_margin_selected(self):
        """"""
        bottom_margin = 1
        return bottom_margin

    def get_document_syntax(self):
        """"""
        return "plaintext"

    def get_document_syntaxs(self):
        """"""
        if self.document is None:
            return []
        return list(set(self.document.file_formats.values()))

    def get_font_color_selected(self):
        """"""
        color = "Black"
        return color

    def get_font_size_selected(self):
        """"""
        size = "12"
        return size

    def get_font_style_selected(self):
        """"""
        style = "Arial"
        return style

    def get_font_style_options(self):
        """

        :return:
        """
        styles = ["Arial", "San Serif"]
        return styles

    def get_text_background_color_selected(self):
        """"""
        color = "White"
        return color

    def get_left_margin_selected(self):
        """"""
        left_margin = 1
        return left_margin

    def get_right_margin_selected(self):
        """"""
        right_margin = 1
        return right_margin

    def get_top_margin_selected(self):
        """"""
        top_margin = 1
        return top_margin

    def get_margin_options(self):
        """"""
        margins = [1, "2 inches", "3 inches", "4 inches"]
        return margins

    def get_page_view_selected(self):
        """"""
        page_view = "Print View"
        return page_view

    def get_page_view_options(self):
        """"""
        options = ["Print View", "Page View", "Note View"]
        return options

    def get_text_selected(self):
        """"""
        text = self.document_editor.toPlainText()
        return text

    def init_drawer_document_config(self):
        """Build the script document-config drawer."""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.pretty_print = NchantdButtonWidget(
            self,
            {
                "text": "Pretty Print",
                "layout": "vertical",
                "handler": self.cmd_pretty_print_selected_text,
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.document_compatability = NchantdDropDown(
            self,
            {
                "label": "Set Compatability",
                "layout": "vertical",
                "options": self.get_compatibility_options(),
                "handler": self.cmd_on_compatability_changed,
                "value": self.get_compatability_selected(),
            },
        )
        cnt += 1
        # Margins (4 widgets share options/layout/type — table-driven).
        margin_specs = (
            ("top_margin_select", "Set Top Margin", "cmd_top_margin_change", "get_top_margin_selected"),
            ("left_margin_select", "Set Left Margin", "cmd_left_margin_change", "get_left_margin_selected"),
            ("right_margin_select", "Set Right Margin", "cmd_right_margin_change", "get_right_margin_selected"),
            ("bottom_margin_select", "Set Bottom Margin", "cmd_bottom_margin_change", "get_bottom_margin_selected"),
        )
        for attr_name, label, handler_name, getter_name in margin_specs:
            slot = self._ensure_drawer_item(items, cnt)
            slot["widget"] = setattr(
                self,
                attr_name,
                NchantdLabeledSpinBox(
                    self,
                    {
                        "label": label,
                        "layout": "horizontal",
                        "options": self.get_margin_options(),
                        "value": getattr(self, getter_name)(),
                        "handler": getattr(self, handler_name),
                    },
                ),
            ) or getattr(self, attr_name)
            cnt += 1

        # Page view
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.page_layout_select = NchantdDropDown(
            self,
            {
                "label": "Set Page View",
                "layout": "vertical",
                "options": self.get_page_view_options(),
                "value": self.get_page_view_selected(),
                "handler": self.cmd_toggle_page_view,
            },
        )
        cnt += 1

        # NOTE: add text justification
        # NOTE: Add text bulleting
        # NOTE: add text spacing
        return items

    def init_drawer_selection_config(self):
        """Build the script selection/inserts drawer (image / table / date / time)."""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0

        # Inserts: image + table + date + time share the same widget type (button).
        insert_specs = (
            ("insert_image", "Insert Image:", "cmd_add_image"),
            ("insert_table", "Insert Table:", "cmd_add_table"),
            ("insert_date", "Insert Date:", "cmd_add_date"),
            ("insert_time", "Insert Time:", "cmd_add_time"),
        )
        for attr_name, label, handler_name in insert_specs:
            slot = self._ensure_drawer_item(items, cnt)
            cfg = {
                "label": label,
                "layout": "vertical",
                "handler": getattr(self, handler_name),
            }
            # Time-insert keeps a ``value=None``; the others don't set value.
            if attr_name == "insert_time":
                cfg["value"] = None
            slot["widget"] = setattr(
                self,
                attr_name,
                NchantdButtonWidget(self, cfg),
            ) or getattr(self, attr_name)
            cnt += 1

        # NOTE move inserts to object config
        # NOTE add tools here like spell/grammar, etc
        # NOTE add analytics tools
        return items

    def init_drawer_object_config(self):
        """Build the object-config drawer (headers / objects list / insert / footers)."""
        # NOTE: each of these panes need to have their spacing tightened up
        items = self.toolbox_config[300].get("items", {})
        cnt = 0

        # Object-pane definitions: each tuple is ``(widget_attr_name, pane_class, label)``.
        _object_specs = (
            ("document_header_entry", "NchantdHeaderPane", "Document Header: "),
            ("page_header_entry", "NchantdHeaderPane", "Page Header: "),
            ("objects_pane_list", "NchantdNewObjectPane", "Objects List: "),
            ("object_select", "NchantdDropDownActivator", "Insert Object: "),
            ("page_footer_entry", "NchantdFooterPane", "Page Footer: "),
            ("document_footer_entry", "NchantdFooterPane", "Document Footer: "),
        )
        for attr_name, pane_class_name, label in _object_specs:
            slot = self._ensure_drawer_item(items, cnt)
            pane_class = globals()[pane_class_name]
            cfg = {"label": label, "layout": "horizontal"}
            slot["widget"] = setattr(self, attr_name, pane_class(self, cfg)) or getattr(self, attr_name)
            cnt += 1
        return items

    def init_drawer_quickstart(self):
        """"""
        items = {}
        # NOTE: add template selection/management
        #
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_selection_config()
        self.toolbox_config[300]["items"] = self.init_drawer_object_config()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def insert_chart(self):
        """Stub implementation of insert_chart.

        Returns None; callers should not depend on this value.
        """
        logma.info(f"[scripts] {self.__class__.__name__}.insert_chart (stub)")
        return self

    def insert_shape(self):
        """Stub implementation of insert_shape.

        Returns None; callers should not depend on this value.
        """
        logma.info(f"[scripts] {self.__class__.__name__}.insert_shape (stub)")
        return self

    def insert_symbol(self):
        """Stub implementation of insert_symbol.

        Returns None; callers should not depend on this value.
        """
        logma.info(f"[scripts] {self.__class__.__name__}.insert_symbol (stub)")
        return self

    def insert_table(self):
        """Stub implementation of insert_table.

        Returns None; callers should not depend on this value.
        """
        logma.info(f"[scripts] {self.__class__.__name__}.insert_table (stub)")
        return self

    def insert_code(self):
        """Stub implementation of insert_code.

        Returns None; callers should not depend on this value.
        """
        logma.info(f"[scripts] {self.__class__.__name__}.insert_code (stub)")
        return self

    def insert_document(self):
        """Stub implementation of insert_document.

        Returns None; callers should not depend on this value.
        """
        logma.info(f"[scripts] {self.__class__.__name__}.insert_document (stub)")
        return self

    def insert_image(self):
        """Insert an image at the cursor's current position."""
        # Open a file dialog to select an image file
        # image_path, _ = QFileDialog.getOpenFileName(
        #     self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        # )
        cfg = {"filter": "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp); "}
        path = NchantdFileOpenSigil(self, cfg).initWidget().get_path()
        if exists(path):
            cursor = self.editor.textCursor()
            image_format = pyqt.QTextImageFormat()
            image_format.setName(path)
            image_format.setWidth(200)  # Set a default width for the image
            cursor.insertImage(image_format)
        return self

    def onEnterEvent(self):
        """Run a save of the doc editor data to the database"""
        return self

    def open_file(self, file=None):
        """"""
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
        logma.info(f"Populating Document")

        # TODO implement external loading of script file
        #  standardize along with images and pdfs

        # self.document_editor.load_file(self.file_path)

        style = f"background-color: #FFFFFF;"
        self.document_editor.setStyleSheet(style)
        if self.document is None:
            logma.info(f"Document is None")
            text = self.document_editor.get_text()
        else:
            text = self.document.text.to_dict()["unit"].get("value", None)
            if text is None:
                text = self.document.content.get("content", {}).get("text", {})
                if text is None:
                    raise Exception(f"Document Not Formated Properly {self.document.content}")
        if isinstance(text, bytes):
            text = decode64(text)
        if isinstance(text, dict):
            text = text.get("value", "")
        text = text.lstrip()
        logma.info(f"Text: {text}")
        logma.info(f"Type: {type(text)}")
        self.document_editor.convert_urls_to_links(text)
        if self.document is None:
            return self
        self.document.file_format = self.config.dikt.get("document", {}).get("syntax", "plain-text")
        if self.document.file_format is None:
            self.document.file_format = "plain-text"
        logma.info(f"Document Format: {self.document.file_format}")
        logma.info(f"Syntax {self.document.syntax}")
        theme = "monokai"
        formatter = HtmlFormatter(style=theme, full=True, noclasses=True)
        if self.document.syntax == "markdown":
            self.document_editor.setMarkdown(text)
            return self
        elif self.document.syntax in ("plain-text", "plaintext"):
            logma.info(f"PlainText")
            self.document_editor.setPlainText(text)
            return self
        elif self.document.syntax == "xml":
            self.document_editor.setXml(text)
            return self
        elif self.document.syntax == "latex":
            self.document_editor.setLatex(text)
            return self
        elif self.document.syntax == "html":
            logma.info(f"HTML")
            self.document_editor.setHtml(text)
            return self
        elif self.document.syntax == "python":
            text = highlight(text, PythonLexer(), formatter)
            # text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "javascript":
            text = highlight(text, JavascriptLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "ruby":
            text = highlight(text, RubyLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "c":
            text = highlight(text, CLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "cpp":
            text = highlight(text, CppLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "cs":
            text = highlight(text, CSharpLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax in ("css", "qss"):
            text = highlight(text, CssLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "java":
            text = highlight(text, JavaLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "json":
            text = highlight(text, JsonLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "yaml":
            text = highlight(text, YamlLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "toml":
            text = highlight(text, IniLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "r":
            text = highlight(text, RLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "bash":
            text = highlight(text, BashLexer(), formatter)
            text = Sanitized(text).sanitize_html()
            self.document_editor.setHtml(text)
            self.document_editor.setStyleSheet(f"background-color: {formatter.style.background_color};")
            return self
        elif self.document.syntax == "rmd":
            pass
        elif self.document.syntax == "rst":
            pass
        elif self.document.syntax == "tex":
            pass
        elif self.document.syntax == "texinfo":
            pass
        else:
            raise Exception(f"unknown syntax {self.document.syntax}")
        return self

    def save(self):
        """"""
        # if self.document is None:
        #     self.new_document()
        # content = self.get_content()
        # self.document.parse_content(content)
        # if content != self.document.content:
        #     self.document.set_content(content)
        super().save()
        return self

    def set_page_view(self):
        """"""
        self.layout.setContentsMargins(0, 0, 0, 0)
        # Define page size for "Letter" (8.5 x 11 inches in pixels at 96 DPI)
        self.page_width = 816  # 8.5 inches * 96 DPI
        self.page_height = 1056  # 11 inches * 96 DPI
        # Define default margins (in pixels)
        self.margin_top = 72  # 1 inch
        self.margin_bottom = 72  # 1 inch
        self.margin_left = 72  # 1 inch
        self.margin_right = 72  # 1 inch
        self.page_scene = pyqt.QGraphicsScene(self)
        self.page_scene.setBackgroundBrush(pyqt.QBrush(pyqt.QColor("black")))
        self.view = pyqt.QGraphicsView(self.page_scene)
        # #self.view.setRenderHint(self.view.viewportUpdateMode)
        # need add header
        # add footer
        # add methods for creating a second page
        self.layout.addWidget(self.view)
        # self.page_outline = pyqt.QGraphicsRectItem(0, 0, self.page_width, self.page_height)
        self.page_outline = pyqt.QGraphicsRectItem(
            0 + self.margin_left / 2,
            0 + self.margin_bottom / 2,
            self.page_width - self.margin_left,
            self.page_height - self.margin_bottom,
        )
        pen = pyqt.QPen(pyqt.QColor("#a6a6a6"))
        pen.setWidth(self.margin_top)
        self.page_outline.setPen(pen)
        self.page_scene.addItem(self.page_outline)
        self.document_editor.setFont(pyqt.QFont("Arial", 12))  # Default font and size
        self.document_editor.setGeometry(
            self.margin_left,
            self.margin_top,
            self.page_width - self.margin_left - self.margin_right,
            self.page_height - self.margin_top - self.margin_bottom,
        )
        self.page_scene.addWidget(self.document_editor)
        # Define page size for "Letter" (8.5 x 11 inches in pixels at 96 DPI)
        self.page_width = 816  # 8.5 inches * 96 DPI
        self.page_height = 1056  # 11 inches * 96 DPI
        # Define default margins (in pixels)
        self.margin_top = 72  # 1 inch
        self.margin_bottom = 72  # 1 inch
        self.margin_left = 72  # 1 inch
        self.margin_right = 72  # 1 inch

    def set_note_view(self):
        """"""
        self.layout.setContentsMargins(0, 0, 0, 0)
        # self.document_editor = NchantdDocEditor(self, self.config).initWidget()
        self.document_editor.setFont(pyqt.QFont("Arial", 12))  # Default font and size
        self.layout.addWidget(self.document_editor)

    def update_toolbar(self):
        """"""
        # add/remove buttons baseed on syntax selection
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
