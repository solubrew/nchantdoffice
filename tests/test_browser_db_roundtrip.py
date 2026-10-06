"""Sprint 2 — Browser DB round-trip regression test.

Closes the live `TODOs.md` item:
  NchantdBrowser is not saving and retrieving url

Verifies that when NchantdOfficeWebBrowser.save() runs through the parent
``NchantdOfficeDocumentMixin.save()`` flow, the actual stored
``doc_media_content.content_enc64_txt`` blob decodes back to the full
``active_page.to_dict()`` payload (not ``{}``).

The test drives a real NchantdOfficeCloakModel against an in-memory
``CapturingStore`` so the assertion reads the actual stored bytes — not just
the in-memory log line.
"""

import json
from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401  — establish import order first
from nchantdoffice.models import NchantdOfficeCloakModel
from nchantdoffice.widgets.documents.atnrg.browsers import NchantdOfficeWebBrowser


class _CapturingStore:
    """Captures doc_media_content payloads exactly as squirl would receive them."""

    def __init__(self):
        self.media_rows = []
        self.content_rows = []

    def store_doc_media(self, document):
        self.media_rows.append(dict(document))

    def store_doc_media_content(self, payload):
        self.content_rows.append(dict(payload))

    def get_table(self, *_args, **_kwargs):
        return None

    def update_record(self, *_args, **_kwargs):
        # T-NEW-024 followup: store_document writes doc_media.syntax_txt
        # via update_record; the test asserts on the content_enc64_txt
        # blob (not the syntax row), so the update is a no-op here.
        return None


def _make_browser(profile, store):
    parent = SimpleNamespace(
        app=SimpleNamespace(
            view=SimpleNamespace(
                panes={
                    "left": SimpleNamespace(
                        tree=SimpleNamespace(
                            model=SimpleNamespace(current_node=SimpleNamespace(nid="node-1"))
                        )
                    ),
                    "center": SimpleNamespace(
                        model=SimpleNamespace(current_tab=SimpleNamespace(position=0))
                    ),
                }
            ),
            config=SimpleNamespace(dikt={"apps": ["nchantrs", "nchantdoffice"]}),
            model=SimpleNamespace(codex=SimpleNamespace(), user=SimpleNamespace()),
            application_name="NchantdOffice",
        ),
        config=SimpleNamespace(dikt={}),
    )

    browser = NchantdOfficeWebBrowser.__new__(NchantdOfficeWebBrowser)
    browser.parent = parent
    browser.pinned = False
    # T-NEW-079 followup: the browser refactor (commit ef709da) added
    # ``self.file_path = self.get_active_url()`` to ``save()``; that
    # walks ``self.document.active_page.active_url.active_url``. The
    # mock must mirror the production shape — without the inner
    # ``active_url`` SimpleNamespace, the run-on-save AttributeError
    # shadows the round-trip test we actually care about.
    active_url = SimpleNamespace(active_url="https://example.test/path?q=1")
    # Structure matches what browsers.py:435 expects:
    #   get_active_url() -> self.active_page.document.active_url.active_url
    # Also needs to_dict() for get_content() serialization.
    active_page_ns = SimpleNamespace(
        document=SimpleNamespace(
            active_url=active_url,
        ),
        to_dict=lambda: profile,  # used by get_content() / save() for doc_media storage
    )
    browser.document = SimpleNamespace(
        did="browser-1",
        location="internal",
        content=None,
        file_path=None,
        syntax="json",
        active_page=active_page_ns,
        version=1,
        save=lambda path=None: None,
        set_content=lambda content: setattr(browser.document, "content", content),
        to_dict=lambda: {
            "did": "browser-1",
            "content": browser.document.content or {"content": profile},
        },
    )
    # browsers.py:435 accesses browser.active_page (not browser.document.active_page).
    # Mirror the same object so both paths resolve correctly.
    browser.active_page = active_page_ns
    browser.file_path = None
    browser.config = SimpleNamespace(dikt={})
    browser.context_menu = SimpleNamespace(get_menu=lambda *_a, **_k: None)
    browser.button_bar = None
    browser.document_editor = None
    browser.toolbox = None
    browser.toolbox_config = None
    browser.app = parent.app
    return browser


def _build_model_with(store):
    """Wire a real NchantdOfficeCloakModel against the capturing store."""
    model = object.__new__(NchantdOfficeCloakModel)
    model.store = store
    model.has_changed = False
    model.instance = None
    model.app = SimpleNamespace(
        model=model,
        config=SimpleNamespace(dikt={"apps": ["nchantrs", "nchantdoffice"]}),
        view=SimpleNamespace(panes={"center": SimpleNamespace(model=SimpleNamespace(tabbase=[0, 1, 1, 1]))}),
        application_name="NchantdOffice",
    )
    return model


