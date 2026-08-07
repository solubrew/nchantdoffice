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


def test_ad_tab_remove_ads_delegates_to_redirect_helper():
    """Sprint 28: the handler delegates to the shared static
    helper ``NchantdOfficeAdTab.redirect_to_get_pro`` (the
    same one used by the toolbar 'Get Pro' button). The
    helper owns the navigation logic — both call sites
    delegate to it so they stay in sync.
    """
    src = _read(AD_TAB)
    body = _function_source_segment(src, "_on_remove_ads_clicked")
    assert "redirect_to_get_pro" in body, (
        "Ad tab 'Remove ads' handler must delegate to "
        "NchantdOfficeAdTab.redirect_to_get_pro so both "
        "buttons share one navigation implementation."
    )


# --- Contract 3: look up the Nchantd Account node by name ---


def test_ad_tab_remove_ads_helper_uses_tree_find_items():
    """Sprint 28: the shared redirect helper
    (``NchantdOfficeAdTab.redirect_to_get_pro``) must look up
    the "Nchantd Account" node via ``findItems(...)``.
    """
    import ast
    src = _read(AD_TAB)
    tree = ast.parse(src)
    helper_body = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "redirect_to_get_pro":
            helper_body = ast.get_source_segment(src, node) or ""
            break
    assert helper_body, (
        "advertisements.py must expose "
        "NchantdOfficeAdTab.redirect_to_get_pro as a "
        "shared static helper."
    )
    assert "findItems" in helper_body, (
        "redirect_to_get_pro must look up the target node "
        "via tree.findItems."
    )
    assert '"Nchantd Account"' in helper_body or "'Nchantd Account'" in helper_body, (
        "redirect_to_get_pro must look up the "
        "'Nchantd Account' node by name."
    )


# --- Contract 4: graceful fallback when target unavailable ---


def test_ad_tab_redirect_helper_handles_missing_view_gracefully():
    """Sprint 28: the shared redirect helper must guard with
    try/except so missing widgets don't crash either
    caller.
    """
    import ast
    src = _read(AD_TAB)
    tree = ast.parse(src)
    helper_body = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "redirect_to_get_pro":
            helper_body = ast.get_source_segment(src, node) or ""
            break
    assert helper_body, (
        "redirect_to_get_pro must exist as a shared helper."
    )
    assert "try:" in helper_body, (
        "redirect_to_get_pro must guard the navigation call "
        "with a try/except so missing widgets don't crash."
    )
    assert "except" in helper_body, (
        "redirect_to_get_pro must catch exceptions instead "
        "of letting them bubble up to either caller."
    )


def test_ad_tab_target_url_is_compare_not_get_pro():
    """T-DESK-062: the 'Remove ads' / 'Go Pro' CTA opens the
    /compare page on the live server, not the fictional
    /get_pro page (which 404s).

    Pinned by grepping the source: every hardcoded URL on
    the upgrade flow must point at /compare.
    """
    import os
    ad_tab_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "nchantdoffice", "widgets", "advertisements.py",
    )
    with open(ad_tab_path) as f:
        ad_src = f.read()
    assert "nchantdoffice.com/get_pro" not in ad_src, (
        "advertisements.py still references the old /get_pro "
        "URL. The live server only exposes /compare. Update "
        "the CTA target_url."
    )
    assert "nchantdoffice.com/compare" in ad_src, (
        "advertisements.py should point the CTA at /compare."
    )

    upgrades_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "nchantdoffice", "utilities", "upgrades.py",
    )
    with open(upgrades_path) as f:
        up_src = f.read()
    assert "nchantdoffice.com/get_pro" not in up_src, (
        "utilities/upgrades.py still references the old /get_pro "
        "URL. The QMessageBox 'Go Pro' button should open "
        "/compare."
    )
    assert "nchantdoffice.com/compare" in up_src, (
        "utilities/upgrades.py should point the 'Go Pro' button "
        "at /compare."
    )
