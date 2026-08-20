from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from src.permission.exceptions import PermissionNotFoundError
from src.permission.models import Permission
from src.role.exceptions import RoleNotFoundError
from src.role.models import Role
from src.role.schema import RoleAddSchema, RoleUpdateSchema


class RoleService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Role:
        return await self.session.scalar(
            select(Role)
            .where(Role.id == id)
            .options(
                selectinload(Role.permissions).options(
                    joinedload(Permission.object),
                    joinedload(Permission.action),
                )
            )
        )

    async def get_all(self) -> list[Role]:
        return list((await self.session.scalars(select(Role))).all())

    async def add(self, payload: RoleAddSchema) -> Role:
        codes = set(payload.permissions)

        permissions = await self.__check_permission(codes=codes)

        role = Role(title=payload.title, description=payload.description)
        role.permissions = permissions

        self.session.add(role)
        await self.session.flush()
        return role

    async def update(self, id: int, payload: RoleUpdateSchema) -> Role:
        role = await self.session.scalar(select(Role).where(Role.id == id))

        if role is None:
            raise RoleNotFoundError(id=id)
        for field, value in (
            payload.model_dump(exclude_unset=True, exclude={"permissions"})
        ).items():
            setattr(role, field, value)

        if payload.permissions is not None:
            permissions = await self.__check_permission(codes=set(payload.permissions))
            role.permissions = permissions

        await self.session.flush()
        return role

    async def delete(self, id: int) -> None:
        role = await self.session.scalar(select(Role).where(Role.id == id))

        if role is None:
            raise RoleNotFoundError(id=id)

        await self.session.delete(role)

        await self.session.flush()

    async def __check_permission(self, codes: set[str]) -> list[Permission]:
        permissions = list(
            (
                await self.session.scalars(
                    select(Permission).where(Permission.code.in_(codes))
                )
            ).all()
        )

        if len(permissions) != len(codes):
            missing = codes - {p.code for p in permissions}
            raise PermissionNotFoundError(codes=sorted(missing))

        return permissions
