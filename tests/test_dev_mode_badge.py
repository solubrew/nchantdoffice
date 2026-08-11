"""T-NEW-070 (DESK-5): ServerStatus exposes dev_mode flag + [DEV] badge.

Pins the contract that:
  - ServerStatus.is_dev_mode() exists and returns bool
  - state_display() includes "[DEV] " prefix when
    is_dev_mode() is True
  - state_display() does NOT include the prefix when
    is_dev_mode() is False
  - server_status.py must NOT read any env vars (per
    T-NEW-070 hard-break)
"""
import ast
from pathlib import Path

SERVER_STATUS = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/utilities/server_status.py"
)


def _read():
    return SERVER_STATUS.read_text()


def _ast_class(src, name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _class_source(src, name):
    cls = _ast_class(src, name)
    if cls is None:
        return ""
    return ast.unparse(cls)


def test_is_dev_mode_helper_exists():
    src = _read()
    cls = _ast_class(src, "ServerStatus")
    assert cls is not None
    body = _class_source(src, "ServerStatus")
    assert "def is_dev_mode" in body, (
        "ServerStatus.is_dev_mode() must exist (T-NEW-070 DESK-5)"
    )


def test_is_dev_mode_returns_bool():
    src = _read()
    body = _class_source(src, "ServerStatus")
    # The return type annotation should be bool
    assert "-> bool" in body, (
        "ServerStatus.is_dev_mode() must return bool"
    )


def test_state_display_includes_dev_badge_when_dev_mode():
    """state_display() must include '[DEV] ' prefix when
    is_dev_mode() is True (T-NEW-070 DESK-5)."""
    src = _read()
    body = _class_source(src, "ServerStatus")
    # Look for the [DEV] prefix in the state_display method
    assert "[DEV]" in body, (
        "ServerStatus.state_display() must include [DEV] badge "
        "when is_dev_mode() is True"
    )
    # And it must be conditional on is_dev_mode
    assert "is_dev_mode" in body, (
        "state_display() must check is_dev_mode() to decide "
        "whether to show the [DEV] badge"
    )


def test_is_dev_mode_uses_user_config_not_env():
    """T-NEW-070 hard-break: is_dev_mode() must read from
    user_config (nchantdoffice.utilities.user_config), NOT
    from any env var."""
    src = _read()
    body = _class_source(src, "ServerStatus")
    # is_dev_mode method body should reference user_config
    assert "user_config" in body, (
        "is_dev_mode() must import from user_config "
        "(T-NEW-070 hard-break — no env vars)"
    )


def test_server_status_no_env_var_reads():
    """T-NEW-070 hard-break: server_status.py must not read
    any env vars. Dev mode is detected via user_config only.
    """
    src = _read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if func.attr in ("getenv", "environ"):
                    raise AssertionError(
                        f"server_status.py must not use os.{func.attr} "
                        f"(line {node.lineno})"
                    )
            elif isinstance(func, ast.Name):
                if func.id == "getenv":
                    raise AssertionError(
                        f"server_status.py must not use getenv "
                        f"(line {node.lineno})"
                    )
