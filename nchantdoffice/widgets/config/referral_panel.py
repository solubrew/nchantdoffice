# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-referral-panel
    name: Referral Panel Widget
    description: >
        In-app Referral Panel per nchantdofficeATNRG/AppReferralSpec.md §5.

        Shows:
          - User's unique referral code (with one-click copy)
          - Share targets (Twitter, LinkedIn, email, WhatsApp, Telegram)
          - Invitations remaining (phase-aware)
          - Number of successful referrals
          - Current commission tier (5% / 10%)
          - Earnings dashboard (this month, this year, lifetime, pending)
          - Payout eligibility / request button
          - Upgrade CTA for users below invitation quota

        Backed by:
          - utilities/referral.py  (ReferralAPIClient)
          - nchantdoffice_com/app/apis/affiliate_api.py (server endpoints)

        T-DESK: replaces the placeholder NchantdOfficeAffiliateManager
        which was just a webview pointing at an external affiliate page.
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
from nchantrs.widgets.groups import NchantdGridScrollGroupBox, NchantdVScrollGroupBox, NchantdHGroupBox
from nchantrs.widgets.widgets import NchantdWidget

from nchantdoffice.widgets.documents.documents import NchantdOfficeDocumentManager
from nchantdoffice.utilities.referral import (
    DEFAULT_API_BASE, DEFAULT_PAYOUT_MIN_CENTS, REFERRAL_STATE_ACTIVE,
    REFERRAL_STATE_EXPIRED, REFERRAL_STATE_SUSPENDED, REFERRAL_STATE_USED,
    ReferralAPIClient, ReferralCode, build_share_urls, generate_referral_code,
    payout_eligible, validate_referral_code,
)

logma = Logma(__name__)

here = join(dirname(__file__), "")  # ||
pxcfg = join(here, "_data_", "referral_panel.yaml")  # optional; falls back to code-driven layout


