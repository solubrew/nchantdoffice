# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name:
    description: >
    version: 0.0.0.0.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""

# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Self

# ======================================Standard Library Modules======================================================||
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.widgets.applications.applications import NchantdCloak, NchantdMainWindow
from nchantdoffice.models import NchantdOfficeCloakModel
from nchantdoffice.views import NchantdOfficeCloakView
from nchantdoffice.updates.db import NchantdOfficeDBUpdate
from nchantdoffice.updates.checker import UpdateChecker
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from pycurity.pyvice import Device
from nchantdoffice.utilities.users import NchantdOfficeUser

# T-NEW-169 WIRE-3: the 4 high-value NchantdOffice* document
# classes are imported lazily inside
# NchantdDocumentStandaloneWindow.initView (rather than at
# module load) because importing some of them (e.g.
# NchantdOfficeForm via forms.py) drags in the full app
# module graph (Qt + paths + sibling tests). The dispatch
# is read late -- at the standalone-boot site -- so the
# import work happens once per standalone launch, not at
# module-import time. This keeps the test environment
# (and any non-app context that imports nchantdoffice.py)
# free of the heavyweight transitive imports.
_DOC_TYPE_DISPATCH_BY_NAME: dict[str, str] = {
    "script": "nchantdoffice.widgets.documents.media.scripts.NchantdOfficeScript",
    "notebook": "nchantdoffice.widgets.documents.workbooks.notebooks.NchantdOfficeNotebook",
    "image": "nchantdoffice.widgets.documents.media.images.NchantdOfficeImage",
    "form": "nchantdoffice.widgets.documents.media.forms.NchantdOfficeForm",
}

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
logma.info(f"here: {here}")
pxcfg = join(here, "_data_", "nchantdoffice.yaml")


