from typing import Annotated

from fastapi import Depends
from src.database.deps import SessionDep
from src.role.service import RoleService


def get_role_service(session: SessionDep) -> RoleService:
    return RoleService(session)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
