"""T-NEW-164 part B — activate cmd_save_instance in the toolbar + drop stale pop-dialog marker.

The 2026-08-18 PUSH-to-0.0.3 sweep filed T-NEW-164 with 12 misc
deferred items. T-NEW-164 part A (commit 5b586c5) shipped 2
trivial doc-only wins (drop stale Sprint-20 prose + relabel the
settings long-method marker). Part B ships the smallest remaining
UI fix:

1. Activate ``cmd_save_instance`` in the document-buttonbar
   actions dict at toolboxes.py:929. The handler is real
   (Sprint-20 implementation at line 858, post-Sprint-20
   refactor); only the toolbar button was deferred. Uncommenting
   the button makes the "Save Instance" UI reachable for users
   who hit the toolbar but not the keyboard shortcut.

2. Drop the misleading ``# PUSH to 0.0.3 change a pop dialog
   for instance selection/open/new`` comment at toolboxes.py:942.
   The pro-tier new_instance handler on the line above is
   already wired (cmd_create_new_instance) — the comment was
   stale "deferred until 0.0.3" prose for work that shipped.

The other toolbar actions (``duplicate_instance``,
``export_instance``) stay deferred to 0.0.3+ per the card body —
the mirror-instance UX is a separate feature that needs its own
design call.

Tests are AST-source structural (mirroring the established
pattern from T-NEW-117 / T-NEW-161 / T-NEW-165) because the
toolboxes.py module imports PySide6 / nchantrs widgets.
"""

import ast
from pathlib import Path


TOOLBOXES_PATH = (
    Path(__file__).parents[1]
    / "nchantdoffice/widgets/controls/toolboxes.py"
)


def _function_source(name: str) -> str:
    tree = ast.parse(TOOLBOXES_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"{name} not found")


def test_save_instance_action_present_in_toolbar_config():
    """The ``actions`` dict now has ``save_instance`` at position 3.

    T-NEW-164 part B: the toolbar button was the only thing deferred
    — the cmd_save_instance handler shipped in Sprint 20. Uncommenting
    the button makes it reachable from the document-buttonbar.
    """
    src = TOOLBOXES_PATH.read_text()
    # The actions dict uses double-quoted keys/values throughout.
    # Look for the action key (any quoting) and the handler binding.
    assert '"save_instance"' in src, (
        "toolboxes.py must include 'save_instance' as an action key "
        "in the actions dict so the toolbar button is reachable. "
        "T-NEW-164 part B activates cmd_save_instance in the toolbar."
    )
    assert "self.cmd_save_instance" in src, (
        "toolboxes.py must wire the save_instance action to "
        "self.cmd_save_instance (the real handler at line 858)."
    )


def test_pull_marker_removed_from_save_instance_action():
    """The literal ``# PUSH to 0.0.3`` marker above save_instance is gone."""
    src = TOOLBOXES_PATH.read_text()
    import re

    # Find any '# PUSH to 0.0.3' marker lines and confirm none of them
    # are in the document-buttonbar area (where save_instance lives).
    push_lines = [
        i + 1
        for i, ln in enumerate(src.splitlines())
        if re.search(r"#\s*PUSH\s+(?:to|until)\s+(?:version\s+)?0\.0\.3", ln, re.IGNORECASE)
    ]
    # Read the save_instance action line + 3 lines after — confirm no
    # PUSH-to-0.0.3 marker in that vicinity. The action uses
    # double-quoted 'save_instance' so match either quoting.
    save_idx = max(src.find('"save_instance"'), src.find("'save_instance'"))
    assert save_idx != -1, "save_instance action missing"
    # Window: 6 lines around the save_instance line
    lines = src.splitlines()
    save_line = src[:save_idx].count("\n") + 1
    vicinity = lines[max(0, save_line - 5) : save_line + 5]
    for ln in vicinity:
        assert not re.search(
            r"#\s*PUSH\s+(?:to|until)\s+(?:version\s+)?0\.0\.3", ln, re.IGNORECASE
        ), (
            f"save_instance action vicinity still has a PUSH-to-0.0.3 marker: "
            f"{ln!r}. T-NEW-164 part B removes the deferred marker for "
            f"the activated save button."
        )


def test_pop_dialog_marker_removed():
    """The trailing ``# PUSH to 0.0.3 change a pop dialog ...`` comment is gone.

    The pro-tier new_instance handler on the line above is already
    wired (cmd_create_new_instance). The marker was stale "deferred
    until 0.0.3" prose for work that shipped.
    """
    src = TOOLBOXES_PATH.read_text()
    assert "change a pop dialog for instance selection/open/new" not in src, (
        "toolboxes.py:942 still has the stale 'change a pop dialog' "
        "PUSH-to-0.0.3 marker. The pro-tier new_instance handler is "
        "already wired — drop the misleading comment."
    )


def test_duplicate_instance_action_still_deferred():
    """``duplicate_instance`` stays deferred to 0.0.3+ (separate feature).

    The mirror-instance UX (work on two different nodes in two screens
    from the same document) is a substantial feature that needs its
    own design call. T-NEW-164 part B only activates the trivial
    ``save_instance`` button — duplicate_instance stays commented.
    """
    src = TOOLBOXES_PATH.read_text()
    # The duplicate_instance button is the OTHER commented button in
    # the actions dict. Confirm it's NOT in the live action dict.
    # Check the actions dict by looking for "'duplicate_instance'"
    # appearing in a non-comment context.
    import re

    live_count = 0
    for ln in src.splitlines():
        # Skip pure-comment lines (start with whitespace + #)
        stripped = ln.lstrip()
        if stripped.startswith("#"):
            continue
        if "'duplicate_instance'" in ln:
            live_count += 1
    assert live_count == 0, (
        f"duplicate_instance is wired into the live actions dict "
        f"({live_count} matches). T-NEW-164 part B only activates "
        f"save_instance — duplicate_instance stays deferred to 0.0.3+."
    )