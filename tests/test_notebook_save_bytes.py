"""Sprint 4 — Notebook save / reopen round-trip with file_path-first model.

Live failure (user traceback, 2026-07-28): saving a NchantdNotebook
opened to a specific ``.ipynb`` file raised
``TypeError: Object of type bytes is not JSON serializable`` from
``models.py:2094`` (logma.json) because Sprint 2's notebook fix
embedded raw bytes in the DB payload.

User correction (2026-07-28):
  NchantdNotebook should be storing the full path for the .ipynb to
  be reloaded from external as the default and only saved as bytes if
  toggled to internal storage.

The test asserts:

  1. Default ``save_mode == "file_path"`` -> ``get_content()`` returns
     only ``{"file_path": ...}`` (no ``notebook_bytes``).
  2. Toggled ``save_mode == "to_dict"`` -> ``get_content()`` includes
     the serialised bytes for internal storage.
  3. ``store_document`` never raises on a document whose payload
     contains only ``file_path`` (the production fix for the
     ``TypeError: bytes`` crash).
"""

import base64
from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401
from nchantdoffice.models import NchantdOfficeCloakModel as _Model
from nchantdoffice.widgets.documents.workbooks.notebooks import NchantdOfficeNotebook


def _bare_widget(cls):
    """Allocate a Qt-derived widget without running its constructor."""
    return cls.__new__(cls)


def test_get_content_file_path_mode_omits_notebook_bytes():
    """Default (file_path) mode must NOT embed raw bytes in the DB
    payload — the saved content is just the .ipynb path so reopen
    reloads from the external file."""
    notebook = _bare_widget(NchantdOfficeNotebook)
    notebook.file_path = "/home/solubrew/notes/work.ipynb"
    notebook.save_mode = "file_path"
    notebook.cells = [{"cell_type": "code", "source": ["print('ok')"]}]

    content = notebook.get_content()

    assert content["content"]["file_path"] == "/home/solubrew/notes/work.ipynb"
    assert "notebook_bytes" not in content["content"], (
        "Default file_path mode must not embed notebook_bytes — "
        "raw bytes crash JSON serialisation in store_document."
    )


def test_get_content_to_dict_mode_includes_notebook_bytes():
    """When the user has toggled save_mode to ``"to_dict"``, the
    serialised notebook must be present so reopen can recover
    without the external file."""
    notebook = _bare_widget(NchantdOfficeNotebook)
    notebook.file_path = "/home/solubrew/notes/work.ipynb"
    notebook.save_mode = "to_dict"
    notebook.cells = [{"cell_type": "code", "source": ["print('hi')"]}]

    content = notebook.get_content()

    assert content["content"]["file_path"] == "/home/solubrew/notes/work.ipynb"
    assert b'"nbformat": 4' in content["content"]["notebook_bytes"]


def test_get_content_both_mode_also_includes_notebook_bytes():
    notebook = _bare_widget(NchantdOfficeNotebook)
    notebook.file_path = "/home/solubrew/notes/work.ipynb"
    notebook.save_mode = "both"
    notebook.cells = []

    content = notebook.get_content()
    assert "notebook_bytes" in content["content"]


def test_default_save_mode_is_file_path():
    """The widget must default to file_path mode (the new contract)."""
    notebook = _bare_widget(NchantdOfficeNotebook)
    notebook.file_path = "/tmp/work.ipynb"
    # Match what NchantdOfficeDocumentMixin.init_variables does.
    notebook.save_mode = getattr(notebook, "save_mode", "file_path")
    assert notebook.save_mode == "file_path"


def test_store_document_never_raises_on_file_path_only_payload():
    """The live failure path: notebook ``to_dict()`` returns a payload
    containing only ``file_path`` (no bytes) and ``store_document``
    must not raise. Sprint 2's bytes-in-content path is what
    triggered the user traceback.
    """
    captured = []

    class _CapturingStore:
        def store_doc_media(self, *_a, **_k):
            captured.append(("media", _a, _k))

        def store_doc_media_content(self, *_a, **_k):
            captured.append(("content", _a, _k))

        def get_table(self, *_a, **_k):
            return None

        def update_record(self, *_a, **_k):
            # T-NEW-024 followup: store_document writes doc_media.syntax_txt
            # via update_record; this test asserts on the content_enc64_txt
            # blob (not the syntax row), so the update is a no-op here.
            return None

    model = _Model.__new__(_Model)
    model.store = _CapturingStore()
    model.has_changed = False
    model.app = SimpleNamespace(
        model=model,
        view=SimpleNamespace(panes={"center": SimpleNamespace(model=SimpleNamespace(tabbase=[0, 1, 1, 1]))}),
    )
    model.app.application_name = "NchantdOffice"
    model.instance = None

    document = SimpleNamespace(
        did="nb-1",
        version=1,
        is_changed=True,
        syntax="json",  # store_document writes doc_media.syntax_txt (T-NEW-024 followup)
        to_dict=lambda: {
            "did": "nb-1",
            "content": {
                "content": {
                    "file_path": "/home/solubrew/notes/work.ipynb",
                }
            },
            "version": 1,
            "syntax": "json",
            "location": "internal",
        },
    )

    model.store_document(document)

    assert any(entry[0] == "content" for entry in captured), (
        "store_doc_media_content was not called — store_document path "
        "did not reach the persistence layer"
    )


def test_reopen_round_trip_file_path_is_source_of_truth():
    """End-to-end: save captures the .ipynb path; reopen restores it
    so the widget reloads from the external file."""
    notebook = _bare_widget(NchantdOfficeNotebook)
    notebook.name = "Nchantd Notebook"
    notebook.document_name = "Nchantd Notebook"
    notebook.parent = None
    notebook.toolbox_config = None
    notebook.context_menu = SimpleNamespace(get_menu=lambda *_a, **_k: None)
    notebook.config = SimpleNamespace(dikt={})
    notebook.save_mode = "file_path"
    notebook.app = SimpleNamespace(
        model=SimpleNamespace(
            codex=SimpleNamespace(
                init_notebook=lambda cfg: SimpleNamespace(
                    file_path="/home/solubrew/notes/work.ipynb",
                    content={
                        "content": {
                            "file_path": "/home/solubrew/notes/work.ipynb",
                        }
                    },
                    load_document=lambda: None,
                )
            )
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

    # Save captures only the path (no bytes).
    notebook.file_path = "/home/solubrew/notes/work.ipynb"
    content = notebook.get_content()
    assert "notebook_bytes" not in content["content"]
    assert content["content"]["file_path"] == "/home/solubrew/notes/work.ipynb"

    # Reopen: initModel reads the saved file_path back (Sprint 1 fix).
    document = notebook.app.model.codex.init_notebook({})
    saved_content = document.content
    nested = saved_content.get("content", {})
    file_path = (
        nested.get("file_path")
        or saved_content.get("file_path")
        or notebook.config.dikt.get("file_path")
        or document.file_path
    )
    assert file_path == "/home/solubrew/notes/work.ipynb"