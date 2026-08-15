from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.action.exceptions import ActionNotFoundError
from src.action.models import Action
from src.action.schemas import ActionAddSchema, ActionUpdateSchema


class ActionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Action]:
        return list(
            (
                await self.session.scalars(select(Action).order_by(Action.sort_order))
            ).all()
        )

    async def add(self, payload: ActionAddSchema) -> Action:
        new_action = Action(**payload.model_dump(exclude_none=True))

        if payload.sort_order is None:
            max_order = await self.session.scalar(select(func.max(Action.sort_order)))
            new_action.sort_order = (max_order or 0) + 1

        self.session.add(new_action)
        await self.session.flush()
        return new_action

    async def update(self, code: str, payload: ActionUpdateSchema) -> Action:
        action = await self.session.scalar(select(Action).where(Action.code == code))

        if action is None:
            raise ActionNotFoundError(code=code)

        for field, value in (payload.model_dump(exclude_unset=True)).items():
            setattr(action, field, value)

        await self.session.flush()

        return action

    async def delete(self, code: str) -> None:
        action = await self.session.scalar(select(Action).where(Action.code == code))

        if action is None:
            raise ActionNotFoundError(code=code)

        await self.session.delete(action)

        await self.session.flush()
