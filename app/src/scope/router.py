from fastapi import APIRouter, status
from src.scope.deps import ScopeServiceDep, ScopeTypeServiceDep
from src.scope.schema import (
    ScopeAddSchema,
    ScopeSchema,
    ScopeTypeAddSchema,
    ScopeTypeSchema,
    ScopeTypeTreeSchema,
    ScopeTypeUpdateSchema,
)

scope_type_router = APIRouter()


@scope_type_router.get("/", status_code=status.HTTP_200_OK)
async def get_scope_types(service: ScopeTypeServiceDep) -> list[ScopeTypeSchema]:
    return await service.get_all()


@scope_type_router.get("/tree", status_code=status.HTTP_200_OK)
async def get_scope_types_tree(
    service: ScopeTypeServiceDep,
) -> list[ScopeTypeTreeSchema]:
    return await service.get_tree()


@scope_type_router.post("/", status_code=status.HTTP_201_CREATED)
async def add_scope_types(
    service: ScopeTypeServiceDep, payload: ScopeTypeAddSchema
) -> ScopeTypeSchema:
    return await service.add(payload=payload)


@scope_type_router.patch("/{code}", status_code=status.HTTP_200_OK)
async def update_scope_type(
    service: ScopeTypeServiceDep, code: str, payload: ScopeTypeUpdateSchema
) -> ScopeTypeSchema:
    return await service.update(code=code, payload=payload)


@scope_type_router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scope_type(service: ScopeTypeServiceDep, code: str) -> None:
    await service.delete(code=code)


scope_router = APIRouter()


@scope_router.get("/", status_code=status.HTTP_200_OK)
async def get_scope(
    service: ScopeServiceDep, q: str | None = None, scope_type_code: str | None = None
) -> list[ScopeSchema]:
    return await service.get_all(q=q,scope_type_code=scope_type_code)


@scope_router.post("/", status_code=status.HTTP_201_CREATED)
async def add_scope(service: ScopeServiceDep, payload: ScopeAddSchema) -> ScopeSchema:
    return await service.add(payload=payload)


@scope_router.delete("/{scope_type}/{scope_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scope(
    service: ScopeServiceDep, scope_type: str, scope_id: int
) -> None:
    await service.delete(scope_type=scope_type, scope_id=scope_id)
