import json
import redis
from typing import Any, Optional
from app.config.settings import settings


# Cache Key Builder (Versioned)
def make_cache_key(ip: str, model: str = "unknown") -> str:
    """
    Build a versioned, safe Redis key.
    Format:
      ipintel:<version>:<model>:<ip>
    """
    version = settings.CACHE_VERSION
    return f"ipintel:{version}:{model}:{ip}"


class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    
    def get(self, key: str) -> Optional[Any]:
        data = self.client.get(key)
        if not data:
            return None
        try:
            return json.loads(data)
        except Exception:
            return None

    
    def set(self, key: str, value: Any, ttl: int):
        self.client.set(key, json.dumps(value), ex=ttl)

    
    def delete(self, key: str):
        self.client.delete(key)

    def clear(self):
        self.client.flushdb()


redis_cache = RedisCache()


# Helper wrappers called by services
def cache_get(ip: str, model: str = "unknown"):
    key = make_cache_key(ip, model)
    return redis_cache.get(key)


def cache_set(ip: str, value: Any, model: str = "unknown", ttl: Optional[int] = None):
    key = make_cache_key(ip, model)
    ttl = ttl or settings.CACHE_TTL
    redis_cache.set(key, value, ttl)
