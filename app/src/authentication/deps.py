from typing import Annotated

from fastapi import Depends
from src.authentication.router import get_claims
from src.user.deps import UserServiceDep
from src.user.exceptions import UserInactiveError, UserNotFoundError
from src.user.models import User


async def get_current_user(
    claims: Annotated[dict, Depends(get_claims)],
    service: UserServiceDep,
) -> User:
    user = await service.get_by_external_id(external_id=claims["sub"])
    if user is None:
        raise UserNotFoundError(external_id=claims["sub"])
    if not user.is_active:
        raise UserInactiveError(id=user.id)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
