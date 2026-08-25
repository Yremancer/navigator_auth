from fastapi import APIRouter, status
from src.authentication.deps import CurrentUser
from src.grant.deps import GrantServiceDep
from src.grant.schema import GrantAddSchema, GrantSchema

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_grant(service: GrantServiceDep) -> list[GrantSchema]:
    return await service.get_all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_grant(
    service: GrantServiceDep,
    payload: GrantAddSchema,
    current_user: CurrentUser,
) -> GrantSchema:
    return await service.add(payload=payload, granted_by=current_user)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grant(service: GrantServiceDep, id: int) -> None:
    await service.delete(id=id)
