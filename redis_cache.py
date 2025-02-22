import redis
from typing import Optional

class RedisCache:
    def __init__(self, host: str = "redis", port: int = 6379, db: int = 0):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True  # Automatically decode responses to strings
        )

    def increment_count(self, page_id: str) -> int:
        """
        Increment the visit count for a specific page
        Returns the new count
        """
        key = f"page:{page_id}"
        return self.client.incr(key)

    def get_count(self, page_id: str) -> int:
        """
        Get the current visit count for a specific page
        Returns 0 if the page hasn't been visited
        """
        key = f"page:{page_id}"
        count = self.client.get(key)
        return int(count) if count else 0

    def health_check(self) -> bool:
        """
        Check if Redis connection is healthy
        """
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False