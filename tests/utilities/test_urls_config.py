"""Tests for nchantdoffice.utilities.urls (DESK T-NEW-052).

The resolver has three jobs:

  1. Ship production defaults from the bundled yaml.
  2. Honor per-deploy overrides from the XDG user config.
  3. Be the SINGLE source of truth — every other module must
     ask for URLs through here, not hardcode ``nchantdoffice.com``.

This test file covers all three:

  * ``test_*_returns_bundled_default`` — sanity-check every
    accessor against the bundled yaml.
  * ``test_user_override_*`` — verify the XDG ``urls:`` block
    overrides the bundled default for each accessor.
  * ``test_no_hardcoded_hostnames_in_source`` — defensive grep
    over the nchantdoffice package, ensuring no caller still
    hardcodes ``nchantdoffice.com`` or ``api.nchantdoffice.com``
    (this is the regression guard).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from nchantdoffice.utilities import urls


# -----------------------------------------------------------------------------
# Bundled-default smoke tests
# -----------------------------------------------------------------------------


def test_all_accessors_return_nonempty_strings() -> None:
    """Every accessor returns a non-empty string."""
    for name in (
        "server_base_url",
        "affiliate_api_base",
        "feature_gates_url",
        "updates_url",
        "sync_url",
        "home_page",
        "upgrade_compare_url",
        "share_landing_url",
    ):
        value = getattr(urls, name)()
        assert isinstance(value, str)
        assert value, f"{name}() returned empty string"
        assert value.startswith(("http://", "https://")), (
            f"{name}()={value!r} missing scheme"
        )


def test_bundled_defaults_match_yaml() -> None:
    """The bundled defaults in code match the shipped yaml file.

    Catches drift between ``_BUNDLED_DEFAULTS`` and the actual
    yaml file (someone edits one but not the other).
    """
    yaml_path = Path(urls.__file__).parent / "_data_" / "urls.yaml"
    assert yaml_path.exists(), f"bundled yaml missing: {yaml_path}"
    with yaml_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict)
    # Every yaml key must appear in the bundled defaults and
    # produce the same value.
    for k, v in data.items():
        assert k in urls.KNOWN_URL_KEYS, (
            f"yaml key {k!r} not in KNOWN_URL_KEYS"
        )
        assert getattr(urls, k)() == v, (
            f"bundled default for {k!r} diverges from yaml "
            f"(expected {v!r}, got {getattr(urls, k)()!r})"
        )


def test_home_page_keeps_trailing_slash() -> None:
    """The home_page accessor keeps a trailing slash (QUrl convention).

    Other accessors strip trailing slashes — verified by a
    separate test below.
    """
    url = urls.home_page()
    assert url.endswith("/"), (
        f"home_page()={url!r} must keep trailing slash"
    )


def test_non_home_accessors_strip_trailing_slash() -> None:
    """All accessors EXCEPT home_page strip trailing slashes.

    Caller patterns are ``f"{base}{path}"`` — a trailing slash on
    the base would produce ``//api/desktop/install-bootstrap``.
    """
    for name in (
        "server_base_url",
        "affiliate_api_base",
        "feature_gates_url",
        "updates_url",
        "sync_url",
        "upgrade_compare_url",
        "share_landing_url",
    ):
        value = getattr(urls, name)()
        assert not value.endswith("/") or value.count("://") == 1 and "/" in value.split("://", 1)[1], (
            f"{name}()={value!r} has unexpected trailing slash"
        )
        # More targeted check: ends with anything except a slash
        # after the host portion.
        scheme_host, _, _rest = value.partition("/")  # splits off "https:"+rest
        # Just check the final char.
        assert not value.endswith("/"), (
            f"{name}()={value!r} must NOT end with a slash"
        )


def test_all_urls_returns_full_snapshot() -> None:
    """``all_urls()`` returns the canonical dict, not a live view."""
    snap = urls.all_urls()
    assert isinstance(snap, dict)
    assert set(snap.keys()) == set(urls.KNOWN_URL_KEYS)
    # Mutating the snapshot must not affect future calls.
    snap["server_base_url"] = "http://should-not-stick"
    assert urls.server_base_url() != "http://should-not-stick"


def test_reload_invalidates_cache() -> None:
    """``reload()`` forces the next accessor call to re-read.

    Used by the settings tab after the operator edits the
    XDG config; also used by tests that monkey-patch the config.
    """
    # First accessor call populates the cache.
    first = urls.server_base_url()
    assert urls._resolve.cache_info().currsize == 1
    # Reload clears the cache.
    urls.reload()
    assert urls._resolve.cache_info().currsize == 0
    # Next accessor call repopulates it with the same value
    # (no XDG override in this test).
    second = urls.server_base_url()
    assert first == second
    assert urls._resolve.cache_info().currsize == 1


# -----------------------------------------------------------------------------
# DESK T-NEW-053: run-mode profiles (dev / prod).
# -----------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_run_mode():
    """Reset the active run-mode to ``prod`` between tests.

    The module-level ``_run_mode`` persists across tests, so
    a test that flips to ``dev`` would leak state into the
    next test. The fixture calls :func:`urls.set_run_mode`
    before AND after the test body to guarantee a clean slate.

    ``autouse=True`` so every test in this module starts in
    ``prod`` mode without having to declare the fixture.
    The cost is one cache invalidation per test — negligible.
    """
    urls.set_run_mode("prod")
    urls.reload()
    yield
    urls.set_run_mode("prod")
    urls.reload()


def test_run_mode_defaults_to_prod() -> None:
    """On a fresh import, the active run-mode is ``prod``.

    The launch entrypoint flips this before any accessor is
    called, but a default of ``prod`` means accessor calls
    before the entrypoint runs are still safe (they return
    production URLs).
    """
    assert urls.get_run_mode() == "prod"


def test_set_run_mode_to_dev_flips_all_accessors() -> None:
    """``set_run_mode("dev")`` swaps every accessor to the internal
    docker stack at ``http://192.168.1.67:8081``.

    Regression guard for DESK T-NEW-053 — the operator launched
    the desktop with ``run-mode: dev`` and expects every URL
    surface (license bootstrap, embedded browser, account tab,
    upgrade prompts, ad CTAs) to point at the internal site.

    Both the API and the marketing site hit the SAME port
    (8081) on the dev box because the nchantdoffice_com
    Flask app serves both paths on a single port (COM T-NEW-053
    follow-up: split-port was a wrong assumption; see
    docker-compose.lan.yml for the deploy shape).
    """
    urls.set_run_mode("dev")
    assert urls.server_base_url() == "http://192.168.1.67:8081"
    assert (
        urls.affiliate_api_base()
        == "http://192.168.1.67:8081/api/affiliate"
    )
    assert urls.feature_gates_url() == "http://192.168.1.67:8081"
    assert urls.updates_url() == "http://192.168.1.67:8081"
    assert urls.sync_url() == "http://192.168.1.67:8081"
    assert urls.home_page() == "http://192.168.1.67:8081/"
    assert (
        urls.upgrade_compare_url()
        == "http://192.168.1.67:8081/compare"
    )
    assert urls.share_landing_url() == "http://192.168.1.67:8081"
    assert (
        urls.registration_url()
        == "http://192.168.1.67:8081/registration"
    )
    assert (
        urls.whats_new_url()
        == "http://192.168.1.67:8081/whats_new"
    )
    assert (
        urls.affiliate_marketing_url()
        == "http://192.168.1.67:8081/affiliate_marketing"
    )
    assert urls.marketing_base_url() == "http://192.168.1.67:8081"


def test_set_run_mode_back_to_prod_reverts_all_accessors() -> None:
    """``set_run_mode("prod")`` after ``dev`` reverts every accessor
    to the bundled / production URLs.

    Symmetric with the dev case above — switching modes is a
    wholesale replace, not a partial overlay.
    """
    urls.set_run_mode("dev")
    assert urls.server_base_url() == "http://192.168.1.67:8081"
    urls.set_run_mode("prod")
    assert urls.server_base_url() == "https://api.nchantdoffice.com"
    assert urls.home_page() == "https://www.nchantdoffice.com/"


def test_set_run_mode_invalid_value_raises() -> None:
    """Unknown run-mode values fail loud (ValueError) at the
    launch entrypoint — no silent fallback to production.

    Catches typos like ``run-mode: Development`` or
    ``run-mode: testing`` before they ship to the operator.
    """
    with pytest.raises(ValueError):
        urls.set_run_mode("Development")
    with pytest.raises(ValueError):
        urls.set_run_mode("")
    with pytest.raises(ValueError):
        urls.set_run_mode(123)  # type: ignore[arg-type]


def test_set_run_mode_is_idempotent() -> None:
    """Setting the same mode twice is a no-op (besides logging).

    The launch entrypoint may call :func:`set_run_mode` defensively
    on every startup; re-flipping to ``prod`` when already ``prod``
    must not invalidate the cache.
    """
    urls.set_run_mode("prod")  # already default
    urls.server_base_url()  # populate cache
    assert urls._resolve.cache_info().currsize == 1
    urls.set_run_mode("prod")  # no-op
    assert urls._resolve.cache_info().currsize == 1, (
        "re-setting the same run-mode must not invalidate the cache"
    )


def test_set_run_mode_invalidates_resolver_cache() -> None:
    """``set_run_mode`` clears the resolver cache so the next
    accessor call returns values from the new profile.

    Without this, switching modes mid-process would silently
    keep returning stale values from the old profile.
    """
    urls.set_run_mode("prod")
    urls.server_base_url()  # populate cache
    assert urls._resolve.cache_info().currsize == 1
    urls.set_run_mode("dev")
    assert urls._resolve.cache_info().currsize == 0
    # Next accessor repopulates with dev values.
    assert urls.server_base_url() == "http://192.168.1.67:8081"


# -----------------------------------------------------------------------------
# XDG override tests (user_config layer)
# -----------------------------------------------------------------------------


@pytest.fixture
def user_config_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Write a custom XDG config + cwd override, point load_config at it.

    The real :func:`user_config.load_config` reads from a fixed path;
    we monkey-patch ``load_config`` to return our test dict instead.
    This keeps the warning logic in ``_load_user_overrides``
    intact so the unknown-key test can exercise it.
    """
    import nchantdoffice.utilities.urls as _urls_mod
    override_dict: Dict[str, Any] = {}

    def _fake_load_config() -> Dict[str, Any]:
        return dict(override_dict)

    # Patch the user_config import that urls.py uses.
    monkeypatch.setattr(
        "nchantdoffice.utilities.user_config.load_config",
        _fake_load_config,
    )
    # Reset the resolver cache so each test sees a fresh state.
    _urls_mod.reload()

    def _set(updates: Dict[str, Any]) -> None:
        override_dict.clear()
        override_dict.update(updates)
        _urls_mod.reload()

    return _set


