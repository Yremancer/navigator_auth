from typing import Annotated

from fastapi import Depends
from src.database.deps import SessionDep
from src.object.service import ObjectService


def get_object_service(session: SessionDep) -> ObjectService:
    return ObjectService(session)


ObjectServiceDep = Annotated[ObjectService, Depends(get_object_service)]
