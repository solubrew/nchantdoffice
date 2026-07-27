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
from typing import Optional, Dict, Any
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


def update_affilate_links(model, last_affilate_update_dttm: str = "2025-01-01 00:00:00", reload=False):
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
    API_URL = "https://nchantdoffice.com/api/affiliate/links/"
    client = APIClient(API_URL)
    if reload:
        last_affilate_update_dttm = "2025-01-01 00:00:00"
        try:
            model.remove_affilate_links()
        except Exception as e:
            log.error(f"[links] remove_affilate_links failed: {e}", exc_info=True)

    params = {"since_dttm": last_affilate_update_dttm}
    affiliate_count = 0
    non_affiliate_count = 0
    try:
        response = client.get("affiliate/links/", params=params)
        links = response if isinstance(response, (list, tuple)) else response.get("links", [])
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
                    elif hasattr(model, "update_affilate_links"):
                        model.update_affilate_links([link])
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
        log.error(f"[links] update_affilate_links API call failed: {e}", exc_info=True)
    log.info(f"[links] update_affilate_links: {affiliate_count} affiliate + {non_affiliate_count} non-affiliate")
    return {"affiliate_count": affiliate_count, "non_affiliate_count": non_affiliate_count}


def _collect_known_affiliate_ids(model):
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
    """A reusable API client class"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({"User-Agent": "MyApp/1.0", "Accept": "application/json"})

        # Add API key if provided
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make a GET request to the API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logma.warning("[links] request timed out")
            return None
        except requests.exceptions.HTTPError as e:
            logma.error(f"[links] HTTP error: {e}", exc_info=True)
            return None
        except requests.exceptions.RequestException as e:
            logma.error(f"[links] request error: {e}", exc_info=True)
            return None
        except json.JSONDecodeError:
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
def example_with_client():
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

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
