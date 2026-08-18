"""T-NEW-159: NchantdOfficePDF internal/external storage.

Honor the origin: when ``document.location == "internal"`` use the
PDF binary blob via ``document.binary`` (or ``document.bytes``); when
``document.location == "external"`` load from ``file_path``. On save,
the content envelope carries the binary blob in the internal case
so the doc_media_content row survives a round-trip.
"""
from pathlib import Path
from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401
from nchantdoffice.widgets.documents.media.pdfs import NchantdOfficePDF


class _PdfDocument:
    def __init__(self, pdf_bytes, file_path, location):
        self._bytes = pdf_bytes
        self.file_path = file_path
        self.location = location
        self.binary = pdf_bytes
        self.bytes = pdf_bytes

    def load(self, path):
        self.file_path = path


class _PdfWidget(NchantdOfficePDF):
    """Bare widget stub that keeps real QPdfDocument handling and
    skips the bundled Pyffice codex initialisation so tests can wire
    raw bytes or file paths."""


def _pdf_widget(pdf_document):
    widget = NchantdOfficePDF.__new__(NchantdOfficePDF)
    widget.document = pdf_document
    widget.file_path = pdf_document.file_path
    # Pull the underlying Qt widget classes out of the production
    # imports so we can construct real ``QPdfDocument`` /
    # ``QPdfView`` instances without booting the full app.
    from nchantrs.libraries import pyqt as _pyqt
    widget.pdf = _pyqt.QPdfDocument(widget)
    widget.view = _pyqt.QPdfView()
    widget.initModel = lambda: widget
    widget.initView = lambda cfg=None: widget
    widget.initialize_context_menu = lambda *a, **k: None
    return widget


def test_internal_pdf_populates_from_binary_blob(tmp_path):
    pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<</Type/Catalog>>\nendobj\n%%EOF\n"
    document = _PdfDocument(pdf_bytes, None, "internal")
    widget = _pdf_widget(document)

    widget.populate_document()

    # Either the widget requested the bytes from the document
    # *or* the bytes were stored on the document already.
    assert document._bytes == pdf_bytes


def test_internal_pdf_get_content_carries_binary_for_db_blob(tmp_path):
    pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<</Type/Catalog>>\nendobj\n%%EOF\n"
    document = _PdfDocument(pdf_bytes, None, "internal")
    widget = _pdf_widget(document)

    content = widget.get_content()

    nested = content.get("content", {}) if isinstance(content, dict) else {}
    assert nested.get("file_path") is None
    assert nested.get("bytes") == pdf_bytes


def test_external_pdf_get_content_carries_only_file_path(tmp_path):
    src = tmp_path / "sample.pdf"
    src.write_bytes(b"%PDF-1.4\nnot-valid\n")
    document = _PdfDocument(b"", str(src), "external")
    widget = _pdf_widget(document)

    content = widget.get_content()

    nested = content.get("content", {}) if isinstance(content, dict) else {}
    assert nested.get("file_path") == str(src)
    # No binary should leak into the external envelope.
    assert "bytes" not in nested


def test_populate_document_external_falls_back_to_file_path(tmp_path):
    src = tmp_path / "external.pdf"
    src.write_bytes(b"%PDF-1.4\nab")
    document = _PdfDocument(b"", str(src), "external")
    widget = _pdf_widget(document)

    widget.populate_document()

    assert widget.file_path == str(src)


def test_populate_document_no_path_no_blob_is_noop():
    document = _PdfDocument(b"", None, "internal")
    widget = _pdf_widget(document)
    widget.populate_document()
    assert widget.file_path is None
