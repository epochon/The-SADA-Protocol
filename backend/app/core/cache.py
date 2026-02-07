"""
Simple In-Memory Cache for API Responses
Reduces redundant external API calls for repeated ticker lookups
"""

import time
from typing import Any, Optional, Dict
from functools import wraps
from threading import Lock


class SimpleCache:
    """
    Thread-safe in-memory cache with TTL support.
    Used for caching yfinance and other external API responses.
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self._cache: Dict[str, tuple[Any, float]] = {}  # key -> (value, expiry_time)
        self._lock = Lock()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if exists and not expired."""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    self._hits += 1
                    return value
                else:
                    # Expired, remove it
                    del self._cache[key]
            self._misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional custom TTL."""
        with self._lock:
            # Evict oldest entries if cache is full
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
                del self._cache[oldest_key]
            
            expiry = time.time() + (ttl or self.ttl_seconds)
            self._cache[key] = (value, expiry)
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            return {
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self._hits / total if total > 0 else 0,
                "size": len(self._cache),
                "max_size": self.max_size
            }


# Global cache instances
ticker_cache = SimpleCache(max_size=100, ttl_seconds=300)  # 5 min cache for ticker data
transcript_cache = SimpleCache(max_size=50, ttl_seconds=3600)  # 1 hour cache for transcripts


def cached(cache: SimpleCache, key_func=None):
    """
    Decorator for caching function results.
    
    Usage:
        @cached(ticker_cache, key_func=lambda ticker, *args: ticker)
        def get_ticker_data(ticker: str) -> dict:
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = str(key_func(*args, **kwargs))
            else:
                cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        return wrapper
    return decorator
