from typing import Annotated

from fastapi import Depends
from src.action.service import ActionService
from src.database.deps import SessionDep


def get_action_service(session: SessionDep) -> ActionService:
    return ActionService(session)


ActionServiceDep = Annotated[ActionService, Depends(get_action_service)]
