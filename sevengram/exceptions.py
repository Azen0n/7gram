class ValidationError(Exception):
    """Base Validation error."""


class BaseServiceError(Exception):
    """Base service error."""


class NotFoundError(BaseServiceError):
    """Object not found error."""
