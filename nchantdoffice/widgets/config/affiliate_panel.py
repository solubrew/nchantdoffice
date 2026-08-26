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
from __future__ import annotations


from os.path import abspath, dirname, join
from typing import Any, Self

# ======================================3rd Party Library Modules=====================================================||
from nchantrs.libraries import pyqt

# ======================================Solutions Brewer Library Modules=============================================||
from kahndor import kahndor
from kahndor.logma import Logma

logma = Logma(__name__)

here = join(dirname(__file__), "")
