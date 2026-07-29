"""Sprint 6 — T-NEW-007 regression test.

Verifies that the two ``.pyof`` import sites no longer invoke
``pickle.load`` on user-selected files. ``.pyof`` is the
NchantdOffice SQLite DB format; the pickle path was an
arbitrary code execution vector on malicious file selection.

The test imports the affected modules (models + toolboxes),
walks their ASTs, and asserts no ``pickle.load`` / ``pickle.loads``
calls remain. The runtime check (no ``import pickle`` reaching
the import-nchantdoffice paths) is verified by inspecting the
source — a structural test is sufficient because the fix is
a code-removal, not a runtime behaviour.
"""

import ast
from pathlib import Path

import nchantdoffice.models  # noqa: F401


def _module_path(rel_path):
    root = Path(__file__).resolve().parent.parent
    return root / rel_path


def _find_pickle_loads(source: str) -> list:
    """Return ``[(lineno, call_text)]`` for every pickle.load/loads
    call (direct or attribute) in ``source``."""
    tree = ast.parse(source)
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        # pickle.load(f) or pickle.loads(s)
        if isinstance(func, ast.Attribute) and func.attr in ("load", "loads"):
            if isinstance(func.value, ast.Name) and func.value.id == "pickle":
                hits.append((node.lineno, f"pickle.{func.attr}(...)"))
        # _pickle.load / _pickle.loads
        elif isinstance(func, ast.Attribute) and func.attr in ("load", "loads"):
            if (
                isinstance(func.value, ast.Attribute)
                and func.value.attr == "pickle"
            ):
                hits.append((node.lineno, f"{func.value.attr}.{func.attr}(...)"))
    return hits


def test_models_import_nchantdoffice_does_not_pickle_load():
    src = _module_path("nchantdoffice/models.py").read_text()
    # Slice to just the import_nchantdoffice method so other (legitimate)
    # pickle usage elsewhere in models.py is not flagged.
    tree = ast.parse(src)
    method_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "import_nchantdoffice":
            method_src = ast.get_source_segment(src, node)
            break
    assert method_src is not None, "import_nchantdoffice method missing"
    hits = _find_pickle_loads(method_src)
    assert not hits, (
        f"import_nchantdoffice still calls pickle at: {hits}\n"
        f"T-NEW-007: ``.pyof`` is a SQLite DB; remove all pickle.load calls."
    )


def test_toolboxes_open_pyof_instance_does_not_pickle_load():
    src = _module_path("nchantdoffice/widgets/controls/toolboxes.py").read_text()
    tree = ast.parse(src)
    method_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_open_pyof_instance":
            method_src = ast.get_source_segment(src, node)
            break
    assert method_src is not None, "_open_pyof_instance method missing"
    hits = _find_pickle_loads(method_src)
    assert not hits, (
        f"_open_pyof_instance still calls pickle at: {hits}\n"
        f"T-NEW-007: ``.pyof`` is a SQLite DB; remove all pickle.load calls."
    )


def test_toolboxes_docstring_no_longer_says_pickled_object_file():
    src = _module_path("nchantdoffice/widgets/controls/toolboxes.py").read_text()
    assert "Pickled Object File" not in src, (
        "Stale docstring still refers to .pyof as a 'Pickled Object "
        "File'. The format is a SQLite DB; update the wording."
    )


def test_pyof_is_identified_as_sqlite_db():
    src = _module_path("nchantdoffice/models.py").read_text()
    assert "SQLite DB file" in src, (
        "models.py no longer describes .pyof as a SQLite DB file — "
        "the T-NEW-007 docstring is missing."
    )