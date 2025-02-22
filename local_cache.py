from datetime import datetime, timedelta
from typing import Dict, Optional, Any

class LocalCache:
    def __init__(self, ttl_seconds: int = 5):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds

    def set(self, key: str, value: int) -> None:
        """Set a value in the cache with expiration time"""
        self.cache[key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=self.ttl_seconds)
        }

    def get(self, key: str) -> Optional[int]:
        """Get a value from the cache if it exists and hasn't expired"""
        if key in self.cache:
            cache_entry = self.cache[key]
            if cache_entry['expires_at'] > datetime.now():
                return cache_entry['value']
            # Clean up expired entry
            del self.cache[key]
        return None

    def clear(self) -> None:
        """Clear all entries from the cache"""
        self.cache.clear()