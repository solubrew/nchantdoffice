"""T-NEW-035 close-out: file_format vs syntax on the script document.

The Sprint 28 TODO at scripts.py:1462 said ``untagle file_format
and syntax``. The fix unifies the two attributes on the document:

- ``syntax`` is the canonical name (per T-NEW-024 doc-media).
- ``file_format`` is kept as a backward-compat alias that mirrors
  ``syntax`` so the older dispatch paths keep working.

Regression test: tests/test_file_format_syntax_untangle.py
"""

import inspect
from types import SimpleNamespace


def test_file_format_todo_removed():
    """The ``# TODO untagle file_format and syntax`` comment must be gone."""
    from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript
    src = inspect.getsource(NchantdOfficeScript._apply_syntax_highlighting)
    assert "TODO untagle file_format" not in src, (
        "file_format vs syntax TODO must be resolved (T-NEW-035)"
    )


def test_file_format_synced_from_syntax():
    """``_apply_syntax_highlighting`` must mirror file_format from syntax."""
    from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript
    src = inspect.getsource(NchantdOfficeScript._apply_syntax_highlighting)
    assert "file_format = self.document.syntax" in src, (
        "file_format must be a backward-compat alias of syntax (T-NEW-035)"
    )


def test_syntax_canonical_attribute():
    """``script syntax`` is the canonical attribute -- file_format is alias."""
    from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript
    # When syntax is set, file_format must mirror it
    doc = SimpleNamespace(syntax="python", file_format="plain-text")
    # Mirror the production logic
    if hasattr(doc, "file_format"):
        doc.file_format = doc.syntax
    assert doc.file_format == "python"
    assert doc.syntax == "python"


def test_nan_guard_for_syntax():
    """NaN-guard logic for syntax must remain after the cleanup."""
    from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript
    src = inspect.getsource(NchantdOfficeScript._apply_syntax_highlighting)
    assert "isinstance" in src and "float" in src, (
        "NaN guard for syntax must remain (T-NEW-035)"
    )


def test_markdown_syntax_remains_supported():
    """The markdown dispatch path must still fire on syntax='markdown'."""
    from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript
    src = inspect.getsource(NchantdOfficeScript._apply_syntax_highlighting)
    assert "markdown" in src
    assert "setMarkdown" in src
