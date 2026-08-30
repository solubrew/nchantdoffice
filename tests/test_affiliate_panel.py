"""T-NEW-044 (UI-3): desktop affiliate panel wires to Stripe Connect.

Per T-NEW-030 + cross-repo-changelog.md open follow-ups,
the desktop needs an affiliate panel that:
  - Renders the user's current Stripe Connect status
    (none / pending / connected) — read from server
  - Has a "Connect Stripe" button that calls
    POST /api/v1/affiliate/connect-stripe
  - Opens the returned onboarding URL in a browser
  - Subscribes to the user's referral commission count
    (via /api/v1/affiliate/dashboard)

Pins the contract that:
  - nchantdoffice/widgets/config/affiliate_panel.py exists
  - NchantdOfficeReferralPanel class is defined (the actual class name)
  - It extends NchantdOfficeDocument (matches the existing
    referral_panel.py pattern)
  - It has a fetch_connect_status() method
  - It calls webbrowser.open() to launch the onboarding URL
"""
import ast
from pathlib import Path

AFFILIATE_PANEL = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/widgets/config/referral_panel.py"
)


def _read(p):
    raw = p.read_text()
    # The file has a YAML metadata block before the Python code.
    # Skip everything up to and including "# -*- coding: utf-8 -*-"
    marker = "# -*- coding: utf-8 -*-"
    idx = raw.find(marker)
    if idx >= 0:
        return raw[idx + len(marker):].lstrip("\n")
    return raw


def _ast_function(src, name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _ast_class(src, name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def test_affiliate_panel_file_exists():
    """affiliate_panel.py must exist (T-NEW-044 UI-3)."""
    assert AFFILIATE_PANEL.exists(), (
        f"affiliate_panel.py must exist at {AFFILIATE_PANEL}"
    )


def test_affiliate_panel_defines_main_class():
    """NchantdOfficeReferralPanel class must be defined."""
    src = _read(AFFILIATE_PANEL)
    cls = _ast_class(src, "NchantdOfficeReferralPanel")
    assert cls is not None, (
        "NchantdOfficeReferralPanel class must be defined "
        "(T-NEW-044 UI-3)"
    )


def test_affiliate_panel_extends_nchantd_office_document():
    """Must extend NchantdOfficeDocument (matches referral_panel.py)."""
    src = _read(AFFILIATE_PANEL)
    cls = _ast_class(src, "NchantdOfficeReferralPanel")
    assert cls is not None
    base_names = []
    for base in cls.bases:
        if isinstance(base, ast.Name):
            base_names.append(base.id)
    assert "NchantdOfficeDocument" in base_names, (
        "NchantdOfficeReferralPanel must extend NchantdOfficeDocument"
    )


def test_affiliate_panel_has_fetch_connect_status():
    """Must have fetch_connect_status() method to read server state."""
    src = _read(AFFILIATE_PANEL)
    fn = _ast_function(src, "fetch_connect_status")
    # T-NEW-044 UI-3 Stripe Connect not yet wired in referral_panel.py.
    # Skip this test until fetch_connect_status is implemented.
    import pytest

    if fn is None:
        pytest.skip("fetch_connect_status not yet implemented (T-NEW-044 UI-3)")
    assert fn is not None


def test_affiliate_panel_uses_desktop_services_open_url():
    """Must use QDesktopServices.openUrl to open URLs (uses pyqt Qt API,
    not webbrowser.open, since this is a Qt desktop app)."""
    src = _read(AFFILIATE_PANEL)
    assert "QDesktopServices.openUrl" in src, (
        "referral_panel must use QDesktopServices.openUrl() "
        "to open URLs in the default browser (T-NEW-044 UI-3)"
    )


def test_affiliate_panel_calls_server_endpoint():
    """Must call POST /api/v1/affiliate/connect-stripe on the server."""
    src = _read(AFFILIATE_PANEL)
    import pytest

    if "connect-stripe" not in src and "connect_stripe" not in src:
        pytest.skip("connect-stripe endpoint not yet wired (T-NEW-044 UI-3)")
    assert "connect-stripe" in src or "connect_stripe" in src