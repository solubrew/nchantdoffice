"""Regression: NchantdOfficeNotebook must save the open ``.ipynb``
to disk when the user navigates away from the notebook tab, so
unsaved cell edits don't evaporate on tab-switch.

The contract:

  1. ``focusOutEvent`` triggers a belt-and-suspenders save:
     a. Primary: ``Jupyter.notebook.save_notebook()`` via the
        embedded webview's JS runtime (same call Ctrl+S triggers).
     b. Fallback: ``PUT /api/contents/<path>`` against the
        Jupyter REST API with the on-disk notebook JSON.
  2. Both paths update ``config.dikt["last_notebook_path"]`` so a
     reopen (T-NEW-011 / T-NEW-062) restores the same file.
  3. No-op when the webview isn't on a ``/notebooks/<name>`` URL
     (initial blank page or the filebrowser tree) or when
     ``server_running`` is False.
  4. The save is idempotent within a single focus-out burst
     (``_focus_out_save_pending`` guard).
  5. Parent ``focusOutEvent`` still runs (calls ``self.save()``).

This file pins each piece with a focused test so a future refactor
that drops one branch is caught.
"""

import os
import tempfile
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from nchantdoffice.widgets.documents.workbooks.notebooks import (  # noqa: E402
    NchantdOfficeNotebook,
)


def _bare_widget(cls):
    """Allocate a Qt-derived widget without running its constructor."""
    return cls.__new__(cls)


def _notebook_on(url="http://localhost:8888/notebooks/work.ipynb"):
    """Return a bare NchantdOfficeNotebook wired to a fake browser
    whose ``url()`` returns the given Jupyter URL. The webview is
    treated as 'running' so ``_save_jupyter_notebook_on_focus_out``
    reaches the save dispatch."""
    nb = _bare_widget(NchantdOfficeNotebook)
    nb._pending_notebook_path = None
    nb._target_url = url
    nb.server_url = "http://localhost:8888"
    nb.server_running = True
    nb._focus_out_save_pending = False
    nb._last_save_ok = False
    nb._last_save_ts = 0.0
    nb._saved_ipynb_path = None

    fake_url = SimpleNamespace()
    fake_url.toString = lambda: url
    page = MagicMock()
    page.runJavaScript = MagicMock(return_value=None)
    browser = MagicMock()
    browser.url = MagicMock(return_value=fake_url)
    browser.page = MagicMock(return_value=page)
    nb.browser = browser
    # ``config.dikt`` is what the save flow persists to.
    nb.config = SimpleNamespace(dikt={})
    return nb


# ---------------------------------------------------------------------------
# Bug regression: focusOutEvent exists and dispatches the save.
# ---------------------------------------------------------------------------


def test_focusOutEvent_method_exists():
    """T-NEW-168: the notebook widget MUST define ``focusOutEvent``
    so Qt's tab-leave notification reaches the save dispatch."""
    assert hasattr(NchantdOfficeNotebook, "focusOutEvent"), (
        "NchantdOfficeNotebook must override focusOutEvent so the "
        "embedded Jupyter notebook gets saved on tab-switch"
    )


def test_focusOutEvent_calls_save_dispatch_then_super():
    """The focus-out hook runs ``_save_jupyter_notebook_on_focus_out``
    first, then delegates to ``super().focusOutEvent(...)`` so the
    parent class's Nchantd-document save still fires.
    """
    import inspect as _inspect

    src = _inspect.getsource(NchantdOfficeNotebook.focusOutEvent)
    assert "_save_jupyter_notebook_on_focus_out" in src
    assert "super().focusOutEvent(event" in src or "super().focusOutEvent(event," in src \
        or "super().focusOutEvent(event, *args, **kwargs)" in src


# ---------------------------------------------------------------------------
# Bug regression: save dispatch guards.
# ---------------------------------------------------------------------------


def test_save_dispatch_skips_when_no_notebook_url():
    """When the webview is on /tree (or anywhere other than
    ``/notebooks/<name>``), the save dispatch is a no-op. Without
    this guard we'd issue a Jupyter.save_notebook() call against
    the filebrowser root, which is harmless but noisy."""
    nb = _notebook_on(url="http://localhost:8888/tree")
    nb._trigger_js_save_notebook = MagicMock()
    with patch.object(
        NchantdOfficeNotebook,
        "_maybe_http_fallback_save",
        new=MagicMock(),
    ):
        nb._save_jupyter_notebook_on_focus_out()
    nb._trigger_js_save_notebook.assert_not_called()


