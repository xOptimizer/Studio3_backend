"""Notifications routes."""
from flask import Blueprint

from src.middlewares.auth_middleware import auth_required
from src.shared.utils.api_response import success_response
from src.shared.utils.async_handler import async_handler
from src.modules.notifications import notifications_controller

notifications_bp = Blueprint("notifications", __name__)


def _ok(message, data, status=200):
    resp, _ = success_response(message, data, status)
    return resp, status


@notifications_bp.get("")
@auth_required
@async_handler
def list_notifications():
    data, status = notifications_controller.list_for_me()
    return _ok("OK", data, status)


@notifications_bp.patch("/<notification_id>/read")
@auth_required
@async_handler
def mark_read(notification_id):
    data, status = notifications_controller.mark_read(notification_id)
    return _ok("Marked read.", data, status)


@notifications_bp.post("/read-all")
@auth_required
@async_handler
def mark_all_read():
    data, status = notifications_controller.mark_all_read()
    return _ok("All marked read.", data, status)


@notifications_bp.get("/unread-count")
@auth_required
@async_handler
def unread_count():
    data, status = notifications_controller.unread_count()
    return _ok("OK", data, status)
