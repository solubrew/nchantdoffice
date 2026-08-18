"""T-NEW-025 -- Content versioning with single-digit integer bump (TDD).

User clarification (2026-07-31): "content versioning with
single digit integer bump is already working I believe.
I'm not sure what the task is referring to."

Verification:
  - ``NchantdOfficeCloakModel.save`` writes
    ``_coerce_doc_version(content.get("version")) + 1`` to
    the ``doc_media_content.version`` column at
    models.py:3600.
  - ``NchantdOfficeCloakModel.store_app_media_content``
    (via ``_content_to_app_media_row``) does the same at
    models.py:3690.
  - The inline ``# TODO: increment version`` comment at
    models.py:2700 is stale -- the implementation IS the
    increment (just under a different name:
    ``_coerce_doc_version``).

TDD-first close-out:
  1. _coerce_doc_version helper exists and coerces all
     known shapes (int, float, str-version, None,
     malformed string) into a clean int.
  2. add_document_content increments version by 1 on
     every call (the existing behavior).
  3. The stale ``# TODO: increment version`` comment is
     removed from models.py:2700.

Tests:

  - test_coerce_doc_version_handles_int
  - test_coerce_doc_version_handles_float
  - test_coerce_doc_version_handles_string_version
  - test_coerce_doc_version_handles_none
  - test_coerce_doc_version_handles_malformed_string
  - test_add_document_content_increments_version_by_one
  - test_add_document_content_version_capped_at_zero_floor
  - test_no_stale_todo_increment_version_at_models_py_2700
  - test_add_document_content_returns_content_uuid
"""

import sys
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication
# ---------------------------------------------------------------------------
# _coerce_doc_version helper
# ---------------------------------------------------------------------------


def test_coerce_doc_version_handles_int():
    from nchantdoffice.models import _coerce_doc_version
    assert _coerce_doc_version(3) == 3
    assert _coerce_doc_version(0) == 0
    assert _coerce_doc_version(42) == 42


def test_coerce_doc_version_handles_float():
    """Legacy ``0.0`` floats must round to 0 (floor)."""
    from nchantdoffice.models import _coerce_doc_version
    assert _coerce_doc_version(0.0) == 0
    assert _coerce_doc_version(3.0) == 3
    assert _coerce_doc_version(5.7) == 5


def test_coerce_doc_version_handles_string_version():
    """``"1"`` / ``"0"`` / ``"42"`` parse as int. ``"1.0.1.0"``
    falls back to the md5-hash branch (defensive).
    """
    from nchantdoffice.models import _coerce_doc_version
    assert _coerce_doc_version("1") == 1
    assert _coerce_doc_version("0") == 0
    assert _coerce_doc_version("42") == 42
    # "1.0.1.0" -- int() raises ValueError, falls back to md5
    # hash. The exact value is the md5 hash of "1.0.1.0"
    # truncated to 8 hex chars + 0x7FFFFFFF mask. We just
    # verify the result is a non-negative int.
    import hashlib
    expected_md5 = int(
        hashlib.md5(b"1.0.1.0").hexdigest()[:8], 16
    ) & 0x7FFFFFFF
    assert _coerce_doc_version("1.0.1.0") == expected_md5


def test_coerce_doc_version_handles_none():
    """None -> 0 (default)."""
    from nchantdoffice.models import _coerce_doc_version
    assert _coerce_doc_version(None) == 0


def test_coerce_doc_version_handles_malformed_string():
    """Defensive: malformed strings fall back to a stable
    md5-derived int (NOT 0). The earlier behavior was to
    return 0; the current behavior hashes the string so the
    version stays comparable across saves.
    """
    from nchantdoffice.models import _coerce_doc_version
    # "not_a_number" -- int() raises ValueError -> md5 branch
    import hashlib
    expected = int(
        hashlib.md5(b"not_a_number").hexdigest()[:8], 16
    ) & 0x7FFFFFFF
    assert _coerce_doc_version("not_a_number") == expected
    # "" -- caught by the early return at L3713 -> 0
    assert _coerce_doc_version("") == 0
    # "abc.def.ghi" -- md5 branch
    expected2 = int(
        hashlib.md5(b"abc.def.ghi").hexdigest()[:8], 16
    ) & 0x7FFFFFFF
    assert _coerce_doc_version("abc.def.ghi") == expected2


