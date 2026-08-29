# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid:
        name:
        description: >
        version: 0.0.0.0.0.0
        authority: filesystem
        security: seclvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt
import json

# ======================================3rd Party Library Modules=====================================================||
import requests
from typing import Optional, Dict, Any, Set
import time

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "links.yaml")


def update_affiliate_links(model, last_affiliate_update_dttm: str = "2025-01-01 00:00:00", reload=False) -> Dict[str, int]:
    """T-070: fetch links from the API, split into affiliate / non-affiliate rows.

    Steps:
      1. If ``reload=True``, drop the link_affiliate rows first.
      2. GET the link list from ``API_URL?since_dttm=last_update``.
      3. For each link:
           - If it has an ``affiliate_id`` matching an existing
             affiliate record, insert a link_affiliate row
           - Otherwise persist it as a plain link
      4. Persist the join results on ``model`` via its update/
         remove_affiliate helpers (best-effort).

    Returns the count of affiliate / non-affiliate rows.
    """
    from kahndor.logma import Logma
    log = Logma(__name__)
    # DESK T-NEW-052: routes through the unified URL config so
    # the operator can redirect the affiliate API at an internal
    # endpoint without code edits.
    #
    # DESK T-NEW-055: ``affiliate_api_base()`` returns just the
    # API root (``/api/affiliate``); the resource path
    # ``links/`` is appended below. The pre-T-NEW-052 code
    # hardcoded ``.../api/affiliate/links/`` here AND passed
    # ``"affiliate/links/"`` to ``client.get()``, producing a
    # doubled path (``/api/affiliate/links/affiliate/links/``).
    # Production was masking this with a wildcard route; dev
    # mode surfaced the bug with a hard 404/connection-refused.
    from nchantdoffice.utilities.urls import server_base_url as _sbu
    API_URL = _sbu()
    # DESK T-NEW-057: the server's @require_desktop_api_key
    # decorator reads ``x-api-key`` (NOT Authorization: Bearer).
    # Read the install's api_key from the global InstallStore
    # so the header is present on affiliate requests.
    #
    # DESK T-NEW-058: if the install hasn't bootstrapped yet
    # (api_key is None because the desktop just started and
    # the install-bootstrap HTTP call hasn't completed — or
    # returned 4xx/5xx and was swallowed by the fail-soft
    # orchestrator), SKIP the network call entirely. Sending
    # a request without credentials is wasted bandwidth + a
    # noisy 401 in the log. The next launch — once the
    # bootstrap has minted an api_key — will retry.
    api_key: Optional[str] = None
    install_id: Optional[str] = None
    try:
        from nchantdoffice.license.install_store import (
            InstallStore as _InstallStore,
        )
        try:
            _record = _InstallStore().get_or_create()
            api_key = _record.get("api_key")
            install_id = _record.get("install_id")
        except Exception as _exc:
            log.warning(
                f"[links] api_key lookup failed (non-blocking): {_exc}"
            )
    except ImportError:
        log.info("[links] InstallStore module not importable; skipping affiliate sync")

    if not api_key:
        # DESK T-NEW-058: pre-bootstrap skip. Log clearly so the
        # operator can correlate with the bootstrap log lines
        # in the same session and understand WHY the affiliate
        # sync is silent. Common reasons:
        #   - Fresh install, install-bootstrap hasn't completed yet
        #   - Install bootstrap returned 4xx/5xx and was
        #     swallowed fail-soft by startup_refresh
        #   - install.bin was deleted / corrupted
        # In all cases the next launch will retry once the
        # bootstrap has minted a valid api_key.
        log.info(
            f"[links] skip affiliate sync: no api_key in InstallStore "
            f"yet (install_id={install_id!r}). The next launch will "
            f"retry once the install bootstrap completes. "
            f"Set run-mode=prod if you want to bypass the LAN docker."
        )
        return {
            "affiliate_count": 0,
            "non_affiliate_count": 0,
        }

    log.info(
        f"[links] update_affiliate_links: using api_key for "
        f"install_id={install_id!r} against {API_URL}"
    )
    client = APIClient(API_URL, api_key=api_key)
    if reload:
        last_affiliate_update_dttm = "2025-01-01 00:00:00"
        try:
            model.remove_affiliate_links()
        except Exception as e:
            log.error(f"[links] remove_affiliate_links failed: {e}", exc_info=True)

    params = {"since_dttm": last_affiliate_update_dttm}
    affiliate_count = 0
    non_affiliate_count = 0
    try:
        # DESK T-NEW-055: was ``"affiliate/links/"`` (doubled with
        # the ``/api/affiliate`` already in the base). Now just
        # ``"links/"`` — the base + path resolves to
        # ``server_base_url}/api/v1/quicklinks/`` which is the canonical
        # endpoint for fetching affiliate link rows.
        response = client.get("api/v1/quicklinks/", params=params)
        # Normalise the response shape: a list/tuple goes straight
        # through, a dict is unwrapped via "links", and anything else
        # (None when the API is unreachable, an unexpected type)
        # becomes an empty list so the loop is a no-op.
        if isinstance(response, (list, tuple)):
            links = list(response)
        elif isinstance(response, dict):
            links = response.get("links", []) or []
        else:
            links = []
        affiliate_ids = _collect_known_affiliate_ids(model)
        for link in links:
            if not isinstance(link, dict):
                continue
            link_id = link.get("id") or link.get("UUID")
            affiliate_id = link.get("affiliate_id")
            if affiliate_id and affiliate_id in affiliate_ids:
                # Affiliate link - persist to link_affiliate join
                try:
                    if hasattr(model, "_store_link_affiliate"):
                        model._store_link_affiliate(link_id, affiliate_id, link)
                        affiliate_count += 1
                    elif hasattr(model, "update_affiliate_links"):
                        model.update_affiliate_links([link])
                        affiliate_count += 1
                except Exception as e:
                    log.error(f"[links] affiliate insert failed for link {link_id}: {e}", exc_info=True)
            else:
                # Non-affiliate link - persist as a plain link
                try:
                    if hasattr(model, "_store_link"):
                        model._store_link(link)
                        non_affiliate_count += 1
                except Exception as e:
                    log.error(f"[links] link insert failed for {link_id}: {e}", exc_info=True)
    except Exception as e:
        log.error(f"[links] update_affiliate_links API call failed: {e}", exc_info=True)
    log.info(f"[links] update_affiliate_links: {affiliate_count} affiliate + {non_affiliate_count} non-affiliate")
    return {"affiliate_count": affiliate_count, "non_affiliate_count": non_affiliate_count}


