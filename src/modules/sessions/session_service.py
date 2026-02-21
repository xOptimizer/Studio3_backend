"""Redis session: create, find, delete. Key session:<session_id>, TTL 7 days."""
import json
import uuid
from datetime import datetime, timezone

from src.shared.config.redis_client import get_redis_client

SESSION_TTL_DAYS = 7
SESSION_TTL_SECONDS = 60 * 60 * 24 * SESSION_TTL_DAYS


def create_session(user_id: str, user_agent: str = "", ip: str = "") -> str:
    """Create Redis session; return session_id."""
    session_id = str(uuid.uuid4())
    key = f"session:{session_id}"
    value = json.dumps({
        "userId": user_id,
        "userAgent": user_agent or "",
        "ip": ip or "",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    })
    r = get_redis_client()
    r.setex(key, SESSION_TTL_SECONDS, value)
    return session_id


def find_session(session_id: str):
    """Get session data or None if missing/expired."""
    r = get_redis_client()
    raw = r.get(f"session:{session_id}")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def delete_session(session_id: str) -> None:
    """Remove one session from Redis."""
    r = get_redis_client()
    r.delete(f"session:{session_id}")


def delete_all_sessions_for_user(user_id: str) -> None:
    """Scan keys session:* and remove those whose value contains this user_id. O(n) over keys."""
    r = get_redis_client()
    pattern = "session:*"
    for key in r.scan_iter(match=pattern):
        try:
            raw = r.get(key)
            if raw:
                data = json.loads(raw)
                if data.get("userId") == user_id:
                    r.delete(key)
        except Exception:
            continue
