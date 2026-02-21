"""Decorator that catches exceptions and passes to Flask error handler (next(err) style)."""
from functools import wraps
from typing import Callable

from src.shared.utils.app_error import AppError
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


def async_handler(f: Callable):
    """Wrap route/controller so exceptions become AppError or 500 and are handled globally."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppError:
            raise
        except Exception as e:
            logger.exception("Unhandled error in %s: %s", f.__name__, e)
            raise AppError(
                "Something went wrong.",
                status_code=500,
                is_operational=False,
            )

    return wrapper
