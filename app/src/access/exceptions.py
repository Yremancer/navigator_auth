from src.exceptions import ForbiddenError


class PermissionDeniedError(ForbiddenError):
    def __init__(self, permission: str, scope_id: int | None = None) -> None:
        self.permission = permission
        self.scope_id = scope_id
        super().__init__(f"Permission {permission!r} denied")
