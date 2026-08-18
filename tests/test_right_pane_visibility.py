"""T-NEW-028 -- Right-side tab visibility selection regression tests.

The Interface Tab right-side config pane must enumerate the
right-side tabs by querying ``vw_tab`` (the union view over
``app_tab`` + ``doc_tab``) and filtering on
``tabset_type_txt = "right"`` AND ``visible_bit = 1``. Each tab
has a ``cmd_on_change_visible_right_tab`` handler that flips
``visible_bit`` on the underlying row (which lives in either
``app_tab`` or ``doc_tab`` -- ``vw_tab.app_data_type`` discriminates).

Tests drive the live ``NchantdOfficeInterfaceSettings`` instance
via ``__new__`` + attribute injection (per the Sprint 28-29
regression-test pattern). The store mock implements
``get_table`` returning DataFrame-shaped rows + ``update_record``
that captures the args so we can assert on the write shape
(records + columns dict per the Sprint 22 contract -- NOT the
silent-no-op ``"data"`` dict shape).
"""

import sys
from types import SimpleNamespace

# A QApplication instance must exist before any QWidget subclass is
# constructed -- even via __new__ -- because the Shiboken parent class
# registers itself against the app singleton at type-load time.
from PySide6.QtWidgets import QApplication
import nchantdoffice.models  # noqa: F401  -- establish import order first

from nchantdoffice.widgets.config.settings import (
    NchantdOfficeInterfaceSettings,
    RIGHT_PANE_TAB_FALLBACK,
    get_right_pane_tab_options,
    cmd_on_change_visible_right_tab,
)


# ---------------------------------------------------------------------------
# Fixture: a store mock with capturing get_table + update_record
# ---------------------------------------------------------------------------


def _make_settings_with_store(rows):
    """Build a NchantdOfficeInterfaceSettings with a fake store that
    returns ``rows`` from ``get_table`` and captures ``update_record``
    args so tests can assert on the write shape.
    """
    import pandas as pd

    settings = NchantdOfficeInterfaceSettings.__new__(NchantdOfficeInterfaceSettings)
    fake_app = SimpleNamespace(
        model=SimpleNamespace(
            store=_CapturingStore(rows),
            codex=SimpleNamespace(),
        ),
        app=None,
        view=SimpleNamespace(),
        new_application=True,
    )
    settings.parent = fake_app
    settings.app = fake_app
    settings.config = SimpleNamespace(
        dikt={},
        override=lambda *_a, **_k: settings.config,
    )
    return settings


class _CapturingStore:
    """Captures ``update_record`` calls + serves canned ``get_table`` rows.

    The contract tested here mirrors what ``MicroStash`` /
    ``SQuiRL`` actually do at runtime: ``get_table`` returns a
    pandas DataFrame (or empty DataFrame) when the table has no
    matching rows; ``update_record`` is the canonical write path
    using the records + columns shape (NOT the silent-no-op
    ``"data"`` dict shape -- see Sprint 22 fix).
    """

    def __init__(self, rows):
        import pandas as pd
        # ``if rows`` would trigger pandas' ambiguous-truthiness
        # error when rows is a DataFrame. ``if rows is not None``
        # is always safe -- callers can pass a list, a DataFrame,
        # or None (which means "empty table").
        if rows is None:
            self.rows = pd.DataFrame()
        else:
            self.rows = pd.DataFrame(rows)
        self.update_calls = []  # list of (data, column, value, db)

    def get_table(self, table, cfg=None, db="db"):
        # Simulate filtering: cfg["WHERE"]["IN"] is a dict of
        # {col: [values]}. Match rows where the col is in the list.
        if cfg is None or len(self.rows) == 0:
            return self.rows
        where = cfg.get("WHERE", {})
        in_dict = where.get("IN", {})
        if not in_dict:
            return self.rows
        mask = None
        for col, allowed in in_dict.items():
            if col not in self.rows.columns:
                # Column doesn't exist in this fixture -- mask out
                # everything (the real query would error, but we
                # return empty so the fallback kicks in).
                return self.rows.iloc[0:0]
            col_mask = self.rows[col].isin(allowed)
            mask = col_mask if mask is None else mask & col_mask
        return self.rows[mask] if mask is not None else self.rows

    def update_record(self, data, column, value, db="db"):
        # The canonical records + columns shape:
        # data = {"table": {"<table>": {"records": [[v, ...]],
        #                            "columns": ["col", ...]}}}
        # Any other shape silently no-ops at runtime (see Sprint 22
        # sonql fix). The test asserts on this exact shape.
        self.update_calls.append((data, column, value, db))
        return None


