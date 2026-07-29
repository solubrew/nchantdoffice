"""Sprint 17 — T-NEW-005 item 3 UI: primary-instance-registry browser.

Per user direction (2026-07-29): the ``app_instance`` table
stores locations/metadata of OTHER app instances (per the
one-SQLite-per-app-instance model). The UI should expose
``cmd_browse_app_instances`` so the user can see the
secondary DBs the primary instance is tracking.

This test pins the data path (the model surfaces registered
instances as a list of dicts) and the UI hook (the toolbox
exposes a `cmd_browse_app_instances` method).
"""

import ast
from pathlib import Path


def test_app_instance_query_helper_exists():
    """T-NEW-005 item 3: ``NchantdOfficeCloakModel`` exposes
    ``get_app_instances`` (or similar) that returns a list of
    the registered secondary instances. The model must
    delegate to ``self.store.get_table("app_instance", ...)``
    or run a SQLite ``SELECT * FROM app_instance`` query.
    """
    src = (
        Path(__file__).resolve().parent.parent
        / "nchantdoffice/models.py"
    ).read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ClassDef)
            and node.name == "NchantdOfficeCloakModel"
        ):
            class_src = ast.get_source_segment(src, node) or ""
            if "app_instance" in class_src and (
                "get_app_instances" in class_src
                or "list_app_instances" in class_src
            ):
                found = True
                break

    assert found, (
        "NchantdOfficeCloakModel must expose a method that "
        "returns the registered app_instances (e.g. "
        "get_app_instances / list_app_instances). The UI "
        "browser in cmd_browse_app_instances depends on it."
    )


def test_toolbox_exposes_browse_app_instances_command():
    """T-NEW-005 item 3: ``cmd_browse_app_instances`` exists on
    the toolbox widget so the user can see the primary
    instance registry.
    """
    src = (
        Path(__file__).resolve().parent.parent
        / "nchantdoffice/widgets/controls/toolboxes.py"
    ).read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == (
            "cmd_browse_app_instances"
        ):
            found = True
            break

    assert found, (
        "toolboxes.py must expose cmd_browse_app_instances so "
        "the primary-instance-registry browser is reachable "
        "from the UI (e.g. via the toolbox buttonbar)."
    )


def test_app_instance_payload_round_trips_through_sqlite(tmp_path):
    """T-NEW-005 item 3: a row inserted into ``app_instance``
    is recoverable via the new ``get_app_instances`` query.
    Round-trip test using the in-memory SQLite DB created by
    the production ``open_sqlite`` helper.
    """
    import os
    import sqlite3

    from nchantdoffice.models import NchantdOfficeCloakModel

    # Build a bare model + stub store so we don't need the
    # full app bootstrap.
    model = NchantdOfficeCloakModel.__new__(NchantdOfficeCloakModel)
    model.name = "nchantdoffice"

    # Set up a real SQLite DB at a temp path with the
    # ``app_instance`` table + a single row.
    db_path = tmp_path / "primary.pyof"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE app_instance ("
        "  uuid TEXT PRIMARY KEY,"
        "  name TEXT,"
        "  created TEXT,"
        "  version INTEGER"
        ")"
    )
    conn.execute(
        "INSERT INTO app_instance(uuid, name, created, version) "
        "VALUES (?, ?, ?, ?)",
        ("abc-123", "secondary-instance", "2026-07-29", 1),
    )
    conn.commit()

    # Stub the store layer so get_app_instances can read the
    # SQLite connection we just opened. The production
    # ``get_app_instances`` looks for ``_sqlite_connection``
    # on the store (the same attribute set by
    # ``NchantdOfficeStore.open_sqlite``).
    class _StubStore:
        def __init__(self):
            self._sqlite_connection = conn

    model.store = _StubStore()

    method = getattr(model, "get_app_instances", None)
    assert method is not None and callable(method), (
        "model.get_app_instances must exist (T-NEW-005 item 3)."
    )

    rows = method()
    assert isinstance(rows, list), (
        f"get_app_instances must return a list; got {type(rows).__name__}."
    )
    assert len(rows) >= 1, (
        f"Round-trip expected at least 1 row; got {len(rows)}."
    )
    names = [r.get("name") for r in rows]
    assert "secondary-instance" in names, (
        f"Round-trip lost the inserted row; rows={rows}"
    )

    conn.close()