"""
Parallel loading utilities for NchantdOffice performance optimization.

Provides:
- Parallel model loading using ThreadPoolExecutor
- Progress callbacks for UI updates
- Concurrent initialization
"""

import concurrent.futures
import time
import threading
from typing import Callable, Any, Dict, List, Optional
from functools import wraps


# Global thread pool
_executor: Optional[concurrent.futures.ThreadPoolExecutor] = None
_max_workers = 4


def get_executor() -> concurrent.futures.ThreadPoolExecutor:
    """Get or create the global thread pool executor."""
    global _executor
    if _executor is None:
        _executor = concurrent.futures.ThreadPoolExecutor(max_workers=_max_workers)
    return _executor


def shutdown_executor():
    """Shutdown the global executor."""
    global _executor
    if _executor is not None:
        _executor.shutdown(wait=True)
        _executor = None


class ProgressCallback:
    """Thread-safe progress callback for UI updates."""
    
    def __init__(self, callback: Callable = None, total: int = 100):
        self.callback = callback
        self.total = total
        self._current = 0
        self._lock = threading.Lock()
    
    def update(self, increment: int = 1, message: str = ""):
        """Update progress."""
        with self._lock:
            self._current += increment
            if self.callback:
                percentage = (self._current / self.total) * 100 if self.total > 0 else 0
                self.callback(percentage, message)
    
    def set_total(self, total: int):
        """Set total steps."""
        with self._lock:
            self.total = total
    
    @property
    def current(self) -> int:
        return self._current
    
    def reset(self):
        """Reset progress."""
        with self._lock:
            self._current = 0


def parallel_load(items: List[Any], loader: Callable, 
                  max_workers: int = None,
                  progress_callback: Callable = None) -> List[Any]:
    """
    Load items in parallel using ThreadPoolExecutor.
    
    Args:
        items: List of items to load
        loader: Function to load each item
        max_workers: Max number of threads (default: 4)
        progress_callback: Optional callback(completed, total, message)
    
    Returns:
        List of loaded results in same order as input
    """
    if max_workers is None:
        max_workers = _max_workers
    
    results = [None] * len(items)
    
    def load_item(args):
        index, item = args
        result = loader(item)
        return index, result
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(load_item, (i, item)): i 
            for i, item in enumerate(items)
        }
        
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            index = futures[future]
            try:
                result_index, result = future.result()
                results[result_index] = result
            except Exception as e:
                results[index] = e
            
            completed += 1
            if progress_callback:
                progress_callback(completed, len(items), f"Loaded {completed}/{len(items)}")
    
    return results


def parallel_init(items: List[Any], initializer: Callable,
                  max_workers: int = None,
                  progress_callback: Callable = None) -> List[Any]:
    """
    Initialize items in parallel.
    
    Similar to parallel_load but for initialization methods.
    
    Args:
        items: List of items to initialize
        initializer: Function to initialize each item
        max_workers: Max number of threads
        progress_callback: Optional callback
    
    Returns:
        List of initialized results
    """
    if max_workers is None:
        max_workers = _max_workers
    
    results = [None] * len(items)
    
    def init_item(args):
        index, item = args
        result = initializer(item)
        return index, result
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(init_item, (i, item)): i
            for i, item in enumerate(items)
        }
        
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            index = futures[future]
            try:
                result_index, result = future.result()
                results[result_index] = result
            except Exception as e:
                results[index] = e
            
            completed += 1
            if progress_callback:
                progress_callback(completed, len(items))
    
    return results


class ParallelLoader:
    """
    Context manager for parallel loading operations.
    
    Usage:
        with ParallelLoader(max_workers=4) as loader:
            results = loader.load(items, load_func)
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = None
    
    def __enter__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.executor:
            self.executor.shutdown(wait=True)
        return False
    
    def map(self, func: Callable, items: List[Any]) -> List[Any]:
        """Map function over items in parallel."""
        if self.executor is None:
            raise RuntimeError("Context not entered")
        
        results = list(self.executor.map(func, items))
        return results
    
    def submit(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Submit a single task."""
        if self.executor is None:
            raise RuntimeError("Context not entered")
        
        return self.executor.submit(func, *args, **kwargs)


def async_init(func: Callable) -> Callable:
    """
    Decorator to make initialization method run asynchronously.
    
    Usage:
        class MyClass:
            @async_init
            def init_heavy_components(self):
                # This runs in background
                ...
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        executor = get_executor()
        future = executor.submit(func, self, *args, **kwargs)
        
        # Store future for potential later retrieval
        if not hasattr(self, '_async_futures'):
            self._async_futures = []
        self._async_futures.append(future)
        
        return future
    
    return wrapper


def wait_for_async(self) -> List[Any]:
    """Wait for all async initializations to complete."""
    if not hasattr(self, '_async_futures'):
        return []
    
    results = []
    for future in self._async_futures:
        try:
            results.append(future.result())
        except Exception as e:
            results.append(e)
    
    return results


# Performance monitoring
class PerformanceMonitor:
    """Monitor parallel operation performance."""
    
    def __init__(self):
        self._timings: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
    
    def record(self, operation: str, duration: float):
        """Record operation duration."""
        with self._lock:
            if operation not in self._timings:
                self._timings[operation] = []
            self._timings[operation].append(duration)
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        with self._lock:
            timings = self._timings.get(operation, [])
            if not timings:
                return {}
            
            return {
                'count': len(timings),
                'total': sum(timings),
                'avg': sum(timings) / len(timings),
                'min': min(timings),
                'max': max(timings),
            }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all operations."""
        return {op: self.get_stats(op) for op in self._timings.keys()}


# Global monitor instance
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    return _monitor