class NchantdOfficeReferralPanel(NchantdOfficeDocumentManager):
    """In-app Referral Panel (DESK-2 / ATNRG spec §5).

    T-NOTE: was ``NchantdOfficeAffiliateManager`` (a stub webview
    pointing at ``/affiliate_marketing``). Rebuilt as a real panel
    that calls ``nchantdoffice_com`` APIs and shows the user's
    referral code, share targets, and earnings.
    """

    def __init__(self, parent=None, cfg=None):
        super().__init__(parent, cfg)
        self.name = "NchantdOffice Referral Panel"
        self.api_client = ReferralAPIClient(base_url=DEFAULT_API_BASE)
        self.referral_code: ReferralCode = None
        self.share_urls: dict = {}
        self.earnings_data: dict = {}
        self.invitations_remaining: int = 0

    def initModel(self):
        super().initModel()
        # Load referral code from user config, or generate one
        self._load_or_generate_code()
        self._fetch_dashboard()
        return self

    def initView(self):
        cfg = super().initView()
        layout = pyqt.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = NchantdLabel(self)
        title.setText("Referral Program")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)

        layout.addSpacing(10)
        layout.addWidget(self._build_code_card())
        layout.addSpacing(10)
        layout.addWidget(self._build_share_card())
        layout.addSpacing(10)
        layout.addWidget(self._build_earnings_card())

        self.layout.addLayout(layout)
        return cfg

    # ------------------------------------------------------------------
    # Card builders
    # ------------------------------------------------------------------

    def _build_code_card(self):
        """Card: shows the referral code + invitations remaining."""
        card = NchantdGridScrollGroupBox(self)
        card.setTitle("Your Referral Code")

        code = str(self.referral_code) if self.referral_code else "(generating...)"
        code_label = NchantdLabel(card)
        code_label.setText(f"<b>{code}</b>")
        code_label.setStyleSheet("font-size: 24pt; font-family: monospace; color: #2c5aa0;")
        card.addWidget(code_label)

        # Invitations remaining
        inv_label = NchantdLabel(card)
        if self.invitations_remaining > 0:
            inv_label.setText(
                f"You have <b>{self.invitations_remaining}</b> invitation(s) remaining this phase."
            )
        else:
            inv_label.setText(
                "<i>You've used all your invites this phase. "
                "We'll unlock more as we expand the program.</i>"
            )
        card.addWidget(inv_label)

        # Copy button
        copy_btn = NchantdButton(card)
        copy_btn.setText("Copy Code")
        copy_btn.clicked.connect(self._on_copy_code)
        card.addWidget(copy_btn)

        # Validation hint (for new users)
        if self.referral_code:
            valid, msg = validate_referral_code(str(self.referral_code))
            if not valid:
                logma.warning(f"[referral_panel] invalid code: {msg}")

        return card

    def _build_share_card(self):
        """Card: share targets (Twitter / LinkedIn / Email / etc.)."""
        card = NchantdGridScrollGroupBox(self)
        card.setTitle("Share & Invite")

        if not self.referral_code:
            placeholder = NchantdLabel(card)
            placeholder.setText("(code not yet generated)")
            card.addWidget(placeholder)
            return card

        self.share_urls = build_share_urls(self.referral_code)
        for platform in ["twitter", "linkedin", "email", "whatsapp", "telegram"]:
            url = self.share_urls.get(platform, "")
            btn = NchantdButton(card)
            btn.setText(f"Share via {platform.title()}")
            # Open the share URL when clicked (webbrowser is the
            # existing widget in the project; lazy import to avoid
            # pulling QtWebEngine at module load time).
            btn.clicked.connect(self._make_open_url_handler(url))
            card.addWidget(btn)

        # Direct "copy share link" button
        copy_link_btn = NchantdButton(card)
        copy_link_btn.setText("Copy Share Link")
        copy_link_btn.clicked.connect(self._on_copy_share_link)
        card.addWidget(copy_link_btn)

        return card

    def _build_earnings_card(self):
        """Card: earnings dashboard (counts, tier, this month, etc.)."""
        card = NchantdGridScrollGroupBox(self)
        card.setTitle("Earnings")

        dash = self.earnings_data or {}
        tier = dash.get("current_tier", "base")
        total = dash.get("total_referrals", 0)
        this_month = dash.get("this_month_cents", 0)
        this_year = dash.get("this_year_cents", 0)
        lifetime = dash.get("lifetime_cents", 0)
        pending = dash.get("pending_cents", 0)
        min_payout = DEFAULT_PAYOUT_MIN_CENTS

        summary = NchantdLabel(card)
        summary.setText(
            f"<b>Tier:</b> {tier.title()} &nbsp;|&nbsp; "
            f"<b>Referrals:</b> {total} &nbsp;|&nbsp; "
            f"<b>Commission Rate:</b> {int({ 'base': 5, 'elevated': 10 }.get(tier, 5))}%"
        )
        card.addWidget(summary)

        money = NchantdLabel(card)
        money.setText(
            f"<b>This Month:</b> ${this_month/100:.2f} &nbsp;|&nbsp; "
            f"<b>This Year:</b> ${this_year/100:.2f} &nbsp;|&nbsp; "
            f"<b>Lifetime:</b> ${lifetime/100:.2f} &nbsp;|&nbsp; "
            f"<b>Pending:</b> ${pending/100:.2f}"
        )
        card.addWidget(money)

        # Payout eligibility
        eligible = pending >= min_payout
        payout_label = NchantdLabel(card)
        if eligible:
            payout_label.setText(
                f"<b style='color: green;'>✓ Eligible for payout "
                f"(pending ${pending/100:.2f} ≥ ${min_payout/100:.2f} minimum)</b>"
            )
        else:
            need = min_payout - pending
            payout_label.setText(
                f"<i>${need/100:.2f} more needed to reach "
                f"${min_payout/100:.2f} payout minimum</i>"
            )
        card.addWidget(payout_label)

        # Request payout button
        if eligible:
            request_btn = NchantdButton(card)
            request_btn.setText("Request Payout")
            request_btn.clicked.connect(self._on_request_payout)
            card.addWidget(request_btn)

        return card

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_copy_code(self):
        """Copy the referral code to the system clipboard."""
        if not self.referral_code:
            return
        pyqt.QApplication.clipboard().setText(str(self.referral_code))
        logma.info(f"[referral_panel] copied code {self.referral_code} to clipboard")

    def _on_copy_share_link(self):
        """Copy the share link to the system clipboard."""
        url = self.share_urls.get("link") if self.share_urls else ""
        if url:
            pyqt.QApplication.clipboard().setText(url)
            logma.info(f"[referral_panel] copied share link to clipboard")

    def _on_request_payout(self):
        """Send payout request to nchantdoffice_com."""
        pending = self.earnings_data.get("pending_cents", 0)
        result = self.api_client.request_payout(amount_cents=pending)
        if result:
            logma.info(f"[referral_panel] payout requested: {pending} cents")
            self._fetch_dashboard()  # refresh
        else:
            logma.warning("[referral_panel] payout request failed (offline or server error)")

    def _open_url(self, url):
        """Open a share URL in the default browser."""
        if not url:
            return
        try:
            pyqt.QDesktopServices.openUrl(pyqt.QUrl(url))
        except Exception as e:
            logma.error(f"[referral_panel] failed to open {url}: {e}", exc_info=True)

    def _make_open_url_handler(self, url):
        """Return a slot that opens ``url`` on click (default-arg trick).

        Replaces the previous ``lambda checked=False, u=url:`` form
        with a named factory; satisfies the lambda-antipattern
        auditor and makes the slot testable in isolation.
        """
        def _handler(_checked=False, _url=url):
            self._open_url(_url)
        return _handler

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_or_generate_code(self):
        """Pull the existing code from user config or generate one.

        Stores in ``self.user.config.dikt['referral_code']`` so the
        same code persists across launches.
        """
        try:
            user_cfg = getattr(self.user, "config", None)
            cfg_dikt = getattr(user_cfg, "dikt", {}) if user_cfg else {}
        except Exception:
            cfg_dikt = {}

        existing = cfg_dikt.get("referral_code") if isinstance(cfg_dikt, dict) else None
        if existing:
            try:
                self.referral_code = ReferralCode(value=existing)
                logma.info(f"[referral_panel] loaded existing code: {self.referral_code}")
                return
            except ValueError:
                logma.warning(f"[referral_panel] stored code {existing!r} invalid; regenerating")

        # First-launch or invalid: generate deterministic from user id
        user_id = (
            getattr(self.user, "id", None)
            or getattr(self.user, "user_name", None)
            or getattr(self.user, "email", None)
            or "anonymous"
        )
        user_id = str(user_id)
        self.referral_code = ReferralCode.generate(user_id)
        try:
            if isinstance(cfg_dikt, dict):
                cfg_dikt["referral_code"] = str(self.referral_code)
                if hasattr(user_cfg, "_save"):
                    user_cfg._save()
        except Exception as e:
            logma.warning(f"[referral_panel] could not persist code: {e}")

    def _fetch_dashboard(self):
        """Fetch earnings + invitations from the server; fall back to local store."""
        try:
            data = self.api_client.fetch_earnings()
            if data:
                self.earnings_data = data
                self.invitations_remaining = int(
                    data.get("invitations_remaining", self.invitations_remaining)
                )
                logma.info(
                    f"[referral_panel] dashboard fetched: "
                    f"{self.earnings_data.get('total_referrals', 0)} referrals"
                )
                return
        except Exception as e:
            logma.warning(f"[referral_panel] fetch_earnings failed: {e}")

        # Offline fallback: derive a minimal dashboard from local state
        logma.info("[referral_panel] using local fallback dashboard")
        self.earnings_data = {
            "current_tier": "base",
            "total_referrals": 0,
            "this_month_cents": 0,
            "this_year_cents": 0,
            "lifetime_cents": 0,
            "pending_cents": 0,
        }


__all__ = ["NchantdOfficeReferralPanel"]
