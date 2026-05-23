"""DAO for user_activity_counts: get_or_create, increment by activity kind."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.shared.constants import ACTIVITY_KINDS
from src.shared.models.user_activity_count import UserActivityCount


def get_or_create_counts(db: Session, user_id: uuid.UUID) -> UserActivityCount:
    """Return the activity counts row for user_id; create with all zeros if missing."""
    row = db.execute(
        select(UserActivityCount).where(UserActivityCount.user_id == user_id)
    ).scalar_one_or_none()
    if row:
        return row
    row = UserActivityCount(
        user_id=user_id,
        post_count=0,
        purchase_count=0,
        save_count=0,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def increment_activity(
    db: Session, user_id: uuid.UUID, activity_kind: str
) -> None:
    """Increment the count for activity_kind. Must be one of ACTIVITY_KINDS. Commits."""
    if activity_kind not in ACTIVITY_KINDS:
        raise ValueError(
            f"Invalid activity_kind: {activity_kind!r}. Must be one of: {', '.join(ACTIVITY_KINDS)}."
        )
    row = get_or_create_counts(db, user_id)
    if activity_kind == "post":
        row.post_count += 1
    elif activity_kind == "purchase":
        row.purchase_count += 1
    else:  # save
        row.save_count += 1
    row.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
