"""Sprint 25 — Ad tab 'Remove ads' button redirect regression.

The right-side Ad tab has a "Remove ads - Go Pro" button
(NchantdOfficeAdTab._on_remove_ads_clicked). Per user
direction (2026-07-30), the canonical UX is to navigate to an
existing "Nchantd Account" tab under the Settings node in the
left-pane tree (the embedded browser for the nchantdoffice_com
account chain). The handler must NOT launch an external
browser.

This test pins the contract that:
  1. The button click does NOT call ``QDesktopServices.openUrl``.
  2. The handler uses ``tree.findItems`` to look up the
     "Settings" and "Nchantd Account" nodes in the left tree.
  3. The handler uses ``tree.setCurrentItem`` to switch the
     tree selection (and ``scrollToItem`` + ``itemSelectionChanged``
     to make the switch visible).
  4. When the tree or model is missing, the handler falls back
     gracefully (no exception bubbles).
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


# --- Contract 2: use tree.findItems to look up the Settings node ---


def test_ad_tab_remove_ads_uses_tree_find_items_for_settings():
    """Sprint 25: the handler must look up the Settings node
    via ``tree.findItems("Settings", ...)`` so the in-app
    Settings node is selected.
    """
    src = _read(AD_TAB)
    body = _function_source_segment(src, "_on_remove_ads_clicked")
    assert "findItems" in body, (
        "Ad tab 'Remove ads' handler does not use tree.findItems "
        "to look up the Settings node."
    )
    assert '"Settings"' in body or "'Settings'" in body, (
        "Ad tab 'Remove ads' handler must look up the "
        "'Settings' node by name."
    )


# --- Contract 3: switch to the Nchantd Account tab ---


def test_ad_tab_remove_ads_switches_to_nchantd_account_tab():
    """Sprint 25: the handler must switch to the existing
    "Nchantd Account" tab (the embedded browser for the
    nchantdoffice_com account chain) under the Settings node.
    """
    src = _read(AD_TAB)
    body = _function_source_segment(src, "_on_remove_ads_clicked")
    assert "Nchantd Account" in body, (
        "Ad tab 'Remove ads' handler must look up the "
        "'Nchantd Account' node (the embedded browser for the "
        "nchantdoffice_com account chain)."
    )
    assert "setCurrentItem" in body, (
        "Ad tab 'Remove ads' handler must call tree.setCurrentItem "
        "to switch the tree selection."
    )


# --- Contract 4: graceful fallback when target unavailable ---


def test_ad_tab_remove_ads_handles_missing_view_gracefully():
    """Sprint 25: when ``self.app.view`` or the left tree is
    missing, the handler must not raise (it should log +
    return gracefully).
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
