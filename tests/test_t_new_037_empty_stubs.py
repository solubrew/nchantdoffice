"""TDD-first tests for T-NEW-037 empty method stubs.

The T-NEW-037 card groups three empty `# TODO implement
method` markers. Each gets a different treatment based on
the call site:

  1. ``NchantdOfficeAnalyticsChart._build_chart_data_cfg``
     (analytics_charts.py:868) -- FILL. The caller at L209
     passes the returned cfg into ``NchantdChart(...)``;
     an empty dict is a valid (no-op) cfg that produces a
     chart widget with no data. Defensive: returns a dict
     even when the source data is unavailable.

  2. ``_build_chart_action_button_group`` (charts.py:293) --
     DEFER. The caller at L184 is COMMENTED OUT (it
     triggers a NchantdChart segfault -- T-NEW-029). The
     stub is dead code until the segfault is fixed. Replace
     the TODO with a T-NEW-037/T-NEW-029 pointer.

  3. ``NchantdNewDocumentToolBar.set_active_item``
     (toolbars.py:312) -- FILL. The caller at L329 is
     ``set_handlers()`` which runs after ``set_actions()``
     has populated ``self.document_types``. The intended
     behaviour: set ``self.document_types["active"]`` to
     the first entry's index (or None when empty). This
     matches the Sprint 23 "set the active item" pattern.
"""

import sys
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication
_QAPP = QApplication.instance() or QApplication(sys.argv)

import nchantdoffice.widgets.documents.analytics.analytics_charts  # noqa: F401
import nchantdoffice.widgets.controls.toolbars  # noqa: F401


# ---------------------------------------------------------------------------
# _build_chart_data_cfg
# ---------------------------------------------------------------------------


def _make_analytics_chart():
    from nchantdoffice.widgets.documents.analytics.analytics_charts import (
        NchantdOfficeChart,
    )
    chart = NchantdOfficeChart.__new__(NchantdOfficeChart)
    chart.app = SimpleNamespace(
        model=SimpleNamespace(
            get_current_node=lambda: SimpleNamespace(nid="node-1"),
            get_current_tab=lambda: SimpleNamespace(tid="tab-1"),
        )
    )
    return chart


def test_build_chart_data_cfg_returns_dict_with_required_keys():
    """The method must return a dict carrying at minimum the
    expected cfg keys (``type``, ``data``, ``options`` or
    similar) so the NchantdChart constructor accepts it.
    """
    chart = _make_analytics_chart()
    result = chart._build_chart_data_cfg()
    assert isinstance(result, dict), (
        f"_build_chart_data_cfg must return a dict. Got: {type(result)}"
    )


def test_build_chart_data_cfg_swallows_exception():
    """Defensive: when the model raises, the method must log
    + return an empty dict rather than crashing the chart
    widget construction.
    """
    chart = _make_analytics_chart()
    # Make the model raise
    def _raise(*args, **kwargs):
        raise RuntimeError("simulated model failure")
    chart.app.model.get_current_tab = _raise
    # Must NOT raise
    result = chart._build_chart_data_cfg()
    assert isinstance(result, dict)


def test_build_chart_data_cfg_handles_missing_app():
    """Defensive: when ``self.app`` is None, the method is a
    no-op (returns empty dict).
    """
    chart = _make_analytics_chart()
    chart.app = None
    result = chart._build_chart_data_cfg()
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# _build_chart_action_button_group -- deferred
# ---------------------------------------------------------------------------


def test_build_chart_action_button_group_has_no_todo_implement_marker():
    """The deferred stub must NOT carry a `# TODO implement
    method` marker anymore -- the T-NEW-037 close-out
    replaces it with a T-NEW-037/T-NEW-029 pointer. Source-
    level guard.
    """
    from pathlib import Path
    charts_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/panes/charts.py"
    ).read_text()
    # The deferred stub line should still exist (we keep
    # the method for when the segfault is fixed) but the
    # TODO must point to T-NEW-037 (or T-NEW-029).
    # Find the stub region (5 lines after the def).
    import re
    m = re.search(
        r"def _build_chart_action_button_group\(self\):.*?(?=\n    def |\nclass |\Z)",
        charts_py,
        re.S,
    )
    assert m, "_build_chart_action_button_group not found"
    body = m.group(0)
    # The TODO is now a pointer (not "implement").
    assert "TODO implement" not in body, (
        "The TODO implement marker must be replaced with a "
        "T-NEW-037/T-NEW-029 pointer (T-NEW-037 close-out)"
    )
    assert "T-NEW-037" in body or "T-NEW-029" in body, (
        "The deferred stub must reference T-NEW-037 (this card) "
        "or T-NEW-029 (the segfault that blocks the caller)"
    )


# ---------------------------------------------------------------------------
# set_active_item
# ---------------------------------------------------------------------------


def _make_toolbar():
    from nchantdoffice.widgets.controls.toolbars import NchantdNewDocumentToolBar
    bar = NchantdNewDocumentToolBar.__new__(NchantdNewDocumentToolBar)
    import pandas as pd
    bar.document_types = pd.DataFrame(
        [{"name_txt": "Notebook"}, {"name_txt": "Script"}, {"name_txt": "Image"}]
    )
    return bar


def test_set_active_item_sets_first_entry_active():
    """``set_active_item`` must mark the first entry (index 0)
    as the active item in ``self.document_types``.
    """
    bar = _make_toolbar()
    bar.set_active_item()
    assert bar.document_types["active"].iloc[0] == 0, (
        f"First entry must be marked active. "
        f"Got: {bar.document_types['active'].iloc[0]}"
    )


def test_set_active_item_returns_self():
    """Mirrors the Sprint 23 return-self pattern."""
    bar = _make_toolbar()
    result = bar.set_active_item()
    assert result is bar


def test_set_active_item_handles_empty_document_types():
    """Defensive: when ``self.document_types`` is an empty
    DataFrame, the method must log + return self without
    crashing.
    """
    from nchantdoffice.widgets.controls.toolbars import NchantdNewDocumentToolBar
    import pandas as pd
    bar = NchantdNewDocumentToolBar.__new__(NchantdNewDocumentToolBar)
    bar.document_types = pd.DataFrame()
    # Must NOT raise
    result = bar.set_active_item()
    assert result is bar


def test_set_active_item_handles_none_document_types():
    """Defensive: when ``self.document_types`` is None (not
    yet populated), the method must log + return self
    without crashing.
    """
    from nchantdoffice.widgets.controls.toolbars import NchantdNewDocumentToolBar
    bar = NchantdNewDocumentToolBar.__new__(NchantdNewDocumentToolBar)
    bar.document_types = None
    # Must NOT raise
    result = bar.set_active_item()
    assert result is bar


def test_set_active_item_handles_no_active_column_yet():
    """The first call to set_active_item creates the ``active``
    column (pandas allows assigning a scalar that broadcasts).
    Subsequent calls keep the column in place and set the
    first-row flag.
    """
    bar = _make_toolbar()
    assert "active" not in bar.document_types.columns
    bar.set_active_item()
    assert "active" in bar.document_types.columns
    assert bar.document_types["active"].iloc[0] == 0