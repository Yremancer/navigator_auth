from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.scope.exceptions import ScopeTypeNotFoundError
from src.scope.models import ScopeType
from src.scope.schema import ScopeTypeAddSchema, ScopeTypeUpdateSchema


class ScopeTypeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[ScopeType]:
        return list(
            (
                await self.session.scalars(
                    select(ScopeType).order_by(ScopeType.sort_order)
                )
            ).all()
        )

    async def add(self, payload: ScopeTypeAddSchema) -> ScopeType:
        new_scope_type = ScopeType(**payload.model_dump(exclude_none=True))

        if payload.sort_order is None:
            max_order = await self.session.scalar(
                select(func.max(ScopeType.sort_order))
            )
            new_scope_type.sort_order = (max_order or 0) + 1

        self.session.add(new_scope_type)
        await self.session.flush()
        return new_scope_type

    async def update(self, code: str, payload: ScopeTypeUpdateSchema) -> ScopeType:
        scope_type = self.session.scalar(
            select(ScopeType).where(ScopeType.code == code)
        )

        if scope_type is None:
            raise ScopeTypeNotFoundError(code=code)

        for field, value in (payload.model_dump(exclude_unset=True)).items():
            setattr(scope_type, field, value)

        await self.session.flush()
        return scope_type

    async def delete(self, code: str) -> None:
        scope_type = await self.session.scalar(
            select(ScopeType).where(ScopeType.code == code)
        )

        if scope_type is None:
            raise ScopeTypeNotFoundError(code=code)

        await self.session.delete(scope_type)

        await self.session.flush()
