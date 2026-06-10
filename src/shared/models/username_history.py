"""Username history — reserved handles after change."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from src.shared.config.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class UsernameHistory(Base):
    __tablename__ = "username_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    username = Column(String(30), nullable=False, unique=True, index=True)
    reserved_until = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
