"""T-DESK-066 (paired with nchantdofficeATNRG/T-NEW-029) — Ad tab
rotation contract regression tests.

The right-side Ad tab must rotate between four content slot
types on a QTimer:

  1. TipSlot         — productivity tip from the local TIPS_FEED
  2. SubstackSlot    — featured Substack rec from SUBSTACK_FEED
  3. ProCtaSlot      — "Remove ads - Go Pro" CTA (existing)
  4. AffiliateSlot   — affiliate/team-pack banner (existing)

These tests pin the contract that:
  - the source file exposes the four RotationSlot dataclasses
    with a stable ``kind`` string
  - ``TIPS_FEED`` has ≥ 30 non-empty tip strings (the ATNRG
    ``content/memes/tips.md`` count)
  - ``SUBSTACK_FEED`` has ≥ 3 entries with the expected keys
    (title, url, blurb)
  - ``_load_slots()`` calls the four sources in the canonical
    order [tip, substack, pro_cta, affiliate]
  - the QTimer is configured with a non-zero interval and is
    never started when the user is Pro
  - the timer slot-advance callback wraps ``current_slot_index``
    to 0 after the last slot
  - the existing ``_on_remove_ads_clicked`` still delegates to
    ``redirect_to_get_pro`` (no regression from the rotation
    refactor)
  - ``_load_banners`` is kept as a backwards-compat shim that
    still mutates ``self.banners`` for AffiliateSlot entries

Tests are AST-based where possible so they run without a Qt
event loop and without the full nchantdoffice import chain
(the live module imports ``pycurity.pycrypt`` which requires
``base58`` — the same pattern used by
``test_ad_tab_redirect.py``).

Refs:
  - nchantdofficeATNRG/TODOS.md T-NEW-029 (commit b06e022)
  - nchantdofficeATNRG/0-5kpm-revenue-plan.md §"Symbiosis
    Substack Strategy" §4 (Example rotation slots)
  - nchantdofficeATNRG/content/memes/tips.md (commit 48352d3)
"""

import ast
import re
import sys
from pathlib import Path

import pytest

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

AD_TAB = PROJ_ROOT / "nchantdoffice" / "widgets" / "advertisements.py"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    return path.read_text()


def _ast_top_level(src: str, kind, name: str):
    """Return the first top-level node of ``kind`` whose name
    matches ``name`` (ClassDef/FunctionDef/Assign)."""
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, kind):
            if kind is ast.ClassDef and node.name == name:
                return node
            if kind is ast.FunctionDef and node.name == name:
                return node
            if kind is ast.Assign:
                # Name targets: ``TIPS_FEED: list = [...]``
                for tgt in node.targets:
                    if (
                        isinstance(tgt, ast.Name)
                        and tgt.id == name
                    ):
                        return node
            if kind is ast.AnnAssign:
                # ``TIPS_FEED: list = [...]``
                if (
                    isinstance(node.target, ast.Name)
                    and node.target.id == name
                ):
                    return node
    return None


