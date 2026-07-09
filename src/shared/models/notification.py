"""In-app notification model."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.shared.config.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(32), nullable=False)  # save|follow|inquiry|purchase|like|comment
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    target_type = Column(String(16), nullable=True)  # piece|post|order|inquiry|user
    target_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    payload = Column(JSONB, nullable=True)  # pre-rendered display fields (message, pieceTitle, thumbnailUrl, ...)
    read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
