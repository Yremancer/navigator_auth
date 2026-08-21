from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.database.utils import get_or_raise
from src.object.models import Object
from src.permission.models import Permission
from src.scope.exceptions import ScopeNotFoundError, ScopeTypeNotFoundError
from src.scope.models import Scope, ScopeType
from src.scope.schema import ScopeAddSchema, ScopeTypeAddSchema, ScopeTypeUpdateSchema
from src.setting import settings


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

    async def get_tree(self) -> list[ScopeType]:
        return list(
            (
                await self.session.scalars(
                    select(ScopeType)
                    .options(
                        selectinload(ScopeType.objects)
                        .selectinload(Object.permissions)
                        .joinedload(Permission.action)
                    )
                    .order_by(ScopeType.sort_order)
                )
            )
            .unique()
            .all()
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
        scope_type = await get_or_raise(
            session=self.session,
            model=ScopeType,
            pk=code,
            exc=ScopeTypeNotFoundError,
        )

        for field, value in (payload.model_dump(exclude_unset=True)).items():
            setattr(scope_type, field, value)

        await self.session.flush()
        return scope_type

    async def delete(self, code: str) -> None:
        scope_type = await get_or_raise(
            session=self.session,
            model=ScopeType,
            pk=code,
            exc=ScopeTypeNotFoundError,
        )

        await self.session.delete(scope_type)

        await self.session.flush()


class ScopeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, q: str | None, scope_type_code: str | None) -> list[Scope]:
        stmt = select(Scope)

        if q:
            stmt = stmt.where(Scope.title.ilike(f"%{q}%"))

        if scope_type_code is not None:
            stmt = stmt.where(Scope.scope_type == scope_type_code)

        return list((await self.session.scalars(stmt)).all())

    async def add(self, payload: ScopeAddSchema) -> Scope:
        await get_or_raise(
            session=self.session,
            model=ScopeType,
            pk=payload.scope_type,
            exc=ScopeTypeNotFoundError,
        )

        if payload.parent_type is not None:
            await get_or_raise(
                session=self.session,
                model=Scope,
                pk=(payload.parent_type, payload.parent_id),
                exc=ScopeNotFoundError,
            )
        # TODO Проверку на циклы

        new_scope = Scope(**payload.model_dump(exclude_none=True))

        self.session.add(new_scope)
        await self.session.flush()
        return new_scope

    async def delete(
        self, scope_type: str, scope_id: int = settings.SYSTEM_SCOPE_ID
    ) -> None:
        scope = await get_or_raise(
            session=self.session,
            model=Scope,
            pk=(scope_type, scope_id),
            exc=ScopeNotFoundError,
        )

        await self.session.delete(scope)

        await self.session.flush()
