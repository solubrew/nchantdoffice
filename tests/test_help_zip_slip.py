"""Sprint 2 — Zip Slip fix regression test for the help-docs updater.

Status: BLOCKED on direct import of ``NchantdHelp`` because its module
chain pulls in ``pycurity.pyhash.get_file_hash`` which is missing in
the installed ``pycurity`` package. The test below exercises the
production-style protection logic standalone (no import) and asserts
the same invariants the production fix will enforce.

Migration: once ``pycurity.pyhash.get_file_hash`` is available, change
the protection block in ``nchantdoffice.widgets.config.help.update_help_docs``
to call ``_safe_extractall(zf, dest)`` and add a focused integration
test that imports the real ``update_help_docs``.
"""

import io
import os
import tempfile
import zipfile


def _safe_extractall(zf, dest):
    """Production-shape Zip Slip protection: refuse any member whose
    resolved path escapes ``dest``. Returns the list of written files.
    """
    real_dest = os.path.realpath(dest)
    written = []
    for member in zf.infolist():
        target = os.path.realpath(os.path.join(real_dest, member.filename))
        if target != real_dest and not target.startswith(real_dest + os.sep):
            continue
        if member.is_dir():
            os.makedirs(target, exist_ok=True)
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(zf.read(member.filename))
        written.append(target)
    return written


def test_safe_extractall_blocks_parent_traversal():
    """A zip entry ``../escape.txt`` must NOT be written outside ``dest``."""
    with tempfile.TemporaryDirectory() as dest:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("legit/help.pdf", b"%PDF-1.4\nsafe")
            zf.writestr("../escape.txt", b"escaped payload")
        zip_bytes = buf.getvalue()

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            written = _safe_extractall(zf, dest)

        assert any(p.endswith("legit/help.pdf") for p in written), (
            "Legitimate member must still be extracted"
        )
        assert not any("escape.txt" in p for p in written), (
            "Traversing zip member must NOT be written"
        )
        assert not os.path.exists(os.path.join(dest, "..", "escape.txt")), (
            "Zip Slip leak: file written outside dest"
        )


def test_safe_extractall_blocks_absolute_path():
    """Absolute paths inside the archive must be refused (defence in
    depth against Zip Slip variants using absolute targets).
    """
    with tempfile.TemporaryDirectory() as dest:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("/tmp/hermes-zipslip-marker.txt", b"should not write")
        zip_bytes = buf.getvalue()

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            written = _safe_extractall(zf, dest)

        assert not any("zipslip-marker" in p for p in written), (
            "Absolute-path zip member must be refused"
        )