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
from __future__ import annotations

# ======================================Standard Library Modules======================================================||
from typing import Any, Callable, Optional

from dataclasses import dataclass, field
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||
from nchantrs.libraries import pyqt

# ======================================Solutions Brewer Library Modules=============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.groups import NchantdGridScrollGroupBox, NchantdVScrollGroupBox
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantdoffice.utilities.user_config import is_ad_tab_free_active

logma = Logma(__name__)

here = join(dirname(__file__), "")  # ||
pxcfg = join(here, "_data_", "advertisements.yaml")

# ---------------------------------------------------------------------------
# T-DESK-066 (paired with nchantdofficeATNRG/T-NEW-029) —
# four-slot Ad tab rotation: tip → substack → pro_cta → affiliate
# ---------------------------------------------------------------------------

# Surface cadence (ms) — the Ad tab re-asks the server for
# the next ad every 5 minutes. Operator-overridable via
# ``advertisements.yaml``: ``NchantdOfficeAdTab: { surface_interval_ms: 300000 }``.
#
# DESK T-NEW-061: replaced the previous ``DEFAULT_INTERVAL_MS = 12000``
# (12-second local slot rotation) which caused UI lockups when the
# timer callback raced with the in-flight HTTP fetches. The new
# DESK T-NEW-061: server-driven ad surfacing cadence (ms).
# The server picks the ad; the desktop re-asks every 5 minutes.
# Operator-overridable via ``advertisements.yaml``:
# ``NchantdOfficeAdTab: { surface_interval_ms: 300000 }``.
DEFAULT_SURFACE_INTERVAL_MS = 5 * 60 * 1000


# --------------------------------------------------------------------------
# T-DESK-066 — local tip feed (mirrored from
# nchantdofficeATNRG/content/memes/tips.md, commit 48352d3).
#
# The desktop bundles the 30 productivity tips locally so the
# Ad tab rotation works offline. Operator updates this list
# when the ATNRG feed grows past 30.
#
# Markdown bold wrappers are tolerated (the ATNRG source uses
# **…**) — the renderer strips them before display.
TIPS_FEED: list = [
    "**Use Ctrl + Shift + T** (or Cmd + Shift + T on Mac) to instantly reopen the last closed browser tab.",
    "**Batch your email** — check it only 2–3 times a day instead of reacting to every notification.",
    "**Create a “Waiting For” folder** in your email or task list so nothing falls through the cracks.",
    "**Name files with dates first** (YYYY-MM-DD) so they sort chronologically automatically.",
    "**Pin your most-used browser tabs** so they stay put and free up space.",
    "**Turn on Focus Mode / Do Not Disturb** during deep work blocks — even 45 minutes helps.",
    "**Use the browser’s built-in reader view** (Firefox/Edge/Safari) to strip ads and distractions from long articles.",
    "**Keep a running “Today” list** of only 3 priority tasks — everything else goes to a backlog.",
    "**Search your email with operators** like `from:name has:attachment` to find things in seconds.",
    "**Duplicate a browser tab** (right-click → Duplicate) instead of navigating back when you need the same page open twice.",
    "**Set calendar events as “busy” by default** so colleagues know when you’re unavailable.",
    "**Use keyboard shortcuts for text formatting** in documents (Ctrl+B, Ctrl+I, Ctrl+U) instead of reaching for the mouse.",
    "**Create a bookmarks folder called “Read Later”** and clear it once a week.",
    "**Mute group chats and notification-heavy channels** — check them on your schedule.",
    "**Save common replies as templates** or text expanders so you never retype the same email.",
    "**Open links in new tabs by default** (middle-click or Ctrl+click) so you don’t lose your current page.",
    "**Use a single “Inbox Zero” ritual** at the end of each day: process, delete, or schedule everything.",
    "**Name browser windows by project** (right-click tab bar → Name window) when you have multiple open.",
    "**Schedule short “buffer” blocks** between meetings so you can actually finish notes or stretch.",
    "**Turn on auto-correct and smart quotes** only where they help — disable them in code or technical writing.",
    "**Use vertical tabs** (available in Edge, Arc, and some extensions) when you have dozens of tabs open.",
    "**Keep a “Someday/Maybe” list** separate from your active tasks so ideas don’t clutter your day.",
    "**Search Google with site: specificdomain.com** to find information only on trusted sites.",
    "**Close all browser tabs related to one project** the moment that project is finished.",
    "**Use the “Send later” or “Schedule send” feature** so emails arrive at the recipient’s best time.",
    "**Create desktop shortcuts or browser bookmarks** for the three tools you open every single morning.",
    "**Work in full-screen mode** for writing or deep focus — hide the taskbar and browser chrome.",
    "**Review your calendar every Sunday night** for 10 minutes to spot conflicts and plan the week.",
    "**Use Ctrl + F (or Cmd + F)** aggressively inside long documents and web pages — never scroll manually.",
    "**End every work session by writing the very next action** for tomorrow so you start instantly.",
    "**Review your energy, not just your calendar** — schedule high-focus work when you're sharpest.",
]


# ---------------------------------------------------------------------------
# T-DESK-066 — local Substack recommendation feed (the
# symbiosis-reciprocal placement from
# nchantdofficeATNRG/0-5kpm-revenue-plan.md §"Symbiosis Substack
# Strategy" §4). Operator adds entries over time per the
# outreach plan (Quick Starting List step 5: "Add 3-5 of the
# strongest ones into your Ad tab rotation immediately as
# value content").
# ---------------------------------------------------------------------------

SUBSTACK_FEED: list = [
    {
        "title": "Ness Labs",
        "url": "https://nesslabs.com",
        "blurb": "Tools and frameworks for deliberate productivity and note-making.",
    },
    {
        "title": "Farnam Street",
        "url": "https://fs.blog",
        "blurb": "Mastering the best of what other people have already figured out.",
    },
    {
        "title": "Productivity Game",
        "url": "https://productivitygame.substack.com",
        "blurb": "Tactics and routines that compound into measurable output gains.",
    },
    {
        "title": "The Weekly Review",
        "url": "https://fortelabs.com",
        "blurb": "Deep dives into GTD, second brains, and knowledge-worker workflows.",
    },
    {
        "title": "Refactoring by Alex Ewerlöf",
        "url": "https://refactoring.substack.com",
        "blurb": "Career notes for engineers — patterns, anti-patterns, and growth.",
    },
]


def load_tip_feed() -> list:
    """Return the bundled productivity tip feed (30 entries,
    mirrored from nchantdofficeATNRG/content/memes/tips.md).

    Always returns at least 30 entries — the function does
    not fall back to a server call (the feed is fully
    offline-capable, same pattern as FALLBACK_BANNERS).
    """
    return list(TIPS_FEED)


