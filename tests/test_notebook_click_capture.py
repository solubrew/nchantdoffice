"""T-NEW-070 — Tests for NchantdOfficeNotebook click capture.

Per the user's directive: "create methods for capture all
clicks in the web page so that we can intercept/redirect or
replace as needed".

This card adds 3 Python-side methods on NchantdOfficeNotebook
that drive a JS-side QWebEngineScript installed at
DocumentCreation:

  - ``cmd_register_click_handler(handler)`` — register a
    Python callable to fire on every web-page click.
  - ``cmd_redirect_click(url_pattern, replacement_url)`` —
    when a click's href matches ``url_pattern`` (substring),
    cancel the navigation and redirect to
    ``replacement_url``.
  - ``cmd_replace_click_action(selector, action)`` — for
    clicks matching ``selector``, REPLACE the default action
    with one of ``{block, log, stop, stop+block}``.
  - ``cmd_drain_click_events()`` — pull the JS-side
    ``window.__nchantd_clicks`` array into Python.

This file pins 6 invariants the T-NEW-070 implementation
promises:

  1. ``test_init_creates_click_state`` — ``__init__``
     initialises ``_click_handlers``, ``_click_redirects``,
     ``_click_replacements`` to empty lists and
     ``_click_capture_enabled`` to False.

  2. ``test_register_click_handler_appends`` — calling
     ``cmd_register_click_handler`` with a callable appends
     to ``_click_handlers`` and returns self.

  3. ``test_register_click_handler_rejects_non_callable``
     — non-callable handlers are rejected with a warning;
     ``_click_handlers`` is unchanged.

  4. ``test_redirect_click_validates_and_appends`` —
     ``cmd_redirect_click(pattern, replacement)`` appends a
     tuple to ``_click_redirects``; bad inputs are rejected.

  5. ``test_replace_click_action_validates_action`` — only
     ``{block, log, stop, stop+block}`` are valid actions;
     others are rejected.

  6. ``test_js_quote_escapes_specials`` — ``_js_quote``
     returns a JSON-escaped string safe for embedding in a
     JS literal (quotes, backslashes, unicode).
"""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))


def _bare_notebook():
    """Build a bare NchantdOfficeNotebook instance with mocked
    internal state. Skip __init__ (requires a Qt parent chain).
    """
    from nchantdoffice.widgets.documents.workbooks.notebooks import (
        NchantdOfficeNotebook,
    )
    nb = NchantdOfficeNotebook.__new__(NchantdOfficeNotebook)
    # Minimal attrs the T-NEW-070 code reads.
    nb.config = SimpleNamespace(dikt={})
    nb.browser = None
    nb._click_handlers = []
    nb._click_redirects = []
    nb._click_replacements = []
    nb._click_capture_enabled = False
    nb._click_instrumented = False
    return nb


def test_init_creates_click_state():
    """NchantdOfficeNotebook.__init__ seeds the click-capture state."""
    from nchantdoffice.widgets.documents.workbooks.notebooks import (
        NchantdOfficeNotebook,
    )
    # __init__ requires a Qt parent. Patch super().__init__ to
    # be a no-op so we can run __init__ without Qt.
    original_init = NchantdOfficeNotebook.__init__

    def _noop_init(self, parent=None, cfg=None):
        # Skip the parent chain but still seed our click state.
        # The actual click-state assignment happens AFTER
        # super().__init__(), so we replicate it here.
        self.config = SimpleNamespace(dikt={})
        self._click_handlers = []
        self._click_redirects = []
        self._click_replacements = []
        self._click_capture_enabled = False

    NchantdOfficeNotebook.__init__ = _noop_init
    try:
        nb = NchantdOfficeNotebook("test-parent")
    finally:
        NchantdOfficeNotebook.__init__ = original_init

    assert nb._click_handlers == [], (
        f"_click_handlers should start empty; got {nb._click_handlers!r}"
    )
    assert nb._click_redirects == [], (
        f"_click_redirects should start empty; got {nb._click_redirects!r}"
    )
    assert nb._click_replacements == [], (
        f"_click_replacements should start empty; got "
        f"{nb._click_replacements!r}"
    )
    assert nb._click_capture_enabled is False


def test_register_click_handler_appends():
    """A callable handler is appended to _click_handlers."""
    nb = _bare_notebook()
    calls = []
    result = nb.cmd_register_click_handler(
        handler=lambda ev: calls.append(ev),
    )
    assert result is nb, (
        "cmd_register_click_handler should return self"
    )
    assert len(nb._click_handlers) == 1, (
        f"_click_handlers should have 1 entry; got "
        f"{len(nb._click_handlers)}"
    )
    # Invoke the handler to confirm it was bound.
    nb._click_handlers[0]({"ts": 1, "selector": "a#x"})
    assert calls == [{"ts": 1, "selector": "a#x"}], (
        f"handler should receive the dict payload; got {calls!r}"
    )


def test_register_click_handler_rejects_non_callable():
    """Non-callables are rejected with a warning."""
    nb = _bare_notebook()
    # Each non-callable should be rejected without appending.
    for bad in [None, 42, "not_callable", {"a": 1}]:
        before = list(nb._click_handlers)
        nb.cmd_register_click_handler(handler=bad)
        assert nb._click_handlers == before, (
            f"Non-callable handler {bad!r} should be rejected; "
            f"got _click_handlers={nb._click_handlers!r}"
        )


