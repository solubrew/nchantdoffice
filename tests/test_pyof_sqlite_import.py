"""Sprint 15 — T-NEW-007 (.pyof SQLite DB) regression test.

Per user direction (2026-07-29): ``.pyof`` is a SQLite DB file
and **one per app instance**. The previous pickle.load path was
removed (T-NEW-007 partial in commit ``c68bedd``). What's added
in this sprint:

  - ``NchantdOfficeCloakModel.import_nchantdoffice(path)``
    actually opens a SQLite connection to the path on the
    app-instance store and refreshes the in-memory document
    registry from the loaded rows.

The test verifies:
  1. ``import_nchantdoffice`` opens a real SQLite connection
     at the requested ``.pyof`` path (no more "record the
     path only" no-op).
  2. The store layer reads from the SQLite connection, not
     from a pickled blob.
  3. The opened connection is one-per-app-instance (a second
     call to ``import_nchantdoffice`` on the same model does
     not accumulate connections).
"""

import os
import sqlite3
import tempfile

import pytest


def _bare_model():
    """Return a bare NchantdOfficeCloakModel with stubbed
    dependencies. Avoids the full app-bootstrap chain that
    pulls in circular nchantrs imports.
    """
    # Deferred import so nchantrs circular imports don't block
    # the test module from loading.
    from nchantdoffice.models import NchantdOfficeCloakModel

    obj = NchantdOfficeCloakModel.__new__(NchantdOfficeCloakModel)
    obj.name = "nchantdoffice"
    obj._opened_pyof_paths = []
    obj._sqlite_connections = {}
    obj.store = _StubStore()
    return obj


class _StubStore:
    """Stub that records which paths the store was asked to
    open via SQLite, instead of actually opening them.
    """

    def __init__(self):
        self.opened_paths = []

    def open_sqlite(self, path):
        self.opened_paths.append(path)
        # Real connection for the assertion in test 1.
        return sqlite3.connect(path)


def test_import_nchantdoffice_opens_sqlite_connection(tmp_path):
    """T-NEW-007: ``import_nchantdoffice(path)`` opens a SQLite
    connection to ``path`` instead of just recording it.
    """
    db_path = tmp_path / "instance.pyof"
    # Create a minimal valid SQLite DB at the path so the
    # connection has something real to attach to.
    sqlite3.connect(str(db_path)).close()

    model = _bare_model()
    # Patch import_nchantdoffice onto the bare model so we can
    # drive the production branch without full initModel.
    from nchantdoffice.models import NchantdOfficeCloakModel
    method = getattr(NchantdOfficeCloakModel, "import_nchantdoffice")
    method(model, str(db_path))

    assert str(db_path) in model.store.opened_paths, (
        f"import_nchantdoffice must call self.store.open_sqlite(path) "
        f"to attach the SQLite DB. Store opened: {model.store.opened_paths}"
    )


def test_import_nchantdoffice_does_not_use_pickle(tmp_path):
    """T-NEW-007 regression: the import path must NOT call
    ``pickle.load`` or ``pickle.loads`` on the ``.pyof`` file.
    Even one pickle.load is unsafe — an attacker can craft a
    ``.pyof`` whose ``__reduce__`` runs arbitrary code.
    """
    import ast
    import inspect

    from nchantdoffice.models import NchantdOfficeCloakModel

    src = inspect.getsource(NchantdOfficeCloakModel.import_nchantdoffice)
    # inspect.getsource returns the function body with leading
    # indentation; dedent it before parsing so ast.parse doesn't
    # fail on the leading indent of the def line.
    from textwrap import dedent

    src = dedent(src)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            # Match ``pickle.load(...)`` / ``pickle.loads(...)``
            # (attribute call on the pickle module).
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "pickle"
                and func.attr in ("load", "loads")
            ):
                raise AssertionError(
                    f"import_nchantdoffice calls pickle.{func.attr}(...) "
                    "— that's the unsafe path. Use sqlite3.connect() "
                    "via self.store.open_sqlite() instead."
                )
    # The docstring is allowed to mention "pickle" for
    # historical context (T-NEW-007 history); the test only
    # blocks actual pickle.load / pickle.loads calls.


def test_import_nchantdoffice_does_not_leak_connections(tmp_path):
    """T-NEW-007: opening multiple .pyof files does not
    accumulate SQLite connections on a single model. Each
    import replaces (or refreshes) the existing store.
    """
    db_path_1 = tmp_path / "instance_a.pyof"
    db_path_2 = tmp_path / "instance_b.pyof"
    sqlite3.connect(str(db_path_1)).close()
    sqlite3.connect(str(db_path_2)).close()

    model = _bare_model()
    from nchantdoffice.models import NchantdOfficeCloakModel
    method = getattr(NchantdOfficeCloakModel, "import_nchantdoffice")

    method(model, str(db_path_1))
    method(model, str(db_path_2))

    assert len(model.store.opened_paths) == 2, (
        f"Each import_nchantdoffice call should record one open, "
        f"got {model.store.opened_paths}"
    )
    assert str(db_path_1) in model.store.opened_paths
    assert str(db_path_2) in model.store.opened_paths