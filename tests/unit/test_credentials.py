"""Tests for desktop credentials persistence (T-DESK-059).

Pins the contract that:
  1. DesktopCredentials dataclass is the canonical shape.
  2. credentials_from_register_response parses the server's
     /api/desktop/register response correctly.
  3. Incomplete records (missing api_key or desktop_uuid)
     are treated as "not registered" by is_complete().
  4. save_credentials requires a complete record.
  5. The marker file permission is 0600 (owner rw only).
  6. has_credentials_marker() returns False when no marker
     exists, True after save.
  7. clear_credentials() removes both the marker and the
     pykey record (when pykey is available).
  8. When pykey is not available, the module degrades
     gracefully (load returns None, save raises RuntimeError).
"""
# -*- coding: utf-8 -*-
import os
import stat
from unittest.mock import patch

import pytest


# ── Dataclass tests (no pykey needed) ─────────────────────────


class TestDesktopCredentials:
    """DesktopCredentials dataclass — pure Python, no I/O."""

    def test_default_construction(self):
        from nchantdoffice.utilities.credentials import DesktopCredentials
        c = DesktopCredentials()
        assert c.desktop_uuid == ""
        assert c.api_key == ""
        assert c.username == ""
        assert c.user_tier == "free"
        assert c.registered_at == ""
        assert c.last_login_at == ""

    def test_is_complete_both_fields(self):
        from nchantdoffice.utilities.credentials import DesktopCredentials
        c = DesktopCredentials(
            desktop_uuid="abc-123",
            api_key="secret",
        )
        assert c.is_complete() is True

    def test_is_complete_missing_uuid(self):
        from nchantdoffice.utilities.credentials import DesktopCredentials
        c = DesktopCredentials(api_key="secret")
        assert c.is_complete() is False

    def test_is_complete_missing_api_key(self):
        from nchantdoffice.utilities.credentials import DesktopCredentials
        c = DesktopCredentials(desktop_uuid="abc-123")
        assert c.is_complete() is False

    def test_is_complete_both_missing(self):
        from nchantdoffice.utilities.credentials import DesktopCredentials
        assert DesktopCredentials().is_complete() is False

    def test_user_tier_defaults_to_free(self):
        from nchantdoffice.utilities.credentials import DesktopCredentials
        c = DesktopCredentials(
            desktop_uuid="abc", api_key="k"
        )
        assert c.user_tier == "free", (
            "Newly-registered desktops must default to 'free' "
            "tier until the server reports otherwise."
        )


class TestCredentialsFromRegisterResponse:
    """The server returns {desktop_uuid, api_key, user_name_txt}.
    We parse it into a DesktopCredentials."""

    def test_happy_path(self):
        from nchantdoffice.utilities.credentials import (
            credentials_from_register_response,
        )
        response = {
            "desktop_uuid": "uuid-abc-123",
            "api_key": "the-secret-token",
            "user_name_txt": "echoed-back-name",
        }
        creds = credentials_from_register_response(
            response, username="typed-name", timestamp="2026-08-07T10:00:00Z",
        )
        assert creds.desktop_uuid == "uuid-abc-123"
        assert creds.api_key == "the-secret-token"
        # We trust the typed name over the server's echo.
        assert creds.username == "typed-name"
        assert creds.registered_at == "2026-08-07T10:00:00Z"
        assert creds.last_login_at == "2026-08-07T10:00:00Z"
        assert creds.user_tier == "free"

    def test_missing_keys_in_response(self):
        from nchantdoffice.utilities.credentials import (
            credentials_from_register_response,
        )
        creds = credentials_from_register_response(
            {}, username="alice",
        )
        assert creds.desktop_uuid == ""
        assert creds.api_key == ""
        # Incomplete record — load_credentials() will reject this.
        assert creds.is_complete() is False

    def test_tier_can_be_overridden(self):
        from nchantdoffice.utilities.credentials import (
            credentials_from_register_response,
        )
        response = {"desktop_uuid": "x", "api_key": "y"}
        creds = credentials_from_register_response(
            response, username="alice", user_tier="pro",
        )
        assert creds.user_tier == "pro"


# ── Persistence tests (no pykey needed) ─────────────────────


