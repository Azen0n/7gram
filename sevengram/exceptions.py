class ValidationError(Exception):
    """Base Validation error."""


class BaseServiceError(Exception):
    """Base service error."""


class NotFoundError(BaseServiceError):
    """Object not found error."""


class ApiError(Exception):
    """External API error."""
