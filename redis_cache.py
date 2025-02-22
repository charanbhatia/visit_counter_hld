import redis
from typing import Optional, Tuple
from local_cache import LocalCache

class RedisCache:
    def __init__(self, host: str = "redis", port: int = 6379, db: int = 0):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.local_cache = LocalCache(ttl_seconds=5)

    def increment_count(self, page_id: str) -> int:
        """Increment the visit count for a specific page"""
        key = f"page:{page_id}"
        count = self.client.incr(key)
        # Update local cache with new value
        self.local_cache.set(key, count)
        return count

    def get_count(self, page_id: str) -> Tuple[int, str]:
        """Get the current visit count for a specific page"""
        key = f"page:{page_id}"
        
        # Try local cache first
        cached_value = self.local_cache.get(key)
        if cached_value is not None:
            return cached_value, "in_memory"
        
        # On cache miss, get from Redis
        count = self.client.get(key)
        value = int(count) if count else 0
        
        # Update local cache
        self.local_cache.set(key, value)
        return value, "redis"

    def health_check(self) -> bool:
        """Check if Redis connection is healthy"""
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False