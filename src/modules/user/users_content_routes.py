"""Public user content listings (pieces, posts)."""
from flask import Blueprint

from src.shared.utils.api_response import success_response
from src.shared.utils.async_handler import async_handler
from src.modules.pieces import pieces_controller
from src.modules.posts import posts_controller
from src.modules.series import series_controller

users_bp = Blueprint("users", __name__)


def _ok(message, data, status=200):
    resp, _ = success_response(message, data, status)
    return resp, status


@users_bp.get("/<username>/pieces")
@async_handler
def list_pieces(username):
    data, status = pieces_controller.list_for_user(username)
    return _ok("OK", data, status)


@users_bp.get("/<username>/pieces/for-sale")
@async_handler
def list_pieces_for_sale(username):
    data, status = pieces_controller.list_for_user(username, for_sale_only=True)
    return _ok("OK", data, status)


@users_bp.get("/<username>/posts")
@async_handler
def list_posts(username):
    data, status = posts_controller.list_for_user(username)
    return _ok("OK", data, status)


@users_bp.get("/<username>/series")
@async_handler
def list_series(username):
    data, status = series_controller.list_for_user(username)
    return _ok("OK", data, status)
