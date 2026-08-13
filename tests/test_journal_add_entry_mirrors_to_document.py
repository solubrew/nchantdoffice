"""T-NEW-079 — Journal add_entry must mirror to document.pages.

The full-text save path is ``save_app()`` which calls
``self.document.save(self.file_path)`` then
``store_document(self.document, True)`` to persist the Pyffice
document. The document's ``pages`` dict is what gets serialized
into ``app_media_content.content_enc64_txt``.

The inner ``NchantdOfficeJournalAppendEditor.add_entry`` was
writing to ``self.parent.pages`` only (the editor's in-memory
alias). The editor's pages dict was the same reference as the
document's pages dict at initModel time, but after the first
Pyffice save-and-load cycle the two diverged -- the editor
alias was not refreshed. The user-visible bug::

  Decoded content_enc64_txt payload:
    {
      "content": {"text": "--|2026-08-13 14:06:28|--\\ntest", "file_path": ""},
      "pages": {"0": {"entries": {}}}
    }

  The text is persisted, but the entries dict is empty.

The fix writes to BOTH the editor alias AND the document's
pages dict so the entries land in the persisted payload.

This test file pins the contract: add_entry() must land the
entry on BOTH the editor alias AND the document.
"""

from types import SimpleNamespace

from nchantdoffice.widgets.documents.journal import NchantdOfficeJournalAppendEditor


def _make_append_editor():
    """Build a minimal append editor + parent + document mock."""
    editor = NchantdOfficeJournalAppendEditor.__new__(NchantdOfficeJournalAppendEditor)
    editor.new_entry = True
    editor.app = SimpleNamespace(
        model=SimpleNamespace(
            get_current_node=lambda: SimpleNamespace(nid="node-1"),
            get_current_tab=lambda: SimpleNamespace(tid="tab-1"),
        )
    )

    # The Pyffice document's pages dict (the persisted one).
    doc_pages = {"0": {}}
    parent_doc = SimpleNamespace(pages=doc_pages)

    # The editor's parent (the outer JournalEditor) with its own
    # pages alias. In production both share the same dict object
    # but the contract is that add_entry writes to BOTH.
    parent = SimpleNamespace(
        document=parent_doc,
        pages=doc_pages,
        app=editor.app,
    )
    editor.parent = parent
    return editor, parent, parent_doc


def test_add_entry_populates_parent_pages():
    """Smoke test: the legacy behavior -- add_entry writes to
    self.parent.pages -- still works.
    """
    editor, parent, _ = _make_append_editor()
    editor.add_entry("legacy path")
    assert "entries" in parent.pages["0"]
    assert len(parent.pages["0"]["entries"]) == 1


def test_add_entry_populates_document_pages():
    """The new contract: add_entry must also write to
    self.parent.document.pages so the entry lands in the
    persisted payload via save_app().
    """
    editor, _, parent_doc = _make_append_editor()
    editor.add_entry("persisted entry")
    assert "entries" in parent_doc.pages["0"], (
        "add_entry must write to self.parent.document.pages so "
        "save_app() can persist the entry via content_enc64_txt. "
        "Without this mirror the entry is in memory only and "
        "lost on next reopen."
    )
    assert len(parent_doc.pages["0"]["entries"]) == 1


def test_add_entry_writes_to_both_parent_and_document():
    """The entry timestamp must appear in both dicts (use the
    same key so a future reader can find the entry in either
    place).
    """
    editor, parent, parent_doc = _make_append_editor()
    editor.add_entry("the new entry")
    parent_keys = set(parent.pages["0"]["entries"].keys())
    doc_keys = set(parent_doc.pages["0"]["entries"].keys())
    assert parent_keys == doc_keys, (
        f"Entry timestamp keys must match between parent and "
        f"document. parent={parent_keys}, document={doc_keys}"
    )


def test_add_entry_creates_page_0_if_missing():
    """Defensive: when the document's pages dict was empty
    (fresh user, no journal opened yet), add_entry must
    create the page-0 entries dict on the fly.
    """
    editor = NchantdOfficeJournalAppendEditor.__new__(NchantdOfficeJournalAppendEditor)
    editor.new_entry = True
    editor.app = SimpleNamespace(
        model=SimpleNamespace(
            get_current_node=lambda: SimpleNamespace(nid="node-1"),
            get_current_tab=lambda: SimpleNamespace(tid="tab-1"),
        )
    )
    parent_doc = SimpleNamespace(pages={})  # EMPTY pages
    parent = SimpleNamespace(
        document=parent_doc,
        pages={},
        app=editor.app,
    )
    editor.parent = parent

    # Must NOT raise
    editor.add_entry("first entry ever")

    assert "0" in parent_doc.pages
    assert "entries" in parent_doc.pages["0"]
    assert len(parent_doc.pages["0"]["entries"]) == 1


def test_add_entry_handles_missing_parent_document():
    """Defensive: when self.parent.document is None (the editor
    was constructed via __new__ without setting up a document),
    add_entry must not crash -- it just writes to the parent
    alias and skips the document mirror.
    """
    editor = NchantdOfficeJournalAppendEditor.__new__(NchantdOfficeJournalAppendEditor)
    editor.new_entry = True
    editor.app = SimpleNamespace(
        model=SimpleNamespace(
            get_current_node=lambda: SimpleNamespace(nid="node-1"),
            get_current_tab=lambda: SimpleNamespace(tid="tab-1"),
        )
    )
    parent = SimpleNamespace(
        document=None,
        pages={"0": {}},
        app=editor.app,
    )
    editor.parent = parent

    # Must NOT raise
    editor.add_entry("orphaned entry")

    assert len(parent.pages["0"]["entries"]) == 1
