from src.exceptions import ConflictError, NotFoundError


class ScopeTypeNotFoundError(NotFoundError):
    def __init__(self, **criteria):
        conditions = ", ".join(f"{k}={v!r}" for k, v in criteria.items())
        super().__init__(f"Scope type not found ({conditions})")


class ScopeNotFoundError(NotFoundError):
    def __init__(self, **criteria):
        conditions = ", ".join(f"{k}={v!r}" for k, v in criteria.items())
        super().__init__(f"Scope not found ({conditions})")


class ScopeAlreadyExistsError(ConflictError):
    def __init__(self, scope_type: str, scope_id: int):
        super().__init__(f"Scope already exists ({scope_type}:{scope_id})")
