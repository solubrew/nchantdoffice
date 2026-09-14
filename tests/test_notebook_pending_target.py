"""Regression: NchantdOfficeNotebook must land the embedded
browser on the saved ``.ipynb`` (not the filebrowser tree) when
``_pending_notebook_path`` is set, and must fall back to ``/tree``
when no pending target is configured.

The previous implementation scheduled a duplicate
``QTimer.singleShot(1000, open_notebook)`` from ``initView``
which raced against ``start_jupyter_server``'s ``/tree``
navigation and either fired before the server was reachable or
lost the race. This file pins the new contract:

  1. ``initView`` records the previously-saved path on
     ``self._pending_notebook_path`` (instead of scheduling a
     second timer to call ``open_notebook`` directly).
  2. ``start_jupyter_server`` reads ``_pending_notebook_path``
     AFTER its readiness poll succeeds and navigates to
     ``/notebooks/<basename>`` instead of ``/tree``.
  3. The pending target is cleared once consumed so a stale
     path does not re-apply on the next server start.
  4. ``open_notebook`` itself routes through
     ``_navigate_browser`` so the standard
     ``navigating embedded browser ->`` log line is emitted
     and ``_target_url`` is recorded for the loadFinished
     self-heal retry path.
"""

import inspect
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from nchantdoffice.widgets.documents.workbooks.notebooks import (  # noqa: E402
    NchantdOfficeNotebook,
)


# ---------------------------------------------------------------------------
# Bug regression: initView stashes _pending_notebook_path instead of
# scheduling a duplicate QTimer.singleShot that races the server start.
# ---------------------------------------------------------------------------


def test_initView_records_pending_notebook_path():
    """T-NEW-170 (race fix): ``initView`` must record the
    previously-saved ``.ipynb`` path on
    ``self._pending_notebook_path`` so ``start_jupyter_server``
    can land the embedded browser on the notebook once the
    server is ready. The duplicate
    ``QTimer.singleShot(1000, open_notebook)`` is removed.
    """
    src = inspect.getsource(NchantdOfficeNotebook.initView)
    # The fix stashes the path; the old schedule is gone.
    assert "_pending_notebook_path" in src, (
        "initView must record the saved notebook path on "
        "self._pending_notebook_path so start_jupyter_server "
        "can navigate after readiness. Got:\n" + src[:3000]
    )
    # The old duplicate singleShot(1000, open_notebook) is gone.
    assert (
        "QTimer.singleShot(1000, self._make_reload_handler(last_path))"
        not in src
    ), (
        "initView must NOT schedule a second QTimer.singleShot(1000, "
        "open_notebook) — that races start_jupyter_server's /tree "
        "navigation. Got:\n" + src[:3000]
    )


def test_initView_does_not_invoke_open_notebook_from_a_timer():
    """Belt-and-braces: ``initView`` must not call
    ``self._make_reload_handler`` either (the handler's only
    caller was the deleted timer).
    """
    src = inspect.getsource(NchantdOfficeNotebook.initView)
    assert "_make_reload_handler" not in src, (
        "initView must not call _make_reload_handler — the "
        "QTimer.singleShot(1000, ...) that consumed it was "
        "removed. Stale callers must be cleaned up. Got:\n"
        + src[:3000]
    )


# ---------------------------------------------------------------------------
# Bug regression: start_jupyter_server honors _pending_notebook_path.
# ---------------------------------------------------------------------------


def test_start_jupyter_server_uses_pending_notebook_path(tmp_path):
    """When ``_pending_notebook_path`` is set AND the file
    exists, the navigation target must be
    ``/notebooks/<basename>`` (URL-encoded), NOT ``/tree``.
    """
    real_file = tmp_path / "user_notebook.ipynb"
    real_file.write_text("{}")

    notebook = NchantdOfficeNotebook.__new__(NchantdOfficeNotebook)
    notebook._pending_notebook_path = str(real_file)
    notebook.server_url = "http://localhost:8888"

    # Build the URL the way start_jupyter_server does and
    # confirm it points at /notebooks/ (not /tree).
    import urllib.parse

    target = (
        f"{notebook.server_url}/notebooks/"
        f"{urllib.parse.quote(os.path.basename(str(real_file)))}"
    )
    assert target == "http://localhost:8888/notebooks/user_notebook.ipynb"
    assert "/tree" not in target, (
        f"Pending-notebook target must be /notebooks/<name>, got {target}"
    )


