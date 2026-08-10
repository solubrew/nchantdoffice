"""T-NEW-057 — Review-driven regression tests for the update process.

This file adds 4 follow-up tests on top of
``tests/test_update_checker.py`` (T-DESK-053). It pins the
review findings documented in
``docs/update-process-review_20260810.md``:

  1. ``test_upgrade_lock_attribute_exists`` — once T-NEW-058
     lands, ``NchantdOfficeDBUpdate`` must carry an
     ``_upgrade_lock`` flag that prevents double-migration.

  2. ``test_update_checker_constructed_at_boot`` — once
     T-NEW-058 lands, ``NchantdOfficeCloak`` must construct a
     ``UpdateChecker`` instance in ``__init__`` (the review
     established that today NO live code constructs it; this
     test goes GREEN when T-NEW-058 ships).

  3. ``test_refresh_interval_is_function_or_configurable`` —
     once T-NEW-059 lands, ``REFRESH_INTERVAL_SECONDS`` must
     either be a function of cfg OR the test for a
     ``check_update_interval_hours`` config key must pass.
     Today ``REFRESH_INTERVAL_SECONDS`` is a constant — this
     test is RED until T-NEW-059.

  4. ``test_dismiss_version_accepts_days_parameter`` — once
     T-NEW-060 lands, ``dismiss_version()`` must accept an
     optional ``days`` parameter. Today it's positional-only
     with version — this test is RED until T-NEW-060.

The test class names map 1:1 to the follow-up card IDs in the
review doc so a future agent can grep
``git log --oneline -- tests/test_update_checker_review.py``
to find which T-NEW-NNN each test pins.

Tests are pure AST + module-attribute where possible (the test
env may lack a Qt surface; the live-cmd equivalent is
``cmds/_review_update_process.py``).
"""

import ast
import os
import re
import sys
from pathlib import Path

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

UPDATES_DIR = PROJ_ROOT / "nchantdoffice" / "updates"
CHECKER = UPDATES_DIR / "checker.py"
DB_UPDATE = UPDATES_DIR / "db.py"
CLOAK = PROJ_ROOT / "nchantdoffice" / "nchantdoffice.py"
CONSTANTS = PROJ_ROOT / "nchantdoffice" / "utilities" / "constants.py"
NCHANTDOFFICE_YAML = (
    PROJ_ROOT / "nchantdoffice" / "_data_" / "nchantdoffice.yaml"
)


# ---------------------------------------------------------------------------
# helpers (mirror the style of test_update_checker.py)
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    return path.read_text()


def _ast_class(src: str, name: str):
    """Return the first ast.ClassDef matching ``name``."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _ast_function(src: str, name: str):
    """Return the first ast.FunctionDef matching ``name``."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _function_source(src: str, name: str) -> str:
    """Return the full source line range for ``name``."""
    func = _ast_function(src, name)
    if func is None:
        return ""
    lines = src.splitlines()
    return "\n".join(lines[func.lineno - 1: func.end_lineno])


def _module_top_level_constant(src: str, name: str):
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return node.value
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                return node.value
    return None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_upgrade_lock_attribute_exists():
    """T-NEW-058 step 4: ``NchantdOfficeDBUpdate`` must carry
    an ``_upgrade_lock`` flag that prevents double-migration.

    RED until T-NEW-058 ships. The review doc
    (§2.4) calls out this exact fix.
    """
    src = _read(DB_UPDATE)
    cls = _ast_class(src, "NchantdOfficeDBUpdate")
    assert cls is not None, "NchantdOfficeDBUpdate class missing"

    # Look for ``self._upgrade_lock = ...`` in __init__ OR a
    # class-level annotation.
    has_init_attr = bool(
        re.search(r"self\._upgrade_lock\s*=", _function_source(src, "__init__"))
    )
    has_class_ann = bool(
        re.search(r"_upgrade_lock\s*:\s*bool", src)
    )
    assert has_init_attr or has_class_ann, (
        "T-NEW-058 step 4 missing: NchantdOfficeDBUpdate has no "
        "_upgrade_lock flag. See docs/update-process-review_20260810.md §2.4."
    )


def test_update_checker_constructed_at_boot():
    """T-NEW-058 step 2: ``NchantdOfficeCloak.__init__`` must
    construct a ``UpdateChecker`` instance.

    RED until T-NEW-058 ships. The review doc (§1.2 Call Graph)
    established that today NO live code constructs it; this test
    pins the future fix.
    """
    src = _read(CLOAK)
    cls = _ast_class(src, "NchantdOfficeCloak")
    assert cls is not None, "NchantdOfficeCloak class missing"

    init_src = _function_source(src, "__init__")

    # Accept either a direct construction
    # (``UpdateChecker(...)``) or an import + construction.
    assert "UpdateChecker" in src, (
        "T-NEW-058 step 2 missing: NchantdOfficeCloak does not "
        "construct an UpdateChecker. See "
        "docs/update-process-review_20260810.md §1.2."
    )
    # The construction must happen in __init__ or run_on_launch.
    run_on_launch_src = _function_source(src, "run_on_launch")
    combined = init_src + "\n" + run_on_launch_src
    assert (
        "UpdateChecker(" in combined
        or "self.update_checker" in combined
    ), (
        "T-NEW-058 step 2 missing: UpdateChecker is referenced "
        "but not constructed. Place construction in "
        "NchantdOfficeCloak.__init__."
    )


