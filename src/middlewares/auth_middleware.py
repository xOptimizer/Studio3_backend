"""Bearer JWT + Redis session check; set g.user = { id, session_id }."""
from flask import g, request

from src.shared.config.redis_client import get_redis_client
from src.shared.utils.app_error import AppError
from src.shared.utils.jwt_utils import verify_access_token
from src.shared.utils.messages import UNAUTHORIZED


def get_bearer_token():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    return auth[7:].strip()


def auth_required(f):
    """Decorator: verify JWT, check Redis session exists, set g.user."""
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        token = get_bearer_token()
        if not token:
            raise AppError(UNAUTHORIZED, 401)
        payload = verify_access_token(token)
        if not payload:
            raise AppError(UNAUTHORIZED, 401)
        user_id = payload.get("sub")
        session_id = payload.get("sessionId")
        if not user_id or not session_id:
            raise AppError(UNAUTHORIZED, 401)
        redis_client = get_redis_client()
        key = f"session:{session_id}"
        if not redis_client.exists(key):
            raise AppError(UNAUTHORIZED, 401)
        g.user = {"id": user_id, "sessionId": session_id}
        return f(*args, **kwargs)

    return wrapper
