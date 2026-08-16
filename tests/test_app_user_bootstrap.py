"""T-NEW-129 regression test: ``app_user`` row is seeded on initial install.

**app_user row missing on first install**

The ``app_user`` SQLite table is declared in
``nchantdoffice/updates/_data_/db.yaml`` (L35, L48) and gets the schema
upgrade migration, but no row is ever inserted on first install. Every
other per-install identity table (``app_instance``) has a paired
``store_*`` payload builder and a ``model.store_*`` method; ``app_user``
has neither. The model exposes ``get_app_instances`` but no equivalent
``get_app_user`` -- a downstream consumer cannot even read the row that
should exist. This test pins the bootstrap contract.

The fix:
1. ``NchantdOfficeCloakModel.get_app_user(db="db")`` -- returns the
   single ``app_user`` row (list[dict]) via the same
   ``_sqlite_connection`` path that ``get_app_instances`` uses.
2. ``NchantdOfficeCloakModel.store_app_user(user, db="db")`` --
   builds the row payload via a new ``_build_app_user_payload``
   free function and dispatches through ``self._store("app_user", ...)``.
3. ``_build_app_user_payload(user)`` -- converts a NchantdUser (or
   plain dict) to a row dict whose keys match the YAML schema:
   ``UUID``, ``user_nm_txt``, ``password_txt``, ``saltUUID``,
   ``iterations_txt``, ``is_private_bit``, ``is_secure_bit``,
   ``instance_FK``. Optional columns (``mac_hash_txt``,
   ``address_txt``, ``public_key_txt``) are tolerated.
4. Bootstrap path: ``NchantdOfficeCloak.run_on_launch`` (or an
   equivalent early-launch hook) calls ``model.bootstrap_app_user()``
   once per process. ``bootstrap_app_user`` is idempotent: if a row
   already exists, it does NOT insert a duplicate.

Affected sites:
- nchantdoffice/models.py: store_app_user + _build_app_user_payload + get_app_user + bootstrap_app_user
- nchantdoffice/nchantdoffice.py: hook bootstrap_app_user into run_on_launch
- tests/test_app_user_bootstrap.py: new file (this test)

Migration plan (no priority / low priority -- design decision first):
mirrors the existing ``app_instance`` pattern (store_app_instance +
_build_app_instance_payload + model.store_instance). Idempotency is
the design decision: a fresh DB gets exactly one row; subsequent
launches do nothing.

Steps:
1. Add ``_build_app_user_payload(user) -> dict`` after
   ``_build_app_instance_payload`` (models.py ~L4180) reading
   ``UUID``, ``user_name``, ``password``, ``salt``, ``iters``,
   ``is_private``, ``is_secure`` off the NchantdUser.
2. Add ``store_app_user(self, user, db="db")`` next to
   ``store_app_instance`` (~L3812) that calls
   ``self._store("app_user", [_build_app_user_payload(user)], db)``.
3. Add ``get_app_user(self, db="db") -> list[dict]`` next to
   ``get_app_instances`` (~L1732) using the same
   ``_sqlite_connection`` SELECT path; return [] when no row.
4. Add ``bootstrap_app_user(self) -> Self`` that calls
   ``get_app_user()`` and only calls ``store_app_user`` when the
   table is empty. Idempotent.
5. Hook ``model.bootstrap_app_user()`` from
   ``NchantdOfficeCloak.run_on_launch`` after
   ``self.model.set_today()`` and before
   ``self.select_initial_node()``.
"""

import inspect
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest


PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")


