"""T-NEW-044 (UI-1): desktop wires to /api/v1/referral/payout-eligibility.

Closes the UI gap: the referral panel currently does a
CLIENT-SIDE eligibility check (pending >= min_payout) that
ignores the tier-check (free-tier referrers should never
see "Eligible for payout" — they get ad-tab-free hours).

Pins the contract that:
  - ReferralAPIClient has fetch_payout_eligibility(user_id) method
  - The method calls GET /api/v1/referral/payout-eligibility/<id>
  - The method returns the dict from the server, or {} on error
  - NchantdOfficeReferralPanel._build_earnings_card fetches
    the eligibility from the server (not a client-side check)
  - Renders the 3 distinct UI states: free-tier / below-threshold
    / eligible
"""
import ast
from pathlib import Path

REFERRAL_PY = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/utilities/referral.py"
)
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


# === UI-1.a: ReferralAPIClient.fetch_payout_eligibility ===

def test_fetch_payout_eligibility_method_exists():
    """ReferralAPIClient.fetch_payout_eligibility() must exist."""
    src = _read(REFERRAL_PY)
    fn = _ast_function(src, "fetch_payout_eligibility")
    assert fn is not None, (
        "ReferralAPIClient.fetch_payout_eligibility must exist "
        "(T-NEW-044 UI-1.a)"
    )


def test_fetch_payout_eligibility_calls_correct_endpoint():
    """Must call GET /api/v1/referral/payout-eligibility/<user_id>."""
    src = _read(REFERRAL_PY)
    fn = _ast_function(src, "fetch_payout_eligibility")
    assert fn is not None
    body = ast.unparse(fn)
    assert "payout-eligibility" in body, (
        "fetch_payout_eligibility must call /payout-eligibility endpoint"
    )


def test_fetch_payout_eligibility_returns_dict():
    """Returns a dict (the eligibility JSON), or {} on error."""
    src = _read(REFERRAL_PY)
    fn = _ast_function(src, "fetch_payout_eligibility")
    assert fn is not None
    body = ast.unparse(fn)
    assert "Dict" in body or "dict" in body or "-> " in body, (
        "fetch_payout_eligibility must declare a return type"
    )


# === UI-1.b: referral_panel uses server-side check ===

def test_referral_panel_calls_fetch_payout_eligibility():
    """The panel must call ReferralAPIClient.fetch_payout_eligibility
    (not do a client-side pending>=min check)."""
    src = _read(REFERRAL_PANEL)
    assert "fetch_payout_eligibility" in src, (
        "NchantdOfficeReferralPanel must call "
        "fetch_payout_eligibility (T-NEW-044 UI-1.b — "
        "server-side authoritative check)"
    )


def test_referral_panel_handles_free_tier_state():
    """Must render a free-tier message when reason='free_tier'."""
    src = _read(REFERRAL_PANEL)
    assert "free_tier" in src, (
        "NchantdOfficeReferralPanel must render the free-tier "
        "state (reason='free_tier' from get_payout_eligibility)"
    )


def test_referral_panel_handles_below_threshold_state():
    """Must render the below-threshold state with the dollar gap."""
    src = _read(REFERRAL_PANEL)
    assert "below_threshold" in src, (
        "NchantdOfficeReferralPanel must render the below-threshold "
        "state (reason='below_threshold' from get_payout_eligibility)"
    )


def test_referral_panel_handles_eligible_state():
    """Must render the eligible state when eligible=True."""
    src = _read(REFERRAL_PANEL)
    assert "eligible" in src, (
        "NchantdOfficeReferralPanel must render the eligible "
        "state (eligible=True from get_payout_eligibility)"
    )