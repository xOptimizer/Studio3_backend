"""Bearer JWT + Redis session check; set g.user = { id, session_id }."""
from functools import wraps

from flask import g, request

from src.shared.config.database import SessionLocal
from src.shared.config.redis_client import get_redis_client
from src.shared.utils.app_error import AppError
from src.shared.utils.jwt_utils import verify_access_token
from src.shared.utils.messages import UNAUTHORIZED, ONBOARDING_REQUIRED, EMAIL_NOT_VERIFIED


def get_bearer_token():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    return auth[7:].strip()


def _load_user_from_token(required: bool):
    token = get_bearer_token()
    if not token:
        if required:
            raise AppError(UNAUTHORIZED, 401)
        return None
    payload = verify_access_token(token)
    if not payload:
        if required:
            raise AppError(UNAUTHORIZED, 401)
        return None
    user_id = payload.get("sub")
    session_id = payload.get("sessionId")
    if not user_id or not session_id:
        if required:
            raise AppError(UNAUTHORIZED, 401)
        return None
    redis_client = get_redis_client()
    if not redis_client.exists(f"session:{session_id}"):
        if required:
            raise AppError(UNAUTHORIZED, 401)
        return None
    g.user = {"id": user_id, "sessionId": session_id}
    return g.user


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        _load_user_from_token(required=True)
        return f(*args, **kwargs)
    return wrapper


def optional_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        _load_user_from_token(required=False)
        return f(*args, **kwargs)
    return wrapper


def _get_db_user():
    import uuid
    from src.modules.user.user_dao import get_user_by_id
    db = SessionLocal()
    try:
        return get_user_by_id(db, uuid.UUID(g.user["id"]))
    finally:
        db.close()


def email_verified_required(f):
    @wraps(f)
    @auth_required
    def wrapper(*args, **kwargs):
        user = _get_db_user()
        if not user or not user.email_verified:
            raise AppError(EMAIL_NOT_VERIFIED, 403)
        return f(*args, **kwargs)
    return wrapper


def onboarding_required(f):
    @wraps(f)
    @auth_required
    def wrapper(*args, **kwargs):
        user = _get_db_user()
        if not user or not user.onboarding_complete:
            raise AppError(ONBOARDING_REQUIRED, 403)
        if not user.email_verified:
            raise AppError(EMAIL_NOT_VERIFIED, 403)
        return f(*args, **kwargs)
    return wrapper


def seller_required(f):
    @wraps(f)
    @auth_required
    def wrapper(*args, **kwargs):
        user = _get_db_user()
        if not user or not user.seller_enabled:
            raise AppError("Enable seller mode to perform this action.", 403)
        return f(*args, **kwargs)
    return wrapper
