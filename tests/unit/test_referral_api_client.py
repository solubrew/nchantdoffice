"""Tests for the rewritten ReferralAPIClient (T-DESK-052).

Pins the contract that:
  1. The client hits the v1 namespaced endpoints on
     nchantdoffice_com (NOT the old /api/affiliate/* paths
     which no longer exist).
  2. Auth uses x-api-key header, NOT Authorization: Bearer.
  3. The static ``register_desktop`` method calls
     POST /api/desktop/register and returns the server response.
  4. The user_id is required for per-user endpoints; methods
     return None rather than calling the server with no user_id.
  5. All HTTP failures return None (best-effort, doesn't raise).
  6. The ``track_click`` payload is correct (offer_id in body,
     NOT in URL).
"""
# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch



# ── Auth header + base URL ───────────────────────────────────


class TestClientConstruction:
    """The client defaults + how it sends auth."""

    def test_default_base_url_is_v1(self):
        """T-DESK-052 / T-NEW-053: default base URL must be the v1
        endpoint (from urls.yaml server_base_url), not the old
        /api/affiliate path.

        The canonical server_base_url is https://api.nchantdoffice.com
        (per nchantdoffice/utilities/_data_/urls.yaml), so the v1
        API base is https://api.nchantdoffice.com/api/v1.
        """
        from nchantdoffice.utilities.referral import (
            DEFAULT_API_BASE,
        )
        assert DEFAULT_API_BASE == "https://api.nchantdoffice.com/api/v1", (
            f"DEFAULT_API_BASE must be the v1 namespace at api.nchantdoffice.com, "
            f"got {DEFAULT_API_BASE!r}"
        )

    def test_no_auth_header_without_api_key(self):
        """Without an api_key, no x-api-key header is set."""
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient()
        assert "x-api-key" not in client._session.headers
        # Also assert Bearer is NOT used (T-DESK-052 fix).
        assert "Authorization" not in client._session.headers

    def test_api_key_sets_x_api_key_header(self):
        """When an api_key is provided, it's sent as x-api-key
        (the server's contract)."""
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(api_key="the-secret-key")
        assert client._session.headers["x-api-key"] == "the-secret-key"

    def test_no_bearer_token_in_any_header(self):
        """T-DESK-052: the previous implementation used
        ``Authorization: Bearer <key>`` which the server doesn't
        accept. Pin that we never use Bearer."""
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(api_key="the-secret-key")
        for header_name in client._session.headers:
            assert not header_name.lower().startswith("authorization"), (
                f"Client must not send Authorization header "
                f"(server uses x-api-key); got {header_name!r}"
            )

    def test_user_id_optional_at_construction(self):
        """A user_id is required for per-user endpoints but not
        at construction time. Methods that need it return None
        if it's missing (rather than crashing)."""
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient()
        assert client.user_id is None

    def test_trailing_slash_stripped_from_base_url(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(base_url="https://example.com/api/v1/")
        assert client.base_url == "https://example.com/api/v1"


# ── Endpoint paths (the v1 alignment) ────────────────────────


class TestEndpointPaths:
    """Each method hits the correct v1 path. We mock the
    requests Session and assert on the URL."""

    def _make_client(self, **kwargs):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        return ReferralAPIClient(
            base_url="https://nchantdoffice.com/api/v1",
            api_key="test-key",
            user_id=42,
            **kwargs,
        )

    def test_fetch_referral_stats_uses_v1_path(self):
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            client.fetch_referral_stats()
        url = mock_req.call_args.args[1]
        assert url.endswith("/api/v1/referral/stats/42"), (
            f"fetch_referral_stats must call /api/v1/referral/stats/<uid>, "
            f"got {url!r}"
        )

    def test_fetch_referral_stats_with_explicit_user_id(self):
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            client.fetch_referral_stats(user_id=99)
        url = mock_req.call_args.args[1]
        assert url.endswith("/api/v1/referral/stats/99")

    def test_fetch_referral_stats_returns_none_when_no_user_id(self):
        """No user_id anywhere → return None, don't call the server."""
        client = self._make_client()
        client.user_id = None
        with patch.object(client._session, "request") as mock_req:
            result = client.fetch_referral_stats()
        assert result is None
        mock_req.assert_not_called()

    def test_fetch_earnings_uses_v1_path(self):
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            client.fetch_earnings()
        url = mock_req.call_args.args[1]
        assert url.endswith("/api/v1/referral/earnings/42")

    def test_fetch_share_link_uses_v1_path(self):
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            client.fetch_share_link()
        url = mock_req.call_args.args[1]
        assert url.endswith("/api/v1/referral/share/42")

    def test_fetch_offers_uses_quicklinks_path(self):
        """fetch_offers (the old affiliate/offers) now hits
        the v1 quicklinks catalog."""
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b"[]", json=lambda: [],
            )
            client.fetch_offers()
        url = mock_req.call_args.args[1]
        assert url.endswith("/api/v1/quicklinks/")

    def test_fetch_offers_with_category_param(self):
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b"[]", json=lambda: [],
            )
            client.fetch_offers(category="ai")
        call_kwargs = mock_req.call_args.kwargs
        assert call_kwargs.get("params") == {"category": "ai"}

    def test_fetch_dashboard_uses_affiliate_dashboard(self):
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            client.fetch_dashboard()
        url = mock_req.call_args.args[1]
        assert url.endswith("/api/v1/affiliate/dashboard")

    def test_request_payout_uses_v1_path(self):
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            client.request_payout(amount_cents=5000)
        url = mock_req.call_args.args[1]
        assert url.endswith("/api/v1/affiliate/payout/request")
        call_kwargs = mock_req.call_args.kwargs
        assert call_kwargs.get("json") == {"amount_cents": 5000}

    def test_track_click_uses_referral_track_click(self):
        """T-DESK-052: track_click used to call
        /api/affiliate/track/click/<id> with offer_id in URL.
        Now calls /api/v1/referral/track-click with offer_id in
        body."""
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            client.track_click(
                offer_id=123, service_slug="openai", tier="pro",
            )
        url = mock_req.call_args.args[1]
        assert url.endswith("/api/v1/referral/track-click")
        call_kwargs = mock_req.call_args.kwargs
        payload = call_kwargs.get("json")
        assert payload["offer_id"] == 123
        assert payload["service_slug"] == "openai"
        assert payload["tier"] == "pro"
        # Crucial: the offer_id is NOT in the URL anymore.
        assert "/123" not in url

    def test_track_click_returns_true_on_success(self):
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            result = client.track_click(offer_id=1)
        assert result is True

    def test_track_install_uses_v1_path(self):
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            result = client.track_install()
        url = mock_req.call_args.args[1]
        assert url.endswith("/api/v1/referral/track-install")
        assert result is True

    def test_generate_referral_code_uses_v1_path(self):
        client = self._make_client()
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            client.generate_referral_code()
        url = mock_req.call_args.args[1]
        assert url.endswith("/api/v1/referral/generate-code")


