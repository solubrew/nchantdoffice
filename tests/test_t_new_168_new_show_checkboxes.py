"""T-NEW-168 — panes/new.py show_checkboxes / update_checkboxes is a forgotten stub.

The 2026-08-18 sweep of in-code markers turned up a class of
bugs that aren't tagged with any PUSH-to-0.0.3 marker at all:
**forgotten stubs called by live dispatchers**. ``panes/new.py``
has two such pairings:

  - ``show_multiple_options`` at line 388 — the REAL
    implementation that builds a NchantdCheckboxGroup with
    ``[x["name"] for x in self.active_item.multi_options]``
    and adds it to ``self.center_layout``.

  - ``show_checkboxes`` at line 309 — a forgotten stub
    (empty docstring + ``return self``) that is the ONLY
    method called by ``update_checkboxes`` at line 457::

        if self.active_item.has_multiple_options:
            self.show_checkboxes()

The dispatcher fires the wrong (stubbed) method. Operators
selecting a multi-option new-document item see no checkbox UI
render. The real impl ``show_multiple_options`` exists and
works — it's just not wired to the dispatcher.

Fix (T-NEW-168): one-line rename. ``update_checkboxes``
calls ``self.show_multiple_options()`` instead of
``self.show_checkboxes()``. The stub method ``show_checkboxes``
is removed (no other callers).

Tests are AST-source structural — ``panes/new.py`` imports
PySide6 via the parent ``NchantdWidget`` chain.
"""

import ast
from pathlib import Path


NEW_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/panes/new.py"
)


def _function_source(name: str) -> str:
    tree = ast.parse(NEW_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"{name} not found")


def test_update_checkboxes_dispatches_to_show_multiple_options():
    """``update_checkboxes`` calls ``self.show_multiple_options()``.

    Pre-fix it called ``self.show_checkboxes()`` — a forgotten
    stub. ``show_multiple_options`` is the real impl that
    builds the NchantdCheckboxGroup.
    """
    source = _function_source("update_checkboxes")
    # Walk the AST to find call sites in the body (excluding
    # docstring Expr) — the docstring might mention the old
    # name (historical context) but the BODY must only call
    # the new target.
    tree = ast.parse(source)
    body_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                body_calls.append(func.attr)
    assert "show_multiple_options" in body_calls, (
        "update_checkboxes must call self.show_multiple_options() "
        "— that's the real impl (lines 388-395) that builds the "
        "NchantdCheckboxGroup for multi-option new-document items."
    )
    # Pre-fix bug: the body called show_checkboxes (the stub).
    # Post-fix: that call must NOT be present in the body.
    assert "show_checkboxes" not in body_calls, (
        "update_checkboxes body must NOT call self.show_checkboxes() — "
        "that's the forgotten stub. T-NEW-168 fix renames the "
        "dispatch target to show_multiple_options."
    )


def test_show_multiple_options_is_unaffected():
    """Real impl body remains intact after the rename."""
    source = _function_source("show_multiple_options")
    assert "NchantdCheckboxGroup" in source, (
        "show_multiple_options body must still construct the "
        "NchantdCheckboxGroup (real impl)."
    )
    assert "multi_options" in source, (
        "show_multiple_options body must still read "
        "self.active_item.multi_options for the checkbox labels."
    )


def test_show_checkboxes_dispatcher_call_gone():
    """The stub ``show_checkboxes`` method body stays, but no dispatcher calls it.

    After the fix, ``show_checkboxes`` is dead code (no callers).
    We pin that by walking every method body and checking none
    invokes ``self.show_checkboxes()``. The stub definition
    stays (no callers, but defining it preserves the operator's
    intent); the dispatcher rename is what lands the bug-fix.
    """
    src = NEW_PATH.read_text()
    tree = ast.parse(src)
    callers = []
    for node in ast.walk(tree):
        # Find every Call node whose target is ``self.show_checkboxes(...)``.
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "self"
            and func.attr == "show_checkboxes"
        ):
            # Find the enclosing method body
            callers.append(node.lineno)
    assert not callers, (
        f"self.show_checkboxes is still called from {len(callers)} "
        f"site(s) at lines {callers}. Pre-fix the dispatcher at "
        f"update_checkboxes (line 457) called it. T-NEW-168 must "
        f"rename the call target to show_multiple_options."
    )


def test_show_checkboxes_stub_definition_remains():
    """The ``show_checkboxes`` stub definition stays as an alias for back-compat.

    After the dispatcher rename, ``show_checkboxes`` is dead
    code BUT we keep the definition as a thin alias that
    forwards to ``self.show_multiple_options()`` (and returns
    self so chainable callers still work). This preserves any
    external code path that invokes the old name.
    """
    src = NEW_PATH.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name == "show_checkboxes"):
            continue
        # Body must call self.show_multiple_options() (forward)
        body_calls = []
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Call):
                continue
            func = sub.func
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.attr == "show_multiple_options"
            ):
                body_calls.append(sub)
        assert body_calls, (
            "show_checkboxes stub must forward to "
            "self.show_multiple_options() — without the forward, "
            "the stub is still a no-op (just renamed shape). The "
            "T-NEW-168 fix turns the stub into a real alias."
        )
        return
    raise AssertionError(
        "show_checkboxes method missing entirely — T-NEW-168 "
        "renames the call target but keeps the stub as a forwarding "
        "alias. If you intended to remove the stub, that's a "
        "separate cleanup commit."
    )