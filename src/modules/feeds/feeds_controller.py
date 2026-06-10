"""Feed endpoints."""
import uuid

from flask import request, g

from sqlalchemy import select

from src.shared.config.database import SessionLocal
from src.shared.models.social import Follow
from src.shared.models.piece import Piece
from src.shared.models.post import Post
from src.modules.pieces.pieces_dao import piece_to_dict
from src.modules.posts.posts_dao import post_to_dict
from src.modules.user.user_dao import get_user_by_id


def following_feed():
    db = SessionLocal()
    try:
        me = get_user_by_id(db, uuid.UUID(g.user["id"]))
        following_ids = list(
            db.execute(select(Follow.following_id).where(Follow.follower_id == me.id)).scalars().all()
        )
        following_ids.append(me.id)
        items = []
        for piece in db.execute(
            select(Piece)
            .where(Piece.user_id.in_(following_ids), Piece.deleted_at.is_(None), Piece.status == "live")
            .order_by(Piece.created_at.desc())
            .limit(50)
        ).scalars():
            items.append({"type": "piece", **piece_to_dict(piece)})
        for post in db.execute(
            select(Post)
            .where(Post.user_id.in_(following_ids), Post.deleted_at.is_(None), Post.status == "live")
            .order_by(Post.created_at.desc())
            .limit(50)
        ).scalars():
            items.append({"type": "post", **post_to_dict(post)})
        items.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
        return {"items": items[:50]}, 200
    finally:
        db.close()


def explore_feed():
    medium = request.args.get("medium")
    db = SessionLocal()
    try:
        q = select(Piece).where(Piece.deleted_at.is_(None), Piece.status == "live")
        if medium:
            q = q.where(Piece.medium == medium)
        pieces = db.execute(q.order_by(Piece.created_at.desc()).limit(50)).scalars().all()
        return {"items": [{"type": "piece", **piece_to_dict(p)} for p in pieces]}, 200
    finally:
        db.close()


def for_you_feed():
    explore, _ = explore_feed()
    return {"items": explore["items"][:30], "stub": True}, 200
