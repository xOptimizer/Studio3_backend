"""Inquiries routes."""
from flask import Blueprint

from src.middlewares.auth_middleware import auth_required, onboarding_required
from src.shared.utils.api_response import success_response
from src.shared.utils.async_handler import async_handler
from src.modules.inquiries import inquiries_controller

inquiries_bp = Blueprint("inquiries", __name__)


def _ok(message, data, status=200):
    resp, _ = success_response(message, data, status)
    return resp, status


@inquiries_bp.get("")
@auth_required
@async_handler
def list_inbox():
    data, status = inquiries_controller.list_inbox()
    return _ok("OK", data, status)


@inquiries_bp.get("/<inquiry_id>")
@auth_required
@async_handler
def get_thread(inquiry_id):
    data, status = inquiries_controller.get_thread(inquiry_id)
    return _ok("OK", data, status)


@inquiries_bp.post("")
@onboarding_required
@async_handler
def create_inquiry():
    data, status = inquiries_controller.create_inquiry()
    return _ok("Inquiry sent.", data, status)


@inquiries_bp.post("/<inquiry_id>/messages")
@onboarding_required
@async_handler
def reply(inquiry_id):
    data, status = inquiries_controller.reply(inquiry_id)
    return _ok("Message sent.", data, status)


@inquiries_bp.patch("/<inquiry_id>/read")
@auth_required
@async_handler
def mark_read(inquiry_id):
    data, status = inquiries_controller.mark_read(inquiry_id)
    return _ok("Marked read.", data, status)