def test_user_override_server_base_url(user_config_override) -> None:
    """The ``urls.server_base_url`` XDG key overrides the bundled default."""
    user_config_override(
        {"urls": {"server_base_url": "http://192.168.1.67"}}
    )
    assert urls.server_base_url() == "http://192.168.1.67"


def test_user_override_home_page(user_config_override) -> None:
    """The ``urls.home_page`` XDG key overrides the bundled default."""
    user_config_override(
        {"urls": {"home_page": "http://192.168.1.67/"}}
    )
    assert urls.home_page() == "http://192.168.1.67/"


def test_user_override_strips_trailing_slash_on_api_urls(
    user_config_override,
) -> None:
    """Operator-friendly: a trailing slash on an API URL is normalised away."""
    user_config_override(
        {"urls": {"server_base_url": "http://192.168.1.67/"}}
    )
    assert urls.server_base_url() == "http://192.168.1.67"


def test_user_override_unknown_key_warns(
    user_config_override, monkeypatch
) -> None:
    """Typo'd override key logs a warning (doesn't raise).

    We don't drop the override silently — we'd rather the operator
    sees a warning and investigates than ship a broken config.

    Note: we attach a list handler directly to the urls.logma
    instance because Logma (the kahndor logger) is detached from
    the stdlib logging hierarchy — its ``.parent`` is ``None`` —
    so caplog's root-level handlers don't capture its records.
    Direct attachment is the only reliable way to test.
    """
    import logging
    import nchantdoffice.utilities.urls as _urls_mod
    captured: list[logging.LogRecord] = []

    class _CaptureHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            captured.append(record)

    handler = _CaptureHandler(level=logging.WARNING)
    _urls_mod.logma.addHandler(handler)
    try:
        user_config_override(
            {"urls": {"server_base_URL": "http://typo.example/"}}
        )
        # The unknown key is filtered out; the bundled default is
        # still in effect.
        assert urls.server_base_url() == "https://api.nchantdoffice.com"
    finally:
        _urls_mod.logma.removeHandler(handler)

    matches = [
        r for r in captured
        if "server_base_URL" in r.getMessage()
    ]
    assert matches, (
        f"expected WARNING for unknown key 'server_base_URL' "
        f"in captured records; got: {[r.getMessage() for r in captured]}"
    )


