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
from nchantrs.libraries import pyqt

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.views.applicationviews import NchantdCloakView
from nchantdoffice.widgets.controls.toolbars import (
    NchantdNewDocumentToolBar,
)
from kahndor.logma import Logma
from typing import Self

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "views.yaml")


class NchantdOfficeCloakView(NchantdCloakView):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        logma.info(f"NchantdOfficeCloakView init: parent={type(parent).__name__}")
        super().__init__(parent, None)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeCloakView").override(cfg))
        # DESK T-NEW-050: wire the license-startup orchestrator.
        # Lazy-import + try/except so a missing aiohttp / license
        # module cannot block the desktop boot path. The
        # orchestrator itself swallows transient refresh failures
        # (so the desktop still boots when offline); this guard
        # only protects against the import + construction stage.
        try:
            from nchantdoffice.license.install_store import InstallStore
            from nchantdoffice.license.entitlement_cache import EntitlementCache
            from nchantdoffice.license.remote import LicenseRemote
            from nchantdoffice.license import startup_refresh
            from nchantdoffice.utilities import urls as _urls

            _install_store = InstallStore()
            _entitlement_cache = EntitlementCache()
            _remote = LicenseRemote(
                _install_store,
                _entitlement_cache,
                server_base_url=_urls.server_base_url(),
            )
            _prefs: dict = {}
            try:
                _parent_config = getattr(self.parent, "config", None)
                if _parent_config is not None:
                    _prefs = getattr(_parent_config, "dikt", {}).get(
                        "preferences", {}
                    ) or {}
            except Exception:
                _prefs = {}
            startup_refresh.refresh_if_needed(
                install_store=_install_store,
                entitlement_cache=_entitlement_cache,
                license_remote=_remote,
                preferences_db=_prefs,
            )
        except ImportError as exc:
            logma.warning(f"[views] license refresh unavailable: {exc}")

    def initView(self, cfg=None) -> Self:
        """T-NEW-159: restore splitter sizes after super().initView()
        builds the panes so the tree pane width survives a view rebuild."""
        super().init_pre_view(cfg)
        cfg = {}
        self.panes["toolbar"] = NchantdNewDocumentToolBar(self.parent, cfg).initWidget()
        super().initView(cfg)
        self._restore_splitter_sizes()
        # Wire splitterMoved -> save on first init only.  Defer with a
        # single-shot so the signal is set up after the splitter exists
        # (it is created by super().initView -> build_panes).
        pyqt.QTimer.singleShot(0, self._wire_splitter_save)
        return self

    def _wire_splitter_save(self) -> None:
        """Connect splitterMoved so user drags are persisted."""
        splitter = getattr(self, "splitter", None)
        if splitter is not None:
            try:
                splitter.splitterMoved.connect(self._save_splitter_sizes)
            except Exception:
                pass  # not a QSplitter or signal unavailable

    def _save_splitter_sizes(self) -> None:
        """T-NEW-159: persist splitter sizes to config whenever the user
        drags a pane divider.  Mirrors the ``last_selected_node`` pattern."""
        splitter = getattr(self, "splitter", None)
        if splitter is None:
            return
        try:
            sizes = splitter.sizes()
        except Exception:
            return
        if "preferences" not in self.config.dikt:
            self.config.dikt["preferences"] = {}
        self.config.dikt["preferences"]["splitter_sizes"] = sizes
        try:
            self.config.save()
        except Exception:
            pass  # config may not be writable (read-only env)

    def _restore_splitter_sizes(self) -> None:
        """T-NEW-159: restore splitter sizes from config after the panes
        are built.  Falls back to the hard-coded defaults silently."""
        splitter = getattr(self, "splitter", None)
        if splitter is None:
            return
        sizes = self.config.dikt.get("preferences", {}).get("splitter_sizes")
        if not sizes:
            return
        try:
            splitter.setSizes(list(sizes))
        except Exception:
            pass  # invalid sizes or splitter not ready yet

    def switch_to_account_tab(self) -> Self:
        """Switch the center tabset to the user's account tab.

        Sprint 20: previously a stub with a "PUSH to 0.0.3" marker
        that wasn't in the canonical PUSH list. Looks up the
        account tab via ``self.app.user`` (when present) and
        routes the center tabset to it. Falls back to no-op
        when the user or account tab isn't available.
        """
        try:
            user = getattr(self.app, "user", None)
            if user is None:
                return self
            # The account tab is identified by its ``name`` on the
            # user's tree (the Home / Settings / Account triad).
            # When the tab exists, switch to it; otherwise no-op.
            tab = getattr(user, "account_tab", None)
            if tab is None:
                tab = getattr(user, "settings_tab", None)
            if tab is None:
                return self
            center = self.panes.get("center")
            if center is None or not hasattr(center, "set_current_tab"):
                return self
            center.set_current_tab(tab)
        except Exception as exc:
            logma.warning(
                f"[views] switch_to_account_tab failed: {exc}",
                exc_info=True,
            )
        return self

    def on_window_move(self, event) -> Self:
        """Propagate a window-move event to visible notes.

        Sprint 20: previously a stub with a "PUSH to 0.0.3" marker
        that wasn't in the canonical PUSH list. The original
        intent (per the comment) was to move any visible notes
        at the same time as the main application. Iterates the
        center tabset's open tabs and forwards the event to
        any tab that exposes ``on_window_move``.
        """
        try:
            center = self.panes.get("center")
            if center is None:
                return self
            model = getattr(center, "model", None)
            tabs = getattr(model, "tabs", None) if model is not None else None
            if not tabs:
                return self
            for tab in tabs:
                forward = getattr(tab, "on_window_move", None)
                if callable(forward):
                    try:
                        forward(event)
                    except Exception as tab_exc:
                        logma.warning(
                            f"[views] on_window_move: tab "
                            f"{getattr(tab, 'name', '?')!r} "
                            f"forward failed: {tab_exc}"
                        )
        except Exception as exc:
            logma.warning(
                f"[views] on_window_move failed: {exc}",
                exc_info=True,
            )
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
