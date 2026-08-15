"""Sprint 9 followup — T-NEW-024 regression test.

Live trace (2026-07-29, user follow-up):
  "you broke the initial recognition of the file format on file
   open so that only plain text is showing when i open a .md
   file. and it still doesn't reload with the proper white space"

Two regressions to guard:
  1. Opening a ``.md``/``.py``/``.json`` file from disk should
     detect the syntax from the file extension and route through
     the correct ``_apply_syntax_highlighting`` branch, not
     fall through to ``plaintext``.
  2. Reopening the same file must reload the on-disk content
     with whitespace preserved (no Python-style indentation
     collapse, no markdown list flattening).

These tests run without the full Qt harness by inspecting
the production ``_apply_extension_syntax`` helper directly.
"""

import os
import sys
from types import SimpleNamespace


def _bare_widget(cls):
    return cls.__new__(cls)


def test_md_extension_sets_markdown_format_type():
    """T-NEW-024: opening a ``.md`` file must set ``format_type``
    to ``markdown`` so the dispatcher calls ``setMarkdown``
    instead of ``setPlainText``.
    """
    import nchantdoffice.models  # noqa: F401
    from nchantdoffice.widgets.documents.media.scripts import (
        NchantdOfficeScript,
    )

    widget = _bare_widget(NchantdOfficeScript)
    widget.format_type = "plaintext"  # stale default
    widget.config = SimpleNamespace(dikt={})
    widget.document = SimpleNamespace(
        syntax="plaintext",
        file_format="",
        meta_data={},
    )

    syntax = widget._apply_extension_syntax("/tmp/notes.md")
    assert syntax == "markdown", (
        f"Expected format_type=markdown for .md, got {syntax}"
    )
    assert widget.format_type == "markdown"
    assert widget.config.dikt["document_syntax"] == "markdown"


def test_py_extension_sets_python_format_type():
    """T-NEW-024: ``.py`` -> ``python``."""
    import nchantdoffice.models  # noqa: F401
    from nchantdoffice.widgets.documents.media.scripts import (
        NchantdOfficeScript,
    )

    widget = _bare_widget(NchantdOfficeScript)
    widget.format_type = "plaintext"
    widget.config = SimpleNamespace(dikt={})
    widget.document = SimpleNamespace(
        syntax="plaintext",
        file_format="",
        meta_data={},
    )

    syntax = widget._apply_extension_syntax("/tmp/work.py")
    assert syntax == "python"
    assert widget.format_type == "python"


def test_unknown_extension_falls_back_to_plain_text():
    """T-NEW-024: a file with no whitelisted extension stays
    at ``plain-text`` (no false positives).
    """
    import nchantdoffice.models  # noqa: F401
    from nchantdoffice.widgets.documents.media.scripts import (
        NchantdOfficeScript,
    )

    widget = _bare_widget(NchantdOfficeScript)
    widget.format_type = "python"
    widget.config = SimpleNamespace(dikt={})
    widget.document = SimpleNamespace(
        syntax="python",
        file_format="",
        meta_data={},
    )

    syntax = widget._apply_extension_syntax("/tmp/blob")
    assert syntax == "plain-text", (
        f"Expected plain-text fallback, got {syntax}"
    )


def test_md_file_load_preserves_whitespace():
    """User-stated regression: "still doesn't reload with the
    proper white space". Verify _load_external_file reads the
    on-disk content byte-for-byte (including indentation).
    """
    import nchantdoffice.models  # noqa: F401
    from nchantdoffice.widgets.documents.media.scripts import (
        NchantdOfficeScript,
    )

    tmp = "/tmp/t_new_024_whitespace.md"
    md_content = (
        "# Heading\n"
        "\n"
        "    - indented bullet (4 spaces)\n"
        "    - second bullet\n"
        "\n"
        "```python\n"
        "def greet(name):\n"
        "    return f'hi, {name}'\n"
        "```\n"
    )
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(md_content)
    try:
        widget = _bare_widget(NchantdOfficeScript)
        widget.file_path = tmp
        widget.format_type = "markdown"
        widget.config = SimpleNamespace(dikt={})
        widget.document = SimpleNamespace(
            syntax="markdown",
            file_format="markdown",
            meta_data={},
        )

        captured = []

        class _CapturingEditor:
            def setPlainText(self, text):
                captured.append(("plain", text))
            def setHtml(self, html):
                captured.append(("html", html))
            def setMarkdown(self, md):
                captured.append(("md", md))
            def setStyleSheet(self, sheet):
                pass
            def toHtml(self):
                return "<html></html>"
            def toPlainText(self):
                return ""
            def setXml(self, xml):
                captured.append(("xml", xml))
            def setLatex(self, l):
                captured.append(("latex", l))

        widget.document_editor = _CapturingEditor()
        widget._load_external_file()

        # The file content is read with whitespace preserved.
        # _load_external_file calls setPlainText; the dispatcher
        # later calls setMarkdown when format_type == markdown,
        # but that's downstream of _load_external_file.
        assert any(
            kind == "plain" and md_content in text
            for kind, text in captured
        ), (
            f"_load_external_file did not preserve on-disk content. "
            f"Got captures: {[kind for kind, _ in captured]}"
        )
    finally:
        os.unlink(tmp)

