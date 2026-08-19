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
# ======================================Standard Library Modules======================================================|
import argparse
import datetime as dt
import os
import shutil
import sys
import time
from os.path import dirname, join
from pathlib import Path
from sys import argv
from typing import Any

# ---- QtWebEngine render diagnostics + software-render lever -------------------
# These MUST be set before nchantrs (and therefore Qt/QtWebEngine) is imported
# below, or they have no effect. Logging goes through print() because Logma's
# handlers are not configured this early.
_WEBENGINE_ENV_KEYS = (
    "XDG_SESSION_TYPE",
    "WAYLAND_DISPLAY",
    "DISPLAY",
    "QT_QPA_PLATFORM",
    "QT_OPENGL",
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "QTWEBENGINE_DISABLE_GPU_THREAD",
    "LIBGL_ALWAYS_SOFTWARE",
)
print("[runNchantdOffice] pre-Qt webengine env:", {k: os.environ.get(k) for k in _WEBENGINE_ENV_KEYS})
# T-NEW-070 (DESK-4 hard-break): NCHANT_WEBENGINE_SOFTWARE
# env var removed. Software-render mode now comes from
# the user config file via
# nchantdoffice.utilities.user_config.get_webengine_software_render().
#
# Override via:
#   ~/.config/nchantdoffice/config.yaml:
#     webengine:
#       software_render: true
# OR via a project-local nchantdoffice.yaml.


# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||

sys.path.insert(0, "/home/solubrew/Documents/AIM")
import crow  # Commented out - not needed for local system

crow.crowLoad("NchantdOffice", "DELTA")
from kahndor.logma import Logma
from nchantrs.nchantrs import nchantment

from nchantdoffice.nchantdoffice import NchantdOfficeCloak
from nchantdoffice.utilities.user_config import (  # noqa: E402
    get_webengine_software_render,
    write_default_config,
)
from nchantdoffice.wizards.wizards import NchantdOfficeApplicationStartupWizard

logma = None  # noqa: F821  # placeholder until refactor

write_default_config()  # idempotent — first-run setup

# T-NEW-042 (DESK-1): record one app-open on every desktop
# launch. Best-effort — wrapped in try/except so a network
# failure never blocks app launch. Reads the per-install
# user UUID from user_config (which was generated/persisted
# by NchantdOfficeUser.persist_uuid() in DESK-0).
try:
    from nchantdoffice.utilities.referral import ReferralAPIClient
    from nchantdoffice.utilities.user_config import get_user_uuid

    _user_uuid = get_user_uuid()
    if _user_uuid:
        ReferralAPIClient().record_app_open(_user_uuid)
except Exception as _app_open_err:
    logma.info(f"[launcher] record_app_open best-effort failed " f"(non-blocking): {_app_open_err}")

if get_webengine_software_render():
    # Opt-in: rule out GPU/compositor blank-surface issues by forcing software
    # rendering. Set in user_config.yaml: webengine.software_render: true
    _flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        _flags + " --disable-gpu --disable-gpu-compositing --disable-software-rasterizer --no-sandbox"
    ).strip()
    os.environ["QT_OPENGL"] = "software"
    os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
    print(
        "[runNchantdOffice] SOFTWARE RENDERING FORCED ->",
        {k: os.environ.get(k) for k in ("QTWEBENGINE_CHROMIUM_FLAGS", "QT_OPENGL", "LIBGL_ALWAYS_SOFTWARE")},
    )

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
log = True

# ====================================================================================================================||
pxcfg = join(here, "_data_", "runMain.yaml")


def restart() -> None:
    """"""
    try:
        shutil.rmtree(Path.home() / ".local" / "share" / "nchantdoffice")
        logma.info("Removal Complete")
    except Exception:
        logma.info("Removal Failed")


