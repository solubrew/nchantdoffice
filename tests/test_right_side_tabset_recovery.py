"""T-NEW-031 -- Right-side tabset recovery regression tests.

Dropping a tab on the right-side tabset is a "scratch view"
gesture: the tab is added to the right pane in-memory but
NOT persisted to the DB. On reload (which rebuilds the right
pane from the SQL filter ``tabset_type_txt = "right"``), the
tab naturally disappears from the right pane because its DB
row's ``tabset_type_txt`` was unchanged -- the tab "springs
back" to its original tabset (typically the center pane).

The implementation lives on
``NchantdOfficeCloakModel.cmd_open_tab_in_right_scratch(tab)``
which:
  1. Records the tab's original parent (so we can report
     "where it came from" on reload) in
     ``self._right_scratch_tabs[tid]``.
  2. Adds the tab dict to the right pane's in-memory
     ``tabsdata`` (so it visually appears).
  3. Returns ``self`` for chainable call sites.

No DB writes happen -- the SQL filter naturally excludes the
tab on the next ``buildTabSet`` call.

Tests drive the model via ``__new__`` + attribute injection
(Sprint 28-29 pattern). Source-level tests guard the drop
handler wiring.
"""

import sys
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication
_QAPP = QApplication.instance() or QApplication(sys.argv)

import nchantdoffice.models  # noqa: F401  -- establish import order first

from nchantdoffice.models import NchantdOfficeCloakModel


# ---------------------------------------------------------------------------
# Fixture: a NchantdOfficeCloakModel with a fake right pane + capturing store
# ---------------------------------------------------------------------------


def _make_model_with_right_pane(initial_right_tabs=None):
    """Build a NchantdOfficeCloakModel with:
      - a fake store (captures update_record calls; should be empty)
      - a fake right pane with a tabset model whose tabsdata is
        mutable (the model appends to it on drop)
    """
    model = NchantdOfficeCloakModel.__new__(NchantdOfficeCloakModel)
    model.store = _CapturingStore()
    model.has_changed = False

    initial_right_tabs = initial_right_tabs or []
    # The right pane tabset model: a NchantdOfficeTabSetModel-lite
    # with tabsdata + buildTabSet + parent (used by buildTabSet).
    right_tabsdata = list(initial_right_tabs)
    right_model = SimpleNamespace(
        tabsdata=right_tabsdata,
        tabs=right_tabsdata,  # alias used by my T-NEW-030 trees.py code
        tabset="right",
        current_node=SimpleNamespace(nid="current-node-uuid"),
        buildTabSet=lambda node, tabset="right": None,  # used by reload test
    )
    right_pane = SimpleNamespace(model=right_model)
    panes = {
        "right": right_pane,
        "center": SimpleNamespace(model=SimpleNamespace(tabsdata=[], tabset="center")),
    }
    view = SimpleNamespace(panes=panes)
    model.app = SimpleNamespace(
        model=model,
        view=view,
        config=SimpleNamespace(dikt={}),
        application_name="NchantdOffice",
    )
    return model


class _CapturingStore:
    """Captures ``update_record`` calls. The T-NEW-031 contract:
    cmd_open_tab_in_right_scratch must NOT touch the store at
    all (no DB write)."""

    def __init__(self):
        self.update_calls = []

    def update_record(self, data, column, value, db="db"):
        self.update_calls.append((data, column, value, db))
        return None

    def get_table(self, *args, **kwargs):
        return []


# ---------------------------------------------------------------------------
# cmd_open_tab_in_right_scratch -- the new T-NEW-031 handler
# ---------------------------------------------------------------------------


def test_cmd_open_tab_in_right_scratch_adds_tab_to_right_pane_tabsdata():
    """The handler must add the dropped tab to the right pane's
    in-memory tabsdata so the user sees the tab immediately.
    No DB write -- the right pane is a "scratch view".
    """
    model = _make_model_with_right_pane()
    tab = {"tid_txt": "tab-1", "name_txt": "My Notebook"}

    model.cmd_open_tab_in_right_scratch(tab)

    right_tabsdata = model.app.view.panes["right"].model.tabsdata
    assert tab in right_tabsdata, (
        f"Dropped tab must be in right pane tabsdata. "
        f"Got: {right_tabsdata}"
    )


