"""Posts routes."""
import uuid

from flask import Blueprint, g

from src.middlewares.auth_middleware import onboarding_required, optional_auth
from src.shared.utils.api_response import success_response
from src.shared.utils.async_handler import async_handler
from src.modules.posts import posts_controller

posts_bp = Blueprint("posts", __name__)


def _ok(message, data, status=200):
    resp, _ = success_response(message, data, status)
    return resp, status


@posts_bp.post("")
@onboarding_required
@async_handler
def create_post():
    data, status = posts_controller.create()
    return _ok("Post created.", data, status)


@posts_bp.get("/<post_id>")
@optional_auth
@async_handler
def get_post(post_id):
    viewer_id = uuid.UUID(g.user["id"]) if getattr(g, "user", None) else None
    data, status = posts_controller.get_detail(post_id, viewer_id)
    return _ok("OK", data, status)


@posts_bp.patch("/<post_id>")
@onboarding_required
@async_handler
def patch_post(post_id):
    data, status = posts_controller.patch(post_id)
    return _ok("Post updated.", data, status)


@posts_bp.delete("/<post_id>")
@onboarding_required
@async_handler
def delete_post(post_id):
    data, status = posts_controller.delete(post_id)
    return _ok("Post deleted.", data, status)
