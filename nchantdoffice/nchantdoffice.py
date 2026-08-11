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

# -*- coding: utf-8 -*
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

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
logma.info(f"here: {here}")
pxcfg = join(here, "_data_", "nchantdoffice.yaml")


class NchantdOfficeCloak(NchantdCloak):
    """"""

    def __init__(self, name, instance=None, parent=None, cfg=None, args=None):
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
        from pycurity.pyvice import Device
        self.device = Device()
        # T-NEW-042 (DESK-0): instantiate the user singleton so
        # self.user.uuid is the canonical per-install identifier
        # (replaces the previously-hardcoded application_NCD
        # constant). The UUID is loaded from user_config if
        # present, otherwise generated + persisted on first
        # launch — guaranteeing stability across launches.
        from nchantdoffice.utilities.users import NchantdOfficeUser
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

    def run_on_launch(self):
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

    def select_initial_node(self):
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

    def save_selected_node(self, node_id):
        """Save selected node to preferences."""
        if "preferences" not in self.config.dikt:
            self.config.dikt["preferences"] = {}
        self.config.dikt["preferences"]["last_selected_node"] = node_id
        # Persist to storage (config system handles this automatically)
        if hasattr(self.config, "save"):
            self.config.save()

    def _on_tree_selection_changed(self, selected, deselected):
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

    def __init__(self, parent=None, cfg=None):
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
                logma.warning(
                    f"[NchantdOfficeMainWindow] QSystemTrayIcon init failed: {e}"
                )

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def hideEvent(self, event):
        """ "" """
        super().hideEvent(event)

    def _populate_update_tray_menu(self, info):
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
            version_action = menu.addAction(
                f"New version available: {info.latest_version}"
            )
            version_action.setEnabled(False)  # label only
            if info.download_url:
                download_action = menu.addAction("Open download page")
                # Capture info.download_url for the lambda — avoid
                # the classic Python closure-over-loop-variable bug
                # by binding as default arg.
                download_action.triggered.connect(
                    lambda checked=False, url=info.download_url: self._open_url(url)
                )
            dismiss_action = menu.addAction(
                f"Dismiss for {DISMISS_DURATION_DAYS} days"
            )
            dismiss_action.triggered.connect(
                lambda checked=False, v=info.latest_version: dismiss_version(v)
            )
            self.tray_icon.setContextMenu(menu)
            self.tray_icon.show()
            self.tray_icon.showMessage(
                "NchantdOffice update available",
                f"Version {info.latest_version} is now available.",
                pyqt.QSystemTrayIcon.Information,
                5000,  # 5-second balloon
            )
            logma.info(
                f"[NchantdOfficeMainWindow] tray icon menu populated for "
                f"version {info.latest_version!r}."
            )
        except Exception as e:
            logma.warning(
                f"[NchantdOfficeMainWindow] _populate_update_tray_menu failed: {e}",
                exc_info=True,
            )

    def _open_url(self, url):
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


def run_update_process(dbupdate, update_checker, main_window=None):
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
            if (
                info.update_available
                and main_window is not None
                and hasattr(main_window, "_populate_update_tray_menu")
            ):
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
