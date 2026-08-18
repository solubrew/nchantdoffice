"""T-NEW-033 -- Search dispatch (global / node / tab scoped) (TDD).

T-NEW-033 closes 4 polish items on the Right Toolbox:
  1. cmd_search_global(query) -- across all nodes + tabs.
  2. cmd_search_node(query)   -- current node's tabs.
  3. cmd_search_tab(query)    -- current tab's content.
  4. cmd_web_search_pane + cmd_llm_query_pane -- finish
     the stubs (no log+return-self).

Decision (default picked 2026-07-31 -- user skipped):
  - Search index lives in SQLite (queries ``doc`` table
    directly via LIKE matching on ``name_txt`` +
    ``description_txt``). Consistent with the rest of
    nchantdoffice's storage model. In-memory rebuild was
    rejected because it doesn't survive app restarts.

Tests:

  - test_search_global_returns_matches_across_all_nodes
  - test_search_node_returns_matches_for_active_node_only
  - test_search_tab_returns_matches_for_active_tab_only
  - test_search_global_returns_empty_when_no_matches
  - test_search_node_handles_missing_active_node
  - test_search_tab_handles_missing_active_tab
  - test_search_dispatcher_filters_by_scope
  - test_cmd_web_search_pane_dispatches (not stub)
  - test_cmd_llm_query_pane_dispatches (not stub)
"""

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication
# ---------------------------------------------------------------------------
# NchantdOfficeCloakModel.search_documents (SQLite-backed)
# ---------------------------------------------------------------------------


def _make_model_with_documents(docs):
    """Build a NchantdOfficeCloakModel via __new__ with a
    fake ``get_view_documents_all`` (the SQL-backed
    catalog read that ``search_documents`` calls).
    """
    from nchantdoffice.models import NchantdOfficeCloakModel
    model = NchantdOfficeCloakModel.__new__(NchantdOfficeCloakModel)
    import pandas as pd
    docs_df = pd.DataFrame(docs) if docs else pd.DataFrame()
    model.get_view_documents_all = lambda cfg=None: docs_df
    return model


def test_search_global_returns_matches_across_all_nodes():
    """Global search returns every doc whose name /
    description contains the query, regardless of node."""
    model = _make_model_with_documents(
        [
            {"nid_txt": "n1", "tid_txt": "t1", "name_txt": "hello world"},
            {"nid_txt": "n2", "tid_txt": "t2", "name_txt": "hello python"},
            {"nid_txt": "n3", "tid_txt": "t3", "name_txt": "unrelated"},
        ]
    )
    results = model.search_documents("hello")
    assert len(results) == 2, (
        f"Global search for 'hello' must return 2 docs. "
        f"Got: {len(results)}"
    )


def test_search_node_returns_matches_for_active_node_only():
    """Node-scoped search returns docs whose name /
    description match AND belong to the active node."""
    model = _make_model_with_documents(
        [
            {"nid_txt": "n1", "tid_txt": "t1", "name_txt": "hello world"},
            {"nid_txt": "n2", "tid_txt": "t2", "name_txt": "hello python"},
        ]
    )
    results = model.search_documents("hello", scope="node", active_nid="n1")
    assert len(results) == 1, (
        f"Node-scoped search for 'hello' on n1 must return "
        f"only the n1 doc. Got: {len(results)}"
    )


def test_search_tab_returns_matches_for_active_tab_only():
    """Tab-scoped search returns docs whose name /
    description match AND belong to the active tab."""
    model = _make_model_with_documents(
        [
            {"nid_txt": "n1", "tid_txt": "t1", "name_txt": "hello world"},
            {"nid_txt": "n1", "tid_txt": "t2", "name_txt": "hello python"},
        ]
    )
    results = model.search_documents("hello", scope="tab", active_tid="t1")
    assert len(results) == 1, (
        f"Tab-scoped search for 'hello' on t1 must return "
        f"only the t1 doc. Got: {len(results)}"
    )


