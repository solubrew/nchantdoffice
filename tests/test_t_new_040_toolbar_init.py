"""T-NEW-040 -- Toolbar init tech debt (TDD tests).

Two tech-debt notes in toolbars.py:

  1. L125: "this is redundant but for now we need the app
     attribute to be set before the super call". The
     ``init_variables()`` call IS necessary (the parent
     NchantdButtonBar.__init__ doesn't call it) -- the
     comment is stale.

  2. L167: "db = self.app.model.instance.db  # TODO: Switch
     to MultiInstance". The hardcoded ``db = "db"`` is the
     legacy single-instance default. The fix: a helper
     that uses ``self.app.model.instance.db`` when
     ``instance`` is plumbed through, falling back to
     ``"db"`` for single-instance (the current case).

Fix:

  1. Remove the stale "redundant" comment at L125.
  2. Add ``_resolve_db_alias(self)`` that prefers
     ``self.app.model.instance.db`` (when available) and
     falls back to ``"db"``.
  3. Update L168 (``db = "db"``) to call the helper.

Tests (the off-screen path can't drive real model
construction, so we test via __new__ + attribute injection
+ source-level checks):

  - test_resolve_db_alias_returns_db_default_when_model_has_no_instance
  - test_resolve_db_alias_uses_instance_db_when_available
  - test_resolve_db_alias_handles_missing_app
  - test_resolve_db_alias_handles_missing_model
  - test_launch_document_uses_resolve_db_alias
  - test_init_model_no_longer_carries_stale_redundant_comment
"""

import sys
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication
import nchantdoffice.widgets.controls.toolbars  # noqa: F401


def _make_toolbar_with_model(instance_db=None):
    """Build a NchantdNewDocumentToolBar via __new__ with
    a fake app + model. When ``instance_db`` is provided,
    the model exposes an ``instance`` attribute carrying it.
    """
    from nchantdoffice.widgets.controls.toolbars import (
        NchantdNewDocumentToolBar,
    )
    bar = NchantdNewDocumentToolBar.__new__(NchantdNewDocumentToolBar)
    if instance_db is not None:
        bar.app = SimpleNamespace(
            model=SimpleNamespace(instance=SimpleNamespace(db=instance_db))
        )
    else:
        bar.app = SimpleNamespace(
            model=SimpleNamespace()  # no .instance
        )
    return bar


def test_resolve_db_alias_returns_db_default_when_model_has_no_instance():
    """Single-instance mode (the current default): no
    ``self.app.model.instance`` attribute, fall back to ``"db"``.
    """
    bar = _make_toolbar_with_model(instance_db=None)
    assert bar._resolve_db_alias() == "db"


def test_resolve_db_alias_uses_instance_db_when_available():
    """Multi-instance mode (future): use
    ``self.app.model.instance.db`` when present.
    """
    bar = _make_toolbar_with_model(instance_db="db_instance_42")
    assert bar._resolve_db_alias() == "db_instance_42"


def test_resolve_db_alias_handles_missing_app():
    """Defensive: missing ``self.app`` -> return ``"db"``.
    """
    from nchantdoffice.widgets.controls.toolbars import (
        NchantdNewDocumentToolBar,
    )
    bar = NchantdNewDocumentToolBar.__new__(NchantdNewDocumentToolBar)
    bar.app = None
    assert bar._resolve_db_alias() == "db"


def test_resolve_db_alias_handles_missing_model():
    """Defensive: missing ``self.app.model`` -> return ``"db"``."""
    from nchantdoffice.widgets.controls.toolbars import (
        NchantdNewDocumentToolBar,
    )
    bar = NchantdNewDocumentToolBar.__new__(NchantdNewDocumentToolBar)
    bar.app = SimpleNamespace(model=None)
    assert bar._resolve_db_alias() == "db"


def test_resolve_db_alias_handles_instance_without_db():
    """Defensive: ``self.app.model.instance`` exists but has no
    ``db`` attribute -> return ``"db"``.
    """
    from nchantdoffice.widgets.controls.toolbars import (
        NchantdNewDocumentToolBar,
    )
    bar = NchantdNewDocumentToolBar.__new__(NchantdNewDocumentToolBar)
    bar.app = SimpleNamespace(model=SimpleNamespace(instance=SimpleNamespace()))
    assert bar._resolve_db_alias() == "db"


def test_launch_document_uses_resolve_db_alias():
    """The ``launch_document`` method (the function that
    uses ``db``) must call ``self._resolve_db_alias()``
    instead of hardcoding ``db = "db"``. Source-level
    guard.
    """
    from pathlib import Path
    toolbars_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/controls/toolbars.py"
    ).read_text()
    assert "self._resolve_db_alias()" in toolbars_py, (
        "launch_document must call self._resolve_db_alias() "
        "to resolve the DB alias (T-NEW-040 MultiInstance "
        "support)"
    )


def test_init_model_no_longer_carries_stale_redundant_comment():
    """The "this is redundant but for now we need the app
    attribute to be set before the super call" comment at
    L125 must be REMOVED -- ``init_variables()`` is NOT
    redundant (the parent class doesn't call it).
    """
    from pathlib import Path
    toolbars_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/controls/toolbars.py"
    ).read_text()
    stale = "this is redundant but for now we need the app attribute to be set before the super call"
    assert stale not in toolbars_py, (
        f"Stale comment at toolbars.py:125 must be removed -- "
        f"init_variables() IS needed (the parent doesn't call it). "
        f"Found: {stale!r}"
    )