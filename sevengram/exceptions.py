class ValidationError(Exception):
    """Base Validation error."""


class ServiceError(Exception):
    """Service error."""


class NotFoundError(ServiceError):
    """Object not found error."""


class ApiError(Exception):
    """External API error."""