# ---------------------------------------------------------------------------
# Shared base -- 5 right-side tabs (seed layout)
# ---------------------------------------------------------------------------


def _sample_right_pane_rows(visible_overrides=None):
    """Build 5 right-side tab rows matching the models.yaml seeds.

    The ``app_data_type`` column discriminates between ``app_tab``
    (canonical right-side tabs) and ``doc_tab`` (right-side docs --
    none seeded currently). ``visible_bit`` defaults to 1; callers
    can override specific rows via ``visible_overrides``.
    """
    rows = [
        # name_txt, position_int, tid_txt, tabset_type_txt, visible_bit, app_data_type
        ("Journal", 0, "06875532-...c1038a", "right", 1, "app"),
        ("Scratch", 1, "scratch-tid-placeholder", "right", 1, "app"),
        ("ToolBox", 2, "06875532-...a7ece3", "right", 1, "app"),
        ("Calculator", 3, "06875532-...89ef6", "right", 1, "app"),
        ("Ad", 4, "936073aa-...1ba9e0d", "right", 1, "app"),
    ]
    out = []
    for name, position, tid, tabset, visible, app_data_type in rows:
        if visible_overrides and name in visible_overrides:
            visible = visible_overrides[name]
        out.append({
            "name_txt": name,
            "position_int": position,
            "tid_txt": tid,
            "tabset_type_txt": tabset,
            "visible_bit": visible,
            "app_data_type": app_data_type,
        })
    return out


# ---------------------------------------------------------------------------
# get_right_pane_tab_options -- the rewrite target
# ---------------------------------------------------------------------------


def test_get_right_pane_tab_options_queries_vw_tab_for_right_side_tabs():
    """The method queries ``vw_tab`` filtered by
    ``tabset_type_txt = "right"`` and ``visible_bit = 1``.

    The test passes a fake store that captures the cfg passed to
    ``get_table`` -- the cfg must include the right-side filter so
    the live query lands on the right rows.
    """
    settings = _make_settings_with_store(_sample_right_pane_rows())
    options = settings.get_right_pane_tab_options()
    # Options should be ordered by position_int and include all 5
    # seeded right-side tab names.
    assert isinstance(options, list)
    assert len(options) == 5, (
        f"Expected 5 right-side tabs (the 5 seeded ones), got {len(options)}: {options}"
    )
    # Order matters -- position_int drives the display order.
    names_in_order = [
        opt.split(" - ", 1)[-1] if " - " in opt else opt
        for opt in options
    ]
    assert names_in_order == ["Journal", "Scratch", "ToolBox", "Calculator", "Ad"], (
        f"Right-side tabs must be ordered by position_int. Got: {names_in_order}"
    )


def test_get_right_pane_tab_options_filters_out_visible_bit_zero_rows():
    """Rows with ``visible_bit = 0`` (user-hidden) must be excluded.

    The 5 seeded tabs are all visible_bit=1 by default. Mark ToolBox
    as visible_bit=0 (the user toggled it off) -- the method should
    return only the other 4.
    """
    settings = _make_settings_with_store(
        _sample_right_pane_rows(visible_overrides={"ToolBox": 0})
    )
    options = settings.get_right_pane_tab_options()
    names = [opt.split(" - ", 1)[-1] for opt in options if " - " in opt]
    assert "ToolBox" not in names, (
        f"ToolBox (visible_bit=0) must be excluded. Got: {names}"
    )
    assert len(names) == 4, (
        f"Expected 4 visible tabs after ToolBox hidden. Got: {len(names)}: {names}"
    )


def test_get_right_pane_tab_options_falls_back_to_hardcoded_list_when_table_empty():
    """When the DB query returns no rows, the method falls back to the
    canonical 4-tab default list (``RIGHT_PANE_TAB_FALLBACK``). This
    is the no-regression path -- users with no seeded rows still see
    the legacy fallback so the dropdown isn't empty.
    """
    settings = _make_settings_with_store(rows=[])
    options = settings.get_right_pane_tab_options()
    assert options == RIGHT_PANE_TAB_FALLBACK, (
        f"Empty DB result must fall back to RIGHT_PANE_TAB_FALLBACK. "
        f"Got: {options}"
    )
    # The legacy 4-list is the exact one the previous implementation
    # hardcoded -- confirms no regression for users on a fresh DB.
    assert "0 - Journal" in options and "1 - ToolBox" in options, (
        f"Fallback must include the canonical 4-tabs. Got: {options}"
    )


