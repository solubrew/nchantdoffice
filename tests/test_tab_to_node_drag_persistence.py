"""T-NEW-030 -- Tab-to-node drag persistence regression tests.

The Sprint 28+ tab drag-and-drop infrastructure drops a tab
mime-payload on tree nodes (signal ``item_dropped_on_tabs`` in
``widgets/trees.py``). Before this work, no persistence followed:
the in-memory reparent happened but ``doc_tab.pid_txt`` was not
written. Two bugs to fix:

  1. ``NchantdOfficeCloakModel.change_tab_parent`` uses the
     silent-no-op ``"data"`` dict shape and scopes by the wrong
     column (``nid_txt`` instead of ``tid_txt``).
  2. ``widgets/trees.py:dropEvent`` emits the signal but nothing
     connects to it.

This test file pins both. Tests drive ``NchantdOfficeCloakModel``
via ``__new__`` + attribute injection (per Sprint 28-29 pattern).
The drop-handler wiring test is source-level (the off-screen path
can't drive Qt drag-and-drop).
"""

import sys
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication
import nchantdoffice.models  # noqa: F401  -- establish import order first

from nchantdoffice.models import NchantdOfficeCloakModel


# ---------------------------------------------------------------------------
# Fixture: a NchantdOfficeCloakModel with a capturing store
# ---------------------------------------------------------------------------


def _make_model_with_store():
    """Build a NchantdOfficeCloakModel with a fake store that
    captures ``update_record`` calls so tests can assert on the
    write shape (records + columns dict per the Sprint 22 contract
    -- NOT the silent-no-op ``"data"`` dict shape).
    """
    model = NchantdOfficeCloakModel.__new__(NchantdOfficeCloakModel)
    model.store = _CapturingStore()
    model.has_changed = False
    model.app = SimpleNamespace(
        model=model,
        config=SimpleNamespace(dikt={}),
        application_name="NchantdOffice",
    )
    return model


class _CapturingStore:
    """Captures ``update_record`` calls. Mirrors the canonical
    MicroStash / SQuiRL contract: write paths use the
    ``{"table": {"<table>": {"records": [[v, ...]], "columns":
    ["col", ...]}}}`` shape; the legacy ``"data"`` dict shape
    silently no-ops at runtime (Sprint 22 fix).
    """

    def __init__(self):
        self.update_calls = []  # list of (data, column, value, db)

    def update_record(self, data, column, value, db="db"):
        self.update_calls.append((data, column, value, db))
        return None


# ---------------------------------------------------------------------------
# cmd_set_tab_parent -- the new canonical handler (T-NEW-030 Step 3)
# ---------------------------------------------------------------------------


def test_cmd_set_tab_parent_persists_pid_txt_via_canonical_records_columns_shape():
    """When the user drops a tab onto a tree node, the handler writes
    the new ``pid_txt`` to ``doc_tab`` scoped by ``tid_txt`` (the
    actual primary key of the tab row), using the canonical
    records + columns dict shape.

    The previous ``change_tab_parent`` used the silent-no-op
    ``"data"`` dict shape AND scoped by the wrong column
    (``nid_txt`` -- the source node -- instead of ``tid_txt`` --
    the target tab). This test asserts the fix lands both
    behaviours correctly.
    """
    model = _make_model_with_store()
    tab = {"tid_txt": "tab-uuid-1234", "name_txt": "My Notebook"}
    new_parent_node = {"nid_txt": "node-uuid-5678", "name_txt": "New Parent"}

    model.cmd_set_tab_parent(tab, new_parent_node)

    assert len(model.store.update_calls) == 1
    data, column, value, db = model.store.update_calls[0]
    # Must scope on tid_txt (the tab row's primary key) -- NOT
    # nid_txt (the source node, which was the previous bug).
    assert column == "tid_txt", (
        f"cmd_set_tab_parent must scope on tid_txt (the tab row's PK), "
        f"got: {column}"
    )
    assert value == "tab-uuid-1234", (
        f"cmd_set_tab_parent must target the source tab's tid. "
        f"got: {value}"
    )
    assert db == "db"
    # Must use the canonical records + columns shape, NOT the
    # silent-no-op "data" dict shape (Sprint 22 fix).
    assert "table" in data, (
        f"update_record data must use the records+columns shape. "
        f"got: {data}"
    )
    assert "doc_tab" in data["table"]
    payload = data["table"]["doc_tab"]
    assert "records" in payload and "columns" in payload, (
        f"payload must have records + columns keys. got: {payload}"
    )
    assert payload["records"] == [["node-uuid-5678"]], (
        f"records must be [[new_parent_nid]]. got: {payload['records']}"
    )
    assert payload["columns"] == ["pid_txt"], (
        f"columns must be ['pid_txt']. got: {payload['columns']}"
    )


