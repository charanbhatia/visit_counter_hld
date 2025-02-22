import threading
import time
from typing import Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WriteBuffer:
    def __init__(self, sharded_redis, flush_interval: int = 30):
        self.buffer: Dict[str, int] = {}
        self.sharded_redis = sharded_redis
        self.flush_interval = flush_interval
        self.lock = threading.Lock()
        
        # Start background flush thread
        self.flush_thread = threading.Thread(target=self._periodic_flush, daemon=True)
        self.flush_thread.start()
    
    def increment(self, key: str) -> Tuple[int, str]:
        """Increment count in buffer"""
        with self.lock:
            self.buffer[key] = self.buffer.get(key, 0) + 1
            return self._get_total_count(key)
    
    def get_pending_count(self, key: str) -> int:
        """Get pending (non-flushed) count for a key"""
        with self.lock:
            return self.buffer.get(key, 0)
    
    def _get_total_count(self, key: str) -> Tuple[int, str]:
        """Get total count (Redis + buffer)"""
        value, shard_id = self.sharded_redis.get(key)
        redis_count = int(value or 0)
        return redis_count + self.buffer.get(key, 0), shard_id
    
    def flush(self) -> None:
        """Flush all pending writes to appropriate Redis shards"""
        with self.lock:
            if not self.buffer:
                return
            
            # Group writes by shard
            shard_writes: Dict[str, Dict[str, int]] = {}
            for key, count in self.buffer.items():
                _, shard_id = self.sharded_redis.get_shard(key)
                if shard_id not in shard_writes:
                    shard_writes[shard_id] = {}
                shard_writes[shard_id][key] = count
            
            # Execute writes for each shard
            for shard_id, writes in shard_writes.items():
                shard = self.sharded_redis.shards[shard_id]
                pipeline = shard.pipeline()
                for key, count in writes.items():
                    pipeline.incrby(key, count)
                try:
                    pipeline.execute()
                    logger.info(f"Flushed {len(writes)} keys to {shard_id}")
                except Exception as e:
                    logger.error(f"Error flushing to {shard_id}: {e}")
            
            self.buffer.clear()
    
    def _periodic_flush(self) -> None:
        """Background thread that periodically flushes buffer"""
        while True:
            time.sleep(self.flush_interval)
            try:
                self.flush()
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")