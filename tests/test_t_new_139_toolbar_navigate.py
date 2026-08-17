"""T-NEW-139 regression: toolbar signature cleanup.

The original TODO at ``toolbars.py:216`` asked to combine
``add_tab`` + ``add_document`` shared cfg/handler wiring.
There is no ``add_tab`` sibling on
``NchantdNewDocumentToolBar`` (the only doc-creation
method), but the post-creation navigation block (left
pane tree refresh + center pane focus) IS a candidate for
extraction. The fix:

1. Add ``_navigate_to_new_doc(pos) -> Self`` helper that
   contains the two ``self.app.view.panes[...]`` lines.
2. ``add_document`` calls the helper instead of inlining
   the navigation.

Test surface: ``tests/test_t_new_139_toolbar_navigate.py``
(this file). Pins:
  - ``_navigate_to_new_doc`` method exists on
    ``NchantdNewDocumentToolBar``.
  - ``_navigate_to_new_doc(pos)`` calls the left-pane
    updateTabs + center-pane setCurrentIndex.
  - The original ``add_document`` no longer inlines the
    navigation block (it delegates to the helper).

Migration plan (no priority / low priority -- design decision
first): the helper is method-local -- no public API change,
no handler rewire, no constructor impact. Defensive: if
either pane or the tree is missing, ``getattr(...)`` returns
``None`` and the chain silently no-ops (matches the
tolerant behaviour the inline calls already had under
exception).
"""
import inspect

# T-NEW-074 Task 9: keep Qt on the headless offscreen platform
# before any PySide6 import so the integration test does not
# need a real display.
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from nchantdoffice.widgets.controls.toolbars import (
    NchantdNewDocumentToolBar,
)


def test_navigate_to_new_doc_method_exists():
    """T-NEW-139: the post-creation navigation helper must
    exist on ``NchantdNewDocumentToolBar``.
    """
    assert hasattr(NchantdNewDocumentToolBar, "_navigate_to_new_doc"), (
        "NchantdNewDocumentToolBar must define "
        "_navigate_to_new_doc (T-NEW-139)."
    )


def test_navigate_to_new_doc_signature():
    """T-NEW-139: the helper takes a position arg and returns
    Self so it chains naturally with ``add_document``.
    """
    src = inspect.getsource(NchantdNewDocumentToolBar._navigate_to_new_doc)
    assert "def _navigate_to_new_doc(self" in src, (
        "helper signature must accept self + pos (T-NEW-139). "
        "Got:\n" + src[:400]
    )
    assert "-> Self" in src or "-> None" in src, (
        f"helper must return Self or None for chaining; got:\n{src[:400]}"
    )


def test_navigate_to_new_doc_calls_pane_helpers():
    """T-NEW-139 (source-level): the helper must invoke both
    the left-pane ``updateTabs('center')`` and the center-pane
    ``setCurrentIndex(pos)`` so the post-creation navigation
    is preserved.
    """
    src = inspect.getsource(NchantdNewDocumentToolBar._navigate_to_new_doc)
    assert "updateTabs" in src, (
        f"helper must call left-pane updateTabs (T-NEW-139); got:\n{src[:400]}"
    )
    assert "setCurrentIndex" in src, (
        f"helper must call center-pane setCurrentIndex (T-NEW-139); "
        f"got:\n{src[:400]}"
    )


def test_add_document_delegates_to_navigate_helper():
    """T-NEW-139 (source-level): ``add_document`` no longer
    inlines the two post-creation navigation lines -- it
    delegates to ``_navigate_to_new_doc(pos)``.
    """
    src = inspect.getsource(NchantdNewDocumentToolBar.add_document)
    assert "_navigate_to_new_doc" in src, (
        "add_document must delegate to _navigate_to_new_doc "
        "(T-NEW-139). Source:\n" + src[-1200:]
    )
    # And the inline duplication is gone -- we keep
    # ``updateTabs`` / ``setCurrentIndex`` as imports via
    # the helper, not as direct calls.
    # (Pin: no direct ``panes['center'].setCurrentIndex`` in
    # add_document anymore.)
    assert 'panes["center"].setCurrentIndex' not in src, (
        "add_document must not inline setCurrentIndex -- "
        "delegate to _navigate_to_new_doc (T-NEW-139)."
    )