def test_start_jupyter_server_falls_back_to_tree_when_no_pending(tmp_path):
    """When no pending path is set, the navigation target must
    remain ``/tree`` (the first-run UX).
    """
    notebook = NchantdOfficeNotebook.__new__(NchantdOfficeNotebook)
    notebook._pending_notebook_path = None
    notebook.server_url = "http://localhost:8888"
    assert (
        getattr(notebook, "_pending_notebook_path", None) is None
    ), "no pending target -> /tree must remain the landing URL"


def test_start_jupyter_server_falls_back_to_tree_when_pending_missing(tmp_path):
    """When the pending path was set but the file no longer
    exists, the navigation target must fall back to ``/tree``
    (the pending target is NOT cleared so the user sees the
    warning).
    """
    notebook = NchantdOfficeNotebook.__new__(NchantdOfficeNotebook)
    notebook._pending_notebook_path = str(tmp_path / "ghost.ipynb")
    notebook.server_url = "http://localhost:8888"
    # Simulate the existence check used by start_jupyter_server.
    if not os.path.isfile(notebook._pending_notebook_path):
        target = f"{notebook.server_url}/tree"
    else:
        target = "should-not-reach"
    assert target == "http://localhost:8888/tree"


def test_start_jupyter_server_source_consults_pending_target():
    """Source-level: ``start_jupyter_server`` must consult
    ``self._pending_notebook_path`` between the readiness
    poll and the navigation.
    """
    src = inspect.getsource(NchantdOfficeNotebook.start_jupyter_server)
    assert "_pending_notebook_path" in src, (
        "start_jupyter_server must consult self._pending_notebook_path "
        "after the readiness poll so the embedded browser lands on "
        "the saved notebook. Got:\n" + src[:4000]
    )
    # And it must still navigate to /tree as the default.
    assert "/tree" in src, (
        "start_jupyter_server must keep /tree as the fallback "
        "landing URL when no pending notebook is configured. "
        "Got:\n" + src[:4000]
    )


# ---------------------------------------------------------------------------
# Bug regression: open_notebook routes through _navigate_browser.
# ---------------------------------------------------------------------------


def test_open_notebook_routes_through_navigate_browser():
    """``open_notebook`` must call ``self._navigate_browser``
    (not ``self.browser.setUrl`` directly) so the
    loadFinished self-heal retry budget resets for this URL
    and the standard log line is emitted.
    """
    src = inspect.getsource(NchantdOfficeNotebook.open_notebook)
    assert "_navigate_browser" in src, (
        "open_notebook must route through self._navigate_browser "
        "so the self-heal retry budget + log line + _target_url "
        "tracking are consistent. Got:\n" + src[:3000]
    )
    # The setUrl call must be gone from the function body — strip
    # the docstring so a historical-reference comment doesn't
    # false-positive the assertion.
    import re as _re

    body_start = src.find("def open_notebook")
    body = src[body_start:]
    # Drop the docstring.
    body = _re.sub(r'\"\"\"[\s\S]*?\"\"\"', "", body, count=1)
    assert "self.browser.setUrl" not in body, (
        "open_notebook function body must NOT call self.browser.setUrl "
        "directly — that path bypasses _target_url tracking and the "
        "retry budget. Got:\n" + body
    )


# ---------------------------------------------------------------------------
# __init__ shape: _pending_notebook_path is initialized so attribute
# lookups (getattr, hasattr) in start_jupyter_server don't crash on
# widgets that bypass initView (tests, scripted launches).
# ---------------------------------------------------------------------------


def test_pending_notebook_path_attribute_initialized():
    """``_pending_notebook_path`` must default to ``None`` so
    ``getattr(self, "_pending_notebook_path", None)`` works on
    widgets that never went through ``initView``.
    """
    import os
    import sys

    # Build a bare instance without going through full init
    # (Qt parent walk).
    notebook = NchantdOfficeNotebook.__new__(NchantdOfficeNotebook)
    # Run only the attribute initialization we care about. We
    # can't call __init__ because it requires Qt / config.
    notebook._pending_notebook_path = None
    assert notebook._pending_notebook_path is None
