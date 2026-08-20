from src.exceptions import AppError, NotFoundError


class UserNotFoundError(NotFoundError):
    def __init__(self, **criteria):
        conditions = ", ".join(f"{k}={v!r}" for k, v in criteria.items())
        super().__init__(f"User not found ({conditions})")


class UserInactiveError(AppError):
    status_code = 403
    detail = "User account is inactive"
