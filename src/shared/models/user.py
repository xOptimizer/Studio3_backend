"""User model."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Boolean, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.shared.config.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=True)  # null for OAuth-only users
    image = Column(String(512), nullable=True)
    cover_photo_url = Column(String(512), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    phone = Column(String(32), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    role = Column(String(32), nullable=True)
    seller_enabled = Column(Boolean, default=False, nullable=False)
    onboarding_complete = Column(Boolean, default=False, nullable=False)
    taste_preferences = Column(JSONB, nullable=True)  # {mediums, styles, themes}
    last_username_change_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    password_reset_tokens = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )
    username_history = relationship(
        "UsernameHistory", backref="user", cascade="all, delete-orphan"
    )
