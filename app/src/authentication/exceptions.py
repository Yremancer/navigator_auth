from src.exceptions import NotAuthenticatedError


class InvalidTokenError(NotAuthenticatedError):
    detail = "Invalid token"


class RefreshFailedError(NotAuthenticatedError):
    detail = "Refresh failed"
