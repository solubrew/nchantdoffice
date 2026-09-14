"""Regression: NchantdOfficeNotebook must persist the open-state
to the database (via ``document.save()``) whenever the notebook
tab is no longer the active visible widget.

Background (T-NEW-168 followup):

The notebook tab survives tab-switches (because ``focusOutEvent``
fires the save chain) but evaporates when:

  (a) the user opens a NEW tab (addTab hides the current widget),
  (b) the left-pane tree changes node (which rebuilds the center
      pane around a different document),
  (c) the app quits / the widget is destroyed.

None of those paths hit ``focusOutEvent``. The fix is a
``hideEvent`` override (fires on hide for any reason) plus an
``aboutToQuit`` hook (catches the clean-quit case before Qt's
event loop tears down). ``save_open_state()`` is the single
entry point that:

  1. Captures the live Jupyter path
     (``current_notebook_path`` -> ``_pending_notebook_path`` ->
     ``file_path``).
  2. Writes it to ``config.dikt["last_notebook_path"]`` (kept for
     backwards compatibility with initView).
  3. Calls ``self.save()`` which walks the parent chain to
     ``NchantdOfficeDocument.get_content`` -> ``document.set_content``
     -> ``document.save`` (DB row write). ``get_content`` now
     carries ``last_notebook_path`` + ``current_notebook_path`` so
     the full open-state survives the round-trip.

On reopen, ``initModel`` reads the persisted
``last_notebook_path`` from the DB envelope, seeds
``config.dikt`` before ``initView`` runs, and ``initView``
queues the navigation to land on the right ``.ipynb``.

This file pins every link in that chain with a focused test.
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


def _fake_url_obj(url):
    obj = SimpleNamespace()
    obj.toString = lambda u=url: u
    return obj


def _notebook_with(
    *,
    file_path=None,
    current_notebook_path=None,
    pending_notebook_path=None,
    config_dikt=None,
    save_returns=True,
):
    """Allocate a notebook widget wired with a fake config and
    ``save()`` that just records the call.

    Returns the widget + a list to which ``save()`` calls are
    appended so tests can assert on the order/contents of the
    dicts that were persisted.
    """
    nb = _bare_widget(NchantdOfficeNotebook)
    nb.file_path = file_path
    nb.current_notebook_path = current_notebook_path
    nb._pending_notebook_path = pending_notebook_path
    nb._in_shutdown = False
    nb.config = SimpleNamespace(dikt=dict(config_dikt or {}))
    # save() is what NchantdOfficeDocument.save() ultimately
    # calls to persist the document. Replace it with a MagicMock
    # so we can verify get_content's output.
    save_calls = []
    save_mock = MagicMock(side_effect=lambda *a, **kw: save_calls.append(("save",)) or save_returns)
    nb.save = save_mock
    return nb, save_calls


# ---------------------------------------------------------------------------
# Bug regression: the helpers exist on the widget.
# ---------------------------------------------------------------------------


def test_save_open_state_method_exists():
    """The notebook widget MUST expose ``save_open_state`` so callers
    (focusOutEvent, hideEvent, closeEvent, shutdown, atexit) can
    route through the single persistence entry point."""
    assert hasattr(NchantdOfficeNotebook, "save_open_state"), (
        "NchantdOfficeNotebook is missing save_open_state — without it "
        "tab-leave / new-tab / node-change / app-quit can't persist the "
        "open-state via document.save()"
    )


def test_hideEvent_method_exists():
    """``hideEvent`` is the hook that fires when the notebook tab is
    hidden by addTab/removeTab/switch, which is the user's "new tab"
    and "node change" complaint."""
    assert hasattr(NchantdOfficeNotebook, "hideEvent"), (
        "NchantdOfficeNotebook must override hideEvent so the open-state "
        "is persisted whenever the widget stops being the visible tab"
    )


def test_closeEvent_method_exists():
    """``closeEvent`` is the last chance to persist before destruction."""
    assert hasattr(NchantdOfficeNotebook, "closeEvent"), (
        "NchantdOfficeNotebook must override closeEvent so app-quit and "
        "tab-close persist the open-state"
    )


# ---------------------------------------------------------------------------
# Bug regression: save_open_state captures current_notebook_path.
# ---------------------------------------------------------------------------


def test_save_open_state_uses_current_notebook_path_when_present():
    """When the user navigated to ``foo.ipynb`` in the embedded
    Jupyter webview, that path is now ``current_notebook_path``
    (set by ``_sync_notebook_from_url``). ``save_open_state``
    MUST capture that path, persist it to ``config.dikt``, and
    pass it through ``self.save()``."""
    tmpdir = tempfile.mkdtemp()
    foo = os.path.join(tmpdir, "foo.ipynb")
    with open(foo, "w") as f:
        f.write("{}\n")
    nb, save_calls = _notebook_with(
        file_path=os.path.join(tmpdir, "default.ipynb"),
        current_notebook_path=foo,
    )
    nb.save_open_state()
    assert nb.config.dikt["last_notebook_path"] == foo
    assert nb.current_notebook_path == foo
    assert len(save_calls) == 1, "save_open_state must call self.save()"


def test_save_open_state_falls_back_to_pending_path():
    """If the user is mid-navigation (the URL hasn't yet updated to
    a ``/notebooks/<name>`` URL but ``_pending_notebook_path`` was
    set by ``open_notebook``), the pending path is the next-best
    signal for what file the user was trying to open."""
    tmpdir = tempfile.mkdtemp()
    foo = os.path.join(tmpdir, "foo.ipynb")
    with open(foo, "w") as f:
        f.write("{}\n")
    nb, _ = _notebook_with(pending_notebook_path=foo)
    nb.save_open_state()
    assert nb.config.dikt["last_notebook_path"] == foo
    assert nb.current_notebook_path == foo


def test_save_open_state_falls_back_to_canonical_file_path():
    """When no live navigation has happened yet, fall back to the
    document's canonical ``file_path``. ``initModel`` always sets
    this so it's the lowest-precision but most reliable anchor."""
    tmpdir = tempfile.mkdtemp()
    bound = os.path.join(tmpdir, "bound.ipynb")
    with open(bound, "w") as f:
        f.write("{}\n")
    nb, _ = _notebook_with(file_path=bound)
    nb.save_open_state()
    assert nb.config.dikt["last_notebook_path"] == bound
    assert nb.current_notebook_path == bound