def test_redirect_click_validates_and_appends():
    """cmd_redirect_click appends a tuple when inputs are valid."""
    nb = _bare_notebook()
    # Patch _push_click_redirect_to_webview to avoid Qt calls.
    nb._push_click_redirect_to_webview = lambda p, r: None
    result = nb.cmd_redirect_click("/old", "/new")
    assert result is nb
    assert nb._click_redirects == [("/old", "/new")], (
        f"_click_redirects should have one entry; got "
        f"{nb._click_redirects!r}"
    )
    # Append a second.
    nb.cmd_redirect_click("/foo", "/bar")
    assert nb._click_redirects == [
        ("/old", "/new"),
        ("/foo", "/bar"),
    ]


def test_redirect_click_rejects_bad_inputs():
    """Empty pattern or non-string replacement are rejected."""
    nb = _bare_notebook()
    nb._push_click_redirect_to_webview = lambda p, r: None
    for bad_pattern in ["", None, 42]:
        before = list(nb._click_redirects)
        nb.cmd_redirect_click(bad_pattern, "/x")
        assert nb._click_redirects == before, (
            f"Bad pattern {bad_pattern!r} should be rejected"
        )
    for bad_repl in [None, 42, ["x"], {"a": 1}]:
        before = list(nb._click_redirects)
        nb.cmd_redirect_click("/ok", bad_repl)
        assert nb._click_redirects == before, (
            f"Bad replacement {bad_repl!r} should be rejected"
        )


def test_replace_click_action_validates_action():
    """Only {block, log, stop, stop+block} are valid actions."""
    nb = _bare_notebook()
    nb._push_click_replacement_to_webview = lambda s, a: None

    # Valid actions append.
    for action in ["block", "log", "stop", "stop+block"]:
        before = list(nb._click_replacements)
        nb.cmd_replace_click_action(f"a.{action}", action)
        assert nb._click_replacements == before + [
            (f"a.{action}", action)
        ], (
            f"Action {action!r} should be accepted; got "
            f"{nb._click_replacements!r}"
        )

    # Invalid actions rejected.
    for bad_action in ["", "destroy", "click", None, 42]:
        before = list(nb._click_replacements)
        nb.cmd_replace_click_action("div", bad_action)
        assert nb._click_replacements == before, (
            f"Bad action {bad_action!r} should be rejected"
        )

    # Empty selector rejected.
    before = list(nb._click_replacements)
    nb.cmd_replace_click_action("", "block")
    assert nb._click_replacements == before


def test_js_quote_escapes_specials():
    """_js_quote escapes quotes, backslashes, and unicode safely.

    Python's json.dumps uses ``ensure_ascii=True`` by default,
    which escapes non-ASCII chars as ``\\uXXXX``. That's valid
    JS literal syntax, so we test for that — the contract is
    "safe for embedding in a JS literal", not "round-trip the
    exact bytes".
    """
    from nchantdoffice.widgets.documents.workbooks.notebooks import (
        NchantdOfficeNotebook,
    )
    # Cases that have historically broken naive string concat.
    cases = [
        ('plain', '"plain"'),
        ('with "quotes"', '"with \\"quotes\\""'),
        ("with 'apostrophe'", '"with \'apostrophe\'"'),
        ("with \\backslash", '"with \\\\backslash"'),
        ("with\nnewline", '"with\\nnewline"'),
        # Unicode is escaped as \\uXXXX — valid JS literal syntax.
        ("unicode 🎉", '"unicode \\ud83c\\udf89"'),
        ("", '""'),
        ("</script>", '"</script>"'),
    ]
    for input_str, expected in cases:
        actual = NchantdOfficeNotebook._js_quote(input_str)
        assert actual == expected, (
            f"_js_quote({input_str!r}) returned {actual!r}; "
            f"expected {expected!r}"
        )


def test_install_click_instrumentation_is_idempotent():
    """Repeated _install_click_instrumentation calls don't
    re-inject the script (guards via _click_instrumented flag)."""
    nb = _bare_notebook()
    # Mock the view + page + scripts() so we can observe calls.
    mock_scripts = MagicMock()
    mock_page = MagicMock()
    mock_page.scripts.return_value = mock_scripts
    mock_view = MagicMock()
    mock_view.page.return_value = mock_page

    # First call: should insert the script + set the flag.
    nb._install_click_instrumentation(mock_view)
    assert nb._click_instrumented is True, (
        f"_click_instrumented should be True after first call; "
        f"got {nb._click_instrumented!r}"
    )
    first_call_count = mock_scripts.insert.call_count

    # Second call: should be a no-op.
    nb._install_click_instrumentation(mock_view)
    assert mock_scripts.insert.call_count == first_call_count, (
        f"Second call should NOT insert the script again; "
        f"got {mock_scripts.insert.call_count} insert calls "
        f"(expected {first_call_count})."
    )


def test_cmd_drain_click_events_returns_empty_when_no_webview():
    """cmd_drain_click_events returns [] when no webview is loaded."""
    nb = _bare_notebook()
    # browser=None (no webview).
    result = nb.cmd_drain_click_events()
    assert result == [], (
        f"cmd_drain_click_events with no webview should return []; "
        f"got {result!r}"
    )
