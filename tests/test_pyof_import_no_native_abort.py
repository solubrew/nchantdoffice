"""Regression guard: ``test_cmd_import_pyof_calls_orchestrator`` must
not abort the interpreter.

T-NEW suite stabilisation, 2026-08-18: the integration test in
``tests/test_pyof_import.py::test_cmd_import_pyof_calls_orchestrator``
constructs a real ``QThread`` via ``cmd_import_pyof`` and never waits
for it to finish. After the test function returns, the running
``QThread`` is garbage-collected along with the bare ``__new__``
instance, and Qt's destruction-time check
(``QThread: Destroyed while thread '' is still running``) escalates
to a native SIGABRT (exit -6). In the full suite, the SIGABRT
sometimes lands inside the next test's ``ast.parse`` call (the
``Garbage-collecting`` -> ``ast.parse`` abort trace), making the
abort non-deterministic but consistently fatal at the same ~49%
progress mark.

The guard runs the offending test in a fresh subprocess and asserts
the subprocess exits cleanly:

  1. Return code is 0 (no SIGABRT).
  2. stderr does NOT contain ``QThread: Destroyed while thread``.
  3. The pytest run itself reports the test as PASSED.

If any of those three checks fail, the guard fails. This is a
**regression** guard -- it cannot fix the underlying bug; the fix
lives in ``test_cmd_import_pyof_calls_orchestrator`` itself.

Why a subprocess (not an in-process check):

  * In-process, the bug only manifests when the *next* test runs and
    triggers GC. A subprocess containing only the offending test
    reproduces the abort reliably (verified 2026-08-18: exit -6,
    ``QThread: Destroyed while thread '' is still running`` on
    stderr).
  * The subprocess is fresh: no leftover QApplication from prior
    tests, no test-leader QThread still alive.
  * ``QT_QPA_PLATFORM=offscreen`` lets PySide6 import without a real
    display (the test already sets this; we re-export for safety).

This test runs the ``QThread`` integration path through the real
production ``cmd_import_pyof`` so any future regression that
re-introduces an un-cleaned-up ``QThread`` (or any other Qt native
abort) trips the guard immediately.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


# Locate the offending test by node id so the guard is robust to file
# renames inside the test directory.
_OFFENDING_NODEID = (
    "tests/test_pyof_import.py::test_cmd_import_pyof_calls_orchestrator"
)
# Substring that Qt prints to stderr when a QThread is destroyed
# while still running. Match on this rather than the full line so
# Qt-side wording tweaks don't break the guard.
_QTHREAD_DESTROYED_MARKER = "QThread: Destroyed while thread"
# Wallclock cap. The test usually finishes in <10s on this host;
# 60s is generous and short enough that a hang fails the suite
# quickly.
_TIMEOUT_SECONDS = 60


def _run_offending_test_in_subprocess() -> subprocess.CompletedProcess:
    """Spawn a clean Python process that runs only the offending
    pytest node, with ``QT_QPA_PLATFORM=offscreen`` and the repo root
    on ``PYTHONPATH``. Returns the completed process so the caller
    can inspect returncode + stderr.
    """
    repo_root = Path(__file__).resolve().parent.parent
    env = dict(os.environ)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        str(repo_root) + os.pathsep + existing_pythonpath
    )
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        _OFFENDING_NODEID,
        "-v",
        "--tb=short",
        "-p",
        "no:cacheprovider",
    ]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_SECONDS,
        env=env,
        cwd=str(repo_root),
    )


def test_cmd_import_pyof_calls_orchestrator_does_not_abort_subprocess():
    """The offending integration test must run cleanly in a fresh
    subprocess: pytest exit code 0, no ``QThread: Destroyed`` on
    stderr, and the test itself reported as PASSED.

    If the underlying bug returns (an un-waited ``QThread`` that Qt
    aborts during destruction), the subprocess exits with ``-6``
    (SIGABRT) and the stderr contains ``QThread: Destroyed while
    thread '' is still running`` -- both of which fail this guard.
    """
    proc = _run_offending_test_in_subprocess()

    # Check 1: clean exit. SIGABRT would surface as a negative
    # return code; pytest's own non-zero codes (1/2/3/4/5) would
    # mean the test failed before the abort even fired. We want 0.
    assert proc.returncode == 0, (
        "Subprocess running "
        f"{_OFFENDING_NODEID} exited with code {proc.returncode}; "
        "the integration test must not abort the interpreter. "
        "Last 1500 chars of stdout:\n"
        f"{proc.stdout[-1500:]}\n"
        "Last 1500 chars of stderr:\n"
        f"{proc.stderr[-1500:]}"
    )

    # Check 2: no QThread-destroyed-while-running warning. This is
    # the Qt-side signal that an un-waited QThread was GC'd.
    assert _QTHREAD_DESTROYED_MARKER not in proc.stderr, (
        f"Subprocess stderr contains {_QTHREAD_DESTROYED_MARKER!r}; "
        "a QThread was destroyed while still running, which Qt "
        "escalates to SIGABRT. The integration test must wait for "
        "the worker thread to finish before returning. stderr:\n"
        f"{proc.stderr[-1500:]}"
    )

    # Check 3: pytest itself reports the test as PASSED. Pytest
    # prints "1 passed" on success. We accept either "1 passed" or
    # the verbose "::test_cmd_import_pyof_calls_orchestrator PASSED"
    # so future pytest formatting tweaks don't break the guard.
    assert "PASSED" in proc.stdout, (
        f"Subprocess stdout does not report the test as PASSED. "
        "Last 1500 chars of stdout:\n"
        f"{proc.stdout[-1500:]}"
    )


def test_cmd_import_pyof_calls_orchestrator_does_not_abort_in_full_suite():
    """The same contract, checked against the full pytest run for
    this single test module. If the fix only patches the test in a
    way that works in isolation but still aborts when run with the
    rest of the suite (e.g. shared ``QApplication`` state,
    lingering prior threads), this guard catches it.

    Running just ``tests/test_pyof_import.py`` exercises the
    integration test in the same pytest process as the rest of the
    module's tests. If the integration test leaks a QThread but the
    module's own teardown runs first, the abort might be suppressed
    in-module -- but the full-suite abort pattern was tied to the
    integration test running alone (verified 2026-08-18). This
    guard runs both:

      (a) the offending test in isolation (above), and
      (b) the offending test as part of its whole module.

    The (b) run must also exit cleanly. The integration test must
    not abort when other tests in the same module run before/after
    it.
    """
    repo_root = Path(__file__).resolve().parent.parent
    env = dict(os.environ)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        str(repo_root) + os.pathsep + existing_pythonpath
    )
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_pyof_import.py",
        "-v",
        "--tb=short",
        "-p",
        "no:cacheprovider",
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_SECONDS * 2,
        env=env,
        cwd=str(repo_root),
    )
    assert proc.returncode == 0, (
        f"pytest tests/test_pyof_import.py exited with code "
        f"{proc.returncode}; the module must exit cleanly. "
        "Last 1500 chars of stdout:\n"
        f"{proc.stdout[-1500:]}\n"
        "Last 1500 chars of stderr:\n"
        f"{proc.stderr[-1500:]}"
    )
    assert _QTHREAD_DESTROYED_MARKER not in proc.stderr, (
        f"pytest tests/test_pyof_import.py stderr contains "
        f"{_QTHREAD_DESTROYED_MARKER!r}; a QThread was destroyed "
        "while still running. The integration test must wait for "
        "the worker thread to finish before returning. stderr:\n"
        f"{proc.stderr[-1500:]}"
    )
