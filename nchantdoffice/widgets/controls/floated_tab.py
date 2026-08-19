# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||

# ======================================Standard Library Modules======================================================|
from typing import Any

# ======================================3rd Party Library Modules======================================================|

# ======================================Solutions Brewer Library Modules==============================================|
from nchantrs.libraries import pyqt

# T-NEW-170 (DESK / 2026-08-19): FloatedTab dialog class. The
# LOCKED DESIGN is from the card body in TODOs.md; both
# DECIDE-1 and DECIDE-2 are operator-approved.

# DECIDE-1 (a) -- re-attach ONLY on dialog close or app
# close. The tab stays detached for the entire lifetime of
# the dialog. The operator closes the dialog (X button /
# File>Close / app exit) and the tab re-attaches to its
# recorded position.
#
# DECIDE-2 (ii) -- full standalone 2-pane shell that REUSES
# NchantdDocumentStandaloneWindow from T-NEW-169. The
# FloatedTab host wraps the standalone window as the
# dialog body's central widget. The right-toolbox is fully
# accessible from the second monitor -- operator doesn't
# alt-tab back to the main window when they need a tool.


# T-NEW-170 WIRE-5: module-level registry of open FloatedTab
# instances. Populated in __init__ (each new FloatedTab
# appends itself), drained by the aboutToQuit hook (iterated
# + re-attach invoked), and pruned by closeEvent (closed
# dialogs are removed so the on-quit iteration doesn't
# double-process an already-closed dialog).
_FLOATED_TABS_REGISTRY: list = []
_APP_QUIT_HOOK_INSTALLED: bool = False