def _ast_class(src: str, name: str):
    """Return the first ClassDef whose name matches."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _ast_function(src: str, name: str):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _function_source(src: str, name: str) -> str:
    node = _ast_function(src, name)
    if node is None:
        return ""
    return ast.get_source_segment(src, node) or ""


def _class_source(src: str, name: str) -> str:
    node = _ast_class(src, name)
    if node is None:
        return ""
    return ast.get_source_segment(src, node) or ""


def _eval_list_literal_node(node: ast.List) -> list:
    """Materialize a static ``[...]`` literal from the AST.

    Only handles the shapes used by TIPS_FEED (str elements)
    and SUBSTACK_FEED (dict elements with str values). Anything
    fancier raises so the test fails loudly instead of
    silently passing on a degraded parse.
    """
    out = []
    for elt in node.elts:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            out.append(elt.value)
        elif isinstance(elt, ast.Dict):
            d = {}
            for k, v in zip(elt.keys, elt.values):
                if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
                    raise ValueError(f"non-str dict key: {ast.dump(k)}")
                if not (isinstance(v, ast.Constant) and isinstance(v.value, str)):
                    raise ValueError(f"non-str dict value: {ast.dump(v)}")
                d[k.value] = v.value
            out.append(d)
        else:
            raise ValueError(f"unsupported list element: {ast.dump(elt)}")
    return out


def _module_top_level_list(src: str, name: str) -> list:
    """Return the materialized list assigned to top-level
    ``name``. Supports both bare ``X = [...]`` and
    annotated ``X: list = [...]``."""
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == name:
                    if isinstance(node.value, ast.List):
                        return _eval_list_literal_node(node.value)
        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == name
                and isinstance(node.value, ast.List)
            ):
                return _eval_list_literal_node(node.value)
    raise ValueError(f"no top-level list literal named {name!r}")


# ---------------------------------------------------------------------------
# Contract 1: RotationSlot dataclass + four concrete subclasses exist
# ---------------------------------------------------------------------------


def test_rotation_slot_base_class_exists():
    """The four-slot rotation is anchored by a ``RotationSlot``
    base dataclass with ``kind`` and ``render`` attributes.

    Pinning the names here lets the loaders and the renderer
    agree on the rotation contract.
    """
    src = _read(AD_TAB)
    base = _ast_class(src, "RotationSlot")
    assert base is not None, (
        "advertisements.py must declare a RotationSlot base "
        "class (the anchor for the four-slot rotation)."
    )
    # Must be decorated with @dataclass.
    for dec in base.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "dataclass":
            break
    else:
        raise AssertionError(
            "RotationSlot must be decorated with @dataclass."
        )
    body = _class_source(src, "RotationSlot")
    assert "kind" in body, "RotationSlot must carry a 'kind' field."
    assert "render" in body, "RotationSlot must carry a 'render' method."


def test_rotation_slot_subclasses_exist():
    """All four slot subclasses must exist with the documented kinds."""
    src = _read(AD_TAB)
    for cls, kind in [
        ("TipSlot", "tip"),
        ("SubstackSlot", "substack"),
        ("ProCtaSlot", "pro_cta"),
        ("AffiliateSlot", "affiliate"),
    ]:
        node = _ast_class(src, cls)
        assert node is not None, (
            f"advertisements.py must declare {cls} (kind={kind!r})."
        )
        # All four must subclass RotationSlot (the anchor).
        base_names = {
            b.id if isinstance(b, ast.Name) else ast.unparse(b)
            for b in node.bases
        }
        assert "RotationSlot" in base_names, (
            f"{cls} must subclass RotationSlot."
        )
        body = _class_source(src, cls)
        assert f'"{kind}"' in body or f"'{kind}'" in body, (
            f"{cls} must declare its kind as the literal string "
            f"{kind!r} (used by _load_slots for ordering)."
        )


# ---------------------------------------------------------------------------
# Contract 2: TIPS_FEED has ≥ 30 tips
# ---------------------------------------------------------------------------


def test_tips_feed_has_at_least_thirty_entries():
    """``TIPS_FEED`` must have ≥ 30 entries (the ATNRG
    ``content/memes/tips.md`` count, commit 48352d3). The
    desktop bundles the 30 tips locally so the rotation
    works offline — exactly the same offline-first pattern
    as ``FALLBACK_BANNERS``.
    """
    src = _read(AD_TAB)
    tips = _module_top_level_list(src, "TIPS_FEED")
    assert len(tips) >= 30, (
        f"TIPS_FEED must have ≥ 30 entries (the ATNRG "
        f"content/memes/tips.md count), got {len(tips)}."
    )
    for i, tip in enumerate(tips):
        assert isinstance(tip, str), (
            f"tips[{i}] must be a str, got {type(tip).__name__}."
        )
        assert tip.strip(), f"tips[{i}] must be non-empty."
        # Markdown bold (**…**) wrappers are tolerated but the
        # raw text must be at least 20 chars (the ATNRG tips
        # are short paragraphs).
        stripped = re.sub(r"\*+", "", tip).strip()
        assert len(stripped) >= 20, (
            f"tips[{i}] is suspiciously short ({len(stripped)} chars)."
        )


def test_tips_feed_contains_ctrl_shift_t_anchor():
    """At least one tip must mention Ctrl+Shift+T (the canonical
    'reopen closed tab' tip — the first one in ATNRG tips.md).
    The test pins the bundle so it can't drift silently to a
    different set.
    """
    src = _read(AD_TAB)
    tips = _module_top_level_list(src, "TIPS_FEED")
    blob = " ".join(tips).lower()
    assert "ctrl" in blob and "shift" in blob and "tab" in blob, (
        "TIPS_FEED must contain the canonical Ctrl+Shift+T "
        "'reopen closed tab' tip from ATNRG content/memes/tips.md."
    )


def test_load_tip_feed_helper_exists_and_returns_tips_feed():
    """``load_tip_feed()`` must exist as a module-level helper
    and return a copy of TIPS_FEED (the static fallback chain
    — never a server call, always works offline).
    """
    src = _read(AD_TAB)
    fn = _ast_function(src, "load_tip_feed")
    assert fn is not None, (
        "advertisements.py must declare load_tip_feed() "
        "as a module-level helper (returns TIPS_FEED)."
    )
    body = _function_source(src, "load_tip_feed")
    assert "TIPS_FEED" in body, (
        "load_tip_feed() must return TIPS_FEED (or a copy)."
    )


# ---------------------------------------------------------------------------
# Contract 3: SUBSTACK_FEED has ≥ 3 entries
# ---------------------------------------------------------------------------


def test_substack_feed_has_at_least_three_entries():
    """``SUBSTACK_FEED`` must have ≥ 3 hand-curated Substack
    recommendations (the ATNRG revenue plan §"Quick Starting
    List" step 5 recommends "3-5 of the strongest ones into
    your Ad tab rotation").

    Each entry must have title, url, and blurb (the symbiosis
    reciprocal placement — short description + link).
    """
    src = _read(AD_TAB)
    feed = _module_top_level_list(src, "SUBSTACK_FEED")
    assert len(feed) >= 3, (
        f"SUBSTACK_FEED must have ≥ 3 entries (ATNRG revenue "
        f"plan Quick Starting List step 5), got {len(feed)}."
    )
    for i, entry in enumerate(feed):
        assert isinstance(entry, dict), (
            f"substack[{i}] must be a dict, got {type(entry).__name__}."
        )
        for key in ("title", "url", "blurb"):
            assert key in entry, (
                f"substack[{i}] missing required key {key!r}."
            )
            assert isinstance(entry[key], str) and entry[key].strip(), (
                f"substack[{i}][{key!r}] must be a non-empty string."
            )
        # URL sanity — must be an https URL.
        assert entry["url"].startswith("https://"), (
            f"substack[{i}].url must be an https URL "
            f"(got {entry['url']!r})."
        )


def test_load_substack_feed_helper_exists_and_returns_substack_feed():
    """``load_substack_feed()`` must exist as a module-level
    helper and return SUBSTACK_FEED (or a copy).
    """
    src = _read(AD_TAB)
    fn = _ast_function(src, "load_substack_feed")
    assert fn is not None, (
        "advertisements.py must declare load_substack_feed() "
        "as a module-level helper (returns SUBSTACK_FEED)."
    )
    body = _function_source(src, "load_substack_feed")
    assert "SUBSTACK_FEED" in body, (
        "load_substack_feed() must return SUBSTACK_FEED (or a copy)."
    )


# ---------------------------------------------------------------------------
# Contract 4: _load_slots() ordering (tip → substack → pro → affiliate)
# ---------------------------------------------------------------------------


def test_load_slots_returns_canonical_order():
    """``_load_slots()`` must build the rotation in the
    canonical order documented in T-NEW-029 step 4:

      [tip (1)] + [substack (≥ 3)] + [pro_cta (1)] + [affiliate (≥ 1)]

    Pinning the order (not just the kinds) is what makes the
    rotation visibly follow the ATNRG revenue plan §"Example
    rotation slots".
    """
    src = _read(AD_TAB)
    fn = _ast_function(src, "_load_slots")
    assert fn is not None, (
        "advertisements.py must declare _load_slots() "
        "(replacing the flat _load_banners() helper)."
    )
    body = _function_source(src, "_load_slots")
    # All four sources must be appended in the documented order.
    assert "load_tip_feed" in body, (
        "_load_slots must call load_tip_feed() first (1 tip)."
    )
    assert "load_substack_feed" in body, (
        "_load_slots must call load_substack_feed() next "
        "(≥ 3 Substack entries)."
    )
    assert "ProCtaSlot" in body, (
        "_load_slots must append a ProCtaSlot (1 Pro CTA)."
    )
    assert "AffiliateSlot" in body, (
        "_load_slots must append AffiliateSlot entries "
        "(the existing affiliate/team-pack banner chain)."
    )
    # Tip must come before Substack before Pro before Affiliate.
    tip_pos = body.find("load_tip_feed")
    sub_pos = body.find("load_substack_feed")
    pro_pos = body.find("ProCtaSlot")
    aff_pos = body.find("AffiliateSlot")
    assert -1 < tip_pos < sub_pos < pro_pos < aff_pos, (
        "_load_slots() must append in canonical order "
        "[tip, substack, pro_cta, affiliate] "
        f"(got positions tip={tip_pos}, "
        f"sub={sub_pos}, pro={pro_pos}, aff={aff_pos})."
    )


# ---------------------------------------------------------------------------
# Contract 5: _start_surface_timer exists and wires the server-driven cadence
# ---------------------------------------------------------------------------


def test_start_surface_timer_exists_and_uses_surface_interval():
    """``_start_surface_timer()`` must exist and read the
    server-driven surface cadence from config, falling back to
    ``DEFAULT_SURFACE_INTERVAL_MS`` (5 minutes).

    DESK T-NEW-061: replaced the previous local 5-second
    slot rotation with a server-driven fetch that re-asks
    ``GET /api/ads/rotation/next`` every 5 minutes. The
    QTimer callback is ``_fetch_and_render`` (not the old
    ``_advance_slot`` local cycler).
    """
    src = _read(AD_TAB)
    fn = _ast_function(src, "_start_surface_timer")
    assert fn is not None, (
        "advertisements.py must declare _start_surface_timer() "
        "(the QTimer that re-asks the server every 5 minutes)."
    )
    body = _function_source(src, "_start_surface_timer")
    assert "DEFAULT_SURFACE_INTERVAL_MS" in body, (
        "_start_surface_timer must reference DEFAULT_SURFACE_INTERVAL_MS."
    )
    assert "setInterval" in body, (
        "_start_surface_timer must call .setInterval() on the QTimer."
    )
    # The timer must call _fetch_and_render, not the old _advance_slot.
    assert "_fetch_and_render" in body, (
        "_start_surface_timer must connect the QTimer to _fetch_and_render "
        "(the server-driven ad fetch, not the old local slot cycler)."
    )


# ---------------------------------------------------------------------------
# Contract 6: initView wires QTimer for Free users only
# ---------------------------------------------------------------------------


def test_initView_starts_surface_timer_for_free_users_only():
    """``initView()`` must start the server-driven surface
    timer for Free users and never start it for Pro users
    (the existing ``_is_visible_for_user`` short-circuit).
    The Pro-user path must NOT reference QTimer.

    DESK T-NEW-061: the timer configuration lives in
    ``_start_surface_timer()`` — ``initView`` delegates to it.
    The contract is that the Pro check happens BEFORE the
    timer starts.
    """
    src = _read(AD_TAB)
    body = _function_source(src, "initView")
    assert "_start_surface_timer" in body, (
        "initView must delegate QTimer startup to "
        "_start_surface_timer() (the configuration lives there)."
    )
    # The Pro short-circuit must come BEFORE the surface timer call.
    is_visible = body.find("_is_visible_for_user")
    start_timer = body.find("_start_surface_timer")
    assert -1 < is_visible < start_timer, (
        "initView must check _is_visible_for_user BEFORE "
        "calling _start_surface_timer (Pro users get no timer)."
    )


# ---------------------------------------------------------------------------
# Contract 6b: _start_surface_timer uses the surface cadence (5 min)
# ---------------------------------------------------------------------------


def test_start_surface_timer_uses_5min_cadence():
    """``_start_surface_timer()`` must read ``surface_ms`` from
    ``self.config`` (advertisements.yaml) and fall back to
    ``DEFAULT_SURFACE_INTERVAL_MS`` (300_000 ms = 5 minutes).
    """
    src = _read(AD_TAB)
    body = _function_source(src, "_start_surface_timer")
    assert body, "advertisements.py must declare _start_surface_timer()."
    assert "DEFAULT_SURFACE_INTERVAL_MS" in body, (
        "_start_surface_timer must reference DEFAULT_SURFACE_INTERVAL_MS."
    )
    assert "setInterval" in body, (
        "_start_surface_timer must call .setInterval() on the QTimer."
    )


# ---------------------------------------------------------------------------
# Contract 7: no regression on the existing 'Remove ads' redirect
# ---------------------------------------------------------------------------


def test_remove_ads_handler_still_delegates_to_redirect_helper():
    """The Sprint 28 contract (the redirect_to_get_pro helper
    is shared by both the Ad tab 'Remove ads' button AND the
    center-tab toolbar 'Get Pro' button) must survive the
    rotation refactor.
    """
    src = _read(AD_TAB)
    body = _function_source(src, "_on_remove_ads_clicked")
    assert "redirect_to_get_pro" in body, (
        "Ad tab 'Remove ads' handler must still delegate to "
        "NchantdOfficeAdTab.redirect_to_get_pro after the "
        "T-DESK-066 rotation refactor."
    )


# ---------------------------------------------------------------------------
# Contract 8: backwards-compat shim — _load_banners kept
# ---------------------------------------------------------------------------


def test_load_banners_kept_as_backwards_compat():
    """Existing callers (and the base-layer test) depend on
    ``_load_banners()`` returning the same flat list shape
    it returned before the refactor. Keep it as a thin shim
    that still mutates ``self.banners`` for AffiliateSlot
    entries.
    """
    src = _read(AD_TAB)
    fn = _ast_function(src, "_load_banners")
    assert fn is not None, (
        "_load_banners must be kept as a backwards-compat "
        "shim (still mutates self.banners)."
    )
    body = _function_source(src, "_load_banners")
    assert "self.banners" in body, (
        "_load_banners shim must still mutate self.banners "
        "so existing tests keep passing."
    )
    assert "FALLBACK_BANNERS" in body, (
        "_load_banners shim must still fall back to "
        "FALLBACK_BANNERS when both server sources are unreachable."
    )


# ---------------------------------------------------------------------------
# Contract 9: __all__ exposes the new public symbols
# ---------------------------------------------------------------------------


def test_module_dunder_all_lists_new_symbols():
    """``__all__`` must list the new public symbols so
    ``from nchantdoffice.widgets.advertisements import …``
    works for test imports and external callers.
    """
    src = _read(AD_TAB)
    tree = ast.parse(src)
    found = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "__all__":
                    if isinstance(node.value, ast.List):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(
                                elt.value, str
                            ):
                                found.append(elt.value)
    assert found, "advertisements.py must declare __all__."
    for sym in (
        "RotationSlot",
        "TipSlot",
        "SubstackSlot",
        "ProCtaSlot",
        "AffiliateSlot",
        "load_tip_feed",
        "load_substack_feed",
        "TIPS_FEED",
        "SUBSTACK_FEED",
    ):
        assert sym in found, (
            f"__all__ must include {sym!r} (T-DESK-066 export)."
        )


# ---------------------------------------------------------------------------
# Contract 10: dead-code removal — _build_banner_card is gone
# ---------------------------------------------------------------------------


def test_build_banner_card_is_removed():
    """T-DESK-066 step 6 cleanup: the legacy
    ``_build_banner_card`` helper was deleted once its
    visual language was absorbed into
    ``AffiliateSlot.render()``. Pinning the absence so a
    future refactor can't accidentally resurrect the dead
    helper alongside the new render() path.
    """
    src = _read(AD_TAB)
    assert _ast_function(src, "_build_banner_card") is None, (
        "_build_banner_card must be removed — its visual "
        "language was absorbed into AffiliateSlot.render() "
        "during the T-DESK-066 step-6 cleanup. If you need "
        "a card builder, add a static method on RotationSlot "
        "instead of resurrecting this helper."
    )


# ---------------------------------------------------------------------------
# Contract 11: cross-repo parity — desktop TIPS_FEED must mirror ATNRG
# ---------------------------------------------------------------------------


def test_tips_feed_count_matches_atnrg_source():
    """R-1 release checklist (docs/cross-repo-review_20260807.md):
    the desktop ``TIPS_FEED`` is the bundled mirror of
    ``nchantdofficeATNRG/content/memes/tips.md``. When the
    ATNRG source adds/removes tips, the desktop bundle must
    be updated in lockstep.

    The test asserts ``len(TIPS_FEED) >= len(atnrg_tips)`` —
    the desktop bundle is allowed to grow beyond the source
    (operators may add extra tips that haven't yet landed
    upstream), but it must never silently drop below it
    (that would mean an ATNRG update was forgotten).

    The Ctrl+Shift+T anchor from R-1 step 4 is already
    pinned by ``test_tips_feed_contains_ctrl_shift_t_anchor``
    above, so an ATNRG rewrite that drops the canonical tip
    is caught separately.
    """
    src = _read(AD_TAB)
    desktop_tips = _module_top_level_list(src, "TIPS_FEED")

    atnrg_path = (
        PROJ_ROOT.parent
        / "nchantdofficeATNRG"
        / "content"
        / "memes"
        / "tips.md"
    )
    if not atnrg_path.exists():
        # The ATNRG checkout isn't always co-located with the
        # desktop repo (e.g. CI without the marketing repo).
        # Skip rather than fail — the local tip count pin in
        # ``test_tips_feed_has_at_least_thirty_entries``
        # still guards the absolute floor.
        import pytest

        pytest.skip(
            f"ATNRG tips.md not found at {atnrg_path} — skip "
            "cross-repo parity check (ATNRG repo not present "
            "in this checkout)."
        )

    atnrg_text = atnrg_path.read_text()
    # ATNRG tips.md uses numbered markdown list items like
    # ``1. **Use Ctrl + Shift + T** …``. Count them.
    import re as _re

    atnrg_tips = _re.findall(r"^\s*\d+\.\s+", atnrg_text, flags=_re.MULTILINE)

    assert len(desktop_tips) >= len(atnrg_tips), (
        f"desktop TIPS_FEED has {len(desktop_tips)} tips but "
        f"ATNRG content/memes/tips.md has {len(atnrg_tips)} — "
        "the desktop bundle fell behind the marketing source. "
        "Follow the R-1 mirror steps in "
        "docs/cross-repo-review_20260807.md."
    )


# ---------------------------------------------------------------------------
# Contract 12: release-checklist doc exists with the R-1 mirror steps
# ---------------------------------------------------------------------------


def test_release_checklist_documents_tips_mirror_steps():
    """R-1 release checklist: the tip-mirror procedure must
    be documented somewhere visible. The desktop docs at
    ``docs/cross-repo-review_20260807.md`` carry the R-1
    section (added 2026-08-07 during T-DESK-066).

    Pinning this here so a future cleanup can't silently
    remove the procedure and leave the next operator
    guessing how to mirror ATNRG content updates.
    """
    doc_path = PROJ_ROOT / "docs" / "cross-repo-review_20260807.md"
    assert doc_path.exists(), (
        "docs/cross-repo-review_20260807.md must exist "
        "(the R-1 release checklist lives there)."
    )
    text = doc_path.read_text()
    assert "## Release checklist" in text, (
        "docs/cross-repo-review_20260807.md must include a "
        "'## Release checklist' section (added for T-DESK-066)."
    )
    assert "R-1" in text and "Mirror" in text, (
        "Release checklist must include the R-1 mirror step "
        "for ATNRG content/memes/tips.md → TIPS_FEED."
    )
    assert "TIPS_FEED" in text, (
        "Release checklist must name the TIPS_FEED symbol "
        "(the bundled mirror target)."
    )
    assert "content/memes/tips.md" in text, (
        "Release checklist must name the ATNRG source path "
        "content/memes/tips.md."
    )


# ---------------------------------------------------------------------------
# T-NEW-040 DESK-1 — ProInternalSlot dataclass.
# ---------------------------------------------------------------------------


def test_pro_internal_slot_exists():
    """T-NEW-040 DESK-1: ProInternalSlot class added to the rotation.

    New slot type for in-house cross-promos (nchantdoffice Pro,
    ProData, white-label). Same shape as AffiliateSlot but with
    ``kind: str = "pro_internal"`` so telemetry can split
    external vs internal affiliate clicks (DESK-3).
    """
    src = _read(AD_TAB)
    cls = _ast_class(src, "ProInternalSlot")
    assert cls is not None, (
        "advertisements.py must declare ProInternalSlot "
        "(T-NEW-040 — in-house cross-promos)"
    )
    bases = [ast.unparse(b) for b in cls.bases]
    assert any("RotationSlot" in b for b in bases), (
        "ProInternalSlot must subclass RotationSlot"
    )
    body = _class_source(src, "ProInternalSlot")
    assert 'kind: str = "pro_internal"' in body, (
        "ProInternalSlot.kind must be 'pro_internal'"
    )
    assert "def render(self" in body, (
        "ProInternalSlot must implement render(parent)"
    )


def test_pro_internal_slot_render_uses_banner_card_shape():
    """ProInternalSlot.render() must use the same card shape
    as AffiliateSlot so the rotation looks consistent. The
    simplest assertion: it uses NchantdGridScrollGroupBox
    (the canonical banner card widget).
    """
    src = _read(AD_TAB)
    body = _class_source(src, "ProInternalSlot")
    assert "NchantdGridScrollGroupBox" in body, (
        "ProInternalSlot.render must use NchantdGridScrollGroupBox"
    )


def test_pro_internal_promos_constant_exists():
    """The bundled PRO_INTERNAL_PROMOS list must exist and
    contain at least 3 entries (Pro, ProData, white-label)."""
    src = _read(AD_TAB)
    tree = ast.parse(src)
    found = None
    for node in tree.body:
        if isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == "PRO_INTERNAL_PROMOS"
            ):
                found = node
                break
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                if (
                    isinstance(tgt, ast.Name)
                    and tgt.id == "PRO_INTERNAL_PROMOS"
                ):
                    found = node
                    break
            if found:
                break
    assert found is not None, (
        "PRO_INTERNAL_PROMOS module-level constant must exist "
        "(T-NEW-040 DESK-1)"
    )
    assert isinstance(found.value, ast.List), (
        "PRO_INTERNAL_PROMOS must be a list literal"
    )
    assert len(found.value.elts) >= 3, (
        f"PRO_INTERNAL_PROMOS must have ≥3 entries, got {len(found.value.elts)}"
    )


def test_load_pro_internal_promos_helper_exists():
    """load_pro_internal_promos() returns a copy of PRO_INTERNAL_PROMOS
    so callers can't mutate the module-level constant. Mirrors
    the pattern of load_tip_feed() / load_substack_feed()."""
    src = _read(AD_TAB)
    fn = _ast_function(src, "load_pro_internal_promos")
    assert fn is not None, (
        "load_pro_internal_promos() helper must exist "
        "(T-NEW-040 DESK-1)"
    )
    body = _function_source(src, "load_pro_internal_promos")
    assert "PRO_INTERNAL_PROMOS" in body, (
        "load_pro_internal_promos must return PRO_INTERNAL_PROMOS"
    )


def test_pro_internal_promos_have_required_keys():
    """Each PRO_INTERNAL_PROMOS entry must have the keys
    AffiliateSlot.render() expects: title, subtitle (optional),
    cta_text + cta_url, background, foreground."""
    src = _read(AD_TAB)
    tree = ast.parse(src)
    node = None
    for n in tree.body:
        if isinstance(n, ast.AnnAssign):
            if (
                isinstance(n.target, ast.Name)
                and n.target.id == "PRO_INTERNAL_PROMOS"
            ):
                node = n
                break
    assert node is not None
    assert isinstance(node.value, ast.List)
    for elt in node.value.elts:
        assert isinstance(elt, ast.Dict), (
            "Each PRO_INTERNAL_PROMOS entry must be a dict literal"
        )
        keys = {
            k.value for k in elt.keys
            if isinstance(k, ast.Constant)
        }
        assert "title" in keys, "each entry must have 'title'"
        assert "cta_text" in keys, "each entry must have 'cta_text'"
        assert "cta_url" in keys, "each entry must have 'cta_url'"
        assert "background" in keys, "each entry must have 'background'"
        assert "foreground" in keys, "each entry must have 'foreground'"


# ---------------------------------------------------------------------------
# T-NEW-040 DESK-2 — _load_affiliate_rotation() helper +
# AffiliateSlot.source field + ProInternalSlot wiring in _load_slots.
# ---------------------------------------------------------------------------


def test_affiliate_slot_has_source_field():
    """T-NEW-040 DESK-2: AffiliateSlot must carry a ``source``
    field so the click handler in DESK-3 can fire the right
    telemetry event. Allowed values: 'external' (default,
    third-party QuickLinks) or 'internal' (in-house
    ProInternalSlot passthrough).

    The test pins the field as an annotated dataclass member
    (``source: str = "external"``) — not just any occurrence
    of the word 'source' in a docstring/comment.
    """
    src = _read(AD_TAB)
    cls = _ast_class(src, "AffiliateSlot")
    assert cls is not None
    body_src = _class_source(src, "AffiliateSlot")
    # Strip comments and docstrings to avoid false positives
    tree = ast.parse(body_src)
    cls_node = next(
        n for n in tree.body
        if isinstance(n, ast.ClassDef)
    )
    # Look for ``source: str = ...`` annotation in the class body
    found_source_field = False
    for stmt in cls_node.body:
        if isinstance(stmt, ast.AnnAssign):
            if (
                isinstance(stmt.target, ast.Name)
                and stmt.target.id == "source"
            ):
                found_source_field = True
                break
        elif isinstance(stmt, ast.Assign):
            for tgt in stmt.targets:
                if (
                    isinstance(tgt, ast.Name)
                    and tgt.id == "source"
                ):
                    found_source_field = True
                    break
            if found_source_field:
                break
    assert found_source_field, (
        "AffiliateSlot must declare a ``source`` dataclass field "
        "(T-NEW-040 DESK-2 — telemetry split). "
        "Expected: ``source: str = 'external'`` (or 'internal')."
    )


def test_load_affiliate_rotation_helper_exists():
    """T-NEW-040 DESK-2: new module-level helper that fetches
    /api/v1/quicklinks/?ad_rotation_categories=... and returns
    a curated list of banner dicts in the AffiliateSlot shape.
    Falls back to FALLBACK_BANNERS on network failure (offline-first).
    """
    src = _read(AD_TAB)
    fn = _ast_function(src, "_load_affiliate_rotation")
    assert fn is not None, (
        "_load_affiliate_rotation() helper must exist "
        "(T-NEW-040 DESK-2)"
    )
    body = _function_source(src, "_load_affiliate_rotation")
    # Must hit the quicklinks endpoint
    assert "/api/v1/quicklinks" in body, (
        "_load_affiliate_rotation() must call /api/v1/quicklinks"
    )
    # Must pass the new ad_rotation_categories filter
    assert "ad_rotation_categories" in body, (
        "_load_affiliate_rotation() must pass ad_rotation_categories "
        "filter (creator_marketplace, affiliate_network, cross_promo)"
    )
    # Must fall back to FALLBACK_BANNERS on network failure
    assert "FALLBACK_BANNERS" in body or "load_fallback_banners" in body, (
        "_load_affiliate_rotation() must fall back to FALLBACK_BANNERS "
        "on network failure (offline-first contract)"
    )


def test_load_slots_wires_pro_internal_promos():
    """T-NEW-040 DESK-2: _load_slots() must append ProInternalSlot
    entries (from load_pro_internal_promos()) after the AffiliateSlot
    entries. This is the in-house cross-promo rotation slot — sits
    at the end of the rotation, in the same place as the affiliate
    slot tier but tagged kind='pro_internal' for telemetry."""
    src = _read(AD_TAB)
    fn = _ast_function(src, "_load_slots")
    assert fn is not None
    body = _function_source(src, "_load_slots")
    assert "load_pro_internal_promos" in body, (
        "_load_slots must call load_pro_internal_promos() "
        "(T-NEW-040 DESK-2)"
    )
    assert "ProInternalSlot" in body, (
        "_load_slots must append ProInternalSlot entries "
        "(T-NEW-040 DESK-2)"
    )


def test_load_slots_canonical_order_extended():
    """T-NEW-040 DESK-2: the canonical rotation order is now:
      [tip] + [substack] + [pro_cta] + [affiliate] + [pro_internal]
    The new pro_internal tier sits at the end (in-house cross-promos
    rotate last so users see external affiliates first — that's the
    revenue-producing tier).

    Pinned by the position of each ``slots.append(...)`` call
    (not the docstring mentions, which can appear anywhere in
    the function).
    """
    src = _read(AD_TAB)
    fn = _ast_function(src, "_load_slots")
    assert fn is not None
    body = _function_source(src, "_load_slots")
    # Pin via the slot append positions (not the loader-call
    # positions, since the loaders are called once but the
    # appends happen in the documented order).
    tip_pos = body.find("slots.append(TipSlot")
    sub_pos = body.find("slots.append(SubstackSlot")
    pro_cta_pos = body.find("slots.append(ProCtaSlot")
    aff_pos = body.find("slots.append(AffiliateSlot")
    pro_int_pos = body.find("slots.append(ProInternalSlot")
    assert -1 < tip_pos < sub_pos < pro_cta_pos < aff_pos < pro_int_pos, (
        f"Rotation order wrong: "
        f"tip={tip_pos}, substack={sub_pos}, "
        f"pro_cta={pro_cta_pos}, affiliate={aff_pos}, "
        f"pro_internal={pro_int_pos}. "
        f"Expected tip < substack < pro_cta < affiliate < pro_internal. "
        f"Search for ``slots.append(<SlotType>`` in the source."
    )


# ---------------------------------------------------------------------------
# T-NEW-040 DESK-3 — affiliate_click_internal vs _external
# telemetry split.
# ---------------------------------------------------------------------------


def test_make_open_url_handler_static_accepts_event_name():
    """T-NEW-040 DESK-3: the static click-handler factory must
    accept an event_name parameter so renderers can wire
    distinct telemetry events (affiliate_click_internal vs
    affiliate_click_external)."""
    src = _read(AD_TAB)
    fn = _ast_function(src, "_make_open_url_handler_static")
    assert fn is not None
    body = _function_source(src, "_make_open_url_handler_static")
    assert "event_name" in body, (
        "_make_open_url_handler_static must accept event_name kwarg "
        "(T-NEW-040 DESK-3)"
    )


def test_emit_ad_telemetry_helper_exists():
    """T-NEW-040 DESK-3: a small helper that fires ad-tab
    telemetry events via app.store_event(...). Module-level
    function so it works from slot renderers (no self)."""
    src = _read(AD_TAB)
    fn = _ast_function(src, "_emit_ad_telemetry")
    assert fn is not None, (
        "_emit_ad_telemetry helper must exist (T-NEW-040 DESK-3)"
    )
    body = _function_source(src, "_emit_ad_telemetry")
    assert "event_name" in body, (
        "_emit_ad_telemetry must take an event_name parameter"
    )


def test_affiliate_slot_render_fires_external_telemetry():
    """T-NEW-040 DESK-3: AffiliateSlot.render() must wire the
    CTA button click through _make_open_url_handler_static
    with an external telemetry event (default source='external')."""
    src = _read(AD_TAB)
    body = _class_source(src, "AffiliateSlot")
    assert "affiliate_click_external" in body, (
        "AffiliateSlot.render must wire CTA click to "
        "fire affiliate_click_external telemetry "
        "(T-NEW-040 DESK-3)"
    )


def test_pro_internal_slot_render_fires_internal_telemetry():
    """T-NEW-040 DESK-3: ProInternalSlot.render() must wire
    the CTA button click to fire affiliate_click_internal
    telemetry — in-house cross-promos get their own event
    name so revshare reporting can distinguish them from
    third-party affiliate clicks."""
    src = _read(AD_TAB)
    body = _class_source(src, "ProInternalSlot")
    assert "affiliate_click_internal" in body, (
        "ProInternalSlot.render must fire "
        "affiliate_click_internal telemetry "
        "(T-NEW-040 DESK-3)"
    )


def test_substack_slot_render_uses_substack_event_name():
    """T-NEW-040 DESK-3 (consistency check): the existing
    SubstackSlot.render() must continue to fire its own
    distinct event name (``substack_recommendation_clicked``
    or similar) so analytics can route Substack clicks to
    the symbiosis report. Just assert it doesn't fire the
    affiliate_* events — it should have its own."""
    src = _read(AD_TAB)
    body = _class_source(src, "SubstackSlot")
    # Substack has its own event (not affiliate_*)
    assert "affiliate_click_internal" not in body, (
        "SubstackSlot must NOT fire affiliate_click_internal"
    )
    assert "affiliate_click_external" not in body, (
        "SubstackSlot must NOT fire affiliate_click_external"
    )


# ============================================================================
# Runtime bug fix 2026-08-11: NchantdVScrollGroupBox.count() missing
# ============================================================================
# The AdTab._render_current_slot() method tried to call
# self._slot_container.count() to iterate over the container's
# children. But NchantdVScrollGroupBox is a QWidget (extends
# NchantdWidget) — it has no count() method. The count() lives
# on the inner QVBoxLayout (self._slot_container.layout_box).
#
# Runtime symptom (4x in 2026-08-11 11:27 log):
#   [ad_tab] _render_current_slot clear failed:
#   'NchantdVScrollGroupBox' object has no attribute 'count'
#
# The exception was swallowed by the try/except so the AdTab
# continued to render new slots on top of stale ones. Visual
# symptom: ad slot doesn't actually rotate / clear, stack-up of
# old widgets in the container.


def test_render_current_slot_is_removed():
    """DESK T-NEW-061 closeout: the local slot rotation
    (_render_current_slot, _advance_slot, _start_rotation)
    is replaced by the server-driven _fetch_and_render.
    _render_current_slot must NOT exist — replaced by _render_ad
    which renders a single server ad.

    The layout_box fix (T-NEW-070) is absorbed into
    _render_ad which uses layout_box.count() and layout_box.takeAt().
    """
    src = _read(AD_TAB)
    fn = _ast_function(src, "_render_current_slot")
    assert fn is None, (
        "_render_current_slot must be removed — "
        "replaced by _render_ad (server-driven single ad)."
    )
    # Verify _render_ad exists and uses the layout_box pattern.
    render_ad = _ast_function(src, "_render_ad")
    assert render_ad is not None, "_render_ad must exist."
    body = _function_source(src, "_render_ad")
    assert "layout_box.count()" in body, (
        "_render_ad must use layout_box.count() "
        "(T-NEW-070 fix: NchantdVScrollGroupBox has no count() method)."
    )
    assert "layout_box.takeAt" in body, (
        "_render_ad must use layout_box.takeAt() to remove items."
    )

def test_nchantd_vscroll_group_box_has_no_count_method():
    """Sanity check: NchantdVScrollGroupBox (in nchantrs) is a
    QWidget, not a QLayout. The .count() method lives on the
    inner layout_box, not on the widget itself.

    If this test ever fails, the upstream nchantrs class has
    been changed to expose .count() directly — in which case
    the bug fix in _render_current_slot should be re-evaluated.
    """
    nchantrs_groups = Path(
        "/home/solubrew/EDN/AGTs/morgbai/workspace/projects/nchantrs/"
        "nchantrs/widgets/groups.py"
    )
    if not nchantrs_groups.exists():
        # Skip if upstream isn't available in this env
        return
    src = nchantrs_groups.read_text()
    # Find the class
    tree = ast.parse(src)
    cls = None
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ClassDef)
            and node.name == "NchantdVScrollGroupBox"
        ):
            cls = node
            break
    assert cls is not None, "NchantdVScrollGroupBox class must exist"
    body = ast.unparse(cls)
    # Class must NOT have a count() method (it's a QWidget, not QLayout)
    has_count_def = re.search(r"def\s+count\s*\(", body) is not None
    assert not has_count_def, (
        "NchantdVScrollGroupBox.count() exists upstream — the "
        "fix in _render_current_slot should be re-evaluated "
        "(maybe we can call .count() directly now)"
    )
    # But it MUST have a layout_box attribute
    assert "self.layout_box" in body, (
        "NchantdVScrollGroupBox must have self.layout_box "
        "(the QVBoxLayout where addWidget lands)"
    )

# ---------------------------------------------------------------------------
# Contract 12: _switch_to_this_tab surfaces the Ad tab in the right pane
# ---------------------------------------------------------------------------


def test_switch_to_this_tab_method_exists():
    """DESK T-NEW-061 follow-up: _switch_to_this_tab()
    must exist on NchantdOfficeAdTab and switch the right-pane
    tabset to this tab after rendering an ad.

    This method is called at the end of _render_ad so that every
    5-minute server fetch auto-surfaces the new ad to the user.
    """
    src = _read(AD_TAB)
    fn = _ast_function(src, "_switch_to_this_tab")
    assert fn is not None, (
        "NchantdOfficeAdTab must declare _switch_to_this_tab() "
        "to auto-surface the Ad tab in the right pane on every ad render."
    )


def test_render_ad_calls_switch_to_this_tab():
    """_render_ad() must call _switch_to_this_tab() after
    successfully rendering an ad card.

    This wires the auto-surfacing: every time the 5-minute
    timer fires and _fetch_and_render produces an ad, the
    right pane switches to the Ad tab so the user sees it.
    """
    src = _read(AD_TAB)
    body = _function_source(src, "_render_ad")
    assert "_switch_to_this_tab" in body, (
        "_render_ad must call _switch_to_this_tab() after "
        "rendering the ad card so the right pane auto-surfaces."
    )


def test_switch_to_this_tab_checks_already_on_tab():
    """_switch_to_this_tab() must guard against switching when
    already on the Ad tab (avoid redundant signal firing on
    the initial render).

    The implementation must check currentIndex() == ad_index
    before calling setCurrentIndex.
    """
    src = _read(AD_TAB)
    body = _function_source(src, "_switch_to_this_tab")
    assert "currentIndex" in body, (
        "_switch_to_this_tab must check currentIndex() "
        "to avoid switching when already on the Ad tab."
    )
    assert "setCurrentIndex" in body, (
        "_switch_to_this_tab must call setCurrentIndex "
        "on the right pane to switch tabs."
    )