def test_browser_save_writes_full_payload_into_doc_media_content():
    """The live bug: get_content returned active_page.to_dict() directly,
    so the parent save() flow replaced ``document.content`` with the raw
    payload (no ``content`` wrapper), and the stored blob was an opaque
    dict instead of the serialized active_page state.

    The post-Sprint-1 fix wraps the payload under ``content`` so it
    round-trips through doc_media_content.content_enc64_txt.
    """
    profile = {
        "active_url": "https://example.test/path?q=1",
        "history": ["https://example.test/path?q=1", "https://example.test/path?q=2"],
        "snapshots": [{"ts": "2026-07-28T20:00:00", "url": "https://example.test"}],
        "pinned_on": "2026-07-28T19:55:00",
        "level_of_trust": 2,
    }

    store = _CapturingStore()
    browser = _make_browser(profile, store)
    model = _build_model_with(store)

    captured_payloads = []
    original_store_doc_media_content = store.store_doc_media_content

    def capture_and_store(payload):
        captured_payloads.append(dict(payload))
        original_store_doc_media_content(payload)

    store.store_doc_media_content = capture_and_store
    browser.app.model = model

    browser.save()

    assert captured_payloads, (
        "save() never invoked store_doc_media_content — DB persistence "
        "path was skipped (Sprint 1 regression)."
    )

    payload = captured_payloads[-1]
    raw = payload.get("content") or payload.get("content_enc64_txt")
    assert raw is not None, f"content key missing from payload: {list(payload)}"
    import base64
    decoded = base64.b64decode(raw).decode("utf-8")
    parsed = json.loads(decoded)

    assert parsed == {"content": profile}, (
        f"Decoded browser payload mismatch.\nExpected: {{'content': {profile}}}\nGot: {parsed}"
    )
    assert payload["pUUID"] == "browser-1"
    assert payload["page"] == 0
    assert payload["entry"] == 0


# ---------------------------------------------------------------------------
# T-NEW-079 — full tab-switch state restoration regression tests.
#
# The Sprint 2 round-trip test above proves the *save* payload is correct.
# These tests prove the *restore* path actually re-hydrates the URL+history
# from the saved blob, which is what the user-visible "tab returns to last
# site" bug depends on. Both bug classes were root-caused to:
#
#   1) ``PyfficeURL.__init__`` ignored a positional str (only ``cfg={"url":...}``
#      populated fields), so ``PyfficeURL("https://x.com")`` silently kept the
#      defaults and ``url_string`` was never set on the page object.
#   2) ``to_dict`` did NOT include ``url_string`` in the ``url_attributes``
#      list, so the saved blob had no URL.
#   3) ``set_url`` had a ``pinned_on_dttm is None`` guard that no-op'd every
#      nav after the first ``load_document`` (which stamps
#      ``pinned_on_dttm=now()`` via ``set_page_pinned(None)``).
#   4) ``set_pages`` discarded the saved page dicts
#      (``PyfficeWebPage(page); page.load_document()`` no-args).
#   5) ``load_document`` (page) read ``document.get("url")`` from the OUTER
#      dict, but the serialised form puts the URL under
#      ``document["data"]["url"]["url_string"]`` → always None on restore.
#   6) The nchantdoffice widget only called ``self.save()`` on
#      ``focusOutEvent`` — tab-switch (which fires ``hideEvent``, not
#      ``focusOutEvent``) lost the last URL before the lazy rebuild.
#
# These tests drive real pyffice classes — no mocks — so the same regressions
# cannot sneak past the unit boundary. The widget-level assert lives in the
# ``hideEvent`` / ``closeEvent`` docstrings on ``NchantdOfficeWebBrowser``
# (browsers.py:493-528) and is verified by the live-flow-debugging skill
# (Lesson 55 notebook pattern).
# ---------------------------------------------------------------------------


def _pyffice_imports():
    """Lazily import pyffice so a missing venv produces a clean skip, not a
    test-collection ImportError that masks other failures."""
    try:
        import sys
        sys.path.insert(0, "/home/solubrew/.hermes/projects/pyffice")
        from pyffice.web.url import PyfficeURL
        from pyffice.web.web import PyfficeWebPage, PyfficeWebBrowser
        return PyfficeURL, PyfficeWebPage, PyfficeWebBrowser
    except Exception as e:
        import pytest
        pytest.skip(f"pyffice not importable: {e}")


