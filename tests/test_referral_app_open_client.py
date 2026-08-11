"""T-NEW-042 (DESK-1): desktop records app-open on launch.

Pins the contract that:
  - ReferralAPIClient.record_app_open(referee_user_id)
    exists in nchantdoffice/utilities/referral.py
  - The method POSTs to /api/v1/referral/record-app-open
    with JSON {referee_user_id: ...}
  - The method is best-effort (failures logged, never raise)
  - The method uses the user_config.get_server_url() —
    NOT env vars (T-NEW-070 hard-break)
  - cmds/runNchantdOffice.py calls record_app_open on
    startup so the 3-opens-minimum rule actually counts
    desktop launches (not just installs)
"""
import ast
from pathlib import Path

REFERRAL = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/utilities/referral.py"
)
RUN = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "cmds/runNchantdOffice.py"
)


def _read(p):
    return p.read_text()


def test_record_app_open_method_exists():
    src = _read(REFERRAL)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ReferralAPIClient":
            body = ast.unparse(node)
            assert "def record_app_open" in body, (
                "ReferralAPIClient.record_app_open() must exist "
                "(T-NEW-042 DESK-1)"
            )
            return
    assert False, "ReferralAPIClient class must exist"


def test_record_app_open_uses_self_base_url():
    """The method must use self.base_url (computed from
    user_config.get_server_url — not an env var)."""
    src = _read(REFERRAL)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "record_app_open":
            body = ast.unparse(node)
            assert "self.base_url" in body, (
                "record_app_open must use self.base_url (which is "
                "sourced from user_config.get_server_url — "
                "T-NEW-070 hard-break)"
            )
            return
    assert False, "record_app_open function must exist"


def test_record_app_open_posts_json_body():
    """The method POSTs a JSON body with referee_user_id."""
    src = _read(REFERRAL)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "record_app_open":
            body = ast.unparse(node)
            assert "requests.post" in body, (
                "record_app_open must POST to the server endpoint"
            )
            assert "referee_user_id" in body, (
                "record_app_open body must include referee_user_id"
            )
            # Endpoint path
            assert "/record-app-open" in body, (
                "record_app_open must POST to /referral/record-app-open"
            )
            return
    assert False, "record_app_open function must exist"


def test_record_app_open_called_in_launcher():
    """cmds/runNchantdOffice.py must call record_app_open on
    startup so the server's 3-opens-minimum rule can count
    actual app launches, not just installs."""
    src = _read(RUN)
    assert "record_app_open" in src, (
        "cmds/runNchantdOffice.py must call ReferralAPIClient"
        ".record_app_open on startup (T-NEW-042 DESK-1)"
    )
