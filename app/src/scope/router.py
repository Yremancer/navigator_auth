from fastapi import APIRouter, status
from src.scope.deps import ScopeTypeServiceDep
from src.scope.schema import (
    ScopeTypeAddSchema,
    ScopeTypeSchema,
    ScopeTypeTreeSchema,
    ScopeTypeUpdateSchema,
)

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_scope_types(service: ScopeTypeServiceDep) -> list[ScopeTypeSchema]:
    return await service.get_all()


@router.get("/tree", status_code=status.HTTP_200_OK)
async def get_scope_types_tree(
    service: ScopeTypeServiceDep,
) -> list[ScopeTypeTreeSchema]:
    return await service.get_tree()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_scope_types(
    service: ScopeTypeServiceDep, payload: ScopeTypeAddSchema
) -> ScopeTypeSchema:
    return await service.add(payload=payload)


@router.patch("/{code}", status_code=status.HTTP_200_OK)
async def update_scope_type(
    service: ScopeTypeServiceDep, code: str, payload: ScopeTypeUpdateSchema
) -> ScopeTypeSchema:
    return await service.update(code=code, payload=payload)


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scope_type(service: ScopeTypeServiceDep, code: str) -> None:
    await service.delete(code=code)