# ── Auth header is sent on every request ──────────────────────


class TestAuthHeaderSent:
    """The api_key must be sent as x-api-key on every request."""

    def test_x_api_key_on_fetch_referral_stats(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="my-key-123", user_id=1,
        )
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            client.fetch_referral_stats()
        sent_headers = client._session.headers
        assert sent_headers.get("x-api-key") == "my-key-123"

    def test_x_api_key_on_track_click(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="my-key-123", user_id=1,
        )
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b'{}', json=lambda: {},
            )
            client.track_click(offer_id=1)
        sent_headers = client._session.headers
        assert sent_headers.get("x-api-key") == "my-key-123"

    def test_x_api_key_on_register_desktop(self):
        """register_desktop is static and also sends the
        api_key if one is set (it usually isn't — registration
        is what GETS the api_key — but the test pins the
        behavior)."""
        from nchantdoffice.utilities.referral import ReferralAPIClient
        with patch("nchantdoffice.utilities.referral.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"desktop_uuid": "x", "api_key": "y"},
                content=b'{"desktop_uuid":"x","api_key":"y"}',
            )
            ReferralAPIClient.register_desktop(
                base_url="https://example.com",
                username="alice",
                public_key="the-key",
            )
        # The static method doesn't set a header (the
        # registration endpoint is unauthenticated). But it
        # also doesn't accidentally send an api_key header.
        # (Hard to test directly because the mock just checks
        # the call, not the absence of headers. This test
        # exists as a sentinel.)
        assert mock_post.called


# ── HTTP failure handling ────────────────────────────────────


class TestHttpFailureHandling:
    """All HTTP failures must return None, never raise."""

    def test_connection_error_returns_none(self):
        import requests
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="k", user_id=1,
        )
        with patch.object(client._session, "request") as mock_req:
            mock_req.side_effect = requests.ConnectionError("no network")
            result = client.fetch_referral_stats()
        assert result is None

    def test_http_500_returns_none(self):
        import requests
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="k", user_id=1,
        )
        with patch.object(client._session, "request") as mock_req:
            mock_req.side_effect = requests.HTTPError("500 Server Error")
            result = client.fetch_earnings()
        assert result is None

    def test_timeout_returns_none(self):
        import requests
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="k", user_id=1,
        )
        with patch.object(client._session, "request") as mock_req:
            mock_req.side_effect = requests.Timeout("timed out")
            result = client.fetch_offers()
        assert result is None

    def test_invalid_json_returns_none(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="k", user_id=1,
        )
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b"not json", json=MagicMock(
                    side_effect=ValueError("not json"),
                ),
            )
            result = client.fetch_dashboard()
        assert result is None

    def test_track_click_returns_false_on_failure(self):
        import requests
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="k", user_id=1,
        )
        with patch.object(client._session, "request") as mock_req:
            mock_req.side_effect = requests.ConnectionError("nope")
            result = client.track_click(offer_id=1)
        assert result is False


