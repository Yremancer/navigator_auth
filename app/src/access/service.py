from collections import defaultdict

from src.access.repository import AccessRepository
from src.access.schema import (
    CheckResult,
    GrantedPermission,
    GrantedScope,
    PermissionCheck,
    ScopeQuery,
    ScopeResult,
    UserRoleSchema,
)
from src.setting import settings


class AccessService:
    def __init__(self, repo: AccessRepository):
        self._repo = repo

    async def can(
        self,
        user_id: int,
        permission: str,
        scope_id: int = settings.SYSTEM_SCOPE_ID,
    ) -> bool:
        check = PermissionCheck(permission=permission, scope_id=scope_id)
        (result,) = await self.check_batch(user_id, [check])
        return result.allowed

    async def check_batch(
        self, user_id: int, checks: list[PermissionCheck]
    ) -> list[CheckResult]:
        if not checks:
            return []

        if not await self._repo.is_active(user_id):
            return [CheckResult(**c.model_dump(), allowed=False) for c in checks]

        if await self.is_superuser(user_id):
            return [CheckResult(**c.model_dump(), allowed=True) for c in checks]

        targets = {(c.permission, c.scope_type, c.scope_id) for c in checks}
        granted = await self._repo.find_granted(user_id, targets)

        return [
            CheckResult(
                **c.model_dump(),
                allowed=(c.permission, c.scope_id) in granted,
            )
            for c in checks
        ]

    async def list_scopes(
        self, user_id: int, permission: str, scope_type: str | None = None
    ) -> list[int]:
        query = ScopeQuery(permission=permission, scope_type=scope_type)
        (result,) = await self.list_scopes_batch(user_id, [query])
        return result.scope_ids

    async def list_scopes_batch(
        self, user_id: int, queries: list[ScopeQuery]
    ) -> list[ScopeResult]:
        if not queries:
            return []

        if not await self._repo.is_active(user_id):
            return [
                ScopeResult(
                    permission=q.permission,
                    scope_type=q.scope_type,
                    scope_ids=[],
                )
                for q in queries
            ]

        if await self.is_superuser(user_id):
            return [
                ScopeResult(
                    permission=q.permission,
                    scope_type=q.scope_type,
                    scope_ids=await self._repo.list_scope_ids(q.scope_type),
                )
                for q in queries
            ]

        rows = await self._repo.find_reachable(
            user_id,
            permissions={q.permission for q in queries},
            scope_types={q.scope_type for q in queries},
        )

        found: dict[tuple[str, str], set[int]] = defaultdict(set)
        for permission, scope_type, scope_id in rows:
            found[(permission, scope_type)].add(scope_id)

        return [
            ScopeResult(
                permission=q.permission,
                scope_type=q.scope_type,
                scope_ids=sorted(found.get((q.permission, q.scope_type), set())),
            )
            for q in queries
        ]

    async def get_all_granted(self, user_id: int) -> list[GrantedPermission]:
        if not await self._repo.is_active(user_id):
            return []

        rows = await self._repo.find_reachable(user_id)

        grouped: dict[str, dict[str, set[int]]] = defaultdict(lambda: defaultdict(set))
        for permission, scope_type, scope_id in rows:
            grouped[permission][scope_type].add(scope_id)

        return [
            GrantedPermission(
                permission=permission,
                scopes=[
                    GrantedScope(scope_type=scope_type, scope_ids=sorted(ids))
                    for scope_type, ids in sorted(by_type.items())
                ],
            )
            for permission, by_type in sorted(grouped.items())
        ]

    async def get_user_roles(self, user_id: int) -> list[UserRoleSchema]:
        rows = await self._repo.list_user_roles(user_id)
        return [UserRoleSchema.model_validate(row) for row in rows]

    async def is_superuser(self, user_id: int) -> bool:
        return await self._repo.has_super_role(user_id)
