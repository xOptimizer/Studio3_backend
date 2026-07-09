"""Social graph controller."""
import uuid
from datetime import datetime

from flask import request, g
from sqlalchemy import select

from src.shared.config.database import SessionLocal
from src.shared.models.social import Follow, Like, Comment, Save, Collection, CollectionItem
from src.shared.models.user import User
from src.shared.models.piece import Piece
from src.shared.models.post import Post
from src.shared.utils.app_error import AppError
from src.modules.auth.auth_dao import find_user_by_username
from src.modules.user.user_dao import get_user_by_id
from src.modules.social import social_dao
from src.modules.notifications import notifications_dao


def _get_target_owner_id(db, target_type: str, target_id):
    model = Piece if target_type == "piece" else Post
    row = db.get(model, target_id)
    return row.user_id if row else None


def follow(username: str):
    db = SessionLocal()
    try:
        me = get_user_by_id(db, uuid.UUID(g.user["id"]))
        target = find_user_by_username(db, username.lower())
        if not target:
            raise AppError("User not found.", 404)
        if target.id == me.id:
            raise AppError("Cannot follow yourself.", 400)
        existing = db.query(Follow).filter_by(follower_id=me.id, following_id=target.id).first()
        if existing:
            return {"following": True}, 200
        db.add(Follow(id=uuid.uuid4(), follower_id=me.id, following_id=target.id))
        db.commit()
        notifications_dao.create_and_push(
            db,
            user_id=target.id,
            type="follow",
            actor_id=me.id,
            target_type="user",
            target_id=me.id,
            payload={"followerUsername": me.username, "followerName": me.name},
            title="New follower",
            body=f"{me.name} started following you",
        )
        return {"following": True}, 200
    finally:
        db.close()


def unfollow(username: str):
    db = SessionLocal()
    try:
        me = get_user_by_id(db, uuid.UUID(g.user["id"]))
        target = find_user_by_username(db, username.lower())
        if target:
            db.query(Follow).filter_by(follower_id=me.id, following_id=target.id).delete()
            db.commit()
        return {"following": False}, 200
    finally:
        db.close()


def _toggle_like(target_type: str, target_id: str, like: bool):
    db = SessionLocal()
    try:
        me = get_user_by_id(db, uuid.UUID(g.user["id"]))
        tid = uuid.UUID(target_id)
        q = db.query(Like).filter_by(user_id=me.id, target_type=target_type, target_id=tid)
        if like:
            if not q.first():
                db.add(Like(id=uuid.uuid4(), user_id=me.id, target_type=target_type, target_id=tid))
                db.commit()
                owner_id = _get_target_owner_id(db, target_type, tid)
                if owner_id and owner_id != me.id:
                    notifications_dao.create_and_push(
                        db,
                        user_id=owner_id,
                        type="like",
                        actor_id=me.id,
                        target_type=target_type,
                        target_id=tid,
                        payload={"likerUsername": me.username, "likerName": me.name},
                        title="New like",
                        body=f"{me.name} liked your {target_type}",
                    )
            return {"liked": True}, 200
        q.delete()
        db.commit()
        return {"liked": False}, 200
    finally:
        db.close()


def like_piece(piece_id: str):
    return _toggle_like("piece", piece_id, True)


def unlike_piece(piece_id: str):
    return _toggle_like("piece", piece_id, False)


def like_post(post_id: str):
    return _toggle_like("post", post_id, True)


def unlike_post(post_id: str):
    return _toggle_like("post", post_id, False)


def save_target(target_type: str, target_id: str):
    db = SessionLocal()
    try:
        me = get_user_by_id(db, uuid.UUID(g.user["id"]))
        tid = uuid.UUID(target_id)
        existing = db.query(Save).filter_by(user_id=me.id, target_type=target_type, target_id=tid).first()
        if existing:
            return {"saved": True}, 200
        db.add(Save(id=uuid.uuid4(), user_id=me.id, target_type=target_type, target_id=tid))
        db.commit()
        owner_id = _get_target_owner_id(db, target_type, tid)
        if owner_id and owner_id != me.id:
            notifications_dao.create_and_push(
                db,
                user_id=owner_id,
                type="save",
                actor_id=me.id,
                target_type=target_type,
                target_id=tid,
                payload={"saverUsername": me.username, "saverName": me.name},
                title="New save",
                body=f"{me.name} saved your {target_type}",
            )
        return {"saved": True}, 200
    finally:
        db.close()


def unsave_target(target_type: str, target_id: str):
    db = SessionLocal()
    try:
        me = get_user_by_id(db, uuid.UUID(g.user["id"]))
        db.query(Save).filter_by(
            user_id=me.id, target_type=target_type, target_id=uuid.UUID(target_id)
        ).delete()
        db.commit()
        return {"saved": False}, 200
    finally:
        db.close()


def add_comment(target_type: str, target_id: str):
    body = request.get_json() or {}
    text = (body.get("body") or "").strip()
    if not text:
        raise AppError("Comment body is required.", 400)
    db = SessionLocal()
    try:
        me = get_user_by_id(db, uuid.UUID(g.user["id"]))
        comment = Comment(
            id=uuid.uuid4(),
            user_id=me.id,
            target_type=target_type,
            target_id=uuid.UUID(target_id),
            body=text[:1000],
        )
        db.add(comment)
        db.commit()
        owner_id = _get_target_owner_id(db, target_type, comment.target_id)
        if owner_id and owner_id != me.id:
            notifications_dao.create_and_push(
                db,
                user_id=owner_id,
                type="comment",
                actor_id=me.id,
                target_type=target_type,
                target_id=comment.target_id,
                payload={"commentPreview": text[:140], "commenterUsername": me.username},
                title="New comment",
                body=f"{me.name} commented: {text[:100]}",
            )
        return {
            "id": str(comment.id),
            "body": comment.body,
            "userId": str(me.id),
            "username": me.username,
            "createdAt": comment.created_at.isoformat(),
        }, 201
    finally:
        db.close()


def get_comments(target_type: str, target_id: str, cursor: str | None, limit: int = 50):
    db = SessionLocal()
    try:
        tid = uuid.UUID(target_id)
        before = datetime.fromisoformat(cursor) if cursor else None
        comments = social_dao.list_comments(db, target_type, tid, limit=limit + 1, before=before)
        has_more = len(comments) > limit
        comments = comments[:limit]
        user_ids = {c.user_id for c in comments}
        users = {}
        if user_ids:
            users = {u.id: u for u in db.execute(select(User).where(User.id.in_(user_ids))).scalars()}
        items = [social_dao.comment_to_dict(c, users.get(c.user_id)) for c in comments]
        next_cursor = comments[-1].created_at.isoformat() if has_more and comments else None
        return {"items": items, "nextCursor": next_cursor}, 200
    finally:
        db.close()
