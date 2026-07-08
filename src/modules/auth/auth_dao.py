"""Auth-related DB access."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.shared.models.user import User
from src.shared.models.password_reset_token import PasswordResetToken
from src.shared.models.username_history import UsernameHistory


def find_user_by_email(db: Session, email: str) -> Optional[User]:
    result = db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def find_user_by_username(db: Session, username: str) -> Optional[User]:
    result = db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


def find_user_by_username_or_history(db: Session, username: str) -> tuple[Optional[User], bool]:
    """Resolve user by current username or active history entry. Returns (user, is_redirect)."""
    user = find_user_by_username(db, username)
    if user:
        return user, False

    now = datetime.now(timezone.utc)
    hist = db.execute(
        select(UsernameHistory).where(
            UsernameHistory.username == username,
            UsernameHistory.reserved_until > now,
        )
    ).scalar_one_or_none()
    if hist:
        user = db.get(User, hist.user_id)
        return user, True
    return None, False


def create_user(
    db: Session,
    username: str,
    email: str,
    name: str,
    password_hash: Optional[str] = None,
    image: Optional[str] = None,
    email_verified: bool = False,
    role: Optional[str] = None,
    phone: Optional[str] = None,
) -> User:
    user = User(
        id=uuid.uuid4(),
        username=username,
        email=email,
        name=name,
        password=password_hash,
        image=image,
        email_verified=email_verified,
        role=role,
        phone=phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_password_reset_token(
    db: Session, user_id: uuid.UUID, token_hash: str, expires_at: datetime
) -> PasswordResetToken:
    row = PasswordResetToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def find_password_reset_by_token_hash(
    db: Session, token_hash: str
) -> Optional[PasswordResetToken]:
    result = db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


def delete_password_reset_tokens_for_user(db: Session, user_id: uuid.UUID) -> None:
    from sqlalchemy import delete
    db.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id))
    db.commit()


def update_user_password(db: Session, user_id: uuid.UUID, password_hash: str) -> None:
    from sqlalchemy import update
    db.execute(
        update(User).where(User.id == user_id).values(password=password_hash)
    )
    db.commit()
