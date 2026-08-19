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

# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
import datetime as dt
import os
import shutil
import sys
from os.path import dirname, join
from pathlib import Path
from sys import argv

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


def run(args: list[str]) -> None:
    """Run individual tabs with mock data for development purposes

    python runNchantdOffice.py scratch setup - create new file
    python runNchantdOffice.py scratch - continue file
    python runNchantdOffice.py - use the wizard to setup
    """
    # if len(args) > 2:
    # restart()
    app = NchantdOfficeCloak
    wizard = NchantdOfficeApplicationStartupWizard
    nchantment("NchantdOffice", args, app, None, wizard)


if __name__ == "__main__":

    start = dt.datetime.now()
    logma.info("Start")
    run(argv)
    end = dt.datetime.now()
    logma.info(f"End Duration {end - start}")


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
