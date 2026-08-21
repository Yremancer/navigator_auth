from typing import Annotated

from fastapi import Depends
from src.database.deps import SessionDep
from src.scope.service import ScopeService, ScopeTypeService


def get_scope_type_service(session: SessionDep) -> ScopeTypeService:
    return ScopeTypeService(session)


ScopeTypeServiceDep = Annotated[ScopeTypeService, Depends(get_scope_type_service)]


def get_scope_service(session: SessionDep) -> ScopeService:
    return ScopeService(session)


ScopeServiceDep = Annotated[ScopeService, Depends(get_scope_service)]
