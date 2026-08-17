"""T-NEW-138 regression: journal editor always-scrolls to bottom
on init, and populate_document goes through the standard parse()
contract.

**T-NEW-138 markers:**
- ``journal.py:132`` -- ``# TODO always scroll to bottom of document``
  in the outer ``NchantdOfficeJournalEditor.initView``. Today
  the editor stays scrolled to the top after open, so users see
  the first entry instead of the latest one.
- ``journal.py:422`` -- ``# TODO refactor to use the standard
  populate methods``. Today ``populate_document`` is a no-op stub
  (``def populate_document(self):``). The journal has a
  ``parse(content)`` method that builds the ``self.entries``
  dict from the full text; ``populate_document`` should call
  it with the loaded content so the entries dict is populated
  by the standard pipeline rather than via the bespoke
  ``_parse_entry`` chain.

The fix:
1. ``initView`` calls ``self.scroll_to_bottom()`` after the
   editor is added to the layout. The standard
   ``populate_document`` helper ends with
   ``scroll_to_bottom()`` -- the journal override skips it.
2. ``populate_document(self)`` calls
   ``self.parse(self.get_content())`` so the entries dict is
   ready when the user opens the journal. The parse()
   method handles None / empty / dict / string content
   inputs defensively.

Test surface: ``tests/test_t_new_138_journal_scroll_and_populate.py``
(this file). Pins:
  - source-level: initView ends with scroll_to_bottom() call
  - source-level: populate_document delegates to parse()
  - behavioural: stub initView / populate_document on a
    NchantdOfficeJournalEditor and verify the call shape
    matches expectations.

Migration plan (no priority / low priority -- design decision
first): the scroll fix is a single ``self.scroll_to_bottom()``
call after ``populate_document`` -- no priority, safe to land
first. The populate_document refactor routes through parse();
this preserves the bespoke _parse_entry path (which is the
append-editor's per-entry parser, not the outer editor's
bulk-load parser).
"""
import inspect

# T-NEW-074 Task 9: keep Qt on the headless offscreen platform
# before any PySide6 import so the integration test does not
# need a real display.
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from nchantdoffice.widgets.documents.journal import (
    NchantdOfficeJournalEditor,
)


# ---------------------------------------------------------------------------
# Source-level pin: initView scrolls to bottom
# ---------------------------------------------------------------------------

def test_journal_init_view_calls_scroll_to_bottom():
    """T-NEW-138 (scroll half): ``NchantdOfficeJournalEditor
    .initView`` must call ``self.scroll_to_bottom()`` (or
    equivalent) after the editor widget is added to the layout.
    Without this, opening a long journal leaves the user looking
    at the first entry instead of the latest.
    """
    src = inspect.getsource(NchantdOfficeJournalEditor.initView)
    assert "scroll_to_bottom" in src, (
        "NchantdOfficeJournalEditor.initView must call "
        "scroll_to_bottom() (T-NEW-138). Source:\n" + src[:1500]
    )


# ---------------------------------------------------------------------------
# Source-level pin: populate_document delegates to parse()
# ---------------------------------------------------------------------------

def test_journal_populate_document_calls_parse():
    """T-NEW-138 (populate half): ``populate_document`` must
    delegate to ``self.parse(...)`` so the entries dict is
    populated by the standard pipeline rather than via a
    bespoke no-op. The current code is a no-op stub
    (``def populate_document(self): ...``).
    """
    src = inspect.getsource(NchantdOfficeJournalEditor.populate_document)
    assert "parse(" in src, (
        "NchantdOfficeJournalEditor.populate_document must "
        "call self.parse(...) so the entries dict is populated "
        "(T-NEW-138). Source:\n" + src[:600]
    )


# ---------------------------------------------------------------------------
# Behavioural pin: populate_document invokes the parse method
# ---------------------------------------------------------------------------

def test_journal_populate_document_invokes_parse():
    """T-NEW-138 (behavioural): ``populate_document`` invokes
    ``self.parse`` with the loaded content. The stub bypasses
    parse() entirely; the fix routes through it.

    We don't instantiate the full journal editor (Qt singleton
    restrictions in the sasquatch test env). Instead we mock
    out the parts we don't need and assert the call shape.
    """
    editor = NchantdOfficeJournalEditor.__new__(
        NchantdOfficeJournalEditor
    )
    called = []

    def fake_parse(content):
        called.append(content)
        return {"2026-08-16 12:00:00": "test entry"}

    def fake_get_content():
        return "--|2026-08-16 12:00:00|--\ntest entry\n"

    editor.parse = fake_parse
    editor.get_content = fake_get_content

    editor.populate_document()

    assert called, (
        "populate_document must invoke self.parse (T-NEW-138)"
    )
    assert "--|2026-08-16 12:00:00|--" in called[0], (
        f"populate_document must pass the loaded content "
        f"(from get_content) to self.parse; got {called[0]!r}"
    )


# ---------------------------------------------------------------------------
# Behavioural pin: populate_document populates self.entries
# ---------------------------------------------------------------------------

def test_journal_populate_document_populates_entries():
    """T-NEW-138 (integration of the two halves):
    ``populate_document`` should populate ``self.entries``
    from the parse() result so the date-navigation widgets
    can read it.
    """
    editor = NchantdOfficeJournalEditor.__new__(
        NchantdOfficeJournalEditor
    )
    editor.entries = {}

    def fake_get_content():
        return (
            "old prefix\n"
            "--|2026-08-15 09:00:00|--\n"
            "first entry text\n"
            "--|2026-08-16 10:00:00|--\n"
            "second entry text\n"
        )

    editor.get_content = fake_get_content
    editor.populate_document()

    assert "2026-08-15 09:00:00" in editor.entries
    assert "2026-08-16 10:00:00" in editor.entries
    # Verify the entry text is the block following the marker,
    # not the marker itself.
    assert "first entry text" in editor.entries["2026-08-15 09:00:00"]
    assert "second entry text" in editor.entries["2026-08-16 10:00:00"]