def _collect_known_affiliate_ids(model) -> Set[Any]:
    """Return the set of known affiliate ids from ``model``.

    T-070 helper. Reads from ``model.get_affiliate_ids()``
    when available, then ``model.app_affiliate_getter()``,
    then the table ``app_affiliate_registry`` (when the
    store is reachable). Returns an empty set on any
    failure.
    """
    from kahndor.logma import Logma
    log = Logma(__name__)
    try:
        if hasattr(model, "get_affiliate_ids"):
            return set(model.get_affiliate_ids())
    except Exception as e:
        log.error(f"[links] get_affiliate_ids failed: {e}", exc_info=True)
    try:
        store = getattr(model, "store", None)
        if store is not None and hasattr(store, "get_table"):
            df = store.get_table("app_affiliate_registry")
            if df is not None and not getattr(df, "empty", True):
                return set(df.iloc[:, 0].tolist())
    except Exception as e:
        log.error(f"[links] _collect_known_affiliate_ids store read failed: {e}", exc_info=True)
    return set()


class APIClient:
    """A reusable API client class.

    Auth convention (DESK T-NEW-057): the server's
    @require_desktop_api_key decorator reads
    ``request.headers.get("x-api-key")`` and returns 401 when
    the header is missing or named differently. APIClient
    used to set ``Authorization: Bearer <key>`` which is the
    FAB-User convention; the desktop-install API uses a
    different header (``x-api-key``). The two look the same in
    the browser dev tools but the server treats them as
    distinct — this is the standard confusion between
    FAB-User auth and Desktop-Install auth.
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({"User-Agent": "MyApp/1.0", "Accept": "application/json"})

        # Attach the install's api_key as ``x-api-key`` (NOT
        # Authorization: Bearer — that header is for FAB-User
        # auth and the desktop-install endpoint ignores it).
        if api_key:
            self.session.headers["x-api-key"] = api_key

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make a GET request to the API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            # Timeout is informational — the operator may be
            # mid-setup on a docker stack that hasn't deployed
            # the endpoint yet. Demoted from ERROR in T-NEW-056.
            logma.warning("[links] request timed out")
            return None
        except requests.exceptions.HTTPError as e:
            # 4xx/5xx server response — a real problem (server
            # up but endpoint missing or bug). Keep at ERROR so
            # the operator notices it.
            logma.error(f"[links] HTTP error: {e}", exc_info=True)
            return None
        except requests.exceptions.RequestException as e:
            # Network-level failure: DNS, connection refused,
            # connection reset, etc. Demoted from ERROR to
            # WARNING in T-NEW-056: when ``run-mode: dev`` is
            # active and the operator is mid-setup on a docker
            # stack, the affiliate service may not be deployed
            # yet. ERRORS here are noise — the desktop is doing
            # the right thing (catching + logging + moving on
            # with 0 affiliates). HTTPError (above) remains
            # ERROR because that means the server IS reachable
            # but rejected the request, which IS actionable.
            logma.warning(f"[links] request error: {e}")
            return None
        except json.JSONDecodeError:
            # Server reachable but body isn't JSON — likely a
            # proxy/load-balancer returning HTML. ERROR-worthy:
            # the endpoint isn't speaking the expected protocol.
            logma.error("[links] invalid JSON response")
            return None

    def post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a POST request to the API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logma.error(f"[links] request error: {e}", exc_info=True)
            return None


# Example usage of the API client
def example_with_client() -> None:
    """Example using the APIClient class"""

    # Initialize the client
    client = APIClient("https://jsonplaceholder.typicode.com")

    # Get a specific post
    post = client.get("posts/1")
    if post:
        logma.info(f"[links] post title: {post['title']}")

    # Get posts with parameters
    posts = client.get("posts", params={"userId": 1, "_limit": 3})
    if posts:
        logma.info(f"[links] found {len(posts)} posts")

    # Create a new post
    new_post_data = {"title": "My API Test", "body": "Testing the API client", "userId": 1}

    created_post = client.post("posts", new_post_data)
    if created_post:
        logma.info(f"[links] created post with id: {created_post.get('id')}")


# ====================================================================================================================||

# T-DESK: track_quicklink_click helper (DESK-3 / ATNRG spec §1 analytics).
#
# Posts a click event to nchantdoffice_com's /api/affiliate/track/click/<id>
# endpoint whenever a quicklink is opened. Best-effort: never raises so a
# network failure doesn't block the click itself. Designed to be called
# from anywhere a quicklink UI item is invoked (catalog item, browser,
# quickstart pane, etc.).

# DESK T-NEW-052: the constant now mirrors the
# ``urls.server_base_url()`` resolver. The bundled default
# is ``https://nchantdoffice.com`` (which serves the
# quicklinks API at ``/api/v1/quicklinks/``).
from nchantdoffice.utilities.urls import server_base_url as _sbu
DEFAULT_AFFILIATE_API_BASE = _sbu() + "/api/v1"


def track_quicklink_click(offer_id: Optional[int] = None,
                           *,
                           service_slug: Optional[str] = None,
                           session_id: Optional[str] = None,
                           tier: Optional[str] = None,
                           api_base: str = DEFAULT_AFFILIATE_API_BASE,
                           timeout: float = 3.0,
                           user=None) -> bool:
    """POST a quicklink click event to nchantdoffice_com.

    Args:
        offer_id: numeric offer id (preferred). If absent the call still
            goes through with the service_slug — the server resolves it.
        service_slug: stable slug for the affiliate (e.g. "notion").
        session_id: client session id for funnel analysis.
        tier: user tier at click time ("free" / "pro") for segmentation.
        api_base: override for testing (default: production URL).
        timeout: HTTP timeout in seconds (kept small to not block UI).
        user: optional in-app user object. When provided, the upgrade
            prompt logic is fired at the "after 5th quicklink"
            friction point per ATNRG spec §5.

    Returns:
        True if the server accepted the event, False otherwise. Never
        raises — the click must succeed regardless of telemetry state.
    """
    payload: Dict[str, Any] = {}
    if service_slug:
        payload["service_slug"] = service_slug
    if session_id:
        payload["session_id"] = session_id
    if tier:
        payload["tier"] = tier
    if offer_id is not None:
        payload["offer_id"] = offer_id

    # T-DESK: attach the local device_id (ATNRG spec §8 anti-abuse).
    # The server uses this to reject self-referrals where the
    # clicker and the referrer are on the same device.
    try:
        from nchantdoffice.utilities.device_id import get_device_id
        payload["device_id"] = get_device_id()
    except Exception as e:
        logma.warning(f"[links] device_id not available: {e}")

    endpoint = f"track/click/{offer_id}" if offer_id is not None else "track/click"
    url = f"{api_base.rstrip('/')}/{endpoint.lstrip('/')}"
    accepted = False
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        accepted = True
        logma.info(
            f"[links] quicklink click tracked: offer_id={offer_id} "
            f"slug={service_slug} tier={tier}"
        )
    except requests.exceptions.RequestException as e:
        logma.warning(
            f"[links] quicklink click track failed (offer_id={offer_id}): {e}"
        )
    except Exception as e:
        logma.error(
            f"[links] quicklink click track crashed (offer_id={offer_id}): {e}",
            exc_info=True,
        )

    # T-DESK: fire upgrade prompt at "after 5th quicklink" friction
    # point per ATNRG spec §5. Best-effort — never affects the
    # return value of the telemetry call.
    try:
        from nchantdoffice.utilities.upgrades import maybe_prompt_for_upgrade
        maybe_prompt_for_upgrade(user, on_quicklink_click=True)
    except Exception as e:
        logma.warning(f"[links] upgrade-prompt fire failed: {e}")

    return accepted


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
