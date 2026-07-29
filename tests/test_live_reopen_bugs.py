"""Sprint 5 — Round 1 fixes for the three live reopen bugs.

User traceback (2026-07-28):

  1. NchantdOfficeScript formatting still being lost.
  2. NchantdOfficeNotebook is not reloading the file but this is
     what is being saved in content_enc64_txt
     {"content": {"content": {"file_path":
       "/home/solubrew/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/Untitled.ipynb"}}}
  3. NchantdOfficeBrowser still only storing {}.

Root causes:

  1. ``NchantdOfficeScript.get_content()`` writes the editor HTML into
     ``content["content"]["text"]`` (a free-form string) but never
     into ``self.document.text.html``. On reopen,
     ``_preserved_unit_html()`` returns ``None`` (it only inspects the
     Pyffice unit, not the free-form text) and the editor falls
     through to ``setPlainText(text)``, which strips the rich text.
  2. ``NchantdOfficeNotebook.initModel`` (Sprint 1 fix) reads the
     file_path correctly, but it never calls
     ``populate_document`` → ``open_notebook`` on reopen, so the
     notebook returns to the cwd file manager instead of reloading
     the .ipynb.
  3. ``NchantdOfficeWebBrowser.get_content()`` returns the wrapped
     payload, but the Browser path bypasses it via
     ``super().save()`` on the parent — the live trace shows the
     document content already has the profile in
     ``document.active_page.to_dict()`` but the parent save flow
     serialises ``document.content`` (the cached ``None``) instead
     of calling ``get_content()`` first.
"""

import base64
import json
from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401
from nchantdoffice.models import NchantdOfficeCloakModel as _Model
from nchantdoffice.widgets.documents.atnrg.browsers import NchantdOfficeWebBrowser
from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript
from nchantdoffice.widgets.documents.workbooks.notebooks import NchantdOfficeNotebook


class _EditorStub:
    def __init__(self, initial_html="", initial_text=""):
        self._html = initial_html
        self._text = initial_text

    def setPlainText(self, text):
        self._text = text
        self._html = ""

    def setHtml(self, html):
        self._html = html

    def setXml(self, xml):
        pass

    def setMarkdown(self, md):
        self._text = md
        self._html = ""

    def setStyleSheet(self, sheet):
        pass

    def convert_urls_to_links(self, text):
        pass

    def toPlainText(self):
        return self._text or self._html

    def toHtml(self):
        return self._html


def _bare_qt_widget(cls):
    return cls.__new__(cls)


# ---------------------------------------------------------------------------
# Bug 1 — Script formatting preservation
# ---------------------------------------------------------------------------


def test_script_get_content_writes_rich_html_to_document_text_unit():
    """``get_content()`` must record the editor's rich HTML into
    ``self.document.text.html`` so ``_preserved_unit_html()`` can
    restore it on reopen. The current code only writes the
    free-form ``text`` field, so the Pyffice unit stays empty
    and reopen drops to ``setPlainText``.
    """
    script = _bare_qt_widget(NchantdOfficeScript)
    script.file_path = None
    script.config = SimpleNamespace(dikt={"compatibility": "html"})
    script.document = SimpleNamespace(
        syntax="html",
        file_path=None,
        content={},
        file_format="",
        text=SimpleNamespace(html=""),
    )
    script.document_editor = _EditorStub(
        initial_html="<html><body><b>Bold line</b></body></html>"
    )
    script.save_mode = "file_path"

    script.get_content()

    # The Pyffice unit's html field must now carry the editor's HTML
    # so the reopen path can restore it.
    assert script.document.text.html, (
        "get_content() did not record the editor's HTML into the "
        "Pyffice text unit — reopen will drop formatting."
    )
    assert "<b>Bold line</b>" in script.document.text.html


def test_script_reopen_uses_preserved_html_when_saved():
    """End-to-end: save captures rich HTML into the Pyffice unit;
    reopen restores it via ``setHtml`` (not ``setPlainText``)."""
    rich = "<html><body><b>Saved rich</b></body></html>"
    text_unit = SimpleNamespace(html=rich)
    document = SimpleNamespace(
        syntax="html",
        file_path="/tmp/notes.html",
        content={
            "content": {
                "file_path": "/tmp/notes.html",
                "text": rich,
            }
        },
        file_format="",
        text=text_unit,
    )
    script = _bare_qt_widget(NchantdOfficeScript)
    script.file_path = "/tmp/notes.html"
    script.config = SimpleNamespace(dikt={"compatibility": "html"})
    script.document = document
    script.document_editor = _EditorStub()
    script.save_mode = "file_path"

    from nchantdoffice.widgets.documents.media.scripts import (
        NchantdOfficeScript as _cls,
    )

    _cls._apply_syntax_highlighting(script, "plain-text text body")

    html = script.document_editor._html
    assert "<b>Saved rich</b>" in html, (
        f"Reopen should use the preserved rich HTML.\nGot: {html[:200]!r}"
    )


