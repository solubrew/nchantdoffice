"""Sprint 26 — Ad tab 'Remove ads' button redirect regression.

The right-side Ad tab has a "Remove ads - Go Pro" button
(NchantdOfficeAdTab._on_remove_ads_clicked). Per user direction
(2026-07-30), the canonical UX is to navigate to the existing
"Nchantd Account" tab under the Settings node in the left-pane
tree (the embedded browser for the nchantdoffice_com account
chain).

The Sprint 25 implementation called tree.setCurrentItem +
itemSelectionChanged.emit(), which only updated the QTreeWidget's
selection state but did NOT drive navigation. The actual
navigation lives in NchantdTreeView.set_current_node(node),
the nchantrs treeview wrapper method that sets
``model.current_node`` and calls ``updateTabs('center')``.

This test pins the contract that:
  1. The button click does NOT call ``QDesktopServices.openUrl``.
  2. The handler calls ``tree.set_current_node`` (the nchantrs
     treeview wrapper method) to drive navigation.
  3. The handler uses ``tree.findItems`` with "Nchantd Account"
     (with "Settings" as fallback) to locate the target node.
  4. When the tree wrapper or model is missing, the handler
     falls back gracefully (no exception bubbles).
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


def test_ad_tab_remove_ads_calls_tree_set_current_node():
    """Sprint 26: the handler must call
    ``tree.set_current_node(...)`` (the nchantrs treeview
    wrapper method that propagates selection to
    ``updateTabs('center')`` and ``model.current_node``).
    Calling bare ``tree.setCurrentItem`` only updates the
    QTreeWidget's selection state but does NOT drive
    navigation — the user reports clicks "select the Settings
    node but doesn't navigate there".
    """
    src = _read(AD_TAB)
    body = _function_source_segment(src, "_on_remove_ads_clicked")
    assert "set_current_node" in body, (
        "Ad tab 'Remove ads' handler does not call "
        "tree.set_current_node — without that the treeview "
        "will not propagate the selection to model.current_node "
        "or call updateTabs('center')."
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
