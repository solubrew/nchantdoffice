"""Sprint 24 — Ad tab 'Remove ads' button redirect regression.

The right-side Ad tab has a "Remove ads - Go Pro" button
(NchantdOfficeAdTab._on_remove_ads_clicked) that previously
opened a browser via QDesktopServices.openUrl. The user wants
it to redirect into an existing tab under the Settings node
that points at nchantdoffice.com (the canonical "Get Pro" page).

This test pins the contract that:
  1. The button click does NOT call ``QDesktopServices.openUrl``.
  2. The handler delegates to the app's view for navigation
     (via ``self.app.view.switch_to_tab`` or a similar
     ``switch_to_*`` method) rather than opening a browser.
  3. The redirect target is an in-app tab pointing at
     https://www.nchantdoffice.com (not a uuid placeholder).
  4. When the redirect target is unavailable, the handler
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
    """Sprint 24: the 'Remove ads' click handler must NOT call
    QDesktopServices.openUrl — the redirect should go through
    the app's view, not launch an external browser.
    """
    src = _read(AD_TAB)
    body = _function_source_segment(src, "_on_remove_ads_clicked")
    assert "QDesktopServices.openUrl" not in body, (
        "Ad tab 'Remove ads' handler still calls "
        "QDesktopServices.openUrl — the redirect should go "
        "through self.app.view.switch_to_tab(...) instead of "
        "launching an external browser."
    )


# --- Contract 2: delegate to the app's view for navigation ---


def test_ad_tab_remove_ads_calls_view_switch():
    """Sprint 24: the handler must delegate to ``self.app.view``
    (specifically a ``switch_to_*`` method) to navigate, not
    raise or silently no-op.
    """
    src = _read(AD_TAB)
    body = _function_source_segment(src, "_on_remove_ads_clicked")
    assert "self.app.view" in body, (
        "Ad tab 'Remove ads' handler does not delegate to "
        "self.app.view — the redirect should go through the app's "
        "view to find the Settings tab."
    )
    # Should call a switch_to_* method.
    assert "switch_to" in body, (
        "Ad tab 'Remove ads' handler must call a switch_to_* "
        "method on self.app.view to route to the Settings tab."
    )


# --- Contract 3: target is nchantdoffice.com ---


def test_ad_tab_remove_ads_target_is_nchantdoffice_com():
    """Sprint 24: the redirect target must point at
    https://www.nchantdoffice.com (or its ``/get_pro`` sub-path).
    """
    src = _read(AD_TAB)
    body = _function_source_segment(src, "_on_remove_ads_clicked")
    assert "nchantdoffice.com" in body, (
        "Ad tab 'Remove ads' redirect target must point at "
        "nchantdoffice.com."
    )


# --- Contract 4: graceful fallback when target unavailable ---


def test_ad_tab_remove_ads_handles_missing_view_gracefully():
    """Sprint 24: when ``self.app.view`` is missing or the
    Settings tab cannot be found, the handler must not raise
    (it should log + return gracefully).
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
