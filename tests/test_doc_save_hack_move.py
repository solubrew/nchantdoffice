"""T-NEW-039 close-out: hack-move refactor.

The inline TODO at documents.py:618 said:

  # TODO this has to be moved to NchantdOfficeCloakModel this is a hack

After T-NEW-024, ``NchantdOfficeCloakModel.store_document`` already
runs the ``UPDATE doc_media SET syntax_txt = ? WHERE did = ?``
update as part of the canonical save path. The widget's
post-save ``update_doc_media_syntax`` call was redundant -- and
T-NEW-039 removes it, so the model owns the write.

Regression test: tests/test_doc_save_hack_move.py
"""

import inspect


def test_documents_save_no_longer_calls_update_doc_media_syntax():
    """The widget's save() must NOT call update_doc_media_syntax.

    The model (``store_document``) already does the
    ``UPDATE doc_media SET syntax_txt = ?`` call. The widget no
    longer needs to do it. The word may appear in a comment that
    references the migration, but the actual call site must be gone.
    """
    from nchantdoffice.widgets.documents.documents import NchantdOfficeDocumentMixin
    src = inspect.getsource(NchantdOfficeDocumentMixin.save)
    # Strip comments and adjacent docstring text to find ACTUAL calls
    lines_with_call = [
        line for line in src.split("\n")
        if "update_doc_media_syntax" in line and not line.strip().startswith("#")
    ]
    assert not lines_with_call, (
        f"Widget save() must not call update_doc_media_syntax directly. "
        f"Found: {lines_with_call}"
    )


def test_documents_save_no_longer_has_hack_todo():
    """The 'this is a hack' TODO comment must be gone."""
    from nchantdoffice.widgets.documents.documents import NchantdOfficeDocumentMixin
    src = inspect.getsource(NchantdOfficeDocumentMixin.save)
    assert "this is a hack" not in src, (
        "The 'this is a hack' TODO must be resolved (T-NEW-039)"
    )


def test_documents_save_calls_model_store_document():
    """The widget's save() must still call ``self.app.model.store_document``."""
    from nchantdoffice.widgets.documents.documents import NchantdOfficeDocumentMixin
    src = inspect.getsource(NchantdOfficeDocumentMixin.save)
    assert "self.app.model.store_document" in src, (
        "Widget save() must still call model.store_document (T-NEW-039)"
    )


def test_store_document_writes_syntax_in_canonical_path():
    """Source-level: ``store_document`` must run the doc_media syntax update."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    src = inspect.getsource(NchantdOfficeCloakModel.store_document)
    assert "doc_media" in src
    assert "syntax_txt" in src
    assert "records" in src