# -----------------------------------------------------------------------------
# Regression guard: no caller hardcodes a hostname
# -----------------------------------------------------------------------------


# Files / dirs we exempt from the grep — the yaml + this test
# + docstrings that mention the hostname as part of the contract.
EXEMPT_PATHS = {
    # The bundled yaml — production defaults are intentional.
    "nchantdoffice/utilities/_data_/urls.yaml",
    # This test file — the grep hits itself.
    "tests/utilities/test_urls_config.py",
    # The resolver module — it has the constants.
    "nchantdoffice/utilities/urls.py",
    # The user_config module — its docstring carries an example
    # config that names the production URL.
    "nchantdoffice/utilities/user_config.py",
    # The license/remote.py + license/claim_flow.py docstrings
    # mention the production URL as part of their contract docs.
    "nchantdoffice/license/remote.py",
    "nchantdoffice/license/claim_flow.py",
}


def test_no_hardcoded_hostnames_in_nchantdoffice_source() -> None:
    """No module in nchantdoffice/ (outside the resolver + yaml) hardcodes
    ``nchantdoffice.com`` or ``api.nchantdoffice.com``.

    This is the regression guard for DESK T-NEW-052. If this
    test fails, someone added a new ``BASE_URL = "https://…nchantdoffice…"``
    constant instead of routing through the resolver.

    Docstrings (which use the production hostname as part of the
    contract documentation) are exempted via a two-pass scan:
      1. AST walk to find every docstring's source line range.
      2. Line scan, skipping lines inside any docstring range.
    """
    import ast

    repo_root = Path(__file__).resolve().parents[2]
    src_root = repo_root / "nchantdoffice"
    hits: list[tuple[str, int, str]] = []
    for py_file in src_root.rglob("*.py"):
        rel = py_file.relative_to(repo_root).as_posix()
        if rel in EXEMPT_PATHS:
            continue
        try:
            text = py_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        # Step 1: collect docstring line ranges via AST.
        # A docstring starts at the first line of a string
        # expression statement (Module / FunctionDef / ClassDef /
        # AsyncFunctionDef body[0]) and ends at the matching
        # triple-quote. We use a rough heuristic that matches
        # this codebase's docstring convention (single-line
        # ``"""..."""`` or multi-line ``"""\n...\n"""``).
        docstring_ranges: list[tuple[int, int]] = []
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        if tree is not None:
            lines = text.splitlines(keepends=True)
            for node in ast.walk(tree):
                if isinstance(
                    node,
                    (
                        ast.Module,
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                        ast.ClassDef,
                    ),
                ):
                    body = getattr(node, "body", [])
                    if (
                        body
                        and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)
                    ):
                        start = body[0].lineno
                        end = getattr(body[0], "end_lineno", start) or start
                        docstring_ranges.append((start, end))

        def _in_docstring(lineno: int) -> bool:
            for s, e in docstring_ranges:
                if s <= lineno <= e:
                    return True
            return False

        # Step 2: line scan, skip docstrings + pure comments.
        # Also handle inline trailing comments: split on first '#'
        # (outside string literals — we approximate by trimming from
        # the rightmost '#' that's preceded by whitespace, which is
        # good enough for this codebase's style).
        import re
        for lineno, line in enumerate(text.splitlines(), start=1):
            # Drop inline comments — find the LAST '#' preceded by
            # whitespace (so we don't accidentally match '#' inside
            # a string literal in this codebase's style).
            stripped_full = line
            match = re.search(r"\s+#", line)
            if match:
                code_part = line[: match.start()]
            else:
                code_part = line
            if (
                "nchantdoffice.com" not in code_part
                and "api.nchantdoffice.com" not in code_part
            ):
                continue
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            if _in_docstring(lineno):
                continue
            hits.append((rel, lineno, line.strip()))

    if hits:
        msg = "\n".join(
            f"  {rel}:{lineno}: {line}"
            for rel, lineno, line in hits
        )
        pytest.fail(
            "Hardcoded nchantdoffice.com / api.nchantdoffice.com found in "
            "source (route through nchantdoffice.utilities.urls instead):\n"
            + msg
        )