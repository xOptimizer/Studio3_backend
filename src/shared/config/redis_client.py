"""Single Redis connection client."""
import os
from typing import Optional

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Return the global Redis client (create if needed)."""
    global _client
    if _client is None:
        # rediss:// = TLS; many hosted Redis (Render, Upstash) need cert verification relaxed
        kwargs = {"decode_responses": True}
        if REDIS_URL.startswith("rediss://"):
            kwargs["ssl_cert_reqs"] = None
        _client = redis.from_url(REDIS_URL, **kwargs)
    return _client


def close_redis() -> None:
    """Close the Redis connection (call on shutdown)."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


def check_redis_connection() -> bool:
    """Ping Redis to verify it's reachable."""
    try:
        r = get_redis_client()
        return r.ping()
    except Exception as e:
        from src.shared.utils.logger import get_logger
        get_logger("redis").error("Redis connection failed: %s", e)
        return False
