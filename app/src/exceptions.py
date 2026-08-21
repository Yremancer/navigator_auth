class AppError(Exception):
    status_code = 500
    detail = "Internal error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    detail = "Not found"


class ConflictError(AppError):
    status_code = 409
    detail = "Conflict"


class ForbiddenError(AppError):
    status_code = 403
    detail = "Forbidden"