class NchantdOfficeCloak(NchantdCloak):
    """"""

    def __init__(self, name, instance=None, parent=None, cfg=None, args=None) -> None:
        """ """
        super().__init__(name, instance, parent, None, args)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeCloak").override(cfg))
        self.config.override({"app": "nchantdoffice"})
        self.parent = parent
        logma.info(f"NchantdOfficeCloak: {self.config.dikt.get('config', None)}")
        if self.parent is None:
            self.parent = self
        self.main = NchantdOfficeMainWindow(self)
        self.model = NchantdOfficeCloakModel(name, self.instance, self)
        self.view = NchantdOfficeCloakView(self)
        self.dbupdate = NchantdOfficeDBUpdate(self)
        # T-NEW-058 §1.2/§2 — construct the UpdateChecker at boot
        # so the boot hook (run_on_launch) can invoke check() without
        # importing the class there. The instance is caller-driven;
        # the class itself does not start a background thread.
        # T-NEW-059: pass self.config.dikt so UpdateChecker.check()
        # honours the user's check_update_interval_hours override
        # (Interface Tab settings → "Update check interval (hours)").
        self.update_checker = UpdateChecker(cfg=self.config.dikt)
        # T-NEW-042b: NchantdUser.__init__ (parent) reads
        # self.parent.device.user at line 65. Set self.device
        # BEFORE constructing NchantdOfficeUser(self) so the
        # parent class has access to it. Real-world crash
        # reported 2026-08-11 14:21:27:
        #   AttributeError: 'NchantdOfficeCloak' object has no
        #   attribute 'device'
        self.device = Device()
        # T-NEW-042 (DESK-0): instantiate the user singleton so
        # self.user.uuid is the canonical per-install identifier
        # (replaces the previously-hardcoded application_NCD
        # constant). The UUID is loaded from user_config if
        # present, otherwise generated + persisted on first
        # launch — guaranteeing stability across launches.
        self.user = NchantdOfficeUser(self)
        self.user.persist_uuid()
        self.application_NCD = self.user.uuid
        self.install = True
        self.primary_focus = "office_platform"
        self.is_installable = True
        self.is_install_optional = False
        self.has_comms = True
        self.has_library = True
        self.library_optional = True
        self.toolbox = None

    def run_on_launch(self) -> Self:
        """Called on every application startup.

        T-NEW-058: in addition to the inherited base-class work,
        this method now invokes the two update-process entry points
        that the review doc (docs/update-process-review_20260810.md)
        §1.2 identified as dead-code at the call layer:

          1. ``self.dbupdate.update_pyffice_document()`` — runs the
             Pyffice schema upgrade. The call is guarded by the
             ``_upgrade_lock`` flag inside ``NchantdOfficeDBUpdate``,
             so a second invocation in the same process is a no-op.

          2. ``self.update_checker.check()`` — polls the server for
             new releases. Result is logged; tray-icon wiring lives
             in T-NEW-060.

        Both calls are wrapped in try/except so a network or
        migration failure does NOT block application startup —
        the user's app comes up regardless. The exception is logged
        so the operator can see it.
        """
        super().run_on_launch()
        self.model.set_today()
        # T-NEW-129: seed the ``app_user`` row on first install.
        # Idempotent: a no-op once the row exists, so safe to
        # call every launch. Wrapped in try/except inside the
        # method itself -- a missing store or table never blocks
        # app boot.
        try:
            self.model.bootstrap_app_user()
        except Exception as e:
            logma.warning(f"[nchantdoffice] run_on_launch: " f"bootstrap_app_user raised: {e}")
        # Restore last selected node or default to Home
        self.select_initial_node()
        # T-NEW-058 §2.4 — delegate to the testable module-level
        # helper. Tests in tests/test_update_checker_boot_hook.py
        # call run_update_process() directly so they don't need to
        # instantiate the full NchantdOfficeCloak (which is a Qt
        # singleton).
        # T-NEW-060: pass self.main so the tray icon can be
        # populated when an update-available response comes back.
        run_update_process(
            dbupdate=self.dbupdate,
            update_checker=self.update_checker,
            main_window=self.main,
        )
        return self

    def cmd_save(self) -> None:
        """T-NEW-145: Ctrl+S dispatch.

        Overrides ``NchantdCloak.cmd_save`` (which calls
        ``self.parent.model.save()`` — application-level instance
        write). The user expects Ctrl+S to behave like the
        document toolbar save button (``cmd_save_tab`` -> ``self.save()``),
        not the app-instance save.

        Resolution order:
          1. Look up the active document via
             ``self.main.view.panes["center"].currentWidget()``.
          2. If found, call its ``save()`` (and ``save_app()`` when
             the doc is an app_media document — same routing as
             ``NchantdOfficeDocumentMixin.save``).
          3. Fall back to ``self.parent.model.save()`` when no
             active document exists or the lookup chain raises
             (defensive: missing view / panes / currentWidget).
        """
        active_doc = None
        try:
            view = getattr(getattr(self, "main", None), "view", None)
            panes = getattr(view, "panes", {}) or {}
            center = panes.get("center")
            active_doc = center.currentWidget() if center is not None else None
        except Exception as exc:
            logma.warning(
                f"[nchantdoffice] cmd_save: active-document lookup " f"failed: {exc}; falling back to model.save()"
            )
        if active_doc is not None:
            try:
                # Mirror cmd_save_tab: call save() (and save_app()
                # when present) so app_media docs persist through
                # the app_doc_content / app_media_content path.
                if hasattr(active_doc, "save") and callable(active_doc.save):
                    active_doc.save()
                if hasattr(active_doc, "save_app") and callable(active_doc.save_app):
                    active_doc.save_app()
                return
            except Exception as exc:
                logma.warning(
                    f"[nchantdoffice] cmd_save: active document save " f"raised: {exc}; falling back to model.save()"
                )
        # No active document (or its save raised): preserve the
        # inherited app-instance save behaviour so the application
        # state still persists when no tab is focused.
        self.parent.model.save()

    def select_initial_node(self) -> None:
        """Restore last selected node on successive runs, fallback to Home."""
        # Get last selected node from preferences
        last_selected_id = self.config.dikt.get("preferences", {}).get("last_selected_node")

        # Find the tree widget
        tree = None
        if hasattr(self.main, "application_tree"):
            tree = self.main.application_tree.tree if hasattr(self.main.application_tree, "tree") else None

        if tree and hasattr(tree, "findItems"):
            # Try to restore last selected node
            if last_selected_id:
                items = tree.findItems(last_selected_id, pyqt.Qt.MatchExactly | pyqt.Qt.MatchRecursive, 0)
                if items:
                    tree.setCurrentItem(items[0])
                    return

            # Fallback to Home node
            home_items = tree.findItems("Home", pyqt.Qt.MatchExactly, 0)
            if home_items:
                tree.setCurrentItem(home_items[0])

    def save_selected_node(self, node_id) -> None:
        """Save selected node to preferences."""
        if "preferences" not in self.config.dikt:
            self.config.dikt["preferences"] = {}
        self.config.dikt["preferences"]["last_selected_node"] = node_id
        # Persist to storage (config system handles this automatically)
        if hasattr(self.config, "save"):
            self.config.save()

    def _on_tree_selection_changed(self, selected, deselected) -> None:
        """Handle tree selection change - save to preferences."""
        # Get selected node ID from selection model
        indexes = selected.indexes() if selected else []
        if indexes:
            # Get the node ID from the model
            node_id = indexes[0].data(pyqt.Qt.UserRole)
            if node_id:
                self.save_selected_node(node_id)


