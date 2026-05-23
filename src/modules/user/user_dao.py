"""User DB access only."""
import uuid
from typing import Optional

from sqlalchemy import select, func, update
from sqlalchemy.orm import Session

from src.shared.models.user import User


def find_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    result = db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def update_user_role(db: Session, user_id: uuid.UUID, role: str) -> None:
    db.execute(update(User).where(User.id == user_id).values(role=role))
    db.commit()


def get_all(db: Session):
    """Return list of all users (for getall endpoint)."""
    result = db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


def count(db: Session) -> int:
    result = db.execute(select(func.count(User.id)))
    return result.scalar() or 0
