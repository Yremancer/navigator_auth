from src.exceptions import NotFoundError


class ScopeTypeNotFoundError(NotFoundError):
    def __init__(self, **criteria):
        conditions = ", ".join(f"{k}={v!r}" for k, v in criteria.items())
        super().__init__(f"Scope type not found ({conditions})")
