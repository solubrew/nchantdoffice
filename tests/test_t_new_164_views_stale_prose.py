"""T-NEW-164 part A — drop stale Sprint-20 closeout prose + relabel settings long-method marker.

The 2026-08-18 PUSH-to-0.0.3 sweep filed T-NEW-164 with 12 misc
deferred items. The DECIDE-1 matrix narrows this commit to two
trivial doc-only wins:

1. views.py: drop the 'Sprint 20: previously a stub with a
   "PUSH to 0.0.3" marker' prose from the switch_to_account_tab
   and on_window_move docstrings. The Sprint-20 fixes shipped
   long ago; the markers are gone; the historical closeout
   prose is misleading.

2. settings.py:139: replace the '# PUSH 0.0.3: long_method
   >150 audit false-positive.' marker with a T-NEW-166
   reference. Per the T-NEW-164 card body, the settings
   long-method marker rolls into T-NEW-166 (the auditor
   false-positive card).

Tests are AST-source structural — views.py and settings.py are
not Qt-bound themselves but importing them can pull in Qt
via module-level imports. Mirroring the established Qt-bound-
module test pattern from T-NEW-117 / T-NEW-161 / T-NEW-162 /
T-NEW-165.
"""

import ast
from pathlib import Path


VIEWS_PATH = Path(__file__).parents[1] / "nchantdoffice/views.py"
SETTINGS_PATH = (
    Path(__file__).parents[1]
    / "nchantdoffice/widgets/config/settings.py"
)


def _function_source(path: Path, name: str) -> str:
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"{name} not found in {path}")


def test_switch_to_account_tab_docstring_drops_stale_prose():
    """The Sprint-20 closeout prose is removed from switch_to_account_tab.

    T-NEW-164 DROP: the prose was misleading because the
    PUSH 0.0.3 marker no longer exists in the codebase (the
    Sprint-20 implementation shipped it). The docstring now
    describes the current contract directly.
    """
    source = _function_source(VIEWS_PATH, "switch_to_account_tab")
    assert "previously a stub" not in source, (
        "switch_to_account_tab docstring still has the stale "
        "'previously a stub' closeout prose. T-NEW-164 DROP-1: "
        "remove it — the Sprint-20 fix shipped long ago."
    )
    assert "PUSH to 0.0.3" not in source, (
        "switch_to_account_tab still mentions the PUSH-to-0.0.3 "
        "marker in its docstring. T-NEW-164 DROP-1: remove the "
        "misleading historical reference."
    )


def test_on_window_move_docstring_drops_stale_prose():
    """The Sprint-20 closeout prose is removed from on_window_move.

    T-NEW-164 DROP: same as switch_to_account_tab — the
    Sprint-20 work shipped, the marker is gone, the prose is
    misleading.
    """
    source = _function_source(VIEWS_PATH, "on_window_move")
    assert "previously a stub" not in source, (
        "on_window_move docstring still has the stale 'previously "
        "a stub' closeout prose. T-NEW-164 DROP-1: remove it."
    )
    assert "PUSH to 0.0.3" not in source, (
        "on_window_move still mentions the PUSH-to-0.0.3 marker. "
        "T-NEW-164 DROP-1: remove the misleading reference."
    )


def test_settings_init_view_marker_rolls_into_t_new_166():
    """settings.py:139 references T-NEW-166, not PUSH 0.0.3.

    T-NEW-164 DEMOTE-1 (rolled into T-NEW-166 per the card body):
    the long-method marker is an auditor false-positive, not a
    deferred feature. Replace the literal '# PUSH 0.0.3: long_method'
    comment with '# T-NEW-166: long_method >150 audit
    false-positive.' so the catalog search surfaces the right
    card.
    """
    src = SETTINGS_PATH.read_text()
    assert "PUSH 0.0.3: long_method" not in src, (
        "settings.py:139 still has the literal '# PUSH 0.0.3: "
        "long_method >150 audit false-positive.' marker. "
        "T-NEW-164 relabels it as T-NEW-166."
    )
    assert "T-NEW-166: long_method" in src, (
        "settings.py must reference T-NEW-166 in the long-method "
        "comment so the catalog surfaces the right card."
    )


def test_views_module_no_push_marker_remains():
    """No literal '# PUSH to 0.0.3' marker exists in views.py."""
    src = VIEWS_PATH.read_text()
    # Allow prose mentions in comments but flag the literal
    # PUSH-to-0.0.3 marker form that the sweep grep uses.
    import re

    matches = re.findall(r"#\s*PUSH\s+to\s+0\.0\.3", src, flags=re.IGNORECASE)
    assert not matches, (
        f"views.py still contains literal '# PUSH to 0.0.3' "
        f"markers: {matches}. T-NEW-164 DROP-1 must clear them."
    )