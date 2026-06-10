"""Social graph controller."""
import uuid

from flask import request, g

from src.shared.config.database import SessionLocal
from src.shared.models.social import Follow, Like, Comment, Save, Collection, CollectionItem
from src.shared.utils.app_error import AppError
from src.modules.auth.auth_dao import find_user_by_username
from src.modules.user.user_dao import get_user_by_id


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
        return {
            "id": str(comment.id),
            "body": comment.body,
            "userId": str(me.id),
            "username": me.username,
            "createdAt": comment.created_at.isoformat(),
        }, 201
    finally:
        db.close()