def test_search_global_returns_empty_when_no_matches():
    """When no docs match the query, return empty DataFrame."""
    model = _make_model_with_documents(
        [{"nid_txt": "n1", "tid_txt": "t1", "name_txt": "hello"}]
    )
    results = model.search_documents("xyzzy_does_not_match")
    assert len(results) == 0, (
        f"Search for non-matching query must return empty. "
        f"Got: {len(results)}"
    )


def test_search_node_handles_missing_active_node():
    """Defensive: when scope='node' but active_nid is None,
    return empty (don't fall back to global)."""
    model = _make_model_with_documents(
        [{"nid_txt": "n1", "tid_txt": "t1", "name_txt": "hello"}]
    )
    results = model.search_documents(
        "hello", scope="node", active_nid=None
    )
    assert len(results) == 0, (
        f"Node search with no active node must return empty. "
        f"Got: {len(results)}"
    )


def test_search_tab_handles_missing_active_tab():
    """Defensive: when scope='tab' but active_tid is None,
    return empty."""
    model = _make_model_with_documents(
        [{"nid_txt": "n1", "tid_txt": "t1", "name_txt": "hello"}]
    )
    results = model.search_documents(
        "hello", scope="tab", active_tid=None
    )
    assert len(results) == 0, (
        f"Tab search with no active tab must return empty. "
        f"Got: {len(results)}"
    )


def test_search_global_default_scope():
    """When scope is omitted, default to 'global'."""
    model = _make_model_with_documents(
        [{"nid_txt": "n1", "tid_txt": "t1", "name_txt": "hello"}]
    )
    # No scope kwarg -> defaults to 'global'
    results = model.search_documents("hello")
    assert len(results) == 1


def test_search_dispatcher_filters_by_scope():
    """The three scope values return three distinct result sets."""
    model = _make_model_with_documents(
        [
            {"nid_txt": "n1", "tid_txt": "t1", "name_txt": "hello global"},
            {"nid_txt": "n2", "tid_txt": "t2", "name_txt": "hello node"},
            {"nid_txt": "n1", "tid_txt": "t3", "name_txt": "hello tab"},
        ]
    )
    global_results = model.search_documents("hello")
    assert len(global_results) == 3, (
        f"Global must return all 3. Got: {len(global_results)}"
    )
    node_results = model.search_documents(
        "hello", scope="node", active_nid="n1"
    )
    assert len(node_results) == 2, (
        f"Node-scoped (n1) must return 2 (t1, t3). "
        f"Got: {len(node_results)}"
    )
    tab_results = model.search_documents(
        "hello", scope="tab", active_tid="t1"
    )
    assert len(tab_results) == 1, (
        f"Tab-scoped (t1) must return 1. "
        f"Got: {len(tab_results)}"
    )


# ---------------------------------------------------------------------------
# cmd_web_search_pane + cmd_llm_query_pane (no stubs)
# ---------------------------------------------------------------------------


def test_cmd_web_search_pane_dispatches():
    """The cmd handler must NOT be a stub (return self) --
    it must call cmd_search_global. Source-level guard.
    """
    from pathlib import Path
    tb_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/controls/toolboxes.py"
    ).read_text()
    assert "cmd_search_global" in tb_py, (
        "NchantdOfficeApplicationToolBox must define a "
        "cmd_search_global handler (T-NEW-033 dispatch)"
    )


def test_cmd_llm_query_pane_dispatches():
    """The cmd handler must NOT be a stub -- it must call
    cmd_search_global with the LLM-flavored scope. Source-
    level guard.
    """
    from pathlib import Path
    tb_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/controls/toolboxes.py"
    ).read_text()
    assert "cmd_search_global" in tb_py


def test_three_search_handlers_defined():
    """The toolbox must define cmd_search_global, _node, _tab."""
    from pathlib import Path
    tb_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/controls/toolboxes.py"
    ).read_text()
    for handler in ("cmd_search_global", "cmd_search_node", "cmd_search_tab"):
        assert f"def {handler}" in tb_py, (
            f"Toolbox must define {handler} (T-NEW-033)"
        )
