"""Redis OTP: lock (30s), resend limit (3 per 1 min), store/verify OTP (5 min TTL)."""
import random
import string
from src.shared.config.redis_client import get_redis_client

OTP_TTL = 60 * 5  # 5 min
LOCK_TTL = 30  # 30 s
RESEND_WINDOW = 60  # 1 min
RESEND_MAX = 3


def _key_otp(email: str) -> str:
    return f"otp:{email}"


def _key_lock(email: str) -> str:
    return f"otp:lock:{email}"


def _key_resend(email: str) -> str:
    return f"otp:resend:{email}"


def acquire_lock(email: str) -> bool:
    """Try to set lock; return True if acquired."""
    r = get_redis_client()
    key = _key_lock(email)
    return r.set(key, "1", nx=True, ex=LOCK_TTL)


def check_resend_limit(email: str) -> bool:
    """True if can resend (under limit). Uses sliding window: incr resend key, set ex if new."""
    r = get_redis_client()
    key = _key_resend(email)
    count = r.incr(key)
    if count == 1:
        r.expire(key, RESEND_WINDOW)
    return count <= RESEND_MAX


def store_otp(email: str, otp: str) -> None:
    r = get_redis_client()
    r.setex(_key_otp(email), OTP_TTL, otp)


def verify_otp(email: str, otp: str) -> bool:
    """Verify and delete OTP key if match."""
    r = get_redis_client()
    key = _key_otp(email)
    stored = r.get(key)
    if stored is None or stored != otp:
        return False
    r.delete(key)
    return True


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))
