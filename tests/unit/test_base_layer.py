"""Tests for the desktop base-layer ad feed client (T-DESK-063).

Pins the contract that:
  1. ``get_base_layer_ads()`` returns a list of ad dicts
     matching the FALLBACK_BANNERS shape.
  2. Fresh cache is returned without hitting the server.
  3. Stale cache triggers a server fetch.
  4. Server failure falls back to stale cache, then empty.
  5. ``force_refresh=True`` bypasses the cache.
  6. Cache file is written with mode 0600.
  7. ``_extract_ads`` handles malformed cache gracefully.
"""
# -*- coding: utf-8 -*-
import datetime as dt
from unittest.mock import MagicMock, patch

import pytest

from nchantdoffice.utilities import base_layer


# ── Fixtures ───────────────────────────────────────────────


SAMPLE_ADS = [
    {
        "id": 1,
        "slug": "notion-q3-2026",
        "title": "Try Notion - All-in-one workspace",
        "subtitle": "Get 50% off your first year.",
        "cta_text": "Get Notion",
        "cta_url": "https://www.notion.so/affiliate?ref=nchantdoffice",
        "background": "#FF6B6B",
        "foreground": "#FFFFFF",
        "icon_url": "",
        "priority": 100,
        "status": "active",
    },
    {
        "id": 2,
        "slug": "railway-default",
        "title": "Railway - Deploy in seconds",
        "subtitle": "$5 credit for every new Railway user.",
        "cta_text": "Try Railway",
        "cta_url": "https://railway.app?ref=nchantdoffice",
        "background": "#1F2937",
        "foreground": "#FFFFFF",
        "icon_url": "",
        "priority": 110,
        "status": "active",
    },
]

SAMPLE_SERVER_RESPONSE = {
    "as_of": "2026-08-07T15:00:00Z",
    "count": 2,
    "ads": SAMPLE_ADS,
}


@pytest.fixture
def fresh_cache_env(tmp_path, monkeypatch):
    """Redirect the cache to a temp directory and reset
    any environment overrides."""
    cache_dir = tmp_path / ".nchantd"
    monkeypatch.setattr(base_layer, "_CACHE_DIR", cache_dir)
    monkeypatch.setattr(
        base_layer, "_CACHE_PATH", cache_dir / "base_layer_cache.json",
    )
    return cache_dir


@pytest.fixture
def mock_requests():
    """Patch ``requests.get`` with a mock that returns
    SAMPLE_SERVER_RESPONSE."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_SERVER_RESPONSE
    with patch.object(base_layer, "requests") as mock_req:
        mock_req.get.return_value = mock_resp
        yield mock_req


# ── Cache freshness ────────────────────────────────────────


class TestCacheFreshness:
    """The cache is considered fresh if it's younger than
    REFRESH_INTERVAL_SECONDS (6h)."""

    def test_missing_cache_is_not_fresh(self):
        assert not base_layer._cache_is_fresh(None)

    def test_recent_cache_is_fresh(self):
        cache = {
            "_cached_at": dt.datetime.utcnow().isoformat(),
            "ads": SAMPLE_ADS,
        }
        assert base_layer._cache_is_fresh(cache)

    def test_old_cache_is_not_fresh(self):
        old = dt.datetime.utcnow() - dt.timedelta(hours=7)
        cache = {
            "_cached_at": old.isoformat(),
            "ads": SAMPLE_ADS,
        }
        assert not base_layer._cache_is_fresh(cache)

    def test_cache_without_timestamp_is_not_fresh(self):
        cache = {"ads": SAMPLE_ADS}
        assert not base_layer._cache_is_fresh(cache)

    def test_cache_with_garbage_timestamp_is_not_fresh(self):
        cache = {"_cached_at": "not-a-date", "ads": SAMPLE_ADS}
        assert not base_layer._cache_is_fresh(cache)


# ── Cache read/write ────────────────────────────────────────


class TestCacheReadWrite:
    """Cache file read/write round-trip."""

    def test_write_then_read(self, fresh_cache_env):
        data = {"ads": SAMPLE_ADS, "_cached_at": "2026-08-07T12:00:00"}
        base_layer._write_cache(data)
        result = base_layer._read_cache()
        assert result is not None
        assert result["ads"] == SAMPLE_ADS

    def test_read_missing_file_returns_none(self, fresh_cache_env):
        assert base_layer._read_cache() is None

    def test_read_corrupt_json_returns_none(self, fresh_cache_env):
        base_layer._CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        base_layer._CACHE_PATH.write_text("{corrupt", encoding="utf-8")
        assert base_layer._read_cache() is None

    def test_write_creates_parent_dir(self, fresh_cache_env):
        """The cache dir doesn't exist on first launch."""
        assert not fresh_cache_env.exists()
        base_layer._write_cache({"ads": [], "_cached_at": "x"})
        assert fresh_cache_env.exists()

    def test_write_sets_secure_permissions(self, fresh_cache_env):
        """Cache file must be mode 0600 so other users on
        the machine can't read the desktop's ad state."""
        base_layer._write_cache({"ads": [], "_cached_at": "x"})
        mode = base_layer._CACHE_PATH.stat().st_mode & 0o777
        assert mode == 0o600, f"Expected 0600, got {oct(mode)}"


# ── Extract ads ────────────────────────────────────────────