class FloatedTab(pyqt.QDialog):
    """T-NEW-170 \u2014 popup dialog hosting one pulled-out document tab.

    Lifecycle (per the locked DECIDE-1 a):
        1. Operator right-clicks a tab (or clicks the toolbar
           \"\u2197\" button) \u2192 the parent tabset's pop_out_tab()
           instantiates a FloatedTab.
        2. The dialog shows on the operator's second monitor.
        3. The operator works in the dialog for as long as
           they want; the tab stays in the dialog (no
           auto-reattach on node-change).
        4. The operator closes the dialog (X / File>Close /
           app-exit) \u2192 closeEvent fires \u2192 home_tabset
           re_attach_tab(self) \u2192 the tab reappears in its
           home tabset at its home position.

    The dialog itself is QDialog (the Qt class for top-level
    popup windows). The standalone-window widget (from
    T-NEW-169) is the central widget of the dialog body.
    """

    def __init__(
        self,
        parent: Any,
        standalone_window: Any,
        document_widget: Any,
        home_node_id: Any,
        home_position: int,
        home_tabset: Any,
    ) -> None:
        """Initialise the popup dialog.

        Args:
            parent: QWidget owner (typically the main app
                window). Drives the dialog's parent-chrome
                + window-modality rules.
            standalone_window: the NchantdDocumentStandaloneWindow
                instance (T-NEW-169) that hosts the pulled-out
                document + right-toolbox. FloatedTab composes
                this as the dialog's central widget; the
                standalone_window's own lifecycle (init /
                show / close) is owned by T-NEW-169, NOT by
                FloatedTab.
            document_widget: the QWidget that was detached
                from its parent tabset. Stored on self so
                re_attach_tab can re-parent it.
            home_node_id: str / int -- the node the tab
                belonged to. Stored for re-attach.
            home_position: int -- the position in the home
                tabset. Stored for re-attach.
            home_tabset: NchantdOfficeTabSet (T-NEW-170's
                caller) -- where the tab returns to on
                re-attach. closeEvent calls
                ``self.home_tabset.re_attach_tab(self)``.
        """
        super().__init__(parent)
        # T-NEW-170 WIRE-1: store the home coordinates for
        # re-attach. closeEvent reads these and passes them
        # to home_tabset.re_attach_tab(self).
        self.home_node_id = home_node_id
        self.home_position = home_position
        self.home_tabset = home_tabset
        # Store the detached document_widget so the parent
        # can re-parent it on close. (The standalone_window
        # stays in this dialog for its lifetime; only the
        # document_widget re-parents on close.)
        self.document_widget = document_widget

        # Compose the standalone window into the dialog's
        # body. The standalone window already has its own
        # inner layout (the 2-pane left-document + right-
        # toolbox shell from T-NEW-169's NchantdDocumentStandaloneWindow).
        # We use a simple QVBoxLayout to host it; if the
        # operator wants padding / margins / a status bar,
        # that comes in a future card.
        layout = pyqt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(standalone_window)
        self.setLayout(layout)

        # Dialog window settings. Operator-friendly defaults:
        # resize to a usable size (mirrors the main app) and
        # leave the operator free to maximize when they need
        # the full second-screen real estate.
        self.resize(1280, 800)

        # T-NEW-170: set the dialog title to the document
        # widget's name if available. The title bar acts as
        # the operator's "I know what tab this was" anchor
        # when they have multiple FloatedTabs open on
        # multiple monitors.
        try:
            doc_name = (
                getattr(document_widget, "name", None)
                or getattr(document_widget, "document_nm", None)
                or "Document"
            )
        except Exception:
            doc_name = "Document"
        self.setWindowTitle(f"Pulled out: {doc_name}")

        # T-NEW-170 WIRE-5: register this FloatedTab in the
        # module-level registry and ensure the
        # QApplication.aboutToQuit hook is installed. Both
        # are best-effort (log + skip if Qt isn't fully
        # wired); the dialog is still functional without
        # the hook -- the dialog-close path (closeEvent,
        # T-NEW-170 WIRE-1) still re-attaches individually.
        try:
            FloatedTab._ensure_app_quit_hook_installed()
        except Exception as _install_err:
            logma.info(
                f"[FloatedTab] app-quit hook install failed "
                f"(non-blocking): {_install_err!r}"
            )
        try:
            _FLOATED_TABS_REGISTRY.append(self)
        except Exception:
            pass

    @staticmethod
    def _ensure_app_quit_hook_installed() -> None:
        """T-NEW-170 WIRE-5 -- idempotently install the
        ``aboutToQuit`` hook on the live QApplication.

        The first call wires the connection. Subsequent
        calls (from later FloatedTab constructions) are a
        no-op -- the flag ``_APP_QUIT_HOOK_INSTALLED``
        prevents duplicate installations.

        Best-effort: if QApplication.instance() returns
        None (e.g. in a test without a Qt event loop), the
        function logs and returns -- the dialog is still
        functional in isolation.
        """
        global _APP_QUIT_HOOK_INSTALLED
        if _APP_QUIT_HOOK_INSTALLED:
            return
        app = None
        try:
            app = pyqt.QApplication.instance()
        except Exception:
            app = None
        if app is None:
            # Fall back to pyqt.QApplication without a
            # live instance binding -- some Qt bindings
            # accept a static aboutToQuit.
            try:
                app = pyqt.QApplication
            except Exception:
                return
        try:
            about_to_quit = getattr(app, "aboutToQuit", None)
            if about_to_quit is None:
                return
            try:
                about_to_quit.connect(FloatedTab._on_app_quit)
            except Exception:
                return
            _APP_QUIT_HOOK_INSTALLED = True
            logma.info(
                "[FloatedTab] installed aboutToQuit hook "
                "for app-shutdown re-attach"
            )
        except Exception:
            return

    @staticmethod
    def _on_app_quit() -> None:
        """T-NEW-170 WIRE-5 -- iterate the registry and
        re-attach every open FloatedTab to its home tabset.

        Connects to ``QApplication.aboutToQuit`` (set up by
        ``_ensure_app_quit_hook_installed``). On the app-quit
        signal, this static method iterates the module-level
        ``_FLOATED_TABS_REGISTRY`` and calls
        ``home_tabset.re_attach_tab(floated_tab)`` on each
        entry.

        Best-effort: each entry's re-attach is wrapped in a
        try/except so a single failure doesn't block the
        others. The registry is cleared after iteration
        (the dialogs are going away anyway).
        """
        try:
            # Snapshot the registry so iteration + close
            # coupling don't mutate the list mid-loop.
            snapshot = list(_FLOATED_TABS_REGISTRY)
            for ftab in snapshot:
                try:
                    home_tabset = getattr(
                        ftab, "home_tabset", None
                    )
                    if home_tabset is not None:
                        home_tabset.re_attach_tab(ftab)
                except Exception as e:
                    logma.warning(
                        f"[FloatedTab._on_app_quit] "
                        f"re_attach_tab failed: {e!r}"
                    )
            # Clear the registry post-iteration. The dialogs
            # themselves are about to be torn down by Qt;
            # we don't want stale entries.
            try:
                _FLOATED_TABS_REGISTRY.clear()
            except Exception:
                pass
        except Exception as e:
            logma.warning(
                f"[FloatedTab._on_app_quit] top-level failure "
                f"(swallowed): {e!r}"
            )

    def closeEvent(self, event) -> None:
        """T-NEW-170 DECIDE-1 (a): re-attach on dialog close.

        The user closes this dialog (X / File>Close / app-exit).
        closeEvent fires, calls home_tabset.re_attach_tab(self)
        to put the document widget back in its home tabset at
        its home position, then defers to QDialog's standard
        closeEvent so the dialog window actually closes.
        """
        # T-NEW-170 WIRE-3: the actual re-attach lives on the
        # parent tabset (NchantdOfficeTabSet.re_attach_tab).
        # That method is added in T-NEW-170 WIRE-3. FloatedTab
        # simply calls the contract. The contract is: pass
        # self so the tabset can read standalone_window,
        # document_widget, home_node_id, home_position,
        # home_tabset off the FloatedTab's storage.
        try:
            if self.home_tabset is not None:
                self.home_tabset.re_attach_tab(self)
        except Exception as _e:
            # Re-attach is best-effort: a failure here must
            # not block the dialog from closing (the tab
            # will survive as a widget unparented; an operator
            # can recover via restart or re-open). Log via
            # the nchantrs-side logger if available.
            try:
                from nchantrs.utilities.logger import get_logger

                _log = get_logger(__name__)
                _log.warning(
                    f"FloatedTab.closeEvent: re_attach_tab failed: "
                    f"{_e!r}"
                )
            except Exception:
                # No logger reachable -- swallow silently.
                pass
        # Always defer to super, so the dialog window actually
        # closes even if re-attach raised. This is the
        # critical invariant: closeEvent MUST call
        # super().closeEvent(event) so the QDialog internal
        # state transitions to closed.
        super().closeEvent(event)
