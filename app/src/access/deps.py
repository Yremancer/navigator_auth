from typing import Annotated

from fastapi import Depends
from src.access.service import AccessService
from src.database.deps import SessionDep
from src.object.service import ObjectService


def get_access_service(session: SessionDep) -> ObjectService:
    return AccessService(session)


AccessServiceDep = Annotated[AccessService, Depends(get_access_service)]
