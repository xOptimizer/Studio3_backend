"""Per-user activity counts for role-from-activity. Post/sell, buy, save."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID

from src.shared.config.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class UserActivityCount(Base):
    __tablename__ = "user_activity_counts"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    post_count = Column(Integer, nullable=False, default=0)
    purchase_count = Column(Integer, nullable=False, default=0)
    save_count = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
