"""JournalEditor save regression test -- current contract.

The journal save flow has two contracts the tests pin:

1. ``NchantdOfficeJournalEditor.save()`` calls ``self.save_app()``
   (the app_media path) and that's it. Per user directive
   (commits 9e74486 / cb6ebb9) ``super().save()`` is NOT called on
   the journal path -- it would persist to ``doc_media_content``,
   the wrong table for an app_media document. The always-save
   scaffolding (``self._parse_entry()`` + ``self.parent.save()``)
   is left in the source but commented out (see T-NEW-079 step 3
   in TODOs.md).

2. ``NchantdOfficeJournalAppendEditor.add_entry()`` writes to BOTH
   ``self.parent.pages`` (editor alias) AND
   ``self.parent.document.pages`` (the persisted object). The
   second write is what makes the entry land in
   ``app_media_content.content_enc64_txt`` via ``save_app()``.

See tests/test_journal_add_entry_mirrors_to_document.py for the
exhaustive 5-test coverage of the add_entry contract. This file
focuses on the outer save() flow + the inner save() chain.
"""

import inspect
from types import SimpleNamespace

import pytest

from nchantdoffice.widgets.documents.journal import (
    NchantdOfficeJournalAppendEditor,
    NchantdOfficeJournalEditor,
)


# ---------------------------------------------------------------------------
# Outer save() -- source-level contract
# ---------------------------------------------------------------------------


def test_journal_outer_save_calls_save_app():
    """The outer save() must call ``self.save_app()`` (the app_media
    path) and NOT ``super().save()`` in the executable body.

    The save() docstring may mention super().save() historically --
    that's fine, it's a comment. The negative contract checks the
    function body only (the lines after the closing triple-quote
    of the docstring).
    """
    src = inspect.getsource(NchantdOfficeJournalEditor.save)
    # Split on the docstring close so we check the body only.
    body_start = src.find('"""', src.find('"""') + 3) + 3
    body = src[body_start:]
    assert "self.save_app()" in body, (
        "outer save() must call self.save_app() (T-NEW-079: app_media path)"
    )
    # NEGATIVE contract: super().save() must NOT be called in the
    # save() body. The user removed it (commits 9e74486 / cb6ebb9)
    # because it put erroneous data into doc_media_content.
    assert "super().save()" not in body, (
        "save() must NOT call super().save() on the journal path -- "
        "the journal is app_media, not doc_media (9e74486 / cb6ebb9)."
    )


def test_journal_outer_save_persists_via_save_app():
    """The outer save() must call ``save_app()`` (which is the
    actual persistence path). The legacy ``super().save()`` /
    ``parent.save()`` blocks are intentionally commented out --
    parsing still needs full implementation per the user's 174cfd86
    restore directive.
    """
    # Mock the editor's save() path: stub save_app so we can observe
    # the call. The test verifies that save() reaches save_app, not
    # that save_app itself persists correctly (that's a separate
    # contract tested by test_browser_db_roundtrip et al).
    editor = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor)
    editor.entries = {}

    save_app_calls = []
    save_app_mock = lambda *a, **kw: save_app_calls.append("save_app-called") or editor
    editor.save_app = save_app_mock

    # Save flow needs a document and a get_content() result.
    editor.document = SimpleNamespace(content=None, set_content=lambda c: None)
    editor.get_content = lambda: "test-content"
    editor.new_document = lambda: None

    # The editor save() reads self.app.view.panes["left"]... when
    # the app is None or the panes lookup raises the inner save_app
    # call still completes (save_app itself does the path lookup).
    # We avoid the app lookup entirely by mocking save_app.
    try:
        # Pass when save_app can run without the app/panes lookup.
        editor.save()
    except Exception:
        # The save_app mock short-circuits before the app lookup
        # happens in some paths -- if it raised in save() before
        # reaching save_app, we'd see no calls. That's a real bug.
        pass

    assert save_app_calls, (
        "save() must reach self.save_app() (the canonical app_media "
        "persistence path). If this is empty, save() short-circuited "
        "before the save_app call -- check the early-return guards."
    )


def test_journal_save_app_exception_propagates():
    """Per user directive (commit cb6ebb9 the user removed the
    try/except wrappers around save_app() and _parse_entry() in the
    journal save flow). A save_app() failure now propagates to the
    caller (typically the Qt focus-out handler) -- the journal is a
    background save, the user sees the error in logs, and the Qt
    event loop logs the unhandled exception rather than silently
    dropping the user's text.

    This test pins the new contract. Future agents who try to
    "harden" the save flow by re-adding try/except around
    save_app() will fail this test.
    """
    import pytest
    editor = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor)
    editor.entries = {}

    def bad_save_app(*a, **kw):
        raise RuntimeError("db unavailable")

    editor.save_app = bad_save_app
    editor.document = SimpleNamespace(content=None, set_content=lambda c: None)
    editor.get_content = lambda: "x"
    editor.new_document = lambda: None

    with pytest.raises(RuntimeError, match="db unavailable"):
        editor.save()


def test_journal_outer_save_no_parent_is_safe():
    """If self.parent is None, save() must not crash."""
    editor = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor)
    editor.entries = {}
    editor.parent = None
    editor.document = SimpleNamespace(content=None, set_content=lambda c: None)
    editor.get_content = lambda: "x"
    editor.save_app = lambda *a, **kw: editor
    editor.new_document = lambda: None

    # Must NOT raise
    result = editor.save()


# ---------------------------------------------------------------------------
# Inner save() -- append editor chain
# ---------------------------------------------------------------------------


def test_journal_append_save_calls_super_and_parent():
    """The inner ``NchantdOfficeJournalAppendEditor.save`` calls
    ``super().save()`` then ``self._parse_entry()`` then
    ``self.parent.save()``. This is the always-save contract --
    the parent.save() call drives the outer JournalEditor's
    save() (which then runs save_app()).

    NOTE: this is the always-save flow that the user has NOT yet
    wired into the outer JournalEditor.save() (T-NEW-079 step 3
    in TODOs.md). It currently runs from focusOutEvent via the
    inner editor's ``save()`` method directly.
    """
    src = inspect.getsource(NchantdOfficeJournalAppendEditor.save)
    assert "super().save()" in src, (
        "append save() must call super().save() -- it persists "
        "the QTextEditor text state via the parent pipeline."
    )
    assert "self._parse_entry()" in src, (
        "append save() must call _parse_entry() so the new entry "
        "is pushed into self.parent.pages[0]['entries']."
    )
    assert "self.parent.save()" in src, (
        "append save() must call parent.save() to drive the outer "
        "JournalEditor's save() (which runs save_app())."
    )


def test_journal_initView_creates_append_editor():
    """``NchantdOfficeJournalEditor.initView`` must create the append editor."""
    src = inspect.getsource(NchantdOfficeJournalEditor.initView)
    assert "NchantdOfficeJournalAppendEditor" in src