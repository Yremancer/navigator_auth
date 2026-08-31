from fastapi import APIRouter, status
from src.role.deps import RoleServiceDep
from src.role.schema import (
    RoleAddSchema,
    RoleDetailSchema,
    RoleListSchema,
    RoleUpdateSchema,
)

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_roles(service: RoleServiceDep) -> list[RoleListSchema]:
    return await service.get_all()


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_role(service: RoleServiceDep, id: int) -> RoleDetailSchema:
    return await service.get_by_id(id=id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_role(service: RoleServiceDep, payload: RoleAddSchema) -> RoleDetailSchema:
    return await service.add(payload=payload)


@router.patch("/{id}", status_code=status.HTTP_200_OK)
async def update_role(
    service: RoleServiceDep, id: int, payload: RoleUpdateSchema
) -> RoleDetailSchema:
    return await service.update(id=id, payload=payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(service: RoleServiceDep, id: int) -> None:
    await service.delete(id=id)
