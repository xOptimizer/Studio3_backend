"""Push-device registry DAO."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from src.shared.models.device import Device


def utc_now():
    return datetime.now(timezone.utc)


def upsert_device(db: Session, user_id: uuid.UUID, platform: str, push_token: str) -> Device:
    existing = db.execute(select(Device).where(Device.push_token == push_token)).scalar_one_or_none()
    if existing:
        existing.user_id = user_id
        existing.platform = platform
        existing.last_seen_at = utc_now()
        db.commit()
        db.refresh(existing)
        return existing
    device = Device(id=uuid.uuid4(), user_id=user_id, platform=platform, push_token=push_token)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def delete_device_by_token(db: Session, push_token: str) -> bool:
    result = db.execute(delete(Device).where(Device.push_token == push_token))
    db.commit()
    return result.rowcount > 0
