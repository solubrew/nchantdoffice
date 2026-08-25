"""nchantdoffice.license — desktop entitlement persistence.

DESK T-NEW-047 lives here. This module exposes
:class:`EntitlementCache`, which persists the server-issued
``entitlement_token`` + ``envelope`` so the desktop can gate
features WITHOUT a network round-trip on every widget render.

Architecture
============

The cache writes two files into the ``data_dir`` passed at
construction (or the default ``~/.local/share/nchantdoffice``):

  - ``entitlement.bin`` — Fernet-encrypted JSON::

        {
            "token":     "<fernet-string>",
            "envelope":  {<server-side envelope dict>},
            "stored_at": "<iso8601>",
            "stale":     true | false,
        }

    ``stale`` is the LAST KNOWN stale flag, flipped to True by
    :meth:`EntitlementCache.mark_stale` when the startup refresh
    flow sees a 410 (revoked) or 401 (api_key rotated). The
    cache does NOT delete the record in that case — the tier
    gate continues to gate features based on the LAST KNOWN
    tier until the next successful refresh, so a revoked user
    can't get into pro features for free just by ignoring the
    stale flag.

  - ``.fernet_key`` — cached Fernet key, derived from the
    ``entitlement.bin`` filesystem path (no salt, no machine-id).
    This mirrors :class:`InstallStore` but simpler: the
    entitlement cache has no per-install secret of its own —
    it just needs the bin to be unreadable on disk to a
    casual snooper. Same trade-off as InstallStore: portable
    to backups of the SAME machine only (the derived key
    encodes the absolute filesystem path).

Atomic writes use the same temp-file + ``fsync`` + ``os.replace``
pattern as :class:`InstallStore._atomic_write`. See that method
for the rationale on why we use ``os.replace`` rather than
``os.rename``.

Failure modes
=============

The cache is DELIBERATELY TOLERANT:

  - missing ``entitlement.bin``  → ``load()`` returns ``None``;
  - corrupt or un-decryptable blob → ``load()`` returns ``None``;
  - read errors (``OSError``) → ``load()`` returns ``None``;
  - ``is_expired_or_close()`` on missing cache → ``True`` (so
    the startup flow falls back to /refresh).

This is symmetric with :class:`InstallStore`'s "treat corrupt as
missing" stance. The caller (the remote client in DESK T-NEW-048)
treats ``None`` as "go bootstrap or refresh via the network".
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

# cryptography is used for Fernet (AES-128-CBC + HMAC-SHA256).
# Mirrors InstallStore's import-time try/except — the cache
# degrades to a plaintext-JSON blob when cryptography is not
# installed (worse than Fernet but better than crashing).
try:
    from cryptography.fernet import Fernet, InvalidToken  # type: ignore
    from cryptography.hazmat.primitives import hashes  # noqa: F401
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF  # type: ignore
    _HAS_FERNET = True
except ImportError:  # pragma: no cover — covered indirectly
    _HAS_FERNET = False


# Module-level logger so caplog can pick up warnings in tests.
_logger = logging.getLogger("nchantdoffice.license.entitlement_cache")
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)


# Cache file names. Kept module-level so tests can sniff for them.
_ENTITLEMENT_BIN = "entitlement.bin"
_FERNET_KEY_FILE = ".fernet_key"

# Fernet-key HKDF info byte string — different from InstallStore's
# so the .fernet_key files don't collide if both classes share a
# data_dir.
_FERNET_HKDF_SALT = b"nchantdoffice-license-v1"
_FERNET_HKDF_INFO = b"nchantdoffice-entitlement-cache"

# Default data_dir mirrors InstallStore.
_DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "nchantdoffice"


def _fernet_b64(raw: bytes) -> str:
    """Base64-url encode ``raw`` (32 bytes) the way Fernet wants it.

    Equivalent to ``base64.urlsafe_b64encode(raw).decode("ascii")``
    but kept inline to avoid a top-level stdlib import that
    some downstream linters complain about.
    """
    import base64

    return base64.urlsafe_b64encode(raw).decode("ascii")


class EntitlementCache:
    """On-disk cache of the server-issued entitlement token + envelope.

    See module docstring for the full architecture overview.

    The public surface is :meth:`load`, :meth:`store`,
    :meth:`mark_stale`, :meth:`clear`, and :meth:`is_expired_or_close`.
    All other methods are internal but stable enough that the
    test suite exercises them directly.
    """

    # ---------- public surface ------------------------------------------------

    def __init__(self, data_dir: Optional[Union[str, Path]] = None) -> None:
        """Construct with the local data dir.

        Defaults to ``~/.local/share/nchantdoffice`` (the same
        directory the InstallStore uses). Tests pass an explicit
        tmp dir.
        """
        if data_dir is None:
            self.data_dir: Path = _DEFAULT_DATA_DIR
        else:
            self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> Optional[Dict[str, Any]]:
        """Return ``{token, envelope, stored_at, stale}`` from disk.

        Returns ``None`` on any failure (missing file, corruption,
        schema mismatch). The caller treats ``None`` as "go
        bootstrap or refresh via the network" — the cache is
        deliberately tolerant, matching InstallStore's stance.
        """
        bin_path = self.data_dir / _ENTITLEMENT_BIN
        if not bin_path.exists():
            return None
        try:
            blob = bin_path.read_bytes()
            record = self._decrypt_blob(blob)
        except Exception as e:  # noqa: BLE001 — tolerant by design
            _logger.warning(
                "entitlement.bin corrupt or undecryptable: %s; treating as missing",
                e,
            )
            return None

        if not self._is_valid_record(record):
            _logger.warning(
                "entitlement.bin decrypted to invalid shape; treating as missing",
            )
            return None
        return record

    def store(self, token: str, envelope: Dict[str, Any]) -> None:
        """Persist ``{token, envelope, stored_at, stale=False}``.

        Atomic write — temp file + ``os.replace``, same pattern as
        :meth:`InstallStore._atomic_write`.

        ``token`` is the server-issued Fernet string. ``envelope``
        is the dict decoded from the JWT-shaped payload (see the
        module docstring for the expected keys).
        """
        record = {
            "token": token,
            "envelope": envelope,
            "stored_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "stale": False,
        }
        bin_path = self.data_dir / _ENTITLEMENT_BIN
        self._atomic_write(bin_path, self._encrypt_json(record))

    def mark_stale(self) -> None:
        """Flip the stored ``stale`` flag to True.

        Used by the startup refresh flow when ``/refresh`` returns
        410 (revoked) or 401 (api_key rotated). The gate's
        ``requires_tier()`` decorator continues to gate features
        based on the LAST KNOWN tier until the next successful
        refresh — so a revoked user can't get into pro features
        for free just by ignoring the stale flag.

        No-op if the cache is missing or un-decryptable; the next
        successful ``store()`` will set ``stale=False`` again.
        """
        record = self.load()
        if record is None:
            return
        record["stale"] = True
        bin_path = self.data_dir / _ENTITLEMENT_BIN
        self._atomic_write(bin_path, self._encrypt_json(record))

    def clear(self) -> None:
        """Remove the cache (logout / fresh-install path).

        No-op if the file isn't there. We don't touch
        ``.fernet_key`` — re-deriving the key is cheap and the
        cache key stays correct across logout/login cycles.
        """
        bin_path = self.data_dir / _ENTITLEMENT_BIN
        try:
            if bin_path.exists():
                bin_path.unlink()
        except OSError as e:
            _logger.warning("entitlement.bin unlink failed: %s", e)

    def is_expired_or_close(self, threshold_seconds: int = 12 * 3600) -> bool:
        """True if the cached envelope is past expiry or within
        ``threshold_seconds`` of expiry.

        Used by the startup flow to decide whether to call
        ``/refresh``.

        Returns ``True`` when:

          - no cache is on disk (the safe default — fall back to
            the network);
          - the cached envelope has no parseable ``exp`` field;
          - the current wall-clock time is past ``exp``;
          - the envelope expires within ``threshold_seconds`` of
            now (default: 12 hours).
        """
        record = self.load()
        if record is None:
            return True
        envelope = record.get("envelope") or {}
        exp = envelope.get("exp")
        if not isinstance(exp, (int, float)):
            # No usable expiry — be conservative and refresh.
            return True
        now = dt.datetime.now(dt.timezone.utc).timestamp()
        return now >= float(exp) - threshold_seconds

    # ---------- validation ----------------------------------------------------

    @staticmethod
    def _is_valid_record(record: Any) -> bool:
        """A persisted ``entitlement.bin`` decrypts to a dict with
        the required wrapper fields and an envelope dict.

        We deliberately do NOT validate every envelope field —
        the server's envelope shape can evolve. We only assert
        the wrapper contract that this cache owns.
        """
        if not isinstance(record, dict):
            return False
        for key in ("token", "envelope", "stored_at", "stale"):
            if key not in record:
                return False
        if not isinstance(record["token"], str):
            return False
        if not isinstance(record["envelope"], dict):
            return False
        if not isinstance(record["stored_at"], str):
            return False
        if not isinstance(record["stale"], bool):
            return False
        return True

    # ---------- atomic write --------------------------------------------------

    def _atomic_write(self, path: Path, data: bytes) -> None:
        """Write ``data`` to ``path`` atomically.

        Strategy: write to ``path + ".tmp"``, ``fsync()`` the
        file, then ``os.replace()`` (atomic on POSIX and Windows
        when both paths are on the same filesystem). The temp
        file is best-effort cleaned up on failure so a crash
        mid-write does not leave a stale ``.tmp`` behind on
        subsequent launches.

        This is the same pattern used by
        :meth:`InstallStore._atomic_write` — kept independent
        (not shared) so a change to one doesn't ripple to the
        other.
        """
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        try:
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

    # ---------- Fernet key handling -------------------------------------------

    def _fernet(self) -> Optional[object]:
        """Return a Fernet instance with a per-data-dir stable key.

        Derivation: ``fernet_key = HKDF(salt=fernet_salt, info=entitlement_bin_path)``.
        The 32-byte derived key is base64-url encoded (Fernet
        requires a 32-byte urlsafe-b64 string). The result is
        cached in ``.fernet_key`` so subsequent launches decrypt
        without re-deriving.

        Fallback: when ``cryptography`` is not installed, returns
        ``None`` and callers use the plaintext-JSON path
        (:meth:`_encrypt_json` / :meth:`_decrypt_blob`).
        """
        if not _HAS_FERNET:
            return None
        key_path = self.data_dir / _FERNET_KEY_FILE
        if key_path.exists():
            try:
                key_b64 = key_path.read_text("utf-8").strip()
                return Fernet(key_b64.encode("ascii"))
            except (ValueError, OSError) as e:
                _logger.warning(
                    ".fernet_key unreadable or invalid (%s); re-deriving", e,
                )

        # Derive a fresh key from the entitlement.bin's absolute
        # filesystem path. No salt of our own — the salt is the
        # fixed ``_FERNET_HKDF_SALT`` byte string above (it just
        # disambiguates from any other HKDF use in the same process).
        bin_path = str(self.data_dir / _ENTITLEMENT_BIN).encode("utf-8")
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=_FERNET_HKDF_SALT,
            info=_FERNET_HKDF_INFO + b"|" + bin_path,
        )
        derived = hkdf.derive(b"nchantdoffice-entitlement-cache")
        key_b64 = _fernet_b64(derived)
        try:
            key_path.write_text(key_b64, "utf-8")
            key_path.chmod(0o600)
        except OSError as e:
            _logger.warning("could not cache .fernet_key: %s", e)
        return Fernet(key_b64.encode("ascii"))

    # ---------- encryption helpers --------------------------------------------

    def _encrypt_json(self, record: Dict[str, Any]) -> bytes:
        """Serialize ``record`` to encrypted bytes for entitlement.bin.

        With Fernet: ``Fernet.encrypt(json.dumps(record).encode())``.
        Without: ``b"PLAIN:" + json.dumps(record).encode()`` so the
        decryption helper can distinguish the two paths.
        """
        plaintext = json.dumps(record, sort_keys=True).encode("utf-8")
        fernet = self._fernet()
        if fernet is None:
            return b"PLAIN:" + plaintext
        return fernet.encrypt(plaintext)  # type: ignore[union-attr]

    def _decrypt_blob(self, blob: bytes) -> Dict[str, Any]:
        """Inverse of :meth:`_encrypt_json`.

        Raises whatever the underlying decoder raises on bad data
        (``InvalidToken``, ``json.JSONDecodeError``, etc.) so the
        caller can treat the failure as a missing cache.
        """
        if blob.startswith(b"PLAIN:"):
            return json.loads(blob[len(b"PLAIN:"):].decode("utf-8"))
        fernet = self._fernet()
        if fernet is None:
            # No fernet but the data is encrypted — surface a
            # meaningful error rather than silently returning
            # garbage.
            raise ValueError("fernet unavailable but entitlement.bin is encrypted")
        plaintext = fernet.decrypt(blob)  # type: ignore[union-attr]
        return json.loads(plaintext.decode("utf-8"))


__all__ = ["EntitlementCache"]
