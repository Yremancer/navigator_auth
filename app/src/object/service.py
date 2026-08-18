from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.database.utils import get_or_raise
from src.object.exceptions import ObjectNotFoundError
from src.object.models import Object
from src.object.schema import ObjectAddSchema, ObjectUpdateSchema
from src.scope.exceptions import ScopeTypeNotFoundError
from src.scope.models import ScopeType


class ObjectService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Object]:
        return list(
            (
                await self.session.scalars(
                    select(Object)
                    .order_by(Object.sort_order)
                    .options(joinedload(Object.scope_type))
                )
            ).all()
        )

    async def add(self, payload: ObjectAddSchema) -> Object:
        await get_or_raise(
            self.session, ScopeType, payload.scope_type_code, ScopeTypeNotFoundError
        )

        new_object = Object(
            code=f"{payload.scope_type_code}.{payload.code}",
            title=payload.title,
            scope_type_code=payload.scope_type_code,
            sort_order=payload.sort_order,
        )

        if payload.sort_order is None:
            max_order = await self.session.scalar(
                select(func.max(Object.sort_order)).where(
                    Object.scope_type_code == payload.scope_type_code
                )
            )
            new_object.sort_order = (max_order or 0) + 1

        self.session.add(new_object)
        await self.session.flush()
        return new_object

    async def update(self, code: str, payload: ObjectUpdateSchema) -> Object:
        obj = await self.session.scalar(select(Object).where(Object.code == code))

        if obj is None:
            raise ObjectNotFoundError(code=code)

        for field, value in (payload.model_dump(exclude_unset=True)).items():
            setattr(obj, field, value)

        await self.session.flush()
        return obj

    async def delete(self, code: str) -> None:
        obj = await self.session.scalar(select(Object).where(Object.code == code))

        if obj is None:
            raise ObjectNotFoundError(code=code)

        await self.session.delete(obj)

        await self.session.flush()
