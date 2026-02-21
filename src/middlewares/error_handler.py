"""Global exception handler: AppError -> status_code + message; else 500 + generic message."""
from flask import jsonify

from src.shared.utils.app_error import AppError
from src.shared.utils.api_response import error_response, internal_error_response
from src.shared.utils.messages import INTERNAL_SERVER_ERROR
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


def register_error_handler(app):
    @app.errorhandler(AppError)
    def handle_app_error(e: AppError):
        return error_response(e.message, e.status_code)

    @app.errorhandler(Exception)
    def handle_unhandled(e: Exception):
        logger.exception("Unhandled exception: %s", e)
        return internal_error_response()
