"""T-NEW-140 regression: free users' right-side default tab is
locked to the Ad tab.

**Free users see all right-side tabs; should default to the Ad
tab and restrict the rest.**

The right-side tab dropdown in
``NchantdOfficeInterfaceSettings.get_right_pane_tab_options``
returns all visible right tabs; the user's selection is
recorded by ``cmd_on_change_right_side_tab_select`` without
pro/free gating. Free-tier users can therefore set their
default right tab to anything (Settings, Help, Ad) -- the
upsell surface (Ad tab) gets lost in the shuffle.

The fix:
1. ``cmd_on_change_right_side_tab_select`` consults
   ``is_pro_user(user)``. If the user is NOT pro and the
   selected value is not the Ad tab (``"4 - Ad"`` per
   ``get_right_pane_tab_options`` convention), coerce the
   recorded value to ``"4 - Ad"`` and log a warning.
2. The dropdown options themselves remain unchanged --
   free users can still see all tabs in the right pane --
   only the *default* they open on launch is locked to the
   Ad tab. (Showing only the Ad tab would break the rest of
   the right-side UX.)
3. Pro users are unrestricted -- the coercion only fires
   when ``is_pro_user(user) is False``.

Test surface: ``tests/test_t_new_140_free_user_ad_tab.py``
(this file). Pins:
  - source-level: ``cmd_on_change_right_side_tab_select``
    consults ``is_pro_user`` before recording the value.
  - source-level: the coercion literal is ``"4 - Ad"`` (the
    Ad tab identifier per get_right_pane_tab_options).
  - behavioural (free user): selected non-Ad value is
    coerced to ``"4 - Ad"``.
  - behavioural (pro user): selected non-Ad value is
    preserved as-is.
  - behavioural (no user): defensive no-op (no crash when
    the user attr is absent).

Migration plan (no priority / low priority -- design
decision first): the lock is a single conditional on the
save path. The right-pane tabs themselves are not hidden --
this preserves the rest of the right-side UX (Settings,
Help, etc. are still navigable). Coercion is the lightest
touch that satisfies the T-NEW-135 + T-NEW-140 pair
("when free users hit the cap they get redirected to the
Get Pro upsell; they also default-open on the Ad tab so
the upsell is the first thing they see").
"""
import inspect
from unittest.mock import MagicMock

# T-NEW-074 Task 9: keep Qt on the headless offscreen platform
# before any PySide6 import so the integration test does not
# need a real display.
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402


def _bare_settings():
    """Build a minimal settings instance without running
    __init__ (which requires the full kahndor + Qt stack)."""
    from nchantdoffice.widgets.config.settings import (
        NchantdOfficeInterfaceSettings,
    )
    return NchantdOfficeInterfaceSettings.__new__(
        NchantdOfficeInterfaceSettings
    )


def _settings_with_user(user):
    settings = _bare_settings()
    settings.app = MagicMock()
    settings.app.model.user = user
    settings.default_tab_switch = MagicMock()
    settings.default_tab_switch.currentText = MagicMock(
        return_value="2 - Settings"
    )
    settings.config = MagicMock()
    settings.config.dikt = {}
    return settings


# ---------------------------------------------------------------------------
# Source-level pin: free-user coercion lives in the save handler
# ---------------------------------------------------------------------------

def test_right_side_save_consults_is_pro_user():
    """T-NEW-140: ``cmd_on_change_right_side_tab_select`` must
    consult ``is_pro_user`` so free users get coerced to the
    Ad tab. Without this, the dropdown's selected value is
    recorded verbatim regardless of tier.
    """
    from nchantdoffice.widgets.config.settings import (
        NchantdOfficeInterfaceSettings,
    )
    src = inspect.getsource(
        NchantdOfficeInterfaceSettings.cmd_on_change_right_side_tab_select
    )
    assert "is_pro_user" in src, (
        "cmd_on_change_right_side_tab_select must consult "
        "is_pro_user (T-NEW-140). Source:\n" + src[:1500]
    )


