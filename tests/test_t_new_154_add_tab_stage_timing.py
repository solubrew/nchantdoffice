"""T-NEW-154 -- add_tab stage timing (instrumentation-only, no optimization).

The 2026-08-17 testing report flagged T-NEW-154: 'Profile
new-document creation performance.' The card's first step is
'add stage timing before optimizing; no timing instrumentation
currently identifies the bottleneck in widgets/panes/new.py /
document create.'

Pre-fix: ``add_tab`` at panes/new.py:178 runs 4-5 logical
phases (input-dialog prompt, widget-code resolution,
load-strategy resolution, super().add_tab, override) but
emits no per-phase timing — operators have no way to tell
which phase dominates end-to-end latency.

Post-fix: emit a single line per phase via ``logma.info``
showing the phase name + elapsed ms. The instrumentation
is "always-on" via ``time.monotonic()`` snapshots and adds
two log lines per call. No behavioural change; existing
tests still pass.

Tests are AST-source structural (mirroring the umbrella
pattern). panes/new.py imports PySide6 via nchantrs.
"""

import ast
from pathlib import Path

NEW_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/panes/new.py"
)


def _function_source(name: str) -> str:
    tree = ast.parse(NEW_PATH.read_text())
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
        ):
            return ast.unparse(node)
    raise AssertionError(f"{name} not found")


def test_add_tab_uses_time_monotonic():
    """``add_tab`` body calls ``time.monotonic()`` to snapshot phase timestamps."""
    source = _function_source("add_tab")
    assert "time.monotonic" in source, (
        "add_tab must call time.monotonic() to enable stage "
        "timing. T-NEW-154 instrumentation step; the timing "
        "calls bookend the major phases so operators can "
        "identify the bottleneck phase."
    )


def test_add_tab_emits_phase_log_lines():
    """``add_tab`` body emits at least one ``logma.info`` line that mentions ``ms`` / ``elapsed``.

    The T-NEW-154 instrumentation emits lines like
    ``"[panes.new] T-NEW-154 add_tab total: 12.3ms"``. This
    test runs on the ``ast.unparse``d source (string),
    not the AST, so we look for the literal substring
    ``"ms"`` in a ``logma.info`` call site.
    """
    source = _function_source("add_tab")
    # Look for logma.info with ms/elapsed in surrounding text.
    # Run on the unparsed string and locate 'logma.info' call
    # sites, then check the next 100 chars for 'ms'.
    has_phase_logging = False
    idx = 0
    while True:
        idx = source.find("logma.info", idx)
        if idx < 0:
            break
        # Take the next 250 chars and look for 'ms'
        snippet = source[idx : idx + 250]
        if "ms" in snippet:
            has_phase_logging = True
            break
        idx += 1
    assert has_phase_logging, (
        "add_tab must emit at least one logma.info line containing "
        "'ms' so operators can identify the slow phase. T-NEW-154 "
        "instrumentation step. The 'logma.info' call with the timing "
        "result (e.g. 'add_tab total: 12.3ms') must be present."
    )


def test_add_tab_super_call_still_present():
    """The ``super().add_tab(tabset, widgdata)`` call is preserved (no regression)."""
    source = _function_source("add_tab")
    has_super = False
    for sub in ast.walk(ast.parse(source)):
        if isinstance(sub, ast.Call):
            func = sub.func
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Call)
            ):
                inner = func.value.func
                if (
                    isinstance(inner, ast.Name)
                    and inner.id == "super"
                    and func.attr == "add_tab"
                ):
                    has_super = True
    assert has_super, (
        "add_tab must still call super().add_tab(tabset, widgdata) — "
        "T-NEW-154 is instrumentation-only, not a structural change."
    )
