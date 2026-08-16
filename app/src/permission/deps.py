from typing import Annotated

from fastapi import Depends
from src.database.deps import SessionDep
from src.permission.service import PermissionService


def get_permission_service(session: SessionDep) -> PermissionService:
    return PermissionService(session)


PermissionServiceDep = Annotated[PermissionService, Depends(get_permission_service)]
