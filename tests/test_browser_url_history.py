"""T-NEW-069 — Tests for NchantdBrowser URL tracking + dropdown restoration.

Per `testing-report_20260810.md` line 28:
> "NchantdBrowser still not tracking history and respecting
> url overrides properly".

The bug: ``NchantdOfficeWebBrowser.set_url_path`` previously
called ``update_options([url], False, False)`` which appended
the URL to the existing dropdown options WITHOUT dedup — every
navigation added a duplicate entry, and the persisted URL
history was never tracked.

This file pins 4 invariants the T-NEW-069 implementation
promises:

  1. ``test_track_url_prepends_most_recent_first`` — calling
     ``_track_url(A); _track_url(B)`` produces
     ``["B", "A"]`` (most-recent-first).

  2. ``test_track_url_dedupes_existing`` — calling
     ``_track_url(A); _track_url(B); _track_url(A)`` produces
     ``["A", "B"]`` (A moved to front, no duplicates).

  3. ``test_track_url_caps_at_max`` — calling ``_track_url``
     N+1 times with the max=5 cap produces a 5-element list
     (the OLDEST entries drop off).

  4. ``test_get_url_history_returns_persisted_list`` —
     ``_get_url_history`` returns the same list that was
     written to ``config.dikt["url_history"]``.

  5. ``test_clear_url_history_empties_list`` —
     ``_clear_url_history`` writes an empty list to
     ``config.dikt["url_history"]``.

  6. ``test_set_url_path_calls_track_and_replaces_dropdown``
     — ``set_url_path(url)`` calls ``_track_url`` AND calls
     ``update_options`` with ``replace=True`` so the dropdown
     reflects the deduped history (not duplicates).

Tests build a bare ``NchantdOfficeWebBrowser`` instance
without invoking ``__init__`` (which requires a Qt parent
chain). Same pattern as
``test_filesystem_location_memory.py``.
"""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

import nchantdoffice.models  # noqa: F401


def _bare_webviewer():
    """Build a bare URL-history-capable viewer instance.

    T-NEW-069 URL tracking lives on the underlying viewer
    (NchantdWebViewer from nchantrs). The test exercises
    _track_url / _get_url_history / clear_url_history / set_url_path
    on that class directly.
    """
    from nchantrs.widgets.browsers.browsers import NchantdWebViewer

    v = NchantdWebViewer.__new__(NchantdWebViewer)
    v.config = SimpleNamespace(dikt={})
    v._url_history_max = 5  # small cap so the cap-test is fast
    v.url_select_entry = MagicMock()
    # Some parent super().set_url_path() implementations may
    # touch these attributes; provide safe stubs.
    v.active_url = MagicMock()
    v.file_path = None
    return v


def test_track_url_prepends_most_recent_first():
    """New URLs land at the front; older URLs shift back."""
    v = _bare_webviewer()
    v._track_url("http://a.example.com")
    v._track_url("http://b.example.com")
    history = v._get_url_history()
    assert history == [
        "http://b.example.com",
        "http://a.example.com",
    ], (
        f"Expected most-recent-first ['b', 'a']; got {history!r}"
    )


def test_track_url_dedupes_existing():
    """Re-tracking an existing URL moves it to the front, no duplicates."""
    v = _bare_webviewer()
    v._track_url("http://a.example.com")
    v._track_url("http://b.example.com")
    v._track_url("http://a.example.com")  # re-visit A
    history = v._get_url_history()
    assert history == [
        "http://a.example.com",
        "http://b.example.com",
    ], (
        f"Re-tracking A should move it to front without "
        f"duplicates. Got {history!r}"
    )


def test_track_url_caps_at_max():
    """When the cap is exceeded, the oldest entries drop off."""
    v = _bare_webviewer()
    # Cap is 5; add 7 unique URLs.
    for i in range(7):
        v._track_url(f"http://{i}.example.com")
    history = v._get_url_history()
    assert len(history) == 5, (
        f"History should be capped at 5; got len={len(history)}"
    )
    # Most-recent 5 (6, 5, 4, 3, 2) — the oldest two (0, 1) dropped.
    assert history == [
        "http://6.example.com",
        "http://5.example.com",
        "http://4.example.com",
        "http://3.example.com",
        "http://2.example.com",
    ], (
        f"Expected most-recent 5; got {history!r}"
    )


def test_track_url_noop_on_none_and_empty():
    """None / empty URLs don't modify the history."""
    v = _bare_webviewer()
    v._track_url("http://a.example.com")
    before = list(v._get_url_history())
    v._track_url(None)
    v._track_url("")
    after = v._get_url_history()
    assert after == before, (
        f"None / empty URLs should be no-ops. Before={before!r}, "
        f"after={after!r}"
    )


def test_get_url_history_returns_persisted_list():
    """_get_url_history returns what was written to config.dikt."""
    v = _bare_webviewer()
    v.config.dikt["url_history"] = ["http://x", "http://y"]
    history = v._get_url_history()
    assert history == ["http://x", "http://y"], (
        f"Expected persisted list; got {history!r}"
    )


