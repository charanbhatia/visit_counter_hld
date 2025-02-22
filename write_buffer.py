import threading
import time
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WriteBuffer:
    def __init__(self, redis_client, flush_interval: int = 30):
        self.buffer: Dict[str, int] = {}
        self.redis_client = redis_client
        self.flush_interval = flush_interval
        self.lock = threading.Lock()
        
        # Start background flush thread
        self.flush_thread = threading.Thread(target=self._periodic_flush, daemon=True)
        self.flush_thread.start()
    
    def increment(self, key: str) -> int:
        """Increment count in buffer"""
        with self.lock:
            self.buffer[key] = self.buffer.get(key, 0) + 1
            return self._get_total_count(key)
    
    def get_pending_count(self, key: str) -> int:
        """Get pending (non-flushed) count for a key"""
        with self.lock:
            return self.buffer.get(key, 0)
    
    def _get_total_count(self, key: str) -> int:
        """Get total count (Redis + buffer)"""
        redis_count = int(self.redis_client.get(key) or 0)
        return redis_count + self.buffer.get(key, 0)
    
    def flush(self) -> None:
        """Flush all pending writes to Redis"""
        with self.lock:
            if not self.buffer:
                return
            
            # Use Redis pipeline for atomic updates
            pipeline = self.redis_client.pipeline()
            for key, count in self.buffer.items():
                pipeline.incrby(key, count)
            pipeline.execute()
            
            logger.info(f"Flushed {len(self.buffer)} keys to Redis")
            self.buffer.clear()
    
    def _periodic_flush(self) -> None:
        """Background thread that periodically flushes buffer"""
        while True:
            time.sleep(self.flush_interval)
            try:
                self.flush()
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")