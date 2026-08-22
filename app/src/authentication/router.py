from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from src.authentication.cookies import AuthCookies
from src.authentication.deps import AuthServiceDep, CurrentUser
from src.authentication.exceptions import RefreshFailedError
from src.setting import settings
from src.user.schema import UserSchema

router = APIRouter()

NextPath = Annotated[str, Query(alias="next")]


@router.get("/login")
async def login(
    request: Request,
    service: AuthServiceDep,
    app: str | None = None,
    next_path: NextPath = "/",
):
    request.session["return_url"] = service.build_return_url(app, next_path)
    return await service.authorize_redirect(request)


@router.get("/callback")
async def callback(request: Request, service: AuthServiceDep) -> RedirectResponse:
    _, token = await service.handle_callback(request)

    return_url = request.session.get("return_url", "/")
    request.session.clear()

    resp = RedirectResponse(url=return_url)
    AuthCookies.set(resp, token)
    return resp


@router.post("/refresh")
async def refresh(request: Request, service: AuthServiceDep) -> JSONResponse:
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise RefreshFailedError

    token = await service.refresh(refresh_token)

    resp = JSONResponse({"status": "ok"})
    AuthCookies.set(resp, token)
    return resp


@router.get("/logout")
async def logout(
    request: Request,
    service: AuthServiceDep,
    app: str | None = None,
    next_path: NextPath = "/",
) -> RedirectResponse:
    request.session["return_url"] = service.build_return_url(app, next_path)
    id_token = request.cookies.get(settings.ID_COOKIE_NAME)

    resp = RedirectResponse(url=await service.end_session_url(id_token))
    AuthCookies.clear(resp)
    return resp


@router.get("/logout/done")
async def logout_done(request: Request) -> RedirectResponse:
    return_url = request.session.get("return_url", "/")
    request.session.clear()

    resp = RedirectResponse(url=return_url)
    AuthCookies.clear(resp)
    return resp


@router.get("/me")
async def me(current_user: CurrentUser) -> UserSchema:
    return current_user
