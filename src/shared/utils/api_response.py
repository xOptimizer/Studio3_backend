"""Success and error response helpers - same shape as reference."""

from flask import jsonify
from typing import Any, Optional

from src.shared.utils.messages import INTERNAL_SERVER_ERROR


def success_response(
    message: str,
    data: Any = None,
    status_code: int = 200,
):
    """Return JSON: { success: true, message, data? }."""
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status_code


def error_response(
    message: str,
    status_code: int = 500,
):
    """Return JSON: { success: false, message }."""
    return jsonify({"success": False, "message": message}), status_code


def internal_error_response():
    """Generic 500 response."""
    return error_response(INTERNAL_SERVER_ERROR, 500)