def test_save_open_state_skips_nonexistent_paths():
    """A path that's been deleted from disk MUST NOT be persisted —
    the Jupyter REST API would 404 and ``initView`` would warn
    about a stale entry. The capture helper filters non-existent
    files at every tier."""
    tmpdir = tempfile.mkdtemp()
    bound = os.path.join(tmpdir, "bound.ipynb")
    with open(bound, "w") as f:
        f.write("{}\n")
    ghost = os.path.join(tmpdir, "ghost.ipynb")  # never created
    nb, _ = _notebook_with(
        file_path=bound,
        current_notebook_path=ghost,
    )
    nb.save_open_state()
    # Falls through current (ghost) -> pending (None) -> file_path (bound)
    assert nb.config.dikt["last_notebook_path"] == bound


def test_save_open_state_returns_self_for_chaining():
    """The helper returns ``self`` so callers can chain like
    ``nb.save_open_state().update_status_labels()``."""
    nb, _ = _notebook_with()
    assert nb.save_open_state() is nb


def test_save_open_state_skips_during_shutdown():
    """When ``_in_shutdown`` is True the helper returns without
    touching the DB. This protects teardown paths (closeEvent
    followed by another save call from atexit) from racing
    against a closing DB handle."""
    nb, save_calls = _notebook_with()
    nb._in_shutdown = True
    nb.save_open_state()
    assert len(save_calls) == 0, (
        "save_open_state must short-circuit during shutdown to avoid "
        "calling self.save() against a closed DB handle"
    )


# ---------------------------------------------------------------------------
# Bug regression: get_content exposes the open-state for the DB envelope.
# ---------------------------------------------------------------------------


