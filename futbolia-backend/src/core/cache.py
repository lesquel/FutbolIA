"""
FutbolIA - Advanced Caching System
Implements TTL-based caching for API responses and expensive operations
"""
import time
from typing import Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
import asyncio


class CacheEntry:
    """Represents a cached value with expiration time"""
    
    def __init__(self, value: Any, ttl_seconds: int = 3600):
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return time.time() - self.created_at > self.ttl_seconds
    
    def get_age(self) -> float:
        """Get age of cache entry in seconds"""
        return time.time() - self.created_at


class TTLCache:
    """
    Thread-safe TTL cache implementation
    
    Features:
    - Automatic expiration based on TTL
    - Size limits to prevent memory issues
    - Background cleanup of expired entries
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                return None
            
            if entry.is_expired():
                del self._cache[key]
                return None
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional custom TTL"""
        async with self._lock:
            # Remove oldest entries if at max size
            if len(self._cache) >= self.max_size:
                await self._cleanup_expired()
                
                # If still at max, remove oldest
                if len(self._cache) >= self.max_size:
                    oldest_key = min(
                        self._cache.keys(),
                        key=lambda k: self._cache[k].created_at
                    )
                    del self._cache[oldest_key]
            
            ttl_to_use = ttl if ttl is not None else self.default_ttl
            self._cache[key] = CacheEntry(value, ttl_to_use)
    
    async def delete(self, key: str) -> None:
        """Delete a key from cache"""
        async with self._lock:
            self._cache.pop(key, None)
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
    
    async def _cleanup_expired(self) -> None:
        """Remove all expired entries"""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
    
    async def get_or_set(
        self,
        key: str,
        fetch_func: Callable,
        ttl: Optional[int] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Get value from cache or fetch and cache it
        
        Usage:
            value = await cache.get_or_set(
                "team:123",
                fetch_team_data,
                ttl=7200,
                team_id=123
            )
        """
        value = await self.get(key)
        if value is not None:
            return value
        
        # Fetch new value
        if asyncio.iscoroutinefunction(fetch_func):
            value = await fetch_func(*args, **kwargs)
        else:
            value = fetch_func(*args, **kwargs)
        
        if value is not None:
            await self.set(key, value, ttl)
        
        return value
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns comprehensive cache statistics including:
        - Current size and max size
        - Default TTL
        - Details for each cache entry (age, TTL, expiration time)
        """
        async with self._lock:
            await self._cleanup_expired()
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "default_ttl": self.default_ttl,
                "entries": {
                    key: {
                        "age_seconds": entry.get_age(),
                        "ttl_seconds": entry.ttl_seconds,
                        "expires_in": entry.ttl_seconds - entry.get_age(),
                    }
                    for key, entry in self._cache.items()
                }
            }
    
    def get_stats_sync(self) -> Dict[str, Any]:
        """
        Get basic cache statistics synchronously (without cleanup)
        
        Use this only when async context is not available.
        For full stats with cleanup, use get_stats() instead.
        """
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "default_ttl": self.default_ttl,
        }


# Global cache instances for different data types
api_cache = TTLCache(max_size=500, default_ttl=3600)  # 1 hour for API responses
team_cache = TTLCache(max_size=200, default_ttl=7200)  # 2 hours for team data
squad_cache = TTLCache(max_size=300, default_ttl=1800)  # 30 min for squad data
prediction_cache = TTLCache(max_size=100, default_ttl=300)  # 5 min for predictions


def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Usage:
        @cached(ttl=7200, key_prefix="team")
        async def get_team(team_id: int):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            value = await api_cache.get(cache_key)
            if value is not None:
                return value
            
            # Call function and cache result
            if asyncio.iscoroutinefunction(func):
                value = await func(*args, **kwargs)
            else:
                value = func(*args, **kwargs)
            
            if value is not None:
                await api_cache.set(cache_key, value, ttl)
            
            return value
        
        return wrapper
    return decorator

