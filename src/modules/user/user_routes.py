"""User Blueprint: /api/user."""
from flask import Blueprint

from src.shared.utils.api_response import success_response
from src.shared.utils.messages import USERS_FETCHED
from src.middlewares.auth_middleware import auth_required
from src.modules.user import user_controller

user_bp = Blueprint("user", __name__)


@user_bp.get("/getall")
@auth_required
def getall():
    data, status = user_controller.getall()
    resp, _ = success_response(USERS_FETCHED, data, status)
    return resp, status


@user_bp.get("/me")
@auth_required
def get_me():
    data, status = user_controller.get_me()
    resp, _ = success_response("Profile fetched.", data, status)
    return resp, status


@user_bp.patch("/me")
@auth_required
def update_me():
    data, status = user_controller.update_me()
    resp, _ = success_response("Profile updated.", data, status)
    return resp, status
