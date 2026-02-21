"""Auth-related DB access: users (by email, create), accounts, password_reset_tokens."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.shared.models.user import User
from src.shared.models.account import Account
from src.shared.models.password_reset_token import PasswordResetToken


def find_user_by_email(db: Session, email: str) -> Optional[User]:
    result = db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def create_user(
    db: Session,
    email: str,
    name: Optional[str] = None,
    password_hash: Optional[str] = None,
    image: Optional[str] = None,
    email_verified: bool = False,
) -> User:
    user = User(
        id=uuid.uuid4(),
        email=email,
        name=name,
        password=password_hash,
        image=image,
        email_verified=email_verified,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_account(
    db: Session,
    user_id: uuid.UUID,
    provider: str,
    provider_account_id: str,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    id_token: Optional[str] = None,
) -> Account:
    acc = Account(
        id=uuid.uuid4(),
        user_id=user_id,
        type="oauth",
        provider=provider,
        provider_account_id=provider_account_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        id_token=id_token,
    )
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc


def find_account_by_provider(
    db: Session, provider: str, provider_account_id: str
) -> Optional[Account]:
    result = db.execute(
        select(Account).where(
            Account.provider == provider,
            Account.provider_account_id == provider_account_id,
        )
    )
    return result.scalar_one_or_none()


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
