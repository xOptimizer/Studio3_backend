"""Social graph DAO — batched lookups for likes/saves/comments/follows."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.shared.models.social import Follow, Like, Save, Comment
from src.shared.models.piece import Piece
from src.shared.models.post import Post
from src.shared.models.user import User


def count_likes(db: Session, target_type: str, target_id: uuid.UUID) -> int:
    return db.execute(
        select(func.count(Like.id)).where(Like.target_type == target_type, Like.target_id == target_id)
    ).scalar_one()


def count_comments(db: Session, target_type: str, target_id: uuid.UUID) -> int:
    return db.execute(
        select(func.count(Comment.id)).where(Comment.target_type == target_type, Comment.target_id == target_id)
    ).scalar_one()


def user_liked(db: Session, target_type: str, target_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    return db.execute(
        select(Like.id).where(
            Like.target_type == target_type, Like.target_id == target_id, Like.user_id == user_id
        )
    ).first() is not None


def user_saved(db: Session, target_type: str, target_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    return db.execute(
        select(Save.id).where(
            Save.target_type == target_type, Save.target_id == target_id, Save.user_id == user_id
        )
    ).first() is not None


def user_follows(db: Session, follower_id: Optional[uuid.UUID], following_id: uuid.UUID) -> bool:
    if not follower_id:
        return False
    return db.execute(
        select(Follow.id).where(Follow.follower_id == follower_id, Follow.following_id == following_id)
    ).first() is not None


def count_followers(db: Session, user_id: uuid.UUID) -> int:
    return db.execute(select(func.count(Follow.id)).where(Follow.following_id == user_id)).scalar_one()


def count_following(db: Session, user_id: uuid.UUID) -> int:
    return db.execute(select(func.count(Follow.id)).where(Follow.follower_id == user_id)).scalar_one()


def count_user_saves(db: Session, user_id: uuid.UUID) -> int:
    """Number of pieces/posts this user has saved."""
    return db.execute(select(func.count(Save.id)).where(Save.user_id == user_id)).scalar_one()


def batch_like_counts(db: Session, target_type: str, target_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
    if not target_ids:
        return {}
    rows = db.execute(
        select(Like.target_id, func.count(Like.id))
        .where(Like.target_type == target_type, Like.target_id.in_(target_ids))
        .group_by(Like.target_id)
    ).all()
    return {tid: c for tid, c in rows}


def batch_comment_counts(db: Session, target_type: str, target_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
    if not target_ids:
        return {}
    rows = db.execute(
        select(Comment.target_id, func.count(Comment.id))
        .where(Comment.target_type == target_type, Comment.target_id.in_(target_ids))
        .group_by(Comment.target_id)
    ).all()
    return {tid: c for tid, c in rows}


def batch_user_likes(db: Session, target_type: str, target_ids: list[uuid.UUID], user_id: Optional[uuid.UUID]) -> set:
    if not user_id or not target_ids:
        return set()
    rows = db.execute(
        select(Like.target_id).where(
            Like.target_type == target_type, Like.target_id.in_(target_ids), Like.user_id == user_id
        )
    ).scalars().all()
    return set(rows)


def batch_user_saves(db: Session, target_type: str, target_ids: list[uuid.UUID], user_id: Optional[uuid.UUID]) -> set:
    if not user_id or not target_ids:
        return set()
    rows = db.execute(
        select(Save.target_id).where(
            Save.target_type == target_type, Save.target_id.in_(target_ids), Save.user_id == user_id
        )
    ).scalars().all()
    return set(rows)


def count_saves_for_targets(db: Session, target_type: str, target_ids: list[uuid.UUID]) -> int:
    if not target_ids:
        return 0
    return db.execute(
        select(func.count(Save.id)).where(Save.target_type == target_type, Save.target_id.in_(target_ids))
    ).scalar_one()


def count_likes_for_targets(db: Session, target_type: str, target_ids: list[uuid.UUID]) -> int:
    if not target_ids:
        return 0
    return db.execute(
        select(func.count(Like.id)).where(Like.target_type == target_type, Like.target_id.in_(target_ids))
    ).scalar_one()


def list_comments(
    db: Session, target_type: str, target_id: uuid.UUID, limit: int = 50, before: Optional[datetime] = None
) -> list[Comment]:
    q = select(Comment).where(Comment.target_type == target_type, Comment.target_id == target_id)
    if before:
        q = q.where(Comment.created_at < before)
    return list(db.execute(q.order_by(Comment.created_at.desc()).limit(limit)).scalars().all())


def comment_to_dict(comment: Comment, author: Optional[User]) -> dict:
    return {
        "id": str(comment.id),
        "body": comment.body,
        "author": (
            {"username": author.username, "name": author.name, "profilePhotoUrl": author.image}
            if author
            else None
        ),
        "createdAt": comment.created_at.isoformat(),
    }
