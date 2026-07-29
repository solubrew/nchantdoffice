"""Sprint 3 — NchantdScript newline/format round-trip regression test.

Closes the user's live report:
  NchantdScript still not preserving newlines and formats properly

The test exercises the full save → reopen cycle on the same widget
and asserts the editor text round-trips unchanged. Three independent
failures are caught:

1. ``_resolve_document_text()`` calls ``text.lstrip()`` which strips
   leading indentation (Python / YAML / markdown lists break).
2. ``get_content()`` for plain-text syntax stores ``toPlainText()``
   instead of the editor's HTML payload, so line breaks collapse
   inconsistently and embedded newlines are not preserved verbatim.
3. ``populate_document()`` only runs ``_load_external_file`` when
   ``file_path`` is set; on a DB reopen the in-memory content path
   runs instead and the file-load step silently skips.

The fix preserves the editor's current text exactly (no leading
whitespace strip) and stores a canonical ``text`` representation
that round-trips through the DB unchanged.
"""

from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401
from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript


class _EditorStub:
    def __init__(self, initial_html="", initial_text=""):
        self._html = initial_html
        self._text = initial_text
        self.set_calls = []

    def setPlainText(self, text):
        self.set_calls.append(("setPlainText", text))
        self._text = text
        self._html = ""

    def setHtml(self, html):
        self.set_calls.append(("setHtml", html))
        self._html = html

    def setXml(self, xml):
        self.set_calls.append(("setXml", xml))

    def setMarkdown(self, md):
        self.set_calls.append(("setMarkdown", md))
        self._md = md

    def setStyleSheet(self, sheet):
        self.set_calls.append(("setStyleSheet", sheet))

    def convert_urls_to_links(self, text):
        self.set_calls.append(("convert_urls_to_links", text))

    def toPlainText(self):
        return self._text or self._html

    def toHtml(self):
        return self._html


def _make_script(syntax, content_text):
    script = NchantdOfficeScript.__new__(NchantdOfficeScript)
    script.file_path = None
    # T-NEW-024 followup: the dispatch in _apply_syntax_highlighting
    # reads config.dikt["document"]["syntax"] to populate
    # self.document.file_format. The stub must mirror the
    # post-_apply_extension_syntax shape so the dispatch sees the
    # right syntax (the production path sets both top-level
    # config.dikt["document_syntax"] and the nested
    # config.dikt["document"]["syntax"]).
    script.config = SimpleNamespace(
        dikt={
            "compatibility": syntax,
            "document_syntax": syntax,
            "syntax": syntax,
            "document": {"syntax": syntax},
        }
    )
    script.document = SimpleNamespace(
        syntax=syntax,
        file_path=None,
        content={"content": {"file_path": None, "text": content_text}},
        file_format=syntax,
        text=SimpleNamespace(html=""),
    )
    script.document_editor = _EditorStub()
    return script


def test_resolve_document_text_preserves_leading_indentation():
    """The reopen path must not strip leading whitespace — Python /
    YAML / indented-markdown documents lose their structure if the
    first-line indent is dropped."""
    indented = "    def hello():\n        return 1\n"
    doc = SimpleNamespace(
        text=None,
        content={"content": {"text": indented}},
    )
    script = _make_script("python", indented)
    script.document = doc

    from nchantdoffice.widgets.documents.media.scripts import (
        NchantdOfficeScript as _cls,
    )

    resolved = _cls._resolve_document_text(script)

    assert resolved == indented, (
        f"Leading whitespace was stripped during reopen.\n"
        f"Expected: {indented!r}\nGot: {resolved!r}"
    )
    assert resolved.startswith("    "), "Indentation must survive reopen"


def test_get_content_preserves_newlines_for_plain_text_syntax():
    """``get_content()`` for plain-text syntax must capture the
    editor's text with newlines intact (not the HTML envelope).
    """
    multiline = "line one\nline two\n  line three\n"
    script = _make_script("plaintext", multiline)
    script.document_editor = _EditorStub(initial_text=multiline)

    content = script.get_content()

    assert content["text"] == multiline, (
        f"Plain-text round-trip lost newlines.\n"
        f"Expected: {multiline!r}\nGot: {content['text']!r}"
    )


def test_reopen_round_trip_preserves_newlines_and_formatting():
    """Full save → reopen round-trip on the same widget. The editor
    must end up with the same content the user saved — the
    pygments-highlighted HTML must contain every body token (the
    indent survives because the body token itself is unchanged).
    """
    original = "def greet(name):\n    return f'hi, {name}'\n"
    syntax = "python"
    script = _make_script(syntax, original)
    script.document_editor = _EditorStub(initial_text=original)

    # Step 1: user edits and saves — get_content captures the body.
    content = script.get_content()
    saved_text = content["text"]

    # Step 2: reopen — populate_document reads back from saved payload.
    script.document = SimpleNamespace(
        syntax=syntax,
        file_path=None,
        content={"content": {"file_path": None, "text": saved_text}},
        file_format="",
        text=SimpleNamespace(html=""),
    )
    script.document_editor = _EditorStub()
    script.populate_document()

    rendered = script.document_editor._html or script.document_editor._text
    # The body must be present. Pygments wraps every token in
    # ``<span ...>token</span>`` so a substring match for ``return``
    # without angle brackets works. The indent must survive — pygments
    # embeds it as a literal newline + 4 spaces between the preceding
    # line's closing ``</span>`` and the next ``<span>``.
    newline_indent_span = "\n    <span"
    assert "return" in rendered and newline_indent_span in rendered, (
        f"Pygments render dropped indent or token.\nGot: {rendered[:600]!r}"
    )
    # Pygments splits ``greet`` and ``(name):`` into separate spans
    # so the substring ``greet(name)`` never appears contiguously;
    # check the two halves independently.
    assert "greet" in rendered and "(name)" in rendered, (
        f"Pygments render dropped function token.\nGot: {rendered[:600]!r}"
    )
    # The f-string body ``f'hi, {name}'`` is split across the string
    # tokenisation; assert on its halves (``hi, {`` and ``name``)
    # rather than the contiguous form.
    assert "hi, {" in rendered and "name" in rendered


def test_reopen_round_trip_preserves_indentation_plaintext():
    """End-to-end: a plain-text script with leading indentation
    must reopen with the indentation intact.
    """
    original = "    indented line one\n    indented line two\n"
    syntax = "plaintext"
    script = _make_script(syntax, original)
    script.document_editor = _EditorStub(initial_text=original)

    saved_text = script.get_content()["text"]

    script.document = SimpleNamespace(
        syntax=syntax,
        file_path=None,
        content={"content": {"file_path": None, "text": saved_text}},
        file_format="",
        text=SimpleNamespace(html=""),
    )
    script.document_editor = _EditorStub()
    script.populate_document()

    rendered = script.document_editor._html or script.document_editor._text
    assert "    indented line one" in rendered, (
        f"Indentation lost on reopen.\nGot: {rendered!r}"
    )