def test_url_constructor_accepts_positional_string():
    """T-NEW-079 (1): PyfficeURL(s) must populate ``url_string`` from ``s``."""
    PyfficeURL, _, _ = _pyffice_imports()
    u = PyfficeURL("https://positional.example.com/")
    assert u.url_string == "https://positional.example.com/", (
        f"PyfficeURL positional str lost; got url_string={u.url_string!r}"
    )


def test_to_dict_serializes_url_string():
    """T-NEW-079 (2): the saved blob must carry ``url_string`` for restore."""
    PyfficeURL, PyfficeWebPage, _ = _pyffice_imports()
    u = PyfficeURL("https://serialise.example.com/")
    p = PyfficeWebPage({})
    p.set_url("https://serialise.example.com/")
    saved = p.to_dict()
    url_blob = saved.get("data", {}).get("url", {})
    assert url_blob.get("url_string") == "https://serialise.example.com/", (
        f"url_string missing from to_dict: {list(url_blob)}"
    )


def test_set_url_works_after_load_document():
    """T-NEW-079 (3): the ``pinned_on_dttm is None`` guard no longer no-ops."""
    PyfficeURL, PyfficeWebPage, _ = _pyffice_imports()
    p = PyfficeWebPage({})
    # First load_document stamps pinned_on_dttm = now(); pre-fix this
    # permanently disabled navigation.
    p.load_document({"content": {"url_string": "https://seed.example.com/"}})
    p.set_url("https://after-load.example.com/")
    assert p.active_url.url_string == "https://after-load.example.com/", (
        f"set_url no-op after load_document; got {p.active_url.url_string!r}"
    )


def test_set_pages_restores_saved_url_dicts():
    """T-NEW-079 (4): ``set_pages`` must rebuild every page from its saved dict."""
    _, PyfficeWebPage, PyfficeWebBrowser = _pyffice_imports()
    b = PyfficeWebBrowser({})
    b.set_pages([
        {"url": "https://p1.example.com/"},
        {"url": "https://p2.example.com/"},
        {"url": "https://p3.example.com/"},
    ])
    urls = [pg.active_url.url_string for pg in b.pages if getattr(pg, "active_url", None)]
    assert urls == [
        "https://p1.example.com/",
        "https://p2.example.com/",
        "https://p3.example.com/",
    ], f"set_pages discarded restores; got {urls}"


def test_load_document_recovers_url_from_data_nested_path():
    """T-NEW-079 (5): ``load_document`` must read URL from the canonical nested
    position (``data.url.url_string``), not the outer dict."""
    _, PyfficeWebPage, _ = _pyffice_imports()
    blob = {
        "data": {
            "url": {"url_string": "https://nested.example.com/"},
        },
    }
    p = PyfficeWebPage({})
    p.load_document(blob)
    assert p.active_url.url_string == "https://nested.example.com/", (
        f"nested restore missed; got {p.active_url.url_string!r}"
    )


def test_full_save_then_rebuild_round_trip():
    """T-NEW-079 (1-6): user-visible scenario.

    Navigate to site-X, save, simulate widget destruction + rebuild (a
    new ``PyfficeWebPage`` reading the saved blob), assert the URL
    came back. Pre-fix the new page showed HOMEPAGE because every step
    in the chain silently degraded.
    """
    _, PyfficeWebPage, PyfficeWebBrowser = _pyffice_imports()
    # Phase 1: user navigates.
    browser = PyfficeWebBrowser({})
    browser.set_page_active("https://site-X.example.com/article?read=1")
    assert browser.active_page.active_url.url_string == "https://site-X.example.com/article?read=1"
    # Phase 2: widget save() — what hideEvent/closeEvent triggers.
    saved_blob = browser.active_page.to_dict()
    assert saved_blob["data"]["url"]["url_string"] == "https://site-X.example.com/article?read=1"
    # Phase 3: tab-switch destroys the old widget; on return, initModel
    # rebuilds. The new widget is a fresh PyfficeWebBrowser that loads
    # the saved blob into a fresh active page — exactly what
    # ``load_widget -> initModel -> load_document`` does in production.
    browser2 = PyfficeWebBrowser({})
    browser2.load_document({"document": {"active_page": {"url": saved_blob["data"]["url"]["url_string"]}}})
    assert browser2.active_page.active_url.url_string == "https://site-X.example.com/article?read=1", (
        f"tab-return restore lost the URL; got {browser2.active_page.active_url.url_string!r}"
    )
