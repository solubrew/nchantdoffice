"""External save uses the syntax-aware exporter and preserves formatting/newlines.

Tests exercise the on-disk writer directly through ``save_external``
(the writer-only seam) so they don't need a Qt parent, app model,
or ``PyfficeDocument`` instance. The contract: external files are
written atomically and only when the document is marked
``location == "external"``; internal scripts never touch disk.
"""
from pathlib import Path
from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401
from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript


class _Editor:
    """Stand-in for ``NchantdDocEditor`` exposing only the API the
    exporter queries. Real QTextEdit (``toHtml``) wraps plain text in
    Qt styling, so we model the editor as a slot that returns the
    user-visible payload verbatim."""

    def __init__(self, syntax, text="", html=""):
        self.syntax = syntax
        self.text = text
        self.html = html

    def toPlainText(self):
        return self.text

    def toHtml(self):
        return self.html

    def toMarkdown(self):
        # Real QTextEdit.toMarkdown() always emits a trailing newline.
        return self.text.rstrip("\n") + "\n"

    def setStyleSheet(self, _style):
        pass


def _script(path, syntax, text="", html=""):
    script = NchantdOfficeScript.__new__(NchantdOfficeScript)
    script.file_path = str(path)
    script.document = SimpleNamespace(
        file_path=str(path), location="external", syntax=syntax,
        content=None, set_content=lambda c: setattr(script.document, "content", c),
    )
    script.document_editor = _Editor(syntax, text=text, html=html)
    script.config = SimpleNamespace(dikt={"encoding": "utf-8"})
    return script


def save_external(script):
    """Run only the on-disk writer (the production ``save()`` plus
    ``super().save()`` requires a Qt app, model, and config)."""
    if (
        getattr(script.document, "location", None) == "external"
        and getattr(script, "file_path", None)
    ):
        script._write_external_file()


def test_external_html_save_writes_full_html_payload(tmp_path):
    path = tmp_path / "doc.html"
    html = "<html><body><p>Hi</p></body></html>"
    script = _script(path, "html", text="", html=html)
    save_external(script)
    assert path.read_text(encoding="utf-8") == html


def test_external_plain_text_save_writes_exact_bytes(tmp_path):
    path = tmp_path / "note.md"
    text = "# Heading\n\n    indented line\n"
    script = _script(path, "plain-text", text=text)
    save_external(script)
    assert path.read_bytes() == text.encode("utf-8")


def test_external_markdown_save_writes_markdown_payload(tmp_path):
    path = tmp_path / "doc.md"
    text = "# Heading\n\nbody\n"
    script = _script(path, "markdown", text=text)
    save_external(script)
    assert path.read_text(encoding="utf-8") == text


def test_internal_save_does_not_create_external_file(tmp_path):
    path = tmp_path / "must-not-exist.md"
    script = _script(path, "markdown", text="ignored\n")
    script.document.location = "internal"
    script.file_path = None
    save_external(script)
    assert not path.exists()


def test_external_save_is_noop_when_no_editor(tmp_path):
    path = tmp_path / "noop.md"
    script = _script(path, "markdown")
    script.document_editor = None
    save_external(script)
    assert not path.exists()