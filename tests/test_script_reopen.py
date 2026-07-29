"""Sprint 2 — Script rich-text reopen regression test.

Closes the live `TODOs.md` item:
  NchantdScript is still loading with no formatting when returned to tab
  but loads properly when opened from a file directly.

Drives the actual ``populate_document`` / ``_apply_syntax_highlighting``
path through a stub document_editor and asserts that ``setHtml`` is
called with the preserved rich-text payload (not ``setPlainText`` with
empty content) when the saved Pyffice unit carries HTML.
"""

from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401
from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript


class _EditorStub:
    def __init__(self):
        self.calls = []

    def setPlainText(self, text):
        self.calls.append(("setPlainText", text))

    def setHtml(self, html):
        self.calls.append(("setHtml", html))

    def setXml(self, xml):
        self.calls.append(("setXml", xml))

    def setMarkdown(self, md):
        self.calls.append(("setMarkdown", md))


def _make_script(syntax, text_attr, content, data_pages=None):
    script = NchantdOfficeScript.__new__(NchantdOfficeScript)
    script.file_path = "/tmp/notes.html"
    script.config = SimpleNamespace(dikt={"compatibility": syntax})
    script.document = SimpleNamespace(
        syntax=syntax,
        file_path="/tmp/notes.html",
        content=content,
        file_format="",
        text=text_attr,
        data={"pages": data_pages or {}},
    )
    script.document_editor = _EditorStub()
    return script


def _html_unit(html):
    return {"meta_data": {"unit": {"html": html}}}


def test_populate_html_syntax_uses_setHtml_with_full_payload():
    """Live bug: a script saved with rich-text HTML loses its formatting
    on tab return. The reopen path must invoke ``setHtml`` with the
    preserved HTML when the syntax is ``html``.
    """
    preserved_html = "<html><body><b>Saved rich text</b></body></html>"
    script = _make_script(
        syntax="html",
        text_attr=SimpleNamespace(html=preserved_html),
        content={"content": {"file_path": "/tmp/notes.html"}},
        data_pages={"0": {"entries": {"0": _html_unit(preserved_html)}}},
    )

    NchantdOfficeScript._apply_syntax_highlighting(script, "<b>Saved rich text</b>")

    html_calls = [c for c in script.document_editor.calls if c[0] == "setHtml"]
    assert html_calls, f"Expected setHtml call; got {script.document_editor.calls!r}"
    assert html_calls[0][1] == preserved_html


def test_populate_plain_text_syntax_falls_back_to_setPlainText():
    """When the syntax is plain-text and no rich-text HTML is preserved,
    the reopen path must still call ``setPlainText`` with the supplied
    text — never silently drop formatting or fall through to a syntax
    error.
    """
    script = _make_script(
        syntax="plaintext",
        text_attr=SimpleNamespace(html=""),
        content={},
        data_pages={},
    )

    NchantdOfficeScript._apply_syntax_highlighting(script, "Just plain text")

    plain_calls = [c for c in script.document_editor.calls if c[0] == "setPlainText"]
    assert plain_calls, f"Expected setPlainText call; got {script.document_editor.calls!r}"
    assert plain_calls[0][1] == "Just plain text"