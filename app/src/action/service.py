from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.action.models import Action
from src.action.schemas import ActionAddSchema


class ActionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_actions(self) -> list[Action]:
        return list((await self.session.scalars(select(Action))).all())

    async def add_action(self, data: ActionAddSchema) -> Action:
        new_action = Action(**data.model_dump(exclude_none=True))

        if data.sort_order is None:
            max_order = await self.session.scalar(select(func.max(Action.sort_order)))
            new_action.sort_order = (max_order or 0) + 1

        self.session.add(new_action)
        return new_action
