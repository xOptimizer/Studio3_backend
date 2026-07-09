"""Orders routes."""
from flask import Blueprint

from src.middlewares.auth_middleware import auth_required
from src.shared.utils.api_response import success_response
from src.shared.utils.async_handler import async_handler
from src.modules.orders import orders_controller

orders_bp = Blueprint("orders", __name__)


def _ok(message, data, status=200):
    resp, _ = success_response(message, data, status)
    return resp, status


@orders_bp.get("/<order_id>")
@auth_required
@async_handler
def get_order(order_id):
    data, status = orders_controller.get_detail(order_id)
    return _ok("OK", data, status)


@orders_bp.post("/<order_id>/confirm")
@auth_required
@async_handler
def confirm(order_id):
    data, status = orders_controller.confirm(order_id)
    return _ok("Order confirmed.", data, status)


@orders_bp.patch("/<order_id>")
@auth_required
@async_handler
def patch(order_id):
    data, status = orders_controller.patch(order_id)
    return _ok("Order updated.", data, status)
