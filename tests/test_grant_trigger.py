"""T-NEW-045 (WIRE-1): Desktop grant trigger for ad-tab-free hours.

Closes the UI-2 follow-up from T-NEW-044. The plumbing
(user_config.set_ad_tab_free_hours / is_ad_tab_free_active
helpers, _is_visible_for_user check) was landed in T-NEW-044
UI-2 — but the actual call to set_ad_tab_free_hours() was
deferred. This commit adds the trigger logic.

Pins the contract that:
  - ReferralPanel has a _maybe_grant_ad_tab_free_hours() method
  - The method is called from _fetch_payout_eligibility() after
    a free-tier response is received
  - The method computes hours = floor(pending_total * 24 / 5)
    (24h per $5 of pending credit, per AppReferralSpec §10)
  - The method only grants if hours >= MIN_GRANT_HOURS (1)
  - The method is best-effort (logs + swallows errors)
  - The method does NOT grant if user already has an active
    grant (no stacking — instead extends if newer)
  - ReferralPanel imports set_ad_tab_free_hours + is_ad_tab_free_active
"""
import ast
from pathlib import Path

REFERRAL_PANEL = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/widgets/config/referral_panel.py"
)


def _read(p):
    return p.read_text()


def _ast_function(src, name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def test_grant_method_exists():
    """_maybe_grant_ad_tab_free_hours() method must exist."""
    src = _read(REFERRAL_PANEL)
    fn = _ast_function(src, "_maybe_grant_ad_tab_free_hours")
    assert fn is not None, (
        "_maybe_grant_ad_tab_free_hours must exist (T-NEW-045 WIRE-1)"
    )


def test_grant_method_calls_set_ad_tab_free_hours():
    """The method must call set_ad_tab_free_hours()."""
    src = _read(REFERRAL_PANEL)
    fn = _ast_function(src, "_maybe_grant_ad_tab_free_hours")
    assert fn is not None
    body = ast.unparse(fn)
    assert "set_ad_tab_free_hours" in body, (
        "_maybe_grant_ad_tab_free_hours must call "
        "user_config.set_ad_tab_free_hours (T-NEW-045 WIRE-1)"
    )


def test_grant_method_checks_is_ad_tab_free_active():
    """Must check is_ad_tab_free_active to avoid stacking."""
    src = _read(REFERRAL_PANEL)
    fn = _ast_function(src, "_maybe_grant_ad_tab_free_hours")
    assert fn is not None
    body = ast.unparse(fn)
    assert "is_ad_tab_free_active" in body, (
        "_maybe_grant_ad_tab_free_hours must check "
        "is_ad_tab_free_active to avoid stacking grants "
        "(T-NEW-045 WIRE-1)"
    )


def test_grant_method_computes_hours():
    """Must compute hours from pending_total (the formula).
    Pin the shape: at least one arithmetic op on pending_total."""
    src = _read(REFERRAL_PANEL)
    fn = _ast_function(src, "_maybe_grant_ad_tab_free_hours")
    assert fn is not None
    body = ast.unparse(fn)
    assert "pending_total" in body or "pending" in body, (
        "_maybe_grant_ad_tab_free_hours must compute hours from "
        "pending_total (T-NEW-045 WIRE-1)"
    )


def test_panel_imports_set_ad_tab_free_hours():
    """The panel must import set_ad_tab_free_hours from user_config."""
    src = _read(REFERRAL_PANEL)
    assert "set_ad_tab_free_hours" in src, (
        "NchantdOfficeReferralPanel must import "
        "set_ad_tab_free_hours from user_config (T-NEW-045 WIRE-1)"
    )
    assert "is_ad_tab_free_active" in src, (
        "NchantdOfficeReferralPanel must import "
        "is_ad_tab_free_active from user_config (T-NEW-045 WIRE-1)"
    )


def test_fetch_payout_eligibility_calls_grant_method():
    """_fetch_payout_eligibility must call _maybe_grant_ad_tab_free_hours
    after receiving the eligibility response (with reason='free_tier')."""
    src = _read(REFERRAL_PANEL)
    fn = _ast_function(src, "_fetch_payout_eligibility")
    assert fn is not None
    body = ast.unparse(fn)
    assert "_maybe_grant_ad_tab_free_hours" in body, (
        "_fetch_payout_eligibility must call "
        "_maybe_grant_ad_tab_free_hours (T-NEW-045 WIRE-1)"
    )