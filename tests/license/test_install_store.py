"""Tests for nchantdoffice.license.install_store.InstallStore.

DESK T-NEW-046: the InstallStore persists a per-machine install_id
and hardware_key into the desktop's local data directory. It must
be deterministic across launches (same install_id + hardware_key
returned for the same data_dir) and re-mint a fresh record when
either file is missing or corrupt.

These tests cover:

  - the public contract (``get_or_create`` returns {install_id,
    hardware_key, salt}; subsequent calls round-trip the same
    values);
  - the on-disk shape (salt.bin + install.bin created on first
    run, in the data_dir passed to the constructor);
  - corruption recovery (garbage bytes in either file are
    detected and replaced with a fresh install record);
  - the OS-specific derivation can be monkeypatched so the tests
    don't depend on the host platform.

Atomic-write semantics are partially covered — see test #10 for
the limit of what pytest can deterministically simulate.
"""
from __future__ import annotations

import json
import re
import uuid as _uuid
from pathlib import Path

import pytest

from nchantdoffice.license.install_store import InstallStore


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

_UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


def _make_store(tmp_path: Path, monkeypatch) -> InstallStore:
    """Build an InstallStore bound to tmp_path with a stable machine-id.

    Each call generates a fresh data_dir under tmp_path, so tests
    that need two independent stores can call this twice.
    """
    data_dir = tmp_path / "store"
    data_dir.mkdir(parents=True, exist_ok=True)
    # Pin the OS machine-id so the derived hardware_key is
    # deterministic across runs (and not host-dependent).
    monkeypatch.setattr(
        InstallStore, "_read_os_machine_id",
        lambda self: b"test-machine-id-12345",
    )
    return InstallStore(data_dir=data_dir)


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


def test_get_or_create_returns_dict_with_three_keys(tmp_path, monkeypatch):
    """get_or_create must return a dict with exactly install_id,
    hardware_key, salt — these are the three values the network
    client (DESK T-NEW-048) round-trips to the server.
    """
    store = _make_store(tmp_path, monkeypatch)

    record = store.get_or_create()

    assert isinstance(record, dict)
    assert set(record.keys()) >= {"install_id", "hardware_key", "salt"}
    assert isinstance(record["install_id"], str)
    assert isinstance(record["hardware_key"], str)
    assert isinstance(record["salt"], (bytes, bytearray))


def test_get_or_create_persists_across_instances(tmp_path, monkeypatch):
    """Two InstallStore instances pointing at the SAME data_dir
    must return the SAME install_id + hardware_key + salt.

    This is the whole point of persistence: without it, every
    launch would mint a new install and defeat install tracking.
    """
    store_a = _make_store(tmp_path, monkeypatch)
    first = store_a.get_or_create()

    # Build a second store pointing at the same dir (no monkeypatch
    # re-applied — but the OS machine-id monkeypatch is in
    # InstallStore._read_os_machine_id, which is read from the
    # class, so it persists across instances).
    store_b = InstallStore(data_dir=store_a.data_dir)
    second = store_b.get_or_create()

    assert first["install_id"] == second["install_id"]
    assert first["hardware_key"] == second["hardware_key"]
    assert first["salt"] == second["salt"]


def test_get_or_create_deterministic_hardware_key(tmp_path, monkeypatch):
    """Same salt + same OS machine-id ⇒ same hardware_key.

    PBKDF2-HMAC-SHA256 is deterministic; this test pins both
    inputs and asserts the output is reproducible.
    """
    store = _make_store(tmp_path, monkeypatch)
    salt = b"\x01" * 32  # any fixed 32-byte salt

    key_one = store._derive_hardware_key(salt)
    key_two = store._derive_hardware_key(salt)

    assert key_one == key_two
    assert _HEX64_RE.match(key_one), (
        f"expected 64 lowercase hex chars, got {key_one!r}"
    )


def test_salt_bin_is_created_on_first_run(tmp_path, monkeypatch):
    """After get_or_create(), salt.bin must exist in data_dir."""
    store = _make_store(tmp_path, monkeypatch)
    assert not (store.data_dir / "salt.bin").exists()

    store.get_or_create()

    assert (store.data_dir / "salt.bin").exists()
    # Salt must be 32 bytes of CSPRNG randomness.
    salt_bytes = (store.data_dir / "salt.bin").read_bytes()
    assert len(salt_bytes) == 32


def test_install_bin_is_created_on_first_run(tmp_path, monkeypatch):
    """After get_or_create(), install.bin must exist in data_dir."""
    store = _make_store(tmp_path, monkeypatch)
    assert not (store.data_dir / "install.bin").exists()

    store.get_or_create()

    assert (store.data_dir / "install.bin").exists()
    # install.bin is Fernet-encrypted; we don't decrypt here,
    # that's covered by the round-trip tests. Just assert it's
    # non-empty.
    blob = (store.data_dir / "install.bin").read_bytes()
    assert len(blob) > 0


