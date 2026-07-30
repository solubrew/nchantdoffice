"""Sprint 19 — T-NEW-007 store-layer refresh.

Per Sprint 15: ``import_nchantdoffice`` opens the SQLite via
``store.open_sqlite`` and surfaces rows via ``store.refresh_from_sqlite``.
The store-layer refresh was deferred — only the open hook shipped.

This test pins:
  1. ``NchantdOfficeStore.refresh_from_sqlite`` is a real method
     (not just documented).
  2. After opening a SQLite DB that carries an ``app_instance``
     row, ``refresh_from_sqlite`` returns a list of the
     registered secondary instances.
  3. Calling ``refresh_from_sqlite`` before opening a SQLite
     raises a clear error (one-per-instance enforcement).
"""

import os
import sqlite3
import tempfile
from types import SimpleNamespace

import pytest

from nchantdoffice.models import NchantdOfficeStore


def _make_parent():
    """Build a minimal parent so ``NchantdOfficeStore.__init__``
    can wire ``self.parent.instance`` / ``self.app`` /
    ``self.config`` (via ``parent.config``).
    """
    import kahndor  # noqa: F401

    return SimpleNamespace(
        instance=SimpleNamespace(version="0.0.1.0.1.4"),
        app=SimpleNamespace(),
        config=SimpleNamespace(dikt={"dstruct": {}}),
    )


def _make_store_with_sqlite():
    """Return a fresh ``NchantdOfficeStore`` wired to a temp
    SQLite DB that contains an ``app_instance`` row."""
    fd, path = tempfile.mkstemp(suffix=".pyof")
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE app_instance (
            instance_id_txt TEXT,
            name_txt TEXT,
            description_ltxt TEXT,
            is_primary_bit INTEGER,
            application_NCD_txt TEXT,
            application_path_txt TEXT,
            instance_path_txt TEXT,
            version_txt TEXT,
            meta_data_dict TEXT
        );
        """
    )
    conn.execute(
        """INSERT INTO app_instance
           (instance_id_txt, name_txt, description_ltxt,
            is_primary_bit, application_NCD_txt,
            application_path_txt, instance_path_txt,
            version_txt, meta_data_dict)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "uuid-1",
            "secondary-alpha",
            "First secondary instance",
            0,
            "nchantdoffice",
            "/tmp/secondary.pyof",
            "/var/lib/nchantdoffice/secondary.pyof",
            "0.0.1.0.1.4",
            "{}",
        ),
    )
    conn.commit()
    conn.close()
    store = NchantdOfficeStore(
        "test-store", parent=_make_parent(), cfg={"dikt": {"dstruct": {}}}
    )
    return store, path


def test_refresh_from_sqlite_is_real_method():
    """T-NEW-007 full integration: the store must expose
    ``refresh_from_sqlite`` as a callable method (not just a
    documented hook).
    """
    store = NchantdOfficeStore(
        "test", parent=_make_parent(), cfg={"dikt": {"dstruct": {}}}
    )
    assert hasattr(store, "refresh_from_sqlite"), (
        "NchantdOfficeStore must expose refresh_from_sqlite to "
        "complete T-NEW-007 store-layer integration."
    )
    assert callable(getattr(store, "refresh_from_sqlite")), (
        "NchantdOfficeStore.refresh_from_sqlite must be callable."
    )


def test_refresh_from_sqlite_surfaces_app_instance_rows():
    """T-NEW-007 full integration: after open_sqlite, calling
    refresh_from_sqlite must return the registered
    secondary-instance rows from the loaded SQLite DB.
    """
    store, path = _make_store_with_sqlite()
    store.open_sqlite(path)
    rows = store.refresh_from_sqlite()
    assert isinstance(rows, list)
    assert len(rows) == 1
    row = rows[0]
    # The exact column names mirror the YAML schema
    # (nchantrs/models/_data_/applicationmodels.yaml).
    assert row["name_txt"] == "secondary-alpha"
    assert row["instance_path_txt"] == "/var/lib/nchantdoffice/secondary.pyof"


def test_refresh_from_sqlite_without_open_raises():
    """T-NEW-007 one-per-instance guard: calling refresh_from_sqlite
    before open_sqlite must raise a clear error rather than silently
    return empty rows (which would mask import bugs).
    """
    store = NchantdOfficeStore(
        "test", parent=_make_parent(), cfg={"dikt": {"dstruct": {}}}
    )
    with pytest.raises(RuntimeError):
        store.refresh_from_sqlite()