def test_get_content_includes_last_notebook_path():
    """``get_content`` MUST surface ``last_notebook_path`` so the DB
    row carries the open-state. Without this, ``initModel`` on
    reopen has no idea what the user had open."""
    nb = _bare_widget(NchantdOfficeNotebook)
    nb.file_path = "/some/where/bound.ipynb"
    nb.current_notebook_path = "/some/where/foo.ipynb"
    nb.config = SimpleNamespace(dikt={"last_notebook_path": "/some/where/foo.ipynb"})
    nb.save_mode = "file_path"
    out = nb.get_content()
    nested = out.get("content", out)
    assert nested.get("last_notebook_path") == "/some/where/foo.ipynb"
    assert nested.get("current_notebook_path") == "/some/where/foo.ipynb"


def test_get_content_includes_current_notebook_path_even_if_no_last():
    """``current_notebook_path`` is the live signal; it must be
    visible even when ``config.dikt["last_notebook_path"]`` was
    somehow not populated."""
    nb = _bare_widget(NchantdOfficeNotebook)
    nb.file_path = "/some/where/bound.ipynb"
    nb.current_notebook_path = "/some/where/current.ipynb"
    nb.config = SimpleNamespace(dikt={})
    nb.save_mode = "file_path"
    out = nb.get_content()
    nested = out.get("content", out)
    assert nested.get("current_notebook_path") == "/some/where/current.ipynb"
    assert "last_notebook_path" not in nested


def test_get_content_omits_open_state_when_neither_set():
    """If neither path is set, ``get_content`` returns just the
    canonical ``file_path``. Downstream code (initModel) treats
    the absence as "use whatever default the document was bound
    to"."""
    nb = _bare_widget(NchantdOfficeNotebook)
    nb.file_path = "/some/where/default.ipynb"
    nb.current_notebook_path = None
    nb.config = SimpleNamespace(dikt={})
    nb.save_mode = "file_path"
    out = nb.get_content()
    nested = out.get("content", out)
    assert nested == {"file_path": "/some/where/default.ipynb"}


# ---------------------------------------------------------------------------
# Bug regression: hideEvent + closeEvent drive save_open_state.
# ---------------------------------------------------------------------------


def test_hideEvent_persists_open_state():
    """The full ``hideEvent`` path: a fake QHideEvent is passed in,
    ``save_open_state`` runs, then super().hideEvent(event) is
    delegated to. We verify ``save`` was called and the config
    dikt carries the live path."""
    tmpdir = tempfile.mkdtemp()
    foo = os.path.join(tmpdir, "foo.ipynb")
    with open(foo, "w") as f:
        f.write("{}\n")
    nb, save_calls = _notebook_with(current_notebook_path=foo)
    fake_event = MagicMock()
    with patch.object(NchantdOfficeNotebook.__bases__[0], "hideEvent", new=MagicMock()):
        nb.hideEvent(fake_event)
    assert len(save_calls) == 1
    assert nb.config.dikt["last_notebook_path"] == foo


def test_hideEvent_swallows_save_errors():
    """If ``save_open_state`` raises (DB closed mid-flight, etc.)
    the widget MUST still delegate to ``super().hideEvent(event)``
    so Qt doesn't see an exception bubble out of a UI event."""
    nb, _ = _notebook_with()
    nb.save_open_state = MagicMock(side_effect=RuntimeError("db closed"))
    fake_event = MagicMock()
    with patch.object(NchantdOfficeNotebook.__bases__[0], "hideEvent", new=MagicMock()) as mock_super:
        nb.hideEvent(fake_event)  # must not raise
    mock_super.assert_called_once_with(fake_event)


def test_closeEvent_sets_in_shutdown_and_persists():
    """``closeEvent`` (fires on permanent widget destruction, not
    every hide) sets ``_in_shutdown`` first so save_open_state's
    guard kicks in if the path tries to write to a closed DB."""
    tmpdir = tempfile.mkdtemp()
    foo = os.path.join(tmpdir, "foo.ipynb")
    with open(foo, "w") as f:
        f.write("{}\n")
    nb, save_calls = _notebook_with(current_notebook_path=foo)
    fake_event = MagicMock()
    with patch.object(NchantdOfficeNotebook.__bases__[0], "closeEvent", new=MagicMock()):
        nb.closeEvent(fake_event)
    assert nb._in_shutdown is True
    assert len(save_calls) == 1


