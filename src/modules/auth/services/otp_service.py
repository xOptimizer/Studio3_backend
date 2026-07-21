"""Redis OTP: lock (30s), resend limit (3 per 1 min), store/verify OTP (5 min TTL)."""
import functools
import random
import string

from redis.exceptions import RedisError

from src.shared.config.redis_client import get_redis_client
from src.shared.utils.app_error import AppError

OTP_TTL = 60 * 5  # 5 min
LOCK_TTL = 30  # 30 s
RESEND_WINDOW = 60  # 1 min
RESEND_MAX = 3

OTP_SERVICE_UNAVAILABLE = "OTP service is temporarily unavailable. Please try again in a moment."


def _guard_redis(fn):
    """Turn a Redis connectivity failure into a clean 503 instead of an
    unhandled 500 — otherwise any transient connection hiccup crashes with
    a raw stack trace via the generic exception handler."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except RedisError:
            raise AppError(OTP_SERVICE_UNAVAILABLE, 503)
    return wrapper


def _key_otp(email: str) -> str:
    return f"otp:{email}"


def _key_lock(email: str) -> str:
    return f"otp:lock:{email}"


def _key_resend(email: str) -> str:
    return f"otp:resend:{email}"


@_guard_redis
def acquire_lock(email: str) -> bool:
    """Try to set lock; return True if acquired."""
    r = get_redis_client()
    key = _key_lock(email)
    return r.set(key, "1", nx=True, ex=LOCK_TTL)


@_guard_redis
def check_resend_limit(email: str) -> bool:
    """True if can resend (under limit). Uses sliding window: incr resend key, set ex if new."""
    r = get_redis_client()
    key = _key_resend(email)
    count = r.incr(key)
    if count == 1:
        r.expire(key, RESEND_WINDOW)
    return count <= RESEND_MAX


@_guard_redis
def store_otp(email: str, otp: str) -> None:
    r = get_redis_client()
    r.setex(_key_otp(email), OTP_TTL, otp)


@_guard_redis
def verify_otp(email: str, otp: str) -> bool:
    """Verify and delete OTP key if match — the real, single-use consumption
    used by register()/confirm_email_change()."""
    r = get_redis_client()
    key = _key_otp(email)
    stored = r.get(key)
    if stored is None or stored != otp:
        return False
    r.delete(key)
    return True


@_guard_redis
def peek_otp(email: str, otp: str) -> bool:
    """Check the OTP matches without deleting it, and refresh its TTL on
    success so the remaining sign-up steps (username/phone/password) aren't
    racing the original 5-minute window. Used by the dedicated /otp/verify
    step; the real, single-use check still happens in verify_otp() at
    registration time."""
    r = get_redis_client()
    key = _key_otp(email)
    stored = r.get(key)
    if stored is None or stored != otp:
        return False
    r.expire(key, OTP_TTL)
    return True


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))
