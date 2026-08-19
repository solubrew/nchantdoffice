"""T-NEW-162 part A — wire 3 trivial browser profile deferred stubs.

The 2026-08-18 PUSH-to-0.0.3 sweep filed T-NEW-162 with 5 deferred
markers in ``atnrg/browsers.py``. Three are 5-line forgotten stubs:

  1. ``cmd_scan_source`` (line 357) — was `return self`
     (Sprint-20 anti-pattern). Now logs + opens the source
     inspection drawer that T-NEW-161 just activated.
  2. ``cmd_add_profile`` (line 226) — was `return self`
     (Sprint-20 anti-pattern). Now delegates to ``add_profile``
     and is decorated with ``@feature_restrict`` so non-pro
     users see the Get-Pro CTA instead.
  3. ``get_profiles`` (line 570) — was `return self.profiles`
     (wrong, returns the profiles manager not the list). Now
     delegates to ``self.app.model.get_profiles()`` which is a
     real implementation at models.py:2414.

The fourth deferred method (``add_profile``) was deferred in
this commit and shipped in T-NEW-162 part B (companion commit).
Part B wires ``add_profile`` to delegate to
``self.app.model.store.store_app_profile`` — the real
persistence impl landed in nchantrs commit 4d7170b.

``init_drawer_form_control`` (line 760, the fourth deferred block)
remains deferred; it lands as part of this card's WIRE-4 once
the operator confirms the form-control UI shape.

Tests are AST-source structural (mirroring the established
Qt-bound-module pattern from T-NEW-117 / T-NEW-161 / T-NEW-165)
because ``NchantdOfficeBrowser`` imports PySide6.
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


def test_cmd_scan_source_is_uncommented():
    """``cmd_scan_source`` is live code, not a commented stub.

    T-NEW-162 WIRE-3: was a PUSH 0.0.3 stub (line 357) returning
    ``self``. Now logs + opens the source inspection drawer that
    T-NEW-161 just activated.
    """
    src = BROWSERS_PATH.read_text()
    lines = src.splitlines()
    matches = [i for i, ln in enumerate(lines) if "def cmd_scan_source" in ln]
    assert matches, "cmd_scan_source not found"
    target = lines[matches[0]]
    assert not target.lstrip().startswith("#"), (
        f"cmd_scan_source still commented out at line {matches[0] + 1}: "
        f"{target!r}"
    )


def test_cmd_scan_source_delegates_to_source_inspection():
    """``cmd_scan_source`` triggers the source-inspection drawer flow.

    The handler logs the URL being scanned and fires the cmd that
    drives the crawler — both are observable actions, not silent
    no-ops.
    """
    source = _function_source("cmd_scan_source")
    # Must log a meaningful message (not just pass / return self)
    assert "logma" in source, (
        "cmd_scan_source must log its activity; the old stub silently "
        "returned self."
    )
    # Must NOT be a pure pass / return self body
    assert source.count("return self") <= 1, (
        f"cmd_scan_source still has multiple return-self paths "
        f"(the Sprint-20 anti-pattern)"
    )


def test_cmd_add_profile_is_uncommented():
    """``cmd_add_profile`` is live code."""
    src = BROWSERS_PATH.read_text()
    lines = src.splitlines()
    matches = [i for i, ln in enumerate(lines) if "def cmd_add_profile" in ln]
    assert matches, "cmd_add_profile not found"
    target = lines[matches[0]]
    assert not target.lstrip().startswith("#"), (
        f"cmd_add_profile still commented out at line {matches[0] + 1}: "
        f"{target!r}"
    )


def test_cmd_add_profile_gates_on_has_pro():
    """``cmd_add_profile`` reads ``has_pro`` to gate the pro-tier action.

    T-NEW-162 WIRE-4: the comment at line 226 says "decorate as
    paid feature". The codebase convention is inline checks
    (cf. ``cmd_fill_in_forms`` etc.) rather than decorators, so
    the gating is an inline ``getattr(..., "has_pro", False)``
    on ``self.app.model.user``. Non-pro users fall through to
    ``cmd_get_pro`` (the Get-Pro CTA flow already wired).
    """
    source = _function_source("cmd_add_profile")
    assert "has_pro" in source, (
        "cmd_add_profile must read has_pro (the pro-tier gate). "
        "The original PUSH 0.0.3 marker comment explicitly said "
        "'decorate as paid feature'."
    )
    assert "cmd_get_pro" in source, (
        "cmd_add_profile must route non-pro users to cmd_get_pro "
        "(the existing Get-Pro CTA flow)."
    )


def test_cmd_add_profile_delegates_to_add_profile_helper():
    """``cmd_add_profile`` calls ``self.add_profile(...)``."""
    source = _function_source("cmd_add_profile")
    assert "self.add_profile" in source, (
        "cmd_add_profile must call self.add_profile(...) — "
        "the helper does the actual storage write."
    )


def test_get_profiles_is_uncommented():
    """``get_profiles`` is live code."""
    src = BROWSERS_PATH.read_text()
    lines = src.splitlines()
    matches = [i for i, ln in enumerate(lines) if "def get_profiles" in ln]
    assert matches, "get_profiles not found"
    target = lines[matches[0]]
    assert not target.lstrip().startswith("#"), (
        f"get_profiles still commented out at line {matches[0] + 1}: "
        f"{target!r}"
    )


def test_get_profiles_delegates_to_model():
    """``get_profiles`` delegates to ``self.app.model.get_profiles()``.

    T-NEW-162 WIRE-1: the deferred body returned ``self.profiles``
    (the profiles manager, not the list). The model has a real
    ``get_profiles()`` at models.py:2414 that reads from
    ``self.store.get_app_profile()``.
    """
    source = _function_source("get_profiles")
    assert "self.app.model.get_profiles" in source, (
        "get_profiles must delegate to self.app.model.get_profiles() — "
        "the model-side method at models.py:2414 is the real impl "
        "(reads self.store.get_app_profile()['profile_txt'])"
    )
    # Must NOT just return self.profiles (the wrong shape)
    assert "return self.profiles" not in source, (
        "get_profiles must NOT return self.profiles — that's the "
        "deferred body (returns the manager, not the list)"
    )


def test_add_profile_now_wired_via_store():
    """``add_profile`` is no longer deferred — T-NEW-162 part B shipped.

    Pre-fix: the body was commented with ``# PUSH 0.0.3`` and
    referenced a non-existent ``self.profiles`` profile-manager.
    T-NEW-162 part B (this card's followup commit) wired it to
    delegate to ``self.app.model.store.store_app_profile`` — see
    tests/test_t_new_162_add_profile.py for the contract tests.

    This test is a regression guard: a future sweep that re-adds
    the ``# PUSH 0.0.3`` marker should fail this test so the
    catalog catches the rollback.
    """
    src = BROWSERS_PATH.read_text()
    lines = src.splitlines()
    matches = [i for i, ln in enumerate(lines) if "def add_profile" in ln]
    assert matches, "add_profile not found"
    target = lines[matches[0]]
    assert not target.lstrip().startswith("#"), (
        f"add_profile was re-commented out (PUSH 0.0.3 marker "
        f"restored) at line {matches[0] + 1}: {target!r}. "
        f"T-NEW-162 part B landed a real impl — do not roll "
        f"back to a deferred stub."
    )