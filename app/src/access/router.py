from fastapi import APIRouter
from src.access.deps import AccessServiceDep
from src.access.schema import (
    CheckRequest,
    CheckResponse,
    ScopeListRequest,
    ScopeListResponse,
)
from src.authentication.deps import CurrentUser

router = APIRouter()


@router.post("/check")
async def check_access(
    payload: CheckRequest,
    current_user: CurrentUser,
    service: AccessServiceDep,
) -> CheckResponse:
    target_id = payload.user_id or current_user.id

    if target_id != current_user.id:
        pass  # TODO Проверка на наличие прав

    results = await service.check_batch(target_id, payload.checks)
    return CheckResponse(user_id=target_id, results=results)


@router.post("/check/list-scope")
async def check_list_scope(
    payload: ScopeListRequest,
    current_user: CurrentUser,
    service: AccessServiceDep,
) -> ScopeListResponse:
    target_id = payload.user_id or current_user.id

    if target_id != current_user.id:
        pass  # TODO Проверка на наличие прав

    results = await service.list_scopes_batch(
        user_id=target_id, queries=payload.queries
    )
    return ScopeListResponse(user_id=target_id, results=results)
