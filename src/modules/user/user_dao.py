"""User profile and onboarding DAO."""
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.shared.models.user import User
from src.shared.models.piece import Piece


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    return db.get(User, user_id)


def update_user_fields(db: Session, user: User, **fields) -> User:
    for k, v in fields.items():
        if hasattr(user, k):
            setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


def delist_user_pieces(db: Session, user_id: uuid.UUID) -> None:
    pieces = db.execute(
        select(Piece).where(Piece.user_id == user_id, Piece.is_for_sale == True)
    ).scalars().all()
    for p in pieces:
        p.is_for_sale = False
        p.status = "delisted"
    db.commit()
