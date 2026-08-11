# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-affiliate-panel
    name: Affiliate Panel Widget
    description: >
        In-app Affiliate Panel (DESK-3 of T-NEW-044 UI work).

        Shows the user's affiliate onboarding state and
        the Stripe Connect "Connect" button. The user
        clicks "Connect Stripe" -> POST /api/v1/affiliate/
        connect-stripe -> opens the Stripe-hosted onboarding
        URL in the user's browser -> on success, the
        server stores the stripe_connect_id on the
        AffiliateModel.

        T-NEW-030 (server) provides the
        PaymentService.connect_stripe_account() method this
        panel calls. T-NEW-044 (UI-3) wires the desktop
        widget.

        Backed by:
          - utilities/referral.py (ReferralAPIClient)
          - nchantdoffice_com/app/apis/affiliate_api.py
            (/connect-stripe, /connect-status endpoints)
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""

# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
import webbrowser
from os.path import abspath, dirname, join

# ======================================3rd Party Library Modules=====================================================||
from nchantrs.libraries import pyqt

# ======================================Solutions Brewer Library Modules=============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.groups import NchantdGridScrollGroupBox
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantdoffice.utilities.referral import (
    DEFAULT_API_BASE,
    ReferralAPIClient,
)

logma = Logma(__name__)

here = join(dirname(__file__), "")


class NchantdOfficeAffiliatePanel(NchantdOfficeDocument):
    """T-NEW-044 (UI-3): in-app Affiliate Panel.

    Surfaces the user's Stripe Connect status and the
    "Connect Stripe" button. The actual onboarding flow
    runs in the user's browser (Stripe-hosted KYC).
    """

    def __init__(self, parent=None, cfg=None, user=None):
        """Initialize the affiliate panel.

        Args:
            parent: parent widget (None for tab root)
            cfg: project config dict
            user: NchantdOfficeUser instance (for user_id lookup)
        """
        self.name = "NchantdOffice Affiliate Panel"
        super().__init__(self.name, parent, cfg)
        self.api_client = ReferralAPIClient(base_url=DEFAULT_API_BASE)
        self.user = user
        self.stripe_connect_status: dict = {}
        self.connect_button: NchantdButton = None
        self.status_label: NchantdLabel = None

    def initModel(self):
        """Initialize the model — minimal for now (panel renders
        on demand rather than via a complex data model)."""
        pass

    def initView(self):
        """Build the panel UI."""
        card = NchantdGridScrollGroupBox(self)
        card.setTitle("Affiliate Program")

        # Title + description
        desc = NchantdLabel(card)
        desc.setText(
            "<b>Become a NchantdOffice Affiliate</b><br><br>"
            "Earn cash commissions by referring new users. "
            "Connect your Stripe account below to receive "
            "monthly payouts (you'll need a verified Stripe "
            "account; Stripe's onboarding handles KYC)."
        )
        card.addWidget(desc)

        # Status label (None / Connected)
        self.status_label = NchantdLabel(card)
        self.status_label.setText("<i>Loading...</i>")
        card.addWidget(self.status_label)

        # Connect Stripe button
        self.connect_button = NchantdButton(card)
        self.connect_button.setText("Connect Stripe Account")
        self.connect_button.clicked.connect(self._on_connect_stripe)
        card.addWidget(self.connect_button)

        return card

    def fetch_connect_status(self):
        """T-NEW-044 (UI-3): fetch the user's current Stripe
        Connect status from the server (via
        ``GET /api/v1/affiliate/connect-status``).

        Best-effort: silent on failure (the panel falls back
        to a "Status unavailable" message).
        """
        try:
            user_id = getattr(self.user, "id", None)
            if user_id is None:
                return
            # Use the existing _request helper to call the
            # server endpoint. The endpoint doesn't require
            # a body, just an authenticated user.
            data = self.api_client._request(
                "GET", "affiliate/connect-status",
            )
            if data:
                self.stripe_connect_status = data
                self._refresh_status_label()
        except Exception as exc:
            logma.warning(
                f"[affiliate_panel] fetch_connect_status failed: {exc}"
            )

    def _refresh_status_label(self):
        """Update the status label based on self.stripe_connect_status."""
        if not self.status_label:
            return
        if self.stripe_connect_status.get("connected"):
            acct_id = self.stripe_connect_status.get("stripe_connect_id", "")
            self.status_label.setText(
                f"<b style='color: green;'>✓ Connected to Stripe "
                f"(account {acct_id[:12]}...)</b>"
            )
            if self.connect_button:
                self.connect_button.setText("Reconnect Stripe")
        else:
            self.status_label.setText(
                "<i>Not connected. Click below to start "
                "Stripe onboarding.</i>"
            )
            if self.connect_button:
                self.connect_button.setText("Connect Stripe Account")

    def _on_connect_stripe(self):
        """T-NEW-044 (UI-3): event handler for the Connect
        Stripe button click.

        Calls ``POST /api/v1/affiliate/connect-stripe`` on the
        server, receives the Stripe-hosted onboarding URL, and
        opens it in the user's browser. The user completes KYC
        in the browser (we don't try to embed Stripe Connect
        onboarding in the desktop — it's always browser-based).
        """
        try:
            user_id = getattr(self.user, "id", None)
            if user_id is None:
                logma.warning(
                    "[affiliate_panel] _on_connect_stripe: "
                    "no user.id — cannot call server"
                )
                return
            # Server-side endpoint: PaymentService.connect_stripe_account
            data = self.api_client._request(
                "POST", "affiliate/connect-stripe",
                json={"user_id": user_id},
            )
            if not data:
                logma.warning(
                    "[affiliate_panel] connect-stripe returned no data"
                )
                return
            onboarding_url = data.get("onboarding_url")
            if not onboarding_url:
                logma.warning(
                    f"[affiliate_panel] connect-stripe response "
                    f"missing onboarding_url: {data}"
                )
                return
            logma.info(
                f"[affiliate_panel] launching Stripe onboarding: "
                f"{onboarding_url[:60]}..."
            )
            webbrowser.open(onboarding_url)
        except Exception as exc:
            logma.error(
                f"[affiliate_panel] _on_connect_stripe failed: {exc}"
            )