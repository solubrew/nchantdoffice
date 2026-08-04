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
from nchantrs.widgets.groups import NchantdGridScrollGroupBox, NchantdGroup
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantdoffice.utilities.referral import (
    DEFAULT_API_BASE,
    DEFAULT_PAYOUT_MIN_CENTS,
    REFERRAL_STATE_ACTIVE,
    REFERRAL_STATE_EXPIRED,
    REFERRAL_STATE_SUSPENDED,
    REFERRAL_STATE_USED,
    ReferralAPIClient,
    ReferralCode,
    build_share_urls,
    generate_referral_code,
    payout_eligible,
    validate_referral_code,
)

logma = Logma(__name__)

here = join(dirname(__file__), "")  # ||
pxcfg = join(here, "_data_", "referral_panel.yaml")  # optional; falls back to code-driven layout


class NchantdOfficeReferralPanel(NchantdOfficeDocument):
    """In-app Referral Panel (DESK-2 / ATNRG spec §5).

    T-NOTE: was ``NchantdOfficeAffiliateManager`` (a stub webview
    pointing at ``/affiliate_marketing``). Rebuilt as a real panel
    that calls ``nchantdoffice_com`` APIs and shows the user's
    referral code, share targets, and earnings.
    """

    def __init__(self, parent=None, cfg=None, user=None):
        """T-NEW-019 (live crash): ``_load_or_generate_code``
        read ``self.user.id`` which raised ``AttributeError`` on
        the Referral tab init chain. The init signature now
        accepts an optional ``user`` (None when the host
        doesn't inject one), and ``_load_or_generate_code``
        falls back to ``"anonymous"`` in that case.
        """
        self.name = "NchantdOffice Referral Panel"
        super().__init__(self.name, parent, cfg)
        self.api_client = ReferralAPIClient(base_url=DEFAULT_API_BASE)
        self.user = user
        self.referral_code: ReferralCode = None
        self.share_urls: dict = {}
        self.earnings_data: dict = {}
        self.invitations_remaining: int = 0

    def initModel(self):
        """"""
        super().initModel()
        document = {"document": self.config.get("document", {})}
        logma.info(f"Document {document}")
        # Load referral code from user config, or generate one
        self.document = self.app.model.codex.init_config(document)
        self.document.load_document()
        self._load_or_generate_code()  # TODO: must always load from external source
        self._fetch_dashboard()
        return self

    def initView(self, cfg=None):
        """"""
        cfg = cfg or {}
        super().initView(cfg)
        layout = pyqt.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        # Title
        cfg = {}
        title = NchantdLabel(self, cfg).initWidget()
        title.setText("Referral Program")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)
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
        card = NchantdGroup(self)
        layout = pyqt.QVBoxLayout()
        card.setLayout(layout)
        card.setTitle("Your Referral Code")

        code = str(self.referral_code) if self.referral_code else "(generating...)"
        code_label = NchantdLabel(card)
        code_label.setText(f"<b>{code}</b>")
        code_label.setStyleSheet("font-size: 24pt; font-family: monospace; color: #2c5aa0;")
        card.addWidget(code_label)

        # Invitations remaining
        inv_label = NchantdLabel(card)
        if self.invitations_remaining > 0:
            inv_label.setText(f"You have <b>{self.invitations_remaining}</b> invitation(s) remaining this phase.")
        else:
            inv_label.setText(
                "<i>You've used all your invites this phase. " "We'll unlock more as we expand the program.</i>"
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
                f"<i>${need/100:.2f} more needed to reach " f"${min_payout/100:.2f} payout minimum</i>"
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
        # T-NEW-019 (live crash): guard the self.user access so the
        # Referral tab doesn't AttributeError when the panel is
        # opened without a User instance injected by the host.
        # T-NEW-026 (close-out step 2): prefer the affiliate id
        # stored in pycurity.PyKeyStore over the user-id / "anonymous"
        # fallback chain. The keystore value is set by the user's
        # Affiliate Manager tab (write_api_caller) and survives
        # across the user's sessions (vs. the user-id based code,
        # which changes when the user record changes).
        user_obj = getattr(self, "user", None)
        try:
            # T-NEW-026: use the canonical pycurity.pykey.PyKeyStore
            # import path (matches the rest of the project).
            from pycurity.pykey import PyKeyStore

            keystore = PyKeyStore()
            try:
                stored_record = keystore.get("affiliate_id")
            except Exception as e:
                logma.debug(f"[referral_panel] PyKeyStore.get(affiliate_id) failed: {e}")
                stored_record = None
            # ``PyKeyStore.get(service)`` returns a dict (or
            # raises KeyError when missing). We pull the
            # ``public_id`` field -- the canonical affiliate
            # identifier slot -- and fall back to ``api_key``,
            # then ``private_key`` for older record shapes.
            stored_affiliate_id = None
            if isinstance(stored_record, dict):
                stored_affiliate_id = (
                    stored_record.get("public_id") or stored_record.get("api_key") or stored_record.get("private_key")
                )
        except Exception as e:
            logma.debug(f"[referral_panel] PyKeyStore init failed: {e}")
            stored_affiliate_id = None
        if isinstance(stored_affiliate_id, str) and stored_affiliate_id:
            # T-NEW-026: PyKeyStore value wins over user.id.
            user_id = stored_affiliate_id
            logma.info(f"[referral_panel] using PyKeyStore affiliate_id")
        elif user_obj is not None:
            user_id = (
                getattr(user_obj, "id", None)
                or getattr(user_obj, "user_name", None)
                or getattr(user_obj, "email", None)
                or "anonymous"
            )
        else:
            user_id = "anonymous"
        user_id = str(user_id)
        self.referral_code = ReferralCode.generate(user_id)
        # T-NEW-026 (close-out step 3): surface the referral
        # URL to the ad pane so a logged-in user sees the
        # link alongside the banners. The ad pane may not be
        # available in all contexts (test harnesses, partial
        # UI builds) -- the helper handles the missing case.
        self._surface_referral_url_to_ad_pane()
        try:
            if isinstance(cfg_dikt, dict):
                cfg_dikt["referral_code"] = str(self.referral_code)
                if hasattr(user_cfg, "_save"):
                    user_cfg._save()
        except Exception as e:
            logma.warning(f"[referral_panel] could not persist code: {e}")

    def set_ad_pane(self, ad_pane):
        """Register the NchantdOfficeAdTab pane so the panel
        can surface the user's referral URL there (T-NEW-026
        close-out step 3).

        Defensive: any pane object that has a
        ``show_referral_url(url)`` method is accepted.
        Returns ``self`` for chainable call sites.
        """
        try:
            self._ad_pane = ad_pane
        except Exception:
            self._ad_pane = None
        return self

    def _surface_referral_url_to_ad_pane(self):
        """Build the referral URL from the code and push it to
        the registered ad pane (T-NEW-026 close-out step 3).

        The URL format is ``https://nchantdoffice.com/?r=<code>``
        (the canonical nchantd office affiliate / referral
        base URL). Defensive: missing pane, missing code, or
        any exception is logged + swallowed.
        """
        try:
            pane = getattr(self, "_ad_pane", None)
            code = getattr(self, "referral_code", None)
            if pane is None or code is None:
                return
            url = f"https://nchantdoffice.com/?r={code}"
            if hasattr(pane, "show_referral_url"):
                try:
                    pane.show_referral_url(url)
                except Exception as e:
                    logma.warning(f"[referral_panel] ad_pane.show_referral_url failed: {e}")
        except Exception as e:
            logma.warning(f"[referral_panel] _surface_referral_url_to_ad_pane failed: {e}")

    def _fetch_dashboard(self):
        """Fetch earnings + invitations from the server; fall back to local store."""
        try:
            data = self.api_client.fetch_earnings()
            if data:
                self.earnings_data = data
                self.invitations_remaining = int(data.get("invitations_remaining", self.invitations_remaining))
                logma.info(
                    f"[referral_panel] dashboard fetched: " f"{self.earnings_data.get('total_referrals', 0)} referrals"
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
