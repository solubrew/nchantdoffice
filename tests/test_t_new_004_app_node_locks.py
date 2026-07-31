"""T-NEW-004 -- Locks on App Nodes (TDD tests).

Three app nodes (Home / Journal / Settings) are seeded by
``nchantdoffice/_data_/models.yaml`` as the canonical
application-level top-level entries. They are NOT
user-created -- the user must not be able to delete /
rename them, or the app breaks.

The current state: ``cmd_delete_node`` and
``model.delete_node`` have no lock check. The user can
delete any node, including Home / Journal / Settings.

Fix:

  1. Add a class-level constant
     ``NchantdOfficeCloakModel.LOCKED_NODE_NAMES`` with the
     canonical locked names (case-insensitive matching).
  2. Add ``is_locked_node(node) -> bool`` helper.
  3. ``cmd_delete_node`` (widgets/panes/documents.py:126)
     returns self when the node is locked and logs a
     warning.
  4. ``model.delete_node`` (models.py:1235) refuses to
     delete locked nodes (defensive server-side check).

Tests:

  - test_locked_node_names_constant_is_present
  - test_is_locked_node_matches_home
  - test_is_locked_node_matches_journal
  - test_is_locked_node_matches_settings
  - test_is_locked_node_case_insensitive
  - test_is_locked_node_returns_false_for_non_locked
  - test_is_locked_node_handles_none
  - test_is_locked_node_handles_missing_name_attribute
  - test_cmd_delete_node_skips_locked_node
  - test_model_delete_node_skips_locked_node
  - test_locked_node_names_includes_the_three_app_nodes
"""

import sys
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication
_QAPP = QApplication.instance() or QApplication(sys.argv)


# ---------------------------------------------------------------------------
# Source-level checks: the LOCKED_NODE_NAMES constant must exist
# ---------------------------------------------------------------------------


def test_locked_node_names_constant_is_present():
    """``NchantdOfficeCloakModel`` must define
    ``LOCKED_NODE_NAMES`` (a frozenset of lowercase names).
    """
    from pathlib import Path
    models_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "models.py"
    ).read_text()
    assert "LOCKED_NODE_NAMES" in models_py, (
        "NchantdOfficeCloakModel.LOCKED_NODE_NAMES must exist "
        "(T-NEW-004: locks on Home / Journal / Settings app nodes)"
    )


def test_locked_node_names_includes_the_three_app_nodes():
    """The constant must include 'home', 'journal', 'settings'
    (case-insensitive canonical names).
    """
    from nchantdoffice.models import NchantdOfficeCloakModel
    names = getattr(NchantdOfficeCloakModel, "LOCKED_NODE_NAMES", None)
    assert names is not None, "LOCKED_NODE_NAMES constant missing"
    # Normalize to lowercase for the check
    lower = {n.lower() for n in names}
    for required in ("home", "journal", "settings"):
        assert required in lower, (
            f"LOCKED_NODE_NAMES must include {required!r}. "
            f"Got: {lower}"
        )


# ---------------------------------------------------------------------------
# is_locked_node helper
# ---------------------------------------------------------------------------


def _make_model():
    from nchantdoffice.models import NchantdOfficeCloakModel
    model = NchantdOfficeCloakModel.__new__(NchantdOfficeCloakModel)
    return model


def test_is_locked_node_matches_home():
    """A node whose name is 'home' (or 'Home', 'HOME', etc.)
    is locked.
    """
    model = _make_model()
    node = SimpleNamespace(name="Home")
    assert model.is_locked_node(node) is True


def test_is_locked_node_matches_journal():
    """A node whose name is 'Journal' is locked."""
    model = _make_model()
    node = SimpleNamespace(name="Journal")
    assert model.is_locked_node(node) is True


def test_is_locked_node_matches_settings():
    """A node whose name is 'Settings' is locked."""
    model = _make_model()
    node = SimpleNamespace(name="Settings")
    assert model.is_locked_node(node) is True


def test_is_locked_node_case_insensitive():
    """Mixed-case names also match (case-insensitive comparison).
    """
    model = _make_model()
    for variant in ("home", "Home", "HOME", "HoMe"):
        node = SimpleNamespace(name=variant)
        assert model.is_locked_node(node) is True, (
            f"is_locked_node must match case-insensitively. "
            f"Failed for: {variant!r}"
        )


def test_is_locked_node_returns_false_for_non_locked():
    """A node named 'My Project' or 'Untitled' is NOT locked."""
    model = _make_model()
    for variant in ("My Project", "Untitled", "Random", "user-node-1"):
        node = SimpleNamespace(name=variant)
        assert model.is_locked_node(node) is False, (
            f"{variant!r} must NOT be locked. "
            f"Got True from is_locked_node."
        )


def test_is_locked_node_handles_none():
    """Defensive: when node is None, returns False."""
    model = _make_model()
    assert model.is_locked_node(None) is False


def test_is_locked_node_handles_missing_name_attribute():
    """Defensive: when node has no name attribute, returns False.
    """
    model = _make_model()
    node = SimpleNamespace()  # no name
    assert model.is_locked_node(node) is False


def test_is_locked_node_handles_non_string_name():
    """Defensive: when name is not a string, returns False."""
    model = _make_model()
    node = SimpleNamespace(name=None)
    assert model.is_locked_node(node) is False
    node = SimpleNamespace(name=42)
    assert model.is_locked_node(node) is False


# ---------------------------------------------------------------------------
# Source-level checks: cmd_delete_node + model.delete_node skip locked
# ---------------------------------------------------------------------------


def test_cmd_delete_node_skips_locked_node():
    """Source-level: ``cmd_delete_node`` (in
    ``widgets/panes/documents.py``) must call
    ``is_locked_node`` (or equivalent) and skip deletion
    when the node is locked.
    """
    from pathlib import Path
    docs_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/panes/documents.py"
    ).read_text()
    # The check may live in cmd_delete_node or in a helper
    # that cmd_delete_node calls -- we accept either.
    has_check = (
        "is_locked_node" in docs_py
        or "locked_node" in docs_py
        or "LOCKED_NODE_NAMES" in docs_py
    )
    assert has_check, (
        "cmd_delete_node must consult is_locked_node before "
        "calling model.delete_node (T-NEW-004)"
    )


def test_model_delete_node_skips_locked_node():
    """Source-level: ``model.delete_node`` must also check
    is_locked_node (defensive server-side check).
    """
    from pathlib import Path
    models_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "models.py"
    ).read_text()
    # Find the delete_node method body
    import re
    m = re.search(
        r"def delete_node\(self, node\):(.*?)(?=\n    def |\nclass |\Z)",
        models_py,
        re.S,
    )
    assert m, "delete_node method not found"
    body = m.group(1)
    has_check = (
        "is_locked_node" in body
        or "LOCKED_NODE_NAMES" in body
    )
    assert has_check, (
        "model.delete_node must call is_locked_node before "
        "calling super().delete_node (T-NEW-004)"
    )
