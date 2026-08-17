"""T-NEW-142 regression: Tab Delete button works from both surfaces.

**Tab Delete button not working from document toolbar or from
NchantdTabPane in the toolbox.**

The button-bar config at ``widgets/panes/documents.py:791`` and
``widgets/panes/documents.py:93`` registers the ``delete_tab`` and
``delete_node`` actions. The lookup chain in
``nchantrs.utilities.utils.lookup`` reads the
``app_action`` table from the database, indexed by
``lookup_code_txt``. If the lookup code is missing from the
seed yaml (``nchantdoffice/_data_/models.yaml``), the lookup
raises ``Exception('Action <name> Lookup Config is Empty')``
and the button bar fails to render.

Root cause: ``nchantdoffice/_data_/models.yaml`` only registers
ONE ``app_action`` row (``import_pyof``). The 8+ actions
referenced from the document-pane buttonbars (``delete_tab``,
``delete_node``, ``sort_children_ascending``,
``sort_children_descending``, ``duplicate_document``,
``import_document``, ``export_document``, ``take_snapshot``,
``create_dataset``, ``unlock_view``, ``lock_view``) are all
missing. The Delete buttons in particular never render.

The fix:
1. Add ``app_action`` records for ``delete_tab`` and
   ``delete_node`` (the two buttons in the testing-report
   Issue 2 scope) to ``nchantdoffice/_data_/models.yaml`` so
   they exist in the seed YAML and propagate into the
   runtime ``app_action`` table.
2. Optionally extend the schema to the remaining missing
   actions (``sort_children_*``, ``duplicate_document``,
   etc.) but those are out of scope for T-NEW-142; their
   fixes belong in a follow-up card.
3. Test surface: ``tests/test_t_new_142_tab_delete_action.py``
   (this file) -- source-level pin that the yaml record
   exists, and a behavioural check that ``lookup(app,
   'delete_tab')`` returns the config (i.e. does NOT raise
   "Lookup Config is Empty").

Migration plan (no priority / low priority -- design decision
first): the existing single record format is preserved
(squirl record list: ``[code_group, lookup_code, name,
description, UUID, icon, short_cut, tip, advanced_tip,
widget, parameters]``). The icon paths match the existing
convention (``nchantrs/_data_/*.svg`` for stock icons like
``delete``, ``delete-document``).

Steps:
1. Add RED tests (this file) asserting that
   ``models.yaml`` contains ``delete_tab`` and ``delete_node``
   ``app_action`` records, and that ``lookup(...)`` returns a
   populated config for both.
2. Verify RED fails (lookup raises "Lookup Config is Empty"
   for delete_tab / delete_node).
3. Add the two records to ``models.yaml``.
4. Verify GREEN (lookup returns icon + tip, no exception).
"""
import inspect
import sqlite3
import tempfile
from pathlib import Path

# T-NEW-074 Task 9: keep Qt on the headless offscreen platform
# before any PySide6 import so the integration test does not
# need a real display.
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

# The seed yaml -> app_action population is a runtime operation
# (sonql migration + write). For these tests we directly
# construct a minimal in-memory ``app_action`` table and
# populate it with whatever rows the seed yaml declares. This
# isolates the test from the full app boot.


def _read_seed_records(yaml_path: Path) -> list[list]:
    """Read the seed ``app_action`` records from
    ``nchantdoffice/_data_/models.yaml``. Returns the inner
    ``records:`` block as a list of list-of-strings.
    """
    import yaml
    text = yaml_path.read_text()
    data = yaml.safe_load(text)
    # Walk the yaml tree:
    # NchantdOfficeCloakModel.dstruct.database.objects.table.app_action.records
    # (Models are keyed by class name at the top level.)
    records = []
    for top_key, top_val in (data or {}).items():
        if not isinstance(top_val, dict):
            continue
        records = (
            top_val.get("dstruct", {})
            .get("database", {})
            .get("objects", {})
            .get("table", {})
            .get("app_action", {})
            .get("records", [])
        )
        if records:
            break
    return records


def _seed_action_db(tmp_path: Path, records: list[list]) -> sqlite3.Connection:
    """Build an in-memory SQLite with an ``app_action`` table and
    insert the given records. Returns the connection."""
    db_path = tmp_path / "seed.pyof"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE app_action ("
        "code_group_txt TEXT,"
        "lookup_code_txt TEXT,"
        "name_txt TEXT,"
        "description_ltxt TEXT,"
        "UUID TEXT,"
        "icon_txt TEXT,"
        "short_cut_txt TEXT,"
        "tip_txt TEXT,"
        "advanced_tip_txt TEXT,"
        "widget_txt TEXT,"
        "parameters_dict TEXT"
        ")"
    )
    for rec in records:
        # Pad short records to the expected 11-column shape.
        padded = list(rec) + [""] * (11 - len(rec))
        conn.execute(
            "INSERT INTO app_action VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            padded[:11],
        )
    conn.commit()
    return conn