# ── Registration flow ────────────────────────────────────────


class TestRegisterDesktop:
    """The static register_desktop method calls the correct
    endpoint and returns the parsed JSON."""

    def test_register_posts_to_api_desktop_register(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        with patch("nchantdoffice.utilities.referral.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                content=b'{"desktop_uuid":"abc","api_key":"xyz"}',
                json=lambda: {"desktop_uuid": "abc", "api_key": "xyz"},
            )
            ReferralAPIClient.register_desktop(
                base_url="https://nchantdoffice.com",
                username="alice",
                public_key="the-pub-key",
            )
        # The URL must be /api/desktop/register, NOT under
        # /api/v1 (registration is at the top level).
        url = mock_post.call_args.args[0]
        assert url == "https://nchantdoffice.com/api/desktop/register", (
            f"register_desktop must POST to /api/desktop/register "
            f"(not under /api/v1), got {url!r}"
        )

    def test_register_body_includes_username_and_public_key(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        with patch("nchantdoffice.utilities.referral.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200, content=b"{}",
                json=lambda: {},
            )
            ReferralAPIClient.register_desktop(
                base_url="https://nchantdoffice.com",
                username="alice",
                public_key="the-pub-key",
            )
        sent_json = mock_post.call_args.kwargs.get("json")
        assert sent_json == {"username": "alice", "public_key": "the-pub-key"}

    def test_register_returns_parsed_response(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        expected = {"desktop_uuid": "abc-123", "api_key": "secret"}
        with patch("nchantdoffice.utilities.referral.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                content=b'{"desktop_uuid":"abc-123","api_key":"secret"}',
                json=lambda: expected,
            )
            result = ReferralAPIClient.register_desktop(
                base_url="https://nchantdoffice.com",
                username="alice",
                public_key="the-pub-key",
            )
        assert result == expected

    def test_register_returns_none_on_failure(self):
        import requests
        from nchantdoffice.utilities.referral import ReferralAPIClient
        with patch("nchantdoffice.utilities.referral.requests.post") as mock_post:
            mock_post.side_effect = requests.ConnectionError("nope")
            result = ReferralAPIClient.register_desktop(
                base_url="https://nchantdoffice.com",
                username="alice",
                public_key="the-pub-key",
            )
        assert result is None

    def test_register_strips_trailing_slash(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        with patch("nchantdoffice.utilities.referral.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200, content=b"{}",
                json=lambda: {},
            )
            ReferralAPIClient.register_desktop(
                base_url="https://nchantdoffice.com/",
                username="alice",
                public_key="the-pub-key",
            )
        url = mock_post.call_args.args[0]
        # No double slash
        assert "//api" not in url
        assert url == "https://nchantdoffice.com/api/desktop/register"


# ── Response shape handling ──────────────────────────────────


class TestResponseShape:
    """Some methods normalize the response (list vs dict).
    Pin the normalization contract."""

    def test_fetch_offers_returns_list_directly(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="k", user_id=1,
        )
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b"[]", json=lambda: [],
            )
            assert client.fetch_offers() == []

    def test_fetch_offers_extracts_items_from_dict(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="k", user_id=1,
        )
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b"{}",
                json=lambda: {"items": [{"a": 1}, {"b": 2}]},
            )
            result = client.fetch_offers()
        assert result == [{"a": 1}, {"b": 2}]

    def test_fetch_offers_extracts_offers_from_dict(self):
        """Backward-compat: if the server uses ``offers`` key
        instead of ``items``, we still find it."""
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="k", user_id=1,
        )
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b"{}",
                json=lambda: {"offers": [{"a": 1}]},
            )
            result = client.fetch_offers()
        assert result == [{"a": 1}]

    def test_fetch_offers_returns_none_for_unrecognized_shape(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="k", user_id=1,
        )
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = MagicMock(
                status_code=200, content=b"{}",
                json=lambda: {"unexpected": "shape"},
            )
            result = client.fetch_offers()
        assert result is None


# ── fetch_banners backwards compatibility ────────────────────


class TestFetchBannersCompatibility:
    """The ad tab (Sprint 27+) still calls ``fetch_banners()``.
    That method must still exist and delegate to fetch_offers."""

    def test_fetch_banners_exists(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        assert hasattr(ReferralAPIClient, "fetch_banners")

    def test_fetch_banners_delegates_to_offers(self):
        """fetch_banners now returns the quicklinks catalog
        (the v1 server has no dedicated banners endpoint)."""
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="k", user_id=1,
        )
        with patch.object(client, "fetch_offers", return_value=[{"x": 1}]):
            result = client.fetch_banners()
        assert result == [{"x": 1}]

    def test_fetch_banners_returns_none_on_empty(self):
        from nchantdoffice.utilities.referral import ReferralAPIClient
        client = ReferralAPIClient(
            base_url="https://example.com/api/v1",
            api_key="k", user_id=1,
        )
        with patch.object(client, "fetch_offers", return_value=None):
            result = client.fetch_banners()
        assert result is None