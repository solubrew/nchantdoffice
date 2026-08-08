# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-affiliate-fallback
    name: Affiliate Fallback Catalog
    description: >
        T-DESK-057 (cross-repo review §2.2): the offline
        fallback catalog for the Ad tab's affiliate rotation.
        Mirrors the ``active`` entries from
        ``nchantdofficeATNRG/ReferralLinks.yaml`` so the
        desktop always has a real cross-section of the
        affiliate offerings, not 3 hand-picked ones.

        Release checklist (R-5 in
        ``docs/cross-repo-review_20260807.md``): when ATNRG
        adds a new ``status: active`` entry to
        ReferralLinks.yaml, copy the
        ``{display_name, base_url, affiliate_url}`` triple
        into ``FALLBACK_BANNERS`` here. The
        ``test_fallback_count_meets_release_checklist`` test
        fails when the desktop bundle falls behind the
        marketing source.

        Same visual-language contract as the Ad tab's
        AffiliateSlot.render() — each banner is a dict with
        ``title, subtitle, cta_text, cta_url, background,
        foreground``.
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*-

# T-DESK-057 — bundled fallback catalog (mirrored from
# nchantdofficeATNRG/ReferralLinks.yaml, status=active entries
# only). The four ``active`` services per the YAML:
#   1. openai   — $200 API credit referral
#   2. railway  — $5 credit per referral
#   3. supabase — $50 credit for referred orgs
#   4. dropbox  — 500MB storage bonus (up to 19GB)
#
# Each entry is a banner card dict matching the Ad tab's
# AffiliateSlot.render() shape (title, subtitle, cta_text,
# cta_url, background, foreground). The background colors are
# the brand-aligned hex codes from the existing FALLBACK_BANNERS
# (or closest match from the brand palette).
#
# Operators: when you add a new ``status: active`` entry to
# ReferralLinks.yaml, add the matching banner dict here AND
# bump the count in ``test_fallback_count_meets_release_checklist``.

FALLBACK_BANNERS: list = [
    {
        "title": "OpenAI - Build with GPT models",
        "subtitle": "$200 API credit for new users. Build AI apps with GPT-4, GPT-4o, and more.",
        "cta_text": "Get OpenAI credit",
        "cta_url": "https://platform.openai.com?ref=nchantdoffice",
        "background": "#10A37F",
        "foreground": "#FFFFFF",
    },
    {
        "title": "Railway - Deploy in seconds",
        "subtitle": "$5 credit per referred user. Push to git, get a live URL.",
        "cta_text": "Try Railway",
        "cta_url": "https://railway.app?ref=nchantdoffice",
        "background": "#1F2937",
        "foreground": "#FFFFFF",
    },
    {
        "title": "Supabase - The open source Firebase",
        "subtitle": "$50 credit for referred organizations. Postgres, auth, storage in one platform.",
        "cta_text": "Start with Supabase",
        "cta_url": "https://supabase.com?ref=nchantdoffice",
        "background": "#3ECF8E",
        "foreground": "#0F172A",
    },
    {
        "title": "Dropbox - 500MB free per referral",
        "subtitle": "Earn up to 19GB of bonus storage by referring friends to Dropbox.",
        "cta_text": "Get Dropbox",
        "cta_url": "https://www.dropbox.com/referrals?ref=nchantdoffice",
        "background": "#0061FF",
        "foreground": "#FFFFFF",
    },
]


def load_fallback_banners() -> list:
    """Return the bundled fallback banner catalog.

    Returns a copy of ``FALLBACK_BANNERS`` so callers can't
    mutate the module-level constant. Same offline-first
    pattern as ``load_tip_feed`` / ``load_substack_feed``
    in ``nchantdoffice/widgets/advertisements.py``.
    """
    return list(FALLBACK_BANNERS)


__all__ = ["FALLBACK_BANNERS", "load_fallback_banners"]