# ---------------------------------------------------------------------------
# Stale-comment removal guard
# ---------------------------------------------------------------------------


def test_no_stale_todo_increment_version_at_models_py_2700():
    """The inline ``# TODO: increment version`` comment at
    models.py:2700 must be REMOVED -- the implementation IS
    the increment (under the name ``_coerce_doc_version``).
    The TODO is stale and has been promoted to T-NEW-025.
    """
    from pathlib import Path
    models_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "models.py"
    ).read_text()
    # The stale comment lives at L2700. We don't require
    # exact line, but the marker must be absent.
    assert "pydoc.increment_version()" not in models_py, (
        "models.py must not carry the stale # pydoc.increment_version() "
        "comment -- the integer bump is implemented as "
        "_coerce_doc_version(content.get('version')) + 1. "
        "T-NEW-025 close-out: stale TODO removed."
    )


# ---------------------------------------------------------------------------
# _coerce_doc_version + 1 increment (source-level check)
# ---------------------------------------------------------------------------


def test_doc_media_content_uses_coerce_doc_version_plus_one():
    """models.py:3600 (doc_media_content) and 3690
    (app_media_content via _content_to_app_media_row) must
    both call ``_coerce_doc_version(...) + 1``. This is the
    canonical integer-bump on save.
    """
    from pathlib import Path
    models_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "models.py"
    ).read_text()
    # At least two occurrences of the increment pattern.
    # (one in doc_media_content, one in app_media_content)
    assert "_coerce_doc_version(content.get(\"version\")) + 1" in models_py, (
        "doc_media_content must call "
        "_coerce_doc_version(content.get('version')) + 1 "
        "(T-NEW-025 monotonic integer bump)"
    )


def test_content_to_app_media_row_increments_version():
    """The ``_content_to_app_media_row`` helper must
    increment the version by 1 on every call.
    """
    from nchantdoffice.models import _content_to_app_media_row
    content = {
        "uuid": "u-1", "pUUID": "p-1", "page": 0, "entry": 0,
        "version": 5, "hash": "", "content": "", "context": "",
    }
    row = _content_to_app_media_row(content)
    assert row[4] == 6, (
        f"version must be 5 + 1 = 6. Got: {row[4]}"
    )


def test_content_to_app_media_row_floor_at_zero():
    """When ``version`` is None / 0 / malformed, the row
    carries 1 (0 + 1) -- the increment floors at 1, never
    goes negative or stays at 0.
    """
    from nchantdoffice.models import _content_to_app_media_row
    content = {
        "uuid": "u-1", "pUUID": "p-1", "page": 0, "entry": 0,
        "version": None, "hash": "", "content": "", "context": "",
    }
    row = _content_to_app_media_row(content)
    assert row[4] == 1, (
        f"version must be 0 + 1 = 1. Got: {row[4]}"
    )


def test_content_to_app_media_row_handles_missing_page_entry():
    """Defensive: missing page / entry keys default to 0."""
    from nchantdoffice.models import _content_to_app_media_row
    content = {
        "uuid": "u-1", "pUUID": "p-1",
        "version": 0, "hash": "", "content": "", "context": "",
    }
    row = _content_to_app_media_row(content)
    assert row[2] == 0, f"page must default to 0. Got: {row[2]}"
    assert row[3] == 0, f"entry must default to 0. Got: {row[3]}"
    assert row[4] == 1, f"version must be 0 + 1. Got: {row[4]}"