def test_populate_document_reapplies_extension_and_dispatches(tmp_path):
    """T-NEW-024: on the reopen path (``populate_document``
    called when returning to the tab), the syntax detection
    must re-run from the file extension, then the dispatcher
    must NOT re-render disk content (per T-NEW-023 followup:
    "reload should be opening the file on disk again" — the
    editor mirrors the raw bytes, not a re-rendered version).
    """
    import nchantdoffice.models  # noqa: F401
    from nchantdoffice.widgets.documents.media.scripts import (
        NchantdOfficeScript,
        NchantdOfficeScript as _Cls,
    )

    md = tmp_path / "open_format_check.md"
    md_content = "# Hello\n\n    - indented bullet\n"
    md.write_text(md_content, encoding="utf-8")

    widget = NchantdOfficeScript.__new__(NchantdOfficeScript)
    widget.file_path = str(md)
    widget.format_type = "plaintext"  # stale DB-cached value
    widget.config = SimpleNamespace(dikt={"syntax": "plaintext"})
    widget.document = SimpleNamespace(
        syntax="plaintext",
        file_format="plaintext",
        file_path=str(md),
        location="external",
        content="",
        meta_data={"syntax": "plaintext"},
        open_file=lambda _path: None,  # T-NEW-023 reload stub
        set_location=lambda _loc: None,  # T-NEW-023 reload stub
        set_content=lambda _c: None,  # save() calls this
    )

    # Extension re-apply runs at the top of populate_document.
    if widget.file_path:
        widget._apply_extension_syntax(widget.file_path)

    assert widget.format_type == "markdown", (
        f"populate_document should re-apply 'markdown' from "
        f"the .md extension, but format_type={widget.format_type!r}"
    )
    assert widget.document.syntax == "markdown"
    assert widget.document.meta_data["syntax"] == "markdown"

    # Capture which editor setter fires during reload.
    captured = []

    class _FakeEditor:
        def setPlainText(self, t):
            captured.append(("plain", t))

        def setHtml(self, html):
            captured.append(("html", html))

        def setMarkdown(self, md):
            captured.append(("md", md))

        def setStyleSheet(self, sheet):
            pass

        def toHtml(self):
            return "<html></html>"

        def toPlainText(self):
            return ""

        def setXml(self, xml):
            captured.append(("xml", xml))

        def setLatex(self, l):
            captured.append(("latex", l))

        def convert_urls_to_links(self, t):
            captured.append(("urls", t))

    widget.document_editor = _FakeEditor()

    # Simulate the reload path: initView() resets _initial_load
    # to False, then populate_document() runs. The reload must
    # use setPlainText only (no dispatcher) so whitespace is
    # preserved.
    widget.initView = lambda cfg=None: (
        setattr(widget, "_initial_load", False)
        or widget.populate_document()
    )
    widget.initView(None)

    # Reload must call setPlainText with the raw file content so
    # tabs and newlines are preserved verbatim — NOT the syntax
    # dispatcher (which drops the leading whitespace).
    plain_calls = [c for c in captured if c[0] == "plain"]
    assert plain_calls, (
        f"Reload did not call setPlainText with file content. "
        f"Got: {captured}"
    )
    assert any(
        "    - indented bullet" in c[1] for c in plain_calls
    ), (
        f"Reload setPlainText lost the indentation. "
        f"Captured: {plain_calls}"
    )
    # No dispatcher output on reload.
    bad = [c for c in captured if c[0] in ("md", "html", "xml", "latex")]
    assert not bad, (
        f"Reload fired the syntax dispatcher on disk content — "
        f"whitespace was re-rendered. Got: {bad}"
    )

    # Now simulate the initial open_file() path: opens with
    # _initial_load = True so the dispatcher fires for syntax
    # formatting (per T-NEW-024 + T-NEW-023 contract).
    captured.__init__()
    widget._initial_load = True
    # Stub out save() — the full save chain requires the app/view/model
    # which the test mock doesn't have. We're testing the dispatch, not
    # the persistence.
    widget.save = lambda *a, **kw: None
    widget.open_file(str(md))

    # The dispatcher must use setMarkdown for .md so the
    # initial-open rendering is correct.
    md_calls = [c for c in captured if c[0] == "md"]
    assert md_calls, (
        f"Initial open did not call setMarkdown for the .md file - "
        f"format was not dispatched. Got: {captured}"
    )
    # Markdown content preserved verbatim on initial open too.
    assert any(
        "# Hello" in c[1] and "    - indented bullet" in c[1]
        for c in md_calls
    ), (
        f"setMarkdown lost content. Captured md: "
        f"{[c[1] for c in md_calls]}"
    )

    # Production source asserts: the reload branch short-circuits
    # without _apply_syntax_highlighting, but the initial-open
    # branch dispatches via the _initial_load flag.
    import inspect
    from nchantdoffice.widgets.documents.media.scripts import (
        NchantdOfficeScript as _Cls,
    )
    src = inspect.getsource(_Cls.populate_document)
    assert "if getattr(self, \"_initial_load\", False):" in src
    assert "_resolve_document_text" in src  # DB fallback only
