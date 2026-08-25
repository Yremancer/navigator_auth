from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.database.utils import get_or_raise
from src.grant.exceptions import GrantNotFoundError
from src.grant.models import Grant
from src.grant.schema import GrantAddSchema
from src.permission.exceptions import PermissionNotFoundError
from src.permission.models import Permission
from src.scope.exceptions import ScopeNotFoundError, ScopeTypeNotFoundError
from src.scope.models import Scope, ScopeType
from src.user.exceptions import UserNotFoundError
from src.user.models import User


class GrantService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Grant]:
        return list(
            (
                await self.session.scalars(
                    select(Grant).options(
                        joinedload(Grant.user),
                        joinedload(Grant.scope_type),
                        joinedload(Grant.granted_by),
                    )
                )
            ).all()
        )

    async def add(self, payload: GrantAddSchema, granted_by: User) -> Grant:
        user = await get_or_raise(
            session=self.session, model=User, pk=payload.user_id, exc=UserNotFoundError
        )
        scope_type = await get_or_raise(
            session=self.session,
            model=ScopeType,
            pk=payload.scope_type_code,
            exc=ScopeTypeNotFoundError,
        )
        permission = await get_or_raise(
            session=self.session,
            model=Permission,
            pk=payload.permission_code,
            exc=PermissionNotFoundError,
        )
        scope = await get_or_raise(
            session=self.session,
            model=Scope,
            pk=(payload.scope_type_code, payload.scope_id),
            exc=ScopeNotFoundError,
        )

        new_grant = Grant(**payload.model_dump(exclude_none=True))
        new_grant.user = user
        new_grant.permission = permission
        new_grant.scope_type = scope_type
        new_grant.granted_by = granted_by

        self.session.add(new_grant)
        await self.session.flush()
        return new_grant

    async def delete(self, id: int) -> None:
        grant = await get_or_raise(
            session=self.session,
            model=Grant,
            pk=id,
            exc=GrantNotFoundError,
        )

        await self.session.delete(grant)

        await self.session.flush()