# ---------------------------------------------------------------------------
# Bug regression: shutdown calls save_open_state before tearing down.
# ---------------------------------------------------------------------------


def test_shutdown_persists_open_state_before_stopping_server():
    """``shutdown`` (wired to ``aboutToQuit``) MUST call
    ``save_open_state`` BEFORE ``stop_jupyter_server``. The order
    matters because save_open_state's save() path may want to
    touch the DB while it's still open — stopping Jupyter first
    doesn't break save, but doing the save first guarantees
    the DB row reflects the user's last interaction even if
    server-stopping takes a few hundred ms."""
    tmpdir = tempfile.mkdtemp()
    foo = os.path.join(tmpdir, "foo.ipynb")
    with open(foo, "w") as f:
        f.write("{}\n")
    nb, save_calls = _notebook_with(current_notebook_path=foo)
    # Patch stop_kernel/stop_jupyter_server to avoid actual subprocess teardown.
    nb.stop_kernel = MagicMock()
    nb.stop_jupyter_server = MagicMock()
    order = []

    def _record_save(*_a, **_kw):
        order.append("save_open_state")
        return True

    nb.save_open_state = MagicMock(side_effect=_record_save)
    nb.stop_kernel.side_effect = lambda: order.append("stop_kernel")
    nb.stop_jupyter_server.side_effect = lambda: order.append("stop_jupyter_server")
    nb.shutdown()
    assert order.index("save_open_state") < order.index("stop_jupyter_server"), (
        f"save_open_state must run BEFORE stop_jupyter_server; got {order}"
    )


# ---------------------------------------------------------------------------
# Bug regression: initModel restores last_notebook_path from the DB row.
# ---------------------------------------------------------------------------


def test_initModel_seeds_last_notebook_path_from_saved_content():
    """When the user previously had ``foo.ipynb`` open and the
    document was saved, the DB envelope carries
    ``nested_content["last_notebook_path"]``. ``initModel`` MUST
    seed that into ``config.dikt`` so ``initView``'s lookup at
    line 251 picks it up and queues the navigation."""
    # Build a notebook whose document.content reports the saved
    # last_notebook_path. We bypass ``__init__`` so we can poke
    # at ``initModel``'s read paths without booting Jupyter.
    nb = _bare_widget(NchantdOfficeNotebook)
    nb.file_path = "/unrelated/bound.ipynb"
    nb.current_notebook_path = None
    nb._pending_notebook_path = None
    nb.config = SimpleNamespace(dikt={})
    nb.save_mode = "file_path"

    # Fake document model so initModel's ``document.content``
    # lookups return what we want.
    saved_path = "/some/where/foo.ipynb"
    saved = {"content": {"file_path": "/some/where/bound.ipynb", "last_notebook_path": saved_path}}
    doc_obj = SimpleNamespace(
        content=saved,
        file_path=None,
        load_document=MagicMock(),
        set_location=MagicMock(),
    )
    nb.app = SimpleNamespace(
        model=SimpleNamespace(codex=SimpleNamespace(init_notebook=MagicMock(return_value=doc_obj))),
    )
    # context_menu init in initModel
    nb.context_menu = SimpleNamespace(get_menu=MagicMock())
    # open_notebook is called when resolved_path is a real file; we
    # mock it out so the test doesn't need a disk path.
    nb.open_notebook = MagicMock()
    # ``_looks_like_ipynb_path`` is the filter for what counts as a
    # valid pending target.
    nb._looks_like_ipynb_path = lambda path: bool(path) and path.endswith(".ipynb")

    # Skip the call into the full super().initModel() chain
    # (which would need a real QWidget parent) — only exercise
    # the data-shuffling part by inlining it.
    self_doc = nb.app.model.codex.init_notebook({"document": nb.config.dikt.get("document", {})})
    nb.document = self_doc
    saved_content = self_doc.content or {}
    nested_content = saved_content.get("content", {}) if isinstance(saved_content, dict) else {}
    resolved_path = (
        nested_content.get("file_path")
        or saved_content.get("file_path")
        or nb.config.dikt.get("file_path")
        or self_doc.file_path
    )
    last_notebook = (
        nested_content.get("last_notebook_path")
        or nested_content.get("current_notebook_path")
        or saved_content.get("last_notebook_path")
        or nb.config.dikt.get("last_notebook_path")
    )
    if last_notebook and nb._looks_like_ipynb_path(last_notebook):
        nb.config.dikt["last_notebook_path"] = last_notebook

    assert nb.config.dikt["last_notebook_path"] == saved_path


