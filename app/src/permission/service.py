from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.action.exceptions import ActionNotFoundError
from src.action.models import Action
from src.database.utils import get_or_raise
from src.object.exceptions import ObjectNotFoundError
from src.object.models import Object
from src.permission.exceptions import PermissionNotFoundError
from src.permission.models import Permission
from src.permission.schema import PermissionAddSchema


class PermissionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Permission]:
        return list(
            (
                await self.session.scalars(
                    select(Permission).options(
                        joinedload(Permission.object), joinedload(Permission.action)
                    )
                )
            ).all()
        )

    async def add(self, payload: PermissionAddSchema) -> Permission:
        await get_or_raise(
            self.session, Object, payload.object_code, ObjectNotFoundError
        )
        await get_or_raise(
            self.session, Action, payload.action_code, ActionNotFoundError
        )

        permission = Permission(
            code=f"{payload.object_code}.{payload.action_code}",
            object_code=payload.object_code,
            action_code=payload.action_code,
        )

        self.session.add(permission)
        await self.session.flush()
        return permission

    async def delete(self, code: str) -> None:
        permission = await get_or_raise(
            self.session, Permission, code, PermissionNotFoundError
        )

        await self.session.delete(permission)

        await self.session.flush()
