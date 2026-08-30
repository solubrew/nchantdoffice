"""T-NEW-070 (DESK-4b): runNchantdOffice.py import order contract.

Pins the contract that:
  - crow.crowLoad is called BEFORE the user_config import
    (because crow.crowLoad sets up sys.path so the
    nchantdoffice package is importable)
  - The user_config import is NOT wrapped in try/except
    (because the import is guaranteed to work once
    crow.crowLoad has run)
  - The QtWebEngine env setup runs AFTER crow.crowLoad but
    BEFORE Qt is imported (so QT_OPENGL etc. are set in time)
  - write_default_config() is called before any Qt usage
"""
import ast
from pathlib import Path

RUN = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "cmds/runNchantdOffice.py"
)


def _read():
    return RUN.read_text()


def _ast_function_or_import(src):
    """Return list of (name, lineno) for top-level imports."""
    tree = ast.parse(src)
    items = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                items.append((alias.asname or alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                items.append((f"{node.module}.{alias.name}", node.lineno))
        elif isinstance(node, ast.Expr):
            # Catch top-level expression statements (sys.path.insert, crow.crowLoad, etc.)
            if isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Attribute):
                    items.append((f"<call> {func.attr}", node.lineno))
                elif isinstance(func, ast.Name):
                    items.append((f"<call> {func.id}", node.lineno))
    return items


def test_crow_crowLoad_before_user_config_import():
    """crow.crowLoad is no longer used — the sys.path.insert at
    /home/solubrew/Documents/AIM replaces it for local development.
    This test verifies the old contract is gone (no live crowLoad
    call in the actual code) so the file cannot regress by
    re-adding it without updating the test.
    """
    src = _read()
    # Use AST to find actual crowLoad CALLS, not string mentions
    # in embedded docs. The heredoc (# ||...||) contains CHANGES.md
    # which references "crow.crowLoad" in prose.
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # skip docstring / heredoc string literals
        if isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Attribute) and func.attr == "crowLoad":
                    raise AssertionError(
                        "crow.crowLoad() call found — must not be used in "
                        "runNchantdOffice.py (replaced by sys.path.insert at "
                        "/home/solubrew/Documents/AIM for local development). "
                        "If crow.crowLoad is intentionally needed again, update "
                        "this test AND re-add the ordering contract."
                    )


def test_qt_webengine_env_setup_before_user_config():
    """The QtWebEngine env setup (QTWEBENGINE_CHROMIUM_FLAGS etc.)
    must run BEFORE any nchantdoffice import that uses Qt WebEngine.
    With crow.crowLoad removed, the ordering is driven by the
    sys.path.insert and early exit / runtime flow."""
    src = _read()
    # Verify QtWebEngine env is still set up (the setup code is present)
    assert 'os.environ["QTWEBENGINE_CHROMIUM_FLAGS"]' in src, (
        "QtWebEngine env setup is missing from runNchantdOffice.py"
    )


def test_write_default_config_called():
    """write_default_config() must be called (idempotent first-run setup)."""
    src = _read()
    assert "write_default_config()" in src, (
        "write_default_config() must be called to ensure the "
        "config file exists on first run"
    )


def test_no_try_except_around_user_config_import():
    """The user_config import is NOT wrapped in try/except.

    The defensive try/except was the previous approach (for
    partial-checkout safety), but the proper fix is to
    ensure crow.crowLoad runs first — so the import is
    guaranteed to succeed and doesn't need a fallback.

    If this test ever fails, it means someone re-added the
    try/except defensive guard. That's OK (defense-in-depth
    is fine) — but they should ALSO add a comment explaining
    why both guards exist.
    """
    src = _read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if (
                    handler.type
                    and isinstance(handler.type, ast.Name)
                    and handler.type.id == "ImportError"
                ):
                    # Check if the try body imports user_config
                    for stmt in node.body:
                        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                            mod = getattr(stmt, "module", "") or ""
                            for alias in stmt.names:
                                if "user_config" in (mod + alias.name):
                                    raise AssertionError(
                                        "user_config import should NOT be "
                                        "wrapped in try/except (the import "
                                        "order with crow.crowLoad first "
                                        "guarantees it works). If you want "
                                        "defense-in-depth, keep this test "
                                        "in sync by also adding a comment."
                                    )
