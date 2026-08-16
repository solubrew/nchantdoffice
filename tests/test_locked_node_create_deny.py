"""T-NEW-131 regression test: explicit deny logic for child-node creates
under Settings / Journal / Home app-node trees, for ALL users.

**Deny rule: no children under app-locked node trees**

The user wants the Settings, Journal, and Home trees to be
*terminal*: no user (free or pro) can create a child node
under any of them. Today the model allows it; only deletion
is guarded (T-NEW-004 ``is_locked_node`` check in
``delete_node``). The new rule is the symmetric
``create-side`` guard: when the *parent* pid resolves to a
node whose name matches ``LOCKED_NODE_NAMES`` (case-insensitive),
``add_node`` and ``add_node_app`` refuse the create and return
``None``. Pro users do NOT bypass -- this is a structural
constraint, not a quota.

Affected sites:
- nchantdoffice/models.py: ``add_node`` + ``add_node_app``
  gate on parent-node lock state (new ``is_locked_parent``
  helper).
- nchantdoffice/models.py: ``is_locked_node`` already exists
  (T-NEW-004); the new helper resolves pid -> row -> node
  for the gating check.
- tests/test_locked_node_create_deny.py: this test file.

Migration plan (no priority / low priority -- design decision
first): mirrors the existing T-NEW-004 ``is_locked_node``
delete guard. The deny is symmetric: if you can't delete
Home/Journal/Settings, you also can't add children under
them. Pro users are explicitly NOT bypassed -- this is a
structural rule, not a quota. Idempotency, sibling-create
guards, and the existing 100-node ``max_nodes_per_user``
limit are unaffected.

Steps:
1. Add ``is_locked_pid(pid)`` helper that resolves a pid to
   the ``doc_tree_node`` row by nid_txt and returns True
   iff the row's name_txt matches ``LOCKED_NODE_NAMES``.
2. Add ``is_locked_parent(pid)`` convenience that returns
   True for ``pid in (None, '', '0')`` (root pid is *not*
   locked -- top-level creates are governed separately by
   T-NEW-130 / the follow-up top-level-deny ticket) or when
   ``is_locked_pid(pid)`` is True.
3. ``add_node`` and ``add_node_app`` consult
   ``is_locked_parent(pid)`` after the existing 100-node
   gate. Refuse with a warning when the parent is locked.
   Return ``None``.
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


def _sqlite_with_locked_parents():
    """Create a fresh in-memory SQLite DB seeded with Home, Journal,
    Settings rows + a free user node to attempt children under.

    Schema matches ``treemodels.yaml``: ``nid_txt`` is the
    primary-key column (production contract).
    """
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
CREATE TABLE doc_tree_node (
    nid_txt TEXT PRIMARY KEY, icon_txt TEXT, name_txt TEXT, type_txt TEXT,
    pid_txt TEXT, position_int TEXT, parameters_dict TEXT
);
INSERT INTO doc_tree_node VALUES
    ('home-uuid',     '', 'Home',     'appnode',     '0', '0', '{}'),
    ('journal-uuid',  '', 'Journal',  'displaynode', '1', '1', '{}'),
    ('settings-uuid', '', 'Settings', 'displaynode', '1', '2', '{}'),
    ('user-uuid',     '', 'MyNode',   'usernode',    '0', '3', '{}');
""")
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Helpers exist
# ---------------------------------------------------------------------------

def test_is_locked_parent_helper_exists():
    """NchantdOfficeCloakModel must define ``is_locked_parent``."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    assert hasattr(
        NchantdOfficeCloakModel, "is_locked_parent"
    ), (
        "NchantdOfficeCloakModel must define is_locked_parent "
        "(T-NEW-131)."
    )


def test_is_locked_pid_helper_exists():
    """NchantdOfficeCloakModel must define ``is_locked_pid``."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    assert hasattr(
        NchantdOfficeCloakModel, "is_locked_pid"
    ), (
        "NchantdOfficeCloakModel must define is_locked_pid "
        "(T-NEW-131)."
    )


# ---------------------------------------------------------------------------
# Behavioural: helper accepts a real DB connection and resolves pids
# ---------------------------------------------------------------------------

def test_is_locked_pid_true_for_settings():
    """is_locked_pid(settings-uuid) -> True."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_locked_parents()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)
    assert m.is_locked_pid("settings-uuid") is True, (
        "is_locked_pid must return True for Settings"
    )


def test_is_locked_pid_true_for_journal():
    """is_locked_pid(journal-uuid) -> True."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_locked_parents()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)
    assert m.is_locked_pid("journal-uuid") is True, (
        "is_locked_pid must return True for Journal"
    )


def test_is_locked_pid_true_for_home():
    """is_locked_pid(home-uuid) -> True."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_locked_parents()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)
    assert m.is_locked_pid("home-uuid") is True, (
        "is_locked_pid must return True for Home"
    )


def test_is_locked_pid_false_for_user_node():
    """is_locked_pid('user-uuid' -> MyNode) -> False."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_locked_parents()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)
    assert m.is_locked_pid("user-uuid") is False, (
        "is_locked_pid must return False for a regular usernode parent"
    )


