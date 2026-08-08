"""T-DESK-057 — Refresh ``FALLBACK_BANNERS`` from ATNRG
``ReferralLinks.yaml``.

Paired with nchantdofficeATNRG cross-repo review
(``docs/cross-repo-review_20260807.md`` §2.2).

Today the desktop's ``FALLBACK_BANNERS`` (in
``nchantdoffice/widgets/advertisements.py``) lists 3
hand-picked services (OpenAI, Notion, Railway, Supabase).
The server's affiliate catalog has 27 services across 7
categories (per ``nchantdofficeATNRG/ReferralLinks.yaml``).
The fallback should mirror the live catalog so:

  - users on a fresh install / offline see a real
    cross-section of the affiliate offerings, not 3 picked
    ones
  - the desktop bundle stays in sync with the marketing
    source of truth (mirrors the TIPS_FEED release-checklist
    discipline)

T-DESK-057 deliverable:
  - Extract the 4 ``active`` services from
    ``ReferralLinks.yaml`` and add them to FALLBACK_BANNERS
    (openai, railway, supabase, dropbox per the YAML's
    status field).
  - Replace the hand-picked ``Notion`` entry with the
    Notion entry from ReferralLinks (display_name +
    base_url + affiliate_url).
  - Use ``nchantdoffice_utilities/affiliate_fallback.py``
    (a new module) to hold the fallback list — keeps
    advertisements.py focused on the rotation logic, and
    lets the test layer target the fallback list directly
    without pulling in the Qt widget code.
  - Pin a release-checklist test that asserts the fallback
    count stays ≥ 4 (the YAML's ``active`` count) so a
    future operator who deletes entries gets a failing test.

This test is AST-based (mirrors the pattern from
test_ad_tab_rotation.py's release-checklist pin).

Refs:
  - docs/cross-repo-review_20260807.md §2.2
  - nchantdofficeATNRG/ReferralLinks.yaml
  - nchantdoffice/widgets/advertisements.py::FALLBACK_BANNERS
  - nchantdoffice/utilities/feature_gates.py (sibling module
    shape — module-level constants + small helpers)
"""

import ast
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

UTILS_DIR = PROJ_ROOT / "nchantdoffice" / "utilities"
AFFILIATE_FALLBACK = UTILS_DIR / "affiliate_fallback.py"

AD_TAB = PROJ_ROOT / "nchantdoffice" / "widgets" / "advertisements.py"

ATNRG_REFERRAL_LINKS = (
    PROJ_ROOT.parent / "nchantdofficeATNRG" / "ReferralLinks.yaml"
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    return path.read_text()


def _ast_class(src: str, name: str):
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


def _module_top_level_constant(src: str, name: str):
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == name:
                    return node.value
        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == name
            ):
                return node.value
    return None


def _eval_simple_expr(node, scope=None):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        left = _eval_simple_expr(node.left, scope=scope)
        right = _eval_simple_expr(node.right, scope=scope)
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        raise ValueError(f"unsupported binop: {ast.dump(node.op)}")
    if isinstance(node, ast.Name):
        if scope is None or node.id not in scope:
            raise ValueError(f"unresolved name: {node.id}")
        return scope[node.id]
    raise ValueError(f"unsupported expr: {ast.dump(node)}")


def _build_name_scope(src: str) -> Dict[str, Any]:
    scope: Dict[str, Any] = {}
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    try:
                        scope[tgt.id] = _eval_simple_expr(
                            node.value, scope=scope
                        )
                    except ValueError:
                        pass
        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.value is not None
            ):
                try:
                    scope[node.target.id] = _eval_simple_expr(
                        node.value, scope=scope
                    )
                except ValueError:
                    pass
    return scope


# ---------------------------------------------------------------------------
# Contract 1: the affiliate_fallback module exists
# ---------------------------------------------------------------------------


def test_affiliate_fallback_module_exists():
    """``nchantdoffice/utilities/affiliate_fallback.py`` must
    exist (T-DESK-057 deliverable — separate module keeps
    ``advertisements.py`` focused on rotation logic).
    """
    assert AFFILIATE_FALLBACK.exists(), (
        f"nchantdoffice/utilities/affiliate_fallback.py must exist "
        f"(T-DESK-057). Expected at {AFFILIATE_FALLBACK}."
    )


