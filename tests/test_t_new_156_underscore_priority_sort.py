"""T-NEW-156 -- Sort `_`-prefixed nodes first.

The 2026-08-17 testing report: 'Sort `_`-prefixed nodes
first. Add an explicit underscore-priority comparator while
preserving the selected ascending/descending order for the
remaining names.'

Operators keep a few "internal" subtrees whose names begin
with `_` (e.g. `_system`, `_template`). Currently those
internal subtrees get sorted into the alphabetical middle
of the tree, hidden between their siblings. Operators want
the underscore-prefixed entries to ALWAYS come first
(priority group), then ascending/descending for the rest.

Implementation: a comparator that returns:

   (-1, lowercased_name) if name starts with '_'
   (0, lowercased_name) otherwise

Wrapping the name in a sort-key tuple makes the priority
group stable regardless of order (ascending/descending flip
the secondary sort key, but the priority group is
wholesale-ordered).

The upstream ``NchantdOfficeTreeNode.sortChildren``
(nchantrs/nchantrs/widgets/items/nodes.py:446) already
accepts a ``sort_key=`` parameter; the fix is to build the
underscore-first comparator in ``panes/documents.py`` and
thread it through ``_sort_subtree`` /
``cmd_sort_children``.

Tests are AST-source structural (mirroring T-NEW-133 / T-NEW-152).
"""

import ast
from pathlib import Path

DOCUMENTS_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/panes/documents.py"
)


def _function_source(name: str) -> str:
    tree = ast.parse(DOCUMENTS_PATH.read_text())
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
        ):
            return ast.unparse(node)
    raise AssertionError(f"{name} not found")


def test_underscore_priority_key_exists():
    """A helper ``_underscore_priority_key`` (or equivalent) is defined on the class.

    T-NEW-156: comparator that returns (-1, name) for
    underscore-prefixed names, (0, name) otherwise.
    """
    tree = ast.parse(DOCUMENTS_PATH.read_text())
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and (
            node.name == "_underscore_priority_key"
            or node.name == "underscore_priority_key"
            or node.name == "_sort_priority_key"
        ):
            found = True
            break
    assert found, (
        "A sort-key helper (_underscore_priority_key or "
        "underscore_priority_key or _sort_priority_key) must "
        "exist on NchantdOfficeNodeEditPane — that's the "
        "underscore-first comparator T-NEW-156 requires."
    )


def test_sort_subtree_threads_priority_key():
    """``_sort_subtree`` threads the priority ``sort_key`` through to ``node.sortChildren``."""
    source = _function_source("_sort_subtree")
    # Post-fix: node.sortChildren(0, order=direction,
    # sort_key=self._underscore_priority_key)
    has_priority_key = (
        "sort_key" in source
        and ("_underscore_priority_key" in source or "underscore_priority_key" in source)
    )
    assert has_priority_key, (
        "_sort_subtree must thread the priority sort_key "
        "through to node.sortChildren. Pre-fix the call was "
        "node.sortChildren(0, order=direction) -- T-NEW-156 "
        "adds sort_key=self._underscore_priority_key so the "
        "underscore-first comparator applies."
    )


def test_sort_subtree_recurse_still_present():
    """The recursive sort for descendants stays intact (regression guard)."""
    source = _function_source("_sort_subtree")
    # Look for the recursive call
    has_recurse = "_sort_subtree" in source and (
        "child(" in source and "for i in range" in source
    )
    assert has_recurse, (
        "_sort_subtree must still recurse into each child "
        "(T-NEW-156 is comparator-only; the cascade is "
        "preserved from T-NEW-133)."
    )
