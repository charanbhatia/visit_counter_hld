from typing import Tuple
from local_cache import LocalCache
from write_buffer import WriteBuffer
from consistent_hash import ShardedRedis

class RedisCache:
    def __init__(self):
        self.sharded_redis = ShardedRedis()
        self.local_cache = LocalCache(ttl_seconds=5)
        self.write_buffer = WriteBuffer(self.sharded_redis, flush_interval=30)

    def increment_count(self, page_id: str) -> Tuple[int, str]:
        """
        Increment the visit count in write buffer
        Returns tuple of (count, shard_id)
        """
        key = f"page:{page_id}"
        total_count, shard_id = self.write_buffer.increment(key)
        # Update local cache with new total
        self.local_cache.set(key, total_count)
        return total_count, shard_id

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
        self.write_buffer.flush()
        
        # Get count from appropriate shard
        count, shard_id = self.sharded_redis.get(key)
        count = int(count or 0)
        
        # Add any new pending counts
        pending_count = self.write_buffer.get_pending_count(key)
        total_count = count + pending_count
        
        # Update local cache
        self.local_cache.set(key, total_count)
        
        if pending_count > 0:
            return total_count, "batch"
        return total_count, shard_id

    def health_check(self) -> dict:
        """Check health of all Redis shards"""
        status = {}
        for shard_id, client in self.sharded_redis.shards.items():
            try:
                status[shard_id] = client.ping()
            except Exception:
                status[shard_id] = False
        return status