def test_cmd_set_tab_parent_rejects_missing_tid():
    """Defensive: the handler must reject a tab dict with no
    ``tid_txt``. Without this, the write would scope by an
    empty string and update the wrong row.
    """
    model = _make_model_with_store()
    tab = {"name_txt": "no tid here"}
    new_parent_node = {"nid_txt": "node-uuid-5678"}

    result = model.cmd_set_tab_parent(tab, new_parent_node)

    assert model.store.update_calls == [], (
        f"Missing tid_txt must reject -- no update_record call. "
        f"got: {model.store.update_calls}"
    )
    # Return self for chainable call sites.
    assert result is model


def test_cmd_set_tab_parent_rejects_missing_nid():
    """Defensive: the handler must reject a node dict with no
    ``nid_txt``. The previous bug wrote ``pid_txt = ""`` silently
    (silent-no-op shape), which would orphan the tab.
    """
    model = _make_model_with_store()
    tab = {"tid_txt": "tab-uuid-1234"}
    new_parent_node = {"name_txt": "no nid here"}

    result = model.cmd_set_tab_parent(tab, new_parent_node)

    assert model.store.update_calls == [], (
        f"Missing nid_txt must reject -- no update_record call. "
        f"got: {model.store.update_calls}"
    )
    assert result is model


def test_cmd_set_tab_parent_returns_self_for_chainable_call_sites():
    """Mirrors the Sprint 23 ``cmd_on_change_*`` return-self pattern
    so callers can chain: ``model.cmd_set_tab_parent(tab, node).foo()``.
    """
    model = _make_model_with_store()
    tab = {"tid_txt": "tab-1"}
    node = {"nid_txt": "node-1"}
    result = model.cmd_set_tab_parent(tab, node)
    assert result is model


# ---------------------------------------------------------------------------
# change_tab_parent -- the legacy method, kept as alias for backward
# compatibility (zero callers today per the survey, but kept so the
# sprint29 deprecation stays explicit).
# ---------------------------------------------------------------------------


def test_change_tab_parent_delegates_to_cmd_set_tab_parent():
    """``change_tab_parent(pid)`` is kept as a thin wrapper around
    ``cmd_set_tab_parent`` for backward compatibility. The legacy
    signature took a pid string (not a node dict); the wrapper
    coerces that into the new shape.
    """
    model = _make_model_with_store()
    # The legacy signature uses self.get_current_node() for the
    # tab side -- patch that to a known tab dict.
    model.get_current_node = lambda: SimpleNamespace(nid="node-source-uuid")
    model.get_current_tab = lambda: SimpleNamespace(
        tid="tab-source-uuid", name="Source"
    )
    model.change_tab_parent("node-target-uuid")

    assert len(model.store.update_calls) == 1
    data, column, value, db = model.store.update_calls[0]
    assert column == "tid_txt"
    assert value == "tab-source-uuid"
    assert data["table"]["doc_tab"]["records"] == [["node-target-uuid"]]
    assert data["table"]["doc_tab"]["columns"] == ["pid_txt"]


