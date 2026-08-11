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

logma = Logma(__name__)

here = join(dirname(__file__), "")  # ||
pxcfg = join(here, "_data_", "advertisements.yaml")

# ---------------------------------------------------------------------------
# T-DESK-066 (paired with nchantdofficeATNRG/T-NEW-029) —
# four-slot Ad tab rotation: tip → substack → pro_cta → affiliate
# ---------------------------------------------------------------------------

# Default rotation interval (ms) — operator can override via
# advertisements.yaml: ``NchantdOfficeAdTab: { interval_ms: 12000 }``.
DEFAULT_INTERVAL_MS = 12000


# ---------------------------------------------------------------------------
# T-DESK-066 — local tip feed (mirrored from
# nchantdofficeATNRG/content/memes/tips.md, commit 48352d3).
#
# The desktop bundles the 30 productivity tips locally so the
# Ad tab rotation works offline. Operator updates this list
# when the ATNRG feed grows past 30.
#
# Markdown bold wrappers are tolerated (the ATNRG source uses
# **…**) — the renderer strips them before display.
# ---------------------------------------------------------------------------

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

    def render(self, parent):  # pragma: no cover - abstract
        """Return the QWidget to display for this slot."""
        raise NotImplementedError("subclasses must override render()")


@dataclass
class TipSlot(RotationSlot):
    """A productivity tip card (source: TIPS_FEED / ATNRG
    content/memes/tips.md). Renders the tip as a single
    full-width card with no CTA.
    """

    kind: str = "tip"

    def render(self, parent):
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

    def render(self, parent):
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

    def render(self, parent):
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

    def render(self, parent):
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

    def render(self, parent):
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
PRO_INTERNAL_PROMOS: list = [
    {
        "title": "nchantdoffice Pro — Remove ads + unlimited nodes",
        "subtitle": (
            "$20/mo or $200/yr. Unlock ProData (10K AI calls/mo) "
            "for $50/mo."
        ),
        "cta_text": "Upgrade to Pro",
        "cta_url": "https://nchantdoffice.com/compare",
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
        "cta_url": "https://nchantdoffice.com/compare#prodata",
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
        "cta_url": "https://nchantdoffice.com/contact",
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

    def __init__(self, parent=None, cfg=None):
        super().__init__("NchantdOfficeAdTab", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeAdTab").override(cfg))
        # T-DESK-066: the four-slot rotation engine state.
        # ``slots`` replaces the old flat ``banners`` list.
        # ``current_slot_index`` is the visible-slot pointer;
        # ``_timer`` is the QTimer that advances it.
        self.slots: list = []
        self.current_slot_index: int = 0
        self._timer = None
        # Kept as a backwards-compat shim (some tests still
        # assert on the flat shape).
        self.banners: list = []
        self._user = None

    def initModel(self, cfg=None):
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

    def show_referral_url(self, url):
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
        # (and crucially, we never start the rotation timer
        # for Pro users, even though initModel already loaded
        # the slots — the slots exist but never animate).
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

        # T-DESK-066: single visible-slot container.
        # The QTimer in ``_start_rotation`` advances
        # ``current_slot_index`` and re-renders this container.
        self._slot_container = NchantdVScrollGroupBox(self)
        self._slot_container.setTitle("")
        if not self.slots:
            placeholder = NchantdLabel(self._slot_container)
            placeholder.setText("<i>No ads available right now.</i>")
            self._slot_container.addWidget(placeholder)
        else:
            self._render_current_slot()
        layout.addWidget(self._slot_container)

        # Manual advance button (lets the user cycle without
        # waiting for the timer — a common UX nicety for
        # rotation-style ad panels).
        adv_row = pyqt.QHBoxLayout()
        adv_row.setContentsMargins(0, 0, 0, 0)
        adv_row.setSpacing(6)
        next_btn = NchantdButton(self)
        next_btn.setText("Next \u203a")
        next_btn.clicked.connect(self._advance_slot)
        adv_row.addWidget(next_btn)
        adv_row.addStretch(1)
        layout.addLayout(adv_row)

        self.layout.addLayout(layout)

        # Start the rotation timer (Free users only — the
        # Pro short-circuit above returned early).
        self._start_rotation()
        return cfg

    def _render_current_slot(self):
        """Render the slot at ``self.current_slot_index`` into
        the ``_slot_container``. Clears the container first so
        only one slot is visible at a time (the rotation, not
        a stack).

        T-DESK-066 step 6.

        Runtime bug fix (2026-08-11): ``NchantdVScrollGroupBox``
        is a QWidget (extends NchantdWidget) — it has no
        ``count()`` method. The ``count()`` and ``takeAt()``
        live on its inner ``layout_box`` (a QVBoxLayout). The
        previous code called ``self._slot_container.count()``
        which raised ``AttributeError`` 4x in the 11:27 log.
        Now we operate on the layout instead.
        """
        try:
            # Remove every child widget from the container.
            # The container's children are added via
            # ``addWidget()`` (line 720) which delegates to
            # ``self._slot_container.layout_box.addWidget()``.
            # To remove them, iterate over the layout_box.
            layout_box = self._slot_container.layout_box
            for i in reversed(range(layout_box.count())):
                item = layout_box.takeAt(i)
                w = item.widget() if item is not None else None
                if w is not None:
                    w.setParent(None)
                    w.deleteLater()
        except Exception as e:
            logma.warning(f"[ad_tab] _render_current_slot clear failed: {e}")

        if not self.slots:
            placeholder = NchantdLabel(self._slot_container)
            placeholder.setText("<i>No ads available right now.</i>")
            self._slot_container.addWidget(placeholder)
            return

        idx = self.current_slot_index % len(self.slots)
        slot = self.slots[idx]
        try:
            widget = slot.render(self._slot_container)
            self._slot_container.addWidget(widget)
            # Wire the Pro CTA's button (the only slot whose
            # click handler needs ``self``).
            btn = getattr(widget, "_pro_cta_button", None)
            if btn is not None:
                btn.clicked.connect(self._on_remove_ads_clicked)
        except Exception as e:
            logma.warning(
                f"[ad_tab] render slot[{idx}] ({slot.kind}) failed: {e}"
            )

    def _advance_slot(self):
        """QTimer callback + manual advance handler.

        Increments ``current_slot_index`` and wraps to 0 after
        the last slot. Re-renders the visible-slot container.

        T-DESK-066 step 5.
        """
        if not self.slots:
            return
        # Wrap with modulo so the rotation is cyclic. ``%`` on
        # the post-increment value avoids an off-by-one when
        # ``current_slot_index`` is incremented from len-1.
        self.current_slot_index = (self.current_slot_index + 1) % len(self.slots)
        try:
            self._render_current_slot()
        except Exception as e:
            logma.warning(f"[ad_tab] _advance_slot re-render failed: {e}")

    def _start_rotation(self):
        """Start the QTimer that drives the slot rotation.

        T-DESK-066 step 5. The interval is configurable via
        ``advertisements.yaml`` (key: ``interval_ms``,
        default ``DEFAULT_INTERVAL_MS`` = 12000). Pro users
        never reach this code path (initView returns early).
        """
        try:
            interval_ms = int(
                self.config.dikt.get("interval_ms", DEFAULT_INTERVAL_MS)
            )
        except Exception:
            interval_ms = DEFAULT_INTERVAL_MS
        self._timer = pyqt.QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._advance_slot)
        self._timer.start()
        logma.info(
            f"[ad_tab] rotation started (interval={interval_ms}ms, "
            f"slots={len(self.slots)})"
        )

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

    def _load_slots(self):
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
            api_base = ""
            try:
                # The AdTab's config may carry the API base URL
                # in models.yaml — try to read it. We use a
                # permissive get() so this never crashes; an
                # empty string means _load_affiliate_rotation
                # uses the relative URL.
                api_base = (self.config.get("api_base_url", "")
                            if self.config else "")
            except Exception:
                api_base = ""
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

    def _load_banners(self):
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

    def _on_remove_ads_clicked(self):
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
    def redirect_to_get_pro(app):
        """Navigate the left-pane tree to the "Nchantd Account"
        tab (the embedded browser for the nchantdoffice_com
        account chain) so the user lands on the in-app Get Pro
        page instead of an external browser.

        This is the shared helper used by:
          - the right-side Ad tab "Remove ads" button
            (``_on_remove_ads_clicked``)
          - the center-tab ``NchantdDocumentToolBar`` "Get Pro"
            button (``NchantdOfficeDocumentProfilePane.initView``
            in ``documents.py``).

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
        target_url = "https://www.nchantdoffice.com/compare"
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

    @staticmethod
    def _make_open_url_handler_static(
        url,
        event_name=None,
        event_properties=None,
    ):
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
        def _handler(_checked=False, _url=url):
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
