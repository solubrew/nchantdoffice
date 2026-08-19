"""T-NEW-167 — wire panes/sources.py cmd_on_name_change / cmd_on_description_change.

The 2026-08-18 sweep of PUSH-to-0.0.3 markers turned up 70+
genuine deferred features, but the audit also surfaced a smaller
class of bugs: **stubs with no marker**. The cmd_on_name_change
and cmd_on_description_change methods in panes/sources.py are
textbook forgotten stubs:

  - Empty docstring (`""""""`)
  - Body just `return self`
  - No PUSH-to-0.0.3 marker (these were forgotten so completely
    they don't even have a deferred-feature comment)

The user impact: the Data Source Name and Description input
fields in the Sources pane (wired via NchantdLabeledEntry at
sources.py:749/758) fire their handlers on every keystroke
— but the handlers are no-ops. **Typing in the fields doesn't
save**. Operators can fill in a name/description, hit Save, and
the values are dropped.

The canonical contract lives in panes/charts.py:616/635
(the sibling `cmd_on_name_change` / `cmd_on_description_change`
patterns). Those:

  1. Read ``event`` (the signal payload from the input widget)
  2. Pull ``text`` off it (the new value the user typed)
  3. Try the model first (``self.model.set_chart_name(value)``)
  4. Fall back to ``self.config.dikt["chart_name"] = value``
  5. Wrap in try/except so a model read failure doesn't crash

The fix mirrors that pattern in panes/sources.py. The
``cmd_connect_source`` stub at sources.py:784 is a third
adjacent forgotten stub, but it's wired to a separate action
(the "Connect" button, distinct from name/description
edits) — out of scope for this card, filed separately.

Tests are AST-source structural (mirroring the established
pattern from T-NEW-117 / T-NEW-148 / T-NEW-161 / T-NEW-162 /
T-NEW-163 / T-NEW-165) — ``panes/sources.py`` imports PySide6
via the parent ``NchantdWidget`` chain.
"""

import ast
from pathlib import Path


SOURCES_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/panes/sources.py"
)


def _function_source(name: str) -> str:
    tree = ast.parse(SOURCES_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"{name} not found")


def test_cmd_on_name_change_is_not_a_return_self_stub():
    """``cmd_on_name_change`` reads ``event.text`` and persists it.

    Pre-fix body was ``return self`` (forgotten stub). The handler
    is wired to the Data Source Name input field (sources.py:749)
    so every keystroke fires a no-op.
    """
    source = _function_source("cmd_on_name_change")
    # Must NOT be the pure stub (docstring + return self only).
    body_stmts = [
        s for s in ast.parse(source).body[0].body
        if not (
            isinstance(s, ast.Expr)
            and isinstance(s.value, ast.Constant)
            and isinstance(s.value.value, str)
        )
    ]
    assert len(body_stmts) > 1 or (
        len(body_stmts) == 1
        and not isinstance(body_stmts[0], ast.Return)
        or not (
            isinstance(body_stmts[0].value, ast.Name)
            and body_stmts[0].value.id == "self"
        )
    ), (
        "cmd_on_name_change body must NOT be the empty docstring + "
        "return self shape. Pre-fix: typing in the Data Source Name "
        "field was a no-op."
    )
    # Must pull value from event
    assert "event" in source, (
        "cmd_on_name_change must read event (the signal payload from "
        "NchantdLabeledEntry)."
    )
    assert "text" in source or "value" in source, (
        "cmd_on_name_change must extract the text/value from event "
        "(NchantdLabeledEntry passes the value via event.text or "
        "the event itself in some Qt versions)."
    )


def test_cmd_on_description_change_is_not_a_return_self_stub():
    """``cmd_on_description_change`` reads event and persists it."""
    source = _function_source("cmd_on_description_change")
    body_stmts = [
        s for s in ast.parse(source).body[0].body
        if not (
            isinstance(s, ast.Expr)
            and isinstance(s.value, ast.Constant)
            and isinstance(s.value.value, str)
        )
    ]
    assert len(body_stmts) > 1 or (
        len(body_stmts) == 1
        and not isinstance(body_stmts[0], ast.Return)
        or not (
            isinstance(body_stmts[0].value, ast.Name)
            and body_stmts[0].value.id == "self"
        )
    ), (
        "cmd_on_description_change body must NOT be the empty docstring + "
        "return self shape. Pre-fix: typing in the Data Source Description "
        "field was a no-op."
    )
    assert "event" in source, (
        "cmd_on_description_change must read event (the signal payload "
        "from NchantdLabeledEntry)."
    )


def test_cmd_on_name_change_persists_to_model_or_config():
    """``cmd_on_name_change`` calls ``model.set_chart_name`` or sets config fallback.

    Mirrors the canonical charts.py:616 pattern: model first,
    config fallback. The user's typed name must land somewhere.
    """
    source = _function_source("cmd_on_name_change")
    # Look for the persistence hooks
    has_model_call = "set_chart_name" in source or "set_source_name" in source or "set_name" in source
    has_config_fallback = "config" in source and "dikt" in source
    assert has_model_call or has_config_fallback, (
        "cmd_on_name_change must persist the typed value — either "
        "via the model (set_chart_name / set_source_name / set_name) "
        "or via the config fallback (config.dikt[key] = value). "
        "Otherwise the typed Data Source Name is silently dropped."
    )


def test_cmd_on_description_change_persists_to_model_or_config():
    """``cmd_on_description_change`` persists via model or config fallback."""
    source = _function_source("cmd_on_description_change")
    has_model_call = (
        "set_chart_description" in source
        or "set_source_description" in source
        or "set_description" in source
    )
    has_config_fallback = "config" in source and "dikt" in source
    assert has_model_call or has_config_fallback, (
        "cmd_on_description_change must persist the typed value — "
        "either via the model or via the config fallback."
    )


def test_handlers_wrapped_in_try_except():
    """Both handlers wrap their work in try/except so a model read failure doesn't crash.

    Mirrors the canonical charts.py:616 pattern. A user typing in
    a field should never crash the app.
    """
    name_src = _function_source("cmd_on_name_change")
    desc_src = _function_source("cmd_on_description_change")
    for label, src in [("cmd_on_name_change", name_src), ("cmd_on_description_change", desc_src)]:
        assert "try:" in src and "except" in src, (
            f"{label} must wrap its persistence work in try/except so "
            f"a transient model failure doesn't crash the app."
        )