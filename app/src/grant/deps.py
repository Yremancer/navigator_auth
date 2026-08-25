from typing import Annotated

from fastapi import Depends
from src.database.deps import SessionDep
from src.grant.service import GrantService


def get_grant_service(session: SessionDep) -> GrantService:
    return GrantService(session)


GrantServiceDep = Annotated[GrantService, Depends(get_grant_service)]
