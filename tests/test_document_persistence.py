"""Sprint-1 regression tests for document persistence behavior."""

from types import SimpleNamespace

# Importing models first establishes the nchantrs tabset dependency order used
# by the application and avoids the package's known circular import on a direct
# documents-module import.
import nchantdoffice.models  # noqa: F401
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocumentMixin


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
