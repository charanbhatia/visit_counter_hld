import hashlib
from typing import List, Dict, Tuple, Optional
import redis

class ConsistentHash:
    def __init__(self, nodes: List[str], replicas: int = 100):
        """
        Initialize consistent hash ring
        nodes: List of node identifiers (e.g., ['redis_7070', 'redis_7071'])
        replicas: Number of virtual nodes per real node
        """
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []

        # Add nodes to the ring
        for node in nodes:
            self.add_node(node)

    def add_node(self, node: str) -> None:
        """Add a node to the hash ring"""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            self.sorted_keys.append(key)
        self.sorted_keys.sort()

    def remove_node(self, node: str) -> None:
        """Remove a node from the hash ring"""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)

    def get_node(self, key: str) -> str:
        """Get the node that should store this key"""
        if not self.ring:
            raise Exception("Hash ring is empty")

        hash_key = self._hash(key)
        
        # Find the first point in the ring that comes after hash_key
        for ring_key in self.sorted_keys:
            if ring_key >= hash_key:
                return self.ring[ring_key]
        
        # If we reached the end, return the first node
        return self.ring[self.sorted_keys[0]]

    def _hash(self, key: str) -> int:
        """Generate hash for a key"""
        key_bytes = key.encode('utf-8')
        return int(hashlib.md5(key_bytes).hexdigest(), 16)

class ShardedRedis:
    def __init__(self):
        # Initialize Redis clients
        self.shards: Dict[str, redis.Redis] = {
            'redis_7070': redis.Redis(host='redis_7070', port=6379, decode_responses=True),
            'redis_7071': redis.Redis(host='redis_7071', port=6379, decode_responses=True)
        }
        
        # Initialize consistent hash ring
        self.hash_ring = ConsistentHash(list(self.shards.keys()))

    def get_shard(self, key: str) -> Tuple[redis.Redis, str]:
        """Get the appropriate Redis shard for a key"""
        shard_id = self.hash_ring.get_node(key)
        return self.shards[shard_id], shard_id

    def set(self, key: str, value: str) -> None:
        """Set a value in the appropriate shard"""
        shard, _ = self.get_shard(key)
        shard.set(key, value)

    def get(self, key: str) -> Tuple[Optional[str], str]:
        """Get a value from the appropriate shard"""
        shard, shard_id = self.get_shard(key)
        return shard.get(key), shard_id

    def incr(self, key: str) -> Tuple[int, str]:
        """Increment a value in the appropriate shard"""
        shard, shard_id = self.get_shard(key)
        return shard.incr(key), shard_id