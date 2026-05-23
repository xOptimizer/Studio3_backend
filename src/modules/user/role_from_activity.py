"""Compute user role(s) from activity counts; recalculate and persist. Multiple roles when active in 2+ categories."""

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from src.modules.user.user_activity_dao import get_or_create_counts
from src.modules.user.user_dao import find_user_by_id, update_user_role

# Any count >= this is "active" for that category. Can make configurable later.
ACTIVITY_THRESHOLD = 1


def compute_role_from_counts(
    post_count: int, purchase_count: int, save_count: int
) -> Optional[List[str]]:
    """Return list of roles for every category where user is active (count >= threshold). All zero -> None."""
    roles: List[str] = []
    if post_count >= ACTIVITY_THRESHOLD:
        roles.append("artist")
    if purchase_count >= ACTIVITY_THRESHOLD:
        roles.append("collector")
    if save_count >= ACTIVITY_THRESHOLD:
        roles.append("enthusiast")
    if not roles:
        return None
    return roles


def recalculate_user_role(db: Session, user_id: uuid.UUID) -> bool:
    """Load activity counts, compute role(s), persist as comma-separated if different. Returns True if updated."""
    row = get_or_create_counts(db, user_id)
    if row.post_count == 0 and row.purchase_count == 0 and row.save_count == 0:
        return False
    computed = compute_role_from_counts(
        row.post_count, row.purchase_count, row.save_count
    )
    if not computed:
        return False
    persisted_string = ",".join(sorted(computed))  # stable order: artist, collector, enthusiast
    user = find_user_by_id(db, user_id)
    if not user:
        return False
    if user.role == persisted_string:
        return False
    update_user_role(db, user_id, persisted_string)
    return True
