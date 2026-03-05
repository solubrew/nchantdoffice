# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name: NchantdAgent Sentinel
    description: >
        Monitoring and health check system for NchantdOffice
    version: 0.3.0
"""
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
import time
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Dict, List, Optional

# ======================================3rd Party Library Modules=====================================================||

# ====================================================================================================================||


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheck:
    """Base health check implementation"""
    
    def __init__(self, name: str, check_func: Callable, interval: int = 60):
        """
        Initialize health check.
        
        Args:
            name: Name of the health check
            check_func: Function that returns (status, message)
            interval: Check interval in seconds
        """
        self.name = name
        self.check_func = check_func
        self.interval = interval
        self.last_check = None
        self.last_status = HealthStatus.UNKNOWN
        self.last_message = ""
        
    def run(self) -> tuple:
        """Run the health check"""
        try:
            status, message = self.check_func()
            self.last_status = status
            self.last_message = message
        except Exception as e:
            self.last_status = HealthStatus.UNHEALTHY
            self.last_message = str(e)
        finally:
            self.last_check = datetime.now()
            
        return self.last_status, self.last_message
    
    def is_healthy(self) -> bool:
        """Check if last result was healthy"""
        return self.last_status == HealthStatus.HEALTHY


class HealthMonitor:
    """
    System health monitoring for NchantdOffice/NchantdAgent.
    Provides periodic health checks and alerts.
    """
    
    def __init__(self):
        self.checks: Dict[str, HealthCheck] = {}
        self._monitor_thread = None
        self._running = False
        self._alerts: List[dict] = []
        
    def register_check(self, name: str, check_func: Callable, interval: int = 60):
        """
        Register a health check.
        
        Args:
            name: Check name
            check_func: Function returning (HealthStatus, message)
            interval: Check interval in seconds
        """
        self.checks[name] = HealthCheck(name, check_func, interval)
        
    def unregister_check(self, name: str):
        """Remove a health check"""
        if name in self.checks:
            del self.checks[name]
            
    def check_health(self) -> Dict[str, dict]:
        """
        Run all health checks.
        
        Returns:
            Dictionary of check results
        """
        results = {}
        for name, check in self.checks.items():
            status, message = check.run()
            results[name] = {
                "status": status.value,
                "message": message,
                "last_check": check.last_check.isoformat() if check.last_check else None
            }
        return results
    
    def get_status(self) -> HealthStatus:
        """
        Get overall system health status.
        
        Returns:
            Overall health status
        """
        if not self.checks:
            return HealthStatus.UNKNOWN
            
        statuses = [check.last_status for check in self.checks.values()]
        
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNKNOWN
            
    def start_monitoring(self):
        """Start background health monitoring"""
        if self._running:
            return
            
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop background health monitoring"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self._running:
            results = self.check_health()
            
            # Check for unhealthy states and add alerts
            for name, result in results.items():
                if result["status"] == HealthStatus.UNHEALTHY.value:
                    self._alerts.append({
                        "type": "health_check",
                        "check": name,
                        "message": result["message"],
                        "timestamp": datetime.now().isoformat()
                    })
                    
            # Sleep until next check
            time.sleep(10)  # Check every 10 seconds
            
    def get_alerts(self, since: Optional[datetime] = None) -> List[dict]:
        """
        Get alerts.
        
        Args:
            since: Only return alerts after this time
            
        Returns:
            List of alerts
        """
        if since is None:
            return self._alerts
            
        return [a for a in self._alerts if datetime.fromisoformat(a["timestamp"]) > since]
        
    def clear_alerts(self):
        """Clear all alerts"""
        self._alerts.clear()


# ====================================================================================================================||
# Default health checks
# ====================================================================================================================||

def create_default_health_checks(store) -> Dict[str, Callable]:
    """
    Create default health checks for NchantdStore.
    
    Args:
        store: NchantdStore instance
        
    Returns:
        Dictionary of health check functions
    """
    
    def check_database():
        """Check database connectivity"""
        try:
            # Simple query to check database
            if hasattr(store, 'docs') and 'db' in store.docs:
                return HealthStatus.HEALTHY, "Database connected"
            return HealthStatus.UNHEALTHY, "Database not available"
        except Exception as e:
            return HealthStatus.UNKNOWN, str(e)
            
    def check_store():
        """Check store is operational"""
        try:
            if hasattr(store, 'name'):
                return HealthStatus.HEALTHY, f"Store operational: {store.name}"
            return HealthStatus.UNHEALTHY, "Store not initialized"
        except Exception as e:
            return HealthStatus.UNKNOWN, str(e)
    
    return {
        "database": check_database,
        "store": check_store
    }


# ====================================================================================================================||
