"""T-NEW-148 -- NchantdOfficeScript external save-to-disk.

Phase 1 of the T-NEW-144b umbrella: ``NchantdOfficeScript.save()``
must write the current editor bytes to the existing external file
when ``location == "external"`` and ``file_path`` is set; the
internal ``store_document`` DB path must still run.

Three regression tests:

1. ``test_external_save_writes_editor_bytes_to_disk`` -- a real
   ``.py`` file on disk; after ``script.save()`` the file's bytes
   equal the exact current editor text (leading indent + trailing
   newline preserved). ``store_document`` is still called once.

2. ``test_external_save_writes_markdown_to_disk`` -- a ``.md``
   file. Same expectations. Confirms the writer is syntax-agnostic
   (just raw text bytes for the file's known extension).

3. ``test_internal_save_does_not_touch_disk`` -- when
   ``document.location == "internal"`` and ``file_path`` is None
   (or absent), ``script.save()`` must NEVER create or write any
   external file; ``store_document`` still runs.

These tests drive the production ``save()`` method directly with
real ``tempfile`` paths -- no log assertions, no fake ``file_path``
strings: the bytes on disk are the assertion target.

The tests construct the script with ``NchantdOfficeScript.__new__``
and wire a tiny stub ``document_editor`` so we never touch real Qt
editors -- the production ``get_content()`` only needs
``toPlainText()``/``toHtml()`` which the stub provides.
"""

from __future__ import annotations

import os
import tempfile
from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401
from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript


class _EditorStub:
    """Minimal stand-in for a Qt editor widget.

    Mirrors the API the production ``get_content()`` actually
    calls (``toHtml()`` / ``toPlainText()``). For the
    T-NEW-148 path only ``toPlainText()`` matters -- the test
    uses a ``plaintext`` syntax so ``get_content`` reads
    ``toPlainText()``.
    """

    def __init__(self, text: str) -> None:
        self._text = text

    def toPlainText(self) -> str:
        return self._text

    def toHtml(self) -> str:
        return self._text


class _StoreSpy:
    """Records ``store_document`` calls so the test can assert
    the DB path still fires on save (regression guard for
    T-NEW-003 / the ``super().save()`` chain)."""

    def __init__(self) -> None:
        self.calls = []

    def store_document(self, document, *args, **kwargs) -> None:
        self.calls.append((document, args, kwargs))


class _DocumentStub:
    """Pyffice document stand-in.

    The production base ``NchantdOfficeDocument.save()`` calls
    ``self.document.set_content(...)`` and
    ``self.document.save(self.file_path)``. We expose both as
    no-ops (the DB row write happens in ``store_document``,
    which the spy captures). ``content_original`` is read by
    ``PyfficeDocument.set_content`` so we give it a default.
    """

    def __init__(self, *, file_path: str, location: str, content_text: str) -> None:
        self.syntax = "plaintext"
        self.file_path = file_path
        self.location = location
        self.content = {"content": {"file_path": file_path}, "text": content_text}
        self.file_format = "plaintext"
        self.text = SimpleNamespace(html="")
        self.content_original = None
        self.did = "test-did"
        self._save_calls = []

    def set_content(self, content):
        self.content = content
        return self

    def save(self, path=None, *args, **kwargs):
        self._save_calls.append(path)
        return self

    def add_change(self, *args, **kwargs):
        return None


def _make_script(*, editor_text: str, file_path: str, location: str) -> tuple[NchantdOfficeScript, _StoreSpy]:
    """Construct a script instance without running ``__init__``.

    Bypasses Qt widget construction entirely. The stub provides
    exactly the attributes/methods the production ``save()`` chain
    (script.save -> super().save -> documents.save -> document.save)
    touches.
    """
    store = _StoreSpy()
    script = NchantdOfficeScript.__new__(NchantdOfficeScript)
    script.file_path = file_path
    script.config = SimpleNamespace(dikt={"compatibility": "plaintext"})
    # ``app.model.store_document`` is the spy.
    # ``app.view.panes[...]`` is read by the base mixin -- we
    # give a non-None tree/tab so the production short-circuit
    # guards (lines 642/646 of documents.py) don't trip.
    tree_model = SimpleNamespace(
        current_node=SimpleNamespace(nid=1),
    )
    center_model = SimpleNamespace(current_tab=SimpleNamespace(position=0))
    script.app = SimpleNamespace(
        model=store,
        view=SimpleNamespace(panes={
            "left": SimpleNamespace(tree=SimpleNamespace(model=tree_model)),
            "center": SimpleNamespace(model=center_model),
        }),
    )
    script.document = _DocumentStub(
        file_path=file_path,
        location=location,
        content_text=editor_text,
    )
    script.document_editor = _EditorStub(editor_text)
    return script, store


