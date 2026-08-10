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
        self.update_checker = UpdateChecker()
        self.application_NCD = "40c94efb-d374-437f-a48b-3c6b843fd110"
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
        run_update_process(
            dbupdate=self.dbupdate,
            update_checker=self.update_checker,
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


# ====================================================================================================================||
# T-NEW-058 — module-level helper for the boot-hook logic.
# ====================================================================================================================||


def run_update_process(dbupdate, update_checker):
    """T-NEW-058: run the two update-process entry points at boot.

    Extracted from ``NchantdOfficeCloak.run_on_launch`` so that
    tests can exercise the logic without instantiating the full
    Qt-singleton ``NchantdOfficeCloak`` (shiboken enforces
    single-instance, which breaks multi-test execution).

    The function is intentionally permissive — neither the schema
    upgrade nor the network check should ever block app startup.
    Failures are logged and swallowed.

    Parameters
    ----------
    dbupdate : NchantdOfficeDBUpdate
        The Pyffice schema upgrade object. ``update_pyffice_document()``
        is guarded by ``_upgrade_lock`` so double-invocation is a no-op.
    update_checker : UpdateChecker
        The app-version update checker. ``check()`` polls the server
        and caches the response; ``None`` return means the server was
        unreachable AND no fresh cache exists.

    Returns
    -------
    dict
        Summary of what ran: ``{"upgrade_run": bool, "checker_info":
        Optional[UpdateInfo]}``. Useful for tests and for the
        future T-NEW-060 tray icon.
    """
    summary = {"upgrade_run": False, "checker_info": None}

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
    except Exception as e:
        logma.warning(
            f"[run_update_process] update_checker.check() failed: {e}",
            exc_info=True,
        )

    return summary


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
