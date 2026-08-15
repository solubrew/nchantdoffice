"""T-NEW-124: doctype guard in NchantdOfficeScript restore.

User directive (2026-08-15): if the content being restored contains

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" 
    "http://www.w3.org/TR/REC-html40/strict.dtd">

then it must be formatted as HTML — regardless of what
``document.syntax`` claims. That doctype is the signature Qt's
``QTextEdit.toHtml()`` stamps on every rich-text payload it
serialises; when such a payload round-trips back through the
restore path, rendering it with any other setter (setPlainText,
setMarkdown, pygments highlight) strips the formatting and in the
pygments case double-wraps the HTML source in a highlight <pre>.

The guard lives at the top of ``_apply_syntax_highlighting`` so
every restore path (DB payload, preserved unit html, plain text
fallback) is covered.
"""

from types import SimpleNamespace


class _SpyEditor:
    """Minimal QTextEdit stand-in recording which setter was used."""

    def __init__(self):
        self.set_html_calls = []
        self.set_plain_text_calls = []
        self.set_markdown_calls = []

    def setHtml(self, html):
        self.set_html_calls.append(html)

    def setPlainText(self, text):
        self.set_plain_text_calls.append(text)

    def setMarkdown(self, md):
        self.set_markdown_calls.append(md)

    def setStyleSheet(self, sheet):
        pass


DOCTYPE_STRICT = (
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
    '"http://www.w3.org/TR/REC-html40/strict.dtd">'
)

FULL_HTML_PAYLOAD = (
    f"{DOCTYPE_STRICT}\n"
    "<html><head><meta name=\"qrichtext\" content=\"1\" /></head>"
    "<body><p style=\"margin-top:0\">Some <b>bold</b> text</p></body></html>"
)


def _bare_widget(cls):
    return cls.__new__(cls)


def _make_widget(syntax, text):
    import nchantdoffice.models  # noqa: F401  (import side effects)
    from nchantdoffice.widgets.documents.media.scripts import (
        NchantdOfficeScript,
    )

    widget = _bare_widget(NchantdOfficeScript)
    widget.document = SimpleNamespace(
        syntax=syntax,
        file_format=syntax,
        file_path=None,
        content={"content": {"file_path": None, "text": text}},
        text=SimpleNamespace(html=""),
    )
    widget.document_editor = _SpyEditor()
    widget.config = SimpleNamespace(dikt={"document": {"syntax": syntax}})
    return widget


def test_doctype_guard_routes_to_sethtml_for_plain_text_syntax():
    """A strict-doctype payload with syntax='plain-text' must render
    via setHtml, not setPlainText (formatting must survive)."""
    widget = _make_widget("plain-text", FULL_HTML_PAYLOAD)
    widget._apply_syntax_highlighting(FULL_HTML_PAYLOAD)
    editor = widget.document_editor
    assert editor.set_html_calls, "doctype payload must go through setHtml"
    assert editor.set_html_calls[0] == FULL_HTML_PAYLOAD
    assert not editor.set_plain_text_calls, "setPlainText must not run"


def test_doctype_guard_routes_to_sethtml_for_python_syntax():
    """A strict-doctype payload saved under syntax='python' must not
    be pygments-highlighted (which would wrap the HTML source in a
    highlight <pre> and destroy the formatting)."""
    widget = _make_widget("python", FULL_HTML_PAYLOAD)
    widget._apply_syntax_highlighting(FULL_HTML_PAYLOAD)
    editor = widget.document_editor
    assert editor.set_html_calls, "doctype payload must go through setHtml"
    assert editor.set_html_calls[0] == FULL_HTML_PAYLOAD


def test_doctype_guard_routes_to_sethtml_for_markdown_syntax():
    """A strict-doctype payload with syntax='markdown' must render
    via setHtml, not setMarkdown."""
    widget = _make_widget("markdown", FULL_HTML_PAYLOAD)
    widget._apply_syntax_highlighting(FULL_HTML_PAYLOAD)
    editor = widget.document_editor
    assert editor.set_html_calls, "doctype payload must go through setHtml"
    assert editor.set_html_calls[0] == FULL_HTML_PAYLOAD
    assert not editor.set_markdown_calls, "setMarkdown must not run"


def test_doctype_guard_honors_real_doctype_spacing_variant():
    """The doctype token can appear with different internal spacing
    (single-line vs wrapped). The guard matches on the two stable
    substrings: the W3C strict DTD public identifier + the Qt
    qrichtext meta or the strict.dtd URL."""
    payload = (
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
        '"http://www.w3.org/TR/REC-html40/strict.dtd">'
        "<html><body><p>variant</p></body></html>"
    )
    widget = _make_widget("plain-text", payload)
    widget._apply_syntax_highlighting(payload)
    editor = widget.document_editor
    assert editor.set_html_calls, "spacing-variant doctype must go through setHtml"
    assert not editor.set_plain_text_calls


def test_no_doctype_plain_text_still_uses_setplaintext():
    """The guard must NOT hijack genuinely plain payloads — plain
    text under syntax='plain-text' still goes through
    setPlainText."""
    widget = _make_widget("plain-text", "just plain\ntext\n")
    widget._apply_syntax_highlighting("just plain\ntext\n")
    editor = widget.document_editor
    assert editor.set_plain_text_calls, "plain text must still use setPlainText"
    assert editor.set_plain_text_calls[0] == "just plain\ntext\n"


def test_no_doctype_python_still_uses_pygments_path():
    """The guard must NOT hijack real code — python source still
    goes through the pygments highlight path (setHtml with the
    highlighted, sanitised HTML — which is NOT the raw text)."""
    widget = _make_widget("python", "print('hello')\n")
    widget._apply_syntax_highlighting("print('hello')\n")
    editor = widget.document_editor
    assert editor.set_html_calls, "python source must still be highlighted"
    highlighted = editor.set_html_calls[0]
    assert "print" in highlighted
    assert highlighted != "print('hello')\n", (
        "highlight path must transform the text, not pass it through"
    )


def test_guard_is_case_insensitive_on_doctype():
    """Qt stamps uppercase; tolerate case drift in stored payloads."""
    payload = FULL_HTML_PAYLOAD.replace("HTML PUBLIC", "html public")
    widget = _make_widget("plain-text", payload)
    widget._apply_syntax_highlighting(payload)
    editor = widget.document_editor
    assert editor.set_html_calls, "case-drifted doctype must go through setHtml"