def load_substack_feed() -> list:
    """Return the bundled Substack recommendation feed (5
    starter entries — operator grows this over time per the
    ATNRG outreach plan).

    Always returns at least 3 entries — the function does
    not fall back to a server call.
    """
    return list(SUBSTACK_FEED)


# ---------------------------------------------------------------------------
# T-DESK-066 — RotationSlot dataclass + four concrete subclasses.
#
# Each slot carries:
#   kind    — stable string used by _load_slots for ordering
#             and by tests for contract pinning
#   payload — the raw data dict (banner dict, tip string,
#             substack dict, pro_cta config)
#   render  — bound method that builds the visible widget
# ---------------------------------------------------------------------------


@dataclass
class RotationSlot:
    """Base class for the four-slot Ad tab rotation.

    Subclasses must override ``kind`` (string literal) and
    ``render(parent)``. ``payload`` is the raw data dict
    used by ``render``.
    """

    kind: str = "base"
    payload: dict = field(default_factory=dict)

    def render(self, parent) -> Any:  # pragma: no cover - abstract
        """Return the QWidget to display for this slot."""
        raise NotImplementedError("subclasses must override render()")


@dataclass
class TipSlot(RotationSlot):
    """A productivity tip card (source: TIPS_FEED / ATNRG
    content/memes/tips.md). Renders the tip as a single
    full-width card with no CTA.
    """

    kind: str = "tip"

    def render(self, parent) -> Any:
        card = NchantdGridScrollGroupBox(parent)
        card.setTitle("")
        tip = str(self.payload.get("text", "")).strip()
        body = NchantdLabel(card)
        # Strip ATNRG's markdown bold wrappers for clean display.
        import re as _re

        display = _re.sub(r"\*+", "", tip)
        body.setText(f"<b style='color:#0F172A;'>Tip of the day</b><br>{display}")
        body.setStyleSheet(
            "color:#0F172A; background-color:#F1F5F9; padding:10px;"
            " border-left:4px solid #10A37F;"
        )
        body.setWordWrap(True)
        card.addWidget(body)
        card.setStyleSheet(
            "QGroupBox { background-color:#F1F5F9; border-radius:8px; padding:6px; }"
        )
        return card


@dataclass
class SubstackSlot(RotationSlot):
    """A featured Substack recommendation (source: SUBSTACK_FEED
    / ATNRG 0-5kpm-revenue-plan.md §Symbiosis). Renders the
    title + blurb + a 'Read on Substack' CTA that opens the
    URL in the default browser.
    """

    kind: str = "substack"

    def render(self, parent) -> Any:
        card = NchantdGridScrollGroupBox(parent)
        card.setTitle("")
        title = NchantdLabel(card)
        title.setText(
            f"<b style='color:#FF6B35;'>Readers of nchantd also like</b><br>"
            f"<b>{self.payload.get('title', '')}</b>"
        )
        title.setStyleSheet(
            "color:#FF6B35; background-color:#FFF7ED; padding:6px;"
        )
        title.setWordWrap(True)
        card.addWidget(title)

        blurb = NchantdLabel(card)
        blurb.setText(self.payload.get("blurb", ""))
        blurb.setStyleSheet(
            "color:#7C2D12; background-color:#FFF7ED; padding:6px;"
        )
        blurb.setWordWrap(True)
        card.addWidget(blurb)

        url = self.payload.get("url", "")
        if url:
            cta = NchantdButton(card)
            cta.setText(f"Read {self.payload.get('title', 'on Substack')}")
            # Use the same default-arg factory as the affiliate
            # banner so the slot is testable in isolation.
            factory = NchantdOfficeAdTab._make_open_url_handler_static(url)
            cta.clicked.connect(factory)
            card.addWidget(cta)

        card.setStyleSheet(
            "QGroupBox { background-color:#FFF7ED; border-radius:8px; padding:6px; }"
        )
        return card


@dataclass
class ProCtaSlot(RotationSlot):
    """The 'Remove ads — Go Pro' CTA. Renders the same single
    button that was at the bottom of the static Ad tab. The
    button delegates to ``NchantdOfficeAdTab.redirect_to_get_pro``
    (the shared static helper from Sprint 28).
    """

    kind: str = "pro_cta"

    def render(self, parent) -> Any:
        card = NchantdGridScrollGroupBox(parent)
        card.setTitle("")
        title = NchantdLabel(card)
        title.setText(
            "<b style='color:#FFFFFF;'>Love nchantd Office?</b>"
        )
        title.setStyleSheet(
            "color:#FFFFFF; background-color:#2563EB; padding:6px;"
        )
        title.setWordWrap(True)
        card.addWidget(title)

        sub = NchantdLabel(card)
        sub.setText(
            "Pro removes ads, unlocks extra storage, and supports the work."
        )
        sub.setStyleSheet(
            "color:#FFFFFF; background-color:#2563EB; padding:6px;"
        )
        sub.setWordWrap(True)
        card.addWidget(sub)

        cta = NchantdButton(card)
        cta.setText("Remove ads - Go Pro")
        # The actual click wiring happens in initView (needs
        # the live self reference). We stash the button on the
        # card so initView can connect the slot to
        # _on_remove_ads_clicked.
        card._pro_cta_button = cta  # type: ignore[attr-defined]
        card.addWidget(cta)

        card.setStyleSheet(
            "QGroupBox { background-color:#2563EB; border-radius:8px; padding:6px; }"
        )
        return card


