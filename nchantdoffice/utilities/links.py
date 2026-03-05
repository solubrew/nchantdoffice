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

import os

# ======================================3rd Party Library Modules=====================================================||
import requests
from typing import Optional, Dict, Any
import time

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# Configurable API URL from environment or default
API_URL = os.environ.get("NCHANTDOFFICE_API_URL", "https://nchantdoffice.com/api/affiliate/")

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")
pxcfg = {}


def update_affilate_links(model, last_affilate_update_dttm: str = "2025-01-01 00:00:00", reload=False):
    """
    TODO: get link table where connection to the link_affiliate table
            SPLIT into affiliate links and non-affilate links
            create a link_affiliate entry for each non-affilate link
            where the affiliate exists
    :return:
    """
    # Use configurable API_URL from environment
    client = APIClient(API_URL)
    if reload:
        last_affilate_update_dttm = "2025-01-01 00:00:00"
        model.remove_affilate_links()
    params = {"since_dttm": last_affilate_update_dttm}
    model.update_affilate_links(client.get(f"affiliate/links/", params=params))
    return


class APIClient:
    """A reusable API client class with caching"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self._cache = {}  # Simple in-memory cache

        # Set default headers
        self.session.headers.update({"User-Agent": "MyApp/1.0", "Accept": "application/json"})

        # Add API key if provided
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"

    @lru_cache(maxsize=64)
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make a GET request to the API with caching"""
        # Create cache key from endpoint and params
        cache_key = f"{endpoint}:{str(params)}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            self._cache[cache_key] = result
            return result

        except requests.exceptions.Timeout:
            print("Request timed out")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except json.JSONDecodeError:
            print("Invalid JSON response")
            return None

    def clear_cache(self):
        """Clear the API response cache"""
        self._cache.clear()

    def post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a POST request to the API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None


# Example usage of the API client
def example_with_client():
    """Example using the APIClient class"""

    # Initialize the client
    client = APIClient("https://jsonplaceholder.typicode.com")

    # Get a specific post
    post = client.get("posts/1")
    if post:
        print(f"Post title: {post['title']}")

    # Get posts with parameters
    posts = client.get("posts", params={"userId": 1, "_limit": 3})
    if posts:
        print(f"Found {len(posts)} posts")

    # Create a new post
    new_post_data = {"title": "My API Test", "body": "Testing the API client", "userId": 1}

    created_post = client.post("posts", new_post_data)
    if created_post:
        print(f"Created post with ID: {created_post.get('id')}")


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