class NchantdOfficeMainWindow(NchantdMainWindow):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        logma.info(f"NchantdOfficeMainWindow init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeMainWindow").override(cfg))
        # T-NEW-060 — QSystemTrayIcon for update notifications.
        # The icon is created in __init__ (cheap; no menu yet) so
        # that callers can wire menu actions later without re-checking
        # ``QSystemTrayIcon.isSystemTrayAvailable()``. The tray is
        # populated when UpdateChecker.check() returns an
        # update-available response — see
        # ``_populate_update_tray_menu()``.
        self.tray_icon = None
        if pyqt is not None and hasattr(pyqt, "QSystemTrayIcon"):
            try:
                self.tray_icon = pyqt.QSystemTrayIcon(self)
            except Exception as e:
                logma.warning(f"[NchantdOfficeMainWindow] QSystemTrayIcon init failed: {e}")

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> Self:
        """"""
        super().initView(cfg)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def hideEvent(self, event) -> None:
        """ " """
        super().hideEvent(event)

    def _populate_update_tray_menu(self, info) -> None:
        """T-NEW-060: populate the tray icon menu with the latest
        update notification + dismiss action.

        Wired from ``run_update_process()`` when
        ``UpdateChecker.check()`` returns an ``UpdateInfo`` with
        ``update_available=True`` AND ``is_dismissed(latest_version)``
        is False. The dismiss action calls
        ``dismiss_version(latest_version, days=DISMISS_DURATION_DAYS)``
        which writes the snooze to ``~/.nchantd/state.yaml``.

        No-op when the tray icon is unavailable (no system tray in
        the user's environment) or when the version is already
        dismissed.

        Parameters
        ----------
        info : UpdateInfo
            The result of ``UpdateChecker.check()``. Only
            ``latest_version`` and ``download_url`` are read here.
        """
        if self.tray_icon is None:
            return
        # Lazy imports — keep the module surface small when the
        # system tray is unavailable (e.g. headless venv tests).
        try:
            from nchantdoffice.updates.checker import (
                DISMISS_DURATION_DAYS,
                dismiss_version,
                is_dismissed,
            )
        except Exception:
            return
        if info is None or not info.latest_version:
            return
        if is_dismissed(info.latest_version):
            logma.info(
                f"[NchantdOfficeMainWindow] _populate_update_tray_menu: "
                f"version {info.latest_version!r} is dismissed; skipping."
            )
            return
        try:
            menu = pyqt.QMenu()
            version_action = menu.addAction(f"New version available: {info.latest_version}")
            version_action.setEnabled(False)  # label only
            if info.download_url:
                download_action = menu.addAction("Open download page")
                # Capture info.download_url for the lambda — avoid
                # the classic Python closure-over-loop-variable bug
                # by binding as default arg.
                download_action.triggered.connect(lambda checked=False, url=info.download_url: self._open_url(url))
            dismiss_action = menu.addAction(f"Dismiss for {DISMISS_DURATION_DAYS} days")
            dismiss_action.triggered.connect(lambda checked=False, v=info.latest_version: dismiss_version(v))
            self.tray_icon.setContextMenu(menu)
            self.tray_icon.show()
            self.tray_icon.showMessage(
                "NchantdOffice update available",
                f"Version {info.latest_version} is now available.",
                pyqt.QSystemTrayIcon.Information,
                5000,  # 5-second balloon
            )
            logma.info(f"[NchantdOfficeMainWindow] tray icon menu populated for " f"version {info.latest_version!r}.")
        except Exception as e:
            logma.warning(
                f"[NchantdOfficeMainWindow] _populate_update_tray_menu failed: {e}",
                exc_info=True,
            )

    def _open_url(self, url) -> None:
        """Open ``url`` in the user's default browser (T-NEW-060).

        Uses ``QDesktopServices.openUrl`` when available; falls
        back to ``webbrowser.open`` when Qt's helper raises.
        """
        if not url:
            return
        try:
            if hasattr(pyqt, "QDesktopServices") and hasattr(pyqt, "QUrl"):
                pyqt.QDesktopServices.openUrl(pyqt.QUrl(url))
                return
        except Exception as e:
            logma.warning(f"[NchantdOfficeMainWindow] QDesktopServices failed: {e}")
        try:
            import webbrowser

            webbrowser.open(url)
        except Exception as e:
            logma.warning(f"[NchantdOfficeMainWindow] webbrowser.open failed: {e}")


