"""Auth Blueprint: /api/auth."""
from flask import Blueprint

from src.shared.utils.api_response import success_response
from src.shared.utils.messages import (
    OTP_SENT,
    LOGIN_SUCCESS,
    LOGOUT_SUCCESS,
    LOGOUT_ALL_SUCCESS,
    REFRESH_SUCCESS,
    PASSWORD_RESET_EMAIL_SENT,
    PASSWORD_RESET_SUCCESS,
)
from src.middlewares.auth_middleware import auth_required
from src.modules.auth import auth_controller

auth_bp = Blueprint("auth", __name__)


def _apply_cookie_ops(resp, cookie_ops):
    if not cookie_ops:
        return
    if cookie_ops.get("set_refresh_cookie"):
        opts = cookie_ops["set_refresh_cookie"].copy()
        value = opts.pop("value")
        resp.set_cookie("refreshToken", value, **opts)
    if cookie_ops.get("clear_refresh_cookie"):
        resp.delete_cookie("refreshToken", path="/")


def _respond(message, data, status, cookie_ops):
    resp, _ = success_response(message, data, status)
    _apply_cookie_ops(resp, cookie_ops)
    return resp, status


@auth_bp.post("/otp/generate")
def otp_generate():
    data, status, cookie_ops = auth_controller.otp_generate()
    return _respond(OTP_SENT, data, status, cookie_ops)


@auth_bp.post("/otp/resend")
def otp_resend():
    data, status, cookie_ops = auth_controller.otp_resend()
    return _respond(OTP_SENT, data, status, cookie_ops)


@auth_bp.post("/register")
def register():
    data, status, cookie_ops = auth_controller.register()
    return _respond(LOGIN_SUCCESS, data, status, cookie_ops)


@auth_bp.post("/login")
def login():
    data, status, cookie_ops = auth_controller.login()
    return _respond(LOGIN_SUCCESS, data, status, cookie_ops)


@auth_bp.post("/refresh")
def refresh():
    data, status, cookie_ops = auth_controller.refresh()
    return _respond(REFRESH_SUCCESS, data, status, cookie_ops)


@auth_bp.post("/logout")
def logout():
    data, status, cookie_ops = auth_controller.logout()
    return _respond(LOGOUT_SUCCESS, data, status, cookie_ops)


@auth_bp.post("/logout-all")
@auth_required
def logout_all():
    data, status, cookie_ops = auth_controller.logout_all()
    return _respond(LOGOUT_ALL_SUCCESS, data, status, cookie_ops)


@auth_bp.post("/forget-password")
def forget_password():
    data, status, cookie_ops = auth_controller.forget_password()
    return _respond(PASSWORD_RESET_EMAIL_SENT, data, status, cookie_ops)


@auth_bp.post("/reset-password")
def reset_password():
    data, status, cookie_ops = auth_controller.reset_password()
    return _respond(PASSWORD_RESET_SUCCESS, data, status, cookie_ops)


@auth_bp.get("/google")
def google_redirect():
    return auth_controller.google_redirect()


@auth_bp.get("/google/callback")
def google_callback():
    return auth_controller.google_callback()
