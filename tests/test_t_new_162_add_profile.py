"""T-NEW-162 part B (desktop side) — add_profile persists via store_app_profile.

The 2026-08-18 PUSH-to-0.0.3 sweep filed T-NEW-162 covering 5 deferred
markers in atnrg/browsers.py. T-NEW-162 part A (commit d16a5fb) wired
3 of the 5 markers (cmd_scan_source, cmd_add_profile, get_profiles).
The fourth — ``add_profile(profile, cfg)`` at line 138 — was deferred
because its body referenced ``self.profiles.get_count()`` /
``self.profiles.add_profile()`` on a profile-manager abstraction that
doesn't exist (``self.profiles = None`` at line 62).

The T-NEW-162 part B nchantrs commit (4d7170b) implements the real
``store.store_app_profile(record, db, how)`` persistence method. This
commit lands the desktop ``add_profile`` wrapper that:

  1. Reads ``self.app.model.user.has_pro`` to determine the limit
     (1 for free, 10 for pro — matches the deferred body).
  2. Counts existing profiles via ``self.app.model.get_profiles()``
     (real impl at models.py:2414 since T-NEW-162 part A).
  3. Returns ``self`` silently when the cap is hit.
  4. Builds a record dict (UUID + userUUID + profile_txt) and
     delegates to ``self.app.model.store.store_app_profile(...)``.

Tests are AST-source structural — mirrors the established Qt-bound-
module test pattern from T-NEW-117 / T-NEW-161 / T-NEW-162 part A /
T-NEW-165.
"""

import ast
from pathlib import Path


BROWSERS_PATH = (
    Path(__file__).parents[1]
    / "nchantdoffice/widgets/documents/atnrg/browsers.py"
)


def _function_source(name: str) -> str:
    tree = ast.parse(BROWSERS_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"{name} not found")


def test_add_profile_is_uncommented():
    """``add_profile`` is live code (PUSH 0.0.3 marker removed)."""
    src = BROWSERS_PATH.read_text()
    lines = src.splitlines()
    matches = [i for i, ln in enumerate(lines) if "def add_profile" in ln]
    assert matches, "add_profile not found"
    target = lines[matches[0]]
    assert not target.lstrip().startswith("#"), (
        f"add_profile still commented out at line {matches[0] + 1}: "
        f"{target!r}. T-NEW-162 part B must uncomment it."
    )


def test_add_profile_reads_has_pro_for_profile_limit():
    """``add_profile`` reads ``has_pro`` to gate the cap.

    T-NEW-162 part B: the deferred body used
    ``getattr(self.app.model.user, "has_pro", False)`` to set
    profile_limit = 10 (pro) or 1 (free). The fix preserves that
    contract.
    """
    source = _function_source("add_profile")
    assert "has_pro" in source, (
        "add_profile must read has_pro (the pro-tier gate). "
        "The deferred body lifted profile_limit from 1 -> 10 for "
        "pro users."
    )


def test_add_profile_counts_existing_via_model():
    """``add_profile`` counts existing profiles via ``self.app.model.get_profiles()``."""
    source = _function_source("add_profile")
    assert "self.app.model.get_profiles" in source, (
        "add_profile must count existing profiles via "
        "self.app.model.get_profiles() — the model-side helper "
        "(real impl at models.py:2414) reads app_profile rows."
    )


def test_add_profile_delegates_to_store_app_profile():
    """``add_profile`` persists via ``self.app.model.store.store_app_profile``.

    T-NEW-162 part B nchantrs commit (4d7170b) lands the real impl
    of store_app_profile. The desktop wrapper builds a record dict
    and delegates. The record must include at least profile_txt
    (the column get_profiles reads back) — the wrapper passes
    the profile name as profile_txt.
    """
    source = _function_source("add_profile")
    assert "store_app_profile" in source, (
        "add_profile must delegate to self.app.model.store.store_app_profile(...) "
        "— that's the persistence path that landed in the nchantrs "
        "commit 4d7170b."
    )
    assert "profile_txt" in source, (
        "add_profile must build a record with profile_txt (the column "
        "get_profiles reads back). Without it, the profile writes "
        "but never reads back."
    )


def test_add_profile_returns_self_when_at_cap():
    """``add_profile`` returns ``self`` (no exception) when cap is hit."""
    source = _function_source("add_profile")
    # The cap-hit path is `return self` — graceful no-op, not an
    # exception. The free-tier user gets a silent skip rather than
    # a stack trace.
    assert source.count("return self") >= 1, (
        "add_profile must return self on the cap-hit branch — "
        "the deferred body's graceful-skip behaviour is preserved."
    )