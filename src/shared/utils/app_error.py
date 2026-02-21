"""Custom exception with status_code and is_operational for global error handler."""


class AppError(Exception):
    """Raised for operational HTTP errors (4xx, controlled 5xx)."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        is_operational: bool = True,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.is_operational = is_operational
