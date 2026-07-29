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
    browser.document = SimpleNamespace(
        did="browser-1",
        location="internal",
        content=None,
        file_path=None,
        active_page=SimpleNamespace(to_dict=lambda: profile),
        version=1,
        save=lambda path=None: None,
        set_content=lambda content: setattr(browser.document, "content", content),
        to_dict=lambda: {
            "did": "browser-1",
            "content": browser.document.content or {"content": profile},
            "version": 1,
            "syntax": "json",
            "location": "internal",
        },
    )
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