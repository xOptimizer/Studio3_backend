"""Username utilities — normalize, availability, claim."""

from src.shared.username.availability import AvailabilityResult, check_availability
from src.shared.username.claim import change_username, claim_username
from src.shared.username.normalize import normalize

__all__ = [
    "AvailabilityResult",
    "check_availability",
    "claim_username",
    "change_username",
    "normalize",
]