@dataclass
class AffiliateSlot(RotationSlot):
    """An affiliate/team-pack banner (source: base-layer feed →
    affiliate API → FALLBACK_BANNERS). Renders the same
    title/subtitle/CTA card shape as the static Ad tab used
    to show.

    T-NEW-040 DESK-2: ``source`` field distinguishes
    'external' (third-party QuickLinks from the server's
    /api/v1/quicklinks endpoint) from 'internal' (in-house
    ProInternalSlot passthrough — same shape, different
    telemetry event). The default 'external' keeps the
    pre-T-NEW-040 behavior for any caller that doesn't set
    it.
    """

    kind: str = "affiliate"
    source: str = "external"  # T-NEW-040 DESK-2: 'external' | 'internal'

    def render(self, parent) -> Any:
        # Render an affiliate/team-pack banner card. The
        # visual language mirrors the pre-rotation
        # ``_build_banner_card`` helper (removed in T-DESK-066
        # step 6 — AffiliateSlot.render() is now the single
        # source of truth for this card shape).
        banner = self.payload
        card = NchantdGridScrollGroupBox(parent)
        card.setTitle("")
        bg = banner.get("background", "#2563eb")
        fg = banner.get("foreground", "#ffffff")
        title = NchantdLabel(card)
        title.setText(f"<b style='color: {fg};'>{banner.get('title', '')}</b>")
        title.setStyleSheet(
            f"color: {fg}; font-size: 14pt; background-color: {bg}; padding: 6px;"
        )
        title.setWordWrap(True)
        card.addWidget(title)
        if banner.get("subtitle"):
            sub = NchantdLabel(card)
            sub.setText(banner["subtitle"])
            sub.setStyleSheet(
                f"color: {fg}; background-color: {bg}; padding: 6px;"
            )
            sub.setWordWrap(True)
            card.addWidget(sub)
        if banner.get("cta_text") and banner.get("cta_url"):
            cta = NchantdButton(card)
            cta.setText(banner["cta_text"])
            url = banner["cta_url"]
            cta.clicked.connect(
                NchantdOfficeAdTab._make_open_url_handler_static(
                    url,
                    event_name="affiliate_click_external",
                    event_properties={
                        "slot_kind": "affiliate",
                        "source": banner.get("source", "external"),
                        "destination_url": url,
                    },
                )
            )
            card.addWidget(cta)
        card.setStyleSheet(
            f"QGroupBox {{ background-color: {bg}; border-radius: 8px; padding: 6px; }}"
        )
        return card


# T-NEW-040 (DESK-1) — In-house cross-promo slot. Same render
# shape as AffiliateSlot, but with ``kind: pro_internal`` so
# the click handler in DESK-3 can fire
# ``affiliate_click_internal`` (vs ``affiliate_click_external``
# for third-party QuickLinks affiliates). The bundled
# PRO_INTERNAL_PROMOS list below is the offline-first fallback
# so the in-house cross-promo rotation works without a network.


@dataclass
class ProInternalSlot(RotationSlot):
    """An in-house cross-promo (Pro tier, ProData, white-label).

    Source: ``PRO_INTERNAL_PROMOS`` (bundled) or operator-curated
    server-side feed in the future. Renders the same card shape
    as AffiliateSlot so the rotation looks consistent — the
    only difference is the ``kind`` tag for telemetry routing
    (DESK-3).

    T-NEW-040: until ≥500 Free MAU, in-house cross-promos are
    the only fully-owned revenue surface in the Ad tab; we own
    the creative, the conversion path, and the revshare
    reporting (none flows to a third-party affiliate network).
    """

    kind: str = "pro_internal"

    def render(self, parent) -> Any:
        banner = self.payload
        card = NchantdGridScrollGroupBox(parent)
        card.setTitle("")
        bg = banner.get("background", "#0F172A")
        fg = banner.get("foreground", "#FFFFFF")
        title = NchantdLabel(card)
        title.setText(
            f"<b style='color: {fg};'>{banner.get('title', '')}</b>"
        )
        title.setStyleSheet(
            f"color: {fg}; font-size: 14pt; "
            f"background-color: {bg}; padding: 6px;"
        )
        title.setWordWrap(True)
        card.addWidget(title)
        if banner.get("subtitle"):
            sub = NchantdLabel(card)
            sub.setText(banner["subtitle"])
            sub.setStyleSheet(
                f"color: {fg}; background-color: {bg}; padding: 6px;"
            )
            sub.setWordWrap(True)
            card.addWidget(sub)
        if banner.get("cta_text") and banner.get("cta_url"):
            cta = NchantdButton(card)
            cta.setText(banner["cta_text"])
            url = banner["cta_url"]
            cta.clicked.connect(
                NchantdOfficeAdTab._make_open_url_handler_static(
                    url,
                    event_name="affiliate_click_internal",
                    event_properties={
                        "slot_kind": "pro_internal",
                        "destination_url": url,
                    },
                )
            )
            card.addWidget(cta)
        card.setStyleSheet(
            f"QGroupBox {{ background-color: {bg}; "
            f"border-radius: 8px; padding: 6px; }}"
        )
        return card


# T-NEW-040 (DESK-1) — Bundled in-house cross-promo catalog.
# Mirrors the offline-first pattern of FALLBACK_BANNERS /
# TIPS_FEED / SUBSTACK_FEED. The server-side quicklinks
# endpoint (/api/v1/quicklinks/?ad_rotation_categories=
# pro_internal) will eventually source from here; until the
# server integration lands in DESK-2, this is the only
# source.
#
# DESK T-NEW-052: CTA URLs compose from
# ``urls.marketing_base_url()`` so the operator can point the
# whole ad catalog at an internal site by overriding that one
# key (or each individual ``cta_url`` via the server response
# when DESK-2 lands).
from nchantdoffice.utilities.urls import marketing_base_url as _mbu
_MBU = _mbu()
PRO_INTERNAL_PROMOS: list = [
    {
        "title": "nchantdoffice Pro — Remove ads + unlimited nodes",
        "subtitle": (
            "$20/mo or $200/yr. Unlock ProData (10K AI calls/mo) "
            "for $50/mo."
        ),
        "cta_text": "Upgrade to Pro",
        "cta_url": f"{_MBU}/compare",
        "background": "#0F172A",
        "foreground": "#FACC15",
    },
    {
        "title": "ProData — 10K AI calls/mo + Sheets/Docs/Forms APIs",
        "subtitle": (
            "$50/mo or $500/yr. The data-services tier for "
            "power users."
        ),
        "cta_text": "Upgrade to ProData",
        "cta_url": f"{_MBU}/compare#prodata",
        "background": "#1E3A8A",
        "foreground": "#FFFFFF",
    },
    {
        "title": "White-label nchantdoffice for your team",
        "subtitle": (
            "Custom branding, custom domain, your team's colors. "
            "Talk to us about a B2B deal."
        ),
        "cta_text": "Talk to us",
        "cta_url": f"{_MBU}/contact",
        "background": "#7C3AED",
        "foreground": "#FFFFFF",
    },
]


def load_pro_internal_promos() -> list:
    """Return the bundled in-house cross-promo catalog.

    Returns a copy of ``PRO_INTERNAL_PROMOS`` so callers can't
    mutate the module-level constant. Same offline-first
    pattern as ``load_tip_feed`` / ``load_substack_feed`` /
    ``load_fallback_banners``.
    """
    return list(PRO_INTERNAL_PROMOS)


