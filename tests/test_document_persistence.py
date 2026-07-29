"""Sprint-1 regression tests for document persistence behavior."""

from types import SimpleNamespace

# Importing models first establishes the nchantrs tabset dependency order used
# by the application and avoids the package's known circular import on a direct
# documents-module import.
import nchantdoffice.models  # noqa: F401
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocumentMixin, NchantdOfficeDocument
from nchantdoffice.widgets.documents.atnrg.browsers import NchantdOfficeWebBrowser
from nchantdoffice.widgets.documents.workbooks.notebooks import NchantdOfficeNotebook
from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript


class _Document:
    def __init__(self, file_path="/tmp/existing.txt"):
        self.did = "doc-1"
        self.file_path = file_path
        self.content = {"body": "saved"}
        self.version = 1
        self.is_changed = True
        self.saved_paths = []

    def save(self, path):
        self.saved_paths.append(path)

    def to_dict(self):
        return {"did": self.did, "content": self.content, "version": self.version}


class _PersistenceHarness(NchantdOfficeDocumentMixin):
    def __init__(self, document):
        self.document = document
        self.file_path = document.file_path
        self.config = SimpleNamespace(dikt={})
        self.document_editor = None
        self.stored = []
        self.app = SimpleNamespace(
            model=SimpleNamespace(store_document=self.stored.append),
            view=SimpleNamespace(
                panes={
                    "left": SimpleNamespace(
                        tree=SimpleNamespace(model=SimpleNamespace(current_node=SimpleNamespace(nid="node-1")))
                    ),
                    "center": SimpleNamespace(model=SimpleNamespace(current_tab=SimpleNamespace(position=0))),
                }
            ),
        )


def test_save_without_new_path_preserves_existing_external_path():
    document = _Document()
    widget = _PersistenceHarness(document)

    NchantdOfficeDocumentMixin.save(widget)

    assert widget.file_path == "/tmp/existing.txt"
    assert document.file_path == "/tmp/existing.txt"
    assert document.saved_paths == ["/tmp/existing.txt"]
    assert widget.stored == [document]


def test_save_internal_passes_pyffice_document_not_serialized_dict():
    document = _Document()
    widget = _PersistenceHarness(document)

    widget.save_internal()

    assert widget.stored == [document]


def _bare_qt_widget(cls):
    """Allocate a Qt-derived widget without running its coupled constructor."""
    return cls.__new__(cls)


def test_browser_content_keeps_payload_under_canonical_content_key():
    profile = {"active_url": "https://example.test", "history": ["https://example.test"]}
    browser = _bare_qt_widget(NchantdOfficeWebBrowser)
    browser.document = SimpleNamespace(active_page=SimpleNamespace(to_dict=lambda: profile))

    assert browser.get_content() == {"content": profile}


def test_notebook_content_keeps_location_and_serialized_notebook():
    notebook = _bare_qt_widget(NchantdOfficeNotebook)
    notebook.file_path = "/tmp/work.ipynb"
    notebook.cells = [{"cell_type": "code", "source": ["print('ok')"]}]
    notebook.kernel_name = "python3"

    content = notebook.get_content()

    assert content["content"]["file_path"] == "/tmp/work.ipynb"
    assert b'"nbformat": 4' in content["content"]["notebook_bytes"]


def test_script_save_captures_current_editor_html_before_parent_save(monkeypatch):
    script = _bare_qt_widget(NchantdOfficeScript)
    script.document = SimpleNamespace(
        syntax="html",
        content={},
        set_content=lambda content: setattr(script.document, "content", content),
    )
    script.document_editor = SimpleNamespace(
        toHtml=lambda: "<html><body><b>Current edit</b></body></html>",
        toPlainText=lambda: "Current edit",
    )
    script.config = SimpleNamespace(dikt={})
    script.file_path = "/tmp/work.html"
    captured = []

    monkeypatch.setattr(NchantdOfficeDocument, "save", lambda self, *args, **kwargs: captured.append(self.document.content) or self)

    script.save()

    assert captured
    assert "<b>Current edit</b>" in captured[0]["text"]
