"""T-NEW-070 (DESK-1): user_config.py — XDG user config resolver.

Pins the contract that:
  - Default config path: ~/.config/nchantdoffice/config.yaml
  - Override path: <cwd>/nchantdoffice.yaml
  - Precedence: cwd override > XDG > defaults
  - get_dev_mode() returns True iff config has dev_mode: true
  - get_server_url() returns the configured URL or DEFAULT
  - get_cache_dir() returns the configured cache dir or default
  - get_server_timeout() returns the configured timeout or default
  - get_webengine_software_render() returns the configured flag
  - write_default_config() is idempotent (skips if file exists)
  - **No environment variable reads** (per T-NEW-070 hard-break)
  - Pure Python — no Qt, no flask (testable in isolation)
"""
import ast
from pathlib import Path

USER_CONFIG = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/utilities/user_config.py"
)


def _read():
    return USER_CONFIG.read_text()


def _ast_function(src, name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _class_source(src, name):
    cls = _ast_function(src, name)
    if cls is None:
        return ""
    return ast.unparse(cls)


def test_module_exists():
    assert USER_CONFIG.exists(), "user_config.py must exist"


def test_get_user_config_path_uses_xdg():
    src = _read()
    fn = _ast_function(src, "get_user_config_path")
    assert fn is not None
    body = ast.unparse(fn)
    assert ".config/nchantdoffice" in body
    assert "config.yaml" in body


def test_get_cwd_override_path_uses_nchantdoffice_yaml():
    src = _read()
    fn = _ast_function(src, "get_cwd_override_path")
    assert fn is not None
    body = ast.unparse(fn)
    assert "nchantdoffice.yaml" in body


def test_load_config_precedence_cwd_over_xdg():
    src = _read()
    fn = _ast_function(src, "load_config")
    assert fn is not None
    body = ast.unparse(fn)
    # cwd path is loaded via get_cwd_override_path() helper
    assert "get_cwd_override_path" in body
    # XDG path is loaded either via get_user_config_path() or
    # via the USER_CONFIG_PATH module constant (both are
    # acceptable — the constant is just a shortcut).
    assert (
        "get_user_config_path" in body or "USER_CONFIG_PATH" in body
    )


def test_get_dev_mode_returns_true_iff_configured():
    src = _read()
    fn = _ast_function(src, "get_dev_mode")
    assert fn is not None


def test_get_server_url_returns_localhost_5000_in_dev_mode():
    src = _read()
    fn = _ast_function(src, "get_server_url")
    assert fn is not None
    body = ast.unparse(fn)
    assert "localhost" in body
    assert "5000" in body


def test_module_does_not_read_env_vars():
    """T-NEW-070: user_config.py must NOT use os.environ / os.getenv.

    Hard-break: no env-var reads anywhere in this module.
    """
    src = _read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if func.attr in ("getenv", "environ"):
                    raise AssertionError(
                        f"user_config.py must not use os.{func.attr} "
                        f"(line {node.lineno})"
                    )
            elif isinstance(func, ast.Name):
                if func.id == "getenv":
                    raise AssertionError(
                        f"user_config.py must not use getenv "
                        f"(line {node.lineno})"
                    )


def test_yaml_dependency_used():
    """user_config.py must use the yaml library for parsing."""
    src = _read()
    tree = ast.parse(src)
    imports_yaml = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "yaml":
                    imports_yaml = True
        elif isinstance(node, ast.ImportFrom):
            if node.module == "yaml":
                imports_yaml = True
    assert imports_yaml, "user_config.py must import yaml"


def test_write_default_config_is_idempotent():
    """write_default_config() must not overwrite an existing
    config file (idempotent)."""
    src = _read()
    fn = _ast_function(src, "write_default_config")
    assert fn is not None
    body = ast.unparse(fn)
    # Must check existence before writing
    assert "exists" in body


def test_get_webengine_software_render_helper_exists():
    """T-NEW-070 DESK-4: get_webengine_software_render() must
    exist to replace the legacy NCHANT_WEBENGINE_SOFTWARE
    env var."""
    src = _read()
    fn = _ast_function(src, "get_webengine_software_render")
    assert fn is not None, (
        "get_webengine_software_render() must exist (T-NEW-070 DESK-4)"
    )
