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
# Contract 5: _advance_slot wraps index to 0
# ---------------------------------------------------------------------------


def test_advance_slot_wraps_index_to_zero():
    """``_advance_slot()`` must increment ``current_slot_index``
    by 1 and wrap to 0 when it passes the last slot. The
    arithmetic wrap is the whole point of the rotation.
    """
    src = _read(AD_TAB)
    fn = _ast_function(src, "_advance_slot")
    assert fn is not None, (
        "advertisements.py must declare _advance_slot() "
        "(the QTimer callback that cycles the rotation)."
    )
    body = _function_source(src, "_advance_slot")
    assert "current_slot_index" in body, (
        "_advance_slot must mutate self.current_slot_index."
    )
    # The wrap must use modulo by len(self.slots). Either
    # ``current_slot_index % len(slots)`` or an explicit
    # ``if … : current_slot_index = 0`` is acceptable.
    assert (
        "% len(self.slots)" in body
        or "% len(slots)" in body
        or "current_slot_index = 0" in body
    ), (
        "_advance_slot must wrap current_slot_index to 0 after "
        "the last slot (modulo len(self.slots) or an explicit reset)."
    )


# ---------------------------------------------------------------------------
# Contract 6: initView wires QTimer for Free users only
# ---------------------------------------------------------------------------


def test_initView_starts_qtimer_for_free_users_only():
    """``initView()`` must start a QTimer for Free users and
    never start it for Pro users (the existing
    ``_is_visible_for_user`` short-circuit). The Pro-user
    path must NOT reference QTimer.

    The QTimer configuration lives in ``_start_rotation()``
    — ``initView`` delegates to it. The contract is that
    the Pro check happens BEFORE the timer starts (not
    where the timer is configured).
    """
    src = _read(AD_TAB)
    body = _function_source(src, "initView")
    assert "_start_rotation" in body, (
        "initView must delegate QTimer startup to "
        "_start_rotation() (the configuration lives there)."
    )
    # The Pro short-circuit must come BEFORE the _start_rotation call.
    is_visible = body.find("_is_visible_for_user")
    start_rot = body.find("_start_rotation")
    assert -1 < is_visible < start_rot, (
        "initView must check _is_visible_for_user BEFORE "
        "calling _start_rotation (Pro users get no rotation)."
    )


def test_start_rotation_uses_default_or_configured_interval():
    """``_start_rotation()`` must read ``interval_ms`` from
    ``self.config`` (advertisements.yaml) and fall back to
    ``DEFAULT_INTERVAL_MS`` (12000).
    """
    src = _read(AD_TAB)
    body = _function_source(src, "_start_rotation")
    assert body, "advertisements.py must declare _start_rotation()."
    assert "DEFAULT_INTERVAL_MS" in body, (
        "_start_rotation must reference DEFAULT_INTERVAL_MS."
    )
    assert "setInterval" in body, (
        "_start_rotation must call .setInterval() on the QTimer."
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
