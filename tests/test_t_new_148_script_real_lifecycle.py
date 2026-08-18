"""Regression for the real external Script open-edit-save-reopen lifecycle."""
from pathlib import Path
from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript


class _Editor:
    def __init__(self):
        self.text = ""

    def setPlainText(self, text):
        self.text = text

    def toPlainText(self):
        return self.text

    def toHtml(self):
        return self.text

    def setStyleSheet(self, _style):
        pass


def _script(path):
    script = NchantdOfficeScript.__new__(NchantdOfficeScript)
    script.file_path = str(path)
    script.document = SimpleNamespace(
        file_path=str(path), location="external", syntax="markdown",
        content={}, text=SimpleNamespace(html=""),
        set_content=lambda content: setattr(script.document, "content", content),
    )
    script.document_editor = _Editor()
    script.config = SimpleNamespace(dikt={"compatibility": "markdown", "document": {"syntax": "markdown"}})
    script.format_type = "markdown"
    script._initial_load = False
    return script


def test_external_script_open_edit_save_reopen_preserves_real_file_lifecycle(tmp_path, monkeypatch):
    path = tmp_path / "note.md"
    original = "# Original\n\n    indented\n"
    edited = "# Edited\n\n    still indented\n"
    path.write_text(original, encoding="utf-8")

    writer = _script(path)
    assert writer._load_external_file() is True
    assert writer.document_editor.toPlainText() == original
    writer.document_editor.setPlainText(edited)

    stored = []
    monkeypatch.setattr(NchantdOfficeDocument, "save", lambda self, *a, **k: stored.append(self.document.content) or self)
    writer.save()

    assert path.read_bytes() == edited.encode("utf-8")
    assert stored, "DB recovery-copy path must still run"

    reopened = _script(path)
    assert reopened._load_external_file() is True
    assert reopened.document_editor.toPlainText() == edited


def test_external_script_save_refuses_to_write_before_successful_load(tmp_path, monkeypatch):
    path = tmp_path / "existing.md"
    original = "do not truncate\n"
    path.write_text(original, encoding="utf-8")
    script = _script(path)
    script.document_editor.setPlainText("")
    script._external_file_loaded = False
    monkeypatch.setattr(NchantdOfficeDocument, "save", lambda self, *a, **k: self)
    script.save()
    assert path.read_text(encoding="utf-8") == original