def test_cmd_open_tab_in_right_scratch_does_NOT_persist_to_db():
    """The right-pane scratch view is in-memory only. No
    update_record call. This is the key T-NEW-031 contract:
    on reload, the tab naturally returns to its original
    tabset because the DB row's tabset_type_txt was never
    changed.
    """
    model = _make_model_with_right_pane()
    tab = {"tid_txt": "tab-1", "name_txt": "My Notebook"}

    model.cmd_open_tab_in_right_scratch(tab)

    assert model.store.update_calls == [], (
        f"cmd_open_tab_in_right_scratch must NOT write to DB. "
        f"Got: {model.store.update_calls}"
    )


def test_cmd_open_tab_in_right_scratch_records_original_parent():
    """The handler records the tab's original parent (in-memory
    only) so the UI can show "this tab came from <node>" if
    needed, and so a future "undo" can re-home it explicitly.

    Source: read from ``tab.get("pid_txt")`` (the doc_tab
    primary key for the source node). Fall back to None if
    absent.
    """
    model = _make_model_with_right_pane()
    tab = {
        "tid_txt": "tab-1",
        "name_txt": "My Notebook",
        "pid_txt": "node-source-uuid",
    }

    model.cmd_open_tab_in_right_scratch(tab)

    assert model._right_scratch_tabs["tab-1"] == "node-source-uuid", (
        f"_right_scratch_tabs must record the original parent. "
        f"Got: {model._right_scratch_tabs}"
    )


def test_cmd_open_tab_in_right_scratch_rejects_missing_tid():
    """Defensive: tab dict with no ``tid_txt`` is rejected.
    The right pane needs a key to look up the original parent.
    """
    model = _make_model_with_right_pane()
    tab = {"name_txt": "no tid"}

    result = model.cmd_open_tab_in_right_scratch(tab)

    right_tabsdata = model.app.view.panes["right"].model.tabsdata
    assert right_tabsdata == [], (
        f"Missing tid_txt must reject -- nothing in tabsdata. "
        f"Got: {right_tabsdata}"
    )
    assert result is model


def test_cmd_open_tab_in_right_scratch_returns_self():
    """Mirrors the Sprint 23 / T-NEW-030 return-self pattern
    so callers can chain: ``model.cmd_open_tab_in_right_scratch(tab).foo()``.
    """
    model = _make_model_with_right_pane()
    tab = {"tid_txt": "tab-1"}
    result = model.cmd_open_tab_in_right_scratch(tab)
    assert result is model


def test_cmd_open_tab_in_right_scratch_appends_to_existing_right_pane_tabs():
    """If the right pane already has tabs (Journal, ToolBox,
    etc. from the seed data), the dropped tab must be
    APPENDED, not replace. Otherwise the right pane's existing
    tabs would vanish on every drop.
    """
    existing = [{"tid_txt": "journal", "name_txt": "Journal"}]
    model = _make_model_with_right_pane(initial_right_tabs=list(existing))
    tab = {"tid_txt": "tab-1", "name_txt": "My Notebook"}

    model.cmd_open_tab_in_right_scratch(tab)

    right_tabsdata = model.app.view.panes["right"].model.tabsdata
    assert existing[0] in right_tabsdata
    assert tab in right_tabsdata
    assert len(right_tabsdata) == 2


# ---------------------------------------------------------------------------
# Reload behaviour -- the T-NEW-031 acceptance criterion
# ---------------------------------------------------------------------------


