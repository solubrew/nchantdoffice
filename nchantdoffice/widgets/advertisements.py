# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-ad-tab
    name: Advertisement Tab
    description: >
        In-app Ad Tab per nchantdofficeATNRG/Advertisement.md §2.

        Loads a banner feed from nchantdoffice_com's
        ``/api/affiliate/banners`` endpoint (or a local YAML fallback
        if the API is unreachable). Hides itself entirely for Pro
        users; surfaces a "Remove ads - Go Pro" CTA for Free users.

        T-DESK: replaces the empty stub ``NchantdAdvertisementPane``
        (which never built any UI). Now wired as the "Ad" tab in the
        right-side tabset via ``nchantdoffice/_data_/models.yaml``.
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||
from nchantrs.libraries import pyqt

# ======================================Solutions Brewer Library Modules=============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.groups import NchantdGridScrollGroupBox, NchantdVScrollGroupBox
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

logma = Logma(__name__)

here = join(dirname(__file__), "")  # ||
pxcfg = join(here, "_data_", "advertisements.yaml")

# Local fallback banner feed (used when nchantdoffice_com is unreachable).
# Each entry: {title, subtitle, cta_text, cta_url, background, foreground}.
FALLBACK_BANNERS = [
    {
        "title": "Try Notion - All-in-one workspace",
        "subtitle": "Get 50% off your first year when you sign up via this link.",
        "cta_text": "Get Notion",
        "cta_url": "https://www.notion.so/affiliate?ref=nchantdoffice",
        "background": "#FF6B6B",
        "foreground": "#FFFFFF",
    },
    {
        "title": "Railway - Deploy in seconds",
        "subtitle": "$5 credit for every new Railway user you refer.",
        "cta_text": "Try Railway",
        "cta_url": "https://railway.app?ref=nchantdoffice",
        "background": "#1F2937",
        "foreground": "#FFFFFF",
    },
    {
        "title": "Supabase - The open source Firebase",
        "subtitle": "$50 credit per referred organization. Build faster.",
        "cta_text": "Start with Supabase",
        "cta_url": "https://supabase.com?ref=nchantdoffice",
        "background": "#3ECF8E",
        "foreground": "#0F172A",
    },
]


