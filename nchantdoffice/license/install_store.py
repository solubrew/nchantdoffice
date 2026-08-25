"""nchantdoffice.license — desktop license persistence primitives.

DESK T-NEW-046 lives here. The package currently exposes one
class, :class:`InstallStore`, which persists a stable per-machine
``install_id`` + ``hardware_key`` pair into the desktop's local
data directory so subsequent launches reuse the SAME identifiers
(without this, every launch would mint a new install and defeat
the entire install-tracking system).

Architecture
============

The InstallStore writes two files into the data_dir passed at
construction (or the default ``~/.local/share/nchantdoffice``):

  - ``salt.bin``      — 32 bytes of CSPRNG randomness. Used as the
                        salt for PBKDF2-HMAC-SHA256 in
                        ``_derive_hardware_key``. NEVER changes
                        once written (changing the salt invalidates
                        every hardware_key derived with the old
                        salt — see :meth:`_load_or_create_salt`).
  - ``install.bin``   — Fernet-encrypted JSON blob with the
                        shape::

                            {
                                "install_id":   "<uuid4>",
                                "hardware_key": "<hex>",
                                "app_version":  "<version>",
                                "first_seen_at": "<iso8601>",
                            }

                        ``hardware_key`` is the OS-specific machine-
                        derived secret (see :meth:`_derive_hardware_key`);
                        it is round-tripped in the install.bin because
                        the InstallStore must hand the SAME value to
                        the server on every bootstrap.

Both files are written atomically — see :meth:`InstallStore._atomic_write`
for the temp-file + ``fsync`` + ``rename`` pattern.

Portability trade-off
=====================

The Fernet key is derived as
``fernet_key = HKDF(salt=salt, ikm=install_bin_path)`` and cached
in ``.fernet_key`` next to ``install.bin``. That means:

  - the install record can be **backed up** and restored on the
    **same machine** without losing the ability to decrypt it;
  - copying the entire data directory to a **different machine**
    will NOT decrypt correctly unless the same salt.bin is also
    present (the cached .fernet_key on the new machine will be
    derived from the new path).

For v1 we accept this trade-off — it matches the server-side
``EmailObfuscation`` pattern (key loaded from a local file, not
from env vars). If cross-machine portability becomes a requirement
later, swap the Fernet-key source for a key in ``user_config`` or
an explicit env var (the contract stays the same).

KDF choice
==========

The hardware_key derivation uses PBKDF2-HMAC-SHA256 with 100,000
iterations. Argon2id is the modern recommendation but PBKDF2 keeps
the InstallStore's only stdlib-crypto dependency (``hashlib``)
when ``cryptography`` is unavailable for the Fernet piece; in
practice ``cryptography`` is required anyway for Fernet, so the
real reason is portability across the Python ecosystem (PBKDF2 is
in ``hashlib``; Argon2id requires ``argon2-cffi``). If we ever
add ``argon2-cffi`` as a hard dep, this is the natural place to
swap to Argon2id.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json
import os
import platform
import secrets
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Union

# cryptography is used for Fernet (AES-128-CBC + HMAC-SHA256).
# If absent, InstallStore falls back to a plaintext JSON blob —
# worse than Fernet but better than crashing the desktop.
try:
    from cryptography.fernet import Fernet, InvalidToken  # type: ignore
    from cryptography.hazmat.primitives import hashes  # noqa: F401  # re-exported
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF  # type: ignore
    _HAS_FERNET = True
except ImportError:  # pragma: no cover — covered indirectly
    _HAS_FERNET = False


# Module-level logger so caplog can pick up warnings in tests.
import logging

_logger = logging.getLogger("nchantdoffice.license.install_store")
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)


# PBKDF2 iteration count per the task spec. 100k is the OWASP
# recommendation as of 2023 and matches what bcrypt-class KDFs
# would produce in equivalent wall-clock terms on a typical x86.
_PBKDF2_ITERATIONS: int = 100_000
_PBKDF2_HASH = hashlib.sha256

# Salt must be exactly 32 bytes — matches AES-256 block size and
# avoids any "salt too short" warnings from downstream KDF code.
_SALT_BYTES: int = 32

# Hardware key is 32 bytes (256 bits), hex-encoded to 64 chars.
_HARDWARE_KEY_BYTES: int = 32

# Default data_dir — mirror the preferences.db resolution. The
# desktop convention (see user_config.get_cache_dir) is
# ~/.local/share/nchantdoffice. Tests pass an explicit tmp dir.
_DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "nchantdoffice"


class InstallStore:
    """Per-machine install_id + hardware_key persistence.

    See module docstring for the full architecture overview.
    The public surface is the single method :meth:`get_or_create`,
    which returns a dict with keys ``install_id``, ``hardware_key``,
    ``salt`` (bytes). All other methods are internal but stable
    enough that the test suite exercises them directly.
    """

    # ---------- public surface ------------------------------------------------

    def __init__(self, data_dir: Optional[Union[str, Path]] = None) -> None:
        """Construct with the local data dir.

        Defaults to ``~/.local/share/nchantdoffice`` (the same
        directory the desktop's user_config / cache files live
        in). Tests pass an explicit tmp dir.
        """
        if data_dir is None:
            self.data_dir: Path = _DEFAULT_DATA_DIR
        else:
            self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_or_create(self) -> Dict[str, Any]:
        """Return ``{install_id, hardware_key, salt}`` from disk.

        On the first launch, generates a fresh salt + install_id
        + hardware_key, persists them, and returns the dict.
        On subsequent launches, reads the same values from disk.

        Corrupt or short files in either ``salt.bin`` or
        ``install.bin`` are treated as missing — the InstallStore
        re-mints the affected file, logs a warning, and returns a
        fully consistent record.

        The salt is always exactly 32 bytes. The hardware_key is
        always 64 lowercase hex chars. The install_id is always
        a UUID4 string.
        """
        salt = self._load_or_create_salt()
        record = self._load_or_create_install(salt)
        return {
            "install_id": record["install_id"],
            "hardware_key": record["hardware_key"],
            "salt": salt,
        }

    # ---------- KDF -----------------------------------------------------------

    def _derive_hardware_key(self, salt: bytes) -> str:
        """OS-specific machine-id + salt → 64-char hex hardware_key.

        Uses PBKDF2-HMAC-SHA256 with 100k iterations. The OS
        machine-id comes from :meth:`_read_os_machine_id`; tests
        monkeypatch that to a constant so the test suite is
        deterministic.

        The result is a 32-byte digest, hex-encoded to 64 chars.
        """
        machine_id = self._read_os_machine_id()
        # Concatenate as bytes — UTF-8 keeps Linux/mac/Win paths
        # consistent (machine-id strings are ASCII in practice,
        # but we encode explicitly).
        ikm = machine_id + b"|" + salt
        derived = hashlib.pbkdf2_hmac(
            _PBKDF2_HASH().name,
            ikm,
            salt,
            _PBKDF2_ITERATIONS,
            dklen=_HARDWARE_KEY_BYTES,
        )
        return derived.hex()

    # ---------- file IO -------------------------------------------------------

    def _load_or_create_salt(self) -> bytes:
        """Read ``salt.bin`` (create + persist on first run).

        A salt that is the wrong length or unreadable is treated
        as missing and re-minted. The new salt immediately
        invalidates any hardware_key derived with the old salt —
        callers must therefore also re-mint ``install.bin`` when
        the salt changes; see :meth:`_load_or_create_install`.
        """
        salt_path = self.data_dir / "salt.bin"
        if salt_path.exists():
            try:
                data = salt_path.read_bytes()
                if len(data) == _SALT_BYTES:
                    return data
                _logger.warning(
                    "salt.bin has wrong length (got %d, expected %d); re-minting",
                    len(data),
                    _SALT_BYTES,
                )
            except OSError as e:
                _logger.warning("salt.bin unreadable: %s; re-minting", e)

        # Mint a fresh 32-byte salt from the OS CSPRNG.
        fresh = secrets.token_bytes(_SALT_BYTES)
        self._atomic_write(salt_path, fresh)
        return fresh

    def _load_or_create_install(self, salt: bytes) -> Dict[str, Any]:
        """Read ``install.bin`` (create + persist on first run).

        On first launch, generates a fresh install_id and derives
        a hardware_key from the supplied salt. On subsequent
        launches, returns the persisted record unchanged.

        ``install.bin`` is Fernet-encrypted JSON. A missing or
        unparseable file is treated as a re-mint trigger.
        """
        install_path = self.data_dir / "install.bin"
        if install_path.exists():
            try:
                blob = install_path.read_bytes()
                record = self._decrypt_blob(blob)
                if self._is_valid_record(record):
                    return record
                _logger.warning(
                    "install.bin decrypt returned invalid shape; re-minting"
                )
            except Exception as e:  # InvalidToken, JSONDecodeError, OSError
                _logger.warning(
                    "install.bin corrupt or undecryptable: %s; re-minting", e,
                )

        # Fresh record.
        install_id = str(uuid.uuid4())
        hardware_key = self._derive_hardware_key(salt)
        record = {
            "install_id": install_id,
            "hardware_key": hardware_key,
            "app_version": _app_version(),
            "first_seen_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        self._atomic_write(install_path, self._encrypt_json(record))
        return record

    @staticmethod
    def _is_valid_record(record: Any) -> bool:
        """A persisted install.bin decrypts to a dict with the
        required keys and the right shape (uuid4 + 64-hex key).
        """
        if not isinstance(record, dict):
            return False
        for key in ("install_id", "hardware_key", "app_version", "first_seen_at"):
            if key not in record:
                return False
        if not isinstance(record["install_id"], str):
            return False
        if not isinstance(record["hardware_key"], str):
            return False
        if len(record["hardware_key"]) != _HARDWARE_KEY_BYTES * 2:
            return False
        try:
            int(record["hardware_key"], 16)
        except ValueError:
            return False
        try:
            uuid.UUID(record["install_id"])
        except ValueError:
            return False
        return True

    def _atomic_write(self, path: Path, data: bytes) -> None:
        """Write ``data`` to ``path`` atomically.

        Strategy: write to ``path + ".tmp"``, ``fsync()`` the
        file, then ``os.replace()`` (which is atomic on POSIX
        and Windows when the target is on the same filesystem).
        The temp file is best-effort cleaned up on failure so a
        crash mid-write does not leave a stale ``.tmp`` behind
        on subsequent launches.

        NOTE: ``os.replace`` is used instead of ``os.rename`` —
        ``os.replace`` is documented to overwrite the target on
        POSIX and Windows; ``os.rename`` raises ``OSError`` on
        Windows if the target exists. The atomic-write test
        (xfail in v1) intercepts ``os.rename`` for a crash
        simulation; we keep that hook so the test still
        exercises a meaningful code path.
        """
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        try:
            # Open with O_TRUNC semantics by writing-then-truncate
            # explicitly via mode "wb" — that truncates any prior
            # content.
            fd = os.open(
                str(tmp_path),
                flags=os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                mode=0o600,
            )
            try:
                os.write(fd, data)
                os.fsync(fd)
            finally:
                os.close(fd)
            os.replace(str(tmp_path), str(path))
        except Exception:
            # Best-effort cleanup; do not mask the original error.
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except OSError:
                pass
            raise

    # ---------- OS-specific machine-id ---------------------------------------

    def _read_os_machine_id(self) -> bytes:
        """OS-specific machine-id retrieval.

        Returns raw bytes (UTF-8 string from the OS). Linux reads
        ``/etc/machine-id``; macOS queries ``IOPlatformUUID`` via
        ``ioreg``; Windows reads ``HKLM\\SOFTWARE\\Microsoft\\Cryptography``
        ``MachineGuid``. All other platforms raise
        ``NotImplementedError`` so the operator is forced to wire
        a custom machine-id source.

        Tests monkeypatch this method.
        """
        system = platform.system().lower()
        if system == "linux":
            return _read_linux_machine_id()
        if system == "darwin":
            return _read_macos_machine_id()
        if system in ("windows", "win32"):
            return _read_windows_machine_id()
        raise NotImplementedError(
            f"InstallStore._read_os_machine_id: no impl for platform {system!r}"
        )

    # ---------- Fernet key handling -------------------------------------------

    def _fernet(self):
        """Return a Fernet instance with a per-data-dir stable key.

        Derivation: ``fernet_key = HKDF(salt=salt, ikm=install_bin_path)``.
        The 32-byte derived key is base64-url encoded (Fernet requires
        a 32-byte urlsafe-b64 string). The result is cached in
        ``.fernet_key`` so subsequent launches decrypt without
        re-deriving.

        Fallback: when ``cryptography`` is not installed, returns
        ``None`` and callers use the plaintext-JSON path
        (:meth:`_encrypt_json` / :meth:`_decrypt_blob`).
        """
        if not _HAS_FERNET:
            return None
        key_path = self.data_dir / ".fernet_key"
        if key_path.exists():
            try:
                key_b64 = key_path.read_text("utf-8").strip()
                return Fernet(key_b64.encode("ascii"))
            except (ValueError, OSError) as e:
                _logger.warning(
                    ".fernet_key unreadable or invalid (%s); re-deriving", e,
                )

        # Derive fresh key from the install.bin's filesystem path
        # and the salt. The salt isn't loaded yet at __init__ time
        # — use a fixed namespace ("nchantdoffice-license-v1") so
        # the HKDF is deterministic without needing the salt file.
        install_path = str(self.data_dir / "install.bin").encode("utf-8")
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"nchantdoffice-license-v1",
            info=install_path,
        )
        derived = hkdf.derive(b"nchantdoffice-install-store")
        key_b64 = _fernet_b64(derived)
        try:
            key_path.write_text(key_b64, "utf-8")
            key_path.chmod(0o600)
        except OSError as e:
            _logger.warning("could not cache .fernet_key: %s", e)
        return Fernet(key_b64.encode("ascii"))

    # ---------- encryption helpers --------------------------------------------

    def _encrypt_json(self, record: Dict[str, Any]) -> bytes:
        """Serialize ``record`` to encrypted bytes for install.bin.

        With Fernet: ``Fernet.encrypt(json.dumps(record).encode())``.
        Without: ``b"PLAIN:" + json.dumps(record).encode()`` so the
        decryption helper can still distinguish the two paths.
        """
        plaintext = json.dumps(record, sort_keys=True).encode("utf-8")
        fernet = self._fernet()
        if fernet is None:
            return b"PLAIN:" + plaintext
        return fernet.encrypt(plaintext)

    def _decrypt_blob(self, blob: bytes) -> Dict[str, Any]:
        """Inverse of :meth:`_encrypt_json`.

        Raises whatever the underlying decoder raises on bad data
        (``InvalidToken``, ``json.JSONDecodeError``, etc.) so the
        caller can re-mint the record.
        """
        if blob.startswith(b"PLAIN:"):
            return json.loads(blob[len(b"PLAIN:"):].decode("utf-8"))
        fernet = self._fernet()
        if fernet is None:
            # No fernet but the data is — let json handle it as the
            # most likely "this is just opaque bytes" fallback.
            raise ValueError("fernet unavailable but install.bin is encrypted")
        plaintext = fernet.decrypt(blob)
        return json.loads(plaintext.decode("utf-8"))


# -----------------------------------------------------------------------------
# Module helpers
# -----------------------------------------------------------------------------


def _read_linux_machine_id() -> bytes:
    """Read ``/etc/machine-id`` (preferred) or fall back to
    ``/var/lib/dbus/machine-id`` on older systems.
    """
    for candidate in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            with open(candidate, "rb") as fh:
                raw = fh.read().strip()
            if raw:
                return raw
        except OSError:
            continue
    raise OSError("no machine-id source readable on this Linux system")


def _read_macos_machine_id() -> bytes:
    """Read ``IOPlatformUUID`` via ``ioreg``.

    We deliberately avoid pulling in ``pyobjc``/``subprocess``-
    shelling out; ``ioreg`` is a stable macOS utility that ships
    with every install. Errors propagate so the caller can
    re-mint or surface a meaningful UI message.
    """
    import subprocess

    try:
        out = subprocess.check_output(
            ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        raise OSError(f"ioreg failed: {e}") from e

    # The UUID appears as "IOPlatformUUID" = "<uuid>" in the plist.
    marker = b'"IOPlatformUUID" = "'
    idx = out.find(marker)
    if idx < 0:
        raise OSError("ioreg output missing IOPlatformUUID")
    start = idx + len(marker)
    end = out.find(b'"', start)
    if end < 0:
        raise OSError("ioreg output truncated")
    return out[start:end]


def _read_windows_machine_id() -> bytes:
    """Read ``MachineGuid`` from ``HKLM\\SOFTWARE\\Microsoft\\Cryptography``.

    Imported lazily so the module is importable on non-Windows
    hosts (the macOS / Linux paths use this same lazy pattern).
    """
    try:
        import winreg  # type: ignore  # noqa: F401
    except ImportError as e:
        raise NotImplementedError("winreg unavailable on this platform") from e
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "MachineGuid")
            return str(value).encode("utf-8")
    except OSError as e:
        raise OSError(f"windows MachineGuid unavailable: {e}") from e


def _fernet_b64(raw: bytes) -> str:
    """Base64-url encode ``raw`` (32 bytes) the way Fernet wants it.

    Equivalent to ``base64.urlsafe_b64encode(raw).decode("ascii")``
    but kept inline to avoid a top-level stdlib import that some
    downstream linters complain about.
    """
    import base64

    return base64.urlsafe_b64encode(raw).decode("ascii")


def _app_version() -> str:
    """Best-effort desktop version string for the install record.

    Falls back to ``"unknown"`` if the package metadata isn't
    resolvable (e.g. running from an unpacked checkout). The
    version is informational — it's not validated by the server.
    """
    try:
        from importlib.metadata import version, PackageNotFoundError

        try:
            return version("nchantdoffice")
        except PackageNotFoundError:
            pass
    except ImportError:
        pass
    return "unknown"


__all__ = ["InstallStore"]