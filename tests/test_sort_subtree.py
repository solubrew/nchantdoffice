"""T-NEW-133 regression test: node sort buttons actually sort the
**subtree** of the selected node, honouring ascending/descending,
and persisting to SQLite.

**Sort buttons silently do nothing useful**

The toolbar's ``sort_children_ascending`` / ``_descending``
buttons are wired to ``cmd_sort_children`` on the
node-edit pane (L274 of ``widgets/panes/documents.py``). The
handler is a 2-line stub:

    def cmd_sort_children(self, event=None, *args, **kwargs):
        node = self.get_node()
        node.sortChildren()
        return self

Three bugs:
1. The button's ``args`` ("ascending" / "descending") is
   ignored -- the handler always calls Qt's
   ``sortChildren(column, AscendingOrder)``.
2. ``sortChildren()`` sorts only the immediate children of
   the selected node. The user wants the entire *subtree*
   (descendants at every depth) sorted.
3. The Qt-side ``super().sortChildren(...)`` does not persist
   the new positions; the Python-side
   ``NchantdTreeNode.sortChildren(order=...)`` override does
   (it calls ``store.update_record(...)`` per child). Calling
   the bare Qt API skips persistence, so the next reload
   reverts the order.

The fix:
1. ``cmd_sort_children`` reads the direction from the
   first positional arg when present
   ("ascending" / "descending"), falls back to
   ``event`` or kwargs, then defaults to ascending.
2. Calls ``NchantdTreeNode.sortChildren(order=...)`` on the
   selected node so the immediate children are sorted AND
   persisted (per the override at
   ``nchantrs/widgets/items/nodes.py:512``).
3. Recurses into the subtree -- for each child of the
   selected node, calls the same logic so every descendant
   depth gets sorted with the same direction. Persistence
   cascades naturally because the override writes per child.

Affected sites:
- nchantdoffice/widgets/panes/documents.py: ``cmd_sort_children``
- nchantdoffice/models.py (optional): may add a
  ``sort_subtree(node, order)`` helper that the cmd calls.
- tests/test_sort_subtree.py: this test file.

Migration plan (no priority / low priority -- design decision
first): the buttons are already wired with ``args``. The
handler just needs to (a) read the args, (b) call the
Python-side override (not Qt's bare API), (c) recurse. No UI
changes. No config flag -- the toolbar's existing args is the
single source of truth for direction.

Steps:
1. Refactor ``cmd_sort_children`` to extract direction from
   the call args (positional, event, or kwarg). Default to
   ``"ascending"``.
2. Call ``node.sortChildren(order=direction)`` (the Python
   override that honours ``order`` AND persists).
3. Recurse: for each child, call
   ``cmd_sort_children(event, direction)`` so descendants
   sort with the same direction.
"""

import inspect
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest


PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")


def _bare_pane():
    """Create a minimal NchantdOfficeNodeEditPane without Qt init.

    Uses ``__new__`` so we can call ``cmd_sort_children``
    without spinning up a QApplication. Stubs the
    minimum surface the handler touches: ``app`` (for
    ``get_current_node``), ``get_node``, and any helper
    used to recurse.
    """
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeNodeEditPane,
    )
    pane = NchantdOfficeNodeEditPane.__new__(
        NchantdOfficeNodeEditPane
    )
    return pane


# ---------------------------------------------------------------------------
# Source-level: handler reads direction and recurses
# ---------------------------------------------------------------------------

def test_cmd_sort_children_reads_direction_arg():
    """``cmd_sort_children`` must inspect / branch on a
    direction argument so ascending vs descending buttons
    take different code paths.
    """
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeNodeEditPane,
    )
    src = inspect.getsource(NchantdOfficeNodeEditPane.cmd_sort_children)
    # Must reference both directions (case-insensitive ok).
    assert "ascending" in src.lower(), (
        "cmd_sort_children must read ascending direction "
        "(T-NEW-133)"
    )
    assert "descending" in src.lower(), (
        "cmd_sort_children must read descending direction "
        "(T-NEW-133)"
    )


def test_cmd_sort_children_calls_python_override():
    """``cmd_sort_children`` must call ``sortChildren(order=...)``
    on the Python side (the override that persists), NOT the
    bare Qt ``super().sortChildren(...)``.
    """
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeNodeEditPane,
    )
    src = inspect.getsource(NchantdOfficeNodeEditPane.cmd_sort_children)
    assert "order=" in src, (
        "cmd_sort_children must pass order= to the Python "
        "override (T-NEW-133)"
    )


def test_cmd_sort_children_recurses_into_subtree():
    """Source-level: handler must recurse into children so the
    entire subtree (not just immediate children) gets sorted.
    """
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeNodeEditPane,
    )
    src = inspect.getsource(NchantdOfficeNodeEditPane.cmd_sort_children)
    # The recursion call site should call the same handler (or
    # a helper) per child.
    assert (
        "childCount" in src or "get_children" in src or "recurs" in src.lower()
    ), (
        "cmd_sort_children must recurse over the node's "
        "children (T-NEW-133)"
    )


# ---------------------------------------------------------------------------
# Behavioural: handler sorts subtree with the requested direction
# ---------------------------------------------------------------------------

class _FakeChild:
    """Lightweight stand-in for a Qt tree node."""

    def __init__(self, name, children=None, persist_log=None):
        self.name = name
        self.children = list(children or [])
        self.persist_log = persist_log
        self.sort_calls = []  # records (column, order_str) per sort

    def childCount(self):
        return len(self.children)

    def child(self, i):
        return self.children[i]

    def sortChildren(self, column=0, order="ascending", db="db", sort_key=None):
        """Stand-in for the Python override at
        nchantrs/widgets/items/nodes.py:512.

        Records the call, sorts the children in place, and
        mirrors the real override's persistence (per-child
        position write) into ``persist_log``.
        """
        self.sort_calls.append((column, order, db))
        reverse = order == "descending"
        self.children.sort(key=lambda c: c.name.lower(), reverse=reverse)
        if self.persist_log is not None:
            for n, child in enumerate(self.children):
                self.persist_log.append((self.name, child.name, n))


