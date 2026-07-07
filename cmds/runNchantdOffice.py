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
from os.path import abspath, dirname, join
import os
from sys import argv
import datetime as dt
import sys
from pathlib import Path
import shutil

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
if os.environ.get("NCHANTD_WEBENGINE_SOFTWARE") == "1":
    # Opt-in: rule out GPU/compositor blank-surface issues by forcing software
    # rendering. Run with:  NCHANTD_WEBENGINE_SOFTWARE=1 python runNchantdOffice.py
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

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||

sys.path.insert(0, "/home/solubrew/Documents/AIM")
import crow  # Commented out - not needed for local system

crow.crowLoad("NchantdOffice", "DELTA")
from kahndor import kahndor
from nchantrs.nchantrs import nchantment
from nchantdoffice.nchantdoffice import NchantdOfficeCloak
from nchantdoffice.wizards.wizards import NchantdOfficeApplicationStartupWizard
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
log = True

# ====================================================================================================================||
pxcfg = join(here, "_data_", "runMain.yaml")


def restart():
    """"""
    try:
        shutil.rmtree(Path.home() / ".local" / "share" / "nchantdoffice")
        logma.info(f"Removal Complete")
    except Exception as e:
        logma.info(f"Removal Failed")


def run(args):
    """Run individual tabs with mock data for development purposes

    python runNchantdOffice.py scratch setup - create new file
    python runNchantdOffice.py scratch - continue file
    python runNchantdOffice.py - use the wizard to setup
    """
    # if len(args) > 2:
    restart()
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
