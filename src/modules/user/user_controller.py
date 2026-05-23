"""User controller: request/response; calls DAO; returns (data, status)."""
import uuid
from typing import List, Optional, Union

from flask import g, request

from src.shared.config.database import SessionLocal
from src.shared.constants import ALLOWED_ROLES
from src.shared.utils.api_response import success_response
from src.shared.utils.messages import USERS_FETCHED
from src.shared.utils.app_error import AppError
from src.modules.user.user_dao import get_all, count, find_user_by_id, update_user_role


def _role_for_response(role_str: Optional[str]) -> Optional[Union[str, List[str]]]:
    """Return role as array when multiple (comma-separated), else as string or None."""
    if not role_str:
        return None
    if "," in role_str:
        return [p.strip() for p in role_str.split(",") if p.strip()]
    return role_str


def getall():
    """Protected: return { users, count }."""
    db = SessionLocal()
    try:
        users = get_all(db)
        total = count(db)
        user_list = [
            {
                "id": str(u.id),
                "email": u.email,
                "name": u.name,
                "image": u.image,
                "email_verified": u.email_verified,
                "role": _role_for_response(u.role),
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
        data = {"users": user_list, "count": total}
        return data, 200
    finally:
        db.close()


def get_me():
    """Protected: return current user profile (for onboarding check and profile)."""
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        user = find_user_by_id(db, user_id)
        if not user:
            raise AppError("User not found.", 404)
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "image": user.image,
            "email_verified": user.email_verified,
            "role": _role_for_response(user.role),
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }, 200
    finally:
        db.close()


def update_me():
    """Protected: set/update current user role (onboarding or toggle). Role is primary interest only—not used for permissions. Body: role string or comma-separated (e.g. \"artist\" or \"artist,collector\")."""
    body = request.get_json() or {}
    role_input = (body.get("role") or "").strip().lower()
    if not role_input:
        raise AppError("Invalid role. Must be one or more of: artist, collector, enthusiast (comma-separated).", 400)
    parts = [p.strip() for p in role_input.split(",") if p.strip()]
    invalid = [p for p in parts if p not in ALLOWED_ROLES]
    if invalid or not parts:
        raise AppError("Invalid role. Must be one or more of: artist, collector, enthusiast (comma-separated).", 400)
    role_string = ",".join(sorted(set(parts)))
    user_id = uuid.UUID(g.user["id"])
    db = SessionLocal()
    try:
        update_user_role(db, user_id, role_string)
        user = find_user_by_id(db, user_id)
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "image": user.image,
            "email_verified": user.email_verified,
            "role": _role_for_response(user.role),
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }, 200
    finally:
        db.close()
