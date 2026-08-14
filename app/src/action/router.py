from fastapi import APIRouter
from src.action.deps import ActionServiceDep
from src.action.schemas import ActionAddSchema, ActionSchema

router = APIRouter()


@router.get("/", response_model=list[ActionSchema])
async def get_actions(service: ActionServiceDep):
    return await service.get_actions()


@router.post("/")
async def add_action(service: ActionServiceDep, data: ActionAddSchema):
    await service.add_action(data=data)
