from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
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
        new_permission = Permission(**payload.model_dump(exclude_none=True))

        new_permission.code = f"{payload.object_code}.{payload.action_code}"

        self.session.add(new_permission)
        await self.session.flush()
        return new_permission

    async def delete(self, code: str) -> None:
        permission = await self.session.scalar(
            select(Permission).where(Permission.code == code)
        )

        if permission is None:
            raise PermissionNotFoundError(code=code)

        await self.session.delete(permission)

        await self.session.flush()