# T-NEW-040 (DESK-2) — Fetch the curated QuickLinks catalog
# entries that belong in the Ad tab's affiliate rotation.
# Returns a list of banner dicts in the AffiliateSlot shape
# (title, subtitle, cta_text, cta_url, background, foreground,
# source='external'). Falls back to FALLBACK_BANNERS if the
# server is unreachable (offline-first).
#
# Until ≥500 Free MAU, this rotation IS the primary revenue
# mechanism for the Ad tab. The bundled FALLBACK_BANNERS
# keeps the rotation functional offline.
_LOAD_AFFILIATE_TIMEOUT_SECS = 3


def _load_affiliate_rotation(api_base_url: str = "") -> list:
    """Fetch Ad tab affiliate rotation entries from the
    QuickLinks catalog.

    Hits ``GET /api/v1/quicklinks/?ad_rotation_categories=
    creator_marketplace,affiliate_network,cross_promo`` and
    converts each entry into the AffiliateSlot banner shape
    (title, subtitle, cta_text, cta_url, background,
    foreground, source='external'). Empty result + offline
    fallback both flow through ``FALLBACK_BANNERS``.

    Args:
        api_base_url: base URL of the server (e.g.,
            ``https://api.nchantdoffice.com``). Defaults to
            an empty string which means ``urllib`` uses the
            relative path. The desktop typically injects the
            configured base from ``self.config``.

    Returns:
        List of banner dicts (each becomes one
        ``AffiliateSlot`` in ``_load_slots``).

    T-NEW-040 DESK-2.
    """
    import json
    try:
        from urllib.request import urlopen, Request
        from urllib.parse import urlencode
        base = api_base_url.rstrip("/") if api_base_url else ""
        url = (
            f"{base}/api/v1/quicklinks/?"
            + urlencode({
                "ad_rotation_categories":
                    "creator_marketplace,"
                    "affiliate_network,"
                    "cross_promo",
            })
        )
        with urlopen(
            Request(url), timeout=_LOAD_AFFILIATE_TIMEOUT_SECS
        ) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        # Offline / API unreachable / timeout — fall back
        # to bundled list. Same offline-first pattern as
        # the base-layer / FALLBACK_BANNERS chain in
        # _load_banners().
        logma.warning(
            f"[ad_tab] affiliate rotation fetch failed: {e}; "
            f"using FALLBACK_BANNERS"
        )
        return [
            {**banner, "source": "external"}
            for banner in load_fallback_banners()
        ]

    # The /api/v1/quicklinks/ endpoint returns a bare list
    # of link dicts (per its marshal_list_with(service_link_model)
    # decorator). Handle both shapes (list, {"links": [...]})
    # for forward-compat.
    if isinstance(payload, dict):
        entries = payload.get("links", [])
    else:
        entries = payload

    out = []
    for entry in entries or []:
        out.append({
            "title": entry.get("display_name", ""),
            "subtitle": entry.get("description", ""),
            "cta_text": "Try it",
            "cta_url": (
                entry.get("affiliate_url")
                or entry.get("base_url", "")
            ),
            "background": "#2563eb",
            "foreground": "#FFFFFF",
            "source": "external",
        })
    if not out:
        # Empty feed — fall back to bundled list so the
        # rotation still has content.
        return [
            {**banner, "source": "external"}
            for banner in load_fallback_banners()
        ]
    return out


# T-DESK-057 — ``FALLBACK_BANNERS`` is now sourced from
# ``nchantdoffice.utilities.affiliate_fallback`` (the bundled
# mirror of ``nchantdofficeATNRG/ReferralLinks.yaml``'s
# ``active`` entries). The inline list literal was removed
# to keep ``advertisements.py`` focused on rotation logic;
# see R-5 in ``docs/cross-repo-review_20260807.md`` for the
# release-checklist mirror procedure.
from nchantdoffice.utilities.affiliate_fallback import (  # noqa: E402,F401
    FALLBACK_BANNERS,
    load_fallback_banners,
)


