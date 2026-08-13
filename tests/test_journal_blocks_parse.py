"""T-NEW-XXX -- Journal full-text + datetime-blocks serialization.

The journal save pipeline has two consumers with different needs:

1. ``NchantdOfficeJournalEditor`` (the outer editor) shows the FULL
   content of the journal entry the user is currently reading or
   writing. It needs the uncompressed, unparsed text.

2. Other, date-navigation widgets (e.g. an upcoming "Journal
   Overview" widget that lists entries by date) only need SPECIFIC
   blocks dated to a particular marker. They cannot ask the user
   to scroll through the full text.

The serialized payload written to ``app_media_content.content_enc64_txt``
must therefore carry BOTH:

    {
      "full":   "<the full text>",
      "blocks": {
        "2026-08-13 12:00:00": "<text of that block>",
        "2026-08-13 14:30:00": "<text of that block>",
        ...
      }
    }

The block markers in the text are the
``--|YYYY-MM-DD HH:MM:SS|--`` shape already documented in the
NchantdOfficeJournalEditor.parse() docstring (journal.py:275).

This test file pins the contract that:
- NchantdOfficeJournalEditor.parse(content) returns a dict of
  datetime -> block text entries split on the marker.
- The save() flow uses that parsed dict to construct the
  serialized payload before the text reaches ``app_media_content``.
- The payload is the dict shape {full, blocks}, not just the full
  text alone.
- A malformed marker (no closing --|) is tolerated (the rest of
  the text is the last block; no exception).
- An empty input parses to {"blocks": {}, "full": ""}.
"""

import inspect
from types import SimpleNamespace

import pytest


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

JOURNAL_SAMPLE = (
    "preamble text\n"
    "--|2026-08-13 10:00:00|--\n"
    "morning reflection\n"
    "another line\n"
    "--|2026-08-13 12:30:00|--\n"
    "lunch notes\n"
    "--|2026-08-13 18:15:00|--\n"
    "evening wrap\n"
)


def _make_editor():
    """Build a bare-minimum NchantdOfficeJournalEditor for unit tests."""
    from nchantdoffice.widgets.documents.journal import (
        NchantdOfficeJournalEditor,
    )
    editor = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor)
    editor.new_entry = False
    editor.parent = SimpleNamespace(save=lambda: None)
    editor.document = SimpleNamespace(content="", set_content=lambda c: None)
    editor.get_content = lambda: ""
    return editor


# ---------------------------------------------------------------------------
# parse() contract
# ---------------------------------------------------------------------------


def test_parse_splits_full_text_into_datetime_blocks():
    """parse() returns a dict keyed on the marker timestamps."""
    editor = _make_editor()
    result = editor.parse(JOURNAL_SAMPLE)

    assert isinstance(result, dict), (
        f"parse() must return a dict with full + blocks, got {type(result)}"
    )
    assert "full" in result and "blocks" in result, (
        f"parse() must return {{full, blocks}}, got keys: {list(result)}"
    )
    blocks = result["blocks"]
    assert isinstance(blocks, dict), (
        f"parse()['blocks'] must be a dict, got {type(blocks)}"
    )
    # Three markers in the sample
    assert "2026-08-13 10:00:00" in blocks
    assert "2026-08-13 12:30:00" in blocks
    assert "2026-08-13 18:15:00" in blocks
    assert "morning reflection" in blocks["2026-08-13 10:00:00"]
    assert "lunch notes" in blocks["2026-08-13 12:30:00"]
    assert "evening wrap" in blocks["2026-08-13 18:15:00"]


def test_parse_preserves_full_text_and_preamble():
    """parse() must also return the full text (including the markers)
    so the outer editor can re-display the same content on reopen.
    """
    editor = _make_editor()
    result = editor.parse(JOURNAL_SAMPLE)

    # Either returns a dict with "full" + "blocks" or a plain
    # dict-of-blocks. The full-must-be-preserved contract is that
    # we can reconstruct the source from the result.
    assert "full" in result, f"parse() must include 'full' key. Got: {list(result)}"
    assert result["full"] == JOURNAL_SAMPLE
    assert "blocks" in result, f"parse() must include 'blocks' key. Got: {list(result)}"
    assert isinstance(result["blocks"], dict) and len(result["blocks"]) == 3


def test_parse_returns_empty_blocks_for_empty_text():
    """Empty input parses to empty blocks; no marker found means no entries."""
    editor = _make_editor()
    result = editor.parse("")

    assert result["full"] == ""
    assert result["blocks"] == {}


def test_parse_returns_empty_blocks_for_text_without_markers():
    """Text with no markers parses to empty blocks; the full text is preserved."""
    editor = _make_editor()
    text = "Just a plain journal entry with no markers at all."
    result = editor.parse(text)

    assert result["full"] == text
    assert result["blocks"] == {}


def test_parse_tolerates_malformed_marker():
    """An opening marker with no matching close is tolerated; the rest
    of the text is treated as the last block (or skipped -- design
    choice). Must not raise.
    """
    editor = _make_editor()
    text = (
        "--|2026-08-13 10:00:00|--\n"
        "good block\n"
        "--|2026-08-13 11:00:00\n"  # missing closing --|
        "trailing without a close\n"
    )
    # Must not raise
    result = editor.parse(text)
    assert result["full"] == text


def test_parse_handles_block_at_start_of_text():
    """A marker at the very start of the text produces a block with no
    preceding preamble. The first block should still be keyed by the
    marker timestamp.
    """
    editor = _make_editor()
    text = "--|2026-08-13 09:00:00|--\nfirst block of the day\n"
    result = editor.parse(text)

    assert "2026-08-13 09:00:00" in result["blocks"]
    assert "first block of the day" in result["blocks"]["2026-08-13 09:00:00"]


# ---------------------------------------------------------------------------
# save() payload contract
# ---------------------------------------------------------------------------


def test_save_constructs_payload_with_full_and_blocks():
    """The save() flow must call parse() and pass the {full, blocks}
    dict to ``self.document.set_content()`` so the parent save_app
    pipeline writes the structured payload to ``content_enc64_txt``.
    """
    from nchantdoffice.widgets.documents.journal import (
        NchantdOfficeJournalEditor,
    )

    editor = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor)
    editor.new_entry = False
    editor.parent = SimpleNamespace(save=lambda: None)
    editor.get_content = lambda: JOURNAL_SAMPLE

    captured = {}

    def capture_set_content(content):
        captured["content"] = content

    editor.document = SimpleNamespace(content=None, set_content=capture_set_content)

    # Stub super().save() so we don't recurse.
    base = NchantdOfficeJournalEditor.__mro__[1]
    orig_save = base.save
    base.save = lambda *a, **kw: None
    try:
        editor.save()
    finally:
        base.save = orig_save

    assert "content" in captured, "save() must call document.set_content()"
    assert isinstance(captured["content"], dict), (
        f"save() must pass a dict-shaped payload to set_content, "
        f"got {type(captured['content'])}"
    )
    assert "full" in captured["content"]
    assert "blocks" in captured["content"]
    assert captured["content"]["full"] == JOURNAL_SAMPLE
    assert "2026-08-13 12:30:00" in captured["content"]["blocks"]