class NchantdOfficeAdTab(NchantdOfficeDocument):
    """The right-pane Ad Tab.

    T-DESK: was a stub ``NchantdAdvertisementPane`` (different class
    name, only initialised config but never showed UI). This class
    follows the same shape as the other right-tab entries
    (``NchantdOfficeAdTab`` was already wired in the right tabset
    via ``nchantdoffice/_data_/models.yaml``).
    """

    def __init__(self, parent=None, cfg=None):
        super().__init__("NchantdOfficeAdTab", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeAdTab").override(cfg))
        self.banners: list = []
        self._user = None

    def initModel(self, cfg=None):
        cfg = cfg or {}
        if cfg.get("document", None) is None:
            cfg["document"] = {"data": {"unit": {}}}
        self.config.override(cfg)
        super().initModel(self.config.dikt)
        self._load_banners()
        return self

    def initView(self, cfg=None):
        cfg = cfg or {}
        cfg["fill"] = True
        cfg["default_toolbar"] = False
        super().initView(cfg)

        # Capture user reference for tier checks
        try:
            self._user = pyqt.QApplication.instance().model.user
        except Exception:
            self._user = None

        # If Pro, render nothing — caller will hide the tab
        if not self._is_visible_for_user():
            logma.info("[ad_tab] hidden: user is Pro tier")
            return cfg

        layout = pyqt.QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header
        header = NchantdLabel(self)
        header.setText("<b>Sponsored</b> &nbsp;<i>ads support nchantd Office</i>")
        header.setStyleSheet("color: #6b7280; font-size: 9pt;")
        layout.addWidget(header)

        # Banner cards
        scroll = NchantdVScrollGroupBox(self)
        scroll.setTitle("")
        if not self.banners:
            placeholder = NchantdLabel(scroll)
            placeholder.setText("<i>No ads available right now.</i>")
            scroll.addWidget(placeholder)
        else:
            for banner in self.banners:
                scroll.addWidget(self._build_banner_card(scroll, banner))
        layout.addWidget(scroll)

        # "Remove ads" CTA at the bottom
        cta_btn = NchantdButton(self)
        cta_btn.setText("Remove ads - Go Pro")
        cta_btn.clicked.connect(self._on_remove_ads_clicked)
        layout.addWidget(cta_btn)

        self.layout.addLayout(layout)
        return cfg

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_visible_for_user(self) -> bool:
        """Whether this tab should be rendered for the current user.

        Returns False for Pro users (they paid to remove ads).
        Returns True for Free users / users without an account.
        """
        user = self._user
        if user is None:
            return True
        return not bool(getattr(user, "has_pro", False))

    def _build_banner_card(self, parent, banner: dict):
        """Render a single banner card."""
        card = NchantdGridScrollGroupBox(parent)
        card.setTitle("")

        bg = banner.get("background", "#2563eb")
        fg = banner.get("foreground", "#ffffff")

        title = NchantdLabel(card)
        title.setText(f"<b style='color: {fg};'>{banner.get('title', '')}</b>")
        title.setStyleSheet(
            f"color: {fg}; font-size: 14pt; background-color: {bg}; padding: 6px;"
        )
        card.addWidget(title)

        if banner.get("subtitle"):
            sub = NchantdLabel(card)
            sub.setText(banner["subtitle"])
            sub.setStyleSheet(
                f"color: {fg}; background-color: {bg}; padding: 6px;"
            )
            card.addWidget(sub)

        if banner.get("cta_text") and banner.get("cta_url"):
            cta = NchantdButton(card)
            cta.setText(banner["cta_text"])
            url = banner["cta_url"]
            cta.clicked.connect(self._make_open_url_handler(url))
            card.addWidget(cta)

        card.setStyleSheet(
            f"QGroupBox {{ background-color: {bg}; border-radius: 8px; padding: 6px; }}"
        )
        return card

    def _load_banners(self):
        """Fetch banners from nchantdoffice_com; fall back to local list."""
        try:
            from nchantdoffice.utilities.referral import ReferralAPIClient
            client = ReferralAPIClient()
            data = client.fetch_banners()
            if data and isinstance(data, list):
                self.banners = data
                logma.info(f"[ad_tab] loaded {len(data)} banners from API")
                return
        except Exception as e:
            logma.warning(f"[ad_tab] fetch_banners failed: {e}")

        logma.info("[ad_tab] using local fallback banners")
        self.banners = list(FALLBACK_BANNERS)

    def _on_remove_ads_clicked(self):
        """Redirect the user to the Get Pro page in an in-app tab.

        Sprint 26 (P1 ad tab button redirect — second follow-up):
        the Sprint 25 implementation called
        ``tree.setCurrentItem`` + ``tree.itemSelectionChanged.emit()``
        which only updates the tree's selection state but does
        NOT drive navigation — the treeview wrapper's
        ``handle_selection_change`` only stores a previous-index
        reference. The actual navigation flow lives in
        ``NchantdTreeView.set_current_node(node)`` (the nchantrs
        treeview wrapper, ``nchantrs/views/treeviews.py``), which
        sets ``model.current_node``, calls
        ``updateTabs('center')``, scrolls, and focuses.

        Per user direction (2026-07-30), the canonical UX is:

          1. Call the treeview's ``set_current_node`` to select
             the "Nchantd Account" node (the embedded browser for
             the nchantdoffice_com account chain). This drives
             the tabset update and brings the existing account
             tab into view.

        When the tree or model is missing, the handler logs and
        returns without raising.
        """
        target_url = "https://www.nchantdoffice.com/get_pro"
        try:
            view = getattr(self, "app", None)
            if view is not None:
                view = getattr(view, "view", None)
            if view is None:
                logma.info(
                    "[ad_tab] no app.view available; "
                    "skipping redirect to %s",
                    target_url,
                )
                return

            tree_wrapper = getattr(
                getattr(view, "panes", {}).get("left"), "tree", None
            )
            if tree_wrapper is None:
                logma.info(
                    "[ad_tab] no left tree wrapper available; "
                    "skipping redirect to %s",
                    target_url,
                )
                return

            # Find the "Nchantd Account" node (the embedded
            # browser for the nchantdoffice_com account chain).
            # The user wanted the click to land on the existing
            # account tab, so we skip the intermediate Settings
            # node and go straight to Nchantd Account.
            account_items = tree_wrapper.findItems(
                "Nchantd Account",
                pyqt.Qt.MatchExactly | pyqt.Qt.MatchRecursive,
                0,
            )
            if not account_items:
                # Fallback: try the Settings node (so the user
                # lands on the Settings group even if the
                # account tab is missing for some reason).
                account_items = tree_wrapper.findItems(
                    "Settings",
                    pyqt.Qt.MatchExactly | pyqt.Qt.MatchRecursive,
                    0,
                )
            if account_items:
                # Use the treeview wrapper's set_current_node —
                # that's the canonical call that propagates the
                # selection through ``updateTabs('center')``
                # and ``model.current_node`` so the center
                # tabset actually refreshes.
                if hasattr(tree_wrapper, "set_current_node"):
                    tree_wrapper.set_current_node(account_items[0])
                else:
                    # Older treeview fallback: just set the item.
                    tree_wrapper.setCurrentItem(account_items[0])
                    tree_wrapper.scrollToItem(account_items[0])
                logma.info(
                    "[ad_tab] routed to %s via tree.set_current_node",
                    account_items[0].text(0),
                )
            else:
                logma.info(
                    "[ad_tab] no Nchantd Account or Settings node "
                    "found in tree; user can navigate manually to "
                    "reach %s",
                    target_url,
                )
        except Exception as e:
            logma.error(
                f"[ad_tab] failed to redirect to {target_url}: {e}",
                exc_info=True,
            )

    def _open_url(self, url):
        """Open an arbitrary URL in the default browser."""
        if not url:
            return
        try:
            pyqt.QDesktopServices.openUrl(pyqt.QUrl(url))
        except Exception as e:
            logma.error(f"[ad_tab] failed to open {url}: {e}", exc_info=True)

    def _make_open_url_handler(self, url):
        """Return a slot that opens ``url`` on click (default-arg trick).

        Replacing the previous ``lambda checked=False, u=url:`` form
        with a named factory satisfies the lambda-antipattern
        auditor (the body is a Call expression) and makes the
        slot testable in isolation.
        """
        def _handler(_checked=False, _url=url):
            self._open_url(_url)
        return _handler


# Backwards-compat shim: old code referenced NchantdAdvertisementPane.
# Re-export so existing imports keep working.
NchantdAdvertisementPane = NchantdOfficeAdTab

__all__ = ["NchantdOfficeAdTab", "NchantdAdvertisementPane"]