# ====================================================================================================================||
# T-NEW-058 — module-level helper for the boot-hook logic.
# ====================================================================================================================||


def run_update_process(dbupdate, update_checker, main_window=None) -> dict:
    """T-NEW-058: run the two update-process entry points at boot.

    Extracted from ``NchantdOfficeCloak.run_on_launch`` so that
    tests can exercise the logic without instantiating the full
    Qt-singleton ``NchantdOfficeCloak`` (shiboken enforces
    single-instance, which breaks multi-test execution).

    The function is intentionally permissive — neither the schema
    upgrade nor the network check should ever block app startup.
    Failures are logged and swallowed.

    T-NEW-060: when ``main_window`` is provided AND the checker
    returns a non-dismissed update-available ``UpdateInfo``, the
    tray icon menu is populated. The ``main_window`` argument is
    optional so test scenarios can pass ``None`` (no tray
    available) and still exercise the rest of the flow.

    Parameters
    ----------
    dbupdate : NchantdOfficeDBUpdate
        The Pyffice schema upgrade object. ``update_pyffice_document()``
        is guarded by ``_upgrade_lock`` so double-invocation is a no-op.
    update_checker : UpdateChecker
        The app-version update checker. ``check()`` polls the server
        and caches the response; ``None`` return means the server was
        unreachable AND no fresh cache exists.
    main_window : NchantdOfficeMainWindow, optional
        The main window whose tray icon to populate when a new
        version is available. Defaults to None (no tray wiring).

    Returns
    -------
    dict
        Summary of what ran: ``{"upgrade_run": bool, "checker_info":
        Optional[UpdateInfo], "tray_populated": bool}``. Useful for
        tests and for future debugging tools.
    """
    summary = {"upgrade_run": False, "checker_info": None, "tray_populated": False}

    # Schema upgrade — guarded by _upgrade_lock inside
    # NchantdOfficeDBUpdate so a double-invocation is harmless.
    try:
        # Snapshot the lock state before so we can record whether
        # THIS call actually ran the migration or was a no-op.
        already_locked = getattr(dbupdate, "_upgrade_lock", False)
        dbupdate.update_pyffice_document()
        summary["upgrade_run"] = not already_locked
    except Exception as e:
        logma.warning(
            f"[run_update_process] update_pyffice_document failed: {e}",
            exc_info=True,
        )

    # App-version check — best-effort network call.
    try:
        info = update_checker.check()
        summary["checker_info"] = info
        if info is not None:
            logma.info(
                f"[run_update_process] UpdateChecker result "
                f"latest_version={info.latest_version!r} "
                f"update_available={info.update_available!r}"
            )
            # T-NEW-060: populate the tray icon menu when an
            # update is available AND the user hasn't dismissed it.
            if info.update_available and main_window is not None and hasattr(main_window, "_populate_update_tray_menu"):
                try:
                    main_window._populate_update_tray_menu(info)
                    summary["tray_populated"] = True
                except Exception as e:
                    logma.warning(
                        f"[run_update_process] tray icon population failed: {e}",
                        exc_info=True,
                    )
    except Exception as e:
        logma.warning(
            f"[run_update_process] update_checker.check() failed: {e}",
            exc_info=True,
        )

    return summary


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||

# ======================================T-NEW-169 WIRE-2===============================================================|

# T-NEW-169 (DESK / 2026-08-19): NchantdDocumentStandaloneWindow.
# LOCKED DESIGN (operator-approved 2026-08-19):
#   DECIDE-1 (a) -- argparse subcommand
#   DECIDE-2 (ii) -- full standalone 2-pane shell (this class)
#   DECIDE-DOCK -- right-side dock for the toolbox
#
# The class lives in nchantdoffice/nchantdoffice.py (next to
# NchantdOfficeCloak + NchantdOfficeMainWindow) so future
# dispatch wiring in cmds/runNchantdOffice.py can resolve
# `nchantdoffice.nchantdoffice.NchantdDocumentStandaloneWindow`
# without a fresh import path.


