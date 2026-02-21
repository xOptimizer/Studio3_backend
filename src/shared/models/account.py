"""Account model (OAuth/linked accounts)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.shared.config.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    type = Column(String(64), nullable=True)
    provider = Column(String(64), nullable=False)
    provider_account_id = Column(String(255), nullable=False)
    refresh_token = Column(String(512), nullable=True)
    access_token = Column(String(512), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    token_type = Column(String(64), nullable=True)
    scope = Column(String(512), nullable=True)
    id_token = Column(String(2048), nullable=True)
    session_state = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("provider", "provider_account_id", name="uq_provider_account"),
    )

    user = relationship("User", back_populates="accounts")