def test_cmd_sort_children_sorts_immediate_children_ascending():
    """ascending arg -> children sorted by name (a-z)."""
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeNodeEditPane,
    )
    grandchild = _FakeChild("zeta")
    child_b = _FakeChild("bravo")
    child_a = _FakeChild("alpha", children=[grandchild])
    root = _FakeChild("root", children=[child_b, child_a])

    pane = _bare_pane()
    pane.get_node = lambda: root

    pane.cmd_sort_children("ascending")

    assert [c.name for c in root.children] == ["alpha", "bravo"], (
        f"ascending must sort children alphabetically; got "
        f"{[c.name for c in root.children]}"
    )


def test_cmd_sort_children_sorts_immediate_children_descending():
    """descending arg -> children sorted by name (z-a)."""
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeNodeEditPane,
    )
    child_a = _FakeChild("alpha")
    child_b = _FakeChild("bravo")
    root = _FakeChild("root", children=[child_a, child_b])

    pane = _bare_pane()
    pane.get_node = lambda: root

    pane.cmd_sort_children("descending")

    assert [c.name for c in root.children] == ["bravo", "alpha"], (
        f"descending must reverse-sort children; got "
        f"{[c.name for c in root.children]}"
    )


def test_cmd_sort_children_recurses_into_grandchildren():
    """Every descendant depth must get sorted, not just
    immediate children. After sort, root.children sorted AND
    each child's own children sorted.
    """
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeNodeEditPane,
    )
    # Two-level tree:
    #   root
    #     bravo (grandkids: zebra, apple)
    #     alpha (grandkids: mango, kiwi)
    grandkids_b = [_FakeChild("zebra"), _FakeChild("apple")]
    grandkids_a = [_FakeChild("mango"), _FakeChild("kiwi")]
    child_b = _FakeChild("bravo", children=grandkids_b)
    child_a = _FakeChild("alpha", children=grandkids_a)
    root = _FakeChild("root", children=[child_b, child_a])

    pane = _bare_pane()
    pane.get_node = lambda: root

    pane.cmd_sort_children("ascending")

    assert [c.name for c in root.children] == ["alpha", "bravo"], (
        f"root children must sort; got "
        f"{[c.name for c in root.children]}"
    )
    # Each child must have its own children sorted ascending.
    for child in root.children:
        names = [g.name for g in child.children]
        assert names == sorted(names, key=str.lower), (
            f"grandchildren under {child.name} must sort "
            f"ascending; got {names}"
        )


def test_cmd_sort_children_recurses_descending():
    """Subtree sort honours descending direction at every depth."""
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeNodeEditPane,
    )
    grandkids_b = [_FakeChild("apple"), _FakeChild("zebra")]
    child_b = _FakeChild("bravo", children=grandkids_b)
    child_a = _FakeChild("alpha")
    root = _FakeChild("root", children=[child_a, child_b])

    pane = _bare_pane()
    pane.get_node = lambda: root

    pane.cmd_sort_children("descending")

    assert [c.name for c in root.children] == ["bravo", "alpha"]
    for child in root.children:
        names = [g.name for g in child.children]
        if len(names) > 1:
            assert names == sorted(names, key=str.lower, reverse=True), (
                f"grandchildren under {child.name} must sort "
                f"descending; got {names}"
            )


def test_cmd_sort_children_persists_to_store():
    """Each descendant gets a persistence call so the
    database reflects the new order on reload.
    """
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeNodeEditPane,
    )
    persist_log: list = []
    grandkids = [_FakeChild("zebra"), _FakeChild("apple")]
    child_b = _FakeChild(
        "bravo", children=grandkids, persist_log=persist_log
    )
    child_a = _FakeChild("alpha", persist_log=persist_log)
    root = _FakeChild(
        "root", children=[child_b, child_a], persist_log=persist_log
    )

    pane = _bare_pane()
    pane.get_node = lambda: root

    pane.cmd_sort_children("ascending")

    # Every child + grandchild should have been written to the
    # store. Each persist entry is (parent_name, child_name, pos).
    parent_names = {entry[0] for entry in persist_log}
    assert "root" in parent_names, (
        "root's children must be persisted"
    )
    assert "bravo" in parent_names, (
        "bravo's grandchildren must be persisted (subtree sort)"
    )


def test_cmd_sort_children_handles_kwargs_direction():
    """direction may arrive as kwarg (defensive)."""
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeNodeEditPane,
    )
    child_a = _FakeChild("alpha")
    child_b = _FakeChild("bravo")
    root = _FakeChild("root", children=[child_a, child_b])

    pane = _bare_pane()
    pane.get_node = lambda: root

    pane.cmd_sort_children(order="descending")

    assert [c.name for c in root.children] == ["bravo", "alpha"]


def test_cmd_sort_children_defaults_to_ascending():
    """When no direction arg is passed, default to ascending."""
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeNodeEditPane,
    )
    child_b = _FakeChild("bravo")
    child_a = _FakeChild("alpha")
    root = _FakeChild("root", children=[child_b, child_a])

    pane = _bare_pane()
    pane.get_node = lambda: root

    pane.cmd_sort_children()

    assert [c.name for c in root.children] == ["alpha", "bravo"], (
        "default direction must be ascending"
    )