def _lookup_in_db(conn: sqlite3.Connection, action: str) -> dict | None:
    """Mimic ``nchantrs.utilities.utils.lookup``: SELECT WHERE
    code_group_txt='base' AND lookup_code_txt=action, return the
    first row as a dict, or None if missing."""
    cur = conn.execute(
        "SELECT code_group_txt, lookup_code_txt, name_txt,"
        "       description_ltxt, UUID, icon_txt, short_cut_txt,"
        "       tip_txt, advanced_tip_txt, widget_txt, parameters_dict "
        "FROM app_action "
        "WHERE code_group_txt = 'base' AND lookup_code_txt = ? "
        "LIMIT 1",
        (action,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "code_group_txt": row[0],
        "lookup_code_txt": row[1],
        "name_txt": row[2],
        "description_ltxt": row[3],
        "UUID": row[4],
        "icon_txt": row[5],
        "short_cut_txt": row[6],
        "tip_txt": row[7],
        "advanced_tip_txt": row[8],
        "widget_txt": row[9],
        "parameters_dict": row[10],
    }


# ---------------------------------------------------------------------------
# Source-level pins: the seed yaml must contain delete_tab / delete_node
# ---------------------------------------------------------------------------

REPO_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
MODELS_YAML = REPO_ROOT / "nchantdoffice" / "_data_" / "models.yaml"


def test_models_yaml_registers_delete_tab_action():
    """T-NEW-142: ``nchantdoffice/_data_/models.yaml`` must register
    a ``delete_tab`` ``app_action`` row so the Tab Delete button
    in the document toolbar (and the NchantdTabPane toolbox)
    can resolve its icon + tip + handler.

    Without this row the lookup raises
    ``Exception('Action delete_tab Lookup Config is Empty')`` and
    the button bar fails to render.
    """
    records = _read_seed_records(MODELS_YAML)
    lookup_codes = [r[1] for r in records]
    assert "delete_tab" in lookup_codes, (
        f"nchantdoffice/_data_/models.yaml must register a "
        f"'delete_tab' app_action row (T-NEW-142). "
        f"Current lookup codes: {lookup_codes}"
    )


def test_models_yaml_registers_delete_node_action():
    """T-NEW-142 (sibling): ``delete_node`` must also be
    registered for symmetry with delete_tab (both are referenced
    from ``panes/documents.py`` button-bar configs).
    """
    records = _read_seed_records(MODELS_YAML)
    lookup_codes = [r[1] for r in records]
    assert "delete_node" in lookup_codes, (
        f"nchantdoffice/_data/ models.yaml must register a "
        f"'delete_node' app_action row (T-NEW-142). "
        f"Current lookup codes: {lookup_codes}"
    )


def test_delete_tab_record_has_icon_and_tip():
    """The delete_tab row must carry an icon_txt and tip_txt so
    the rendered button has a visible glyph + tooltip. The
    nchantrs convention is to reference a stock SVG by name
    (e.g. 'delete' / 'delete-document'); the runtime resolves
    the full path through the icon pipeline.
    """
    records = _read_seed_records(MODELS_YAML)
    for rec in records:
        if len(rec) > 1 and rec[1] == "delete_tab":
            icon = rec[5] if len(rec) > 5 else ""
            tip = rec[7] if len(rec) > 7 else ""
            assert icon, (
                f"delete_tab app_action row must have a non-empty "
                f"icon_txt; got {icon!r}"
            )
            assert tip, (
                f"delete_tab app_action row must have a non-empty "
                f"tip_txt; got {tip!r}"
            )
            return
    pytest.fail("delete_tab row not found in models.yaml")


# ---------------------------------------------------------------------------
# Behavioural pin: lookup returns the config (does not raise Empty)
# ---------------------------------------------------------------------------

def test_lookup_returns_delete_tab_config(tmp_path):
    """T-NEW-142 (e2e): when the app_action table contains a
    ``delete_tab`` row, the nchantrs lookup contract returns
    its config dict -- it does NOT raise
    ``Action delete_tab Lookup Config is Empty``. This is the
    exact failure mode the testing report described: the button
    silently does not appear (the lookup raised, the bar failed
    to render).

    The seed records flow through the sonql migration into the
    runtime app_action table verbatim; we mimic that shape.
    """
    records = _read_seed_records(MODELS_YAML)
    assert records, "models.yaml must declare at least one app_action row"
    conn = _seed_action_db(tmp_path, records)

    row = _lookup_in_db(conn, "delete_tab")
    conn.close()
    assert row is not None, (
        "lookup('delete_tab') must return a config dict; missing "
        "app_action row in models.yaml causes the button bar to "
        "fail (T-NEW-142)."
    )
    # And it must be a non-empty row (icon + tip + handler
    # plumbing present).
    assert row["icon_txt"], "delete_tab row must carry an icon_txt"
    assert row["tip_txt"], "delete_tab row must carry a tip_txt"


def test_lookup_returns_delete_node_config(tmp_path):
    """T-NEW-142 (sibling e2e): same as the delete_tab test but
    for ``delete_node``.
    """
    records = _read_seed_records(MODELS_YAML)
    conn = _seed_action_db(tmp_path, records)
    row = _lookup_in_db(conn, "delete_node")
    conn.close()
    assert row is not None, (
        "lookup('delete_node') must return a config dict; missing "
        "app_action row in models.yaml causes the button bar to "
        "fail (T-NEW-142)."
    )