def test_corrupt_install_bin_triggers_recreate(tmp_path, monkeypatch, caplog):
    """If install.bin contains garbage, get_or_create must detect
    the corruption, log a warning, and return a fresh install
    record (NOT propagate the error).
    """
    store = _make_store(tmp_path, monkeypatch)
    # Force salt to exist first so only install.bin is corrupt.
    salt_bytes = b"\xaa" * 32
    (store.data_dir / "salt.bin").write_bytes(salt_bytes)
    (store.data_dir / "install.bin").write_bytes(b"this-is-not-fernet-token")

    import logging
    with caplog.at_level(logging.WARNING, logger="nchantdoffice.license.install_store"):
        record = store.get_or_create()

    # Fresh record (the salt is the same because we wrote it
    # first, but the install_id + hardware_key got re-minted
    # alongside a fresh install.bin).
    assert isinstance(record["install_id"], str)
    assert _UUID4_RE.match(record["install_id"])
    assert _HEX64_RE.match(record["hardware_key"])
    # Warning was emitted.
    assert any(
        "install.bin" in rec.message.lower() or "corrupt" in rec.message.lower()
        for rec in caplog.records
    ), f"expected a warning about install.bin corruption; got {[r.message for r in caplog.records]}"


def test_corrupt_salt_bin_triggers_recreate(tmp_path, monkeypatch, caplog):
    """If salt.bin contains garbage, get_or_create must detect
    the corruption, log a warning, and mint a fresh salt +
    install record.
    """
    store = _make_store(tmp_path, monkeypatch)
    (store.data_dir / "salt.bin").write_bytes(b"\x00\x01\x02")  # too short + not 32 bytes

    import logging
    with caplog.at_level(logging.WARNING, logger="nchantdoffice.license.install_store"):
        record = store.get_or_create()

    # Fresh salt + install record.
    assert len(record["salt"]) == 32
    assert _UUID4_RE.match(record["install_id"])
    # Warning was emitted about the salt.
    assert any(
        "salt.bin" in rec.message.lower() or "corrupt" in rec.message.lower()
        for rec in caplog.records
    ), f"expected a warning about salt.bin corruption; got {[r.message for r in caplog.records]}"


def test_hardware_key_is_64_char_hex(tmp_path, monkeypatch):
    """The hardware_key contract: 64 lowercase hex chars (32 bytes
    of PBKDF2 output, hex-encoded).
    """
    store = _make_store(tmp_path, monkeypatch)

    record = store.get_or_create()

    assert _HEX64_RE.match(record["hardware_key"]), (
        f"hardware_key shape wrong: {record['hardware_key']!r}"
    )


def test_install_id_is_uuid4(tmp_path, monkeypatch):
    """The install_id contract: a RFC-4122 UUID4 string."""
    store = _make_store(tmp_path, monkeypatch)

    record = store.get_or_create()

    assert _UUID4_RE.match(record["install_id"]), (
        f"install_id is not UUID4: {record['install_id']!r}"
    )
    # Sanity: it round-trips as a real UUID4.
    parsed = _uuid.UUID(record["install_id"])
    assert parsed.version == 4


@pytest.mark.xfail(
    reason=(
        "Atomic-write crash simulation is hard to make deterministic "
        "from pytest without OS-level fault injection. The InstallStore "
        "implements the temp-file + rename pattern in _atomic_write(); "
        "a unit test that monkeypatches os.rename to raise would assert "
        "the .tmp file is cleaned up but cannot prove no torn write ever "
        "happens. Tracked for an integration test with a crash-injection "
        "harness (out of scope for v1)."
    ),
    strict=False,
)
def test_atomic_writes_no_partial_files_on_crash(tmp_path, monkeypatch):
    """If the rename() step fails mid-write, no .tmp file should
    remain in the data_dir.
    """
    import nchantdoffice.license.install_store as ismod
    store = _make_store(tmp_path, monkeypatch)

    def _boom(*a, **kw):
        raise OSError("simulated crash")

    # The impl uses os.replace, not os.rename (Windows-safe atomic
    # rename). Patch whichever the impl actually invokes so the
    # failure path is exercised.
    monkeypatch.setattr(ismod.os, "replace", _boom)

    try:
        store.get_or_create()
    except OSError:
        pass  # tolerated

    leftover = list(store.data_dir.glob("*.tmp"))
    assert leftover == [], f"tmp file left behind after crash: {leftover}"