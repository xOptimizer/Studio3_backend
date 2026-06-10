"""Posts DAO."""
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.shared.models.post import Post


def create_post(db: Session, **kwargs) -> Post:
    post = Post(id=uuid.uuid4(), **kwargs)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get_post(db: Session, post_id: uuid.UUID) -> Optional[Post]:
    return db.execute(
        select(Post).where(Post.id == post_id, Post.deleted_at.is_(None))
    ).scalar_one_or_none()


def list_user_posts(db: Session, user_id: uuid.UUID) -> list[Post]:
    return list(
        db.execute(
            select(Post)
            .where(Post.user_id == user_id, Post.deleted_at.is_(None), Post.status == "live")
            .order_by(Post.created_at.desc())
        ).scalars().all()
    )


def list_related_posts(db: Session, piece_id: uuid.UUID) -> list[Post]:
    return list(
        db.execute(
            select(Post).where(Post.linked_piece_id == piece_id, Post.deleted_at.is_(None))
        ).scalars().all()
    )


def post_to_dict(post: Post) -> dict:
    return {
        "id": str(post.id),
        "userId": str(post.user_id),
        "mediaUrl": post.media_url,
        "mediaType": post.media_type,
        "caption": post.caption,
        "isProcess": post.is_process,
        "linkedPieceId": str(post.linked_piece_id) if post.linked_piece_id else None,
        "status": post.status,
        "createdAt": post.created_at.isoformat(),
    }
