"""Generate unique username for OAuth signup."""
from sqlalchemy.orm import Session

from src.shared.username.availability import check_availability
from src.shared.username.normalize import normalize
from src.shared.username.suggest import generate_candidates


def allocate_username(db: Session, base: str) -> str:
    norm = normalize(base)
    if not norm.ok or not norm.normalized:
        norm = normalize(f"user_{base[:20]}")

    candidates = [norm.normalized] + generate_candidates(norm.normalized)
    for c in candidates:
        avail = check_availability(db, c, include_suggestions=False)
        if avail.available:
            return c
    raise ValueError("Could not allocate username")
