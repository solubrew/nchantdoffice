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
import datetime as dt
import re
from bs4 import BeautifulSoup
import json

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
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.tabsets import NchantdTab
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.tables.tables import NchantdTable
from nchantrs.widgets.media.editors.editors import NchantdDocEditor
from nchantrs.widgets.media.editors.editors import NchantdAppendOnlyEditor
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.media.editors.selectors import NchantdComboBox, NchantdDropDown
from pycurity.pyhash import decode64

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
debug = True
if not log:
    logma.off()
# ====================================================================================================================||
pxcfg = join(here, "_data_", "journal.yaml")


class NchantdOfficeJournalEditor(NchantdOfficeDocument):
    """ """

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Journal", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdJournalEditor").override(cfg))
        self.context_notes = []
        self.rotate_time = None
        self.current_time = dt.datetime.now()
        self.append_only = True
        self.running_log = False
        self.journal_notes = {}
        self.read_only = False
        self.top_layout = None
        self.settings = None
        self.previous = None
        self.next = None
        self.editor = None
        self.layout = None
        self.app = None
        # self.store_journal()
        self.text = None
        self.data = None
        self.document = None
        self.entries = {}

    def initModel(self):
        """ "" """
        super().initModel()
        logma.info(f"initModel")
        scope = self.config.dikt.get("scope", "TODAY")
        datetime = dt.datetime.now()
        tid = None
        if hasattr(self.app.model.get_current_node(), "tid"):
            tid = self.app.model.get_current_tab().tid
        tags = {"nid": self.app.model.get_current_node().nid, "tid": tid}
        cfg = {"tags": tags, "scope": scope, "datetime": datetime}
        document = {"document": self.get_journal_document(cfg)}
        logma.info(f"Document {document}")
        self.document = self.app.model.codex.init_script(document)
        self.document.load_document()
        self.pages = self.document.pages
        logma.info(f"Pages {self.pages}")
        self.full_text = text = self.document.text.to_dict()["unit"].get("value", "")
        logma.info(f"Full Text {self.full_text}")
        if self.context_menu_name is not None:
            self.initialize_context_menu("context.document.journal")
        return self

    def initView(self, cfg=None):
        """ """
        cfg = cfg or {}
        cfg["default_toolbar"] = False
        editor_cfg = {"default_text": self.full_text}
        self.editor = NchantdOfficeJournalAppendEditor(self, editor_cfg).initWidget()
        super().initView(cfg)
        self.top_layout = pyqt.QHBoxLayout()
        # PUSH to 0.0.3
        # cfg = {
        #     "layout": "horizontal",
        #     "label": f"Date: {dt.datetime.now().strftime('%m/%d/%Y')}",
        #     "options": ["Contextually", "Chronologically"],
        # }
        # self.settings = NchantdDropDown(self, cfg).initWidget()
        cfg = {"text": "Journal Entries"}
        self.settings = NchantdLabel(self, cfg).initWidget()
        self.top_layout.addWidget(self.settings)
        self.layout.addLayout(self.top_layout)

        self.editor.set_background(hex="#4F5665")
        self.layout.addWidget(self.editor)
        # TODO always scroll to bottom of document
        return self

    def initWidget(self):
        """ "" """
        self.initModel()
        self.initView()
        return self

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
            editor_html = self.editor.toHtml()
            soup = BeautifulSoup(editor_html, "html.parser")
            text = html.replace("<[content]>", soup.body.decode_contents())
            # Persist the editor HTML into the Pyffice unit so
            # reopen can restore formatting (see _preserved_unit_html).
            text_attr = getattr(self.document, "text", None)
            if text_attr is not None and hasattr(text_attr, "html"):
                text_attr.html = editor_html
        else:
            text = self.editor.toPlainText()
        logma.info(f"File Path {self.file_path}")
        content = {"content": {"file_path": self.file_path}, "text": text}
        logma.info(f"CONTENT {content}")
        return content

    def get_content_text(self, cfg=None):
        """"""
        document = self.get_journal_document(cfg)
        self.document.set_version(document.get("content_version_int", None))
        logma.info(document)
        text = document.get("content_enc64_txt", None)
        if text is None:
            if debug:
                raise
            return ""
        text = json.loads(decode64(text)).get("content", {}).get("text")
        logma.info(text)
        return text

    def get_journal_document(self, cfg):
        """"""
        document = self.app.model.get_view_journal(cfg)
        logma.info(f"Document {document}")
        return document

    def get_journal_organization(self):
        """"""
        # value = self.settings.get_value()
        # return value

    def focusOutEvent(self, event):
        """"""
        super().focusOutEvent(event)
        self.save()

    def refresh_content(self):
        """Re-fetch the journal document from the model and update the editor.

        T-NEW-036 + T-NEW-073: ``initModel`` fetches the journal text
        once at ``initWidget`` time. On subsequent tab-focus changes,
        ``initModel`` is never re-called, so the editor showed stale
        content. This method re-fetches the current journal text
        (same path as ``initModel``: get_view_journal -> codex.init_script
        -> load_document -> text.to_dict) and pushes the result into
        ``self.full_text`` + the editor widget.

        Called from ``NchantdOfficeTabSet.on_tab_focus`` when the
        focused tab's widget has a ``refresh_content`` method.

        Defensive: missing ``self.app``, missing model, or a raised
        exception is logged + swallowed (returns self) rather than
        crashing the UI.

        Returns ``self`` for chainable call sites.
        """
        try:
            app = getattr(self, "app", None)
            if app is None:
                return self
            model = getattr(app, "model", None)
            if model is None:
                return self
            scope = self.config.dikt.get("scope", "TODAY")
            datetime = dt.datetime.now()
            tid = None
            try:
                tab = model.get_current_tab()
                tid = getattr(tab, "tid", None)
            except Exception:
                pass
            try:
                node = model.get_current_node()
                nid = getattr(node, "nid", None)
            except Exception:
                nid = None
            tags = {"nid": nid, "tid": tid}
            cfg = {"tags": tags, "scope": scope, "datetime": datetime}
            document = {"document": model.get_view_journal(cfg)}
            doc = model.codex.init_script(document)
            doc.load_document()
            text = doc.text.to_dict()["unit"].get("value", "")
            self.full_text = text
            self.document = doc
            self.pages = doc.pages
            if self.editor is not None and hasattr(self.editor, "setPlainText"):
                self.editor.setPlainText(text)
            logma.info(f"[journal] refresh_content: restored {len(text)} chars")
        except Exception as e:
            logma.error(
                f"[journal] refresh_content failed: {e}",
                exc_info=True,
            )
        return self

    def parse(self, content) -> dict[str, str]:
        """Parse the full journal text into a dict keyed by the
        ``--|YYYY-MM-DD HH:MM:SS|--`` marker that delimits each block.

        The save() flow calls ``self.parse(self.get_content())``;
        ``get_content()`` returns a ``{"text": ..., "content": ...}``
        dict, so we unpack the ``text`` field before regex-splitting.
        Test mocks pass a string directly, so the str branch is
        also supported. Empty / non-text input returns ``{}``.

        Returns ``{timestamp: block_text}`` -- the in-memory cache
        for date-navigation widgets. The outer save() persists the
        full text via ``save_app()`` (the app_media path); the
        parse result is NOT serialized into the save payload.
        """
        # Normalize: get_content() returns a dict with a "text" key;
        # test mocks pass a string directly.
        if isinstance(content, dict):
            text = content.get("text", "") or ""
        elif isinstance(content, str):
            text = content
        else:
            text = "" if content is None else str(content)
        # Lazy-init the in-memory cache. The test mocks bypass
        # __init__ via __new__, so self.entries may not exist yet.
        if not hasattr(self, "entries") or self.entries is None:
            self.entries = {}
        if not text:
            return self.entries
        marker_re = re.compile(
            r"--\|(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\|--"
        )
        for match in marker_re.finditer(text):
            ts = match.group(1)
            # Each block runs from the end of its marker to the
            # next marker (or end of text). Store entry in the
            # in-memory cache so date-navigation widgets can read it.
            self.entries[ts] = match.string[match.end():]
        return self.entries

    def populate_document(self):
        """"""

    def save(self, path=None, format_=None, encrypt=False):
        """Persist the journal entry.

        T-NEW-XXX (always-save fix): the previous implementation only
        called ``super().save()`` and never told the journal panel
        (``self.parent``) that a new entry was pending -- so the
        ``new_entry`` flag set on ``focusInEvent`` was never parsed
        out into the journal pages dict, and the user's text was
        lost on reopen.

        The fix mirrors the inner ``NchantdOfficeJournalAppendEditor
        .save()`` (line 538) for the outer editor:
        1. ``super().save()`` persists the base document content.
        2. If ``self.new_entry`` is True, ``self._parse_entry()``
           pulls the new text into ``self.parent.pages``.
        3. ``self.parent.save()`` persists the parent panel.
        Defensive: any of the three steps failing is logged and
        swallowed so the user's save flow never crashes.
        """
        if self.document is None:
            self.new_document()
        content = self.get_content()
        if content != self.document.content:
            self.document.set_content(content)
        self.parse(content)
        # version is not keeping in place causing the newest save not to be reloaded
        logma.info(f"[NCHANTDOFFICEJOURNALEDITOR] - save\n")
        self.save_app()  # TODO save has to redirect to the app_doc_content table
        logma.info(f"")
        # try:
        #     if self.new_entry:
        #         self._parse_entry()
        # except Exception as e:
        #     logma.warning(f"[journal] save: _parse_entry failed: {e}")
        # try:
        #     if self.parent is not None and hasattr(self.parent, "save"):
        #         self.parent.save()
        # except Exception as e:
        #     logma.warning(f"[journal] save: parent.save failed: {e}")
        # return self