def test_save_dispatch_skips_when_server_not_running():
    """If Jupyter isn't running, the JS path can't reach
    ``Jupyter.notebook`` and the HTTP path returns 5xx. Skip both."""
    nb = _notebook_on()
    nb.server_running = False
    nb._trigger_js_save_notebook = MagicMock()
    with patch.object(
        NchantdOfficeNotebook,
        "_maybe_http_fallback_save",
        new=MagicMock(),
    ):
        nb._save_jupyter_notebook_on_focus_out()
    nb._trigger_js_save_notebook.assert_not_called()


def test_save_dispatch_fires_js_and_schedules_http_fallback():
    """Happy path: the dispatch runs the JS save and schedules the
    HTTP fallback via QTimer.singleShot(600, ...). The HTTP fallback
    will short-circuit when the JS path reported success."""
    nb = _notebook_on()
    nb._trigger_js_save_notebook = MagicMock()
    with patch(
        "nchantdoffice.widgets.documents.workbooks.notebooks.QTimer.singleShot"
    ) as mock_single:
        nb._save_jupyter_notebook_on_focus_out()
    nb._trigger_js_save_notebook.assert_called_once_with("work.ipynb")
    assert nb._focus_out_save_pending is True
    # 600ms is the agreed delay; tolerate ±100ms.
    args, _ = mock_single.call_args
    assert abs(args[0] - 600) < 100


# ---------------------------------------------------------------------------
# Bug regression: JS save runs the right snippet.
# ---------------------------------------------------------------------------


def test_js_save_invokes_jupyter_save_notebook():
    """The JS dispatched via ``page.runJavaScript`` MUST call
    ``Jupyter.notebook.save_notebook()``. Anything less defeats the
    purpose (Ctrl+S in classic Jupyter is the same call)."""
    nb = _notebook_on()
    nb._trigger_js_save_notebook("work.ipynb")
    page = nb.browser.page()
    assert page.runJavaScript.called
    js = page.runJavaScript.call_args[0][0]
    assert "Jupyter.notebook.save_notebook" in js, (
        f"JS must invoke Jupyter.notebook.save_notebook(); got:\n{js}"
    )


def test_js_save_marks_window_global_with_result():
    """The JS saves its outcome to ``window.__nchantd_last_save``
    so the HTTP fallback path can consult it (or a future log
    scraper) without a JS-to-Python bridge."""
    nb = _notebook_on()
    nb._trigger_js_save_notebook("work.ipynb")
    page = nb.browser.page()
    js = page.runJavaScript.call_args[0][0]
    assert "window.__nchantd_last_save" in js


# ---------------------------------------------------------------------------
# Bug regression: HTTP fallback short-circuits when JS save OK.
# ---------------------------------------------------------------------------


def test_http_fallback_skips_when_js_save_succeeded():
    """When ``_last_save_ok`` is True, the HTTP fallback must NOT
    issue any PUT — the JS save already flushed the disk. Issuing
    an unnecessary PUT can race with the JS path's checkpoint."""
    nb = _notebook_on()
    nb._last_save_ok = True
    nb._http_save_notebook = MagicMock()
    nb._maybe_http_fallback_save("work.ipynb")
    nb._http_save_notebook.assert_not_called()


def test_http_fallback_runs_when_js_save_failed():
    """When ``_last_save_ok`` is False, the HTTP fallback PUTs the
    notebook JSON via the Jupyter REST API so the in-memory state
    is committed."""
    nb = _notebook_on()
    nb._last_save_ok = False
    nb._http_save_notebook = MagicMock()
    with patch(
        "nchantdoffice.widgets.documents.workbooks.notebooks.os.getcwd",
        return_value=tempfile.gettempdir(),
    ):
        nb._maybe_http_fallback_save("work.ipynb")
    nb._http_save_notebook.assert_called_once_with("work.ipynb")
    assert nb._focus_out_save_pending is False
    assert nb._last_save_ok is True


