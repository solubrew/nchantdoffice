"""Tests for nchantdoffice.utilities.user_config (DESK T-NEW-052 follow-up).

Verifies that ``DEFAULTS`` ships with an ``urls:`` section so the
on-install seed (via :func:`write_default_config`) gives the
operator a place to put internal-host overrides without having
to invent the key.
"""
from __future__ import annotations

import yaml
from pathlib import Path

import pytest

from nchantdoffice.utilities import user_config
from nchantdoffice.utilities.user_config import DEFAULTS, write_default_config


def test_defaults_has_urls_section() -> None:
    """The DEFAULTS dict must include a top-level ``urls`` key.

    DESK T-NEW-052: ``write_default_config`` writes DEFAULTS to
    ``~/.config/nchantdoffice/config.yaml`` on first launch.
    If ``urls`` is missing, the seeded file has no place for the
    operator to put ``urls.server_base_url: http://192.168.1.67``
    without manually inventing the key.
    """
    assert "urls" in DEFAULTS, (
        "DEFAULTS dict missing 'urls' key — write_default_config "
        "would seed ~/.config/nchantdoffice/config.yaml without "
        "a placeholder for internal-host overrides."
    )
    assert isinstance(DEFAULTS["urls"], dict), (
        f"DEFAULTS['urls'] must be a mapping, got {type(DEFAULTS['urls'])}"
    )


def test_write_default_config_seeds_urls_section(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``write_default_config`` writes a config file containing the
    empty ``urls:`` section.

    Regression guard: if a future refactor removes ``urls`` from
    DEFAULTS, the seeded file on a fresh install won't have a
    place for per-host overrides.
    """
    target = tmp_path / "config.yaml"
    # Patch the module-level USER_CONFIG_PATH so write_default_config
    # doesn't touch the operator's real XDG config.
    monkeypatch.setattr(user_config, "USER_CONFIG_PATH", target)
    # Force write_default_config to NOT skip (the default short-circuits
    # when the path exists; in this fresh tmp_path it doesn't).
    write_default_config(path=target)

    assert target.exists(), "write_default_config did not create the file"
    with target.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict)
    assert "urls" in data, (
        f"seeded config missing 'urls' key — content: {data!r}"
    )
    assert data["urls"] == {}, (
        f"seeded urls section must be empty placeholder, got {data['urls']!r}"
    )


def test_load_config_preserves_urls_when_xdg_lacks_them(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Existing installs have an XDG config without ``urls:`` —
    ``load_config`` must return ``urls={}`` so the resolver falls
    through to bundled defaults instead of raising KeyError.

    The merged result should be ``{"urls": {}, ...}`` because
    DEFAULTS provides the placeholder and the XDG file's lack
    of ``urls`` doesn't overwrite it.
    """
    # Write an XDG file WITHOUT the urls key (simulates an
    # existing install from before DESK T-NEW-052).
    xdg = tmp_path / "xdg_config.yaml"
    xdg.write_text(
        "dev_mode: true\n"
        "server:\n"
        "  url: http://legacy-host:5000\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(user_config, "USER_CONFIG_PATH", xdg)
    monkeypatch.setattr(user_config, "get_cwd_override_path",
                        lambda: tmp_path / "nchantdoffice.yaml")

    merged = user_config.load_config()

    assert "urls" in merged, (
        f"merged config must keep 'urls' placeholder from DEFAULTS, "
        f"got keys: {sorted(merged.keys())}"
    )
    assert merged["urls"] == {}
    # The XDG-supplied values still win.
    assert merged["dev_mode"] is True
    assert merged["server"]["url"] == "http://legacy-host:5000"


def test_load_config_merges_urls_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When the operator adds a ``urls:`` block to their XDG config,
    ``load_config`` must merge those overrides in (the resolver
    sees them and uses them in place of the bundled defaults).
    """
    xdg = tmp_path / "xdg_config.yaml"
    xdg.write_text(
        "urls:\n"
        "  server_base_url: http://192.168.1.67\n"
        "  home_page: http://192.168.1.67/\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(user_config, "USER_CONFIG_PATH", xdg)
    monkeypatch.setattr(user_config, "get_cwd_override_path",
                        lambda: tmp_path / "nchantdoffice.yaml")

    merged = user_config.load_config()

    assert merged["urls"]["server_base_url"] == "http://192.168.1.67"
    assert merged["urls"]["home_page"] == "http://192.168.1.67/"