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
import html
from bs4 import BeautifulSoup
import re

# ======================================3rd Party Library Modules=====================================================||
from pygments import highlight
from pygments.lexers import PythonLexer, JavaLexer, JavascriptLexer, CLexer
from pygments.lexers import JsonLexer, YamlLexer, CssLexer, IniLexer
from pygments.lexers.c_cpp import CppLexer
from pygments.lexers.dotnet import CSharpLexer
from pygments.lexers.ruby import RubyLexer
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
debug = False
logma = Logma(__name__)
# logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "scripts.yaml")


class NchantdOfficeScript(NchantdOfficeDocument):  # (pyqt.QsciScintillaBase):

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
        document = {"document": self.config.dikt.get("document", {})}
        self.document = self.app.model.codex.init_script(document)
        self.document.load_document()
        logma.json(self.document.to_dict())
        self.context_menu_name = "context.document.script"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        self.view_type = self.config.dikt.get("view_type", "note_view")
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
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
        if self.file_path is None or not exists(self.file_path):
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

    def cmd_add_chart(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_add_code(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_add_date(self, event, *args, **kwargs):
        """"""

    def cmd_add_image(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_add_shape(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_add_table(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_add_textbox(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_add_time(self, event, *args, **kwargs):
        """"""

    def cmd_on_compatability_changed(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_on_change_document_format(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_on_change_document_syntax(self, event, *args, **kwargs):
        """"""
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

    def cmd_set_margin_top(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_set_margin_bottom(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_set_margin_left(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_set_margin_right(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_toggle_selection_bold(self, event, *args, **kwargs):
        """"""

    def cmd_toggle_selection_italic(self, event, *args, **kwargs):
        """"""

    def cmd_toggle_selection_underline(self, event, *args, **kwargs):
        """"""

    def cmd_toggle_page_view(self, event, *args, **kwargs):
        """"""
        # NOTE: Change between a full screen and a standard 8.5x11/whatever the current page size is set to
        #view port change
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

    def get_bottom_margin_selected(self):
        """"""
        bottom_margin = "1 inch"
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

    def get_text_background_color_options(self):
        """"""
        colors = ["White", "Black"]
        return colors

    def get_text_background_color_selected(self):
        """"""
        color = "White"
        return color

    def get_left_margin_selected(self):
        """"""
        left_margin = "1 inch"
        return left_margin

    def get_right_margin_selected(self):
        """"""
        right_margin = "1 inch"
        return right_margin

    def get_top_margin_selected(self):
        """"""
        top_margin = "1 inch"
        return top_margin

    def get_margin_options(self):
        """"""
        margins = ["1 inch", "2 inches", "3 inches", "4 inches"]
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
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action

        cfg = {
            "text": "Pretty Print",
            "layout": "vertical",
            "handler": self.cmd_pretty_print_selected_text,
        }
        self.pretty_print = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.pretty_print
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action

        cfg = {
            "label": "Set Compatability",
            "layout": "vertical",
            "options": self.get_compatibility_options(),
            "handler": self.cmd_on_compatability_changed,
            "value": self.get_compatability_selected(),
        }
        self.document_compatability = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.document_compatability
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Set Top Margin",
            "layout": "horizontal",
            "options": self.get_margin_options(),
            "value": self.get_top_margin_selected(),
        }
        self.top_margin_select = NchantdLabeledSpinBox(self, cfg)
        items[cnt]["widget"] = self.top_margin_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Set Left Margin",
            "layout": "horizontal",
            "options": self.get_margin_options(),
            "value": self.get_left_margin_selected(),
        }
        self.left_margin_select = NchantdLabeledSpinBox(self, cfg)
        items[cnt]["widget"] = self.left_margin_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Set Right Margin",
            "layout": "horizontal",
            "options": self.get_margin_options(),
            "value": self.get_right_margin_selected(),
        }
        self.right_margin_select = NchantdLabeledSpinBox(self, cfg)
        items[cnt]["widget"] = self.right_margin_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Set Bottom Margin",
            "layout": "horizontal",
            "options": self.get_margin_options(),
            "value": self.get_bottom_margin_selected(),
        }
        self.bottom_margin_select = NchantdLabeledSpinBox(self, cfg)
        items[cnt]["widget"] = self.bottom_margin_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Set Page View",
            "layout": "vertical",
            "options": self.get_page_view_options(),
            "value": self.get_page_view_selected(),
            "handler": self.cmd_toggle_page_view,
        }
        self.page_layout_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.page_layout_select
        cnt += 1
        # NOTE: add text justification
        # NOTE: Add text bulleting
        # NOTE: add text spacing
        #
        return items

    def init_drawer_selection_config(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Insert Image:",
            "layout": "vertical",
            "handler": self.cmd_add_image,
            "value": None,
        }
        self.insert_image = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.insert_image
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Insert Table:",
            "layout": "vertical",
            "handler": self.cmd_add_table,
            "value": None,
        }
        self.insert_table = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.insert_table
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Insert Date:",
            "layout": "vertical",
            "handler": self.cmd_add_date,
            "value": None,
        }
        self.insert_date = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.insert_date
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Insert Time:",
            "layout": "vertical",
            "handler": self.cmd_add_time,
            "value": None,
        }
        self.insert_time = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.insert_time
        cnt += 1
        # NOTE move inserts to object config
        # NOTE add tools here like spell/grammar, etc
        # NOTE add analytics tools
        return items

    def init_drawer_object_config(self):
        """"""
        # NOTE: each of these panes need to have their spacing tightened up
        items = self.toolbox_config[300].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Document Header: ",
            "layout": "horizontal",
        }
        self.document_header_entry = NchantdHeaderPane(self, cfg)
        items[cnt]["widget"] = self.document_header_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Page Header: ",
            "layout": "horizontal",
        }
        self.page_header_entry = NchantdHeaderPane(self, cfg)
        items[cnt]["widget"] = self.page_header_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Objects List: ",
            "layout": "horizontal",
        }
        self.objects_pane_list = NchantdNewObjectPane(self, cfg)
        items[cnt]["widget"] = self.objects_pane_list
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Insert Object: ",
            "layout": "horizontal",
        }
        self.object_select = NchantdDropDownActivator(self, cfg)
        items[cnt]["widget"] = self.object_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Page Footer: ",
            "layout": "horizontal",
        }
        self.page_footer_entry = NchantdFooterPane(self, cfg)
        items[cnt]["widget"] = self.page_footer_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Document Footer: ",
            "layout": "horizontal",
        }
        self.document_footer_entry = NchantdFooterPane(self, cfg)
        items[cnt]["widget"] = self.document_footer_entry
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

    def insert_image(self):
        """
        depnding on the document type this will be slightly different but should be allowed in most documents
        :return:
        """
        return self

    def insert_chart(self):
        """"""
        return self

    def insert_shape(self):
        """"""
        return self

    def insert_symbol(self):
        """"""
        return self

    def insert_table(self):
        """"""
        return self

    def insert_chart(self):
        """"""
        return self

    def insert_code(self):
        """"""
        return self

    def insert_document(self):
        """"""
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

    def insert_shape(self):
        """"""
        return self

    def insert_symbol(self):
        """"""
        return self

    def insert_table(self):
        """"""
        return self

    def onEnterEvent(self):
        """Run a save of the doc editor data to the database"""
        return self

    def open_file(self, file=None):
        """"""
        if file is None:
            file = self.file_path
        cfg = {"file_path": file}
        document = self.app.model.codex.init_script(cfg)
        document.load_document()
        self.set_document(document)
        self.document.open_file()
        self.populate_document()
        return self

    def populate_document(self):
        """"""
        logma.info(f"Populating Document")
        style = f"background-color: #FFFFFF;"
        self.document_editor.setStyleSheet(style)
        if self.document is None:
            text = self.document_editor.get_text()
        else:
            text = self.document.text.to_dict()["unit"].get("value", "")
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
        self.document.syntax = "html"  # NOTE debug
        if self.document.syntax == "markdown":
            self.document_editor.setMarkdown(text)
            return self
        elif self.document.syntax in ("plain-text", "plaintext"):
            self.document_editor.setPlainText(text)
            return self
        elif self.document.syntax == "xml":
            self.document_editor.setXml(text)
            return self
        elif self.document.syntax == "latex":
            self.document_editor.setLatex(text)
            return self
        elif self.document.syntax == "html":
            logma.info(f"HTML {text}")
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
        logma.info(f"HTML {self.document_editor.toHtml()}")
        if self.document is None:
            self.new_document()
        self.document.syntax = "html"
        if self.document.syntax == "html":
            html = """
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN http://www.w3.org/TR/REC-html40/strict.dtd">
            <html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /></head><body><[content]></body></html>
            """
            text = self.document_editor.toHtml()  # .replace("\n", "")
            soup = BeautifulSoup(text, "html.parser")
            contents = soup.body.decode_contents()
            # spaces = [
            #     '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"></br></p>',
            #     '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"> </p>',
            # ]
            logma.info(f"Contents: {contents}")
            # for space in spaces:
            #     logma.info(f"Space: {space}")
            #     logma.info(f"First Line {contents[0 : len(space)+1]}")
            #     if space == contents[1 : len(space) + 1]:
            #         contents = contents[len(space) :]
            #         logma.info(f"Change Contents {contents}")
            #     if space == contents[-len(space) :]:
            #         contents = contents[: -len(space)]
            html = html.replace("<[content]>", contents)
            logma.info(f"Content: {contents}")
            content = html.replace("<[content]>", soup.body.decode_contents())
            logma.info(f"Content: {content}")
        else:
            content = self.document_editor.toPlainText()
        self.document.parse_content(content)
        if content != self.document.content:
            self.document.set_content(content)
        super().save()
        logma.json(self.document.to_dict())
        # logma.info(self.document.to_dict())
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
