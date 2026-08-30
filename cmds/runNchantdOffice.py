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
# crow.crowLoad removed
# import crow  # not needed for local system
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


def _parse_run_mode(args: list, cfg: dict) -> str:
    """Extract the ``run-mode`` value from CLI args / cfg / env / defaults.

    Precedence (highest first):
      1. ``cfg["run-mode"]`` — what the launcher or test harness passed in.
      2. ``--run-mode=<value>`` CLI flag.
      3. ``NCHANTDOFFICE_RUN_MODE`` env var (legacy escape hatch;
         not used by the launch entrypoint — only honoured here
         so external test harnesses can flip the mode without
         rewriting the cfg dict).
      4. ``prod`` (default).

    No-op for the actual :func:`urls.set_run_mode` call — the
    launch entrypoint calls that after parsing.
    """
    # 1. cfg dict (primary path — the launch entrypoint passes
    #    cfg={"run-mode": "dev"} into nchantment).
    raw = cfg.get("run-mode") if isinstance(cfg, dict) else None
    if raw is None and isinstance(args, (list, tuple)):
        for a in args:
            if isinstance(a, str) and a.startswith("--run-mode="):
                raw = a.split("=", 1)[1]
                break
            if isinstance(a, str) and a in ("--run-mode", "--run_mode") and args.index(a) + 1 < len(args):
                raw = args[args.index(a) + 1]
                break
    if raw is None:
        raw = os.environ.get("NCHANTDOFFICE_RUN_MODE")
    if raw is None:
        return "prod"
    norm = str(raw).strip().lower()
    return norm or "prod"


def run(args: list[str]) -> None:
    """Run individual tabs with mock data for development purposes

    python runNchantdOffice.py scratch setup - create new file
    python runNchantdOffice.py scratch - continue file
    python runNchantdOffice.py - use the wizard to setup

    ``run-mode`` (DESK T-NEW-053) selects the URL profile at
    launch. The two supported values are:

      ``run-mode: prod`` (default) — external cloud URLs
        (``https://api.nchantdoffice.com``, etc.). The binary
        that ships to end users.

      ``run-mode: dev`` — internal docker stack on the operator's
        LAN (``http://192.168.1.67:8081`` for the API and
        ``http://192.168.1.67:8080`` for the marketing site).
        License bootstrap, embedded browsers, account tab,
        upgrade prompts, ad CTAs all flip to the internal site
        automatically — no config-file editing required.

    The mode can be set via (in order of precedence):
      1. ``cfg["run-mode"]`` passed into this function
      2. ``--run-mode=dev`` CLI flag
      3. ``NCHANTDOFFICE_RUN_MODE`` env var

    Backward compat: the historical ``website_override`` cfg
    key still works — when present, ``run-mode`` defaults to
    ``dev`` if not explicitly set, so existing launch scripts
    that hand-roll the override keep functioning.
    """
    # Parse run-mode BEFORE any URL access. The resolver
    # caches its result on first call; flipping later still
    # works (it invalidates the cache) but doing it here
    # means the very first accessor call already returns the
    # right values.
    cfg = {"website_override": {"https://nchantdoffice.com": "http://192.168.1.67:8081"}}
    run_mode = _parse_run_mode(args, cfg)
    # Legacy: when ``website_override`` is set but ``run-mode``
    # isn't, infer ``dev`` so the existing launch script
    # pattern keeps working without a code change at the
    # call site.
    if run_mode == "prod" and isinstance(cfg, dict) and cfg.get("website_override") and "run-mode" not in cfg:
        run_mode = "dev"

    try:
        from nchantdoffice.utilities.urls import set_run_mode

        set_run_mode(run_mode)
        logma.info(f"[runNchantdOffice] run-mode: {run_mode} " f"(server_base_url will resolve accordingly)")
    except ValueError as exc:
        logma.warning(f"[runNchantdOffice] invalid run-mode {run_mode!r}: {exc}; " f"falling back to prod")
        from nchantdoffice.utilities.urls import set_run_mode

        set_run_mode("prod")

    # if len(args) > 2:
    # restart()  # DISABLED — wipes instance data every launch
    cfg = {"run-mode": "dev"}
    app = NchantdOfficeCloak
    wizard = NchantdOfficeApplicationStartupWizard
    nchantment("NchantdOffice", args, app, cfg, wizard)


if __name__ == "__main__":

    start = dt.datetime.now()
    logma.info("Start")
    run(argv)
    end = dt.datetime.now()
    logma.info(f"End Duration {end - start}")


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
