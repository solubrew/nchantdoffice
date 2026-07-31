"""T-NEW-036 -- Journal restore on tab change regression tests.

The Journal document does not restore its content/state when
the user switches tabs and comes back. The inline TODO at
``journal.py:75`` says: "need to fix the restore
functionality so that Journal restores properly on each tab
change".

Root cause: ``initModel()`` fetches the journal document and
sets ``self.full_text`` once at first ``initWidget``. On
subsequent tab-focus changes, ``initModel`` is never
re-called, so the editor shows stale content.

Fix: add ``refresh_content`` to ``NchantdOfficeJournalEditor``
that re-fetches the journal text from the model and updates
the editor. Wire it from ``NchantdOfficeTabSet.on_tab_focus``
when the focused tab is a journal.
"""

import sys
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication
_QAPP = QApplication.instance() or QApplication(sys.argv)

import nchantdoffice.widgets.documents.journal  # noqa: F401
from nchantdoffice.widgets.documents.journal import NchantdOfficeJournalEditor


def _make_journal():
    """Build a NchantdOfficeJournalEditor via __new__ + inject
    mocks for the model + editor (Sprint 28-29 pattern)."""
    journal = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor)
    journal.full_text = ""
    journal.editor = SimpleNamespace(
        setPlainText=lambda text: setattr(journal, "_captured_text", text),
        toPlainText=lambda: getattr(journal, "_captured_text", ""),
    )
    journal._captured_text = ""
    journal.document = SimpleNamespace(
        pages={},
        text=SimpleNamespace(
            to_dict=lambda: {"unit": {"value": "restored content"}}
        ),
    )
    # The app.model.get_view_journal returns a document dict
    journal.app = SimpleNamespace(
        model=SimpleNamespace(
            get_current_node=lambda: SimpleNamespace(nid="node-1", tid="tab-1"),
            get_current_tab=lambda: SimpleNamespace(tid="tab-1"),
            codex=SimpleNamespace(
                init_script=lambda cfg: SimpleNamespace(
                    load_document=lambda: None,
                    pages={},
                    text=SimpleNamespace(
                        to_dict=lambda: {"unit": {"value": "restored content"}}
                    ),
                )
            ),
            get_view_journal=lambda cfg: {"content": "restored content"},
        )
    )
    journal.config = SimpleNamespace(dikt={"scope": "TODAY"})
    return journal


# ---------------------------------------------------------------------------
# refresh_content method
# ---------------------------------------------------------------------------


def test_refresh_content_re_fetches_journal_text():
    """``refresh_content`` must re-fetch the journal document
    from the model and update ``self.full_text`` so the
    editor can display the current content.
    """
    journal = _make_journal()
    journal.full_text = "old stale text"
    journal.refresh_content()
    assert journal.full_text == "restored content", (
        f"refresh_content must re-fetch from model. "
        f"Got: {journal.full_text!r}"
    )


def test_refresh_content_updates_editor_text():
    """``refresh_content`` must push the fetched text into the
    editor widget via ``setPlainText`` so the user sees it.
    """
    journal = _make_journal()
    journal._captured_text = "old editor text"
    journal.refresh_content()
    assert journal._captured_text == "restored content", (
        f"Editor text must be updated. Got: {journal._captured_text!r}"
    )


def test_refresh_content_returns_self():
    """Mirrors the Sprint 23 return-self pattern."""
    journal = _make_journal()
    result = journal.refresh_content()
    assert result is journal


def test_refresh_content_swallows_exception():
    """Defensive: if the model is missing or raises, the
    handler must log + swallow rather than crashing the UI.
    """
    journal = _make_journal()
    # Make the model raise
    journal.app.model.get_view_journal = lambda cfg: (_ for _ in ()).throw(RuntimeError("simulated"))
    # Must NOT raise
    result = journal.refresh_content()
    assert result is journal


def test_refresh_content_handles_missing_app():
    """Defensive: when ``self.app`` is missing (e.g. during
    teardown), the handler is a no-op (returns self).
    """
    journal = _make_journal()
    journal.app = None
    result = journal.refresh_content()
    assert result is journal


def test_refresh_content_handles_missing_editor():
    """Defensive: when ``self.editor`` is None (not yet
    initialized), ``refresh_content`` should still update
    ``self.full_text`` but not crash on the editor update.
    """
    journal = _make_journal()
    journal.editor = None
    journal.refresh_content()
    assert journal.full_text == "restored content"


# ---------------------------------------------------------------------------
# on_tab_focus wiring -- source-level test
# ---------------------------------------------------------------------------


def test_on_tab_focus_calls_refresh_for_journal_documents():
    """T-NEW-036 step 3: ``NchantdOfficeTabSet.on_tab_focus``
    must call ``refresh_content`` on the focused tab's widget
    when the widget is a journal document. Source-level test
    -- the off-screen path can't drive real tab focus.
    """
    from pathlib import Path
    widgets_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/widgets.py"
    ).read_text()
    # The on_tab_focus method must reference refresh_content
    # (either directly on the widget or via a hasattr check).
    assert "refresh_content" in widgets_py, (
        "on_tab_focus must call refresh_content on the focused "
        "tab's widget when it's a journal (T-NEW-036)"
    )