"""T-NEW-132 regression test: explicit deny logic for tab create / delete
in the Settings node tree, for ALL users.

**Settings tree is tab-terminal: no create / delete there**

The user wants the Settings tree to be tab-terminal: no user
(free or pro) can create a new tab under Settings, and no user
can delete an existing tab whose parent is Settings. Home
and Journal are node-terminal (T-NEW-131) but remain
tab-mutable; the new rule applies only to the Settings tree.

The fix:
1. ``is_locked_tab_parent(pid)`` returns True when ``pid``
   resolves to a node named ``Settings`` (case-insensitive).
   Returns False for root pids, missing pids, and Home /
   Journal / user-nodes. Defensive against missing store /
   table / row / exceptions.
2. ``add_tab(name, pid, ...)`` consults
   ``is_locked_tab_parent(pid)`` after the existing T-NEW-054
   max-tabs-per-node resolution. When True, refuse with a
   warning and return ``None``. Pro users do NOT bypass --
   Settings tabs are structural.
3. ``delete_tab(tab)`` resolves the tab's parent pid (via
   ``doc_tab.pid_txt`` for the tab's ``tid``), then consults
   the same gate. Refuse with a warning; do not call
   ``super().delete_tab(...)``. Pro users do NOT bypass.

Affected sites:
- nchantdoffice/models.py: ``is_locked_tab_parent`` helper,
  ``add_tab`` + ``delete_tab`` gates.
- tests/test_settings_tab_deny.py: this test file.

Migration plan (no priority / low priority -- design decision
first): mirrors T-NEW-131's locked-node create-deny rule,
narrowed to Settings-only and applied to the tab layer. The
existing T-NEW-054 max-tabs-per-node auto-child logic is
unaffected: when a Settings tab create is refused, we return
``None`` *before* the max-tabs fallback runs. Home / Journal
remain tab-mutable; the rule is Settings-specific. Pro users
are explicitly NOT bypassed.

Steps:
1. Add ``is_locked_tab_parent(pid)`` next to
   ``is_locked_parent`` on NchantdOfficeCloakModel.
   Specialised to ``Settings`` only (case-insensitive).
2. Gate ``add_tab`` on ``is_locked_tab_parent(pid)`` BEFORE
   the T-NEW-054 ``_resolve_pid_for_max_tabs`` call, so the
   deny is the first thing checked.
3. Gate ``delete_tab`` on the same helper, after resolving
   the tab's parent pid via ``store._sqlite_connection``.
4. Refuse with ``logma.warning(...)`` + return ``None``.
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


def _sqlite_with_settings_tree():
    """Create a fresh in-memory SQLite DB seeded with Home, Journal,
    Settings rows + a doc_tab whose pid points at Settings.

    Schema matches production: ``doc_tree_node.nid_txt`` is the
    primary-key column; ``doc_tab.pid_txt`` references it.
    """
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
CREATE TABLE doc_tree_node (
    nid_txt TEXT PRIMARY KEY, icon_txt TEXT, name_txt TEXT, type_txt TEXT,
    pid_txt TEXT, position_int TEXT, parameters_dict TEXT
);
CREATE TABLE doc_tab (
    tid_txt TEXT PRIMARY KEY,
    name_txt TEXT,
    widget_txt TEXT,
    widgdata_dict TEXT,
    pid_txt TEXT,
    did_txt TEXT,
    position_int INTEGER,
    tab_type_txt TEXT,
    tabset_type_txt TEXT,
    readonly_bit INTEGER,
    editable_bit INTEGER,
    visible_bit INTEGER,
    moveable_bit INTEGER
);
INSERT INTO doc_tree_node VALUES
    ('home-uuid',     '', 'Home',     'appnode',     '0', '0', '{}'),
    ('journal-uuid',  '', 'Journal',  'displaynode', '1', '1', '{}'),
    ('settings-uuid', '', 'Settings', 'displaynode', '1', '2', '{}'),
    ('user-uuid',     '', 'MyNode',   'usernode',    '0', '3', '{}');
INSERT INTO doc_tab VALUES
    ('tab-settings-1', 'SettingsTab1', 'widget', '{}', 'settings-uuid',
     'did-1', 0, 'tab', 'center', 0, 1, 1, 1),
    ('tab-user-1',     'UserTab1',     'widget', '{}', 'user-uuid',
     'did-2', 0, 'tab', 'center', 0, 1, 1, 1),
    ('tab-journal-1',  'JournalTab1',  'widget', '{}', 'journal-uuid',
     'did-3', 0, 'tab', 'center', 0, 1, 1, 1),
    ('tab-home-1',     'HomeTab1',     'widget', '{}', 'home-uuid',
     'did-4', 0, 'tab', 'center', 0, 1, 1, 1);
""")
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Helper existence
# ---------------------------------------------------------------------------

