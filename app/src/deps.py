from fastapi import Depends
from src.access.deps import AccessServiceDep
from src.access.exceptions import PermissionDeniedError
from src.authentication.deps import CurrentUser
from src.setting import settings


def require(permission: str):
    async def checker(
        current_user: CurrentUser,
        service: AccessServiceDep,
    ) -> None:
        if not await service.can(current_user.id, permission, settings.SYSTEM_SCOPE_ID):
            raise PermissionDeniedError(permission=permission)

    return Depends(checker)
