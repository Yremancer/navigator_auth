from src.exceptions import NotFoundError


class ObjectNotFoundError(NotFoundError):
    def __init__(self, **criteria):
        conditions = ", ".join(f"{k}={v!r}" for k, v in criteria.items())
        super().__init__(f"Object not found ({conditions})")
