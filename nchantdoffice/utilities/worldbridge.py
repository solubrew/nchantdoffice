# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name: WorldBridge Utility
    description: >
        Integration module for worldbridgeserver to provide web2 (HTTP) and 
        web3 (blockchain) data access in NchantdOffice
    version: 0.3.0
"""
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import dirname, join
from typing import Optional, Dict, List, Any

# ======================================3rd Party Library Modules=====================================================||
import requests

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from worldbridgeserver.worldbridgeserver import Bridge

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "worldbridge.yaml")


class NchantdOfficeWorldBridge:
    """
    WorldBridge integration for NchantdOffice.
    Provides unified access to web2 (HTTP/API) and web3 (blockchain) data sources.
    """
    
    def __init__(self, cfg: Optional[Dict] = None):
        """Initialize WorldBridge with optional configuration"""
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeWorldBridge").override(cfg or {})
        self.bridge = Bridge(cfg=self.config.dikt if self.config else None)
        self.apikeys = {}
        logma.info("NchantdOfficeWorldBridge initialized")
        
    def load_api_keys(self, keys: Dict[str, str]):
        """Load API keys for external services"""
        self.apikeys = keys
        self.bridge.loadAPIKeys(keys)
        logma.info(f"Loaded {len(keys)} API keys")
        return self
        
    def get_stones(self) -> List[str]:
        """Get list of available data stones"""
        return list(self.bridge.active_stones.keys()) if self.bridge.active_stones else []
    
    def get_active_stone(self, service: str) -> Optional[Dict]:
        """Get active stone configuration for a service"""
        return self.bridge.get_active_stone(service)
    
    # =========================================================================
    # Web2 (HTTP/API) Methods
    # =========================================================================
    
    def fetch_api_data(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Fetch data from a REST API endpoint"""
        try:
            response = requests.get(endpoint, params=params or {})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logma.error(f"API fetch error: {e}")
            return {}
            
    def fetch_webpage(self, url: str, selector: Optional[str] = None) -> str:
        """Fetch webpage content"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            if selector:
                # Would use BeautifulSoup for selector
                pass
            return response.text
        except Exception as e:
            logma.error(f"Webpage fetch error: {e}")
            return ""
            
    # =========================================================================
    # Web3 (Blockchain) Methods - via elv1r4 integration
    # =========================================================================
    
    def get_token_price(self, token_address: str, chain: str = "ethereum") -> Optional[float]:
        """Get token price from DEX/blockchain"""
        # Uses elv1r4 for web3 data
        try:
            # Placeholder - actual implementation would use elv1r4
            logma.info(f"Getting token price for {token_address} on {chain}")
            return None
        except Exception as e:
            logma.error(f"Token price error: {e}")
            return None
            
    def get_nft_metadata(self, contract_address: str, token_id: str, chain: str = "ethereum") -> Optional[Dict]:
        """Get NFT metadata from blockchain"""
        try:
            logma.info(f"Getting NFT metadata for {contract_address}/{token_id}")
            return {}
        except Exception as e:
            logma.error(f"NFT metadata error: {e}")
            return None
            
    def get_wallet_balance(self, wallet_address: str, chain: str = "ethereum") -> Optional[Dict]:
        """Get wallet balance for a given chain"""
        try:
            logma.info(f"Getting wallet balance for {wallet_address} on {chain}")
            return {}
        except Exception as e:
            logma.error(f"Wallet balance error: {e}")
            return None
            
    # =========================================================================
    # Data Integration Methods
    # =========================================================================
    
    def sync_data_source(self, source: str, data: List[Dict]) -> bool:
        """Sync external data source to NchantdOffice store"""
        try:
            logma.info(f"Syncing {len(data)} records from {source}")
            # Would integrate with NchantdOfficeStore
            return True
        except Exception as e:
            logma.error(f"Data sync error: {e}")
            return False
            
    def search_external(self, query: str, sources: Optional[List[str]] = None) -> List[Dict]:
        """Search across external data sources"""
        results = []
        sources = sources or self.get_stones()
        for source in sources:
            logma.info(f"Searching {source} for: {query}")
            # Placeholder - would implement actual search
        return results


# ====================================================================================================================||
# Default instance for easy import
# ====================================================================================================================||

_worldbridge_instance = None

def get_worldbridge(cfg: Optional[Dict] = None) -> NchantdOfficeWorldBridge:
    """Get or create the global WorldBridge instance"""
    global _worldbridge_instance
    if _worldbridge_instance is None:
        _worldbridge_instance = NchantdOfficeWorldBridge(cfg)
    return _worldbridge_instance


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
