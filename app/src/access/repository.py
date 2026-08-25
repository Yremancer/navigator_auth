from sqlalchemy import Select, literal, select, union, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from src.assignment.models import Assignment
from src.grant.models import Grant
from src.role.models import Role, role_permission
from src.scope.models import Scope
from src.user.models import User


class AccessRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def is_active(self, user_id: int) -> bool:
        return bool(
            await self._session.scalar(select(User.is_active).where(User.id == user_id))
        )

    async def has_super_role(self, user_id: int) -> bool:
        stmt = (
            select(Assignment.id)
            .join(Role, Role.id == Assignment.role_id)
            .where(Assignment.user_id == user_id, Role.is_super.is_(True))
            .limit(1)
        )
        return await self._session.scalar(stmt) is not None

    async def list_scope_ids(self, scope_type: str) -> list[int]:
        rows = await self._session.scalars(
            select(Scope.scope_id).where(Scope.scope_type == scope_type)
        )
        return sorted(rows.all())

    async def find_granted(
        self, user_id: int, targets: set[tuple[str, str, int]]
    ) -> set[tuple[str, int]]:
        vertical = self._expand(self._targets(targets), "vertical")
        sources = self._sources(user_id)

        stmt = (
            select(vertical.c.permission, vertical.c.origin_id)
            .join(
                sources,
                (sources.c.permission == vertical.c.permission)
                & (sources.c.scope_type == vertical.c.scope_type)
                & (sources.c.scope_id == vertical.c.scope_id),
            )
            .distinct()
        )

        rows = await self._session.execute(stmt)
        return {(permission, origin_id) for permission, origin_id in rows}

    async def find_reachable(
        self,
        user_id: int,
        permissions: set[str] | None = None,
        scope_types: set[str] | None = None,
    ) -> list[tuple[str, str, int]]:
        reachable = self._expand(self._sources(user_id, permissions), "reachable")

        stmt = select(
            reachable.c.permission,
            reachable.c.scope_type,
            reachable.c.scope_id,
        ).distinct()

        if scope_types is not None:
            stmt = stmt.where(reachable.c.scope_type.in_(scope_types))

        rows = await self._session.execute(stmt)
        return [
            (permission, scope_type, scope_id)
            for permission, scope_type, scope_id in rows
        ]

    async def list_user_roles(self, user_id: int):
        stmt = (
            select(
                Role.id,
                Role.title,
                Assignment.scope_type_code.label("scope_type"),
                Assignment.scope_id,
            )
            .join(Assignment, Assignment.role_id == Role.id)
            .where(Assignment.user_id == user_id)
            .order_by(Role.title)
        )
        return (await self._session.execute(stmt)).all()

    @staticmethod
    def _sources(user_id: int, permissions: set[str] | None = None):
        from_roles = (
            select(
                role_permission.c.permission_code.label("permission"),
                Assignment.scope_type_code.label("scope_type"),
                Assignment.scope_id.label("scope_id"),
            )
            .select_from(Assignment)
            .join(role_permission, role_permission.c.role_id == Assignment.role_id)
            .where(Assignment.user_id == user_id)
        )

        from_grants = select(
            Grant.permission_code.label("permission"),
            Grant.scope_type_code.label("scope_type"),
            Grant.scope_id.label("scope_id"),
        ).where(Grant.user_id == user_id)

        if permissions is not None:
            from_roles = from_roles.where(
                role_permission.c.permission_code.in_(permissions)
            )
            from_grants = from_grants.where(Grant.permission_code.in_(permissions))

        return union(from_roles, from_grants).subquery()

    @staticmethod
    def _targets(targets: set[tuple[str, str, int]]):
        parts = [
            select(
                literal(permission).label("permission"),
                literal(scope_type).label("scope_type"),
                literal(scope_id).label("scope_id"),
            )
            for permission, scope_type, scope_id in targets
        ]
        return union_all(*parts).subquery()

    @classmethod
    def _expand(cls, origins, name: str):
        anchor = cls._anchor(origins)
        up = cls._walk(anchor, f"{name}_up", up=True)
        down = cls._walk(anchor, f"{name}_down", up=False)
        return union(cls._visible(up), cls._visible(down)).subquery(name)

    @staticmethod
    def _anchor(origins) -> Select:
        return select(
            Scope.scope_type,
            Scope.scope_id,
            Scope.parent_type,
            Scope.parent_id,
            origins.c.permission,
            origins.c.scope_id.label("origin_id"),
        ).join(
            origins,
            (Scope.scope_type == origins.c.scope_type)
            & (Scope.scope_id == origins.c.scope_id),
        )

    @staticmethod
    def _walk(anchor: Select, name: str, *, up: bool):
        cte = anchor.cte(name, recursive=True)
        node = aliased(Scope)

        edge = (
            (node.scope_type == cte.c.parent_type) & (node.scope_id == cte.c.parent_id)
            if up
            else (node.parent_type == cte.c.scope_type)
            & (node.parent_id == cte.c.scope_id)
        )

        step = select(
            node.scope_type,
            node.scope_id,
            node.parent_type,
            node.parent_id,
            cte.c.permission,
            cte.c.origin_id,
        ).join(cte, edge)

        return cte.union(step)

    @staticmethod
    def _visible(cte):
        return select(
            cte.c.scope_type,
            cte.c.scope_id,
            cte.c.permission,
            cte.c.origin_id,
        )
