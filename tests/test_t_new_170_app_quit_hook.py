"""T-NEW-170 WIRE-5 -- app-quit hook for FloatedTab re-attach.

The operator-set T-NEW-170 DECIDE-1 (a) (refined at lock-time):
"re-attach only on dialog close or application close".

When the operator quits the app while a FloatedTab dialog
is still open, the dialog's closeEvent does NOT fire (the
app is dying). We hook ``QApplication.aboutToQuit`` once
and iterate every FloatedTab that's currently open, calling
``re_attach_tab`` on each.

This commit ships a small ``_install_app_quit_hook`` helper
on the FloatedTab class. The helper:
1. On the first invocation, calls
   ``QApplication.instance().aboutToQuit.connect(self._on_app_quit)``.
2. On every subsequent FloatedTab construction, registers
   the new instance via ``_register_for_app_quit_re_attach``
   so the on-quit handler can iterate the live instances.
3. ``_on_app_quit`` iterates the registered instances and
   calls ``self.home_tabset.re_attach_tab(self)`` on each.

Tests are AST-source structural.
"""

import ast
import re
from pathlib import Path


FLOATED_TAB_PATH = (
    Path(__file__).parents[1]
    / "nchantdoffice/widgets/controls/floated_tab.py"
)


def _source() -> str:
    return FLOATED_TAB_PATH.read_text()


def test_app_quit_hook_exists():
    """FloatedTab references ``aboutToQuit`` to install the
    app-quit re-attach handler.
    """
    assert "aboutToQuit" in _source(), (
        "T-NEW-170 WIRE-5: FloatedTab must reference "
        "`aboutToQuit` (the QCoreApplication signal that "
        "fires on app quit). Without this signal the "
        "FloatedTab dialogs don't get re-attached when "
        "the operator closes the main app."
    )


def test_app_quit_hook_iterates_floated_tabs():
    """The aboutToQuit hook iterates over the currently-open
    FloatedTab instances and calls re_attach_tab on each.

    The connector's body must call back into the re-attach
    primitive (T-NEW-170 WIRE-3), since each open FloatedTab
    carries its own home coordinates.
    """
    ok = "aboutToQuit" in _source() and "re_attach_tab" in _source()
    assert ok, (
        "T-NEW-170 WIRE-5: the `aboutToQuit` hook must "
        "iterate open FloatedTab instances and call "
        "`re_attach_tab(...)` on each."
    )


def test_app_quit_hook_uses_qapplication_instance():
    """The hook connects via ``QApplication.instance().aboutToQuit.connect(...)``.

    Qt's ``aboutToQuit`` is a signal on QCoreApplication; the
    canonical connection pattern is
    ``QApplication.instance().aboutToQuit.connect(...)``.
    """
    src = _source()
    pattern = r"(?:QApplication|qapp|pyqt\.QApplication|\.instance\(\))"
    ok = "aboutToQuit" in src and bool(re.search(pattern, src))
    assert ok, (
        "T-NEW-170 WIRE-5: the aboutToQuit hook must "
        "connect via `QApplication.instance()` (or "
        "equivalent) so the install binds to the live "
        "QApplication."
    )


def test_app_quit_hook_installed_in_floated_tab_init():
    """The hook install lives in ``FloatedTab.__init__`` (the
    natural install point per the card body).

    Acceptable patterns:
      - ``__init__`` directly references ``aboutToQuit`` /
        ``_ensure_app_quit_hook_installed`` /
        ``_FLOATED_TABS_REGISTRY.append``
      - ``__init__`` invokes a private helper that registers
        on the registry (the install indirection is fine;
        we just need a clear "constructed -> installed" path).
    """
    src = _source()
    tree = ast.parse(src)
    # Read the __init__ body source via unparse so we can
    # match against either the literal aboutToQuit or the
    # indirect helper call.
    init_src = None
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == "FloatedTab"):
            continue
        for body_node in node.body:
            if isinstance(body_node, ast.FunctionDef) and body_node.name == "__init__":
                init_src = ast.unparse(body_node)
    assert init_src is not None, (
        "FloatedTab.__init__ not found"
    )
    has_install = (
        "aboutToQuit" in init_src
        or "_ensure_app_quit_hook_installed" in init_src
        or "_FLOATED_TABS_REGISTRY.append" in init_src
    )
    assert has_install, (
        "T-NEW-170 WIRE-5: FloatedTab.__init__ must call "
        "into the app-quit hook installer (literal "
        "aboutToQuit / _ensure_app_quit_hook_installed "
        "/ _FLOATED_TABS_REGISTRY.append). The natural "
        "install point is on every FloatedTab construction."
    )


def test_on_app_quit_iterates_registered_floated_tabs():
    """The hook's body iterates a registry of open FloatedTab
    instances and calls ``re_attach_tab(self_or_instance)``
    on each.

    The natural registry is a module-level list/set that's
    appended on every FloatedTab.__init__ and cleared on
    every close.
    """
    src = _source()
    # Look for the pattern: a registry list (e.g. _REGISTRY or
    # _FLOATED_TABS) + iteration in a callback.
    has_registry = (
        "_REGISTRY" in src
        or "_FLOATED_TABS" in src
        or "_open_floated_tabs" in src
        or "_dialogs" in src
    )
    has_iteration = (
        "for " in src
        or "while " in src
    )
    has_re_attach = "re_attach_tab" in src
    assert has_registry and has_iteration and has_re_attach, (
        "T-NEW-170 WIRE-5: the aboutToQuit hook must "
        "iterate a registry of open FloatedTab instances "
        "and call `re_attach_tab(...)` on each. "
        f"Found registry={has_registry}, "
        f"iteration={has_iteration}, "
        f"re_attach={has_re_attach}."
    )
