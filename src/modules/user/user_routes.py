"""User and media routes."""
import uuid

from flask import Blueprint, g

from src.middlewares.auth_middleware import auth_required, optional_auth
from src.shared.utils.api_response import success_response
from src.shared.utils.async_handler import async_handler
from src.modules.user import user_controller
from src.modules.media import media_controller
from src.modules.pieces import pieces_controller
from src.modules.posts import posts_controller

user_bp = Blueprint("user", __name__)
media_bp = Blueprint("media", __name__)


def _ok(message, data, status=200):
    resp, _ = success_response(message, data, status)
    return resp, status


@user_bp.get("/me")
@auth_required
@async_handler
def get_me():
    data, status = user_controller.get_me()
    return _ok("OK", data, status)


@user_bp.patch("/me")
@auth_required
@async_handler
def patch_me():
    data, status = user_controller.patch_me()
    return _ok("Profile updated.", data, status)


@user_bp.patch("/me/username")
@auth_required
@async_handler
def patch_username():
    data, status = user_controller.patch_username()
    return _ok("Username updated.", data, status)


@user_bp.patch("/me/role")
@auth_required
@async_handler
def patch_role():
    data, status = user_controller.patch_role()
    return _ok("Role updated.", data, status)


@user_bp.post("/me/onboarding/preferences")
@auth_required
@async_handler
def onboarding_preferences():
    data, status = user_controller.onboarding_preferences()
    return _ok("Preferences saved.", data, status)


@user_bp.post("/me/onboarding/photos")
@auth_required
@async_handler
def onboarding_photos():
    data, status = user_controller.onboarding_photos()
    return _ok("Photos saved.", data, status)


@user_bp.post("/me/onboarding/complete")
@auth_required
@async_handler
def onboarding_complete():
    data, status = user_controller.onboarding_complete()
    return _ok("Onboarding complete.", data, status)


@user_bp.post("/me/seller/enable")
@auth_required
@async_handler
def seller_enable():
    data, status = user_controller.seller_enable()
    return _ok("Seller mode enabled.", data, status)


@user_bp.post("/me/seller/disable")
@auth_required
@async_handler
def seller_disable():
    data, status = user_controller.seller_disable()
    return _ok("Seller mode disabled.", data, status)


@user_bp.get("/me/seller")
@auth_required
@async_handler
def seller_status():
    data, status = user_controller.seller_status()
    return _ok("OK", data, status)


@user_bp.get("/me/seller/analytics")
@auth_required
@async_handler
def seller_analytics():
    data, status = user_controller.seller_analytics()
    return _ok("OK", data, status)


@user_bp.get("/me/saved/pieces")
@auth_required
@async_handler
def saved_pieces():
    data, status = pieces_controller.list_saved_for_me(uuid.UUID(g.user["id"]))
    return _ok("OK", data, status)


@user_bp.get("/me/saved/posts")
@auth_required
@async_handler
def saved_posts():
    data, status = posts_controller.list_saved_for_me(uuid.UUID(g.user["id"]))
    return _ok("OK", data, status)


@user_bp.get("/<username>")
@optional_auth
@async_handler
def public_profile(username):
    data, status = user_controller.get_public_profile(username)
    return _ok("OK", data, status)


@media_bp.post("/presign")
@auth_required
@async_handler
def presign():
    data, status = media_controller.presign()
    return _ok("Presigned URL generated.", data, status)
