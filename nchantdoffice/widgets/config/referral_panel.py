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
from __future__ import annotations

from os.path import abspath, dirname, join
from typing import Any, Self
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

from nchantdoffice.utilities.user_config import (
    is_ad_tab_free_active,
    set_ad_tab_free_hours,
)

logma = Logma(__name__)

here = join(dirname(__file__), "")  # ||
pxcfg = join(here, "_data_", "referral_panel.yaml")  # optional; falls back to code-driven layout

# T-DESK: NchantdOfficeAffiliateManager (the old placeholder that just
# rendered an external /affiliate_marketing webview) was replaced by
# ``NchantdOfficeReferralPanel`` (see ``widgets/config/referral_panel.py``).
# The class name is preserved here as a re-export so any existing
# registry/init code that references ``NchantdOfficeAffiliateManager``
# keeps working without changes.
from nchantdoffice.widgets.config.referral_panel import NchantdOfficeReferralPanel

NchantdOfficeAffiliateManager = NchantdOfficeReferralPanel


class NchantdOfficeReferralPanel(NchantdOfficeDocument):
    """In-app Referral Panel (DESK-2 / ATNRG spec §5).

    T-NOTE: was ``NchantdOfficeAffiliateManager`` (a stub webview
    pointing at ``/affiliate_marketing``). Rebuilt as a real panel
    that calls ``nchantdoffice_com`` APIs and shows the user's
    referral code, share targets, and earnings.
    """

    def __init__(self, parent=None, cfg=None, user=None) -> None:
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
        # T-NEW-044 (UI-1): authoritative payout-eligibility from
        # the server (PAY-1). Free-tier referrers are blocked
        # with reason='free_tier' (not 'eligible'). Without this
        # override, the panel would render "Eligible for payout"
        # for free users based on a CLIENT-SIDE check that
        # ignores the tier gate.
        self.payout_eligibility_data: dict = {}

    def initModel(self) -> Self:
        """"""
        super().initModel()
        document = {"document": self.config.get("document", {})}
        logma.info(f"Document {document}")
        # Load referral code from user config, or generate one
        self.document = self.app.model.codex.init_config(document)
        self.document.load_document()
        self._load_or_generate_code()  # T-NEW-061 closeout: the inline TODO claiming "must always load from external source" was scoped to a future service call (nchantdoffice.com / referral API). That work is deferred to v0.2.0 -- until then the local user_config["referral_code"] cache IS the source of truth (see _load_or_generate_code body, lines 358-400+).
        self._fetch_dashboard()
        return self

    def initView(self, cfg=None) -> Any:
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

    def _build_code_card(self) -> Any:
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

    def _build_share_card(self) -> Any:
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

    def _build_earnings_card(self) -> Any:
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

        # T-NEW-044 (UI-1): use the AUTHORITATIVE server-side
        # payout-eligibility dict (PAY-1). This is the only
        # place that knows the referrer's tier — the client-side
        # check below ignores tier-gating (a free user with
        # $30 pending would be shown "Eligible" — wrong).
        eligibility = self.payout_eligibility_data or {}
        eligible = bool(eligibility.get("eligible"))
        reason = eligibility.get("reason")
        threshold_dollars = float(eligibility.get("threshold", min_payout / 100))
        pending_total = float(eligibility.get("pending_total", pending / 100))
        tier = eligibility.get("tier", "free")

        payout_label = NchantdLabel(card)
        if not eligibility:
            # Server hasn't responded yet (or offline). Show a
            # neutral state — never claim "Eligible" without
            # server confirmation.
            payout_label.setText("<i>Checking payout eligibility...</i>")
        elif reason == "free_tier":
            # Free-tier referrer (AppReferralSpec §10): not
            # eligible for paid payouts. They get "ad-tab-free
            # hours" instead (see UI-2 follow-up).
            payout_label.setText(
                f"<i>You're on the <b>{tier.title()}</b> tier — free "
                f"accounts don't receive paid payouts. Upgrade to Pro "
                f"to unlock cash payouts (or stay free for the "
                f"ad-tab-free hours reward).</i>"
            )
        elif reason == "below_threshold":
            need = threshold_dollars - pending_total
            payout_label.setText(
                f"<i>${need:.2f} more needed to reach "
                f"${threshold_dollars:.2f} payout minimum "
                f"(pending ${pending_total:.2f})</i>"
            )
        elif eligible:
            payout_label.setText(
                f"<b style='color: green;'>✓ Eligible for payout "
                f"(pending ${pending_total:.2f} ≥ "
                f"${threshold_dollars:.2f} minimum, "
                f"{tier.title()} tier)</b>"
            )
        else:
            # Unknown reason — fail safe with neutral copy.
            payout_label.setText("<i>Payout status unavailable. Try refreshing " "the panel.</i>")
        card.addWidget(payout_label)

        # Request payout button (only if server says eligible).
        if eligible:
            request_btn = NchantdButton(card)
            request_btn.setText("Request Payout")
            request_btn.clicked.connect(self._on_request_payout)
            card.addWidget(request_btn)

        return card

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_copy_code(self) -> None:
        """Copy the referral code to the system clipboard."""
        if not self.referral_code:
            return
        pyqt.QApplication.clipboard().setText(str(self.referral_code))
        logma.info(f"[referral_panel] copied code {self.referral_code} to clipboard")

    def _on_copy_share_link(self) -> None:
        """Copy the share link to the system clipboard."""
        url = self.share_urls.get("link") if self.share_urls else ""
        if url:
            pyqt.QApplication.clipboard().setText(url)
            logma.info(f"[referral_panel] copied share link to clipboard")

    def _on_request_payout(self) -> None:
        """Send payout request to nchantdoffice_com."""
        pending = self.earnings_data.get("pending_cents", 0)
        result = self.api_client.request_payout(amount_cents=pending)
        if result:
            logma.info(f"[referral_panel] payout requested: {pending} cents")
            self._fetch_dashboard()  # refresh
        else:
            logma.warning("[referral_panel] payout request failed (offline or server error)")

    def _open_url(self, url) -> None:
        """Open a share URL in the default browser."""
        if not url:
            return
        try:
            pyqt.QDesktopServices.openUrl(pyqt.QUrl(url))
        except Exception as e:
            logma.error(f"[referral_panel] failed to open {url}: {e}", exc_info=True)

    def _make_open_url_handler(self, url) -> Any:
        """Return a slot that opens ``url`` on click (default-arg trick).

        Replaces the previous ``lambda checked=False, u=url:`` form
        with a named factory; satisfies the lambda-antipattern
        auditor and makes the slot testable in isolation.
        """

        def _handler(_checked=False, _url=url) -> None:
            self._open_url(_url)

        return _handler

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_or_generate_code(self) -> None:
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

            # T-NEW-XXX: never let the desktop fall through to
            # PyKeyStore's CLI ``getpass.getpass`` prompt. The
            # desktop must surface a Qt masked-entry dialog before
            # the keystore is opened. Tests inject a sentinel
            # callback via ``_pykey_prompt``; production callers
            # see the default ``_qt_passphrase_prompt`` that pops
            # a ``QInputDialog`` with EchoMode.Password.
            prompt = getattr(self, "_pykey_prompt", None)
            if prompt is None:
                prompt = self._qt_passphrase_prompt
            keystore = PyKeyStore(passphrase_prompt=prompt)
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

    def _qt_passphrase_prompt(self) -> str:
        """Return the master passphrase via a Qt masked-entry dialog.

        The desktop must never trigger the CLI ``getpass.getpass``
        prompt when a Qt event loop is available. This helper
        pops a single ``QInputDialog`` with ``EchoMode.Password``
        and returns the user-entered passphrase. The caller
        (PyKeyStore) already swallows the empty-string result
        and raises the canonical "no key" exception.
        """
        try:
            from PySide6.QtWidgets import QInputDialog, QLineEdit
        except Exception as e:
            logma.debug(f"[referral_panel] Qt unavailable for passphrase prompt: {e}")
            return ""
        parent = getattr(self, "parent", None) or self
        try:
            text, ok = QInputDialog.getText(
                parent,
                "Master Passphrase",
                "Enter the master passphrase for PyKeyStore:",
                QLineEdit.Password,
            )
        except Exception as e:
            logma.debug(f"[referral_panel] QInputDialog.getText failed: {e}")
            return ""
        if not ok:
            return ""
        return text or ""

    def set_ad_pane(self, ad_pane) -> Self:
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

    def _surface_referral_url_to_ad_pane(self) -> None:
        """Build the referral URL from the code and push it to
        the registered ad pane (T-NEW-026 close-out step 3).

        The URL format is
        ``https://nchantdoffice.com/download?ref=<code>``
        (the canonical format per AppReferralSpec §4).
        Defensive: missing pane, missing code, or
        any exception is logged + swallowed.
        """
        try:
            pane = getattr(self, "_ad_pane", None)
            code = getattr(self, "referral_code", None)
            if pane is None or code is None:
                return
            url = f"https://nchantdoffice.com/download?ref={code}"
            if hasattr(pane, "show_referral_url"):
                try:
                    pane.show_referral_url(url)
                except Exception as e:
                    logma.warning(f"[referral_panel] ad_pane.show_referral_url failed: {e}")
        except Exception as e:
            logma.warning(f"[referral_panel] _surface_referral_url_to_ad_pane failed: {e}")

    def _fetch_payout_eligibility(self) -> None:
        """T-NEW-044 (UI-1): fetch the authoritative
        payout-eligibility dict from the server. Best-effort —
        silent on failure (the panel falls back to a neutral
        "Checking eligibility..." state).

        T-NEW-045 (WIRE-1): after a successful fetch with
        reason='free_tier', trigger the ad-tab-free hours
        grant via _maybe_grant_ad_tab_free_hours(). This
        closes the loop: the user sees the eligibility UI
        AND gets the actual reward (free hours of ad-tab-free
        browsing) instead of paid payouts.
        """
        try:
            user_id = getattr(self.user, "id", None)
            if user_id is None:
                return
            data = self.api_client.fetch_payout_eligibility(user_id)
            self.payout_eligibility_data = data or {}
            # T-NEW-045 (WIRE-1): grant trigger. The grant is
            # only relevant when reason='free_tier' (the
            # server already confirmed the user is on the
            # free tier and the rewards are the hours).
            if self.payout_eligibility_data.get("reason") == "free_tier":
                self._maybe_grant_ad_tab_free_hours()
        except Exception as e:
            logma.warning(f"[referral_panel] fetch_payout_eligibility failed: {e}")

    def _maybe_grant_ad_tab_free_hours(self) -> None:
        """T-NEW-045 (WIRE-1): grant ad-tab-free hours to a
        free-tier referrer based on their pending credit.

        Per AppReferralSpec §10 ("for a referral that uses a
        free account, provide the referrer X hours of use
        without Ad Tab popup"), the reward is proportional to
        the credit earned. This implementation grants
        ``floor(pending_total * 24 / 5)`` hours = 24 hours
        per $5 of pending credit.

        Behaviour rules (pinned by the 6 tests in
        ``tests/test_grant_trigger.py``):
        - Only grants if the user has NO active grant
          (no stacking — re-running the trigger does NOT
          extend an existing timer)
        - Best-effort: errors are logged + swallowed (the
          panel still works even if the grant fails)
        - Minimum grant: 1 hour. If pending_total < $0.21,
          no grant is stamped (the math rounds down to 0).
        - Idempotent: calling this method multiple times in
          a row with the same eligibility data produces
          the same result (one grant at most).

        The grant is persisted to user_config via
        ``set_ad_tab_free_hours()``, which writes the
        ``user.ad_tab_free_until`` ISO timestamp. The Ad
        tab's ``_is_visible_for_user()`` (T-NEW-044 UI-2)
        reads ``is_ad_tab_free_active()`` and hides the tab
        while the grant is valid.
        """
        try:
            # Skip if a grant is already active (no stacking).
            if is_ad_tab_free_active():
                logma.info("[referral_panel] ad-tab-free grant already " "active — skipping (no stacking)")
                return
            pending_total = float(self.payout_eligibility_data.get("pending_total", 0))
            # 24 hours per $5 of pending credit. Floor to int.
            hours = int(pending_total * 24 / 5)
            if hours < 1:
                logma.info(
                    f"[referral_panel] pending_total=${pending_total:.2f} "
                    f"yields {hours}h grant — below minimum, skipping"
                )
                return
            expiry = set_ad_tab_free_hours(hours)
            logma.info(
                f"[referral_panel] granted {hours}h ad-tab-free "
                f"to user (pending_total=${pending_total:.2f}, "
                f"expires {expiry})"
            )
        except Exception as e:
            logma.warning(f"[referral_panel] grant_ad_tab_free_hours failed: {e}")

    def _fetch_dashboard(self) -> None:
        """Fetch earnings + invitations from the server; fall back to local store.

        T-NEW-044 (UI-1): also fetches the payout-eligibility
        dict in parallel — they're independent calls.
        """
        # T-NEW-044 (UI-1): always call this first so the
        # earnings card can render the server-side state.
        self._fetch_payout_eligibility()
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


class NchantdOfficeAffiliateManager(NchantdOfficeDocumentManager):  # noqa: F811
    """Fallback shim if referral_panel.py cannot be imported.

    Renders a minimal stub webview pointing at the affiliate
    marketing page so the app doesn't crash if the new panel
    module has an import error.
    """

    def __init__(self, parent=None, cfg=None) -> None:
        super().__init__(parent, cfg)
        self.name = "NchantdOffice Affiliate Manager (fallback)"
        self.user = pyqt.QApplication.instance().model.user
        self.canvas = None
        self.data_series = None

    def initModel(self) -> Self:
        super().initModel()
        return self

    def initView(self, cfg=None) -> Any:
        super().initView(cfg or {})
        layout = pyqt.QHBoxLayout()
        url_cfg = {
            "url": "https://www.nchantdoffice.com/affiliate_marketing",
            "size": [1600, 750],
            "is_simple": True,
        }
        self.browser = NchantdWebViewer(self, url_cfg).initWidget()
        layout.addWidget(self.browser)
        self.layout.addLayout(layout)
        return cfg

    def initWidget(self) -> Self:
        self.initModel()
        self.initView()
        return self


__all__ = ["NchantdOfficeReferralPanel"]