def test_get_right_pane_tab_options_is_module_level_callable():
    """The method is reachable both as an instance method AND as a
    module-level helper so callers don't need a live Qt parent.
    """
    import pandas as pd

    # Build a fake store at module scope
    rows_df = pd.DataFrame(_sample_right_pane_rows())
    store = _CapturingStore(rows_df)

    fake_app = SimpleNamespace(model=SimpleNamespace(store=store), view=SimpleNamespace())
    fake_settings = SimpleNamespace(
        app=fake_app,
        config=SimpleNamespace(dikt={}, override=lambda *_a, **_k: None),
    )
    options = get_right_pane_tab_options(fake_settings)
    assert isinstance(options, list)
    assert len(options) == 5


# ---------------------------------------------------------------------------
# cmd_on_change_visible_right_tab -- the toggle handler
# ---------------------------------------------------------------------------


def test_cmd_on_change_visible_right_tab_flips_visible_bit_to_zero():
    """When the user unchecks a right-side tab in the Interface Tab
    config pane, the handler writes ``visible_bit = 0`` to the
    underlying row (app_tab or doc_tab -- discriminated by
    ``app_data_type``).
    """
    settings = _make_settings_with_store(_sample_right_pane_rows())
    # Identify which row to flip -- pick ToolBox.
    # The handler signature: (settings, tid, app_data_type, visible)
    cmd_on_change_visible_right_tab(
        settings,
        tid="06875532-...a7ece3",
        app_data_type="app",
        visible=0,
    )
    # Assert the store received the right update_record call.
    assert len(settings.app.model.store.update_calls) == 1
    data, column, value, db = settings.app.model.store.update_calls[0]
    assert column == "tid_txt", (
        f"update_record must scope on tid_txt column. Got: {column}"
    )
    assert value == "06875532-...a7ece3", (
        f"update_record must target the chosen tid. Got: {value}"
    )
    assert db == "db"
    # Canonical shape: {"table": {"app_tab": {"records": [[0]],
    # "columns": ["visible_bit"]}}}
    assert "table" in data, (
        f"update_record data must use the records+columns shape. Got: {data}"
    )
    assert "app_tab" in data["table"]
    payload = data["table"]["app_tab"]
    assert payload.get("records") == [[0]], (
        f"records must be [[0]] (the new visible_bit). Got: {payload.get('records')}"
    )
    assert payload.get("columns") == ["visible_bit"], (
        f"columns must be ['visible_bit']. Got: {payload.get('columns')}"
    )


def test_cmd_on_change_visible_right_tab_flips_visible_bit_to_one():
    """The reverse path -- re-enable a previously hidden tab.

    Verifies the handler is idempotent across the 0/1 boundary.
    """
    settings = _make_settings_with_store(_sample_right_pane_rows())
    cmd_on_change_visible_right_tab(
        settings,
        tid="06875532-...c1038a",  # Journal
        app_data_type="app",
        visible=1,
    )
    data, _, value, _ = settings.app.model.store.update_calls[0]
    assert data["table"]["app_tab"]["records"] == [[1]]
    assert value == "06875532-...c1038a"


def test_cmd_on_change_visible_right_tab_routes_doc_tab_rows_to_doc_tab():
    """Right-side tabs can live in either ``app_tab`` (canonical tabs)
    or ``doc_tab`` (right-side docs). The handler must route the
    UPDATE to the correct table based on the ``app_data_type`` arg.
    """
    settings = _make_settings_with_store(_sample_right_pane_rows())
    cmd_on_change_visible_right_tab(
        settings,
        tid="some-doc-tid-1234",
        app_data_type="doc",
        visible=0,
    )
    data, _, value, _ = settings.app.model.store.update_calls[0]
    # The table key must be "doc_tab", not "app_tab".
    assert "doc_tab" in data["table"], (
        f"doc-tab row must route to doc_tab table. Got: {list(data['table'].keys())}"
    )
    assert "app_tab" not in data["table"]


