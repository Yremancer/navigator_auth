from fastapi import APIRouter, status
from src.user.deps import UserServiceDep
from src.user.schema import UserSchema

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(service: UserServiceDep) -> list[UserSchema]:
    return await service.get_all()