def test_is_locked_tab_parent_helper_exists():
    """NchantdOfficeCloakModel must define ``is_locked_tab_parent``."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    assert hasattr(
        NchantdOfficeCloakModel, "is_locked_tab_parent"
    ), (
        "NchantdOfficeCloakModel must define is_locked_tab_parent "
        "(T-NEW-132)."
    )


# ---------------------------------------------------------------------------
# Behavioural: helper accepts a real DB connection and resolves pids
# ---------------------------------------------------------------------------

def test_is_locked_tab_parent_true_for_settings():
    """is_locked_tab_parent('settings-uuid') -> True."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)
    assert m.is_locked_tab_parent("settings-uuid") is True, (
        "is_locked_tab_parent must return True for Settings"
    )


def test_is_locked_tab_parent_false_for_journal():
    """is_locked_tab_parent('journal-uuid') -> False (only Settings locked)."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)
    assert m.is_locked_tab_parent("journal-uuid") is False, (
        "is_locked_tab_parent must return False for Journal "
        "(only Settings is tab-locked, T-NEW-132)"
    )


def test_is_locked_tab_parent_false_for_home():
    """is_locked_tab_parent('home-uuid') -> False (only Settings locked)."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)
    assert m.is_locked_tab_parent("home-uuid") is False, (
        "is_locked_tab_parent must return False for Home "
        "(only Settings is tab-locked, T-NEW-132)"
    )


def test_is_locked_tab_parent_false_for_user_node():
    """is_locked_tab_parent('user-uuid' -> MyNode) -> False."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)
    assert m.is_locked_tab_parent("user-uuid") is False, (
        "is_locked_tab_parent must return False for a regular usernode"
    )


def test_is_locked_tab_parent_false_for_unknown_pid():
    """is_locked_tab_parent('does-not-exist') -> False."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)
    assert m.is_locked_tab_parent("does-not-exist") is False, (
        "is_locked_tab_parent must return False when pid doesn't resolve"
    )


def test_is_locked_tab_parent_false_for_root_pid():
    """is_locked_tab_parent(0) -> False (top-level governed separately)."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = None

    m.store = _StubStore(None)
    m.user = SimpleNamespace(has_pro=True)
    for falsy in (None, "", "0", 0):
        assert m.is_locked_tab_parent(falsy) is False, (
            f"is_locked_tab_parent({falsy!r}) must be False (root pid)"
        )


def test_is_locked_tab_parent_case_insensitive():
    """is_locked_tab_parent on a node named 'SETTINGS' still returns True."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
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
    assert m.is_locked_tab_parent("upper-settings-uuid") is True, (
        "is_locked_tab_parent must be case-insensitive"
    )


# ---------------------------------------------------------------------------
# Behavioural: add_tab refuses when parent is Settings
# ---------------------------------------------------------------------------

