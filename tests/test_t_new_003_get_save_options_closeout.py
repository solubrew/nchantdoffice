"""T-NEW-003 closeout — get_save_options / get_save_value land the canonical save_mode contract.

The T-NEW-003 card (save_mode toggle UI + dispatch) shipped in
Sprint 14 (commit b3d8ff8 — "feat(documents): expose save_mode
dropdown in TabEdit Pane (T-NEW-003 d/e)"). The canonical contract
established then:

- Default: ``self.save_mode = "file_path"`` (documents.py:84)
- Three modes: ``file_path`` (on-disk file is source of truth),
  ``to_dict`` (canonical Pyffice serialization persisted; on-disk
  file unchanged), ``both`` (file + DB both written)
- Persistence round-trips through ``self.document.config.dikt["save_mode"]``
  and ``self.config.dikt["save_mode"]`` (documents.py:106-119)

The two helpers in ``panes/documents.py``:

  - ``get_save_options(self) -> list[str]`` at line 1010
  - ``get_save_value(self) -> str`` at line 1017

…are deferred-body stubs returning hardcoded:

  - ``["Local File System"]`` (line 1013, with the other 4
    options commented out at line 1015)
  - ``"Local File System"`` (line 1019, with `# PUSHT` typo in
    the marker)

…which is the **pre-T-NEW-003 schema** (5 storage backends
including "NchantdOffice Primary", "NchantdOffice Instance",
"Cloud File System", "In-Sync"). T-NEW-003 replaced that with
the 3-mode toggle; the deferred body in panes/documents.py
never caught up.

This commit lands the canonical contract — the helpers
return the live 3-mode list and the thread-through config
value (with `file_path` default), exactly matching
``documents.py:84`` and the persistence order at
``documents.py:106-119``.

Tests are AST-source structural (mirroring the established
pattern from T-NEW-117 / T-NEW-148 / T-NEW-161 / T-NEW-162 /
T-NEW-163 / T-NEW-165) because ``panes/documents.py`` imports
PySide6 / nchantrs widgets on module import.
"""

import ast
from pathlib import Path


PANES_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/panes/documents.py"
)


def _function_source(name: str) -> str:
    tree = ast.parse(PANES_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"{name} not found")


def test_get_save_options_returns_three_canonical_modes():
    """``get_save_options`` returns the T-NEW-003 3-mode list.

    Canonical modes per documents.py:84 + b3d8ff8: ``"file_path"``,
    ``"to_dict"``, ``"both"``. The pre-fix body returned
    ``["Local File System"]`` (the obsolete 5-backend schema).
    Note: ``ast.unparse`` normalises string quotes — Python's
    literal ``"file_path"`` becomes ``'file_path'`` when
    parsed-then-unparsed. Assert on the apostrophe form (the
    canonical ast form) AND on the string content (the post-fix
    body returns ``["file_path", "to_dict", "both"]``).
    """
    source = _function_source("get_save_options")
    for mode in ("file_path", "to_dict", "both"):
        assert mode in source, (
            f"get_save_options must return the canonical T-NEW-003 "
            f"mode list including '{mode}'. Pre-fix body had only "
            f"'Local File System' (the obsolete 5-backend schema)."
        )


def test_get_save_value_reads_save_mode_config():
    """``get_save_value`` reads from the save_mode config (with fallback)."""
    source = _function_source("get_save_value")
    assert "save_mode" in source, (
        "get_save_value must read save_mode from the config (per "
        "documents.py:84 + :118). Pre-fix body returned the "
        'hardcoded string "Local File System".'
    )
    assert "file_path" in source, (
        "get_save_value must default to 'file_path' (the canonical "
        "default per documents.py:84)."
    )


def test_get_save_value_no_longer_hardcoded_local_file_system():
    """``get_save_value`` no longer returns the obsolete hardcoded value.

    The obsolete return was `return "Local File System"`. After
    the fix, the return shape should depend on self.document /
    self.config (look for getattr + .get() or .dikt access).
    Note: ``ast.unparse`` normalises string quotes — Python's
    literal `"Local File System"` becomes `'Local File System'`
    when parsed-then-unparsed. Assert on the apostrophe form.
    """
    source = _function_source("get_save_value")
    assert "return 'Local File System'" not in source, (
        "get_save_value must NOT hard-return 'Local File System' "
        "(the ast-normalised form of the obsolete value) — that "
        "was the pre-T-NEW-003 schema (5 backends). The canonical "
        "default is 'file_path'; value derives from "
        "self.document.config.dikt['save_mode'] with fallback."
    )


def test_get_save_options_no_longer_hardcoded():
    """``get_save_options`` body no longer returns the obsolete hardcoded list.

    The docstring legitimately mentions 'Local File System' as
    historical reference. Check the body shape: a single
    return statement that lists the canonical modes (file_path /
    to_dict / both) and does NOT include 'Local File System'.
    """
    source = _function_source("get_save_options")
    # Walk the AST to extract the return statement (not the
    # docstring Expr).
    tree = ast.parse(source)
    return_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Return):
            return_node = node
            break
    assert return_node is not None, (
        "get_save_options must have a return statement."
    )
    # The return value should be a List of 3 string constants.
    assert isinstance(return_node.value, ast.List), (
        f"get_save_options must return a list literal; got {ast.dump(return_node.value)}."
    )
    literals = [
        elt.value for elt in return_node.value.elts
        if isinstance(elt, ast.Constant)
    ]
    assert "Local File System" not in literals, (
        "get_save_options must NOT include 'Local File System' in "
        "the returned list (obsolete pre-T-NEW-003 schema)."
    )
    assert set(literals) == {"file_path", "to_dict", "both"}, (
        f"get_save_options must return exactly the canonical "
        f"T-NEW-003 3-mode list {{'file_path', 'to_dict', 'both'}}; "
        f"got {sorted(literals)}."
    )


def test_no_pushht_marker_remains():
    """The literal ``# PUSHT to 0.0.3`` typo marker is gone."""
    import re

    src = PANES_PATH.read_text()
    matches = re.findall(r"#\s*PUSHT\s+to", src)
    assert not matches, (
        f"panes/documents.py:1019 still has the '# PUSHT to 0.0.3' "
        f"typo marker (matches: {matches}). T-NEW-003 closeout "
        f"should drop it."
    )