def test_external_save_writes_editor_bytes_to_disk():
    """External .py file -- bytes on disk equal the exact editor text.

    The text deliberately includes leading indentation and a
    trailing newline; both must survive. ``store_document`` must
    still be invoked exactly once (the DB path is unchanged).
    """
    editor_text = "    def hello():\n        return 1\n"
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "hello.py")
        # Seed the file with old content to prove the writer
        # overwrites it -- not just touches mtime.
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("OLD CONTENT THAT MUST BE REPLACED\n")
        script, store = _make_script(
            editor_text=editor_text, file_path=file_path, location="external"
        )

        script.save()

        with open(file_path, "rb") as f:
            on_disk = f.read()
        assert on_disk == editor_text.encode("utf-8"), (
            f"External file bytes do not match editor text.\n"
            f"Expected: {editor_text!r}\nGot:      {on_disk.decode('utf-8', 'replace')!r}"
        )
        # Internal DB write still fires.
        assert len(store.calls) == 1, (
            f"store_document must still run on external save; got {len(store.calls)} calls"
        )


def test_external_save_writes_markdown_to_disk():
    """External .md file -- same byte-for-byte contract."""
    md = "# Title\n\n- bullet one\n- bullet two\n\n    indented code\n"
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "notes.md")
        script, store = _make_script(editor_text=md, file_path=file_path, location="external")

        script.save()

        with open(file_path, "rb") as f:
            on_disk = f.read()
        assert on_disk == md.encode("utf-8"), (
            f"Markdown bytes mismatch.\nExpected: {md!r}\nGot:      {on_disk.decode('utf-8', 'replace')!r}"
        )
        assert len(store.calls) == 1


def test_internal_save_does_not_touch_disk():
    """Internal documents must NEVER create or write an external file.

    We use ``tempfile.TemporaryDirectory`` and an *unrelated* file
    name; the script's ``file_path`` is set to a path inside that
    directory only for ``location == "external"``. For internal
    documents we point ``file_path`` at a path inside the temp
    directory and assert the file was never created.

    Internal ``store_document`` still fires once.
    """
    internal_text = "internal-only payload\n"
    with tempfile.TemporaryDirectory() as tmp:
        # Path the script holds; if the internal save path
        # touches ANYTHING on disk, this is the file it would
        # write to. We assert it does not exist after save.
        would_write = os.path.join(tmp, "should_not_be_written.txt")
        script, store = _make_script(
            editor_text=internal_text,
            file_path=would_write,
            location="internal",
        )

        script.save()

        assert not os.path.exists(would_write), (
            f"Internal save must not create external file; found {would_write!r}"
        )
        # No file anywhere under the temp dir was created.
        contents = sorted(os.listdir(tmp))
        assert contents == [], (
            f"Internal save touched the filesystem: {contents!r}"
        )
        # Internal DB write still fires (regression guard).
        assert len(store.calls) == 1, (
            f"Internal save must still call store_document; got {len(store.calls)} calls"
        )


def test_external_save_creates_file_when_missing():
    """External save with a non-existent ``file_path`` creates it.

    The first save of an external document has no existing file.
    The writer must create it (atomic-ish) and the bytes must
    match.
    """
    editor_text = "fresh file content\n"
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "fresh.py")
        assert not os.path.exists(file_path)
        script, store = _make_script(
            editor_text=editor_text, file_path=file_path, location="external"
        )

        script.save()

        assert os.path.exists(file_path)
        with open(file_path, "rb") as f:
            on_disk = f.read()
        assert on_disk == editor_text.encode("utf-8")
        assert len(store.calls) == 1