def test_add_tab_refuses_under_settings_for_pro_user():
    """Even a pro user can't add a tab under Settings."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn
        def store_doc_tab(self, *a, **k):
            return "new-tid"

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)

    result = m.add_tab(
        name="NewTab",
        pid="settings-uuid",
        pos=1,
        widget="widget",
        widgdata={},
        did="did-x",
        doc_type="tab",
        tabset="center",
    )
    assert result is None, (
        f"add_tab under Settings must return None for pro users "
        f"(T-NEW-132); got {result!r}"
    )


def test_add_tab_refuses_under_settings_for_non_pro_user():
    """Non-pro user also can't add a tab under Settings."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn
        def store_doc_tab(self, *a, **k):
            return "new-tid"

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=False)

    result = m.add_tab(
        name="NewTab",
        pid="settings-uuid",
        pos=1,
        widget="widget",
        widgdata={},
        did="did-x",
        doc_type="tab",
        tabset="center",
    )
    assert result is None, (
        f"add_tab under Settings must return None for non-pro users; "
        f"got {result!r}"
    )


def test_add_tab_allows_under_journal():
    """Regression guard: tabs under Journal still work."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    captured: list = []

    # Monkeypatch super().add_tab on the parent class so we don't
    # need to wire the full nchantrs pane chain. The capture list
    # records that super().add_tab was reached (not short-circuited
    # by the T-NEW-132 deny guard).
    def _fake_super_add_tab(self, *args, **kwargs):
        captured.append(("super.add_tab", args, kwargs))
        return "fake-tid"

    # Find the direct parent class in the MRO -- skip
    # NchantdOfficeCloakModel itself and pick NchantdCloakModel.
    parent_cls = next(
        c for c in NchantdOfficeCloakModel.__mro__[1:]
        if c.__name__ == "NchantdCloakModel"
    )
    orig_add_tab = parent_cls.add_tab
    parent_cls.add_tab = _fake_super_add_tab
    try:
        result = m.add_tab(
            name="NewTab",
            pid="journal-uuid",
            pos=1,
            widget="widget",
            widgdata={},
            did="did-x",
            doc_type="tab",
            tabset="center",
        )
    finally:
        parent_cls.add_tab = orig_add_tab

    assert captured, (
        "super().add_tab must be called for non-Settings pids "
        "(T-NEW-132 regression guard)"
    )
    assert result == "fake-tid", (
        f"add_tab under Journal must propagate the super result; "
        f"got {result!r}"
    )


def test_add_tab_allows_under_user_node():
    """Regression guard: tabs under a regular usernode still work."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    captured: list = []

    def _fake_super_add_tab(self, *args, **kwargs):
        captured.append(("super.add_tab", args, kwargs))
        return "fake-tid"

    parent_cls = next(
        c for c in NchantdOfficeCloakModel.__mro__[1:]
        if c.__name__ == "NchantdCloakModel"
    )
    orig_add_tab = parent_cls.add_tab
    parent_cls.add_tab = _fake_super_add_tab
    try:
        result = m.add_tab(
            name="NewTab",
            pid="user-uuid",
            pos=1,
            widget="widget",
            widgdata={},
            did="did-x",
            doc_type="tab",
            tabset="center",
        )
    finally:
        parent_cls.add_tab = orig_add_tab

    assert captured, (
        "super().add_tab must be called for non-Settings pids "
        "(T-NEW-132 regression guard)"
    )
    assert result == "fake-tid"


# ---------------------------------------------------------------------------
# Behavioural: delete_tab refuses when parent is Settings
# ---------------------------------------------------------------------------

