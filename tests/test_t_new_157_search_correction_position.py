"""T-NEW-157 -- Search correction-position fallback at models.py:4768.

The 2026-08-17 testing report: 'Resolve models.py:3039
instead of silently forcing position 0.' The card is
about the active_tab_position clamping behaviour at
``models.py:4768``.

Pre-fix flow:

  try:
      active_tab_position = int(active_tab_position)
  except (ValueError, TypeError):
      active_tab_position = 0

  if tabsdata:
      if active_tab_position >= len(tabsdata):
          active_tab_position = 0  # silently forces 0

If the saved active_tab_position is out-of-bounds (e.g.
the tab was deleted but the parameter still points to
the old index), the load silently jumped to tab 0
instead of staying near the operator's previous context.

Post-fix: clamp to ``len(tabsdata) - 1`` (the last valid
tab) when the saved position is out of bounds. The
operator's context is preserved as much as possible;
they end up on the nearest valid tab instead of an
arbitrary first one.

Tests are AST-source structural (mirroring T-NEW-133 /
T-NEW-152 / T-NEW-156).

Note on the operator's reference to ``models.py:3039``:
that line falls inside ``get_rolling_summary`` (the
``return [...]`` line), not the search-correction code.
The actual correction-position logic is at line 4768.
T-NEW-157 ships the clamping fix at the real site; the
T-3039 reference is treated as a typo in the original
operator writeup.
"""

import ast
from pathlib import Path

MODELS_PATH = Path(__file__).parents[1] / "nchantdoffice/models.py"


def _find_function_containing_lineno(lineno: int) -> str | None:
    """Walk the AST and return the function name that contains ``lineno``.

    The search-correction logic is inline in
    ``go_to_node`` / ``buildTabSet`` — there's no named
    helper. This walks every function in models.py and
    returns the one that contains line 4768 (or nearby
    if the line drifts across commits).
    """
    tree = ast.parse(MODELS_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= lineno <= (node.end_lineno or node.lineno):
                return node.name
    return None


def test_search_correction_clamps_not_zeroes():
    """``go_to_node`` / active_tab_position clamping clamps to last valid index, not 0.

    Pre-fix the fallback on out-of-bounds forced
    ``active_tab_position = 0``. Post-fix it clamps to
    ``len(tabsdata) - 1`` (the nearest valid tab).
    """
    # Look for the clamping fallback. Pre-fix uses
    # `= 0` directly. Post-fix uses `= len(tabsdata) - 1`.
    # Walk every function in models.py and find the one
    # whose body has the `>= len(tabsdata)` guard.
    tree = ast.parse(MODELS_PATH.read_text())
    found_clamps_to_last = False
    found_forces_zero = False  # regression: the OLD silent-zero path

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # Walk the function body
        for sub in ast.walk(node):
            if not isinstance(sub, ast.If):
                continue
            cond = ast.unparse(sub.test)
            if "len(tabsdata)" not in cond:
                continue
            # Found the if-statement. Walk its body for the
            # clamping assignment.
            for body_stmt in sub.body:
                if isinstance(body_stmt, ast.Assign):
                    # Check the right-hand side
                    rhs = ast.unparse(body_stmt.value)
                    if rhs == "len(tabsdata) - 1":
                        found_clamps_to_last = True
                    if rhs == "0":
                        found_forces_zero = True
    assert found_clamps_to_last, (
        "T-NEW-157 fix not present: the "
        "active_tab_position fallback must clamp to "
        "len(tabsdata) - 1 (the last valid tab), not "
        "silently force position 0."
    )
    assert not found_forces_zero, (
        "The pre-fix 'active_tab_position = 0' fallback "
        "is still present in the function body. T-NEW-157 "
        "removed that silent-zero path; the post-fix "
        "uses len(tabsdata) - 1 clamping instead."
    )


def test_search_correction_docstring_mentions_t_new_157():
    """The function containing the fix has its docstring mention T-NEW-157."""
    tree = ast.parse(MODELS_PATH.read_text())
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if not node.body:
            continue
        first = node.body[0]
        if not (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            continue
        if "T-NEW-157" in first.value.value:
            found = True
            break
    assert found, (
        "The function containing the T-NEW-157 fix should "
        "reference T-NEW-157 in its docstring (operator reads "
        "the change log via docstring headers)."
    )
