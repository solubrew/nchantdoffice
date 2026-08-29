# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-upgrade-prompts
    name: Upgrade Prompt Utilities
    description: >
        Free -> Pro upgrade prompt logic per
        nchantdofficeATNRG/AppReferralSpec.md §5 ("In-App Prompts").

        Fires soft prompts at defined friction points:
          - After the user creates their 3rd tab
          - After their 5th Service Quick Link click

        Prompts are non-blocking QMessageBox dialogs. They're rate-
        limited (one prompt per category per session) so we never
        spam the user.

        T-DESK: tier detection comes from the in-app user model
        (``has_pro``). Pro users never see these prompts.
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*-
# -*- Standard Library Imports
import os
from os.path import abspath, dirname, join

# Standard library
import json

# SB Library
from kahndor.logma import Logma

logma = Logma(__name__)

here = join(dirname(__file__), "")  # ||
prompt_counter_path = join(here, "_data_", ".upgrade_prompt_state.json")

# Friction thresholds per ATNRG spec §5
TAB_COUNT_PROMPT = 3
QUICKLINK_COUNT_PROMPT = 5

# Local state file (best-effort persistence; survives across launches)
DEFAULT_STATE: dict = {
    "tabs_created": 0,
    "quicklinks_clicked": 0,
    "prompts_shown": {
        "after_3rd_tab": False,
        "after_5th_quicklink": False,
    },
    "prompt_dismissed": {
        "after_3rd_tab": False,
        "after_5th_quicklink": False,
    },
}


def _load_state() -> dict:
    """Read the persisted prompt-state file, or return defaults.

    T-NOTE: file lives in the user's local config. If reading or
    parsing fails, fall back to in-memory defaults so the prompt
    logic never breaks the app.
    """
    if not os.path.exists(prompt_counter_path):
        return dict(DEFAULT_STATE)
    try:
        with open(prompt_counter_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return dict(DEFAULT_STATE)
        # Merge with defaults so newly-added keys exist
        for key, val in DEFAULT_STATE.items():
            if key not in data:
                data[key] = val
        return data
    except Exception as e:
        logma.warning(f"[upgrade_prompts] could not load state: {e}")
        return dict(DEFAULT_STATE)


def _save_state(state: dict) -> None:
    """Persist the prompt-state file (best-effort)."""
    try:
        os.makedirs(os.path.dirname(prompt_counter_path), exist_ok=True)
        with open(prompt_counter_path, "w") as fh:
            json.dump(state, fh, indent=2)
    except Exception as e:
        logma.warning(f"[upgrade_prompts] could not save state: {e}")


def is_pro_user(user) -> bool:
    """Whether the given user object is on Pro tier (never gets prompts)."""
    return bool(getattr(user, "has_pro", False)) if user is not None else False


def maybe_prompt_for_upgrade(user, *,
                             on_tab_created: bool = False,
                             on_quicklink_click: bool = False,
                             force_show: bool = False) -> bool:
    """Show an upgrade prompt if the friction threshold is crossed.

    Args:
        user: the in-app user object (must have ``has_pro``).
        on_tab_created: True when a new tab was just created.
        on_quicklink_click: True when a Service Quick Link was clicked.
        force_show: skip the rate-limit / threshold checks (used by the
            "Remove ads" CTA on the Ad tab).

    Returns:
        True if a prompt was shown, False otherwise.
    """
    if is_pro_user(user):
        return False

    state = _load_state()

    if on_tab_created:
        state["tabs_created"] = int(state.get("tabs_created", 0)) + 1
        should_prompt = (
            state["tabs_created"] >= TAB_COUNT_PROMPT
            and not state["prompts_shown"].get("after_3rd_tab", False)
        )
    elif on_quicklink_click:
        state["quicklinks_clicked"] = int(state.get("quicklinks_clicked", 0)) + 1
        should_prompt = (
            state["quicklinks_clicked"] >= QUICKLINK_COUNT_PROMPT
            and not state["prompts_shown"].get("after_5th_quicklink", False)
        )
    else:
        should_prompt = force_show

    if should_prompt:
        prompt_key = (
            "after_3rd_tab" if on_tab_created
            else "after_5th_quicklink" if on_quicklink_click
            else "manual"
        )
        _show_upgrade_prompt(prompt_key, state)
        state["prompts_shown"][prompt_key] = True
        _save_state(state)
        return True

    _save_state(state)
    return False


def _show_upgrade_prompt(prompt_key: str, state: dict) -> None:
    """Display the upgrade prompt QMessageBox.

    T-DESK: uses PyQt5's QMessageBox (lazy import so this module is
    safe to import in tests without a Qt event loop).
    """
    if prompt_key == "after_3rd_tab":
        title = "Going Pro unlocks more tabs"
        message = (
            "You've created several tabs already - nice momentum.\n\n"
            "nchantd Office Pro gives you unlimited tabs, no ads, and "
            "priority support. You can also refer friends for 5% of their "
            "subscription, for a year."
        )
    elif prompt_key == "after_5th_quicklink":
        title = "Want to remove ads?"
        message = (
            "You've explored several of our partner services.\n\n"
            "Upgrade to Pro to remove all ads - or share your referral "
            "code and unlock Pro perks when your first referral converts."
        )
    else:
        title = "Upgrade to nchantd Office Pro"
        message = (
            "Get unlimited tabs, no ads, priority support, and white-label "
            "options. Or share your referral code for 5% of referred subscriptions."
        )

    try:
        from nchantrs.libraries import pyqt
        box = pyqt.QMessageBox()
        box.setIcon(pyqt.QMessageBox.Icon.Information)
        box.setWindowTitle(title)
        box.setText(message)
        box.setStandardButtons(
            pyqt.QMessageBox.StandardButton.Yes
            | pyqt.QMessageBox.StandardButton.No
            | pyqt.QMessageBox.StandardButton.Close
        )
        box.button(pyqt.QMessageBox.StandardButton.Yes).setText("Go Pro")
        box.button(pyqt.QMessageBox.StandardButton.No).setText("Maybe later")
        box.button(pyqt.QMessageBox.StandardButton.Close).setText("Don't show again")
        # Open the upgrade page if user clicks "Go Pro"
        result = box.exec()
        if result == pyqt.QMessageBox.StandardButton.Yes:
            # DESK T-NEW-052: route through the unified URL config.
            from nchantdoffice.utilities.urls import upgrade_compare_url
            pyqt.QDesktopServices.openUrl(
                pyqt.QUrl(upgrade_compare_url())
            )
        elif result == pyqt.QMessageBox.StandardButton.Close:
            state["prompt_dismissed"][prompt_key] = True
        logma.info(f"[upgrade_prompts] shown: {prompt_key}, choice={result}")
    except Exception as e:
        logma.error(f"[upgrade_prompts] QMessageBox failed: {e}", exc_info=True)


def reset_state() -> None:
    """Reset the local prompt state (used by tests + the "show prompts
    again" advanced settings option)."""
    if os.path.exists(prompt_counter_path):
        try:
            os.remove(prompt_counter_path)
            logma.info("[upgrade_prompts] state reset")
        except Exception as e:
            logma.warning(f"[upgrade_prompts] could not reset state: {e}")


__all__ = [
    "TAB_COUNT_PROMPT",
    "QUICKLINK_COUNT_PROMPT",
    "maybe_prompt_for_upgrade",
    "is_pro_user",
    "reset_state",
]