def _build_dispatch(argv: list[str]) -> dict[str, Any]:
    """T-NEW-169 WIRE-1: parse argv into a dispatch dict.

    Two modes:
    - `argv` contains `document --type <name> [--path <file>]`:
      return `{"mode": "document", "type": <name>, "path": <path>}`.
    - `argv` is empty / has unrecognised args:
      return `{"mode": "main", "type": None, "path": None}` for the
      default main-app boot.

    The dict shape is what `run(args)` expects (per the
    operator-approved T-NEW-169 dispatch design -- a dict literal
    rather than an if/elif chain, so future per-type wire-ups
    (WIRE-3) can read `args["type"]` and look up the class).
    """
    parser = argparse.ArgumentParser(prog="runNchantdOffice", add_help=True)
    subparsers = parser.add_subparsers(dest="mode")

    # The default subcommand is `main`. argparse's standard idiom is
    # to require an explicit subcommand; we relax that to keep
    # `python runNchantdOffice.py` (no args) booting the full main
    # app unchanged.
    parser.set_defaults(mode="main", type=None, path=None)

    # The standalone-document subcommand: `document --type <name>`
    document = subparsers.add_parser(
        "document",
        help="boot a standalone 2-pane minimal shell for one document type",
    )
    document.add_argument(
        "--type",
        required=True,
        choices=["script", "notebook", "image", "form"],
        help="document type to instantiate",
    )
    document.add_argument(
        "--path",
        default=None,
        help="optional pre-load path (.pyof for notebook, file for "
        "image/script/form)",
    )

    parsed = parser.parse_args(argv)
    return {
        "mode": parsed.mode,
        "type": getattr(parsed, "type", None),
        "path": getattr(parsed, "path", None),
    }


def run(args: dict[str, Any]) -> None:
    """T-NEW-169 WIRE-1: dispatch the launch based on `args["mode"]`.

    `args["mode"] == "main"` (the default when no subcommand is
    passed) boots the full NchantdOfficeCloak application. This is
    the unchanged pre-fix behaviour; the `nchantment()` entry
    point is preserved.

    `args["mode"] == "document"` boots a standalone 2-pane
    minimal shell for one document type (T-NEW-169 WIRE-2 +
    WIRE-3). WIRE-1 only ships the routing; the WIRE-2 class
    `NchantdDocumentStandaloneWindow` lands in the next commit.
    Until WIRE-2 ships, the standalone branch logs an info-level
    "not yet implemented" message and exits cleanly so operators
    see the routing is taking effect (the argparser exit code
    is 0; the standalone boot is the responsibility of WIRE-2).
    """
    mode = args.get("mode", "main")
    if mode == "main":
        app = NchantdOfficeCloak
        wizard = NchantdOfficeApplicationStartupWizard
        nchantment("NchantdOffice", args, app, None, wizard)
        return
    if mode == "document":
        logma.info(  # noqa: F821  # logma module-level placeholder pattern
            f"[runNchantdOffice] document subcommand: "
            f"type={args.get('type')!r} path={args.get('path')!r}"
        )
        logma.info(  # noqa: F821  # logma module-level placeholder pattern
            "[runNchantdOffice] standalone 2-pane boot: "
            "T-NEW-169 WIRE-2 (NchantdDocumentStandaloneWindow class) "
            "lands next. Until WIRE-2 ships, this subcommand logs "
            "the request and exits cleanly."
        )
        return
    raise ValueError(f"unknown mode {mode!r}")


if __name__ == "__main__":

    start = dt.datetime.now()
    # T-NEW-171 SURVEY-1: monotonic-clock boot anchor.
    # dt.datetime.now() is wall-clock (could skip backward
    # on NTP adjust); time.monotonic() is what operators
    # want for performance measurement. The End Duration
    # line below stays as the human-readable hh:mm:ss.sss,
    # but the SURVEY-1 line gives the precise elapsed-ms
    # for performance triage.
    _t171_boot_start = time.monotonic()
    logma.info("Start")
    logma.info(
        f"[T-NEW-171 SURVEY] nchantdoffice boot start: pid={os.getpid()}"
    )
    run(_build_dispatch(argv))
    end = dt.datetime.now()
    logma.info(f"End Duration {end - start}")
    logma.info(
        f"[T-NEW-171 SURVEY] nchantdoffice boot total: "
        f"{(time.monotonic() - _t171_boot_start) * 1000:.1f}ms"
    )


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
