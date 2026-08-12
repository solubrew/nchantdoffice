"""Desktop credentials persistence (T-DESK-059).

The server's per-desktop authentication model requires the
desktop to call ``POST /api/desktop/register`` once at first
launch, then send ``x-api-key: *** on every
authenticated request. The api_key is server-generated,
unique per desktop, and never sent to the user.

Persistence requirements:

  1. The api_key MUST be encrypted at rest. We use the
     existing ``pykey.PYKEYSTORE`` (pycurity's PyKeyStore)
     with a private nchantdoffice store.
  2. The desktop_uuid + username + user_tier are stored in
     the same encrypted record (so reading the file alone
     without the keystore passphrase reveals nothing).
  3. The file is mode 0600 (owner read/write only).
  4. On 401 from any server endpoint, the credentials are
     cleared and the user re-prompts for registration.

This module is the SINGLE point of credential persistence.
The rest of the codebase calls ``load_credentials()`` and
``save_credentials()``; nobody else touches pykey.

Locations:

  - PyKeyStore: ``~/.local/share/nchantdoffice/pycurity/secure_store.db``
    (private nchantdoffice store, separate from system's pycurity)
  - Credentials metadata: stored in the same encrypted
    service record under ``map_dict`` (api_key is the
    encrypted one; everything else is plain JSON)
"""
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Callable

if TYPE_CHECKING:
    from pycurity.pykey import PyKeyStore

# The service name used in pykey.PYKEYSTORE. Hard-coded so
# callers don't have to know about pykey.
CREDENTIALS_SERVICE = "nchantdoffice_desktop"

# Private nchantdoffice pycurity store location
NCHANTDOFFICE_PYCURITY_DIR = Path.home() / ".local" / "share" / "nchantdoffice" / "pycurity"
NCHANTDOFFICE_SECURE_STORE = NCHANTDOFFICE_PYCURITY_DIR / "secure_store.db"
NCHANTDOFFICE_SALT_FILE = NCHANTDOFFICE_PYCURITY_DIR / "secure_store.salt"

# On-disk file is a marker only (so we can detect "has
# this desktop ever been registered" without prompting for
# the pykey passphrase). All actual credentials live in
# the pykey store.
CREDENTIALS_MARKER_PATH = Path.home() / ".nchantd" / ".credentials_present"

# Permission for the marker file (mode 0600 = owner rw only).
CREDENTIALS_FILE_MODE = 0o600


@dataclass
class DesktopCredentials:
    """The per-desktop credentials returned by the server's
    ``POST /api/desktop/register`` endpoint, plus metadata
    for client-side UX (username, tier, registered_at).

    Fields:
      desktop_uuid:    server-generated UUID for the desktop
      api_key:         server-generated token; sent in the
                       x-api-key header on every auth call
      username:        the ab_user.username the desktop
                       registered for
      user_tier:       "free" | "pro" | "pro_data" | "enterprise"
                       (used by the FeatureGate to decide
                       which UI to show)
      registered_at:   ISO 8601 timestamp of the first
                       registration. Useful for "you've been
                       a Pro user for 6 months" UX.
      last_login_at:   ISO 8601 timestamp of the most
                       recent successful authenticated call.
                       Updated by mark_login().
    """
    desktop_uuid: str = ""
    api_key: str = ""
    username: str = ""
    user_tier: str = "free"
    registered_at: str = ""
    last_login_at: str = ""

    def is_complete(self) -> bool:
        """A credentials record is "complete" when the server
        has returned both desktop_uuid AND api_key. Incomplete
        records are treated as "not registered" by load().
        """
        return bool(self.desktop_uuid and self.api_key)


# ── pykey import (lazy) ────────────────────────────────────


def _keystore(passphrase: Optional[str] = None) -> Optional["PyKeyStore"]:
    """Return the pykey.PYKEYSTORE instance, or None if pykey
    isn't available (the pycurity project isn't on sys.path).

    Uses the private nchantdoffice store at:
    ~/.local/share/nchantdoffice/pycurity/secure_store.db

    Callers should handle the None case gracefully — the
    desktop can still operate without persistent credentials
    (the user just has to re-register on every launch).
    """
    try:
        import pykey
        return pykey.PYKEYSTORE(
            db_path=str(NCHANTDOFFICE_SECURE_STORE),
            salt_path=str(NCHANTDOFFICE_SALT_FILE),
            passphrase=passphrase,
        )
    except ImportError:
        return None


# ── Vault initialization ───────────────────────────────────


def init_vault(passphrase_prompt: Callable[[], str]) -> bool:
    """Initialize the nchantdoffice pycurity vault with a master password.

    This should be called during the SetupWizard on first install.
    Creates the private store directory and initializes the vault.

    Args:
        passphrase_prompt: A callable that prompts the user for a
            master password (e.g., getpass.getpass).

    Returns:
        True if vault was initialized successfully, False otherwise.
    """
    # Create the private directory
    NCHANTDOFFICE_PYCURITY_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize vault with passphrase
    try:
        import pykey
        ks = pykey.PYKEYSTORE(
            db_path=str(NCHANTDOFFICE_SECURE_STORE),
            salt_path=str(NCHANTDOFFICE_SALT_FILE),
        )
        # Create the vault with the user's passphrase
        ks.create(passphrase=passphrase_prompt())
        return True
    except Exception:
        return False


def vault_exists() -> bool:
    """Check if the nchantdoffice pycurity vault exists."""
    return NCHANTDOFFICE_SECURE_STORE.exists()


# ── Save / load ────────────────────────────────────────────


