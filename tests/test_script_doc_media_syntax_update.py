"""Sprint 17 — T-NEW-024 reload: doc_media row syntax must be
updated when a file is opened.

User-stated contract (2026-07-29):
  The document.syntax attribute is getting stored as html every time
  when it needs to be stored as the syntax determined from the file
  extension like on file open.

Root cause: ``add_document`` writes ``doc_media.syntax = "html"`` when
a new tab is created (the default for ``add_script_document_*``).
When the user opens a ``.md``/``.py``/``.json`` file via
``cmd_open_local_file`` -> ``open_file`` -> ``_apply_extension_syntax``,
the **in-memory** ``self.document.syntax`` is updated correctly, but
the **doc_media row** in the DB retains the original "html" value.
On reopen, the loaded tab reads syntax="html" from the doc_media
row and the dispatch falls through to ``setPlainText``, dropping
the rich formatting.

The fix:
  1. ``open_file`` (after ``_apply_extension_syntax``) issues an
     UPDATE against the doc_media row whose ``did`` matches the
     current document, setting the syntax column to the detected
     extension syntax.
  2. ``save()`` (the base ``save`` method) issues the same UPDATE
     on every save so the doc_media row stays in sync with the
     in-memory doc.

This test pins both code paths via AST analysis (the nchantrs
circular import blocks importing the actual class).
"""

import ast
import re
from pathlib import Path


def _bare_source():
    """Return the source of documents.py base class."""
    root = Path(__file__).resolve().parent.parent
    return (root / "nchantdoffice/widgets/documents/documents.py").read_text()


def _bare_scripts_source():
    """Return the source of scripts.py."""
    root = Path(__file__).resolve().parent.parent
    return (root / "nchantdoffice/widgets/documents/media/scripts.py").read_text()


def _find_function_source(src, fn_name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn_name:
            return ast.get_source_segment(src, node) or ""
    return ""


def _flattened(src):
    return re.sub(r"\s+", " ", src).strip()


def test_open_file_persists_doc_media_syntax_update():
    """T-NEW-024: when ``open_file`` runs
    ``_apply_extension_syntax``, the doc_media row whose
    ``did`` matches the current document must be UPDATED so
    the saved syntax reflects the file extension (not the
    'html' default written at tab-creation time).
    """
    src = _bare_scripts_source()
    fn_src = _flattened(_find_function_source(src, "open_file"))

    # The open_file must call _apply_extension_syntax (already
    # implemented) AND must trigger a doc_media UPDATE. The
    # cleanest path is to call a helper (e.g.
    # ``_sync_doc_media_syntax``) inside open_file after the
    # extension detection so the DB row stays in sync.
    assert "_apply_extension_syntax" in fn_src, (
        f"open_file must call _apply_extension_syntax; "
        f"body: {fn_src!r}"
    )
    # Pin the new behaviour: open_file must also call a helper
    # that UPDATEs the doc_media row. The helper name is up
    # to the implementer; what matters is that _some_ doc_media
    # update call appears in open_file (or, more flexibly, the
    # extension detector itself writes the row).
    assert (
        "_update_doc_media_syntax" in fn_src
        or "update_doc_media" in fn_src
        or "self.app.model.update_doc_media_syntax" in fn_src
        or "store_doc_media" in fn_src
    ), (
        f"open_file must trigger a doc_media update so the "
        f"saved syntax reflects the file extension; body: {fn_src!r}"
    )


def test_save_persists_doc_media_syntax_update():
    """T-NEW-024: the base ``save()`` method must UPDATE the
    doc_media row so the saved syntax column tracks the
    in-memory doc.syntax. Without this UPDATE, the row
    retains the original 'html' value written at tab-creation
    time and the next reopen reads 'html' from the DB.
    """
    src = _bare_source()
    fn_src = _flattened(_find_function_source(src, "save"))

    # The base save must trigger a doc_media update with the
    # current document.syntax. Look for an explicit UPDATE call
    # or one of the sync helpers.
    assert (
        "_update_doc_media_syntax" in fn_src
        or "update_doc_media_syntax" in fn_src
        or "self.app.model.update_doc_media_syntax" in fn_src
        or "store_doc_media" in fn_src
    ), (
        f"base save() must UPDATE the doc_media row with the "
        f"current document.syntax so the saved syntax column "
        f"tracks the in-memory doc; body: {fn_src!r}"
    )


def test_models_layer_has_update_doc_media_syntax_helper():
    """T-NEW-024: the model layer must expose an
    ``update_doc_media_syntax(did, syntax)`` helper that runs
    ``UPDATE doc_media SET syntax = ? WHERE did = ?``. The
    widget layer calls this helper on file-open and on save.
    """
    src = Path(__file__).resolve().parent.parent
    src = (src / "nchantdoffice/models.py").read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in (
            "update_doc_media_syntax",
            "update_doc_media",
        ):
            body = ast.get_source_segment(src, node) or ""
            # The method must accept syntax and did parameters and
            # generate an UPDATE SQL statement.
            if "syntax" in body and "did" in body and "UPDATE" in body.upper():
                found = True
                break

    assert found, (
        "models.py must expose update_doc_media_syntax(did, syntax) "
        "that runs UPDATE doc_media SET syntax = ? WHERE did = ? "
        "so the file-extension syntax round-trips through the DB."
    )