def test_refresh_interval_is_function_or_configurable():
    """T-NEW-059 step 1: ``REFRESH_INTERVAL_SECONDS`` must
    become configurable via a ``check_update_interval_hours``
    config key (default 6).

    RED until T-NEW-059 ships. Accepts either:
      - the constant is replaced by a function that reads from
        a cfg dict, OR
      - the config YAML has a ``check_update_interval_hours``
        key.

    The test is satisfied by either path (T-NEW-059 may choose
    either; the review doc §2.1 left the choice open).
    """
    checker_src = _read(CHECKER)

    # Option A: REFRESH_INTERVAL_SECONDS is now a function
    is_function = _ast_function(checker_src, "REFRESH_INTERVAL_SECONDS") is not None
    if is_function:
        return  # GREEN by option A

    # Option A': a sibling function ``refresh_interval_seconds(cfg)``
    # exists that reads from cfg. T-NEW-059 chose this path (kept
    # the constant for backward compatibility, added the function
    # alongside it).
    if _ast_function(checker_src, "refresh_interval_seconds") is not None:
        return  # GREEN by option A'

    # Option B: still a constant but the config YAML exposes the knob
    if NCHANTDOFFICE_YAML.exists():
        yaml_src = _read(NCHANTDOFFICE_YAML)
        if "check_update_interval_hours" in yaml_src:
            return  # GREEN by option B

    # Neither path is satisfied — fail with a clear message.
    assert False, (
        "T-NEW-059 step 1 missing: REFRESH_INTERVAL_SECONDS is "
        "still a module-level constant AND no "
        "refresh_interval_seconds() function exists AND "
        "check_update_interval_hours is not in nchantdoffice.yaml. "
        "See docs/update-process-review_20260810.md §2.1."
    )


def test_dismiss_version_accepts_days_parameter():
    """T-NEW-060 step 3: ``dismiss_version()`` must accept an
    optional ``days`` parameter (default 7) for snooze duration.

    RED until T-NEW-060 ships. Today the signature is
    ``dismiss_version(version: str) -> None`` (positional-only).
    After T-NEW-060 it becomes
    ``dismiss_version(version: str, days: int = 7) -> None``.
    """
    src = _read(CHECKER)
    func = _ast_function(src, "dismiss_version")
    assert func is not None, "dismiss_version() missing entirely"

    # Inspect the args
    arg_names = [a.arg for a in func.args.args]
    assert "days" in arg_names, (
        f"T-NEW-060 step 3 missing: dismiss_version() has args "
        f"{arg_names!r}; expected 'days' (default 7). "
        f"See docs/update-process-review_20260810.md §2.3."
    )

    # The default for 'days' should be present (default snooze duration).
    defaults = func.args.defaults
    num_defaults = len(defaults)
    num_no_default = len(func.args.args) - num_defaults
    # 'version' has no default (positional), 'days' has default 7
    assert num_defaults >= 1, (
        f"T-NEW-060 step 3: 'days' has no default value. "
        f"Expected default=7 (snooze duration)."
    )

    # Verify the default is 7 — either a literal int 7 OR a
    # reference to the DISMISS_DURATION_DAYS constant (which
    # itself is 7). The implementation chose the named-constant
    # route for clarity (avoids duplicating the literal in two
    # places). Both forms pass.
    days_default_idx = arg_names.index("days") - num_no_default
    if 0 <= days_default_idx < len(defaults):
        days_default = defaults[days_default_idx]
        actual_value = None
        if isinstance(days_default, ast.Constant):
            actual_value = days_default.value
        elif isinstance(days_default, ast.Name):
            # Named reference — resolve DISMISS_DURATION_DAYS = 7.
            # Look up the module-level constant's value via the
            # same AST scan pattern.
            ref_name = days_default.id
            const_value_node = _module_top_level_constant(src, ref_name)
            if isinstance(const_value_node, ast.Constant):
                actual_value = const_value_node.value
        assert actual_value == 7, (
            f"T-NEW-060 step 3: 'days' default is {actual_value!r}; "
            f"expected 7 (matches the review doc's 7-day snooze, "
            f"either literal or via DISMISS_DURATION_DAYS constant)."
        )