def test_is_locked_pid_unknown_pid_returns_false():
    """is_locked_pid('does-not-exist') -> False (defensive)."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_locked_parents()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)
    assert m.is_locked_pid("does-not-exist") is False, (
        "is_locked_pid must return False when pid doesn't resolve"
    )


def test_is_locked_pid_case_insensitive():
    """is_locked_pid on a node named 'SETTINGS' still returns True."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_locked_parents()
    # Re-insert with a different case to confirm case-insensitive match.
    conn.execute(
        "INSERT INTO doc_tree_node VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("upper-settings-uuid", "", "SETTINGS", "displaynode", "1", "99", "{}"),
    )
    conn.commit()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)
    assert m.is_locked_pid("upper-settings-uuid") is True, (
        "is_locked_pid must be case-insensitive (matches LOCKED_NODE_NAMES)"
    )


# ---------------------------------------------------------------------------
# is_locked_parent: None / '' / '0' / missing pid -> False
# ---------------------------------------------------------------------------

def test_is_locked_parent_root_pid_is_false():
    """is_locked_parent(0) -> False (root pid, governed separately)."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = None

    m.store = _StubStore(None)
    m.user = SimpleNamespace(has_pro=True)
    for falsy in (None, "", "0", 0):
        assert m.is_locked_parent(falsy) is False, (
            f"is_locked_parent({falsy!r}) must be False (root pid); "
            f"got True"
        )


# ---------------------------------------------------------------------------
# Behavioural: add_node refuses when parent is locked
# ---------------------------------------------------------------------------

def test_add_node_refuses_under_settings_for_pro_user():
    """Even a pro user can't add a child under Settings."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_locked_parents()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    m.get_nodes = lambda: DataFrame()  # 0 nodes; pro-lock passes

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn
        def store_doc_tree_node(self, *a, **k):
            return ("new-uuid", ["new-uuid","","x","usernode","settings-uuid","0","{}"]+[""]*15)

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)  # PRO user

    result = m.add_node("child-x", "usernode", "settings-uuid", 0)
    assert result is None, (
        f"add_node under Settings must return None even for pro users "
        f"(T-NEW-131); got {result!r}"
    )


def test_add_node_refuses_under_journal_for_pro_user():
    """Even a pro user can't add a child under Journal."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_locked_parents()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    m.get_nodes = lambda: DataFrame()

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn
        def store_doc_tree_node(self, *a, **k):
            return ("new-uuid", ["new-uuid","","x","usernode","journal-uuid","0","{}"]+[""]*15)

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)

    result = m.add_node("child-x", "usernode", "journal-uuid", 0)
    assert result is None, (
        f"add_node under Journal must return None even for pro users "
        f"(T-NEW-131); got {result!r}"
    )


def test_add_node_refuses_under_settings_for_non_pro_user():
    """Non-pro user also can't add under Settings."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_locked_parents()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    m.get_nodes = lambda: DataFrame()

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn
        def store_doc_tree_node(self, *a, **k):
            return ("new-uuid", ["new-uuid","","x","usernode","settings-uuid","0","{}"]+[""]*15)

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=False)

    result = m.add_node("child-x", "usernode", "settings-uuid", 0)
    assert result is None, (
        f"add_node under Settings must return None for non-pro users; "
        f"got {result!r}"
    )


def test_add_node_app_refuses_under_settings():
    """add_node_app shares the same deny guard as add_node."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_locked_parents()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    m.get_nodes = lambda: DataFrame()

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn
        def store_doc_tree_node(self, *a, **k):
            return ("new-uuid", ["new-uuid","","x","appnode","settings-uuid","0","{}"]+[""]*15)

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)

    result = m.add_node_app("child-x", "appnode", "settings-uuid", 0)
    assert result is None, (
        f"add_node_app under Settings must return None (T-NEW-131); "
        f"got {result!r}"
    )


def test_add_node_allows_under_user_node():
    """Regression guard: child under a regular usernode still works."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_locked_parents()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    m.get_nodes = lambda: DataFrame()

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn
        def store_doc_tree_node(self, name, ntype, pid, pos, parameters=None, tree="left", db="db", how="INSERT"):
            return ("new-uuid", ["new-uuid","",name,ntype,pid,str(pos),parameters or "{}"]+[""]*15)

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)

    result = m.add_node("child-x", "usernode", "user-uuid", 0)
    assert result is not None and result == "new-uuid", (
        f"add_node under a regular usernode must succeed (T-NEW-131 "
        f"regression guard); got {result!r}"
    )


# ---------------------------------------------------------------------------
# Source-level: source code must contain the new gates
# ---------------------------------------------------------------------------

def test_add_node_source_consults_is_locked_parent():
    """Source-level: ``add_node`` must consult ``is_locked_parent``
    BEFORE delegating to ``super().add_node(...)``.
    """
    from nchantdoffice.models import NchantdOfficeCloakModel
    src = inspect.getsource(NchantdOfficeCloakModel.add_node)
    assert "is_locked_parent" in src, (
        "add_node must call is_locked_parent (T-NEW-131)."
    )


def test_add_node_app_source_consults_is_locked_parent():
    """Source-level: ``add_node_app`` must consult ``is_locked_parent``
    before delegating to ``super().add_node(...)``.
    """
    from nchantdoffice.models import NchantdOfficeCloakModel
    src = inspect.getsource(NchantdOfficeCloakModel.add_node_app)
    assert "is_locked_parent" in src, (
        "add_node_app must call is_locked_parent (T-NEW-131)."
    )