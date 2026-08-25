from typing import Annotated

from fastapi import Depends
from src.access.repository import AccessRepository
from src.access.service import AccessService
from src.database.deps import SessionDep


def get_access_repository(session: SessionDep) -> AccessRepository:
    return AccessRepository(session)


AccessRepositoryDep = Annotated[AccessRepository, Depends(get_access_repository)]


def get_access_service(repo: AccessRepositoryDep) -> AccessService:
    return AccessService(repo)


AccessServiceDep = Annotated[AccessService, Depends(get_access_service)]