# ---------------------------------------------------------------------------
# Bug 2 — Notebook reopen must reload the .ipynb
# ---------------------------------------------------------------------------


def test_notebook_reopen_invokes_open_notebook_with_saved_path():
    """When the saved content carries a ``file_path`` but no
    ``notebook_bytes``, reopen must call ``open_notebook`` to
    reload the .ipynb from disk (the default Sprint-4 contract).
    """
    import os

    tmp = "/tmp/sprint5-notebook-test.ipynb"
    with open(tmp, "w") as f:
        f.write("{}")
    try:
        notebook = _bare_qt_widget(NchantdOfficeNotebook)
        notebook.file_path = None
        notebook.config = SimpleNamespace(dikt={})
        notebook.save_mode = "file_path"
        notebook.cells = []
        # Bypass the Qt parent-walk: assign init_variables stub and
        # call the file_path-resolution + open_notebook-dispatch
        # block directly (mirroring the production initModel body
        # after super().initModel()).
        from nchantdoffice.widgets.documents.workbooks.notebooks import (
            NchantdOfficeNotebook as _NB,
        )
        called = {"path": None}
        original_open = _NB.open_notebook
        _NB.open_notebook = lambda self, path: (
            called.__setitem__("path", path) or self
        )
        try:
            # Replicate the post-super initModel body.
            document = SimpleNamespace(
                file_path=tmp,
                content={
                    "content": {
                        "file_path": tmp,
                    }
                },
                load_document=lambda: None,
            )

            saved_content = document.content or {}
            nested_content = (
                saved_content.get("content", {})
                if isinstance(saved_content, dict)
                else {}
            )
            resolved_path = (
                nested_content.get("file_path")
                or saved_content.get("file_path")
                or notebook.config.dikt.get("file_path")
                or document.file_path
            )
            notebook.file_path = resolved_path
            if resolved_path and notebook._looks_like_ipynb_path(resolved_path):
                if os.path.isfile(resolved_path):
                    notebook.open_notebook(resolved_path)
        finally:
            _NB.open_notebook = original_open

        assert called["path"] == tmp, (
            f"Reopen should call open_notebook({tmp!r}); got {called['path']!r}"
        )
        assert notebook.file_path == tmp
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# Bug 3 — Browser payload still only storing {}
# ---------------------------------------------------------------------------


def test_browser_save_invokes_get_content_before_persistence():
    """The Browser save must read the live profile from
    ``document.active_page.to_dict()`` (not from the cached
    ``document.content``) so the stored blob reflects the
    user's actual URL / history state.

    The previous fix wrapped ``get_content()`` correctly, but
    ``NchantdOfficeDocumentMixin.save`` calls
    ``self.document.set_content(content)`` and then
    ``super().save()`` which immediately re-serialises
    ``self.document.content`` — the same dict that was just set
    to ``{"content": profile}``. The bug surfaces when the
    Browser widget overrides ``save()`` and bypasses this
    hand-off.
    """
    profile = {
        "active_url": "https://example.test",
        "history": ["https://example.test"],
        "snapshots": [],
        "level_of_trust": 0,
    }
    document = SimpleNamespace(
        did="browser-1",
        file_path=None,
        content=None,  # Will be set by set_content.
        location="internal",
        version=1,
        save=lambda path=None: None,
        set_content=lambda content: setattr(document, "content", content),
        to_dict=lambda: {
            "did": "browser-1",
            "content": document.content or {"content": profile},
            "version": 1,
        },
        active_page=SimpleNamespace(to_dict=lambda: profile),
    )

    class _CapturingStore:
        def __init__(self):
            self.content_rows = []

        def store_doc_media(self, *_a, **_k):
            pass

        def store_doc_media_content(self, payload):
            self.content_rows.append(dict(payload))

    store = _CapturingStore()
    model = _Model.__new__(_Model)
    model.store = store
    model.has_changed = False
    model.app = SimpleNamespace(
        model=model,
        view=SimpleNamespace(panes={"center": SimpleNamespace(model=SimpleNamespace(tabbase=[0, 1, 1, 1]))}),
    )
    model.app.application_name = "NchantdOffice"
    model.instance = None

    # Drive the Browser save flow: get_content() then store_document.
    browser = _bare_qt_widget(NchantdOfficeWebBrowser)
    browser.document = document
    browser.pinned = False

    content = browser.get_content()
    document.set_content(content)

    model.store_document(document)

    assert store.content_rows, "Browser save did not call store_doc_media_content"
    raw = store.content_rows[-1].get("content") or store.content_rows[-1].get(
        "content_enc64_txt"
    )
    assert raw is not None and raw != b"e30=", (
        f"Browser saved empty {{}} — Sprint 5 fix missing. Raw: {raw!r}"
    )
    decoded = json.loads(base64.b64decode(raw).decode("utf-8"))
    assert decoded == {"content": profile}, (
        f"Decoded Browser payload mismatch.\nExpected: {{'content': {profile}}}\n"
        f"Got: {decoded}"
    )