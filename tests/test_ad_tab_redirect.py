"""Sprint 27 — Ad tab 'Remove ads' button redirect regression.

The right-side Ad tab has a "Remove ads - Go Pro" button
(NchantdOfficeAdTab._on_remove_ads_clicked). Per user direction
(2026-07-30), the canonical UX is to navigate to the existing
"Nchantd Account" tab under the Settings node in the left-pane
tree (the embedded browser for the nchantdoffice_com account
chain).

Sprint 25 called tree.setCurrentItem (no navigation). Sprint 26
called pane.tree.set_current_node, but pane.tree is the inner
NchantdApplicationTree (QTreeWidget subclass) — that class
doesn't have set_current_node. The actual navigation entry point
is the nchantrs NchantdTreeView wrapper, exposed as
``pane.tree.view`` (``nchantrs/views/treeviews.py:38``), whose
``set_current_node`` (line 266) calls ``model.current_node =``
and ``node.updateTabs('center')``.

This test pins the contract that:
  1. The button click does NOT call ``QDesktopServices.openUrl``.
  2. The handler resolves ``pane.tree.view`` (the NchantdTreeView
     wrapper) and calls ``set_current_node`` on it.
  3. The handler uses ``inner_tree.findItems`` with "Nchantd
     Account" (with "Settings" as fallback) to locate the
     target node.
  4. When the wrapper or model is missing, the handler falls
     back gracefully (no exception bubbles).
"""

import ast
import sys
from pathlib import Path

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

AD_TAB = PROJ_ROOT / "nchantdoffice" / "widgets" / "advertisements.py"


def _read(path):
    return path.read_text()


def _ast_find_function(src, name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _function_source_segment(src, name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node) or ""
    return ""


# --- Contract 1: no QDesktopServices.openUrl in the click handler ---


def test_ad_tab_remove_ads_does_not_open_browser():
    """Sprint 25: the 'Remove ads' click handler must NOT call
    QDesktopServices.openUrl — the redirect must go through
    the in-app tree, not launch an external browser.
    """
    src = _read(AD_TAB)
    body = _function_source_segment(src, "_on_remove_ads_clicked")
    assert "QDesktopServices.openUrl" not in body, (
        "Ad tab 'Remove ads' handler still calls "
        "QDesktopServices.openUrl — the redirect should go "
        "through the left-pane tree instead of launching an "
        "external browser."
    )


# --- Contract 2: call the treeview's set_current_node (drives navigation) ---


def test_ad_tab_remove_ads_calls_tree_view_set_current_node():
    """Sprint 27: the handler must call
    ``tree_view.set_current_node(...)`` — the nchantrs
    NchantdTreeView wrapper method
    (``nchantrs/views/treeviews.py:266``) that propagates
    selection to ``updateTabs('center')`` and
    ``model.current_node``. Calling ``set_current_node`` on
    the inner ``NchantdApplicationTree`` (which Sprint 26
    did) silently no-ops because that class doesn't define
    the method.
    """
    src = _read(AD_TAB)
    body = _function_source_segment(src, "_on_remove_ads_clicked")
    assert "set_current_node" in body, (
        "Ad tab 'Remove ads' handler does not call "
        "set_current_node — without that the treeview "
        "wrapper will not propagate the selection to "
        "model.current_node or call updateTabs('center')."
    )
    # The wrapper must be reached via pane.tree.view (not
    # pane.tree directly, since pane.tree is the bare
    # QTreeWidget which lacks the method).
    assert 'inner_tree, "view"' in body or 'getattr(inner_tree, "view"' in body, (
        "Ad tab 'Remove ads' handler must resolve the "
        "NchantdTreeView wrapper via pane.tree.view — the "
        "inner NchantdApplicationTree doesn't define "
        "set_current_node."
    )


# --- Contract 3: look up the Nchantd Account node by name ---


def test_ad_tab_remove_ads_uses_tree_find_items_for_account():
    """Sprint 26: the handler must look up the "Nchantd Account"
    node (the embedded browser for the nchantdoffice_com
    account chain) via ``tree.findItems(...)``.
    """
    src = _read(AD_TAB)
    body = _function_source_segment(src, "_on_remove_ads_clicked")
    assert "findItems" in body, (
        "Ad tab 'Remove ads' handler does not use tree.findItems "
        "to look up the target node."
    )
    assert '"Nchantd Account"' in body or "'Nchantd Account'" in body, (
        "Ad tab 'Remove ads' handler must look up the "
        "'Nchantd Account' node by name (the embedded browser "
        "for the nchantdoffice_com account chain)."
    )


# --- Contract 4: graceful fallback when target unavailable ---


def test_ad_tab_remove_ads_handles_missing_view_gracefully():
    """Sprint 26: when ``self.app.view`` or the left tree
    wrapper is missing, the handler must not raise (it should
    log + return gracefully).
    """
    src = _read(AD_TAB)
    body = _function_source_segment(src, "_on_remove_ads_clicked")
    assert "try:" in body, (
        "Ad tab 'Remove ads' handler must guard the navigation "
        "call with a try/except so missing widgets do not crash."
    )
    assert "except" in body, (
        "Ad tab 'Remove ads' handler must catch exceptions "
        "instead of letting them bubble up."
    )
