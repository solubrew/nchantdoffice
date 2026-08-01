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
from os.path import abspath, dirname, join
import datetime as dt
from bs4 import BeautifulSoup

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from kahndor.logma import Logma
from nchantrs.dialogs.dialogs import NchantdSigil
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.media.editors.editors import NchantdDocEditor
from nchantrs.widgets.annotations import NchantdLabel

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "notes.yaml")


class NchantdOfficeNote(NchantdSigil):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("NchantdNote", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeNote"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.editor = None
        self.is_dragging = False
        self.drag_start_position = pyqt.QPoint()
        self.sequence = None

    def initModel(self):
        """"""
        super().initModel()
        document = {"document": self.config.dikt.get("document", {})}
        document["document"]["version"] = self.config.dikt.get("document", {}).get("content_version_int", 0)
        self.document = self.app.model.codex.init_note(document)
        self.document.load_document()
        self.context_menu_name = "context.document.note"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        self.sequence = 0
        return self

    def initView(self):
        """"""
        super().initView()
        self.setWindowFlags(
            self.windowFlags() | pyqt.Qt.Tool | pyqt.Qt.WindowStaysOnTopHint | pyqt.Qt.FramelessWindowHint
        )
        # self.setWindowModality(pyqt.Qt.ApplicationModal)
        # self.setAttribute(pyqt.Qt.WA_TranslucentBackground)
        # self.set_note_name(self.config.dikt.get("name", "New Note"))
        # self.set_note_content(self.document.get_content())
        cfg = {}
        self.editor = NchantdOfficeNoteDocument(self, cfg).initWidget()
        self.layout.addWidget(self.editor)
        self.set_note_name(self.config.dikt.get("name", "New Note"))
        # self.move(self.config.dikt.get("x", 1287), self.config.dikt.get("y", 125))
        self.launch_position()
        # self.setMinimumedWidth(350)
        # self.setMinimumedHeight(350)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        self.show()
        return self

    def close(self, event=None, *args, **kwargs):
        """"""
        super().close()
        return self

    def launch_position(self):
        """"""
        parent_geometry = self.parent.frameGeometry()  # Get the position and size of the parent
        x = parent_geometry.center().x() * 1.5
        y = parent_geometry.center().y() * 0.3 + self.geometry().height() * 0.1 * self.sequence
        self.move(x, y)
        return self

    def mousePressEvent(self, event: pyqt.QMouseEvent):
        # Check if it's the left mouse button
        if event.button() == pyqt.Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: pyqt.QMouseEvent):
        # If dragging, update the position of the dialog
        if self.is_dragging and event.buttons() == pyqt.Qt.LeftButton:
            pos = event.globalPosition().toPoint() - self.drag_start_position
            logma.info(f"pos: {pos}")
            self.move(pos)
            event.accept()

    def mouseReleaseEvent(self, event: pyqt.QMouseEvent):
        # Stop dragging when the left mouse button is released
        if event.button() == pyqt.Qt.LeftButton:
            self.is_dragging = False
            event.accept()

    def move(self, x, y=None):
        """"""
        if y is None:
            y = x.y()
            x = x.x()
        super().move(x, y)
        return self

    def save(self):
        """"""
        super().save()
        # self.document.set_content(self.document_editor.toHtml())
        # self.document.save()
        self.editor.save()
        return self

    def set_note_name(self, name):
        """"""
        self.setWindowTitle(name)
        return self

    def set_sequence(self, sequence):
        """"""
        self.sequence = sequence
        return self

    def store_note(self):
        """Persist the current note to the underlying storage.

        Writes the current note content via ``self.save`` which pushes
        the editor's text into the document and calls ``self.editor.save``
        to store it. Returns ``self`` for chainable call sites.
        """
        return self.save()


class NchantdOfficeNoteDocument(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Note", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeNoteDocument").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        cfg = {
            "buttons": {
                0: "_skip",
                150: "_skip",
                200: "_skip",
                100: "_skip",
                301: {"action": "hide", "handler": self.cmd_close_note},
                400: {"action": "cancel", "handler": self.cmd_delete_note},
                1000: "_skip",
            }
        }
        super().initView(cfg)
        cfg = {"background_color": "lightyellow", "default_text": "", "size": ["auto", "auto"]}
        self.document_editor = NchantdDocEditor(self, cfg).initWidget()
        self.layout.addWidget(self.document_editor)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_close_note(self, event=None, *args, **kwargs):
        """"""
        self.close()
        self.parent.closeEvent()
        return self

    def cmd_delete_note(self, event, *args, **kwargs):
        """"""
        self.delete_note(self.app.active_tab.active_note)
        return self

    def delete_note(self, note):
        """"""
        self.app.model.delete_note(note)
        self.parent.set_focus(note.position - 1)
        return self

    def save(self):
        """"""
        logma.info(f"HTML {self.document_editor.toHtml()}")

        if self.document.syntax == "html":
            html = """
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
            <html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /></head><body><[content]></body></html>
            """
            text = self.document_editor.toHtml()  # .replace("\n", "")
            soup = BeautifulSoup(text, "html.parser")
            content = html.replace("<[content]>", soup.body.decode_contents())
        else:
            content = self.document_editor.toPlainText()
        logma.info(f"Content: {content}")
        logma.info(f"Document {self.document.content}")
        if content != self.document.content:
            self.document.set_content(content)
            super().save()
        return self


class NchantdOfficeScratchEditor(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Scratch", parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeScratchEditor").override(cfg))
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
        self.text = None
        self.data = None
        self.document = None
        self.full_text = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        logma.info(f"initModel")
        self.document = self.app.model.codex.init_script({"document": self.config.get("document", {})})
        self.document.load_document()
        scope = self.config.dikt.get("scope", "TODAY")
        datetime = dt.datetime.now()
        self.full_text = ""
        logma.info(f"Full Text {self.full_text}")
        return self

    def initView(self):
        """ """
        cfg = {"default_toolbar": False}
        super().initView(cfg)
        self.top_layout = pyqt.QHBoxLayout()
        cfg = {"text": "Scratch Entries"}
        self.settings = NchantdLabel(self, cfg).initWidget()
        self.top_layout.addWidget(self.settings)
        self.layout.addLayout(self.top_layout)
        cfg = {"default_text": self.full_text}
        self.editor = NchantdDocEditor(self, cfg).initWidget()
        self.editor.set_background(hex="#4F5665")
        self.editor.setPlaceholderText("Enter text here...it will not be saved")
        self.layout.addWidget(self.editor)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
