"""Redis-backed rate limiting."""

from __future__ import annotations

from flask import request

from src.shared.config.redis_client import get_redis_client
from src.shared.utils.app_error import AppError


def _client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def rate_limit(key: str, limit: int, window_seconds: int) -> None:
    """Increment counter; raise 429 if over limit."""
    try:
        redis_client = get_redis_client()
        full_key = f"rl:{key}"
        count = redis_client.incr(full_key)
        if count == 1:
            redis_client.expire(full_key, window_seconds)
        if count > limit:
            raise AppError("Too many requests. Please try again later.", 429)
    except AppError:
        raise
    except Exception:
        # Fail open if Redis unavailable
        pass


def rate_limit_ip(action: str, limit: int, window_seconds: int = 60) -> None:
    rate_limit(f"{action}:ip:{_client_ip()}", limit, window_seconds)


def rate_limit_user(action: str, user_id: str, limit: int, window_seconds: int = 60) -> None:
    rate_limit(f"{action}:user:{user_id}", limit, window_seconds)
