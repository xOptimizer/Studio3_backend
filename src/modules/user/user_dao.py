"""User DB access only."""
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.shared.models.user import User


def get_all(db: Session):
    """Return list of all users (for getall endpoint)."""
    result = db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


def count(db: Session) -> int:
    result = db.execute(select(func.count(User.id)))
    return result.scalar() or 0
