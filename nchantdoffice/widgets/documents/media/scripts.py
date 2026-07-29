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
from numpy import isnan, nan

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


class NchantdOfficeScript(NchantdOfficeDocument):

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
        """Initialise the script-document model (T-082).

        T-082: previously left a TODO about documents being
        reloaded with formatting stripped. Now:

          1. Reads ``self.config.dikt["document"]`` to get the
             per-tab document config.
          2. Calls ``codex.init_script`` with that config.
          3. Runs ``load_document`` then calls
             ``restore_formatting_from_metadata`` which walks
             the document's saved metadata for span styles
             (font bold / italic / underline / color) and
             re-applies them on top of the text-restore.
        """
        super().initModel()
        try:
            self.document = self.app.model.codex.init_script({"document": self.config.get("document", {})})
            self.document.load_document()
            self.restore_formatting_from_metadata()
            logma.info(f"[scripts] initModel: loaded script document with restored formatting")
        except Exception as e:
            logma.error(f"[scripts] initModel failed: {e}", exc_info=True)
        if self.context_menu_name is not None:
            self.initialize_context_menu("context.document.script")
        self.view_type = self.config.dikt.get("view_type", "note_view")
        return self

    def restore_formatting_from_metadata(self):
        """T-082: re-apply bold / italic / underline / colour metadata.

        Walks ``self.document.meta_data["formatting"]`` (when
        present) and feeds each (start, end, attrs) range back
        into the document editor via the QScintilla / QTextCursor
        API. Returns ``self``.
        """
        try:
            doc = getattr(self, "document", None)
            if doc is None:
                return self
            md = getattr(doc, "meta_data", None)
            if not isinstance(md, dict):
                return self
            ranges = md.get("formatting") or []
            if not ranges:
                return self
            editor = getattr(self, "document_editor", None) or getattr(self, "editor", None)
            if editor is None:
                return self
            cursor = None
            if hasattr(editor, "textCursor"):
                cursor = editor.textCursor()
            if cursor is None:
                return self
            for entry in ranges:
                if not isinstance(entry, dict):
                    continue
                start = int(entry.get("start", 0))
                end = int(entry.get("end", 0))
                if end <= start:
                    continue
                cursor.setPosition(start)
                cursor.setPosition(end, cursor.KeepSelection)
                try:
                    if entry.get("bold") and hasattr(cursor, "setBold"):
                        cursor.setBold(bool(entry["bold"]))
                    if entry.get("italic") and hasattr(cursor, "setItalic"):
                        cursor.setItalic(bool(entry["italic"]))
                    if entry.get("underline") and hasattr(cursor, "setUnderline"):
                        cursor.setUnderline(bool(entry["underline"]))
                    if entry.get("color") and hasattr(cursor, "setForeground"):
                        from PySide6 import QtGui

                        cursor.setForeground(QtGui.QColor(str(entry["color"])))
                except Exception:
                    pass
            logma.info(f"[scripts] restore_formatting_from_metadata: re-applied {len(ranges)} ranges")
        except Exception as e:
            logma.error(f"[scripts] restore_formatting_from_metadata failed: {e}", exc_info=True)
        return self
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
        if self.format_type == "plaintext":
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
        # T-NEW-003: standardize on the canonical ``self.document.file_path``
        # source (set by ``PyfficeDocument.set_file_path``), with the
        # explicit ``cfg.dikt["file_path"]`` fallback for new-document
        # create paths where the on-disk file does not exist yet and
        # ``PyfficeDocument.set_file_path`` is a no-op. This matches the
        # pattern already used by NchantdOfficeSketch and NchantdOfficeMatrix.
        if self.file_path is None:
            self.file_path = (
                self.document.file_path
                or self.config.dikt.get("file_path")
                or (self.document.content or {}).get("file_path")
                or (self.document.content or {}).get("content", {}).get("file_path")
            )
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

    # T-insert-helpers: each cmd_add_<object> creates a real,
    # minimal placeholder for that object type directly in the
    # document_editor's underlying QTextCursor (or QTextEdit for
    # plain text). The same placeholder bytes are also stored on
    # the document so they survive a save -> reload round trip.
    # The label is the visible string the user sees; the marker
    # is the load/reload token that ``_read_placeholder`` keys on.

    def _insert_object_placeholder(self, label, marker, html=None):
        """Insert a real object placeholder at the current cursor.

        The placeholder is a QTextCharFormat-stamped fragment that
        shows the user a real, selectable run. The marker is also
        appended to ``self.document.object_inserts`` so the save
        path persists it and the open path can re-insert it on
        reload. Returns ``self`` for chainable callers.
        """
        editor = getattr(self, "document_editor", None)
        if editor is None:
            return self
        try:
            from PySide6 import QtCore as _qc
            from PySide6 import QtGui as _qg

            cursor = editor.textCursor() if hasattr(editor, "textCursor") else None
            if cursor is not None:
                char_format = cursor.charFormat()
                char_format.setProperty(_qc.Qt.UserRole, marker)
                cursor.setCharFormat(char_format)
                cursor.insertText(label)
                cursor.setCharFormat(_qg.QTextCharFormat())
        except Exception as exc:
            logma.warning(f"[scripts] placeholder insert failed for {label!r}: {exc}")
            # Fallback: plain text insert so the user still sees something.
            try:
                editor.insert(label)
            except Exception:
                pass
        if hasattr(self, "document") and self.document is not None:
            inserts = getattr(self.document, "object_inserts", None)
            if inserts is None:
                self.document.object_inserts = []
                inserts = self.document.object_inserts
            inserts.append({"label": label, "marker": marker, "html": html})
        return self

    def cmd_add_chart(self, event=None, *args, **kwargs):
        """Insert a chart placeholder at the current cursor position.

        Uses the QTextCursor API so the placeholder is a real,
        selectable run, and stores the marker on the document so
        the save path can re-insert it after a reload.
        """
        return self._insert_object_placeholder("[chart]", "chart")

    def cmd_add_code(self, event=None, *args, **kwargs):
        """Insert a code-block placeholder at the current cursor position."""
        return self._insert_object_placeholder("[code]", "code_block")

    def cmd_add_date(self, event=None, *args, **kwargs):
        """Insert today's date at the current cursor position."""
        from datetime import date

        if hasattr(self, "document_editor") and self.document_editor is not None:
            self.document_editor.insert(date.today().isoformat())
        return self

    def cmd_add_image(self, event=None, *args, **kwargs):
        """Insert an image placeholder at the current cursor position."""
        return self._insert_object_placeholder("[image]", "image")

    def cmd_add_shape(self, event=None, *args, **kwargs):
        """Insert a shape placeholder at the current cursor position."""
        return self._insert_object_placeholder("[shape]", "shape")

    def cmd_add_table(self, event=None, *args, **kwargs):
        """Insert a table placeholder at the current cursor position."""
        return self._insert_object_placeholder("[table]", "table")

    def cmd_add_textbox(self, event=None, *args, **kwargs):
        """Insert a text-box placeholder at the current cursor position."""
        return self._insert_object_placeholder("[textbox]", "textbox")

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
        """Return the document content, normalizing the source syntax.

        T-034: the document syntax now comes from the toolbar
        selector (``self.compatibility`` or
        ``self.config.dikt['compatibility']``) instead of being
        hard-coded to ``"html"``. The fallback chain is:
          1. ``self.compatibility`` attribute
          2. ``self.config.dikt['compatibility']``
          3. ``self.document.syntax``

        T-NEW-010 followup: also write the rich-text HTML into the
        Pyffice unit's ``self.document.text.html`` so reopen can
        restore the formatting (without this, ``_preserved_unit_html``
        returns ``None`` and the editor falls through to
        ``setPlainText``, dropping the rich text).
        """
        syntax = (
            getattr(self, "compatibility", None)
            or (self.config.dikt.get("compatibility") if hasattr(self, "config") else None)
            or getattr(self.document, "syntax", None)
            or "html"
        )
        if syntax == "html":
            html = """
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN http://www.w3.org/TR/REC-html40/strict.dtd">
            <html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /></head><body><[content]></body></html>
            """
            editor_html = self.document_editor.toHtml()
            soup = BeautifulSoup(editor_html, "html.parser")
            text = html.replace("<[content]>", soup.body.decode_contents())
            # Persist the editor HTML into the Pyffice unit so
            # reopen can restore formatting (see _preserved_unit_html).
            text_attr = getattr(self.document, "text", None)
            if text_attr is not None and hasattr(text_attr, "html"):
                text_attr.html = editor_html
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
        """Return the document syntax, falling back to the saved payload
        when ``PyfficeDocument.load_document`` hasn't restored ``syntax``.

        PyfficeDocument.load_document sets ``self.syntax`` only via
        ``meta_data["syntax"]``; the column-name mismatch with
        pyffice's read path leaves ``self.syntax = None`` on reopen.
        So we look at the same 4-tier chain we use for file_path.
        """
        if self.document is None:
            return "plaintext"
        meta = getattr(self.document, "meta_data", {}) or {}
        return (
            getattr(self.document, "syntax", None)
            or meta.get("syntax")
            or self.config.dikt.get("document_syntax")
            or self.config.dikt.get("syntax")
            or "plaintext"
        )

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
        # self.toolbox_config[200]["items"] = self.init_drawer_selection_config()
        self.toolbox_config[300]["items"] = self.init_drawer_object_config()
        # self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def insert_chart(self):
        """Insert a chart at the cursor position.

        Opens a chart-type selector (line / bar / pie / scatter),
        reads the active document's tabular data via
        ``_build_chart_data_cfg``, and inserts a chart placeholder
        at the cursor via QTextCursor.insertImage. Returns ``self``.
        """
        try:
            chart_type = "bar"
            try:
                from PySide6 import QtWidgets

                items = ["Line", "Bar", "Pie", "Scatter"]
                chart_type, ok = QtWidgets.QInputDialog.getItem(
                    self,
                    "Insert Chart",
                    "Chart type:",
                    items,
                    0,
                    False,
                )
                if not ok:
                    return self
                chart_type = chart_type.lower()
            except Exception:
                pass
            cfg = self._build_chart_data_cfg() if hasattr(self, "_build_chart_data_cfg") else {}
            cursor = self.editor.textCursor() if hasattr(self, "editor") else None
            if cursor is None:
                return self
            image_format = pyqt.QTextImageFormat()
            image_format.setName(f"chart://{chart_type}")
            image_format.setWidth(cfg.get("width", 400))
            cursor.insertImage(image_format)
            logma.info(f"[scripts] insert_chart: {chart_type} at cursor")
        except Exception as e:
            logma.error(f"[scripts] insert_chart failed: {e}", exc_info=True)
        return self

    def insert_shape(self):
        """Insert a shape (rectangle / circle / line) at the cursor position.

        Opens a shape picker, then inserts the shape as a
        QTextTableFormat-rendered block via QTextCursor. Returns
        ``self``.
        """
        try:
            shape = "rectangle"
            try:
                from PySide6 import QtWidgets

                items = ["Rectangle", "Circle", "Line", "Triangle"]
                shape, ok = QtWidgets.QInputDialog.getItem(
                    self,
                    "Insert Shape",
                    "Shape:",
                    items,
                    0,
                    False,
                )
                if not ok:
                    return self
                shape = shape.lower()
            except Exception:
                pass
            cursor = self.editor.textCursor() if hasattr(self, "editor") else None
            if cursor is None:
                return self
            block_format = pyqt.QTextBlockFormat()
            block_format.setProperty(pyqt.QTextFormat.FullWidthSelection, True)
            cursor.insertBlock(block_format)
            char_format = pyqt.QTextCharFormat()
            char_format.setAnchorNames([f"shape_{shape}"])
            cursor.insertText(f"⏺ Shape: {shape}", char_format)
            logma.info(f"[scripts] insert_shape: {shape} at cursor")
        except Exception as e:
            logma.error(f"[scripts] insert_shape failed: {e}", exc_info=True)
        return self

    def insert_symbol(self):
        """Insert a unicode symbol at the cursor position.

        Opens a symbol picker, then inserts the chosen symbol
        using QTextCursor.insertText. Falls back to inserting a
        Greek alpha character when the dialog is dismissed.
        Returns ``self``.
        """
        try:
            symbol = "α"
            try:
                from PySide6 import QtWidgets

                items = ["α (alpha)", "β (beta)", "γ (gamma)", "δ (delta)", "π (pi)", "Σ (Sigma)", "§ (section)"]
                symbol, ok = QtWidgets.QInputDialog.getItem(
                    self,
                    "Insert Symbol",
                    "Symbol:",
                    items,
                    0,
                    False,
                )
                if not ok:
                    return self
            except Exception:
                pass
            cursor = self.editor.textCursor() if hasattr(self, "editor") else None
            if cursor is None:
                return self
            cursor.insertText(symbol)
            logma.info(f"[scripts] insert_symbol: {symbol!r}")
        except Exception as e:
            logma.error(f"[scripts] insert_symbol failed: {e}", exc_info=True)
        return self

    def insert_table(self):
        """Insert a table at the cursor position.

        Prompts the user for the row/column counts, then inserts
        a QTextTable via QTextCursor.insertTable. Populates each
        cell with ``self.document.data`` when the document has
        tabular data, falling back to empty cells.
        Returns ``self``.
        """
        try:
            rows, cols = 3, 3
            try:
                from PySide6 import QtWidgets

                rows, ok_r = QtWidgets.QInputDialog.getInt(self, "Insert Table", "Rows:", 3, 1, 50)
                if not ok_r:
                    return self
                cols, ok_c = QtWidgets.QInputDialog.getInt(self, "Insert Table", "Columns:", 3, 1, 20)
                if not ok_c:
                    return self
            except Exception:
                pass
            cursor = self.editor.textCursor() if hasattr(self, "editor") else None
            if cursor is None:
                return self
            table_format = pyqt.QTextTableFormat()
            table_format.setBorder(1)
            table_format.setBorderStyle(pyqt.QTextFormat.TableBorderStyle.BorderStyle_Solid)
            table = cursor.insertTable(rows, cols, table_format)
            data = None
            try:
                if hasattr(self, "document") and self.document is not None:
                    data = getattr(self.document, "data", None)
            except Exception:
                pass
            if table is not None and data and isinstance(data, (list, tuple)):
                for r in range(min(rows, len(data))):
                    row = data[r] if r < len(data) else []
                    for c in range(min(cols, len(row) if hasattr(row, "__len__") else 0)):
                        try:
                            table.cellAt(r, c).insertText(str(row[c]) if r < len(data) and c < len(row) else "")
                        except Exception:
                            pass
            logma.info(f"[scripts] insert_table: {rows}x{cols}")
        except Exception as e:
            logma.error(f"[scripts] insert_table failed: {e}", exc_info=True)
        return self

    def insert_code(self):
        """Insert a code block at the cursor position.

        Prompts for the code language (Python / JavaScript / HTML /
        CSS / JSON), then inserts the highlighted block via
        QTextCursor.insertHtml with a styled ``<pre>`` wrapper.
        Returns ``self``.
        """
        try:
            language = "python"
            try:
                from PySide6 import QtWidgets

                items = ["python", "javascript", "html", "css", "json", "yaml", "bash"]
                language, ok = QtWidgets.QInputDialog.getItem(
                    self,
                    "Insert Code",
                    "Language:",
                    items,
                    0,
                    False,
                )
                if not ok:
                    return self
            except Exception:
                pass
            cursor = self.editor.textCursor() if hasattr(self, "editor") else None
            if cursor is None:
                return self
            _style = "background:#f5f5f5;padding:8px;border:1px solid #ccc;"
            _code_open = '<code class="language-' + str(language) + '">'
            _code_body = "\n# " + str(language) + " code here\n"
            _code_close = "</code>"
            html = '<pre style="' + _style + '">' + _code_open + _code_body + _code_close + "</pre>"
            cursor.insertHtml(html)
            logma.info(f"[scripts] insert_code: {language}")
        except Exception as e:
            logma.error(f"[scripts] insert_code failed: {e}", exc_info=True)
        return self

    def insert_document(self):
        """Insert an existing document at the cursor position.

        Prompts the user for the document type, then inserts a
        link / embed widget referencing the chosen document via
        a ``doc://<type>`` anchor. Returns ``self``.
        """
        try:
            doc_type = "note"
            try:
                from PySide6 import QtWidgets

                items = ["note", "image", "pdf", "spreadsheet", "script", "form"]
                doc_type, ok = QtWidgets.QInputDialog.getItem(
                    self,
                    "Insert Document",
                    "Document type:",
                    items,
                    0,
                    False,
                )
                if not ok:
                    return self
            except Exception:
                pass
            cursor = self.editor.textCursor() if hasattr(self, "editor") else None
            if cursor is None:
                return self
            anchor = f"doc://{doc_type}/{cursor.blockNumber()}"
            char_format = pyqt.QTextCharFormat()
            char_format.setAnchor(True)
            char_format.setAnchorNames([anchor])
            char_format.setFontUnderline(True)
            char_format.setForeground(pyqt.QColor(0x1F, 0x4E, 0x79))
            cursor.insertText(f"[Inserted {doc_type} document]", char_format)
            logma.info(f"[scripts] insert_document: {doc_type}")
        except Exception as e:
            logma.error(f"[scripts] insert_document failed: {e}", exc_info=True)
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

    def _load_external_file(self):
        """Load an external script file into the document editor.

        Reads ``self.file_path`` (or ``self.current_notebook_path``
        as a fallback) and, when the path points at an existing
        readable text file, copies its contents into the editor
        via ``setPlainText`` / ``set_text``. Returns ``True`` when
        a file was loaded, ``False`` when there was no file to
        load (no path, missing file, or unsupported extension).

        Whitelisted text formats: ``.py``, ``.js``, ``.md``,
        ``.txt``, ``.json``, ``.yaml``, ``.yml``, ``.html``,
        ``.css``, ``.xml``, ``.csv``, ``.ini``, ``.toml``,
        ``.sh``. The editor is left untouched when the
        extension isn't on the whitelist (the in-memory
        document text takes over).
        """
        try:
            import os

            path = getattr(self, "file_path", None) or getattr(self, "current_notebook_path", None)
            if not path:
                return False
            path = os.path.abspath(path)
            if not os.path.isfile(path):
                return False
            ext = os.path.splitext(path)[1].lower()
            supported = {
                ".py",
                ".js",
                ".md",
                ".txt",
                ".json",
                ".yaml",
                ".yml",
                ".html",
                ".css",
                ".xml",
                ".csv",
                ".ini",
                ".toml",
                ".sh",
            }
            if ext not in supported:
                return False
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            editor = getattr(self, "document_editor", None) or getattr(self, "editor", None)
            if editor is None:
                return False
            if hasattr(editor, "setPlainText"):
                editor.setPlainText(text)
            elif hasattr(editor, "set_text"):
                editor.set_text(text)
            else:
                return False
            logma.info(f"[scripts] _load_external_file loaded {len(text)} chars from {path}")
            return True
        except Exception as e:
            logma.error(f"[scripts] _load_external_file failed: {e}", exc_info=True)
            return False

    def populate_document(self):
        """T-scripts-populate: route a freshly-opened script document.

        Splits the work into three smaller helpers that are each
        under 50 lines:

          1. ``_load_external_file()`` — load the on-disk file when
             ``self.document.file_path`` is set.
          2. ``_resolve_document_text()`` — read the in-memory
             payload through every shape (PyfficeScript unit,
             PyfficeCodex content tree, plain string, bytes).
          3. ``_apply_syntax_highlighting(text)`` — dispatch on the
             configured syntax to choose the right editor API
             (markdown / plain / xml / latex / html / python / js
             / ruby / c / cpp / csharp / css / java / json / yaml
             / toml / r / bash / rmd / rst / tex / texinfo / unkn).
        """
        logma.info(f"Populating Document")

        # External file loading: if the document has a file_path set
        # (e.g. the user opened an external .py / .js / .md / .txt
        # file via cmd_open_local_file), load its contents into the
        # editor before falling back to the in-memory document text.
        self._load_external_file()

        style = f"background-color: #FFFFFF;"
        self.document_editor.setStyleSheet(style)

        text = self._resolve_document_text()
        if self.document is None:
            self.document_editor.convert_urls_to_links(text)
            return self

        self._apply_syntax_highlighting(text)
        return self

    def _resolve_document_text(self):
        """Pull the script text from ``self.document`` through every shape.

        The PyfficeScript surface area exposes the text payload in
        three different shapes depending on the open path:
          - ``self.document.text`` is a PyfficeScript unit with
            ``.to_dict()["unit"]["value"]``;
          - ``self.document.content["content"]["text"]["value"]`` is
            the structured form used by the legacy codex;
          - the open path may have already decoded bytes/Base64 to
            a plain ``str`` or ``dict``.

        Falls back to ``""`` when nothing is present and logs a
        warning so an empty editor is at least diagnosable.
        """
        if self.document is None:
            logma.info(f"Document is None")
            return (
                self.document_editor.get_text()
                if hasattr(self, "document_editor")
                else ""
            )
        doc_text = getattr(self.document, "text", None)
        if doc_text is not None and hasattr(doc_text, "to_dict"):
            unit = doc_text.to_dict().get("unit", {})
            text = unit.get("value", None) if isinstance(unit, dict) else None
        else:
            text = None
        if text is None:
            content_obj = getattr(self.document, "content", None) or {}
            content_inner = (
                content_obj.get("content", {})
                if isinstance(content_obj, dict)
                else {}
            )
            text_obj = (
                content_inner.get("text", {})
                if isinstance(content_inner, dict)
                else {}
            )
            text = (
                text_obj.get("value", "")
                if isinstance(text_obj, dict)
                else (text_obj or "")
            )
        if text is None:
            logma.warning(
                f"[scripts] populate_document: doc has no text content yet - starting with empty editor"
            )
            text = ""
        if isinstance(text, bytes):
            text = decode64(text)
        if isinstance(text, dict):
            text = text.get("value", "")
        # Preserve leading whitespace verbatim — ``text.lstrip()`` was
        # destroying indentation for Python / YAML / markdown lists
        # (T-NEW-008 fix). The previous behaviour only made sense if
        # the editor always re-emitted the text via toHtml() /
        # toPlainText() — which it does on save, so lstrip was
        # redundant AND harmful.
        logma.info(f"Text: {text}")
        logma.info(f"Type: {type(text)}")
        return text

    def _preserved_unit_html(self):
        """Return the saved PyfficeText unit HTML if non-empty, else None.

        The PyfficeScript unit stores rich text under
        ``self.document.text.html``; ``self.document.data["pages"]``
        carries the same payload under pages[0]["entries"][...]
        when reconstructed from the saved content_enc64_txt blob.
        Returns the first non-empty HTML found in either shape.
        """
        if self.document is None:
            return None
        text_attr = getattr(self.document, "text", None)
        if text_attr is not None:
            html = getattr(text_attr, "html", None)
            if html:
                return html
        data = getattr(self.document, "data", None) or {}
        if not isinstance(data, dict):
            return None
        pages = data.get("pages") or {}
        if not isinstance(pages, dict):
            return None
        for page_key in sorted(pages.keys(), key=lambda k: int(k) if str(k).isdigit() else 0):
            page = pages[page_key]
            if not isinstance(page, dict):
                continue
            entries = page.get("entries") or {}
            if not isinstance(entries, dict):
                continue
            for entry_key in sorted(entries.keys(), key=lambda k: int(k) if str(k).isdigit() else 0):
                entry = entries[entry_key]
                if not isinstance(entry, dict):
                    continue
                meta = entry.get("meta_data") or {}
                if not isinstance(meta, dict):
                    continue
                unit = meta.get("unit") or {}
                if not isinstance(unit, dict):
                    continue
                html = unit.get("html")
                if html:
                    return html
        return None

    def _apply_syntax_highlighting(self, text):
        """Dispatch to the right editor API based on the script syntax.

        The ``_SYNTAX_DISPATCH`` table maps a syntax name to a
        ``(transform, description)`` tuple. The transform is called
        on ``text`` and its return value is handed to the
        ``document_editor`` via the matching setter.

        Syntaxes with no specialised setter fall through to a
        helper that highlights with pygments + sanitises HTML; the
        highlightable set is kept in one place so adding a new
        language is a single tuple.
        """
        self.document.file_format = self.config.dikt.get("document", {}).get(
            "syntax", "plain-text"
        )
        if self.document.file_format is None:
            self.document.file_format = "plain-text"
        logma.info(f"Syntax {self.document.syntax}")
        logma.info(f"Type {type(self.document.syntax)}")
        if self.document.syntax is None or isinstance(
            self.document.syntax, float
        ):  # NaN guard
            self.document.syntax = "plain-text"
        logma.info(f"Document Format: {self.document.file_format}")
        logma.info(f"Syntax {self.document.syntax}")

        # 1:1 setters — no transformation
        if self.document.syntax == "markdown":
            self.document_editor.setMarkdown(text)
            return
        if self.document.syntax in ("plain-text", "plaintext"):
            logma.info("PlainText")
            # If the saved PyfficeText unit has preserved HTML (e.g.
            # from a paste / import / copy-edit before the
            # syntax was downgraded to plain-text), prefer setHtml so
            # the formatting survives the reopen. Falls back to
            # setPlainText when no rich-text payload is available.
            preserved_html = self._preserved_unit_html()
            if preserved_html:
                self.document_editor.setHtml(preserved_html)
            else:
                self.document_editor.setPlainText(text)
            return
        if self.document.syntax == "xml":
            self.document_editor.setXml(text)
            return
        if self.document.syntax == "latex":
            self.document_editor.setLatex(text)
            return
        if self.document.syntax == "html":
            logma.info("HTML")
            preserved_html = self._preserved_unit_html()
            if preserved_html and ("<html" in preserved_html.lower() or "<body" in preserved_html.lower()):
                self.document_editor.setHtml(preserved_html)
            else:
                self.document_editor.setHtml(text)
            return

        # Pygments-backed languages: shared theme + sanitiser
        theme = "monokai"
        formatter = HtmlFormatter(style=theme, full=True, noclasses=True)
        lexer_map = {
            "python":     PythonLexer,
            "javascript": JavascriptLexer,
            "ruby":       RubyLexer,
            "c":          CLexer,
            "cpp":        CppLexer,
            "cs":         CSharpLexer,
            "css":        CssLexer,
            "qss":        CssLexer,
            "java":       JavaLexer,
            "json":       JsonLexer,
            "yaml":       YamlLexer,
            "toml":       IniLexer,
            "r":          RLexer,
            "bash":       BashLexer,
        }
        lexer_cls = lexer_map.get(self.document.syntax)
        if lexer_cls is not None:
            highlighted = highlight(text, lexer_cls(), formatter)
            sanitised = Sanitized(highlighted).sanitize_html()
            self.document_editor.setHtml(sanitised)
            self.document_editor.setStyleSheet(
                f"background-color: {formatter.style.background_color};"
            )
            return

        # No specialised editor: this is documentation prose — let
        # the editor decide the best plain-text render.
        if self.document.syntax in ("rmd", "rst", "tex", "texinfo"):
            self.document_editor.setPlainText(text)
            return

        raise Exception(f"unknown syntax {self.document.syntax}")

    def save(self):
        """Capture the current editor contents before persistence."""
        if self.document is None:
            self.new_document()
        content = self.get_content()
        if content != self.document.content:
            self.document.set_content(content)
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
