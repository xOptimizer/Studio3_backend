"""Push-notification device/token registry (FCM — mobile + web)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.shared.config.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(16), nullable=False)  # ios|android|web
    # Globally unique, not composite with user_id: an FCM token belongs to one app
    # install, not one user — if a different user logs in on the same device, upserting
    # by token reassigns ownership instead of leaving stale rows under the old user.
    push_token = Column(String(512), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    last_seen_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
