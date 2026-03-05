# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name: APIG Utility
    description: >
        Integration module for apig (API interface) to provide HTTP client
        capabilities in NchantdOffice
    version: 0.3.0
"""
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import dirname, join
from typing import Optional, Dict, List, Any, Callable
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "apig.yaml")


class APIClient:
    """
    APIG integration for NchantdOffice.
    Provides robust HTTP client with retry logic, caching, and rate limiting.
    """
    
    def __init__(self, base_url: Optional[str] = None, cfg: Optional[Dict] = None):
        """Initialize APIClient"""
        self.config = condor.Instruct(pxcfg).select("APIClient").override(cfg or {})
        self.base_url = base_url or ""
        self.session = self._create_session()
        self.cache = {}
        self.rate_limit_delay = self.config.dikt.get("rate_limit_delay", 1.0)
        logma.info(f"APIClient initialized with base_url: {self.base_url}")
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic"""
        session = requests.Session()
        retry_config = self.config.dikt.get("retry", {})
        retries = retry_config.get("max_retries", 3)
        backoff = retry_config.get("backoff_factor", 0.5)
        
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
        
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if endpoint.startswith("http"):
            return endpoint
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
    def get(self, endpoint: str, params: Optional[Dict] = None, 
            headers: Optional[Dict] = None, use_cache: bool = True) -> Optional[Dict]:
        """GET request with optional caching"""
        url = self._build_url(endpoint)
        cache_key = f"GET:{url}:{params}"
        
        if use_cache and cache_key in self.cache:
            logma.info(f"Cache hit for {url}")
            return self.cache[cache_key]
            
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if use_cache:
                self.cache[cache_key] = data
                
            logma.info(f"GET {url} - Status: {response.status_code}")
            return data
        except Exception as e:
            logma.error(f"GET error ({url}): {e}")
            return None
            
    def post(self, endpoint: str, data: Optional[Dict] = None,
             json: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Dict]:
        """POST request"""
        url = self._build_url(endpoint)
        
        try:
            response = self.session.post(url, data=data, json=json, headers=headers, timeout=30)
            response.raise_for_status()
            logma.info(f"POST {url} - Status: {response.status_code}")
            return response.json() if response.content else {}
        except Exception as e:
            logma.error(f"POST error ({url}): {e}")
            return None
            
    def put(self, endpoint: str, data: Optional[Dict] = None,
            json: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Dict]:
        """PUT request"""
        url = self._build_url(endpoint)
        
        try:
            response = self.session.put(url, data=data, json=json, headers=headers, timeout=30)
            response.raise_for_status()
            logma.info(f"PUT {url} - Status: {response.status_code}")
            return response.json() if response.content else {}
        except Exception as e:
            logma.error(f"PUT error ({url}): {e}")
            return None
            
    def delete(self, endpoint: str, headers: Optional[Dict] = None) -> bool:
        """DELETE request"""
        url = self._build_url(endpoint)
        
        try:
            response = self.session.delete(url, headers=headers, timeout=30)
            response.raise_for_status()
            logma.info(f"DELETE {url} - Status: {response.status_code}")
            return True
        except Exception as e:
            logma.error(f"DELETE error ({url}): {e}")
            return False
            
    def set_auth(self, auth: Callable[[requests.Request], requests.Request]):
        """Set authentication handler"""
        self.session.auth = auth
        return self
        
    def set_header(self, key: str, value: str):
        """Set default header"""
        self.session.headers.update({key: value})
        return self
        
    def clear_cache(self):
        """Clear the response cache"""
        self.cache.clear()
        logma.info("API cache cleared")
        return self


# ====================================================================================================================||
# Default instances for easy import
# ====================================================================================================================||

_apiclient_instance = None

def get_apiclient(base_url: Optional[str] = None, cfg: Optional[Dict] = None) -> APIClient:
    """Get or create the global APIClient instance"""
    global _apiclient_instance
    if _apiclient_instance is None:
        _apiclient_instance = APIClient(base_url, cfg)
    return _apiclient_instance


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
