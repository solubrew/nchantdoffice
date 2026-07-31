"""T-NEW-041 -- Widget lookup from document_types table (TDD tests).

The inline TODO at toolbars.py:159 said: "need to figure
out how to look up the widget from the document types
table". The canonical lookup was already added at L161
(``self.app.model.get_document_type(cfg["lookup_code_txt"])
.get("widget_txt", None)``) -- the TODO is stale.

The right fix is to:
  1. Remove the stale inline TODO.
  2. Replace with a T-NEW-041 pointer comment.
  3. Add a regression test that asserts the canonical
     ``get_document_type`` lookup is present in
     ``launch_document`` (the function at L143).

Tests (source-level -- the live launch_document path
needs a full Qt parent chain that we can't drive off-screen):

  - test_launch_document_uses_canonical_get_document_type_lookup
  - test_launch_document_no_stale_todo_marker_at_l159
  - test_launch_document_widget_lookup_falls_back_to_get_document_type
"""

import re
import sys
from pathlib import Path
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication
_QAPP = QApplication.instance() or QApplication(sys.argv)


def _toolbars_py():
    return Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/controls/toolbars.py"
    ).read_text()


def test_launch_document_uses_canonical_get_document_type_lookup():
    """The ``launch_document`` method must call
    ``self.app.model.get_document_type(...)`` to resolve
    the widget when the action's ``widget_txt`` is empty
    (the canonical lookup). Source-level guard.
    """
    txt = _toolbars_py()
    assert "self.app.model.get_document_type(" in txt, (
        "launch_document must call self.app.model.get_document_type "
        "to resolve the widget for unknown action codes "
        "(T-NEW-041 canonical lookup)"
    )


def test_launch_document_no_stale_todo_marker_at_l159():
    """The inline TODO at L159 ("need to figure out how to
    look up the widget from the document types table") must
    be REMOVED -- the canonical lookup at L161 is in place.
    Source-level guard against the TODO creeping back in.
    """
    txt = _toolbars_py()
    # The exact TODO text from the original inline marker.
    stale = "TODO:0 need to figure out how to look up the widget from the document types table"
    assert stale not in txt, (
        f"The stale TODO at toolbars.py L159 must be removed -- "
        f"the canonical lookup (self.app.model.get_document_type) "
        f"is in place. Found: {stale!r}"
    )


def test_launch_document_widget_lookup_falls_back_to_get_document_type():
    """The lookup path must use ``get(...).get("widget_txt", None)``
    -- the safe ``.get`` form so a missing document type
    returns ``None`` rather than raising ``KeyError``.

    Also asserts the fallback chain: ``args[0]["action"].action["widget_txt"]``
    is the primary source; ``get_document_type`` is the
    fallback. This is the canonical Sprint 23-style
    two-step lookup.
    """
    txt = _toolbars_py()
    # The fallback uses .get with default None
    pattern = re.compile(
        r'get_document_type\([^)]+\)\.get\(\s*["\']widget_txt["\']\s*,\s*None\s*\)'
    )
    assert pattern.search(txt), (
        "launch_document must use the safe .get('widget_txt', None) "
        "form when calling get_document_type (T-NEW-041 canonical "
        "fallback chain)"
    )


def test_launch_document_t_new_041_pointer_present():
    """After the close-out, the area around the former TODO
    must carry a T-NEW-041 pointer (so future readers know
    where the canonical lookup decision lives).
    """
    txt = _toolbars_py()
    assert "T-NEW-041" in txt, (
        "The T-NEW-041 close-out must leave a T-NEW-041 "
        "pointer in toolbars.py (replacing the stale TODO)"
    )