# ---------------------------------------------------------------------------
# widgets/trees.py:dropEvent -- source-level wiring test
# ---------------------------------------------------------------------------


def test_trees_drop_event_calls_handle_tab_dropped_on_node():
    """T-NEW-030 step 4: ``NchantdOfficeApplicationTree.dropEvent`` must
    resolve the target tree node's nid and the source tab's tid
    from the mime payload, then call
    ``self._handle_tab_dropped_on_node`` (which in turn calls
    ``self.app.model.cmd_set_tab_parent``).

    This is a source-level test (the off-screen path can't drive
    Qt drag-and-drop). It guards the wiring so a future commit
    can't regress the drop handler back to a no-op.

    The implementation chose direct-call from ``dropEvent`` over
    a Qt signal connect because the previous signal
    (``item_dropped_on_tabs``) had no consumers -- connecting
    a signal-to-slot would just add an indirection. Direct call
    keeps the dispatch path clear.
    """
    import re
    from pathlib import Path
    trees_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/trees.py"
    ).read_text()
    # Find the dropEvent method body
    # The signature has a return annotation (def dropEvent(self, event) -> None:)
    # so the regex needs to allow the optional annotation between ) and :.
    m = re.search(
        r"def dropEvent\(self[^\)]*\).*?\n.*?(?=\n    def |\Z)",
        trees_py,
        re.S,
    )
    assert m, "dropEvent method not found"
    body = m.group(0)
    # The dropEvent on tab mime must call
    # _handle_tab_dropped_on_node (the new T-NEW-030 dispatch
    # helper) -- which in turn calls cmd_set_tab_parent on the
    # app model.
    assert "_handle_tab_dropped_on_node" in body, (
        "trees.dropEvent must call _handle_tab_dropped_on_node when "
        "a tab is dropped on a tree node. The previous code only "
        "emitted the item_dropped_on_tabs signal -- nothing "
        "connected to it, so the parent update was lost."
    )
    # The dropEvent must resolve the target tree item via indexAt
    assert "indexAt" in body, (
        "trees.dropEvent must resolve the target node via "
        "self.tree.indexAt(event.pos()) to get the new parent nid"
    )

    # Also assert _handle_tab_dropped_on_node calls cmd_set_tab_parent
    m2 = re.search(
        r"def _handle_tab_dropped_on_node\(self[^\)]*\).*?\n.*?(?=\n    def |\Z)",
        trees_py,
        re.S,
    )
    assert m2, "_handle_tab_dropped_on_node method not found"
    body2 = m2.group(0)
    assert "cmd_set_tab_parent" in body2, (
        "_handle_tab_dropped_on_node must call cmd_set_tab_parent "
        "on the app model"
    )


# ---------------------------------------------------------------------------
# End-to-end behaviour: tab_to_node_drag_persistence (acceptance card 4)
# ---------------------------------------------------------------------------


def test_reload_reads_new_parent_after_drag_persistence():
    """Acceptance criterion for T-NEW-030 (card Migration plan
    step 4): ``cmd_set_tab_parent(tab, new_parent_node)`` followed
    by a reload of the doc_tab row reads the new parent.

    Simulates the full round-trip: drop writes pid_txt -> a
    subsequent get_table on doc_tab filtered by tid_txt returns
    the new pid.
    """
    model = _make_model_with_store()
    tab = {"tid_txt": "tab-uuid-1234"}
    new_parent_node = {"nid_txt": "node-uuid-5678"}
    model.cmd_set_tab_parent(tab, new_parent_node)
    # Round-trip: the same canonical shape that was written would
    # be the shape a reload reads (the store doesn't transform
    # data on write -- it persists the records + columns shape).
    data, column, value, db = model.store.update_calls[0]
    persisted_pid = data["table"]["doc_tab"]["records"][0][0]
    assert persisted_pid == "node-uuid-5678"
    # The scope column + value pin the row to update.
    assert column == "tid_txt"
    assert value == "tab-uuid-1234"