def test_right_side_save_coerces_to_ad_tab_literal():
    """T-NEW-140: the coercion target is the literal ``"4 - Ad"``
    (the Ad tab's identifier per
    ``get_right_pane_tab_options`` convention). The pin is
    source-level because the live DB lookup is too heavy for
    a test env.
    """
    from nchantdoffice.widgets.config.settings import (
        NchantdOfficeInterfaceSettings,
    )
    src = inspect.getsource(
        NchantdOfficeInterfaceSettings.cmd_on_change_right_side_tab_select
    )
    assert '"4 - Ad"' in src or "'4 - Ad'" in src, (
        "cmd_on_change_right_side_tab_select must coerce free "
        "users' selection to '4 - Ad' (T-NEW-140). "
        "Source:\n" + src[:1500]
    )


# ---------------------------------------------------------------------------
# Behavioural pin: free user coerces, pro user preserves
# ---------------------------------------------------------------------------

def test_free_user_selection_coerced_to_ad_tab(monkeypatch):
    """T-NEW-140 (behavioural): when the user is NOT pro and
    selects a non-Ad right-side tab, the recorded value must
    be coerced to ``"4 - Ad"`` (the Ad tab).
    """
    from nchantdoffice.utilities import upgrades as upg

    monkeypatch.setattr(upg, "is_pro_user", lambda user: False)

    settings = _settings_with_user(MagicMock(has_pro=False))
    settings.cmd_on_change_right_side_tab_select()

    assert settings.default_right_side_tab == "4 - Ad", (
        f"Free user's right-side tab must be coerced to "
        f"'4 - Ad' (T-NEW-140); got {settings.default_right_side_tab!r}"
    )
    assert settings.config.dikt["default_right_side_tab"] == "4 - Ad"


def test_pro_user_selection_preserved(monkeypatch):
    """T-NEW-140 (behavioural, pro): when the user IS pro,
    the selected value is recorded verbatim -- the Ad-tab
    lock does NOT fire for paid users.
    """
    from nchantdoffice.utilities import upgrades as upg

    monkeypatch.setattr(upg, "is_pro_user", lambda user: True)

    settings = _settings_with_user(MagicMock(has_pro=True))
    settings.default_tab_switch.currentText = MagicMock(
        return_value="2 - Settings"
    )
    settings.cmd_on_change_right_side_tab_select()

    assert settings.default_right_side_tab == "2 - Settings", (
        f"Pro user's right-side tab selection must be preserved "
        f"(T-NEW-140); got {settings.default_right_side_tab!r}"
    )


def test_free_user_selecting_ad_tab_is_preserved(monkeypatch):
    """T-NEW-140 (idempotent): when the user is NOT pro and
    selects the Ad tab, no coercion is needed -- the value
    stays ``"4 - Ad"``. The pin guards against a bug that
    would crash or no-op on the no-op path.
    """
    from nchantdoffice.utilities import upgrades as upg

    monkeypatch.setattr(upg, "is_pro_user", lambda user: False)

    settings = _settings_with_user(MagicMock(has_pro=False))
    settings.default_tab_switch.currentText = MagicMock(
        return_value="4 - Ad"
    )
    settings.cmd_on_change_right_side_tab_select()

    assert settings.default_right_side_tab == "4 - Ad"


def test_save_handler_swallows_exception(monkeypatch):
    """T-NEW-140 (defensive): when the user object is missing
    or the is_pro_user helper raises, the handler must not
    crash -- it falls back to recording the user's selected
    value as-is.
    """
    from nchantdoffice.utilities import upgrades as upg

    def boom(user):
        raise Exception("user lookup failed")
    monkeypatch.setattr(upg, "is_pro_user", boom)

    settings = _bare_settings()
    settings.app = MagicMock()
    settings.app.model.user = None
    settings.default_tab_switch = MagicMock()
    settings.default_tab_switch.currentText = MagicMock(
        return_value="2 - Settings"
    )
    # Must not raise.
    settings.cmd_on_change_right_side_tab_select()