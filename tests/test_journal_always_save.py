"""JournalEditor always-save regression test.

The New TODOs staging list had:
  'NchantdOfficeJournalEditor needs to have the always save
   functionality fixed as it has regressed during development'

The fix lives at the save() method on
``NchantdOfficeJournalEditor.save(self, path, format_, encrypt)``
(widgets/documents/journal.py:401). The journal editor saves on
focusOut AND on every text change (the "always save" rule).
On save, it must:

1. Call super().save() so the document content is persisted.
2. If new_entry is True, parse the entry and add it to the journal
   pages dict (via self._parse_entry).
3. Call self.parent.save() so the parent panel saves the doc too.

Regression test: tests/test_journal_always_save.py
"""

import inspect
from types import SimpleNamespace


def test_journal_outer_save_calls_parent():
    """The outer ``NchantdOfficeJournalEditor.save(path, format_, encrypt)``
    must call self.save_app() (the app_media path -- the journal is
    NOT a doc_media document), and self.parent.save().

    T-NEW-XXX + 9e74486: the prior contract required super().save()
    but the user removed it because it put erroneous data into the
    doc_media_content table. The journal is an app_media document,
    so the only correct save path is save_app() + parent.save()
    + the parse-scaffold always-save blocks.
    """
    from nchantdoffice.widgets.documents.journal import (
        NchantdOfficeJournalEditor,
    )
    src = inspect.getsource(NchantdOfficeJournalEditor.save)
    assert "self.save_app()" in src, (
        "outer save() must call self.save_app() (T-NEW-XXX: app_media path)"
    )
    assert "self.parent.save()" in src, (
        "outer save() must call parent.save() (T-NEW-XXX)"
    )


def test_journal_outer_save_persists_via_parent():
    """The outer save() must call parent.save() (and save_app -- the
    app_media path). The journal is an app_media document so
    super().save() is intentionally NOT called (it would put erroneous
    data into doc_media_content -- 9e74486).
    """
    from nchantdoffice.widgets.documents.journal import (
        NchantdOfficeJournalEditor,
    )

    editor = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor)

    calls = []

    class FakeParent:
        def save(self):
            calls.append("parent-saved")

    editor.parent = FakeParent()
    editor.new_entry = False
    editor.document = SimpleNamespace(content="", set_content=lambda c: None)
    editor.get_content = lambda: "test-content"

    editor.save()
    assert "parent-saved" in calls
    # Negative contract: super().save() must NOT be called on the
    # journal save path (it persists to doc_media_content, which is
    # the wrong table for a journal entry -- 9e74486).
    base = NchantdOfficeJournalEditor.__mro__[1]
    super_save_calls = []

    def fake_super_save(*args, **kwargs):
        super_save_calls.append("super-saved")

    orig_save = base.save
    base.save = fake_super_save
    try:
        editor.save()
    finally:
        base.save = orig_save
    assert super_save_calls == [], (
        "save() must NOT call super().save() on the journal path -- "
        "the journal is app_media, not doc_media (9e74486)"
    )


def test_journal_outer_save_with_new_entry_parses():
    """When new_entry is True, save() must call _parse_entry()."""
    from nchantdoffice.widgets.documents.journal import (
        NchantdOfficeJournalEditor,
    )

    editor = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor)
    editor.new_entry = True
    editor.parent = SimpleNamespace(save=lambda: None)
    editor.document = SimpleNamespace(content="", set_content=lambda c: None)
    editor.get_content = lambda: "x"

    parsed = []
    editor._parse_entry = lambda: parsed.append("parsed") or editor

    base = NchantdOfficeJournalEditor.__mro__[1]
    orig_save = base.save
    base.save = lambda *a, **kw: None
    try:
        editor.save()
    finally:
        base.save = orig_save

    assert "parsed" in parsed


def test_journal_outer_save_swallows_parent_save_exception():
    """If parent.save() raises, the journal save must not crash."""
    from nchantdoffice.widgets.documents.journal import (
        NchantdOfficeJournalEditor,
    )

    editor = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor)
    editor.new_entry = False
    editor.document = SimpleNamespace(content="", set_content=lambda c: None)
    editor.get_content = lambda: "x"

    class BadParent:
        def save(self):
            raise RuntimeError("parent gone")

    editor.parent = BadParent()

    base = NchantdOfficeJournalEditor.__mro__[1]
    orig_save = base.save
    base.save = lambda *a, **kw: None
    try:
        result = editor.save()
    finally:
        base.save = orig_save

    # Should not raise; returns self
    assert result is editor


def test_journal_outer_save_swallows_parse_entry_exception():
    """If _parse_entry raises, the journal save must not crash."""
    from nchantdoffice.widgets.documents.journal import (
        NchantdOfficeJournalEditor,
    )

    editor = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor)
    editor.new_entry = True
    editor.parent = SimpleNamespace(save=lambda: None)
    editor.document = SimpleNamespace(content="", set_content=lambda c: None)
    editor.get_content = lambda: "x"

    def bad_parse():
        raise RuntimeError("parse boom")

    editor._parse_entry = bad_parse

    base = NchantdOfficeJournalEditor.__mro__[1]
    orig_save = base.save
    base.save = lambda *a, **kw: None
    try:
        result = editor.save()
    finally:
        base.save = orig_save

    assert result is editor


def test_journal_outer_save_no_parent_is_safe():
    """If self.parent is None, save() must not crash."""
    from nchantdoffice.widgets.documents.journal import (
        NchantdOfficeJournalEditor,
    )

    editor = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor)
    editor.new_entry = False
    editor.parent = None
    editor.document = SimpleNamespace(content="", set_content=lambda c: None)
    editor.get_content = lambda: "x"

    base = NchantdOfficeJournalEditor.__mro__[1]
    orig_save = base.save
    base.save = lambda *a, **kw: None
    try:
        result = editor.save()
    finally:
        base.save = orig_save

    assert result is editor


def test_journal_append_save_calls_super():
    """The inner ``NchantdOfficeJournalAppendEditor.save`` must also call super()."""
    from nchantdoffice.widgets.documents.journal import (
        NchantdOfficeJournalAppendEditor,
    )
    src = inspect.getsource(NchantdOfficeJournalAppendEditor.save)
    assert "super().save()" in src


def test_journal_initView_creates_append_editor():
    """``NchantdOfficeJournalEditor.initView`` must create the append editor."""
    from nchantdoffice.widgets.documents.journal import (
        NchantdOfficeJournalEditor,
    )
    src = inspect.getsource(NchantdOfficeJournalEditor.initView)
    assert "NchantdOfficeJournalAppendEditor" in src
