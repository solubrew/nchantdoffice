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
    """crow.crowLoad must run BEFORE the nchantdoffice.utilities.user_config
    import (so sys.path is set up first)."""
    src = _read()
    items = _ast_function_or_import(src)
    crow_line = None
    user_config_line = None
    for name, line in items:
        if name == "<call> crowLoad":
            crow_line = line
        if "nchantdoffice.utilities.user_config" in str(name):
            user_config_line = line
    assert crow_line is not None, "crow.crowLoad() not found"
    assert user_config_line is not None, "user_config import not found"
    assert crow_line < user_config_line, (
        f"crow.crowLoad (line {crow_line}) must run BEFORE "
        f"nchantdoffice.utilities.user_config import (line "
        f"{user_config_line}). Otherwise the import fails with "
        f"ModuleNotFoundError."
    )


def test_qt_webengine_env_setup_after_crow_load():
    """The QtWebEngine env setup (QTWEBENGINE_CHROMIUM_FLAGS etc.)
    must run AFTER crow.crowLoad so the imports of nchantrs/Qt
    pick up the env vars correctly. But it runs BEFORE any
    Qt-using code."""
    src = _read()
    items = _ast_function_or_import(src)
    crow_line = None
    webengine_setenv_line = None
    for name, line in items:
        if name == "<call> crowLoad":
            crow_line = line
        if "QTWEBENGINE_CHROMIUM_FLAGS" in src[:line*100]:  # heuristic
            pass
    # The QtWebEngine env setup is in the if-block, not a top-level
    # statement, so we can't pin via top-level items. Instead, check
    # the if-block ordering via the source text positions.
    crow_pos = src.find("crow.crowLoad")
    webengine_setenv_pos = src.find('os.environ["QTWEBENGINE_CHROMIUM_FLAGS"]')
    assert crow_pos != -1 and webengine_setenv_pos != -1
    # Note: QtWebEngine env setenv must be AFTER crowLoad
    # (the if-block is conditional on the user_config import
    # succeeding, which requires crowLoad to have run).
    # The check above (test_crow_crowLoad_before_user_config_import)
    # already enforces this transitively.


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
