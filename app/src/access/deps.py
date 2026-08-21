from typing import Annotated

from fastapi import Depends
from src.access.exceptions import PermissionDeniedError
from src.access.service import AccessService
from src.authentication.deps import CurrentUser
from src.database.deps import SessionDep
from src.object.service import ObjectService
from src.setting import settings


def get_access_service(session: SessionDep) -> ObjectService:
    return AccessService(session)


AccessServiceDep = Annotated[AccessService, Depends(get_access_service)]


def require(permission: str):
    async def checker(
        current_user: CurrentUser,
        service: AccessServiceDep,
    ) -> None:
        if not await service.can(current_user.id, permission, settings.SYSTEM_SCOPE_ID):
            raise PermissionDeniedError(permission=permission)

    return Depends(checker)