# ---------------------------------------------------------------------------
# Contract 2: FALLBACK_BANNERS shape preserved (banner-card dict)
# ---------------------------------------------------------------------------


def test_fallback_banners_constant_exists():
    """The fallback list must be exposed as ``FALLBACK_BANNERS``
    (the same name the Ad tab already imports — keeping the
    name avoids touching ``advertisements.py``'s loader chain).
    """
    src = _read(AFFILIATE_FALLBACK)
    node = _module_top_level_constant(src, "FALLBACK_BANNERS")
    assert node is not None, (
        "affiliate_fallback.py must declare FALLBACK_BANNERS "
        "top-level (the Ad tab imports this name)."
    )


def _find_banners_node(tree):
    """Find the ``FALLBACK_BANNERS`` top-level assignment or
    annotated assignment. Returns the AST node (List) or None.
    """
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "FALLBACK_BANNERS":
                    return node.value
        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == "FALLBACK_BANNERS"
                and node.value is not None
            ):
                return node.value
    return None


def test_fallback_banners_have_banner_shape():
    """Each fallback banner must carry the keys the Ad tab's
    ``AffiliateSlot.render()`` consumes (title, subtitle,
    cta_text, cta_url, background, foreground). Pinning the
    shape keeps the visual language consistent.
    """
    src = _read(AFFILIATE_FALLBACK)
    tree = ast.parse(src)
    banners_node = _find_banners_node(tree)
    assert banners_node is not None, (
        "FALLBACK_BANNERS top-level assignment not found."
    )
    assert isinstance(banners_node, ast.List), (
        "FALLBACK_BANNERS must be a list literal."
    )
    for i, elt in enumerate(banners_node.elts):
        assert isinstance(elt, ast.Dict), (
            f"FALLBACK_BANNERS[{i}] must be a dict, got "
            f"{type(elt).__name__}."
        )
        keys = [
            k.value for k in elt.keys
            if isinstance(k, ast.Constant)
        ]
        # Minimum required keys (the Ad tab's AffiliateSlot
        # needs at least title + cta_text + cta_url to render
        # a useful card).
        for required in ("title", "cta_text", "cta_url"):
            assert required in keys, (
                f"FALLBACK_BANNERS[{i}] missing required key "
                f"{required!r}. Keys found: {keys}."
            )


# ---------------------------------------------------------------------------
# Contract 3: ATNRG catalog is mirrored
# ---------------------------------------------------------------------------


def test_fallback_includes_atnrg_active_services():
    """The 4 ``active`` services from
    ``nchantdofficeATNRG/ReferralLinks.yaml`` (openai,
    railway, supabase, dropbox) must appear in
    ``FALLBACK_BANNERS``. This is the minimum viable mirror —
    the original card said "the 16-service catalog" but the
    YAML only has 4 ``active`` entries right now (the others
    are pending/paused). Pinning the active count prevents a
    future operator from forgetting to refresh.
    """
    src = _read(AFFILIATE_FALLBACK)
    tree = ast.parse(src)
    banners_node = _find_banners_node(tree)
    assert banners_node is not None, "FALLBACK_BANNERS not found."
    titles = []
    for elt in banners_node.elts:
        if isinstance(elt, ast.Dict):
            for k, v in zip(elt.keys, elt.values):
                if (
                    isinstance(k, ast.Constant)
                    and k.value == "title"
                    and isinstance(v, ast.Constant)
                ):
                    titles.append(str(v.value).lower())
    # The 4 active services must each appear in at least
    # one banner title (case-insensitive).
    for service in ("openai", "railway", "supabase", "dropbox"):
        assert any(service in t for t in titles), (
            f"FALLBACK_BANNERS must include the ATNRG active "
            f"service {service!r} (status=active in "
            f"ReferralLinks.yaml). Found titles: {titles}."
        )