# T-NEW-169 WIRE-3: 4 high-value document types wired into
# the dispatch dict. The dict's values are dotted import
# paths (strings) rather than the concrete classes because
# importing some of the NchantdOffice* widgets at module
# load time pulls in the full app module graph (Qt,
# paths, sibling tests). Lazy lookup happens inside
# NchantdDocumentStandaloneWindow.initView via importlib.
DOCUMENT_TYPE_DISPATCH: dict[str, str] = {
    "script": "nchantdoffice.widgets.documents.media.scripts.NchantdOfficeScript",
    "notebook": "nchantdoffice.widgets.documents.workbooks.notebooks.NchantdOfficeNotebook",
    "image": "nchantdoffice.widgets.documents.media.images.NchantdOfficeImage",
    "form": "nchantdoffice.widgets.documents.media.forms.NchantdOfficeForm",
}


class NchantdDocumentStandaloneWindow(pyqt.QMainWindow):
    """T-NEW-169 WIRE-2 -- standalone 2-pane minimal shell.

    Hosts ONE document on the left (the central widget) and a
    right-side dock for the matching toolbox. Sized to a
    usable default (1280x800) since this shell is intended for
    operator-driven per-document workflows on a single screen
    or a focused second monitor.

    Lifecycle (mirrors NchantdOfficeMainWindow):

        standalone = NchantdDocumentStandaloneWindow(
            parent=None,
            document_type="script",
            preload_path=None,
        )
        standalone.initWidget()    # initModel -> initView
        standalone.show()          # QMainWindow standard

    The constructor does NOT launch Qt -- it's safe to call
    inside a test that has only the QApplication set up via
    the shieldface conftest. `show()` is what triggers the
    display; construction is pure attribute binding.

    T-NEW-170 reuse: T-NEW-170's `FloatedTab` class accepts
    a `NchantdDocumentStandaloneWindow` instance as the
    `standalone_window` parameter (per its construction
    contract committed at T-NEW-170 WIRE-1). The standalone
    shell that lives in a pulled-out dialog IS this class.
    """

    def __init__(
        self,
        parent: Any = None,
        document_type: str = "script",
        preload_path: str | None = None,
    ) -> None:
        """Build the standalone shell; do NOT show it.

        Args:
            parent: optional parent widget (typically None for
                top-level windows).
            document_type: one of the keys in
                DOCUMENT_TYPE_DISPATCH (`script`, `notebook`,
                `image`, `form`). The actual document-widget
                instantiation lands in WIRE-3 via the dispatch
                dict. For WIRE-2 the value is stored verbatim
                so initView can branch on it.
            preload_path: optional path to preload on first
                document open. WIRE-2 only stores the value;
                WIRE-3 opens the document via
                `dispatch[document_type].open(preload_path)`.
        """
        super().__init__(parent)
        self.document_type = document_type
        self.preload_path = preload_path
        self._document_widget = None
        self._toolbox_dock = None

        # T-NEW-169 WIRE-2: window title shows the dispatched
        # doc type so operators running multiple standalone
        # windows have a recognizable title bar.
        self.setWindowTitle(f"Standalone {document_type} document")

    def initWidget(self) -> Self:
        """initWidget -- the nchantrs lifecycle bridge.

        Per the project's convention, initWidget chains
        initModel + initView. For the standalone shell the
        initModel step is a no-op (no model -- the document
        manages its own state); the initView step is where
        the central widget + dock layout comes together.
        """
        self.initView()
        return self

    def initView(self) -> Self:
        """initView -- wire the central widget and right dock.

        The 2-pane layout per DECIDE-2 (b):

            +------------------------------------------+
            |        document (central widget)          |
            |                                          |
            |     (left pane, fills via doc_widget)     |
            |                                          |
            +------------------------------------------+

        The right-side toolbox is mounted via
        `addDockWidget(Qt.RightDockWidgetArea, dock)`. WIRE-3
        swaps in the matching toolbox class per
        `document_type`; for WIRE-2 the dock holds a
        placeholder QDockWidget so the layout geometry is
        correct and the operator can drop the docked pane
        anywhere as expected.
        """
        # T-NEW-169 WIRE-3: dispatch-driven construction. The
        # placeholder central widget from WIRE-2 is replaced
        # with a real document widget constructed via
        # DOCUMENT_TYPE_DISPATCH. The dispatch values are
        # dotted import paths (strings); we resolve them
        # lazily via importlib so the heavyweight
        # NchantdOffice* transitive imports only fire on a
        # real standalone boot, not on every nchantdoffice.py
        # import.
        import importlib
        doc_path = DOCUMENT_TYPE_DISPATCH.get(self.document_type)
        doc_cls = None
        if doc_path is not None:
            try:
                _module_path, _, _class_name = doc_path.rpartition(".")
                _mod = importlib.import_module(_module_path)
                doc_cls = getattr(_mod, _class_name)
            except Exception as _import_err:
                logma.warning(
                    f"[NchantdDocumentStandaloneWindow] "
                    f"{self.document_type} -> {doc_path} "
                    f"failed to import: {_import_err!r}; "
                    f"falling back to placeholder"
                )
        if doc_cls is not None:
            try:
                document_widget = doc_cls(parent=self)
                self._document_widget = document_widget
                # Run the nchantrs lifecycle hooks if available
                # -- the 4 NchantdOffice* classes all expose
                # initModel / initView (the convention) but
                # new ones might not, so `hasattr` guards the
                # sequence.
                if hasattr(document_widget, "initModel"):
                    try:
                        document_widget.initModel()
                    except Exception as _m_err:
                        logma.warning(
                            f"[NchantdDocumentStandaloneWindow] "
                            f"{doc_cls.__name__}.initModel raised: {_m_err!r}"
                        )
                if hasattr(document_widget, "initView"):
                    try:
                        document_widget.initView()
                    except Exception as _v_err:
                        logma.warning(
                            f"[NchantdDocumentStandaloneWindow] "
                            f"{doc_cls.__name__}.initView raised: {_v_err!r}"
                        )
                self.setCentralWidget(document_widget)
                # If a preload_path was passed and the constructed
                # class has an open_file method, thread it through.
                # Tolerant best-effort -- open_file is the canonical
                # entry point across the 4 NchantdOffice* classes
                # but errors are caught so a bad preload path
                # doesn't crash the standalone boot.
                if self.preload_path is not None and hasattr(
                    document_widget, "open_file"
                ):
                    try:
                        document_widget.open_file(self.preload_path)
                    except Exception as _open_err:
                        logma.warning(
                            f"[NchantdDocumentStandaloneWindow] "
                            f"preload open_file failed: {_open_err!r}"
                        )
            except Exception as _ctor_err:
                logma.warning(
                    f"[NchantdDocumentStandaloneWindow] "
                    f"{self.document_type} dispatch -> "
                    f"{doc_cls.__name__} construction failed: "
                    f"{_ctor_err!r}; "
                    f"falling back to placeholder"
                )
                document_widget = None
        else:
            document_widget = None

        # If dispatch failed OR the constructor failed, fall
        # back to the WIRE-2 placeholder central widget so
        # the QMainWindow still has SOMETHING to render.
        if document_widget is None:
            placeholder_central = pyqt.QWidget(self)
            placeholder_layout = pyqt.QVBoxLayout(placeholder_central)
            placeholder_layout.setContentsMargins(8, 8, 8, 8)
            placeholder_label = pyqt.QLabel(
                f"[WIRE-2] {self.document_type} standalone shell \u2014 "
                f"document widget lands in T-NEW-169 WIRE-3"
            )
            placeholder_label.setWordWrap(True)
            placeholder_layout.addWidget(placeholder_label)
            self.setCentralWidget(placeholder_central)

        # T-NEW-169 WIRE-2: dock placeholder. The right-dock
        # is where the toolbox lives once a future card wires
        # the per-document toolbox class (per
        # DOCUMENT_TYPE_DISPATCH keys). Until then the dock
        # holds a placeholder widget so the layout geometry
        # is correct and the operator can move/dock the pane.
        placeholder_dock = pyqt.QDockWidget(
            f"{self.document_type} toolbox (WIRE-2 placeholder)",
            self,
        )
        placeholder_dock.setObjectName(
            f"{self.document_type}ToolboxDock"
        )
        placeholder_dock_inner = pyqt.QWidget(placeholder_dock)
        placeholder_dock_layout = pyqt.QVBoxLayout(placeholder_dock_inner)
        placeholder_dock_label = pyqt.QLabel(
            "[WIRE-2] Right-dock placeholder \u2014 toolbox lands "
            "in a future toolbox-card per T-NEW-169 plan"
        )
        placeholder_dock_label.setWordWrap(True)
        placeholder_dock_layout.addWidget(placeholder_dock_label)
        placeholder_dock.setWidget(placeholder_dock_inner)
        self.addDockWidget(
            pyqt.Qt.RightDockWidgetArea, placeholder_dock
        )
        self._toolbox_dock = placeholder_dock

        self.resize(1280, 800)
        return self


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
