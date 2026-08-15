from fastapi import APIRouter, status
from src.action.deps import ActionServiceDep
from src.action.schemas import ActionAddSchema, ActionSchema, ActionUpdateSchema

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_actions(service: ActionServiceDep) -> list[ActionSchema]:
    return await service.get_all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_action(
    service: ActionServiceDep, payload: ActionAddSchema
) -> ActionSchema:
    return await service.add(payload=payload)


@router.patch("/{code}", status_code=status.HTTP_200_OK)
async def update_action(
    service: ActionServiceDep, code: str, payload: ActionUpdateSchema
) -> ActionSchema:
    return await service.update(code=code, payload=payload)


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action(service: ActionServiceDep, code: str) -> None:
    await service.delete(code=code)