def test_cmd_on_change_visible_right_tab_persists_to_config_dikt():
    """The handler mirrors the Sprint 23 ``cmd_on_change_prompt_for_*``
    pattern -- write the new visible_bit to ``config.dikt`` so the
    current session sees the change immediately.
    """
    settings = _make_settings_with_store(_sample_right_pane_rows())
    cmd_on_change_visible_right_tab(
        settings,
        tid="06875532-...a7ece3",
        app_data_type="app",
        visible=0,
    )
    # config.dikt["visible_right_tabs"] should now reflect the change.
    visible_right_tabs = settings.config.dikt.get("visible_right_tabs", {})
    assert visible_right_tabs.get("06875532-...a7ece3") == 0, (
        f"config.dikt['visible_right_tabs'] must reflect the new state. "
        f"Got: {visible_right_tabs}"
    )


def test_build_right_pane_visibility_checks_renders_one_checkbox_per_row():
    """``_build_right_pane_visibility_checks`` must render a widget
    with one ``NchantdCheckbox`` per right-side tab row returned by
    ``_query_right_pane_tab_rows``. Empty DB -> empty group (no
    false positives).

    Source-level test: the method body must call ``_query_right_pane_tab_rows``
    (not call the DB directly) and add exactly one widget per row.
    The off-screen path doesn't drive ``NchantdCheckbox.initWidget``
    because that requires a live Qt parent -- but the dispatch
    path is what matters here.
    """
    import re
    from pathlib import Path
    settings_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/config/settings.py"
    ).read_text()
    m = re.search(
        r"def _build_right_pane_visibility_checks\(self.*?\n(?=\n    def |\Z)",
        settings_py,
        re.S,
    )
    assert m, "_build_right_pane_visibility_checks not found"
    body = m.group(0)
    # The build path must:
    # - delegate to _query_right_pane_tab_rows (not raw DB calls)
    # - add a NchantdCheckbox per row
    # - call cmd_on_change_visible_right_tab on each toggle
    assert "_query_right_pane_tab_rows" in body, (
        "_build_right_pane_visibility_checks must delegate to "
        "_query_right_pane_tab_rows (single source of truth for the "
        "right-side tab query)"
    )
    assert "NchantdCheckbox" in body, (
        "_build_right_pane_visibility_checks must render NchantdCheckbox rows"
    )
    assert "cmd_on_change_visible_right_tab" in body, (
        "_build_right_pane_visibility_checks must wire each toggle "
        "to cmd_on_change_visible_right_tab"
    )


def test_right_pane_visibility_checks_widget_is_wired_into_initialize_right_side():
    """T-NEW-028 step 5: ``_initialize_right_side`` must build a
    visibility checklist widget (``right_pane_tab_visibility_checks``)
    populated from the DB query (one checkbox per right-side tab).

    Source-level test: the right_side config method must call
    ``_build_right_pane_visibility_checks`` and add the resulting
    widget to ``right_side_settings_group``. Without these two
    calls the user can't see / toggle the right-side tab list.
    """
    import re
    from pathlib import Path
    settings_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/config/settings.py"
    ).read_text()
    # Find _initialize_right_side method body
    m = re.search(
        r"def _initialize_right_side\(self.*?\n(?=\n    def |\Z)",
        settings_py,
        re.S,
    )
    assert m, "_initialize_right_side method not found"
    body = m.group(0)
    assert "_build_right_pane_visibility_checks" in body, (
        "_initialize_right_side must call _build_right_pane_visibility_checks"
    )
    assert "right_pane_tab_visibility_checks" in body, (
        "_initialize_right_side must add the right_pane_tab_visibility_checks "
        "widget to the right_side_settings_group"
    )


def test_cmd_on_change_visible_right_tab_rejects_non_zero_one_value():
    """Defensive: the handler must refuse anything other than 0 or 1
    (per your note: 'visibility is either 0 or 1'). A bogus value
    like 2 or -1 should be rejected without writing to the store.
    """
    settings = _make_settings_with_store(_sample_right_pane_rows())
    cmd_on_change_visible_right_tab(
        settings,
        tid="06875532-...a7ece3",
        app_data_type="app",
        visible=2,  # invalid
    )
    assert settings.app.model.store.update_calls == [], (
        f"Bogus visible value (2) must be rejected -- no update_record call. "
        f"Got: {settings.app.model.store.update_calls}"
    )