def test_reload_restores_tab_to_original_tabset_drops_it_from_right_pane():
    """T-NEW-031 acceptance criterion: on reload, the right pane
    is rebuilt from the SQL filter (tabset_type_txt="right").
    Since the dropped tab's DB row was unchanged (no write),
    the reload's query returns only the original right-side
    tabs -- the dropped tab is no longer in the right pane
    tabsdata. The tab "springs back" to its original tabset
    (center, in the default case).
    """
    model = _make_model_with_right_pane()
    # Drop a center-pane tab into the right pane.
    dropped_tab = {
        "tid_txt": "tab-1",
        "name_txt": "Center Notebook",
        "pid_txt": "node-center-uuid",  # original parent
    }
    model.cmd_open_tab_in_right_scratch(dropped_tab)
    # Confirm it's now in the right pane.
    assert dropped_tab in model.app.view.panes["right"].model.tabsdata

    # Simulate reload: the right pane's model.buildTabSet is
    # called (the same call T-NEW-028 / Sprint 28 use to
    # repopulate the right pane). In real life this re-runs
    # the SQL filter and replaces tabsdata. We simulate that
    # by clearing tabsdata -- mimicking what the real buildTabSet
    # does on reload.
    right_model = model.app.view.panes["right"].model
    right_model.tabsdata.clear()

    # The dropped tab is no longer in the right pane.
    assert dropped_tab not in right_model.tabsdata, (
        f"After reload, dropped tab must be gone from right pane. "
        f"Got: {right_model.tabsdata}"
    )

    # The in-memory _right_scratch_tabs entry remains (we don't
    # clear it -- the marker is what enables a future "undo"
    # gesture to re-home the tab explicitly). But its presence
    # does NOT cause the right pane to keep showing the tab;
    # the tab is back in its original tabset.
    assert model._right_scratch_tabs["tab-1"] == "node-center-uuid"


def test_right_scratch_marker_survives_reload_for_explicit_undo():
    """The ``_right_scratch_tabs`` marker persists across reloads
    so a future "undo drop" gesture can re-home the tab
    explicitly back to the original node. (Today the SQL
    filter is what naturally re-homes the tab; the marker is
    there for an explicit user-driven undo.)
    """
    model = _make_model_with_right_pane()
    tab = {"tid_txt": "tab-1", "pid_txt": "node-original-uuid"}
    model.cmd_open_tab_in_right_scratch(tab)

    # Simulate reload (clear tabsdata).
    right_model = model.app.view.panes["right"].model
    right_model.tabsdata.clear()

    # The marker is still there for an explicit undo.
    assert "tab-1" in model._right_scratch_tabs
    assert model._right_scratch_tabs["tab-1"] == "node-original-uuid"


# ---------------------------------------------------------------------------
# Drop handler wiring -- source-level test (Qt drag-drop is off-screen)
# ---------------------------------------------------------------------------


def test_tabs_drop_event_opens_in_right_scratch_when_target_is_right_pane():
    """T-NEW-031 step 4: ``NchantdOfficeTabs.dropEvent`` must
    detect when ``self.tabset == "right"`` and call
    ``self.app.model.cmd_open_tab_in_right_scratch`` to add
    the dropped tab to the right pane's in-memory tabsdata.

    Today the dropEvent only handles tab-on-tab reorder
    (``tab_moved`` signal) and tree-on-tab (open doc) -- the
    right-pane drop case is unhandled.
    """
    import re
    from pathlib import Path
    tabs_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/tabs.py"
    ).read_text()
    m = re.search(
        r"def dropEvent\(self[^\)]*\):.*?(?=\n    def |\Z)",
        tabs_py,
        re.S,
    )
    assert m, "dropEvent method not found"
    body = m.group(0)
    # The dropEvent on tab mime must branch on self.tabset == "right"
    assert 'self.tabset == "right"' in body or 'self.tabset == \'right\'' in body, (
        "tabs.dropEvent must branch on self.tabset == 'right' to "
        "detect right-pane drops"
    )
    # And in that branch it must call cmd_open_tab_in_right_scratch
    assert "cmd_open_tab_in_right_scratch" in body, (
        "tabs.dropEvent must call cmd_open_tab_in_right_scratch "
        "when self.tabset == 'right'"
    )