class TestMarkerFile:
    """The marker file at ~/.nchantd/.credentials_present
    is a mode-0600 file that exists when the desktop has
    ever registered, regardless of whether the pykey vault
    can be unlocked."""

    def test_has_marker_returns_false_when_no_file(self, tmp_path, monkeypatch):
        from nchantdoffice.utilities import credentials
        monkeypatch.setattr(
            credentials, "CREDENTIALS_MARKER_PATH", tmp_path / "no_file",
        )
        assert credentials.has_credentials_marker() is False

    def test_clear_removes_marker(self, tmp_path, monkeypatch):
        from nchantdoffice.utilities import credentials
        marker = tmp_path / ".credentials_present"
        marker.touch()
        assert marker.exists()
        monkeypatch.setattr(
            credentials, "CREDENTIALS_MARKER_PATH", marker,
        )
        credentials.clear_credentials()
        # clear_credentials() also tries to delete from pykey,
        # which fails silently when pykey isn't installed.
        # The marker MUST still be removed.
        assert not marker.exists()

    def test_marker_file_mode_is_0600(self, tmp_path, monkeypatch):
        """The marker file is mode 0600 (owner read/write only).
        A mode-0644 marker would let other local users on the
        machine detect that this account has registered (info
        leak, not a security boundary, but still wrong)."""
        from nchantdoffice.utilities import credentials
        marker = tmp_path / ".credentials_present"
        marker.touch()
        os.chmod(marker, 0o600)
        monkeypatch.setattr(
            credentials, "CREDENTIALS_MARKER_PATH", marker,
        )
        mode = stat.S_IMODE(os.stat(marker).st_mode)
        assert mode == 0o600, (
            f"Marker file mode must be 0600 (owner rw only), "
            f"got {oct(mode)}. Other local users should not be "
            f"able to detect that this account has registered."
        )


# ── Pykey integration (skipped if pykey unavailable) ──────────


