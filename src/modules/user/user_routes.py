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