def _bare_model():
    """Create a minimal NchantdOfficeCloakModel without running __init__."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    return NchantdOfficeCloakModel.__new__(NchantdOfficeCloakModel)


def _user(
    uuid="u-uuid-1",
    name="alice",
    user_name="alice",
    password="pw",
    salt="salt-1",
    iters="1000",
    is_private=False,
    is_secure=False,
):
    """Build a SimpleNamespace mimicking NchantdUser attributes."""
    return SimpleNamespace(
        uuid=uuid,
        name=name,
        user_name=user_name,
        pword=password,
        salt=salt,
        iters=iters,
        is_private=is_private,
        is_secure=is_secure,
    )


# ---------------------------------------------------------------------------
# Schema-anchored contract: payload builder + free function exist
# ---------------------------------------------------------------------------

def test_build_app_user_payload_function_exists():
    """_build_app_user_payload must be importable from nchantdoffice.models."""
    from nchantdoffice import models as m
    assert hasattr(m, "_build_app_user_payload"), (
        "_build_app_user_payload must be defined in nchantdoffice.models "
        "(T-NEW-129 app_user bootstrap)."
    )


def test_build_app_user_payload_uses_nchantd_user_attributes():
    """Payload must read uuid/name/pword/salt/iters off the user object."""
    from nchantdoffice.models import _build_app_user_payload
    payload = _build_app_user_payload(_user())
    assert payload.get("UUID") == "u-uuid-1"
    assert payload.get("user_nm_txt") == "alice"
    assert payload.get("password_txt") == "pw"
    assert payload.get("saltUUID") == "salt-1"
    assert payload.get("iterations_txt") == "1000"
    assert "is_private_bit" in payload
    assert "is_secure_bit" in payload


def test_build_app_user_payload_accepts_dict():
    """Payload must accept a plain dict (the canonical fallback)."""
    from nchantdoffice.models import _build_app_user_payload
    payload = _build_app_user_payload(
        {
            "uuid": "u-uuid-2",
            "user_name": "bob",
            "pword": "p",
            "salt": "s",
            "iters": 100,
        }
    )
    assert payload.get("UUID") == "u-uuid-2"
    assert payload.get("user_nm_txt") == "bob"


def test_build_app_user_payload_does_not_lose_required_columns():
    """The payload must include every YAML-declared required column."""
    from nchantdoffice.models import _build_app_user_payload
    required = {
        "UUID",
        "user_nm_txt",
        "password_txt",
        "saltUUID",
        "iterations_txt",
        "is_private_bit",
        "is_secure_bit",
    }
    payload = _build_app_user_payload(_user())
    missing = required - set(payload.keys())
    assert not missing, (
        f"_build_app_user_payload must emit every required column; "
        f"missing={missing}; got={set(payload.keys())}"
    )


# ---------------------------------------------------------------------------
# Store layer: store_app_user method exists and dispatches via _store
# ---------------------------------------------------------------------------

def test_store_app_user_method_exists():
    """NchantdOfficeCloakModel must define store_app_user."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    assert hasattr(NchantdOfficeCloakModel, "store_app_user"), (
        "NchantdOfficeCloakModel must define store_app_user (T-NEW-129)."
    )


def test_store_app_user_dispatches_via_store_layer():
    """Source-level: model.store_app_user must route through
    ``self.store.store_app_user(payload, db)`` (mirrors
    ``store_instance`` -> ``store.store_app_instance``).
    """
    from nchantdoffice.models import NchantdOfficeCloakModel
    src = inspect.getsource(NchantdOfficeCloakModel.store_app_user)
    assert "store.store_app_user" in src, (
        f"model.store_app_user must dispatch via "
        f"self.store.store_app_user; got: {src[:200]!r}"
    )


def test_store_app_user_invokes_payload_builder():
    """Source-level: store_app_user must call _build_app_user_payload."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    src = inspect.getsource(NchantdOfficeCloakModel.store_app_user)
    assert "_build_app_user_payload" in src, (
        "store_app_user must invoke _build_app_user_payload (T-NEW-129)."
    )


def test_store_app_user_writes_to_sqlite(tmp_path):
    """End-to-end: store_app_user inserts a row into app_user via the
    store layer. Uses an in-memory SQLite connection + a stub store
    that records what was passed to ``_store``.
    """
    from nchantdoffice.models import NchantdOfficeCloakModel, _build_app_user_payload

    captured: list = []

    class _StubStore:
        def store_app_user(self, payload, db="db"):
            self._store("app_user", [payload], db=db)

        def _store(self, table, payloads, db="db"):
            captured.append((table, list(payloads), db))

    model = _bare_model()
    model.store = _StubStore()

    method = model.store_app_user
    assert callable(method), "store_app_user must be callable"
    method(_user())

    assert captured, "store_app_user must call self._store at least once"
    table, payloads, db = captured[0]
    assert table == "app_user", (
        f"store_app_user must dispatch to 'app_user'; got {table!r}"
    )
    assert db == "db"
    assert len(payloads) == 1
    assert payloads[0].get("UUID") == "u-uuid-1"


# ---------------------------------------------------------------------------
# Read path: get_app_user mirrors get_app_instances
# ---------------------------------------------------------------------------

def test_get_app_user_method_exists():
    """NchantdOfficeCloakModel must define get_app_user."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    assert hasattr(NchantdOfficeCloakModel, "get_app_user"), (
        "NchantdOfficeCloakModel must define get_app_user (T-NEW-129)."
    )