def save_credentials(creds: DesktopCredentials) -> None:
    """Persist the credentials to the encrypted store.

    The api_key is encrypted by pykey (Fernet under the hood).
    The remaining fields (desktop_uuid, username, user_tier,
    registered_at, last_login_at) are stored as plain JSON in
    pykey's ``map_dict`` field — that's the pykey-native way
    to store non-standard metadata alongside the api_key.

    Also creates a marker file at ~/.nchantd/.credentials_present
    so the desktop can detect "has this user ever registered?"
    without prompting for the pykey passphrase.

    Raises:
        RuntimeError: if pykey is not available.
    """
    if not creds.is_complete():
        raise ValueError(
            "save_credentials requires both desktop_uuid and api_key. "
            "Got an incomplete record — was the registration response "
            "parsed correctly?"
        )
    ks = _keystore()
    if ks is None:
        raise RuntimeError(
            "pykey (pycurity) is not installed; cannot persist "
            "credentials. Install via `pip install -e "
            "../../pycurity` and restart."
        )

    # Store everything in the pykey service record. The api_key
    # is the encrypted primary field; the rest goes into
    # map_dict as plain JSON.
    ks.set(
        CREDENTIALS_SERVICE,
        {
            "api_key": creds.api_key,
            "desktop_uuid": creds.desktop_uuid,
            "username": creds.username,
            "user_tier": creds.user_tier,
            "registered_at": creds.registered_at,
            "last_login_at": creds.last_login_at,
        },
        comment="NchantdOffice desktop credentials (T-DESK-059)",
    )

    # Drop a mode-0600 marker so the desktop can detect
    # "has this user ever registered?" without unlocking
    # the pykey vault. The marker contains no secrets.
    CREDENTIALS_MARKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_MARKER_PATH.touch()
    os.chmod(CREDENTIALS_MARKER_PATH, CREDENTIALS_FILE_MODE)


def load_credentials() -> Optional[DesktopCredentials]:
    """Load the persisted credentials, or None if they don't
    exist OR are incomplete.

    The "incomplete" check is important: if the user is mid-
    registration and the server returned a partial response
    (or the marker file is corrupt), we want to treat that
    as "not registered yet" rather than crashing the app.
    """
    if not CREDENTIALS_MARKER_PATH.exists():
        return None
    ks = _keystore()
    if ks is None:
        return None
    try:
        record = ks.get(CREDENTIALS_SERVICE)
    except KeyError:
        return None
    except Exception:
        # Any pykey error (corrupt vault, wrong passphrase)
        # returns None — the caller will trigger a fresh
        # registration flow.
        return None

    # The api_key is the encrypted primary field. Everything
    # else is in map_dict.
    creds = DesktopCredentials(
        api_key=record.get("api_key", ""),
        desktop_uuid=record.get("desktop_uuid", ""),
        username=record.get("username", ""),
        user_tier=record.get("user_tier", "free"),
        registered_at=record.get("registered_at", ""),
        last_login_at=record.get("last_login_at", ""),
    )
    if not creds.is_complete():
        return None
    return creds


def clear_credentials() -> None:
    """Remove the credentials from the encrypted store and
    delete the marker file. Used when:
      - The user manually resets via Settings -> Privacy
      - The server returns 401 (api_key revoked / rotated)
      - The user runs ``nchantdoffice --reset-credentials``
    """
    ks = _keystore()
    if ks is not None:
        try:
            ks.delete(CREDENTIALS_SERVICE)
        except KeyError:
            pass
        except Exception:
            # Best-effort: even if the delete fails, we want
            # the marker gone so the desktop re-prompts.
            pass
    if CREDENTIALS_MARKER_PATH.exists():
        try:
            CREDENTIALS_MARKER_PATH.unlink()
        except OSError:
            pass


def has_credentials_marker() -> bool:
    """True if a credentials file exists (regardless of whether
    the pykey vault can be unlocked). Used by the UI to decide
    whether to show the registration prompt on startup.

    If the marker exists but load_credentials() returns None,
    that means the pykey passphrase is wrong OR the vault is
    corrupt. Either way, the user needs to re-register.
    """
    return CREDENTIALS_MARKER_PATH.exists()


def mark_login(creds: DesktopCredentials, timestamp: str) -> None:
    """Update last_login_at on an existing credentials record
    and persist. No-op if the credentials aren't loaded.
    """
    if not creds.is_complete():
        return
    creds.last_login_at = timestamp
    save_credentials(creds)


# ── Dataclass helpers ─────────────────────────────────────


def credentials_from_register_response(
    response: dict,
    username: str,
    user_tier: str = "free",
    timestamp: str = "",
) -> DesktopCredentials:
    """Parse the server's ``POST /api/desktop/register``
    response into a DesktopCredentials dataclass.

    The server returns::

        {
            "desktop_uuid": "...",
            "api_key": "...",
            "user_name_txt": "...",
        }

    We don't trust ``user_name_txt`` from the response (the
    client knows the username better than the server does —
    the server is just echoing it back). Instead we take it
    as a constructor arg.

    Args:
        response: the JSON dict from /api/desktop/register
        username: the username the user typed in the
            registration prompt
        user_tier: the tier to assume (default "free"; will
            be updated by the first authenticated call once
            the server's response is parsed)
        timestamp: ISO 8601 string for registered_at. If
            empty, the caller is expected to set it later.

    Returns:
        A populated DesktopCredentials.
    """
    return DesktopCredentials(
        desktop_uuid=response.get("desktop_uuid", ""),
        api_key=response.get("api_key", ""),
        username=username,
        user_tier=user_tier,
        registered_at=timestamp,
        last_login_at=timestamp,
    )
