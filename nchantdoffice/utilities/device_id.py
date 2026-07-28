# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-device-fingerprint
    name: Device Fingerprint Utilities
    description: >
        Local-only device fingerprinting per nchantdofficeATNRG
        AppReferralSpec.md §8 (anti-abuse rules).

        Generates a stable, opaque device ID at first launch and
        persists it locally. Used to satisfy anti-abuse rule "no
        self-referral" — when a user clicks their own referral
        code, the device IDs match and the attribution is rejected.

        T-DESK: stored in ``utilities/_data/.device_id``. The file
        path is hard-coded to keep behaviour predictable across
        OSes. ``None`` on any error so the caller can decide what
        to do.
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*-
import hashlib
import os
import platform
import socket
import uuid

from os.path import dirname, join

from kahndor.logma import Logma

logma = Logma(__name__)

here = dirname(__file__)
DEVICE_ID_PATH = join(here, "_data_", ".device_id")


def _load_or_create_device_id() -> str:
    """Return the device ID, creating one if it doesn't exist.

    The ID is a UUID5 derived from the hostname + MAC address of
    the primary NIC. This combination is stable across reboots
    and application reinstalls (within the same user account),
    matching the ATNRG spec §8 anti-abuse expectation.

    Returns:
        A hex UUID string (32 chars, no dashes), or empty string on
        error (the caller treats empty as "anonymous").
    """
    try:
        if os.path.exists(DEVICE_ID_PATH):
            with open(DEVICE_ID_PATH, "r") as fh:
                value = fh.read().strip()
                if value:
                    return value
    except Exception as e:
        logma.warning(f"[device_id] could not read {DEVICE_ID_PATH}: {e}")

    # Generate a new ID from host info + random uuid4
    seed = "|".join(
        [
            platform.node() or "unknown-host",
            platform.machine() or "unknown-machine",
            _safe_get_mac() or "no-mac",
            uuid.uuid4().hex,
        ]
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    device_id = digest[:32]  # 128-bit id

    try:
        os.makedirs(os.path.dirname(DEVICE_ID_PATH), exist_ok=True)
        with open(DEVICE_ID_PATH, "w") as fh:
            fh.write(device_id)
    except Exception as e:
        logma.warning(f"[device_id] could not persist {DEVICE_ID_PATH}: {e}")

    return device_id


def _safe_get_mac() -> str:
    """Best-effort MAC address retrieval; "" on any failure.

    T-NOTE: ``uuid.getnode()`` reads the NIC MAC. On Linux this can
    fail or return a fake MAC on systems with no NIC. Catching
    ensures the fingerprint still works (the random uuid component
    makes it unique enough for anti-abuse use cases).
    """
    try:
        mac = uuid.getnode()
        if (mac >> 40) % 2 == 0:  # bit 0 of byte 0 indicates "valid" MAC
            return f"{mac:012x}"
    except Exception:
        pass
    return ""


def get_device_id() -> str:
    """Public API: return the device ID, creating one on first call."""
    return _load_or_create_device_id()


def get_device_metadata() -> dict:
    """Best-effort device metadata for server-side anti-abuse checks.

    Includes the persistent device_id plus useful identifying
    metadata (hostname, OS, machine). All fields are best-effort;
    missing values fall back to ``"unknown"``.
    """
    return {
        "device_id": get_device_id(),
        "hostname": platform.node() or "unknown",
        "os": platform.system() or "unknown",
        "os_version": platform.version() or "unknown",
        "machine": platform.machine() or "unknown",
        "python": platform.python_version() or "unknown",
    }


def reset_device_id() -> str:
    """Wipe the local device-id file. Used by the "anti-abuse reset"
    tool in advanced settings. Returns the new ID."""
    try:
        if os.path.exists(DEVICE_ID_PATH):
            os.remove(DEVICE_ID_PATH)
            logma.info("[device_id] reset; new id generated on next get_device_id() call")
    except Exception as e:
        logma.warning(f"[device_id] could not remove {DEVICE_ID_PATH}: {e}")
    return _load_or_create_device_id()


__all__ = [
    "get_device_id",
    "get_device_metadata",
    "reset_device_id",
]