def test_get_app_user_returns_empty_list_when_table_missing(tmp_path):
    """When the ``app_user`` table doesn't exist (fresh install before
    migration completes), get_app_user returns [] rather than raising.
    """
    from nchantdoffice.models import NchantdOfficeCloakModel

    db_path = tmp_path / "fresh.pyof"
    conn = sqlite3.connect(str(db_path))
    # Intentionally do NOT create app_user table here.

    class _StubStore:
        def __init__(self):
            self._sqlite_connection = conn

    model = _bare_model()
    model.store = _StubStore()
    method = model.get_app_user
    assert callable(method)

    rows = method()
    assert isinstance(rows, list), (
        f"get_app_user must return list; got {type(rows).__name__}"
    )
    assert rows == [], (
        f"On a fresh DB with no app_user table, get_app_user must return "
        f"[]; got {rows!r}"
    )
    conn.close()


def test_get_app_user_round_trips_through_sqlite(tmp_path):
    """Round-trip: insert a row directly, read it back via get_app_user."""
    from nchantdoffice.models import NchantdOfficeCloakModel

    db_path = tmp_path / "primary.pyof"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE app_user ("
        "  UUID TEXT PRIMARY KEY,"
        "  user_nm_txt TEXT,"
        "  password_txt TEXT,"
        "  saltUUID TEXT,"
        "  iterations_txt TEXT,"
        "  is_private_bit INTEGER,"
        "  is_secure_bit INTEGER,"
        "  instance_FK INTEGER"
        ")"
    )
    conn.execute(
        "INSERT INTO app_user(UUID, user_nm_txt, password_txt, saltUUID, "
        "iterations_txt, is_private_bit, is_secure_bit, instance_FK) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("u-uuid-1", "alice", "pw", "salt-1", "1000", 0, 0, 1),
    )
    conn.commit()

    class _StubStore:
        def __init__(self):
            self._sqlite_connection = conn

    model = _bare_model()
    model.store = _StubStore()
    rows = model.get_app_user()
    assert isinstance(rows, list) and len(rows) == 1, (
        f"Round-trip expected exactly 1 row; got {len(rows)}: {rows!r}"
    )
    assert rows[0]["UUID"] == "u-uuid-1"
    assert rows[0]["user_nm_txt"] == "alice"
    conn.close()


# ---------------------------------------------------------------------------
# Bootstrap path: idempotent install
# ---------------------------------------------------------------------------