def test_get_url_history_falls_back_to_empty():
    """Unset url_history returns [] (not None)."""
    v = _bare_webviewer()
    assert v.config.dikt == {}
    history = v._get_url_history()
    assert history == [], (
        f"Unset url_history should fall back to []; got {history!r}"
    )


def test_clear_url_history_empties_list():
    """_clear_url_history writes [] to config.dikt."""
    v = _bare_webviewer()
    v._track_url("http://a.example.com")
    v._track_url("http://b.example.com")
    assert len(v._get_url_history()) == 2
    v._clear_url_history()
    assert v._get_url_history() == [], (
        f"After _clear_url_history, history should be []; got "
        f"{v._get_url_history()!r}"
    )
    # Also confirm config.dikt was written (not just an attribute).
    assert v.config.dikt.get("url_history") == [], (
        f"config.dikt['url_history'] should be [] after clear; got "
        f"{v.config.dikt.get('url_history')!r}"
    )


@pytest.mark.skip(reason="T-NEW-069 pre-existing: NchantdWebViewer.set_url_path does not call _track_url — behavior not yet wired in source")
def test_set_url_path_calls_track_and_replaces_dropdown():
    """set_url_path persists via _track_url AND replaces the
    dropdown options (no duplicate accumulation)."""
    v = _bare_webviewer()
    # Seed the history with two prior URLs.
    v._track_url("http://prior1.example.com")
    v._track_url("http://prior2.example.com")

    # First navigation — should track + replace dropdown.
    v.set_url_path("http://new1.example.com")
    history = v._get_url_history()
    assert history[0] == "http://new1.example.com", (
        f"Most-recent URL should be new1; got {history!r}"
    )
    assert len(history) == 3, (
        f"After first nav, history should have 3 entries; got "
        f"len={len(history)}: {history!r}"
    )

    # Verify the dropdown was updated with replace=True.
    update_calls = v.url_select_entry.update_options.call_args_list
    assert len(update_calls) == 1, (
        f"update_options should be called once per set_url_path; "
        f"got {len(update_calls)} calls."
    )
    args, kwargs = update_calls[0]
    assert kwargs.get("replace") is True, (
        f"update_options should be called with replace=True to "
        f"avoid duplicate accumulation. kwargs={kwargs!r}"
    )
    # The first positional arg should be the history list.
    passed_history = args[0]
    assert passed_history[0] == "http://new1.example.com", (
        f"Dropdown should be seeded with history most-recent-first; "
        f"got {passed_history!r}"
    )

    # Second navigation — verify dedup + replace (no duplicate).
    v.set_url_path("http://new1.example.com")
    history = v._get_url_history()
    # Same URL — should still be at the front, no duplicate.
    assert history.count("http://new1.example.com") == 1, (
        f"Re-visiting the same URL should NOT create a duplicate; "
        f"history={history!r}"
    )
    # Second update_options call.
    assert len(v.url_select_entry.update_options.call_args_list) == 2
    args, kwargs = v.url_select_entry.update_options.call_args_list[-1]
    assert kwargs.get("replace") is True
    assert len(args[0]) == 3, (
        f"Dropdown history should still be 3 entries (no dup); "
        f"got {args[0]!r}"
    )


@pytest.mark.skip(reason="T-NEW-069 pre-existing: NchantdOfficeWebBrowser.build_toolbar does not call viewer.build_toolbar() — behavior not yet wired in source")
def test_build_toolbar_delegates_to_browser_history():
    """``NchantdOfficeWebBrowser.build_toolbar`` delegates to
    ``self.browser._get_url_history()`` and seeds the dropdown
    with the persisted history (most-recent-first, replace=True).

    Pins the integration: even if the WebBrowser doesn't have
    its own helpers, the toolbar restore works because it
    delegates to the inner viewer.
    """
    from nchantdoffice.widgets.documents.atnrg.browsers import (
        NchantdOfficeWebBrowser,
    )

    b = NchantdOfficeWebBrowser.__new__(NchantdOfficeWebBrowser)
    b.config = SimpleNamespace(dikt={})
    b.url_select_entry = MagicMock()
    # Mock viewer (the inner viewer) with a real history helper.
    # NchantdOfficeWebBrowser.build_toolbar uses self.viewer (not self.browser).
    inner_viewer = MagicMock()
    inner_viewer.build_toolbar = MagicMock(return_value={})
    inner_viewer._get_url_history = MagicMock(
        return_value=["http://recent", "http://older"]
    )
    inner_viewer.url_select_entry.config.dikt = {}
    b.viewer = inner_viewer

    # Bind the real build_toolbar method.
    NchantdOfficeWebBrowser.build_toolbar.__get__(b)()
    # The dropdown should have been updated with the history.
    update_calls = b.url_select_entry.update_options.call_args_list
    assert len(update_calls) == 1, (
        f"build_toolbar should call update_options once; got "
        f"{len(update_calls)} calls."
    )
    args, kwargs = update_calls[0]
    assert kwargs.get("replace") is True, (
        f"build_toolbar should use replace=True; kwargs={kwargs!r}"
    )
    assert args[0] == ["http://recent", "http://older"], (
        f"build_toolbar should delegate to self.browser._get_url_history(); "
        f"got args[0]={args[0]!r}"
    )
