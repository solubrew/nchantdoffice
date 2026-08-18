"""Top-level pytest conftest for the nchantdoffice test suite.

T-NEW-122: this conftest solves the repository-wide module-level
``QApplication()`` collection abort. The pre-fix pattern in 21
test files was::

    from PySide6.QtWidgets import QApplication
    _QAPP = QApplication.instance() or QApplication(sys.argv)

That call sits at module top level, so it runs at pytest
collection time -- before any test executes. It passes when
the file is collected alone, but aborts the whole multi-file
pytest run (exit 134 / 139) when shiboken sees two distinct
top-level constructions colliding (lesson 14 of the
``qt-parent-harness`` skill).

The fix has two halves:

1. The session-scoped autouse :func:`_ensure_qapp_for_session`
   fixture below creates a single ``QApplication`` for the
   whole pytest session, lazily, the first time any test
   actually needs it. Tests that never touch Qt (the majority
   of this repo) never trigger the import.

2. Each test file that previously held a module-level
   ``_QAPP = ...`` line now uses the same lazy approach: the
   line is deleted, the tests that needed ``QApplication``
   inside their bodies still get one because this conftest
   already constructed it.

The shared fixtures (function-scoped, opt-in) live in
:mod:`tests.qt_parent` -- import them via
``from tests.qt_parent import qapp`` when a test needs to
declare its dependency on Qt explicitly.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator

import pytest

# Force offscreen QPA BEFORE any Qt import, mirroring
# tests/qt_parent/server.py. ``setdefault`` preserves any
# value the caller (CI, dev shell, conftest override) already
# set.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _have_pyside6() -> bool:
    """Cheap probe: is PySide6 importable in this interpreter?

    This is intentionally a *probe* -- the real import happens
    inside :func:`_build_qapp`. We avoid a top-level
    ``import PySide6`` so this conftest is safe to load on
    hosts that don't have PySide6 installed (the tests that
    need it will skip with ``pytest.importorskip``).
    """
    try:
        import PySide6  # noqa: F401
    except ImportError:
        return False
    return True


def _build_qapp():
    """Construct the session-wide QApplication singleton.

    Imports are deferred to call time so conftest loading is
    safe on hosts without PySide6. Returns the live
    ``QApplication`` instance.
    """
    from PySide6.QtWidgets import QApplication

    existing = QApplication.instance()
    if existing is not None:
        return existing
    # Empty argv -- we have no CLI args to feed Qt.
    return QApplication(sys.argv or [])


@pytest.fixture(scope="session", autouse=True)
def _ensure_qapp_for_session() -> Iterator[None]:
    """Session-scoped autouse fixture: ensure a QApplication exists.

    On hosts without PySide6, this is a no-op (tests that need
    Qt will skip via ``pytest.importorskip``). On hosts with
    PySide6, the QApplication is built on the first call and
    reused for every subsequent test in the session.
    """
    if not _have_pyside6():
        # No PySide6 -- nothing to do. Tests that actually
        # need Qt will request ``pytest.importorskip("PySide6")``
        # or the ``qapp`` fixture (which also import-skips).
        yield
        return
    _build_qapp()
    yield
    # No explicit teardown: pytest is about to exit and the
    # interpreter shutdown will release the QApplication.