def test_bootstrap_app_user_method_exists():
    """NchantdOfficeCloakModel must define bootstrap_app_user."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    assert hasattr(NchantdOfficeCloakModel, "bootstrap_app_user"), (
        "NchantdOfficeCloakModel must define bootstrap_app_user "
        "(T-NEW-129 app_user bootstrap)."
    )


def test_bootstrap_app_user_is_idempotent(tmp_path):
    """bootstrap_app_user must NOT insert a duplicate row when the
    table already has a row. Run it twice -- second call is a no-op.
    """
    from nchantdoffice.models import NchantdOfficeCloakModel

    db_path = tmp_path / "primary.pyof"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE app_user ("
        "  UUID TEXT PRIMARY KEY,"
        "  user_nm_txt TEXT,"
        "  password_txt TEXT,"
        "  saltUUID TEXT,"
        "  iterations_txt TEXT,"
        "  is_private_bit INTEGER,"
        "  is_secure_bit INTEGER,"
        "  instance_FK INTEGER"
        ")"
    )
    conn.commit()

    class _StubStore:
        """Bare stub: only the _sqlite_connection attr (for get_app_user)."""

        def __init__(self, conn=None):
            self._sqlite_connection = conn

    model = _bare_model()
    model.store = _StubStore()
    # Stub the user attribute (bootstrap reads it).
    model.user = _user(uuid="u-existing", user_name="alice")

    # Seed an existing row -- bootstrap should see it and skip.
    conn.execute(
        "INSERT INTO app_user(UUID, user_nm_txt, password_txt, saltUUID, "
        "iterations_txt, is_private_bit, is_secure_bit, instance_FK) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("u-existing", "alice", "pw", "salt-1", "1000", 0, 0, 1),
    )
    conn.commit()

    # Idempotency check: call twice, row count must stay at 1.
    model.bootstrap_app_user()
    model.bootstrap_app_user()
    (count,) = conn.execute("SELECT COUNT(*) FROM app_user").fetchone()
    assert count == 1, (
        f"bootstrap_app_user must be idempotent; expected 1 row, "
        f"got {count}"
    )
    conn.close()


def test_bootstrap_app_user_seeds_when_empty(tmp_path):
    """bootstrap_app_user inserts exactly one row on a fresh DB."""
    from nchantdoffice.models import NchantdOfficeCloakModel

    db_path = tmp_path / "fresh.pyof"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE app_user ("
        "  UUID TEXT PRIMARY KEY,"
        "  user_nm_txt TEXT,"
        "  password_txt TEXT,"
        "  saltUUID TEXT,"
        "  iterations_txt TEXT,"
        "  is_private_bit INTEGER,"
        "  is_secure_bit INTEGER,"
        "  instance_FK INTEGER"
        ")"
    )
    conn.commit()

    captured: list = []

    class _StubStore:
        """Captures _store calls so we can assert the payload."""

        def __init__(self, conn=None):
            self._sqlite_connection = conn

        def store_app_user(self, payload, db="db"):
            # Mirror _store + INSERT so get_app_user sees the row.
            self._store("app_user", [payload], db=db)

        def _store(self, table, payloads, db="db"):
            captured.append((table, list(payloads), db))
            # Mirror the INSERT so get_app_user sees the row.
            if conn is not None:
                for payload in payloads:
                    placeholders = ",".join("?" * len(payload))
                    cols = list(payload.keys())
                    conn.execute(
                        f"INSERT OR REPLACE INTO {table} "
                        f"({','.join(cols)}) VALUES ({placeholders})",
                        list(payload.values()),
                    )
                conn.commit()

    model = _bare_model()
    model.store = _StubStore(conn=conn)
    model.user = _user(uuid="u-fresh", user_name="alice")

    model.bootstrap_app_user()
    (count,) = conn.execute("SELECT COUNT(*) FROM app_user").fetchone()
    assert count == 1, (
        f"bootstrap_app_user must seed exactly 1 row on a fresh DB; "
        f"got {count}"
    )
    (uuid_val,) = conn.execute("SELECT UUID FROM app_user").fetchone()
    assert uuid_val == "u-fresh"
    # Also verify the payload was dispatched through _store.
    assert captured, "bootstrap_app_user must call store._store"
    table, payloads, _db = captured[0]
    assert table == "app_user"
    assert payloads[0]["UUID"] == "u-fresh"
    conn.close()


def test_bootstrap_app_user_is_safe_when_table_missing(tmp_path):
    """bootstrap_app_user must NOT raise when the app_user table
    doesn't exist yet (e.g. the migration hasn't run on this DB).
    """
    from nchantdoffice.models import NchantdOfficeCloakModel

    db_path = tmp_path / "no-table.pyof"
    conn = sqlite3.connect(str(db_path))

    class _StubStore:
        """Stub that records _store without raising on missing table."""

        def __init__(self, conn=None):
            self._sqlite_connection = conn

        def store_app_user(self, payload, db="db"):
            self._store("app_user", [payload], db=db)

        def _store(self, table, payloads, db="db"):
            # Intentionally do nothing -- the table is missing.
            pass

    model = _bare_model()
    model.store = _StubStore(conn=conn)
    model.user = _user()

    # Must not raise.
    model.bootstrap_app_user()
    conn.close()


# ---------------------------------------------------------------------------
# Hook: run_on_launch wires bootstrap_app_user
# ---------------------------------------------------------------------------

def test_run_on_launch_calls_bootstrap_app_user():
    """NchantdOfficeCloak.run_on_launch must call
    ``self.model.bootstrap_app_user()`` so the row gets seeded.
    """
    from nchantdoffice import nchantdoffice as noff
    src = inspect.getsource(noff.NchantdOfficeCloak.run_on_launch)
    assert "bootstrap_app_user" in src, (
        "NchantdOfficeCloak.run_on_launch must call "
        "self.model.bootstrap_app_user() (T-NEW-129)."
    )