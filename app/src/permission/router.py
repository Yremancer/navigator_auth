from fastapi import APIRouter, status
from src.permission.deps import PermissionServiceDep
from src.permission.schema import (
    PermissionAddedSchema,
    PermissionAddSchema,
    PermissionSchema,
)

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_object(service: PermissionServiceDep) -> list[PermissionSchema]:
    return await service.get_all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_object(
    service: PermissionServiceDep, payload: PermissionAddSchema
) -> PermissionAddedSchema:
    return await service.add(payload=payload)


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_object(service: PermissionServiceDep, code: str) -> None:
    await service.delete(code=code)
