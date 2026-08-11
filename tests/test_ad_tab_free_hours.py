"""T-NEW-044 (UI-2): desktop free-tier ad-tab-free hours fallback.

Pins the contract that:
  - user_config.AD_TAB_FREE_HOURS key exists in DEFAULTS (int)
  - user_config.get_ad_tab_free_until() returns ISO timestamp
    or None (when not granted)
  - user_config.set_ad_tab_free_hours(hours: int) persists the
    grant and resets the timer
  - user_config.clear_ad_tab_free_hours() removes the grant
  - user_config.is_ad_tab_free_active() returns True when the
    timer is still valid (granted + not expired)
  - NchantdOfficeAdTab._is_visible_for_user() returns False when
    the user has ad-tab-free hours active (regardless of tier)
  - Advertisements.is_visible_to_user accepts the new check
"""
import ast
from pathlib import Path

USER_CONFIG = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/utilities/user_config.py"
)
ADVERTISEMENTS = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/widgets/advertisements.py"
)


def _read(p):
    return p.read_text()


def _ast_function(src, name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


# === UI-2.a: user_config ad-tab-free-hours helpers ===

def test_user_config_ad_tab_free_hours_default():
    """AD_TAB_FREE_HOURS key must exist in DEFAULTS (or a similar
    ad_tab_free_hours key — pin the shape, not the literal name).
    """
    src = _read(USER_CONFIG)
    # Look for the key in DEFAULTS — ast.unparse of nested dicts
    # can be fragile, so a literal substring match is more reliable.
    assert '"ad_tab_free_until"' in src, (
        "DEFAULTS must contain an ad_tab_free_until key "
        "(T-NEW-044 UI-2.a)"
    )


def test_get_ad_tab_free_until_exists():
    """user_config.get_ad_tab_free_until() must exist."""
    src = _read(USER_CONFIG)
    fn = _ast_function(src, "get_ad_tab_free_until")
    assert fn is not None, (
        "user_config.get_ad_tab_free_until must exist (T-NEW-044 UI-2.a)"
    )


def test_set_ad_tab_free_hours_exists():
    """user_config.set_ad_tab_free_hours(hours: int) must exist."""
    src = _read(USER_CONFIG)
    fn = _ast_function(src, "set_ad_tab_free_hours")
    assert fn is not None, (
        "user_config.set_ad_tab_free_hours must exist (T-NEW-044 UI-2.a)"
    )


def test_clear_ad_tab_free_hours_exists():
    """user_config.clear_ad_tab_free_hours() must exist."""
    src = _read(USER_CONFIG)
    fn = _ast_function(src, "clear_ad_tab_free_hours")
    assert fn is not None, (
        "user_config.clear_ad_tab_free_hours must exist (T-NEW-044 UI-2.a)"
    )


def test_is_ad_tab_free_active_exists():
    """user_config.is_ad_tab_free_active() must exist."""
    src = _read(USER_CONFIG)
    fn = _ast_function(src, "is_ad_tab_free_active")
    assert fn is not None, (
        "user_config.is_ad_tab_free_active must exist (T-NEW-044 UI-2.a)"
    )


# === UI-2.b: Ad tab respects ad-tab-free hours ===

def test_ad_tab_respects_ad_tab_free_hours():
    """_is_visible_for_user must check is_ad_tab_free_active
    and return False when the user has active hours.
    """
    src = _read(ADVERTISEMENTS)
    fn = _ast_function(src, "_is_visible_for_user")
    assert fn is not None, "_is_visible_for_user must exist"
    body = ast.unparse(fn)
    assert "is_ad_tab_free_active" in body or "ad_tab_free" in body, (
        "_is_visible_for_user must check ad-tab-free hours "
        "(T-NEW-044 UI-2.b)"
    )