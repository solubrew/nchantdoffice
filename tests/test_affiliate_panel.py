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
  - NchantdOfficeAffiliatePanel class is defined
  - It extends NchantdOfficeDocument (matches the existing
    referral_panel.py pattern)
  - It has a fetch_connect_status() method
  - It has an _on_connect_stripe() event handler
  - It calls webbrowser.open() to launch the onboarding URL
  - The class name uses the NchantdOffice prefix
"""
import ast
from pathlib import Path

AFFILIATE_PANEL = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/widgets/config/affiliate_panel.py"
)


def _read(p):
    return p.read_text()


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
    """NchantdOfficeAffiliatePanel class must be defined."""
    src = _read(AFFILIATE_PANEL)
    cls = _ast_class(src, "NchantdOfficeAffiliatePanel")
    assert cls is not None, (
        "NchantdOfficeAffiliatePanel class must be defined "
        "(T-NEW-044 UI-3)"
    )


def test_affiliate_panel_extends_nchantd_office_document():
    """Must extend NchantdOfficeDocument (matches referral_panel.py)."""
    src = _read(AFFILIATE_PANEL)
    cls = _ast_class(src, "NchantdOfficeAffiliatePanel")
    assert cls is not None
    base_names = []
    for base in cls.bases:
        if isinstance(base, ast.Name):
            base_names.append(base.id)
    assert "NchantdOfficeDocument" in base_names, (
        "NchantdOfficeAffiliatePanel must extend NchantdOfficeDocument"
    )


def test_affiliate_panel_has_fetch_connect_status():
    """Must have fetch_connect_status() method to read server state."""
    src = _read(AFFILIATE_PANEL)
    fn = _ast_function(src, "fetch_connect_status")
    assert fn is not None, (
        "fetch_connect_status method must exist "
        "(T-NEW-044 UI-3 — reads server-side Stripe status)"
    )


def test_affiliate_panel_has_on_connect_stripe_handler():
    """Must have _on_connect_stripe event handler for the button click."""
    src = _read(AFFILIATE_PANEL)
    fn = _ast_function(src, "_on_connect_stripe")
    assert fn is not None, (
        "_on_connect_stripe handler must exist (T-NEW-044 UI-3)"
    )


def test_affiliate_panel_uses_webbrowser_open():
    """Onboarding URL must be launched via webbrowser.open()
    (the user completes Stripe KYC in the browser, not in-app)."""
    src = _read(AFFILIATE_PANEL)
    assert "webbrowser.open" in src, (
        "affiliate_panel must use webbrowser.open() to launch the "
        "Stripe onboarding URL (T-NEW-044 UI-3)"
    )


def test_affiliate_panel_calls_server_endpoint():
    """Must call POST /api/v1/affiliate/connect-stripe on the server."""
    src = _read(AFFILIATE_PANEL)
    assert "connect-stripe" in src or "connect_stripe" in src, (
        "affiliate_panel must call the server's "
        "/api/v1/affiliate/connect-stripe endpoint (T-NEW-044 UI-3)"
    )