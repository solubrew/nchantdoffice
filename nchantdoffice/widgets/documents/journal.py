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

# ======================================3rd Party Library Modules=====================================================||

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

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = False
logma = Logma(__name__)
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

    def initModel(self):
        """ """
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
        # logma.json(document)
        logma.info(f"Document {document}")
        self.document = self.app.model.codex.init_script(document)
        self.document.load_document()
        # logma.json(self.document.to_dict())
        self.pages = self.document.pages
        logma.info(f"Pages {self.pages}")
        # self.full_text = self.document.full_text
        self.full_text = text = self.document.text.to_dict()["unit"].get("value", "")
        logma.info(f"Full Text {self.full_text}")
        return self

    def initView(self):
        """ """
        cfg = {"default_toolbar": False}
        super().initView(cfg)
        self.top_layout = pyqt.QHBoxLayout()
        cfg = {
            "layout": "horizontal",
            "label": f"Date: {dt.datetime.now().strftime('%m/%d/%Y')}",
            "options": ["Contextually", "Chronologically"],
        }
        self.settings = NchantdDropDown(self, cfg).initWidget()
        self.top_layout.addWidget(self.settings)
        self.layout.addLayout(self.top_layout)
        cfg = {"default_text": self.full_text}
        self.editor = NchantdOfficeJournalAppendEditor(self, cfg).initWidget()
        self.editor.set_background(hex="#4F5665")
        self.layout.addWidget(self.editor)
        return self

    def initWidget(self):
        """ """
        self.initModel()
        self.initView()
        return self

    def get_journal_document(self, cfg):
        """"""
        document = self.app.model.get_view_journal(cfg)
        logma.json(document)
        return document

    def get_journal_organization(self):
        """"""
        value = self.settings.get_value()
        return value

    def save(self, path=None, format_=None, encrypt=False):
        """"""
        content = self.editor.toPlainText()
        logma.info(f"Data {self.document.pages}")
        logma.info(f"Document {self.document.to_dict()}")
        self.document.parse_content(content)
        # FIX (was double-save bug): Removed redundant super().save() call.
        # super().save() was nested inside `if content != self.document.content`
        # which created an inconsistent save path. self.document.save() handles
        # persistence (versioning + encryption); super().save() was redundant.
        if content != self.document.content:
            self.document.set_content(content)
        logma.info(f"Save Content {self.document.content}")
        # self.document.save() increments versions and (internal encryption..future)
        self.document.save()
        logma.info(f"Save Path {path}")
        if path:
            self.set_file_path(path)
        try:
            pid = self.app.view.panes["left"].tree.model.current_node.nid
            logma.info(f"Save PID {pid}")
        except (AttributeError, KeyError) as e:
            logma.warning(f"Could not resolve PID: {e}")
        logma.info(f"Save DID {self.document.did}")
        logma.info(f"Save Document {self.document.to_dict()}")
        logma.json(self.document.to_dict())
        self.app.model.add_document_content_app(self.document.to_dict(), version=self.document.version)
        return self

    # def store_journal(self):
    #     """"""
    #     #


class NchantdOfficeJournalAppendEditor(NchantdAppendOnlyEditor):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdJournalAppendEditor"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.last_timestamp_position = None
        self.keywords = None
        self.new_entry = False
        self.next_entry_position = 0
        self.data = None
        self.text = None

    def initModel(self):
        """"""
        super().initModel()

        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def add_entry(self, entry, page=0):
        """"""
        logma.info(f"Add Entry {entry}")
        datetime = dt.datetime.now().strftime("%Y%m%d%H%M%S")
        if "entries" not in self.parent.pages[str(page)]:
            self.parent.pages[str(page)]["entries"] = {}
        self.parent.pages[str(page)]["entries"][datetime] = entry
        logma.info(f"Entries {self.parent.pages[str(page)]['entries']}")
        tid = None
        if hasattr(self.app.model.get_current_node(), "tid"):
            tid = self.app.model.get_current_tab().tid
        self.parent.pages[str(page)]["tags"] = {"nid": self.app.model.get_current_node().nid, "tid": tid}
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
        text = self.app.model.get_journal(scope, datetime, tags)
        text = ""
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
