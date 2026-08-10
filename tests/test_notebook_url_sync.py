"""T-NEW-062 — Tests for Jupyter-side notebook URL sync.

The T-NEW-057 review doc + user testing report flagged:
"NotebookNotebook doesn't remember and restore when a notebook
has been opened in that tab previously ... we need a hook to
opening via double click of the file, right click open, and
file open within the notebook filebrowser itself".

The "filebrowser" referenced here is Jupyter's own filebrowser
(the ``/tree`` page served by the Jupyter server) — Nchantd
hosts Jupyter inside a QWebEngineView and the user navigates by
clicking files in the Jupyter UI. The Nchantd widget needs to
observe the webview's URL changes and update its own
``self.file_path`` + URL dropdown + ``last_notebook_path``
persisted state.

This file pins 5 invariants the T-NEW-062 implementation
promises:

  1. ``test_sync_parses_notebook_url`` — given a Jupyter
     ``/notebooks/foo.ipynb`` URL, the helper sets
     ``file_path`` to the resolved path.

  2. ``test_sync_ignores_tree_url`` — given a Jupyter
     ``/tree`` URL, the helper is a no-op (doesn't change
     ``file_path``).

  3. ``test_sync_persists_last_notebook_path`` — the helper
     writes ``config.dikt["last_notebook_path"]`` so the next
     app launch can reopen the user's notebook.

  4. ``test_sync_resolves_against_cwd`` — the helper resolves
     the bare filename in the URL against
     ``dirname(self.file_path)`` (the Jupyter cwd), not the
     process cwd.

  5. ``test_sync_handles_url_with_query_string`` — URLs with
     ``?token=...`` query strings are stripped correctly
     before the filename is extracted.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))


def _make_notebook_lite(tmpdir):
    """Build a notebook-widget-like object with just the
    attributes ``_sync_notebook_from_url`` reads/writes.

    We don't import ``NchantdOfficeNotebook`` because that
    requires Qt + the full NchantdCloak singleton. Instead we
    bind the method to a plain object — same pattern as
    test_update_checker_boot_hook.py.
    """
    from nchantdoffice.widgets.documents.workbooks.notebooks import (
        NchantdOfficeNotebook,
    )

    # Use a plain object so Pyright doesn't complain about
    # missing attributes — we set them all below.
    lite = type("_Lite", (), {})()
    lite.file_path = None
    lite.current_notebook_path = None
    lite.server_url = "http://localhost:8888"
    # config.dikt where last_notebook_path is persisted.
    lite.config = MagicMock()
    lite.config.dikt = {}
    # url_select_entry is None in tests so the refresh path is a
    # no-op (we're not exercising Qt widgets here).
    lite.url_select_entry = None
    # Bind the real method.
    lite._sync_notebook_from_url = (
        NchantdOfficeNotebook._sync_notebook_from_url.__get__(lite)
    )
    # get_url_history / get_current_url are also read by the
    # helper — stub them.
    lite.get_url_history = lambda: ["http://localhost:8888"]
    lite.get_current_url = lambda: "http://localhost:8888"
    return lite


def _create_notebook(tmpdir, name="foo.ipynb"):
    """Create an empty .ipynb file inside ``tmpdir`` so the
    resolution path check passes."""
    p = Path(tmpdir) / name
    p.write_text('{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}')
    return str(p)


def test_sync_parses_notebook_url():
    """``/notebooks/foo.ipynb`` URL updates file_path."""
    with tempfile.TemporaryDirectory() as tmp:
        notebook = _create_notebook(tmp, "foo.ipynb")
        lite = _make_notebook_lite(tmp)
        lite.file_path = notebook  # Jupyter cwd is tmp
        lite._sync_notebook_from_url("http://localhost:8888/notebooks/foo.ipynb")
        assert lite.file_path == notebook, (
            f"file_path should be {notebook!r}, got {lite.file_path!r}"
        )
        assert lite.current_notebook_path == notebook
        assert lite.config.dikt.get("last_notebook_path") == notebook


def test_sync_ignores_tree_url():
    """``/tree`` URL is a no-op (filebrowser root)."""
    with tempfile.TemporaryDirectory() as tmp:
        notebook = _create_notebook(tmp, "foo.ipynb")
        lite = _make_notebook_lite(tmp)
        original_file_path = notebook
        lite.file_path = notebook
        lite._sync_notebook_from_url("http://localhost:8888/tree")
        assert lite.file_path == original_file_path, (
            f"file_path should NOT change for /tree; got {lite.file_path!r}"
        )
        assert "last_notebook_path" not in lite.config.dikt, (
            "last_notebook_path should NOT be written for /tree URLs"
        )


def test_sync_persists_last_notebook_path():
    """Helper writes config.dikt['last_notebook_path']."""
    with tempfile.TemporaryDirectory() as tmp:
        notebook = _create_notebook(tmp, "bar.ipynb")
        lite = _make_notebook_lite(tmp)
        lite.file_path = notebook
        lite._sync_notebook_from_url("http://localhost:8888/notebooks/bar.ipynb")
        assert lite.config.dikt.get("last_notebook_path") == notebook, (
            f"last_notebook_path should be {notebook!r}, got "
            f"{lite.config.dikt.get('last_notebook_path')!r}"
        )


def test_sync_resolves_against_cwd():
    """Bare filename resolves against ``dirname(file_path)``,
    not the process cwd."""
    with tempfile.TemporaryDirectory() as tmp_a, tempfile.TemporaryDirectory() as tmp_b:
        # Notebook lives in tmp_b; current file_path points at a
        # different notebook in tmp_a (the Jupyter cwd is tmp_a).
        nb_in_a = _create_notebook(tmp_a, "current.ipynb")
        nb_in_b = _create_notebook(tmp_b, "other.ipynb")
        lite = _make_notebook_lite(tmp_a)
        lite.file_path = nb_in_a
        # When Jupyter navigates to "other.ipynb", we should look
        # in tmp_a (dirname(file_path)), not tmp_b.
        lite._sync_notebook_from_url("http://localhost:8888/notebooks/other.ipynb")
        # Resolution: tmp_a (cwd) + "other.ipynb" → tmp_a/other.ipynb
        # which doesn't exist. The helper should warn and NOT
        # change file_path.
        assert lite.file_path == nb_in_a, (
            f"file_path should NOT change when resolved path doesn't "
            f"exist; got {lite.file_path!r}"
        )
        # Now create the notebook at tmp_a/other.ipynb and try again.
        nb_in_a_other = _create_notebook(tmp_a, "other.ipynb")
        lite._sync_notebook_from_url("http://localhost:8888/notebooks/other.ipynb")
        assert lite.file_path == nb_in_a_other, (
            f"file_path should resolve to {nb_in_a_other!r} (cwd + name), "
            f"got {lite.file_path!r}"
        )


def test_sync_handles_url_with_query_string():
    """URLs with ``?token=...`` strip the query string before
    extracting the filename."""
    with tempfile.TemporaryDirectory() as tmp:
        notebook = _create_notebook(tmp, "foo.ipynb")
        lite = _make_notebook_lite(tmp)
        lite.file_path = notebook
        # Jupyter often appends ``?token=<hash>`` to URLs.
        lite._sync_notebook_from_url(
            "http://localhost:8888/notebooks/foo.ipynb?token=abc123"
        )
        assert lite.file_path == notebook, (
            f"file_path should be {notebook!r} even with query string; "
            f"got {lite.file_path!r}"
        )
        # Also test with a fragment.
        lite._sync_notebook_from_url(
            "http://localhost:8888/notebooks/foo.ipynb#cell-1"
        )
        assert lite.file_path == notebook
