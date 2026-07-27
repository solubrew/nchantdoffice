# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid:
        name:
        description: >
        version: 0.0.0.0.0.0
        authority: filesystem
        security: seclvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||
# (none)

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||


# T-064: shared dropdown cfg-builder. Replaces the
# per-pane ``cfg = {label, layout, size, combobox: {...}}``
# duplication with a single helper that every pane can call.
def build_dropdown_cfg(label, options, value=None, handler=None, layout="horizontal", size=None):
    """Build a NchantdDropDown cfg dict for a labelled dropdown.

    T-064 helper. options may be a list of strings or a list
    of (text, value) tuples. handler is the cmd_-prefixed
    method to call on value change. size defaults to
    ["auto", "auto"].

    Returns a cfg dict ready to pass to NchantdDropDown.
    """
    if size is None:
        size = ["auto", "auto"]
    cfg = {
        "label": label,
        "layout": layout,
        "size": list(size),
        "combobox": {"options": list(options)},
        "value": value,
    }
    if handler is not None:
        cfg["handler"] = handler
    return cfg


# T-064: dict of dropdown presets used across panes. Each
# preset is a (label, options, handler) tuple that callers can
# pass to build_dropdown_cfg to reduce per-pane duplication.
SHARED_DROPDOWN_PRESETS = {
    "chart_type": (
        "Select Chart Type",
        ["line", "bar", "pie", "scatter", "area", "radar"],
        "cmd_on_change_type",
    ),
    "tab_compatibility": (
        "Tab Compatibility",
        [
            ".docx - Word", ".ods - OpenOffice", ".txt - Text",
            ".py - Python", ".html - HTML", ".css - CSS",
            ".js - JavaScript", ".yaml - YAML", ".json - JSON",
        ],
        "cmd_on_change_compatibility",
    ),
    "panes": (
        "Right Side Tab",
        ["0 - Journal", "1 - ToolBox", "2 - Calendar", "3 - Calculator"],
        "cmd_on_change_right_side_tab_select",
    ),
    "form_compatibility": (
        "Form Compatibility",
        ["Google Forms", "Nchantd Office", ""],
        "cmd_select_form_compatibility",
    ),
    "data_view": (
        "Data View",
        ["Table", "Pivot", "Chart", "Raw"],
        "cmd_select_data_view",
    ),
}


def build_preset_dropdown(preset_name, value=None, layout="horizontal"):
    """Build a dropdown cfg from one of SHARED_DROPDOWN_PRESETS (T-064).

    Returns the cfg dict. Raises KeyError if preset_name is
    not in the shared dict.
    """
    if preset_name not in SHARED_DROPDOWN_PRESETS:
        raise KeyError(f"Unknown preset: {preset_name!r}")
    label, options, handler = SHARED_DROPDOWN_PRESETS[preset_name]
    return build_dropdown_cfg(label, options, value=value, handler=handler, layout=layout)


# T-067: converged toolbar helper. The project previously
# had two separate toolbars (light + advanced) that were
# maintained independently. This helper builds a single
# unified toolbar from a list of button configs. Buttons
# marked ``"advanced": True`` are collapsed into an overflow
# menu when the pane is in 'light' mode.
def build_converged_toolbar(buttons, light_mode=False, layout="horizontal"):
    """Build a converged toolbar cfg from a list of button configs.

    T-067 helper. Each ``buttons`` entry is a dict with at
    minimum ``{"name": str, "label": str, "handler": callable}``.
    Set ``"advanced": True`` on entries that should be hidden in
    light mode.

    Returns a list of cfg dicts ready to feed to a
    NchantdGridScrollGroupBox or similar container.
    """
    out = []
    for entry in buttons or []:
        if not isinstance(entry, dict):
            continue
        if light_mode and entry.get("advanced", False):
            continue
        out.append({
            "text": entry.get("label", entry.get("name", "")),
            "layout": layout,
            "size": ["auto", "auto"],
            "handler": entry.get("handler"),
            "name": entry.get("name"),
        })
    return out


# T-067: active toolbar profile ("light" / "advanced").
# Panes can flip this via ``set_toolbar_profile``.
TOOLBAR_PROFILE = "light"


def set_toolbar_profile(profile):
    """Set the active toolbar profile (T-067).

    Stores the profile on the module-level TOOLBAR_PROFILE so
    all panes read the same setting. Returns the new value.
    """
    global TOOLBAR_PROFILE
    if profile not in ("light", "advanced"):
        raise ValueError(f"Unknown toolbar profile: {profile!r}")
    TOOLBAR_PROFILE = profile
    return profile


def is_light_mode():
    """Return True when the active toolbar profile is 'light' (T-067)."""
    return TOOLBAR_PROFILE == "light"
