import redis
from typing import Tuple
from local_cache import LocalCache
from write_buffer import WriteBuffer

class RedisCache:
    def __init__(self, host: str = "redis", port: int = 6379, db: int = 0):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.local_cache = LocalCache(ttl_seconds=5)
        self.write_buffer = WriteBuffer(self.client, flush_interval=30)

    def increment_count(self, page_id: str) -> int:
        """
        Increment the visit count in write buffer
        Returns the total count (Redis + buffer)
        """
        key = f"page:{page_id}"
        total_count = self.write_buffer.increment(key)
        # Update local cache with new total
        self.local_cache.set(key, total_count)
        return total_count

    def get_count(self, page_id: str) -> Tuple[int, str]:
        """
        Get the current visit count for a specific page
        Returns tuple of (count, source)
        """
        key = f"page:{page_id}"
        
        # Try local cache first
        cached_value = self.local_cache.get(key)
        if cached_value is not None:
            return cached_value, "in_memory"
        
        # On cache miss, flush buffer and get fresh count
        self.write_buffer.flush()  # Immediate flush on read
        
        # Get count from Redis
        redis_count = int(self.client.get(key) or 0)
        
        # Add any new pending counts
        pending_count = self.write_buffer.get_pending_count(key)
        total_count = redis_count + pending_count
        
        # Update local cache
        self.local_cache.set(key, total_count)
        
        return total_count, "batch" if pending_count > 0 else "redis"

    def health_check(self) -> bool:
        """Check if Redis connection is healthy"""
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False