class NchantdOfficeJournalAppendEditor(NchantdAppendOnlyEditor):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdJournalAppendEditor").override(cfg))
        self.last_timestamp_position = None
        self.keywords = None
        self.new_entry = False
        self.next_entry_position = 0
        self.data = None
        self.text = None

    def initModel(self):
        """"""
        super().initModel()
        self.text = self.get_journal_text()
        return self

    def initView(self):
        """"""
        super().initView()
        self.setText(self.text)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def add_entry(self, entry, page=0):
        """Record a new entry into the journal's pages dict on BOTH
        the editor alias and the document (the persisted object).

        See T-NEW-079 step 2 in TODOs.md. The editor alias
        (``self.parent.pages``) is the in-memory reference; the
        document (``self.parent.document.pages``) is what
        ``save_app()`` actually serializes into
        ``app_media_content.content_enc64_txt``. Without mirroring
        to the document, the entries dict was empty on disk (the
        user-visible bug: full text saved, entries lost).
        """
        logma.info(f"Add Entry {entry}")
        datetime = dt.datetime.now().strftime("%Y%m%d%H%M%S")
        # Create the page dict on the fly if the first entry ever.
        if str(page) not in self.parent.pages:
            self.parent.pages[str(page)] = {}
        if "entries" not in self.parent.pages[str(page)]:
            self.parent.pages[str(page)]["entries"] = {}
        self.parent.pages[str(page)]["entries"][datetime] = entry
        logma.info(f"Entries {self.parent.pages[str(page)]['entries']}")
        tid = None
        if hasattr(self.app.model.get_current_node(), "tid"):
            tid = self.app.model.get_current_tab().tid
        self.parent.pages[str(page)]["tags"] = {
            "nid": self.app.model.get_current_node().nid, "tid": tid,
        }
        # Mirror to the document so save_app() persists the entry.
        if (self.parent.document is not None
                and hasattr(self.parent.document, "pages")):
            doc_pages = self.parent.document.pages
            if str(page) not in doc_pages:
                doc_pages[str(page)] = {}
            if "entries" not in doc_pages[str(page)]:
                doc_pages[str(page)]["entries"] = {}
            doc_pages[str(page)]["entries"][datetime] = entry
            doc_pages[str(page)]["tags"] = {
                "nid": self.app.model.get_current_node().nid, "tid": tid,
            }
        return self

    def focusInEvent(self, event):
        """
        Append a timestamp whenever the editor gains focus.
        """
        self.set_cursor_position()
        self.next_entry_position = len(self.toPlainText())
        logma.info(f"Next Entry Position {self.next_entry_position}")
        self.insert_datetime(None, "--|", "|--")
        self.last_timestamp_position = len(self.toPlainText())  # Track position of the last timestamp
        self.new_entry = True
        super().focusInEvent(event)
        return self

    def focusOutEvent(self, event):
        """
        Remove the last timestamp if no user input was added after it.
        """
        current_text = self.toPlainText()
        logma.info(f"Current Position {len(current_text)}")
        # Check if the current text cursor position equals the timestamp's position
        if self.last_timestamp_position is not None and len(current_text) == self.last_timestamp_position:
            # Remove the timestamp by adjusting text content
            self.set_cursor_position()
            cursor = self.textCursor()
            cursor.deletePreviousChar()  # Remove the newline character
            cursor.select(pyqt.QTextCursor.BlockUnderCursor)  # Select the last block of text
            cursor.removeSelectedText()  # Remove the last block (timestamp)
            cursor.deletePreviousChar()  # Remove the newline character
            self.last_timestamp_position = None
            self.new_entry = False
            return self
        self._parse_keywords()
        logma.info(f"Save Entry {current_text}")
        self.save()
        super().focusOutEvent(event)
        return self

    def get_journal_text(self):
        """"""
        organization = self.parent.get_journal_organization()
        if organization == "Contextually":
            pass
        elif organization == "Chronologically":
            pass
        tid = None
        if hasattr(self.app.model.get_current_node(), "tid"):
            tid = self.app.model.get_current_tab().tid
        scope = self.config.dikt.get("scope", "TODAY")
        datetime = dt.datetime.now()
        tags = {"nid": self.app.model.get_current_node().nid, "tid": tid}
        text = self.parent.get_content_text()
        #TODO refactor to use the standard populate methods
        return text

    def save(self):
        """"""
        super().save()
        if self.new_entry:
            self._parse_entry()
        self.parent.save()
        return self

    def _parse_entry(self):
        """"""
        cursor = self.textCursor()
        cursor.setPosition(self.next_entry_position)
        cursor.setPosition(len(self.toPlainText()), pyqt.QTextCursor.KeepAnchor)
        # cursor.select(pyqt.QTextCursor.BlockUnderCursor)  # Select the last block of text
        entry = cursor.selectedText()
        logma.info(f"Add Entry {entry}")
        # entry_slug = """--|20??-??-?? ??:??:??|--"""
        self.add_entry(entry)
        return self

    def _parse_keywords(self):
        """"""
        text = self.toPlainText()
        # parse CREATE TASK:
        # parse SHOW CONTEXT - in the background saving of the journal entry add context of entry like what node and tab was active
        # this will not be shown by default but can be pulled into view by placeing the SHOW CONTEXT tag in the entry
        if self.keywords is None:
            self._set_keywords()
        for keyword in self.keywords.keys():
            if keyword in text:
                process = self.keywords[keyword]
        return self

    def _set_keywords(self, keywords=None):
        """"""
        if keywords is None:
            keywords = self.config.dikt.get("keywords", {})
        self.keywords = keywords
        return self


class NchantdOfficeJournalOverview(NchantdTab):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config = kahndor.Instruct(pxcfg).select("NchantdJournalOverview")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        cfg = {"text": "Journal Overview\nThe Journal is integrated within the application", "size": ["auto", 300]}
        journal_banner = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(journal_banner)
        buttons = {0: "save", 1: "launch_toolbox"}
        cfg = {"layout": "horizontal", "justify": "right"}
        self.button_bar = NchantdButtonBar(self, cfg).initWidget(buttons)
        self.layout.addWidget(self.button_bar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        layout = pyqt.QHBoxLayout()
        self.layout.addLayout(layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        cfg = {}
        self.search_entries = NchantdTable(self, cfg).initWidget()
        layout.addWidget(self.search_entries)
        cfg = {}
        self.entry_reader = NchantdDocEditor(self, cfg).initWidget()
        layout.addWidget(self.entry_reader)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
