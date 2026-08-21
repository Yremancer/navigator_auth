from sqlalchemy import literal, select, union, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from src.access.schema import CheckResult, PermissionCheck, ScopeQuery, ScopeResult
from src.assignment.models import Assignment
from src.role.models import Role, role_permission
from src.scope.models import Scope
from src.setting import settings
from src.user.models import User


class AccessService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_batch(
        self, user_id: int, checks: list[PermissionCheck]
    ) -> list[CheckResult]:
        if not await self._is_active(user_id):
            return [CheckResult(**c.model_dump(), allowed=False) for c in checks]

        if await self._is_superuser(user_id):
            return [CheckResult(**c.model_dump(), allowed=True) for c in checks]

        granted = await self._find_granted(user_id, checks)
        return [
            CheckResult(**c.model_dump(), allowed=(c.permission, c.scope_id) in granted)
            for c in checks
        ]

    async def can(
        self, user_id: int, permission: str, scope_id: int = settings.SYSTEM_SCOPE_ID
    ) -> bool:
        check = PermissionCheck(permission=permission, scope_id=scope_id)
        (result,) = await self.check_batch(user_id, [check])
        return result.allowed

    async def _is_active(self, user_id: int) -> bool:
        return bool(
            await self.session.scalar(select(User.is_active).where(User.id == user_id))
        )

    async def _is_superuser(self, user_id: int) -> bool:
        stmt = (
            select(Assignment.id)
            .join(Role, Role.id == Assignment.role_id)
            .where(Assignment.user_id == user_id, Role.is_super.is_(True))
            .limit(1)
        )
        return await self.session.scalar(stmt) is not None

    async def _find_granted(
        self, user_id: int, checks: list[PermissionCheck]
    ) -> set[tuple[str, int]]:
        targets = {(c.permission, c.scope_id) for c in checks}
        vertical = self._build_vertical(targets)

        stmt = (
            select(vertical.c.target_permission, vertical.c.target_scope_id)
            .select_from(Assignment)
            .join(
                vertical,
                (vertical.c.scope_type == Assignment.scope_type_code)
                & (vertical.c.scope_id == Assignment.scope_id),
            )
            .join(role_permission, role_permission.c.role_id == Assignment.role_id)
            .where(
                Assignment.user_id == user_id,
                role_permission.c.permission_code == vertical.c.target_permission,
            )
            .distinct()
        )

        rows = await self.session.execute(stmt)
        return {(permission, scope_id) for permission, scope_id in rows}

    def _recursive_side(self, anchor, name: str, labels: tuple[str, ...], *, up: bool):
        cte = anchor.cte(name, recursive=True)
        node = aliased(Scope)

        condition = (
            (
                (node.scope_type == cte.c.parent_type)
                & (node.scope_id == cte.c.parent_id)
            )
            if up
            else (
                (node.parent_type == cte.c.scope_type)
                & (node.parent_id == cte.c.scope_id)
            )
        )

        step = select(
            node.scope_type,
            node.scope_id,
            node.parent_type,
            node.parent_id,
            *(cte.c[label] for label in labels),
        ).join(cte, condition)

        return cte.union(step)

    def _build_vertical(self, targets: set[tuple[str, int]]):
        seeds = [
            select(
                Scope.scope_type,
                Scope.scope_id,
                Scope.parent_type,
                Scope.parent_id,
                literal(permission).label("target_permission"),
                literal(scope_id).label("target_scope_id"),
            ).where(
                Scope.scope_type == permission.split(".", 1)[0],
                Scope.scope_id == scope_id,
            )
            for permission, scope_id in targets
        ]
        anchor = union_all(*seeds) if len(seeds) > 1 else seeds[0]
        labels = ("target_permission", "target_scope_id")

        ancestors = self._recursive_side(anchor, "ancestors", labels, up=True)
        descendants = self._recursive_side(anchor, "descendants", labels, up=False)

        columns = lambda side: select(
            side.c.scope_type,
            side.c.scope_id,
            side.c.target_permission,
            side.c.target_scope_id,
        )
        return union(columns(ancestors), columns(descendants)).subquery("vertical")

    async def list_scopes_batch(
        self, user_id: int, queries: list[ScopeQuery]
    ) -> list[ScopeResult]:

        if not await self._is_active(user_id):
            return [self._empty_result(q) for q in queries]

        if await self._is_superuser(user_id):
            return [
                ScopeResult(
                    permission=q.permission,
                    scope_type=q.target_scope_type,
                    scope_ids=await self._all_scopes(q.target_scope_type),
                )
                for q in queries
            ]

        reachable = await self._find_reachable(user_id, queries)
        return [
            ScopeResult(
                permission=q.permission,
                scope_type=q.target_scope_type,
                scope_ids=sorted(
                    reachable.get((q.permission, q.target_scope_type), set())
                ),
            )
            for q in queries
        ]

    async def list_scopes(
        self, user_id: int, permission: str, scope_type: str | None = None
    ) -> list[int]:
        query = ScopeQuery(permission=permission, scope_type=scope_type)
        (result,) = await self.list_scopes_batch(user_id, [query])
        return result.scope_ids

    def _empty_result(self, query: ScopeQuery) -> ScopeResult:
        return ScopeResult(
            permission=query.permission,
            scope_type=query.target_scope_type,
            scope_ids=[],
        )

    async def _all_scopes(self, scope_type: str) -> list[int]:
        stmt = select(Scope.scope_id).where(Scope.scope_type == scope_type)
        return sorted(await self.session.scalars(stmt))

    async def _find_reachable(
        self, user_id: int, queries: list[ScopeQuery]
    ) -> dict[tuple[str, str], set[int]]:

        permissions = {q.permission for q in queries}
        wanted_types = {q.target_scope_type for q in queries}
        reachable = self._build_reachable(user_id, permissions)

        stmt = (
            select(
                reachable.c.target_permission,
                reachable.c.scope_type,
                reachable.c.scope_id,
            )
            .where(reachable.c.scope_type.in_(wanted_types))
            .distinct()
        )

        rows = await self.session.execute(stmt)
        result: dict[tuple[str, str], set[int]] = {}
        for permission, scope_type, scope_id in rows:
            result.setdefault((permission, scope_type), set()).add(scope_id)
        return result

    def _build_reachable(self, user_id: int, permissions: set[str]):
        anchor = (
            select(
                Scope.scope_type,
                Scope.scope_id,
                Scope.parent_type,
                Scope.parent_id,
                role_permission.c.permission_code.label("target_permission"),
            )
            .select_from(Assignment)
            .join(
                Scope,
                (Scope.scope_type == Assignment.scope_type_code)
                & (Scope.scope_id == Assignment.scope_id),
            )
            .join(role_permission, role_permission.c.role_id == Assignment.role_id)
            .where(
                Assignment.user_id == user_id,
                role_permission.c.permission_code.in_(permissions),
            )
        )
        labels = ("target_permission",)

        ancestors = self._recursive_side(anchor, "reachable_up", labels, up=True)
        descendants = self._recursive_side(anchor, "reachable_down", labels, up=False)

        columns = lambda side: select(
            side.c.scope_type, side.c.scope_id, side.c.target_permission
        )
        return union(columns(ancestors), columns(descendants)).subquery("reachable")
