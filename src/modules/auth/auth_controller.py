"""Auth: request/response, validation; calls services and DAOs; returns (data, status, cookie_ops)."""
import os
import uuid
import secrets
import bcrypt
from datetime import datetime, timezone, timedelta
from flask import request, g
from sqlalchemy.orm import Session

from src.shared.config.database import SessionLocal
from src.shared.utils.app_error import AppError
from src.shared.utils.messages import (
    OTP_SENT,
    OTP_VERIFICATION_FAILED,
    EMAIL_REQUIRED,
    INVALID_CREDENTIALS,
    USER_ALREADY_EXISTS,
    LOGIN_SUCCESS,
    LOGOUT_SUCCESS,
    LOGOUT_ALL_SUCCESS,
    REFRESH_SUCCESS,
    PASSWORD_RESET_EMAIL_SENT,
    PASSWORD_RESET_SUCCESS,
    INVALID_RESET_TOKEN,
    UNAUTHORIZED,
)
from src.shared.utils.jwt_utils import sign_access_token
from src.shared.notification.email_service import send_email
from src.shared.templates.otp_template import get_otp_html
from src.modules.auth.auth_dao import (
    find_user_by_email,
    create_user,
)
from src.modules.auth.services.otp_service import (
    acquire_lock,
    check_resend_limit,
    store_otp,
    verify_otp,
    generate_otp,
)
from src.modules.auth.services.password_reset_service import (
    request_password_reset,
    reset_password as do_reset_password,
)
from src.modules.sessions.session_service import (
    create_session,
    delete_session,
    delete_all_sessions_for_user,
)
from src.modules.sessions.refresh_token_dao import (
    create as create_refresh_token,
    find_by_id,
    revoke_by_id,
    revoke_all_for_user,
)
from src.modules.auth.google_oauth_service import (
    get_google_auth_url,
    exchange_code_for_tokens,
    verify_google_id_token,
    get_or_create_user_from_google,
    consume_state,
    build_redirect_with_token,
)

SALT_ROUNDS = int(os.getenv("SALT_ROUNDS", "10"))
REFRESH_TOKEN_DAYS = 7
COOKIE_MAX_AGE = 7 * 24 * 3600


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=SALT_ROUNDS)).decode()


def _verify_password(password: str, pwd_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), pwd_hash.encode())


def _hash_refresh_secret(secret: str) -> str:
    return bcrypt.hashpw(secret.encode(), bcrypt.gensalt(rounds=SALT_ROUNDS)).decode()


def _issue_session_and_tokens(user, request_obj=None):
    """Create Redis session, refresh token row; return (data, status, cookie_ops). Cookie = id.secret."""
    db = SessionLocal()
    try:
        user_id = str(user.id)
        user_agent = request_obj.headers.get("User-Agent", "") if request_obj else ""
        ip = request_obj.remote_addr if request_obj else ""
        session_id = create_session(user_id, user_agent, ip)
        access_token = sign_access_token({"sub": user_id, "sessionId": session_id})

        secret = secrets.token_hex(32)
        hashed = _hash_refresh_secret(secret)
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DAYS)
        row = create_refresh_token(db, user.id, hashed, session_id, expires_at)
        cookie_value = f"{row.id}.{secret}"

        cookie_opts = {
            "value": cookie_value,
            "max_age": COOKIE_MAX_AGE,
            "httponly": True,
            "samesite": "Lax",
            "path": "/",
        }
        if os.getenv("FLASK_ENV") == "production":
            cookie_opts["secure"] = True

        return (
            {"accessToken": access_token, "user": {"name": user.name, "email": user.email}},
            200,
            {"set_refresh_cookie": cookie_opts},
        )
    finally:
        db.close()


# ---- OTP ----
def otp_generate():
    body = request.get_json() or {}
    email = (body.get("email") or "").strip()
    if not email:
        raise AppError(EMAIL_REQUIRED, 400)
    if not acquire_lock(email):
        raise AppError("Please wait before requesting another OTP.", 429)
    if not check_resend_limit(email):
        raise AppError("Resend limit exceeded. Try again later.", 429)
    otp = generate_otp(6)
    store_otp(email, otp)
    send_email(email, "Your verification code", get_otp_html(otp))
    return {"message": OTP_SENT}, 200, None


def otp_resend():
    return otp_generate()


# ---- Register ----
def register():
    body = request.get_json() or {}
    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip().lower()
    password = body.get("password")
    otp = (body.get("otp") or "").strip()
    if not email:
        raise AppError(EMAIL_REQUIRED, 400)
    if not password:
        raise AppError("Password is required.", 400)
    if not otp:
        raise AppError(OTP_VERIFICATION_FAILED, 400)
    if not verify_otp(email, otp):
        raise AppError(OTP_VERIFICATION_FAILED, 400)
    db = SessionLocal()
    try:
        if find_user_by_email(db, email):
            raise AppError(USER_ALREADY_EXISTS, 409)
        user = create_user(
            db, email=email, name=name or None, password_hash=_hash_password(password), email_verified=True
        )
        return _issue_session_and_tokens(user, request)
    finally:
        db.close()