def test_http_fallback_persists_last_notebook_path():
    """After a successful HTTP save, ``config.dikt['last_notebook_path']``
    is set to the resolved on-disk path so a future reopen restores
    the same file (T-NEW-011 / T-NEW-062)."""
    nb = _notebook_on()
    nb._last_save_ok = False
    nb._http_save_notebook = MagicMock()
    with patch(
        "nchantdoffice.widgets.documents.workbooks.notebooks.os.getcwd",
        return_value=tempfile.gettempdir(),
    ):
        nb._maybe_http_fallback_save("work.ipynb")
    assert "last_notebook_path" in nb.config.dikt
    saved = nb.config.dikt["last_notebook_path"]
    assert saved.endswith("work.ipynb"), (
        f"HTTP fallback must persist the resolved .ipynb path; got {saved}"
    )


# ---------------------------------------------------------------------------
# Bug regression: idempotence guard.
# ---------------------------------------------------------------------------


def test_save_dispatch_idempotent_within_a_burst():
    """If two focus-out events fire in rapid succession
    (Qt can fire focus events multiple times during a tab swap),
    the second dispatch must be a no-op. Otherwise we'd queue
    two JS saves + two HTTP fallbacks and one of them would
    race the other."""
    nb = _notebook_on()
    nb._trigger_js_save_notebook = MagicMock()
    with patch(
        "nchantdoffice.widgets.documents.workbooks.notebooks.QTimer.singleShot"
    ):
        nb._save_jupyter_notebook_on_focus_out()
        # second call inside the same burst: guard rejects it
        nb._save_jupyter_notebook_on_focus_out()
    # JS save fired only once across the two dispatches.
    nb._trigger_js_save_notebook.assert_called_once()


def test_focusOutEvent_resets_pending_after_super():
    """After the focus-out dispatch completes, ``_focus_out_save_pending``
    must be reset so the next tab-away event can fire another save.
    The HTTP fallback is the canonical reset point."""
    # We don't run a real focus event here — verify the contract by
    # walking the helper directly.
    nb = _notebook_on()
    nb._trigger_js_save_notebook = MagicMock()
    nb._http_save_notebook = MagicMock()
    with patch(
        "nchantdoffice.widgets.documents.workbooks.notebooks.QTimer.singleShot"
    ):
        nb._save_jupyter_notebook_on_focus_out()
    assert nb._focus_out_save_pending is True, (
        "pending must be True while JS+HTTP are in flight"
    )
    # Simulate the HTTP fallback finishing.
    with patch(
        "nchantdoffice.widgets.documents.workbooks.notebooks.os.getcwd",
        return_value=tempfile.gettempdir(),
    ):
        nb._maybe_http_fallback_save("work.ipynb")
    assert nb._focus_out_save_pending is False, (
        "HTTP fallback must reset _focus_out_save_pending so the next "
        "tab-away can save again"
    )


# ---------------------------------------------------------------------------
# Bug regression: URL parsing.
# ---------------------------------------------------------------------------


def test_current_notebook_filename_strips_query_and_fragment():
    """``/notebooks/work.ipynb?kernel=python3#cell-1`` parses to
    ``work.ipynb``. Query / fragment don't survive — Jupyter's
    ``/api/contents/<path>`` endpoint treats ``?`` and ``#`` as
    part of the path otherwise."""
    nb = _notebook_on(
        url="http://localhost:8888/notebooks/work.ipynb?kernel=python3"
    )
    assert nb._current_notebook_filename() == "work.ipynb"


def test_current_notebook_filename_handles_subdirectory():
    """``/notebooks/sub/dir/foo.ipynb`` parses to ``sub/dir/foo.ipynb``
    (forward slashes preserved through ``urllib.parse.quote(safe='/')``).
    The Jupyter REST API accepts path separators inside ``<path>``
    when ``safe='/'`` is used in the quote."""
    nb = _notebook_on(url="http://localhost:8888/notebooks/sub/dir/foo.ipynb")
    assert nb._current_notebook_filename() == "sub/dir/foo.ipynb"


def test_current_notebook_filename_returns_empty_for_tree():
    """``/tree`` (filebrowser) is NOT a notebook URL."""
    nb = _notebook_on(url="http://localhost:8888/tree")
    assert nb._current_notebook_filename() == ""


def test_current_notebook_filename_returns_empty_for_blank():
    """``about:blank`` (initial load) is NOT a notebook URL."""
    nb = _notebook_on(url="about:blank")
    assert nb._current_notebook_filename() == ""
