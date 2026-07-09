"""Notifications controller."""
import uuid
from datetime import datetime

from flask import request, g
from sqlalchemy import select

from src.shared.config.database import SessionLocal
from src.shared.models.user import User
from src.shared.utils.app_error import AppError
from src.modules.notifications import notifications_dao


def list_for_me():
    cursor = request.args.get("cursor")
    limit = min(int(request.args.get("limit", 20)), 50)
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        before = datetime.fromisoformat(cursor) if cursor else None
        notifications = notifications_dao.list_notifications(db, user_id, limit=limit + 1, before=before)
        has_more = len(notifications) > limit
        notifications = notifications[:limit]
        actor_ids = {n.actor_id for n in notifications if n.actor_id}
        actors = {}
        if actor_ids:
            actors = {u.id: u for u in db.execute(select(User).where(User.id.in_(actor_ids))).scalars()}
        items = [
            notifications_dao.notification_to_dict(n, actors.get(n.actor_id)) for n in notifications
        ]
        next_cursor = notifications[-1].created_at.isoformat() if has_more and notifications else None
        return {"items": items, "nextCursor": next_cursor}, 200
    finally:
        db.close()


def mark_read(notification_id: str):
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        ok = notifications_dao.mark_read(db, user_id, uuid.UUID(notification_id))
        if not ok:
            raise AppError("Notification not found.", 404)
        return {"read": True}, 200
    finally:
        db.close()


def mark_all_read():
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        count = notifications_dao.mark_all_read(db, user_id)
        return {"markedRead": count}, 200
    finally:
        db.close()


def unread_count():
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        count = notifications_dao.count_unread(db, user_id)
        return {"count": count}, 200
    finally:
        db.close()
