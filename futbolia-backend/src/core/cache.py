"""
LLM Response Caching Service
In-memory cache for LLM predictions and player generation with TTL
"""
import asyncio
import time
from typing import Optional, Dict, Any
import hashlib
import json


class CacheEntry:
    """Single cache entry with TTL"""
    def __init__(self, value: Any, ttl: int = 3600):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl  # Time to live in seconds
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return time.time() - self.created_at > self.ttl
    
    def get(self) -> Optional[Any]:
        """Get value if not expired"""
        if self.is_expired():
            return None
        return self.value


class LLMCache:
    """Thread-safe LLM response cache with TTL"""
    
    # Cache storage
    _cache: Dict[str, CacheEntry] = {}
    _lock = asyncio.Lock()
    
    # Configuration
    PREDICTION_CACHE_TTL = 7200  # 2 hours for match predictions
    PLAYER_GENERATION_CACHE_TTL = 86400  # 24 hours for player generation
    CLEANUP_INTERVAL = 3600  # Cleanup expired entries every hour
    _last_cleanup = time.time()
    
    @classmethod
    def _generate_key(cls, namespace: str, **kwargs) -> str:
        """Generate a unique cache key from parameters"""
        # Sort by key to ensure consistent hashing
        sorted_items = sorted(kwargs.items())
        key_string = f"{namespace}:" + ":".join(f"{k}={v}" for k, v in sorted_items)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @classmethod
    async def get_prediction(cls, home_team: str, away_team: str, language: str = "es") -> Optional[dict]:
        """Get cached match prediction"""
        key = cls._generate_key("prediction", home_team=home_team, away_team=away_team, language=language)
        
        async with cls._lock:
            entry = cls._cache.get(key)
            if entry:
                value = entry.get()
                if value is not None:
                    print(f"✅ Cache hit: prediction {home_team} vs {away_team}")
                    return value
                else:
                    # Remove expired entry
                    del cls._cache[key]
        
        return None
    
    @classmethod
    async def set_prediction(cls, home_team: str, away_team: str, prediction: dict, language: str = "es") -> None:
        """Cache a match prediction"""
        key = cls._generate_key("prediction", home_team=home_team, away_team=away_team, language=language)
        
        async with cls._lock:
            cls._cache[key] = CacheEntry(prediction, ttl=cls.PREDICTION_CACHE_TTL)
            print(f"📝 Cached prediction: {home_team} vs {away_team}")
    
    @classmethod
    async def get_players(cls, team_name: str) -> Optional[list]:
        """Get cached generated players"""
        key = cls._generate_key("players", team_name=team_name)
        
        async with cls._lock:
            entry = cls._cache.get(key)
            if entry:
                value = entry.get()
                if value is not None:
                    print(f"✅ Cache hit: players {team_name}")
                    return value
                else:
                    # Remove expired entry
                    del cls._cache[key]
        
        return None
    
    @classmethod
    async def set_players(cls, team_name: str, players: list) -> None:
        """Cache generated players"""
        key = cls._generate_key("players", team_name=team_name)
        
        async with cls._lock:
            cls._cache[key] = CacheEntry(players, ttl=cls.PLAYER_GENERATION_CACHE_TTL)
            print(f"📝 Cached players: {team_name}")
    
    @classmethod
    async def cleanup_expired(cls) -> None:
        """Remove all expired entries"""
        now = time.time()
        if now - cls._last_cleanup < cls.CLEANUP_INTERVAL:
            return
        
        async with cls._lock:
            # Create list of expired keys
            expired_keys = [
                key for key, entry in cls._cache.items() 
                if entry.is_expired()
            ]
            
            # Remove expired entries
            for key in expired_keys:
                del cls._cache[key]
            
            if expired_keys:
                print(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
            
            cls._last_cleanup = now
    
    @classmethod
    async def clear_all(cls) -> None:
        """Clear entire cache"""
        async with cls._lock:
            cls._cache.clear()
        print("🗑️ Cache cleared")
    
    @classmethod
    async def get_stats(cls) -> dict:
        """Get cache statistics"""
        async with cls._lock:
            total_entries = len(cls._cache)
            expired_entries = sum(1 for entry in cls._cache.values() if entry.is_expired())
            valid_entries = total_entries - expired_entries
        
        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": expired_entries
        }
