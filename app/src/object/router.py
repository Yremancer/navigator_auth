from fastapi import APIRouter, status
from src.object.deps import ObjectServiceDep
from src.object.schema import (
    ObjectAddedSchema,
    ObjectAddSchema,
    ObjectSchema,
    ObjectUpdateSchema,
)

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_object(service: ObjectServiceDep) -> list[ObjectSchema]:
    return await service.get_all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_object(
    service: ObjectServiceDep, payload: ObjectAddSchema
) -> ObjectAddedSchema:
    return await service.add(payload=payload)


@router.patch("/{code}", status_code=status.HTTP_200_OK)
async def update_object(
    service: ObjectServiceDep, code: str, payload: ObjectUpdateSchema
) -> ObjectSchema:
    return await service.update(code=code, payload=payload)


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_object(service: ObjectServiceDep, code: str) -> None:
    await service.delete(code=code)
