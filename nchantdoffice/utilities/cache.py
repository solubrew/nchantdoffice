"""
Caching utilities for NchantdOffice performance optimization.

Provides memoization decorators and cache classes for:
- Config file caching
- Template caching
- Include resolution caching
"""

import functools
import hashlib
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional, Dict
import yaml
import json

# Global cache storage
_cache_store: Dict[str, Any] = {}
_cache_timestamps: Dict[str, float] = {}
_cache_hits = 0
_cache_misses = 0


def memoize(func: Callable) -> Callable:
    """
    Memoization decorator with optional TTL.
    
    Usage:
        @memoize
        def expensive_function(arg1, arg2):
            ...
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from args/kwargs
        key = str(args) + str(sorted(kwargs.items()))
        key_hash = hashlib.md5(key.encode()).hexdigest()
        
        if key_hash in cache:
            return cache[key_hash]
        
        result = func(*args, **kwargs)
        cache[key_hash] = result
        return result
    
    wrapper.cache = cache
    wrapper.clear_cache = lambda: cache.clear()
    return wrapper


def memoize_with_ttl(ttl_seconds: int = 300):
    """
    Memoization decorator with Time-To-Live support.
    
    Usage:
        @memoize_with_ttl(ttl_seconds=60)
        def cached_api_call():
            ...
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        timestamps = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            key_hash = hashlib.md5(key.encode()).hexdigest()
            
            current_time = time.time()
            
            # Check if cached and not expired
            if key_hash in cache:
                if current_time - timestamps[key_hash] < ttl_seconds:
                    return cache[key_hash]
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache[key_hash] = result
            timestamps[key_hash] = current_time
            return result
        
        wrapper.cache = cache
        wrapper.clear_cache = lambda: (cache.clear(), timestamps.clear())
        return wrapper
    return decorator


class ConfigCache:
    """
    Cached configuration file loader.
    
    Prevents repeated YAML/JSON parsing of config files.
    """
    
    _config_cache: Dict[str, tuple[Any, float]] = {}
    _cache_dir = Path.home() / ".orin" / "nchantdoffice" / "cache"
    
    @classmethod
    def get(cls, config_path: str, ttl: int = 60) -> Any:
        """
        Get cached config or load and cache it.
        
        Args:
            config_path: Path to config file
            ttl: Time-to-live in seconds
            
        Returns:
            Parsed config data
        """
        abs_path = os.path.abspath(config_path)
        current_mtime = os.path.getmtime(abs_path)
        
        if abs_path in cls._config_cache:
            cached_data, cached_mtime = cls._config_cache[abs_path]
            
            # Check if file was modified
            if current_mtime == cached_mtime:
                return cached_data
        
        # Load and cache
        with open(abs_path, 'r') as f:
            if abs_path.endswith('.yaml') or abs_path.endswith('.yml'):
                data = yaml.safe_load(f)
            elif abs_path.endswith('.json'):
                data = json.load(f)
            else:
                data = f.read()
        
        cls._config_cache[abs_path] = (data, current_mtime)
        return data
    
    @classmethod
    def invalidate(cls, config_path: str = None):
        """Invalidate cache for specific path or all configs."""
        if config_path:
            abs_path = os.path.abspath(config_path)
            cls._config_cache.pop(abs_path, None)
        else:
            cls._config_cache.clear()
    
    @classmethod
    def clear_all(cls):
        """Clear all cached configs."""
        cls._config_cache.clear()


class TemplateCache:
    """
    Cached template loader.
    
    Prevents repeated template parsing.
    """
    
    _template_cache: Dict[str, tuple[str, float]] = {}
    
    @classmethod
    def get(cls, template_path: str, ttl: int = 300) -> str:
        """
        Get cached template or load and cache it.
        
        Args:
            template_path: Path to template file
            ttl: Time-to-live in seconds
            
        Returns:
            Template content string
        """
        abs_path = os.path.abspath(template_path)
        current_mtime = os.path.getmtime(abs_path)
        
        if abs_path in cls._template_cache:
            cached_content, cached_mtime = cls._template_cache[abs_path]
            
            if current_mtime == cached_mtime:
                return cached_content
        
        # Load and cache
        with open(abs_path, 'r') as f:
            content = f.read()
        
        cls._template_cache[abs_path] = (content, current_mtime)
        return content
    
    @classmethod
    def invalidate(cls, template_path: str = None):
        """Invalidate cache for specific template or all templates."""
        if template_path:
            abs_path = os.path.abspath(template_path)
            cls._template_cache.pop(abs_path, None)
        else:
            cls._template_cache.clear()


class IncludeResolver:
    """
    Cached include resolution for template includes.
    
    Resolves {{ include("path") }} statements with caching.
    """
    
    _include_cache: Dict[str, str] = {}
    
    @classmethod
    def resolve(cls, include_path: str, base_dir: str = None) -> str:
        """
        Resolve an include path with caching.
        
        Args:
            include_path: Path to include
            base_dir: Base directory for resolution
            
        Returns:
            Included file content
        """
        abs_path = os.path.abspath(
            os.path.join(base_dir or '.', include_path)
        )
        
        if abs_path in cls._include_cache:
            return cls._include_cache[abs_path]
        
        # Load and cache
        with open(abs_path, 'r') as f:
            content = f.read()
        
        cls._include_cache[abs_path] = content
        return content
    
    @classmethod
    def clear(cls):
        """Clear include cache."""
        cls._include_cache.clear()


def lazy_property(func: Callable) -> property:
    """
    Decorator for lazy-loaded properties.
    
    Property is only computed on first access.
    
    Usage:
        class MyClass:
            @lazy_property
            def expensive_data(self):
                return self._compute_expensive_data()
    """
    attr_name = '_lazy_' + func.__name__
    
    @property
    @functools.wraps(func)
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)
    
    return wrapper


class LRUCache:
    """
    Least Recently Used (LRU) cache implementation.
    
    Useful for caching with limited memory.
    """
    
    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._access_order: list = []
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get item from cache."""
        if key in self._cache:
            # Move to end (most recently used)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key][0]
        return default
    
    def set(self, key: str, value: Any):
        """Set item in cache."""
        if key in self._cache:
            self._access_order.remove(key)
        elif len(self._cache) >= self.max_size:
            # Remove least recently used
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]
        
        self._cache[key] = (value, time.time())
        self._access_order.append(key)
    
    def clear(self):
        """Clear all cached items."""
        self._cache.clear()
        self._access_order.clear()
    
    def __len__(self):
        return len(self._cache)
    
    def __contains__(self, key: str):
        return key in self._cache


# Global cache statistics
def get_cache_stats() -> Dict[str, Any]:
    """Get cache performance statistics."""
    return {
        "config_entries": len(ConfigCache._config_cache),
        "template_entries": len(TemplateCache._template_cache),
        "include_entries": len(IncludeResolver._include_cache),
    }


def clear_all_caches():
    """Clear all caches - useful for testing or memory management."""
    ConfigCache.clear_all()
    TemplateCache.clear_all()
    IncludeResolver.clear()
    _cache_store.clear()
    _cache_timestamps.clear()