def test_delete_tab_refuses_for_settings_child():
    """delete_tab refuses when the tab's parent is Settings."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    class _StubStore:
        def __init__(self, conn):
            self._sqlite_connection = conn
        def delete_record(self, *a, **k):
            raise AssertionError(
                "super().delete_tab must NOT be called when "
                "parent is Settings (T-NEW-132)"
            )
        def delete_document(self, *a, **k):
            raise AssertionError(
                "delete_document must NOT be called when "
                "parent is Settings (T-NEW-132)"
            )

    m.store = _StubStore(conn)
    m.user = SimpleNamespace(has_pro=True)

    # Stub tab object with .tid (the row we want to delete)
    tab = SimpleNamespace(
        tid="tab-settings-1",
        document=SimpleNamespace(did="did-1"),
    )

    # Must not raise and must not call delete_record/delete_document.
    result = m.delete_tab(tab)
    assert result is m, (
        "delete_tab must return self after refusing the delete "
        "(T-NEW-132)"
    )


def test_delete_tab_allows_for_user_child():
    """Regression guard: delete_tab works for a tab under a user node."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    captured: list = []

    # Stub super().delete_tab so we don't need a full store
    # pipeline. Capture confirms the deny guard did NOT
    # short-circuit.
    def _fake_super_delete_tab(self, *args, **kwargs):
        captured.append(("super.delete_tab", args, kwargs))
        return self

    parent_cls = next(
        c for c in NchantdOfficeCloakModel.__mro__[1:]
        if c.__name__ == "NchantdCloakModel"
    )
    orig_delete_tab = parent_cls.delete_tab
    parent_cls.delete_tab = _fake_super_delete_tab
    try:
        # Stub the document delete so we don't need a real doc chain.
        m.delete_document = lambda did, db="db": None

        tab = SimpleNamespace(
            tid="tab-user-1",
            document=SimpleNamespace(did="did-2"),
        )
        result = m.delete_tab(tab)
    finally:
        parent_cls.delete_tab = orig_delete_tab

    assert captured, (
        "super().delete_tab must be called for non-Settings tab "
        "parents (T-NEW-132 regression guard)"
    )
    assert result is m


def test_delete_tab_allows_for_journal_child():
    """Regression guard: delete_tab works for a tab under Journal."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    conn = _sqlite_with_settings_tree()
    m = _bare_model()
    m.config = SimpleNamespace(dikt={})

    captured: list = []

    def _fake_super_delete_tab(self, *args, **kwargs):
        captured.append(("super.delete_tab", args, kwargs))
        return self

    parent_cls = next(
        c for c in NchantdOfficeCloakModel.__mro__[1:]
        if c.__name__ == "NchantdCloakModel"
    )
    orig_delete_tab = parent_cls.delete_tab
    parent_cls.delete_tab = _fake_super_delete_tab
    try:
        m.delete_document = lambda did, db="db": None

        tab = SimpleNamespace(
            tid="tab-journal-1",
            document=SimpleNamespace(did="did-3"),
        )
        result = m.delete_tab(tab)
    finally:
        parent_cls.delete_tab = orig_delete_tab

    assert captured, (
        "super().delete_tab must be called for non-Settings tab "
        "parents (T-NEW-132 regression guard)"
    )
    assert result is m


# ---------------------------------------------------------------------------
# Source-level: source code must contain the new gates
# ---------------------------------------------------------------------------

def test_add_tab_source_consults_is_locked_tab_parent():
    """Source-level: ``add_tab`` must consult
    ``is_locked_tab_parent`` BEFORE delegating.
    """
    from nchantdoffice.models import NchantdOfficeCloakModel
    src = inspect.getsource(NchantdOfficeCloakModel.add_tab)
    assert "is_locked_tab_parent" in src, (
        "add_tab must call is_locked_tab_parent (T-NEW-132)."
    )


def test_delete_tab_source_consults_is_locked_tab_parent():
    """Source-level: ``delete_tab`` must consult
    ``is_locked_tab_parent``.
    """
    from nchantdoffice.models import NchantdOfficeCloakModel
    src = inspect.getsource(NchantdOfficeCloakModel.delete_tab)
    assert "is_locked_tab_parent" in src, (
        "delete_tab must call is_locked_tab_parent (T-NEW-132)."
    )