class NchantdOfficeAdTab(NchantdOfficeDocument):
    """The right-pane Ad Tab.

    T-DESK: was a stub ``NchantdAdvertisementPane`` (different class
    name, only initialised config but never showed UI). This class
    follows the same shape as the other right-tab entries
    (``NchantdOfficeAdTab`` was already wired in the right tabset
    via ``nchantdoffice/_data_/models.yaml``).
    """

    def __init__(self, parent=None, cfg=None) -> None:
        super().__init__("NchantdOfficeAdTab", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeAdTab").override(cfg))
        self._timer = None
        # Kept as a backwards-compat shim (some tests still
        # assert on the flat shape).
        self.banners: list = []
        self._user = None

    def initModel(self, cfg=None) -> "NchantdOfficeAdTab":
        cfg = cfg or {}
        if cfg.get("document", None) is None:
            cfg["document"] = {"data": {"unit": {}}}
        self.config.override(cfg)
        super().initModel(self.config.dikt)
        self.document = self.app.model.codex.init_browser({"document": self.config.get("document", {})})
        self.document.load_document()
        # T-DESK-066: load the four-slot rotation. The legacy
        # ``_load_banners()`` shim is called from inside
        # ``_load_slots()`` to keep one place that decides
        # affiliate banner sources (base-layer / API / fallback).
        self._load_slots()
        return self

    def show_referral_url(self, url) -> Optional["NchantdOfficeAdTab"]:
        """Surface the user's referral URL in the ad tab (T-NEW-026 step 3).

        The Affiliate Manager tab calls this when the user
        generates / loads their referral code so the link is
        visible alongside the banners. Defensive: missing url
        is a no-op. The URL is stored as ``self._referral_url``
        and rendered in the existing header when set.
        """
        try:
            if not isinstance(url, str) or not url:
                return
            self._referral_url = url
            logma.info(f"[ad_tab] referral URL set: {url}")
        except Exception as e:
            logma.warning(f"[ad_tab] show_referral_url failed: {e}")
        return self

    def initView(self, cfg=None) -> Any:
        cfg = cfg or {}
        cfg["fill"] = True
        cfg["default_toolbar"] = False
        super().initView(cfg)

        # Capture user reference for tier checks
        try:
            self._user = pyqt.QApplication.instance().model.user
        except Exception:
            self._user = None

        # If Pro, render nothing — caller will hide the tab.
        # (We also don't start the surface timer — Pro users
        # never see ads at all, so the timer would just spin.)
        if not self._is_visible_for_user():
            logma.info("[ad_tab] hidden: user is Pro tier")
            return cfg

        layout = pyqt.QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header (same Sponsored line as the pre-rotation tab)
        header = NchantdLabel(self)
        header.setText("<b>Sponsored</b> &nbsp;<i>ads support nchantd Office</i>")
        header.setStyleSheet("color: #6b7280; font-size: 9pt;")
        layout.addWidget(header)

        # DESK T-NEW-061: single visible-ad container. The
        # server picks the ad (GET /api/ads/rotation/next);
        # the desktop just renders whatever came back. The
        # QTimer in ``_start_surface_timer`` re-asks every
        # 5 minutes. No local slot rotation.
        self._slot_container = NchantdVScrollGroupBox(self)
        self._slot_container.setTitle("")
        # Show the empty state until the first fetch completes.
        placeholder = NchantdLabel(self._slot_container)
        placeholder.setText("<i>Loading ad…</i>")
        self._slot_container.addWidget(placeholder)
        layout.addWidget(self._slot_container)

        # Manual refresh button — lets the operator force a
        # refresh without waiting 5 minutes (common UX nicety
        # for ad panels). Doesn't bypass the cadence — the
        # next tick still runs at its scheduled time.
        adv_row = pyqt.QHBoxLayout()
        adv_row.setContentsMargins(0, 0, 0, 0)
        adv_row.setSpacing(6)
        refresh_btn = NchantdButton(self)
        refresh_btn.setText("Refresh \u21bb")
        refresh_btn.clicked.connect(self._fetch_and_render)
        adv_row.addWidget(refresh_btn)
        adv_row.addStretch(1)
        layout.addLayout(adv_row)

        self.layout.addLayout(layout)

        # DESK T-NEW-061: start the server-driven surface timer.
        # Free users only — the Pro short-circuit above returned early.
        self._start_surface_timer()
        return cfg

    def _fetch_and_render(self) -> None:
        """Fetch the next ad from the server and render it.

        DESK T-NEW-061: replaces the previous local-slot
        rotation. The server picks which ad to show
        (deterministic bucket based on time + interval),
        the desktop just renders whatever comes back.

        Called by the surface QTimer every 5 minutes and
        by the manual Refresh button. Fail-soft: any
        network/HTTP/JSON error renders the empty state
        and the next tick retries.
        """
        from nchantdoffice.utilities.urls import (
            server_base_url as _sbu,
        )
        from nchantdoffice.widgets.ad_rotation_client import (
            fetch_rotation_ad,
        )
        try:
            ad = fetch_rotation_ad(_sbu())
        except Exception as e:
            logma.warning(f"[ad_tab] _fetch_and_render failed: {e}")
            ad = None
        self._render_ad(ad)

    def _switch_to_this_tab(self) -> None:
        """Switch the right-pane tabset to this tab.

        Called after every successful ad render so the right pane
        auto-surfaces when a new ad arrives on the 5-minute tick.

        Guards:
          - Only runs after initView has built the UI
            (``_slot_container`` exists).
          - Only runs when not already on this tab
            (avoid redundant switch on the initial render).
          - Wrapped in try/except so any Qt or navigation
            failure is silent — the tab is visible and the
            ad renders regardless.
        """
        if not getattr(self, "_slot_container", None):
            return  # initView hasn't run yet
        try:
            app = getattr(self, "app", None)
            if app is None:
                return
            right_pane = getattr(app.view, "panes", {}).get("right")
            if right_pane is None:
                return
            # Find this tab's position in the right pane tabset.
            # Walk the tab bar (QTabBar) by index until we find
            # the tab whose widget is this NchantdOfficeAdTab instance.
            tab_bar = right_pane.tabBar()
            if tab_bar is None:
                return
            ad_index = -1
            for i in range(tab_bar.count()):
                widget_at_i = right_pane.widget(i)
                if widget_at_i is self:
                    ad_index = i
                    break
            if ad_index < 0:
                logma.info(
                    "[ad_tab] _switch_to_this_tab: "
                    "this tab not found in right pane tabset"
                )
                return
            # Skip if we're already on the Ad tab (initial render).
            if right_pane.currentIndex() == ad_index:
                return
            right_pane.setCurrentIndex(ad_index)
            logma.info(
                f"[ad_tab] surfaced (right pane tab index={ad_index})"
            )
        except Exception as e:
            logma.warning(
                f"[ad_tab] _switch_to_this_tab failed (non-blocking): {e}"
            )

    def _render_ad(self, ad: Optional[dict]) -> None:
        """Render a single ad dict (or None for the empty state).

        Pulled out of ``_fetch_and_render`` so tests can drive
        the renderer directly without mocking the network.

        After rendering, switches the right pane to this tab so the
        new ad is auto-surfaced to the user on every 5-minute tick.
        """
        if not getattr(self, "_slot_container", None):
            return  # initView hasn't run yet
        # Clear the container (the old "Loading ad…" or the
        # previously-rendered ad).
        layout_box = self._slot_container.layout_box
        try:
            for i in reversed(range(layout_box.count())):
                item = layout_box.takeAt(i)
                w = item.widget() if item is not None else None
                if w is not None:
                    w.setParent(None)
                    w.deleteLater()
        except Exception as e:
            logma.warning(f"[ad_tab] _render_ad clear failed: {e}")
        if not ad:
            placeholder = NchantdLabel(self._slot_container)
            placeholder.setText("<i>No ads right now.</i>")
            self._slot_container.addWidget(placeholder)
            return
        try:
            # Render the same card shape the previous
            # ``AffiliateSlot`` rendered (title, subtitle,
            # CTA button). Reusing the renderer keeps the
            # operator's ad design intact — they only need
            # to update the server-side ad catalog.
            card = NchantdGridScrollGroupBox(self._slot_container)
            card.setTitle("")
            bg = ad.get("background", "#0F172A")
            fg = ad.get("foreground", "#FFFFFF")
            title = NchantdLabel(card)
            title.setText(
                f"<b style='color: {fg};'>{ad.get('title', '')}</b>"
            )
            title.setStyleSheet(
                f"color: {fg}; font-size: 14pt; "
                f"background-color: {bg}; padding: 6px;"
            )
            title.setWordWrap(True)
            card.addWidget(title)
            sub_text = ad.get("subtitle") or ad.get("description")
            if sub_text:
                sub = NchantdLabel(card)
                sub.setText(sub_text)
                sub.setStyleSheet(
                    f"color: {fg}; background-color: {bg}; padding: 6px;"
                )
                sub.setWordWrap(True)
                card.addWidget(sub)
            cta_text = ad.get("cta_text") or "Learn more"
            cta_url = ad.get("cta_url") or ""
            if cta_url:
                cta = NchantdButton(card)
                cta.setText(cta_text)
                cta.clicked.connect(
                    NchantdOfficeAdTab._make_open_url_handler_static(
                        cta_url,
                        event_name="affiliate_click",
                        event_properties={
                            "ad_id": ad.get("id"),
                            "ad_slug": ad.get("slug"),
                            "destination_url": cta_url,
                            "rotation_source": "server",
                        },
                    )
                )
                card.addWidget(cta)
            card.setStyleSheet(
                f"QGroupBox {{ background-color: {bg}; "
                f"border-radius: 8px; padding: 6px; }}"
            )
            self._slot_container.addWidget(card)
            # Surface the Ad tab after a successful render so the
            # new ad is visible to the user on every 5-minute tick.
            self._switch_to_this_tab()
        except Exception as e:
            logma.warning(f"[ad_tab] _render_ad failed: {e}")
            placeholder = NchantdLabel(self._slot_container)
            placeholder.setText("<i>No ads right now.</i>")
            self._slot_container.addWidget(placeholder)

    def _start_surface_timer(self) -> None:
        """Start the QTimer that re-asks the server for the
        next ad every ``surface_interval_ms``.

        DESK T-NEW-061: replaces the previous 12-second
        local-slot rotation. The surface cadence is
        operator-overridable via ``advertisements.yaml``
        (key ``surface_interval_ms``, default 300_000 ms =
        5 minutes). The manual Refresh button calls
        ``_fetch_and_render`` directly; this timer's job
        is just the 5-minute cadence.

        Pro users never reach this code path (initView
        returns early).
        """
        try:
            surface_ms = int(
                self.config.dikt.get(
                    "surface_interval_ms", DEFAULT_SURFACE_INTERVAL_MS,
                )
            )
        except Exception:
            surface_ms = DEFAULT_SURFACE_INTERVAL_MS
        self._timer = pyqt.QTimer(self)
        self._timer.setInterval(surface_ms)
        self._timer.timeout.connect(self._fetch_and_render)
        self._timer.start()
        logma.info(
            f"[ad_tab] surface timer started (interval="
            f"{surface_ms}ms)"
        )
        # Fire the first fetch immediately so the operator
        # sees an ad on launch instead of the "Loading ad…"
        # placeholder for 5 minutes.
        try:
            self._fetch_and_render()
        except Exception as e:
            logma.warning(
                f"[ad_tab] initial fetch failed (non-blocking): {e}"
            )

    def _cleanup(self) -> None:
        """Stop the surface timer when this tab is being replaced
        (e.g. due to lazy-loading focus swap).

        Without this, the timer's ``_fetch_and_render`` fires on the
        old instance after Qt has removed it from the tabset. The
        subsequent ``_switch_to_this_tab`` then walks the NEW tabset,
        which holds a dummy placeholder instead of ``self``, and logs:
        "this tab not found in right pane tabset".
        """
        timer = getattr(self, "_timer", None)
        if timer is not None:
            timer.stop()
            timer.deleteLater()
            self._timer = None
            logma.info("[ad_tab] surface timer stopped (tab replaced)")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_visible_for_user(self) -> bool:
        """Whether this tab should be rendered for the current user.

        Returns False for:
          - Pro users (they paid to remove ads)
          - Users with active ad-tab-free hours (T-NEW-044 UI-2
            — free-tier referral reward per AppReferralSpec §10).
            The grant is persisted via
            ``user_config.set_ad_tab_free_hours()`` and checked
            via ``user_config.is_ad_tab_free_active()``.

        Returns True for Free users / users without an account
        AND no active ad-tab-free grant.
        """
        # T-NEW-044 (UI-2): check ad-tab-free hours FIRST so
        # the free-tier referral reward hides the tab even
        # before the tier check (the user may be Pro tier
        # OR free-tier, both should respect the grant).
        if is_ad_tab_free_active():
            return False
        user = self._user
        if user is None:
            return True
        return not bool(getattr(user, "has_pro", False))

    def _load_slots(self) -> None:
        """T-DESK-066 — populate ``self.slots`` in the canonical
        order documented in nchantdofficeATNRG/TODOS.md
        T-NEW-029 step 4, extended in T-NEW-040 to a 5-tier
        rotation:

          [tip (1)] + [substack (≥ 3)] + [pro_cta (1)] +
          [affiliate (≥ 1, server quicklinks API or local
          FALLBACK_BANNERS chain)] +
          [pro_internal (3, bundled PRO_INTERNAL_PROMOS)]

        The affiliate tier is now drawn from the new
        ``_load_affiliate_rotation()`` helper (T-NEW-040
        DESK-2) which hits ``/api/v1/quicklinks/?
        ad_rotation_categories=creator_marketplace,
        affiliate_network,cross_promo`` and falls back to
        ``FALLBACK_BANNERS`` on network failure. The
        pro_internal tier is the new in-house cross-promo
        slot (Pro/ProData/white-label) — its entries live
        in the bundled ``PRO_INTERNAL_PROMOS`` list and use
        the new ``ProInternalSlot`` class (DESK-1) so they
        can be telemetry-split from external affiliate
        clicks (DESK-3).
        """
        # First, populate ``self.banners`` via the existing
        # three-tier fallback chain so the affiliate count is
        # correct (and so callers/tests that assert on
        # ``self.banners`` keep working — DESK-2 backwards
        # compat).
        self._load_banners()

        slots: list = []

        # 1. Tip — pick the first tip (the rotation cycles
        # through all of them over time as the operator
        # grows TIPS_FEED; today we cycle one per interval).
        try:
            tips = load_tip_feed()
            if tips:
                slots.append(TipSlot(payload={"text": tips[0]}))
        except Exception as e:
            logma.warning(f"[ad_tab] load_tip_feed failed: {e}")

        # 2. Substack recommendations — one slot per entry.
        try:
            for entry in load_substack_feed():
                slots.append(SubstackSlot(payload=entry))
        except Exception as e:
            logma.warning(f"[ad_tab] load_substack_feed failed: {e}")

        # 3. Pro CTA — one slot, always present for Free users.
        slots.append(ProCtaSlot(payload={}))

        # 4. Affiliate banners — T-NEW-040 DESK-2: now drawn
        # from the curated QuickLinks catalog (via
        # _load_affiliate_rotation) instead of just the
        # base-layer / FALLBACK_BANNERS chain. _load_slots
        # tries the new server endpoint first, then falls
        # back to self.banners (which _load_banners already
        # populated) for offline-first behavior.
        try:
            from nchantdoffice.utilities.urls import server_base_url as _sbu

            api_base = _sbu()  # str — run-mode aware (T-NEW-053)
            try:
                # The AdTab's config may also carry an explicit API
                # base URL in models.yaml — cfg wins over run-mode.
                cfg_base = (
                    self.config.get("api_base_url", "")
                    if self.config else ""
                )
                if cfg_base:
                    api_base = cfg_base
            except Exception:
                pass
            affiliate_banners = _load_affiliate_rotation(
                api_base_url=api_base,
            )
        except Exception as e:
            logma.warning(
                f"[ad_tab] _load_affiliate_rotation failed: {e}; "
                f"using self.banners"
            )
            affiliate_banners = [
                {**b, "source": "external"} for b in self.banners
            ]
        for banner in affiliate_banners:
            slots.append(AffiliateSlot(payload=banner))

        # 5. T-NEW-040 DESK-2 — ProInternalSlot entries (in-house
        # cross-promos: Pro/ProData/white-label). Sourced from
        # the bundled PRO_INTERNAL_PROMOS list so the rotation
        # works offline. These entries fire
        # ``affiliate_click_internal`` (DESK-3) so revshare
        # reporting distinguishes in-house from third-party
        # affiliate clicks.
        try:
            for promo in load_pro_internal_promos():
                slots.append(ProInternalSlot(payload=promo))
        except Exception as e:
            logma.warning(
                f"[ad_tab] load_pro_internal_promos failed: {e}"
            )

        self.slots = slots
        logma.info(
            f"[ad_tab] loaded {len(self.slots)} slots "
            f"(tip=1, substack=multiple, pro_cta=1, "
            f"affiliate={len(affiliate_banners)}, "
            f"pro_internal={len(slots) - len(affiliate_banners) - 1})"
        )

    def _load_banners(self) -> None:
        """Fetch banners from the base-layer feed, then the
        affiliate API, then fall back to the local list.

        T-DESK-066: this method is kept as a backwards-compat
        shim — ``_load_slots()`` calls it to populate the
        affiliate tier of the rotation. It still mutates
        ``self.banners`` (the flat list shape) so any
        existing test that asserts on that shape keeps
        passing.

        T-DESK-063 (2026-08-07): the base-layer feed
        (``GET /api/ads/base-layer``) is the curated house-ad
        slate. It's the first source because:
          1. It's unauthenticated (works before registration).
          2. It's operator-managed (the operator can add/edit
             ads without a code change).
          3. It's cached locally (the desktop has ads even
             offline).

        The affiliate API (``fetch_banners``) is the second
        source — it returns campaign-targeted banners that
        may override the base layer.

        The hardcoded FALLBACK_BANNERS is the last resort
        when both server sources are unreachable.
        """
        # Step 1: Base-layer feed (cached, unauthenticated).
        try:
            from nchantdoffice.utilities.base_layer import (
                get_base_layer_ads,
            )
            base_ads = get_base_layer_ads()
            if base_ads:
                self.banners = base_ads
                logma.info(
                    f"[ad_tab] loaded {len(base_ads)} ads "
                    f"from base-layer feed"
                )
                return
        except Exception as e:
            logma.warning(f"[ad_tab] base-layer fetch failed: {e}")

        # Step 2: Affiliate API (campaign-targeted banners).
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

        # Step 3: Hardcoded fallback (always works, even offline).
        logma.info("[ad_tab] using local fallback banners")
        self.banners = list(FALLBACK_BANNERS)

    def _on_remove_ads_clicked(self) -> None:
        """Redirect the user to the Get Pro page in an in-app tab.

        Sprint 28 (toolbar parity): the same navigation that
        the Ad tab uses (Sprint 27) is now a public static
        helper (``redirect_to_get_pro``) on this module. The
        NchantdDocument toolbar's "Get Pro" button
        (``NchantdOfficeDocumentProfilePane.initView``,
        ``documents.py:378``) wired in the same
        ``switch_to_account_tab`` call that was silently
        no-op'ing on the live app — it now calls this helper
        instead.
        """
        NchantdOfficeAdTab.redirect_to_get_pro(self.app)

    # ------------------------------------------------------------------
    # Public navigation helper (Sprint 28)
    # ------------------------------------------------------------------

    @staticmethod
    def redirect_to_get_pro(app, reason: Optional[str] = None) -> bool:
        """Navigate the left-pane tree to the "Nchantd Account"
        tab (the embedded browser for the nchantdoffice_com
        account chain) so the user lands on the in-app Get Pro
        page instead of an external browser.

        T-NEW-135: ``reason`` is a free-form string that gets
        stashed on ``app.model.get_pro_redirect_reason`` so the
        destination ``NchantdOfficeAccountSettings`` widget
        can append it as a URL query parameter on next
        construction. The website reads the param to tailor
        its copy -- e.g. ``reason=hit_100_nodes`` shows a
        dedicated upsell for users who hit the 100-node cap.

        The stash is the single source of truth across the
        redirect / nav / settings-load race: the helper
        writes it, the settings widget reads + clears it.
        This is the shared helper used by:
          - the right-side Ad tab "Remove ads" button
            (``_on_remove_ads_clicked``)
          - the center-tab ``NchantdDocumentToolBar`` "Get Pro"
            button (``NchantdOfficeDocumentProfilePane.initView``
            in ``documents.py``).
          - the 100-node cap deny path
            (``NchantdOfficeCloakModel.add_node`` /
            ``add_node_app``).

        The nchantrs tree structure is two-layered:
          - ``app.view.panes["left"].tree`` is the inner
            ``NchantdApplicationTree`` (extends QTreeWidget
            directly, no set_current_node).
          - ``app.view.panes["left"].tree.view`` is the nchantrs
            ``NchantdTreeView`` wrapper at
            ``nchantrs/views/treeviews.py:38`` — that's the
            class that owns ``set_current_node`` (line 266).

        The actual navigation flow is:
          ``itemPressed`` (line 95) -> ``onLeftClick`` (line
          181) -> ``set_current_node(signal)`` (line 195) ->
          ``updateTabs('center')`` (line 275).

        Returns ``True`` when the navigation succeeded,
        ``False`` when it was skipped (graceful no-op).
        """
        # T-NEW-135: stash the reason BEFORE the navigation
        # dance so the destination widget sees it regardless
        # of whether the UI tree resolves. Failures in the
        # nav chain below MUST NOT erase the stash -- the
        # destination's ``initView`` will still pick it up.
        try:
            model = getattr(app, "model", None) if app is not None else None
            if model is not None:
                model.get_pro_redirect_reason = reason
        except Exception as e:
            logma.warning(
                f"[ad_tab] redirect_to_get_pro: stash failed: {e}"
            )

        # DESK T-NEW-052: route through the unified URL config.
        from nchantdoffice.utilities.urls import upgrade_compare_url
        target_url = upgrade_compare_url()
        try:
            view = getattr(app, "view", None) if app is not None else None
            if view is None:
                logma.info(
                    "[ad_tab] no app.view available; " "skipping redirect to %s",
                    target_url,
                )
                return False

            pane = getattr(view, "panes", {}).get("left")
            if pane is None:
                logma.info(
                    "[ad_tab] no left pane available; " "skipping redirect to %s",
                    target_url,
                )
                return False

            inner_tree = getattr(pane, "tree", None)
            if inner_tree is None:
                logma.info(
                    "[ad_tab] no inner tree on left pane; " "skipping redirect to %s",
                    target_url,
                )
                return False

            # Resolve the nchantrs treeview WRAPPER (not the
            # bare QTreeWidget) that owns set_current_node.
            tree_view = getattr(inner_tree, "view", None) or inner_tree

            # Locate the "Nchantd Account" node (the embedded
            # browser for the nchantdoffice_com account
            # chain). When missing, fall back to the Settings
            # node so the user at least lands on the group.
            account_items = inner_tree.findItems(
                "Nchantd Account",
                pyqt.Qt.MatchExactly | pyqt.Qt.MatchRecursive,
                0,
            )
            if not account_items:
                account_items = inner_tree.findItems(
                    "Settings",
                    pyqt.Qt.MatchExactly | pyqt.Qt.MatchRecursive,
                    0,
                )
            if not account_items:
                logma.info(
                    "[ad_tab] no Nchantd Account or Settings node "
                    "found in tree; user can navigate manually to "
                    "reach %s",
                    target_url,
                )
                return False

            target_item = account_items[0]

            # Navigate via the treeview wrapper when
            # available. Fall back to itemPressed event so
            # the wrapper's normal click pipeline runs as
            # if the user had clicked the node.
            if hasattr(tree_view, "set_current_node"):
                tree_view.set_current_node(target_item)
                logma.info(
                    "[ad_tab] routed to %s via " "tree_view.set_current_node",
                    target_item.text(0),
                )
                return True
            elif hasattr(inner_tree, "itemPressed"):
                from PySide6 import QtCore

                inner_tree.scrollToItem(target_item)
                QtCore.QCoreApplication.postEvent(
                    inner_tree.viewport(),
                    QtCore.QEvent(
                        QtCore.QEvent.Type.MouseButtonPress,
                    ),
                )
                logma.info(
                    "[ad_tab] routed to %s via itemPressed event",
                    target_item.text(0),
                )
                return True
            logma.info(
                "[ad_tab] no navigation path available; " "user can navigate manually to reach %s",
                target_url,
            )
            return False
        except Exception as e:
            logma.error(
                f"[ad_tab] failed to redirect to {target_url}: {e}",
                exc_info=True,
            )
            return False

    def _open_url(self, url) -> None:
        """Open an arbitrary URL in the default browser."""
        if not url:
            return
        try:
            pyqt.QDesktopServices.openUrl(pyqt.QUrl(url))
        except Exception as e:
            logma.error(f"[ad_tab] failed to open {url}: {e}", exc_info=True)

    def _make_open_url_handler(self, url) -> Callable[[], None]:
        """Return a slot that opens ``url`` on click (default-arg trick).

        Replacing the previous ``lambda checked=False, u=url:`` form
        with a named factory satisfies the lambda-antipattern
        auditor (the body is a Call expression) and makes the
        slot testable in isolation.
        """

        def _handler(_checked=False, _url=url) -> None:
            self._open_url(_url)

        return _handler

    @staticmethod
    def _make_open_url_handler_static(
        url,
        event_name=None,
        event_properties=None,
    ) -> Callable[[], None]:
        """T-DESK-066 — static counterpart of
        ``_make_open_url_handler``. The slot renderers
        (``SubstackSlot.render``, ``AffiliateSlot.render``,
        ``ProInternalSlot.render``) are unbound to ``self``
        at construction time, so they need a static factory
        to wire their CTA buttons. The factory closes over
        ``url`` via the default-arg trick (the same
        anti-pattern guard that ``_make_open_url_handler``
        uses).

        T-NEW-040 DESK-3 — added optional ``event_name`` +
        ``event_properties`` kwargs so the click handler can
        fire a telemetry event BEFORE opening the URL. Used
        by AffiliateSlot (affiliate_click_external) and
        ProInternalSlot (affiliate_click_internal).
        """
        def _handler(_checked=False, _url=url) -> None:
            # T-NEW-040 DESK-3 — fire the telemetry event
            # first so even no-op URL opens (e.g., blocked
            # browser launch) still get attributed.
            if event_name:
                try:
                    _emit_ad_telemetry(event_name, event_properties or {})
                except Exception as e:
                    logma.warning(
                        f"[ad_tab] telemetry emit failed "
                        f"({event_name}): {e}"
                    )
            try:
                pyqt.QDesktopServices.openUrl(pyqt.QUrl(_url))
            except Exception as e:
                logma.error(
                    f"[ad_tab] static handler failed to open {_url}: {e}",
                    exc_info=True,
                )

        return _handler


def _emit_ad_telemetry(event_name: str, properties: dict | None = None) -> None:
    """T-NEW-040 DESK-3 — fire an Ad tab telemetry event.

    Module-level helper (no self) so slot renderers can
    call it from inside ``_make_open_url_handler_static``.

    Currently no-ops safely if no app context is wired;
    future iterations can plumb this through to
    ``self.app.store_event(...)`` once the analytics
    pipeline (ATNRG T-NEW-029 telemetry events) is live.

    Args:
        event_name: one of the documented Ad tab events
            (e.g., ``affiliate_click_internal``,
            ``affiliate_click_external``).
        properties: optional dict of properties
            (slot_kind, destination_url, etc).
    """
    props = dict(properties or {})
    props.setdefault("event", event_name)
    props.setdefault("surface", "ad_tab")
    # Logma info-level so the event is visible in dev logs
    # without firing a real analytics call. The eventual
    # GA4 / Plausible integration (T-NEW-029) will replace
    # this with a real store_event() call.
    logma.info(
        f"[ad_tab] event={event_name} properties={props}"
    )


# Backwards-compat shim: old code referenced NchantdAdvertisementPane.
# Re-export so existing imports keep working.
NchantdAdvertisementPane = NchantdOfficeAdTab

# T-DESK-066: surface the new symbols in __all__ so test
# imports and any external callers can pick them up by
# ``from nchantdoffice.widgets.advertisements import …``.
__all__ = [
    "NchantdOfficeAdTab",
    "NchantdAdvertisementPane",
    "RotationSlot",
    "TipSlot",
    "SubstackSlot",
    "ProCtaSlot",
    "AffiliateSlot",
    "TIPS_FEED",
    "SUBSTACK_FEED",
    "load_tip_feed",
    "load_substack_feed",
]
