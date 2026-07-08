"""Social routes."""
from flask import Blueprint, request

from src.middlewares.auth_middleware import onboarding_required
from src.shared.utils.api_response import success_response
from src.shared.utils.async_handler import async_handler
from src.modules.social import social_controller

social_bp = Blueprint("social", __name__)


def _ok(message, data, status=200):
    resp, _ = success_response(message, data, status)
    return resp, status


@social_bp.post("/users/<username>/follow")
@onboarding_required
@async_handler
def follow(username):
    data, status = social_controller.follow(username)
    return _ok("Following.", data, status)


@social_bp.delete("/users/<username>/follow")
@onboarding_required
@async_handler
def unfollow(username):
    data, status = social_controller.unfollow(username)
    return _ok("Unfollowed.", data, status)


@social_bp.post("/pieces/<piece_id>/like")
@onboarding_required
@async_handler
def like_piece(piece_id):
    data, status = social_controller.like_piece(piece_id)
    return _ok("OK", data, status)


@social_bp.delete("/pieces/<piece_id>/like")
@onboarding_required
@async_handler
def unlike_piece(piece_id):
    data, status = social_controller.unlike_piece(piece_id)
    return _ok("OK", data, status)


@social_bp.post("/posts/<post_id>/like")
@onboarding_required
@async_handler
def like_post(post_id):
    data, status = social_controller.like_post(post_id)
    return _ok("OK", data, status)


@social_bp.delete("/posts/<post_id>/like")
@onboarding_required
@async_handler
def unlike_post(post_id):
    data, status = social_controller.unlike_post(post_id)
    return _ok("OK", data, status)


@social_bp.post("/pieces/<piece_id>/save")
@onboarding_required
@async_handler
def save_piece(piece_id):
    data, status = social_controller.save_target("piece", piece_id)
    return _ok("Saved.", data, status)


@social_bp.delete("/pieces/<piece_id>/save")
@onboarding_required
@async_handler
def unsave_piece(piece_id):
    data, status = social_controller.unsave_target("piece", piece_id)
    return _ok("Unsaved.", data, status)


@social_bp.post("/posts/<post_id>/save")
@onboarding_required
@async_handler
def save_post(post_id):
    data, status = social_controller.save_target("post", post_id)
    return _ok("Saved.", data, status)


@social_bp.delete("/posts/<post_id>/save")
@onboarding_required
@async_handler
def unsave_post(post_id):
    data, status = social_controller.unsave_target("post", post_id)
    return _ok("Unsaved.", data, status)


@social_bp.post("/pieces/<piece_id>/comments")
@onboarding_required
@async_handler
def comment_piece(piece_id):
    data, status = social_controller.add_comment("piece", piece_id)
    return _ok("Comment added.", data, status)


@social_bp.post("/posts/<post_id>/comments")
@onboarding_required
@async_handler
def comment_post(post_id):
    data, status = social_controller.add_comment("post", post_id)
    return _ok("Comment added.", data, status)


@social_bp.get("/pieces/<piece_id>/comments")
@async_handler
def list_piece_comments(piece_id):
    cursor = request.args.get("cursor")
    limit = min(int(request.args.get("limit", 50)), 100)
    data, status = social_controller.get_comments("piece", piece_id, cursor, limit)
    return _ok("OK", data, status)


@social_bp.get("/posts/<post_id>/comments")
@async_handler
def list_post_comments(post_id):
    cursor = request.args.get("cursor")
    limit = min(int(request.args.get("limit", 50)), 100)
    data, status = social_controller.get_comments("post", post_id, cursor, limit)
    return _ok("OK", data, status)