# ---- Login ----
def login():
    body = request.get_json() or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password")
    if not email:
        raise AppError(EMAIL_REQUIRED, 400)
    if not password:
        raise AppError("Password is required.", 400)
    db = SessionLocal()
    try:
        user = find_user_by_email(db, email)
        if not user or not user.password:
            raise AppError(INVALID_CREDENTIALS, 401)
        if not _verify_password(password, user.password):
            raise AppError(INVALID_CREDENTIALS, 401)
        return _issue_session_and_tokens(user, request)
    finally:
        db.close()


# ---- Refresh (rotate: revoke old, create new token + cookie) ----
def refresh():
    cookie = request.cookies.get("refreshToken")
    if not cookie or "." not in cookie:
        raise AppError(UNAUTHORIZED, 401)
    parts = cookie.split(".", 1)
    token_id_str, secret = parts[0], parts[1]
    try:
        token_id = uuid.UUID(token_id_str)
    except ValueError:
        raise AppError(UNAUTHORIZED, 401)
    db = SessionLocal()
    try:
        row = find_by_id(db, token_id)
        if not row or row.is_revoked or row.expires_at < datetime.now(timezone.utc):
            raise AppError(UNAUTHORIZED, 401)
        if not bcrypt.checkpw(secret.encode(), row.hashed_token.encode()):
            raise AppError(UNAUTHORIZED, 401)
        from src.modules.sessions.session_service import find_session as _find_session
        if not _find_session(row.session_id):
            raise AppError(UNAUTHORIZED, 401)
        from src.shared.models.user import User
        user = db.get(User, row.user_id)
        if not user:
            raise AppError(UNAUTHORIZED, 401)
        revoke_by_id(db, token_id)
        return _issue_session_and_tokens(user, request)
    finally:
        db.close()


# ---- Logout ----
def logout():
    cookie = request.cookies.get("refreshToken")
    if cookie and "." in cookie:
        parts = cookie.split(".", 1)
        try:
            token_id = uuid.UUID(parts[0])
        except ValueError:
            pass
        else:
            db = SessionLocal()
            try:
                row = find_by_id(db, token_id)
                if row:
                    revoke_by_id(db, token_id)
                    delete_session(row.session_id)
            finally:
                db.close()
    return {"message": LOGOUT_SUCCESS}, 200, {"clear_refresh_cookie": True}


# ---- Logout all (protected) ----
def logout_all():
    user_id = g.user.get("id")
    if not user_id:
        raise AppError(UNAUTHORIZED, 401)
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise AppError(UNAUTHORIZED, 401)
    db = SessionLocal()
    try:
        revoke_all_for_user(db, uid)
    finally:
        db.close()
    delete_all_sessions_for_user(user_id)
    return {"message": LOGOUT_ALL_SUCCESS}, 200, {"clear_refresh_cookie": True}


# ---- Forget / Reset password ----
def forget_password():
    body = request.get_json() or {}
    email = (body.get("email") or "").strip().lower()
    if not email:
        raise AppError(EMAIL_REQUIRED, 400)
    db = SessionLocal()
    try:
        request_password_reset(db, email)
    finally:
        db.close()
    return {"message": PASSWORD_RESET_EMAIL_SENT}, 200, None


def reset_password():
    body = request.get_json() or {}
    token = (body.get("token") or "").strip()
    new_password = body.get("newPassword")
    if not token:
        raise AppError(INVALID_RESET_TOKEN, 400)
    if not new_password:
        raise AppError("New password is required.", 400)
    db = SessionLocal()
    try:
        ok = do_reset_password(db, token, _hash_password(new_password))
    finally:
        db.close()
    if not ok:
        raise AppError(INVALID_RESET_TOKEN, 400)
    return {"message": PASSWORD_RESET_SUCCESS}, 200, None


# ---- Google OAuth ----
def google_redirect():
    url = get_google_auth_url()
    from flask import redirect
    return redirect(url)


def google_callback():
    from flask import redirect
    state = request.args.get("state")
    code = request.args.get("code")
    if not state or not consume_state(state):
        raise AppError("Invalid or expired OAuth state.", 400)
    if not code:
        raise AppError("Missing authorization code.", 400)
    tokens = exchange_code_for_tokens(code)
    id_token = tokens.get("id_token")
    if not id_token:
        raise AppError("Google did not return id_token.", 400)
    payload = verify_google_id_token(id_token)
    db = SessionLocal()
    try:
        user, _ = get_or_create_user_from_google(db, payload, id_token_raw=id_token)
        data, status, cookie_ops = _issue_session_and_tokens(user, request)
        url = build_redirect_with_token(data["accessToken"])
        resp = redirect(url)
        if cookie_ops and cookie_ops.get("set_refresh_cookie"):
            opts = cookie_ops["set_refresh_cookie"].copy()
            val = opts.pop("value")
            resp.set_cookie("refreshToken", val, **opts)
        return resp
    finally:
        db.close()
