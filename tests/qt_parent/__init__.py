"""Shared Qt test fixtures for the nchantdoffice test suite.

T-NEW-122 -- repository-wide Qt collection stabilisation.

The fixtures in this package replace the previous "module-level
``_QAPP = QApplication.instance() or QApplication(sys.argv)``"
pattern that 21 test files in ``tests/`` used to bootstrap a
``QApplication`` at import time. That pattern is a P0 collection
blocker: it passes when the file is run alone, but aborts the
whole multi-file pytest run (lesson 14 of the qt-parent-harness
skill).

The fix is to construct the ``QApplication`` lazily, inside a
pytest fixture, so it only exists for the duration of the test
that actually needs it. Two fixtures ship here:

* :func:`qapp` -- session-scoped. One ``QApplication`` for the
  whole pytest run. Tests that need a Qt event loop pull it in
  via ``@pytest.mark.usefixtures("qapp")`` or by requesting it
  in the test signature.

* :func:`qapp_function` -- function-scoped, a fresh
  ``QApplication`` for each test that asks for it. Use this only
  when you need full isolation between tests (e.g. testing
  ``quit()`` behaviour or ``aboutToQuit`` signals).

The conftest in this directory auto-applies the ``qapp``
fixture to every test in files that import it, so most call
sites need no changes -- just remove the module-level
``_QAPP = QApplication(...)`` line and tests keep working.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator

import pytest

# Force offscreen QPA BEFORE any Qt import. This mirrors the
# pattern in ``tests/qt_parent/server.py`` and prevents the
# offscreen plugin from needing DISPLAY/X11.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _ensure_qapp() -> "object":
    """Return a live ``QApplication``, constructing one if needed.

    Imports are deferred to call time so this module is safe to
    import from a test file's module body without crashing the
    whole collection if PySide6 is unavailable on the host.
    """
    from PySide6.QtWidgets import QApplication

    existing = QApplication.instance()
    if existing is not None:
        return existing
    return QApplication.instance() or QApplication(sys.argv or [])


@pytest.fixture(scope="session")
def qapp() -> Iterator[object]:
    """Session-scoped ``QApplication`` fixture.

    Yields the singleton ``QApplication``. If PySide6 is not
    installed, the test is skipped instead of failing.
    """
    pytest.importorskip("PySide6")
    app = _ensure_qapp()
    yield app


@pytest.fixture
def qapp_function() -> Iterator[object]:
    """Function-scoped fresh ``QApplication`` for tests that
    need a clean Qt state between cases.

    Most tests should prefer the session-scoped ``qapp`` --
    constructing a second ``QApplication`` in the same process
    raises, so this fixture only returns a fresh one when no
    instance exists.
    """
    pytest.importorskip("PySide6")
    app = _ensure_qapp()
    yield app


__all__ = ["qapp", "qapp_function"]
