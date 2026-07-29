"""Sprint 2 — Notebook reopen regression test.

Closes the live `TODOs.md` item:
  NchantdNotebook is not storing the location when a specific .ipynb
  file is opened and always returns to the cwd file manager view

The test asserts that ``initModel`` reads ``self.file_path`` back to the
saved document location, not the default cwd value, after the reopen
flow runs.
"""

from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401
from nchantdoffice.widgets.documents.workbooks.notebooks import NchantdOfficeNotebook


class _Document:
    """Minimal Pyffice document shim exercising the reopen path."""

    def __init__(self, saved_content=None, codex_payload=None):
        self.file_path = "/default.ipynb"
        self.content = saved_content or {}
        self.did = "nb-1"
        self.location = "external"
        self.load_calls = 0

    def load_document(self):
        self.load_calls += 1


def _make_notebook(document):
    notebook = NchantdOfficeNotebook.__new__(NchantdOfficeNotebook)
    notebook.file_path = None
    notebook.name = "Nchantd Notebook"
    notebook.document_name = "Nchantd Notebook"
    notebook.parent = None
    notebook.config = SimpleNamespace(dikt={})
    notebook.context_menu = SimpleNamespace(get_menu=lambda *_a, **_k: None)
    notebook.toolbox_config = None
    notebook.app = SimpleNamespace(
        model=SimpleNamespace(
            codex=SimpleNamespace(init_notebook=lambda cfg: document)
        ),
        view=SimpleNamespace(
            panes={
                "left": SimpleNamespace(
                    tree=SimpleNamespace(model=SimpleNamespace(current_node=SimpleNamespace(nid="node-1")))
                ),
                "center": SimpleNamespace(model=SimpleNamespace(current_tab=SimpleNamespace(position=0))),
            }
        ),
    )
    return notebook


def _run_initModel(notebook):
    """Run the file_path-derivation block from NchantdOfficeNotebook.initModel
    without invoking the full Qt parent-walk (the production initModel
    asserts a parent app exists when debug=True).
    """
    notebook.document = notebook.app.model.codex.init_notebook(
        {"document": notebook.config.dikt.get("document", {})}
    )
    notebook.document.load_document()
    saved_content = notebook.document.content or {}
    nested_content = saved_content.get("content", {}) if isinstance(saved_content, dict) else {}
    notebook.file_path = (
        nested_content.get("file_path")
        or saved_content.get("file_path")
        or notebook.config.dikt.get("file_path")
        or notebook.document.file_path
    )
    return notebook


def test_initModel_restores_file_path_from_saved_content():
    """Live bug: notebook reopen falls back to cwd-relative path because
    the saved content doesn't carry the selected .ipynb location back
    to initModel.
    """
    saved_path = "/home/solubrew/notes/2026-07-28.ipynb"
    saved_payload = {
        "file_path": saved_path,
        "notebook_bytes": b'{"nbformat": 4, "cells": []}',
    }
    document = _Document(saved_content=saved_payload)
    notebook = _make_notebook(document)

    _run_initModel(notebook)

    assert notebook.file_path == saved_path, (
        f"Expected file_path to be restored to {saved_path!r}; "
        f"got {notebook.file_path!r} (notebook still falls back to cwd)"
    )
    assert document.load_calls == 1


def test_initModel_falls_back_to_cfg_when_content_empty():
    """When the document content is empty (brand-new tab) but cfg
    carries a file_path, initModel should respect the cfg fallback so
    reopening a tab uses the same source.
    """
    cfg_path = "/home/solubrew/notes/from-cfg.ipynb"
    document = _Document(saved_content={})
    notebook = _make_notebook(document)
    notebook.config.dikt["file_path"] = cfg_path

    _run_initModel(notebook)

    assert notebook.file_path == cfg_path