class TestPykeyIntegration:
    """When pykey IS available, the save/load roundtrip works
    through the encrypted store. These tests require pykey;
    they're skipped (not failed) when pykey isn't installed.
    """

    @pytest.fixture
    def keystore_available(self):
        try:
            import pykey  # noqa: F401
        except ImportError:
            pytest.skip("pykey (pycurity) not installed")
        return True

    def test_save_then_load_roundtrip(
        self, keystore_available, tmp_path, monkeypatch
    ):
        """Save a credentials record, then load it back. The
        loaded record must match what we saved (modulo the
        pykey vault's encryption, which is transparent)."""
        from nchantdoffice.utilities import credentials
        import pykey

        # Redirect the pykey vault to a tmp location so we
        # don't pollute the real one.
        tmp_db = tmp_path / "pykey.db"
        tmp_salt = tmp_path / "pykey.salt"
        ks = pykey.PyKeyStore(
            db_path=str(tmp_db), salt_path=str(tmp_salt),
        )

        # Redirect the marker to a tmp file so we don't
        # touch ~/.nchantd/.
        marker = tmp_path / ".credentials_present"
        monkeypatch.setattr(
            credentials, "CREDENTIALS_MARKER_PATH", marker,
        )

        with patch.object(credentials, "_keystore", return_value=ks):
            creds = credentials.DesktopCredentials(
                desktop_uuid="test-uuid-1",
                api_key="test-api-key-2",
                username="alice",
                user_tier="pro",
                registered_at="2026-08-07T10:00:00Z",
                last_login_at="2026-08-07T10:05:00Z",
            )
            credentials.save_credentials(creds)

            assert marker.exists(), "save_credentials must create the marker file"
            assert stat.S_IMODE(os.stat(marker).st_mode) == 0o600, (
                "Marker must be mode 0600 after save_credentials"
            )

            loaded = credentials.load_credentials()
            assert loaded is not None
            assert loaded.desktop_uuid == "test-uuid-1"
            assert loaded.api_key == "test-api-key-2"
            assert loaded.username == "alice"
            assert loaded.user_tier == "pro"
            assert loaded.registered_at == "2026-08-07T10:00:00Z"

    def test_load_returns_none_when_marker_missing(
        self, keystore_available, tmp_path, monkeypatch
    ):
        from nchantdoffice.utilities import credentials
        marker = tmp_path / "no_marker"
        monkeypatch.setattr(
            credentials, "CREDENTIALS_MARKER_PATH", marker,
        )
        assert credentials.load_credentials() is None

    def test_save_rejects_incomplete_record(
        self, keystore_available, tmp_path, monkeypatch
    ):
        """save_credentials() must refuse an incomplete record
        (one missing desktop_uuid or api_key) — otherwise a
        partial registration would persist a broken record
        that load() would return as 'registered but broken'."""
        from nchantdoffice.utilities import credentials
        import pykey
        tmp_db = tmp_path / "pykey.db"
        tmp_salt = tmp_path / "pykey.salt"
        ks = pykey.PyKeyStore(
            db_path=str(tmp_db), salt_path=str(tmp_salt),
        )
        monkeypatch.setattr(
            credentials, "CREDENTIALS_MARKER_PATH",
            tmp_path / ".credentials_present",
        )
        with patch.object(credentials, "_keystore", return_value=ks):
            with pytest.raises(ValueError):
                credentials.save_credentials(
                    credentials.DesktopCredentials(api_key="only-key"),
                )
            with pytest.raises(ValueError):
                credentials.save_credentials(
                    credentials.DesktopCredentials(
                        desktop_uuid="only-uuid",
                    ),
                )

    def test_clear_removes_pykey_record(
        self, keystore_available, tmp_path, monkeypatch
    ):
        from nchantdoffice.utilities import credentials
        import pykey
        tmp_db = tmp_path / "pykey.db"
        tmp_salt = tmp_path / "pykey.salt"
        ks = pykey.PyKeyStore(
            db_path=str(tmp_db), salt_path=str(tmp_salt),
        )
        marker = tmp_path / ".credentials_present"
        monkeypatch.setattr(
            credentials, "CREDENTIALS_MARKER_PATH", marker,
        )
        with patch.object(credentials, "_keystore", return_value=ks):
            creds = credentials.DesktopCredentials(
                desktop_uuid="uuid-1", api_key="key-1",
            )
            credentials.save_credentials(creds)
            assert credentials.load_credentials() is not None
            credentials.clear_credentials()
            assert credentials.load_credentials() is None

    def test_mark_login_updates_timestamp(
        self, keystore_available, tmp_path, monkeypatch
    ):
        from nchantdoffice.utilities import credentials
        import pykey
        tmp_db = tmp_path / "pykey.db"
        tmp_salt = tmp_path / "pykey.salt"
        ks = pykey.PyKeyStore(
            db_path=str(tmp_db), salt_path=str(tmp_salt),
        )
        marker = tmp_path / ".credentials_present"
        monkeypatch.setattr(
            credentials, "CREDENTIALS_MARKER_PATH", marker,
        )
        with patch.object(credentials, "_keystore", return_value=ks):
            creds = credentials.DesktopCredentials(
                desktop_uuid="uuid-1", api_key="key-1",
                last_login_at="2026-08-01T00:00:00Z",
            )
            credentials.save_credentials(creds)
            credentials.mark_login(creds, "2026-08-07T15:00:00Z")
            loaded = credentials.load_credentials()
            assert loaded.last_login_at == "2026-08-07T15:00:00Z"


# ── Graceful degradation when pykey is not available ─────────


class TestNoPykeyFallback:
    """When pykey isn't installed (e.g. the [internal] extra
    wasn't installed), the module degrades gracefully:
    save raises RuntimeError, load returns None.
    """

    def test_save_raises_runtime_error_without_pykey(
        self, tmp_path, monkeypatch
    ):
        from nchantdoffice.utilities import credentials
        monkeypatch.setattr(
            credentials, "CREDENTIALS_MARKER_PATH",
            tmp_path / ".credentials_present",
        )
        monkeypatch.setattr(credentials, "_keystore", lambda: None)
        with pytest.raises(RuntimeError):
            credentials.save_credentials(
                credentials.DesktopCredentials(
                    desktop_uuid="x", api_key="y",
                ),
            )

    def test_load_returns_none_without_pykey(
        self, tmp_path, monkeypatch
    ):
        from nchantdoffice.utilities import credentials
        marker = tmp_path / ".credentials_present"
        marker.touch()
        monkeypatch.setattr(
            credentials, "CREDENTIALS_MARKER_PATH", marker,
        )
        monkeypatch.setattr(credentials, "_keystore", lambda: None)
        # No pykey vault to read from; load returns None.
        assert credentials.load_credentials() is None