def test_fallback_count_meets_release_checklist():
    """R-1 release-checklist pin (mirrors test_ad_tab_rotation.py's
    cross-repo drift detector): the fallback count must be
    ≥ 4 (the ATNRG YAML's ``active`` count). When the YAML
    gains more ``active`` entries, this threshold bumps in
    lockstep — the operator must mirror the new entries.
    """
    import pytest

    if not ATNRG_REFERRAL_LINKS.exists():
        pytest.skip(
            f"ATNRG ReferralLinks.yaml not found at "
            f"{ATNRG_REFERRAL_LINKS}. Skip cross-repo parity check."
        )
    yaml_text = ATNRG_REFERRAL_LINKS.read_text()
    # Count the ``status: active`` entries.
    active_count = len(
        re.findall(r"^\s*status:\s*active\s*$", yaml_text, re.MULTILINE)
    )
    src = _read(AFFILIATE_FALLBACK)
    tree = ast.parse(src)
    banners_node = _find_banners_node(tree)
    assert banners_node is not None, "FALLBACK_BANNERS not found."
    assert isinstance(banners_node, ast.List)
    desktop_count = len(banners_node.elts)
    assert desktop_count >= active_count, (
        f"FALLBACK_BANNERS has {desktop_count} entries but "
        f"ATNRG ReferralLinks.yaml has {active_count} active "
        f"services — the desktop bundle fell behind the "
        f"marketing source. Mirror the new active entries."
    )


# ---------------------------------------------------------------------------
# Contract 4: load_fallback_banners() helper
# ---------------------------------------------------------------------------


def test_load_fallback_banners_helper_exists():
    """``load_fallback_banners()`` must exist as a module-level
    helper (mirrors ``load_tip_feed`` / ``load_substack_feed``
    from advertisements.py). Returns a copy of FALLBACK_BANNERS
    so callers can't mutate the module-level constant.
    """
    src = _read(AFFILIATE_FALLBACK)
    fn = _ast_function(src, "load_fallback_banners")
    assert fn is not None, (
        "affiliate_fallback.py must declare "
        "load_fallback_banners() helper."
    )
    body = _function_source(src, "load_fallback_banners")
    assert "FALLBACK_BANNERS" in body, (
        "load_fallback_banners must return FALLBACK_BANNERS "
        "(or a copy)."
    )


# ---------------------------------------------------------------------------
# Contract 5: the Ad tab imports the new module
# ---------------------------------------------------------------------------


def test_adtab_imports_fallback_from_new_module():
    """``advertisements.py`` must import ``FALLBACK_BANNERS``
    (or ``load_fallback_banners``) from
    ``nchantdoffice.utilities.affiliate_fallback`` — pinning
    the cross-module wiring. Without this the new fallback
    list is dead code (the Ad tab still uses the old 3-entry
    inline list).
    """
    src = _read(AD_TAB)
    assert "affiliate_fallback" in src, (
        "advertisements.py must import from "
        "nchantdoffice.utilities.affiliate_fallback — "
        "otherwise the new FALLBACK_BANNERS is dead code."
    )
    # And the local FALLBACK_BANNERS = [...] block must
    # be REMOVED from advertisements.py (the new module
    # is the source of truth).
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "FALLBACK_BANNERS":
                    raise AssertionError(
                        "advertisements.py must NOT declare "
                        "FALLBACK_BANNERS anymore — the new "
                        "affiliate_fallback module is the "
                        "source of truth. Remove the inline "
                        "list literal."
                    )


# ---------------------------------------------------------------------------
# Contract 6: the release-checklist doc has the R-5 step
# ---------------------------------------------------------------------------


def test_release_checklist_documents_fallback_mirror():
    """R-5 release checklist step (additions to
    docs/cross-repo-review_20260807.md): the fallback mirror
    procedure must be documented, mirroring the R-1 tip
    mirror discipline. The doc must name
    ``FALLBACK_BANNERS`` + ``ReferralLinks.yaml`` so a future
    operator knows exactly where to refresh.
    """
    doc_path = PROJ_ROOT / "docs" / "cross-repo-review_20260807.md"
    assert doc_path.exists(), (
        "docs/cross-repo-review_20260807.md must exist."
    )
    text = doc_path.read_text()
    assert "R-5" in text, (
        "Release checklist must include R-5 (the fallback "
        "mirror step, added during T-DESK-057)."
    )
    assert "FALLBACK_BANNERS" in text, (
        "R-5 must name FALLBACK_BANNERS (the desktop bundle)."
    )
    assert "ReferralLinks.yaml" in text, (
        "R-5 must name ReferralLinks.yaml (the ATNRG source)."
    )
