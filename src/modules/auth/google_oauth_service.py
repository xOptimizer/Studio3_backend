"""Google OAuth: state in Redis (create/consume), exchange code, verify id_token, find/create user+account."""
import os
import uuid
import requests
import jwt
from jwt import PyJWKClient

from sqlalchemy.orm import Session

from src.shared.config.redis_client import get_redis_client
from src.shared.utils.app_error import AppError
from src.modules.auth.auth_dao import (
    find_user_by_email,
    find_account_by_provider,
    create_user,
    create_account,
)

OAUTH_STATE_TTL = 60 * 5  # 5 min
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:9000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
OAUTH_SUCCESS_PATH = os.getenv("OAUTH_SUCCESS_PATH", "/auth/callback")


def create_state() -> str:
    """Store state in Redis, return state string."""
    state = str(uuid.uuid4())
    r = get_redis_client()
    r.setex(f"oauth:state:{state}", OAUTH_STATE_TTL, "1")
    return state


def consume_state(state: str) -> bool:
    """Get and delete state; return True if existed."""
    r = get_redis_client()
    key = f"oauth:state:{state}"
    if not r.get(key):
        return False
    r.delete(key)
    return True


def get_google_auth_url() -> str:
    state = create_state()
    redirect_uri = f"{BACKEND_URL}/api/auth/google/callback"
    scope = "openid email profile"
    return (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        f"&scope={scope}"
        f"&state={state}"
        "&access_type=offline"
        "&prompt=consent"
    )


def exchange_code_for_tokens(code: str) -> dict:
    """Exchange authorization code for access_token and id_token."""
    redirect_uri = f"{BACKEND_URL}/api/auth/google/callback"
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    if resp.status_code != 200:
        raise AppError("Google OAuth token exchange failed", 400)
    return resp.json()


def verify_google_id_token(id_token: str) -> dict:
    """Verify id_token with Google JWKS; return decoded payload."""
    try:
        jwks_url = "https://www.googleapis.com/oauth2/v3/certs"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        payload = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=GOOGLE_CLIENT_ID,
        )
        return payload
    except Exception as e:
        raise AppError(f"Invalid Google id_token: {e}", 400)


def get_or_create_user_from_google(db: Session, payload: dict, id_token_raw: str = None):
    """Find or create user and account from Google id_token payload. Returns (user, account)."""
    email = payload.get("email")
    if not email:
        raise AppError("Google profile missing email", 400)
    sub = payload.get("sub")  # Google subject id
    name = payload.get("name") or (payload.get("email") or "").split("@")[0]
    picture = payload.get("picture")

    account = find_account_by_provider(db, "google", sub)
    if account:
        return account.user, account

    user = find_user_by_email(db, email)
    if not user:
        user = create_user(
            db,
            email=email,
            name=name,
            password_hash=None,
            image=picture,
            email_verified=payload.get("email_verified", True),
        )
    account = create_account(
        db,
        user_id=user.id,
        provider="google",
        provider_account_id=sub,
        id_token=id_token_raw,
    )
    return user, account


def build_redirect_with_token(access_token: str) -> str:
    """Redirect to frontend with access_token in hash."""
    return f"{FRONTEND_URL}{OAUTH_SUCCESS_PATH}#access_token={access_token}"