class TestExtractAds:
    """_extract_ads pulls the 'ads' list from a cache dict."""

    def test_normal_extraction(self):
        cache = {"ads": SAMPLE_ADS}
        result = base_layer._extract_ads(cache)
        assert len(result) == 2
        assert result[0]["slug"] == "notion-q3-2026"

    def test_none_returns_empty(self):
        assert base_layer._extract_ads(None) == []

    def test_missing_ads_key_returns_empty(self):
        assert base_layer._extract_ads({"other": "data"}) == []

    def test_non_list_ads_returns_empty(self):
        cache = {"ads": "not a list"}
        assert base_layer._extract_ads(cache) == []


# ── Server fetch ───────────────────────────────────────────


class TestServerFetch:
    """_fetch_from_server calls the endpoint correctly."""

    def test_successful_fetch(self, mock_requests):
        result = base_layer._fetch_from_server("https://example.com")
        assert result is not None
        assert result["count"] == 2
        assert len(result["ads"]) == 2
        mock_requests.get.assert_called_once()
        url = mock_requests.get.call_args[0][0]
        assert url == "https://example.com/api/ads/base-layer"

    def test_non_200_returns_none(self, mock_requests):
        mock_requests.get.return_value.status_code = 500
        result = base_layer._fetch_from_server("https://example.com")
        assert result is None

    def test_malformed_json_returns_none(self, mock_requests):
        mock_requests.get.return_value.json.return_value = "not a dict"
        result = base_layer._fetch_from_server("https://example.com")
        assert result is None

    def test_missing_ads_key_returns_none(self, mock_requests):
        mock_requests.get.return_value.json.return_value = {"no_ads": []}
        result = base_layer._fetch_from_server("https://example.com")
        assert result is None

    def test_network_error_returns_none(self):
        with patch.object(base_layer, "requests") as mock_req:
            mock_req.get.side_effect = ConnectionError("timeout")
            result = base_layer._fetch_from_server("https://example.com")
        assert result is None

    def test_requests_not_installed_returns_none(self):
        with patch.object(base_layer, "requests", None):
            result = base_layer._fetch_from_server("https://example.com")
        assert result is None


# ── Main entry point: get_base_layer_ads ────────────────────


class TestGetBaseLayerAds:
    """The main entry point orchestrates cache + server."""

    def test_fresh_cache_no_server_call(
        self, fresh_cache_env, mock_requests
    ):
        """If the cache is fresh, don't hit the server."""
        now = dt.datetime.utcnow().isoformat()
        base_layer._write_cache({
            "ads": SAMPLE_ADS,
            "_cached_at": now,
        })
        result = base_layer.get_base_layer_ads()
        assert len(result) == 2
        mock_requests.get.assert_not_called()

    def test_stale_cache_triggers_fetch(
        self, fresh_cache_env, mock_requests
    ):
        """Stale cache triggers a server fetch."""
        old = (dt.datetime.utcnow() - dt.timedelta(hours=7)).isoformat()
        base_layer._write_cache({
            "ads": [{"title": "old ad"}],
            "_cached_at": old,
        })
        result = base_layer.get_base_layer_ads()
        assert len(result) == 2
        assert result[0]["slug"] == "notion-q3-2026"
        mock_requests.get.assert_called_once()

    def test_no_cache_triggers_fetch(
        self, fresh_cache_env, mock_requests
    ):
        """No cache file triggers a server fetch."""
        result = base_layer.get_base_layer_ads()
        assert len(result) == 2
        mock_requests.get.assert_called_once()

    def test_server_failure_falls_back_to_stale_cache(
        self, fresh_cache_env, mock_requests
    ):
        """Server unreachable → use stale cache if any."""
        old = (dt.datetime.utcnow() - dt.timedelta(hours=7)).isoformat()
        base_layer._write_cache({
            "ads": [{"title": "stale but usable"}],
            "_cached_at": old,
        })
        mock_requests.get.return_value.status_code = 500
        result = base_layer.get_base_layer_ads()
        assert len(result) == 1
        assert result[0]["title"] == "stale but usable"

    def test_no_cache_no_server_returns_empty(
        self, fresh_cache_env, mock_requests
    ):
        """No cache + server failure = empty list (the ad
        tab falls back to FALLBACK_BANNERS)."""
        mock_requests.get.return_value.status_code = 500
        result = base_layer.get_base_layer_ads()
        assert result == []

    def test_force_refresh_bypasses_cache(
        self, fresh_cache_env, mock_requests
    ):
        """force_refresh=True always hits the server."""
        now = dt.datetime.utcnow().isoformat()
        base_layer._write_cache({
            "ads": [{"title": "fresh cached"}],
            "_cached_at": now,
        })
        result = base_layer.get_base_layer_ads(force_refresh=True)
        assert len(result) == 2
        assert result[0]["slug"] == "notion-q3-2026"
        mock_requests.get.assert_called_once()

    def test_successful_fetch_writes_cache(
        self, fresh_cache_env, mock_requests
    ):
        """A successful fetch writes the result to cache."""
        base_layer.get_base_layer_ads()
        cache = base_layer._read_cache()
        assert cache is not None
        assert "_cached_at" in cache
        assert len(cache["ads"]) == 2


# ── Clear cache ────────────────────────────────────────────


class TestClearCache:
    def test_clear_removes_file(self, fresh_cache_env):
        base_layer._write_cache({"ads": [], "_cached_at": "x"})
        assert base_layer._CACHE_PATH.exists()
        base_layer.clear_cache()
        assert not base_layer._CACHE_PATH.exists()

    def test_clear_missing_file_no_error(self, fresh_cache_env):
        """clear_cache on a non-existent file doesn't crash."""
        base_layer.clear_cache()  # Should not raise.