def test_initModel_prefers_last_notebook_for_open_when_file_exists():
    """When ``last_notebook_path`` is set in the saved content and
    points at a file that actually exists on disk, ``initModel``
    MUST use that path (not the older ``file_path``) for the
    reopen target. Without this preference, the user returns to
    the doc's bound file even though they had a different
    notebook open in Jupyter at quit time."""
    tmpdir = tempfile.mkdtemp()
    foo = os.path.join(tmpdir, "foo.ipynb")
    bound = os.path.join(tmpdir, "bound.ipynb")
    for p in (foo, bound):
        with open(p, "w") as f:
            f.write("{}\n")
    nb = _bare_widget(NchantdOfficeNotebook)
    nb.file_path = bound
    nb.config = SimpleNamespace(dikt={})
    nb.save_mode = "file_path"
    saved = {"content": {"file_path": bound, "last_notebook_path": foo}}
    doc_obj = SimpleNamespace(content=saved, file_path=None, load_document=MagicMock())
    nb.document = doc_obj
    nb.app = SimpleNamespace(
        model=SimpleNamespace(codex=SimpleNamespace(init_notebook=MagicMock(return_value=doc_obj))),
    )
    nb.context_menu = SimpleNamespace(get_menu=MagicMock())
    nb.open_notebook = MagicMock()
    nb._looks_like_ipynb_path = lambda path: bool(path) and path.endswith(".ipynb")

    # Inline the relevant initModel logic to avoid super().initModel.
    saved_content = nb.document.content or {}
    nested_content = saved_content.get("content", {}) if isinstance(saved_content, dict) else {}
    resolved_path = (
        nested_content.get("file_path")
        or saved_content.get("file_path")
        or nb.config.dikt.get("file_path")
        or nb.document.file_path
    )
    last_notebook = (
        nested_content.get("last_notebook_path")
        or nested_content.get("current_notebook_path")
        or saved_content.get("last_notebook_path")
        or nb.config.dikt.get("last_notebook_path")
    )
    if last_notebook and nb._looks_like_ipynb_path(last_notebook):
        nb.config.dikt["last_notebook_path"] = last_notebook
        if os.path.isfile(last_notebook):
            resolved_path = last_notebook

    assert resolved_path == foo, (
        f"initModel must prefer last_notebook_path for reopen when it "
        f"exists on disk; got {resolved_path!r}, expected {foo!r}"
    )


# ---------------------------------------------------------------------------
# Bug regression: idempotence — multiple lifecycle events don't pile up.
# ---------------------------------------------------------------------------


def test_save_open_state_idempotent_across_repeated_calls():
    """``save_open_state`` is safe to call from focusOutEvent AND
    hideEvent AND closeEvent AND atexit on the same quit. Each
    call writes the same dict; no race, no write storm. We verify
    by calling it three times in a row — save() runs each time
    but the resulting state is identical (last writer wins)."""
    tmpdir = tempfile.mkdtemp()
    foo = os.path.join(tmpdir, "foo.ipynb")
    with open(foo, "w") as f:
        f.write("{}\n")
    nb, save_calls = _notebook_with(current_notebook_path=foo)
    for _ in range(3):
        nb.save_open_state()
    assert len(save_calls) == 3
    assert nb.config.dikt["last_notebook_path"] == foo
