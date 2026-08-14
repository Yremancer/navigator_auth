from typing import Annotated
from urllib.parse import urlencode, urlsplit

import httpx
import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Security
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import APIKeyCookie
from jwt import PyJWKClient
from src.setting import settings

PROVIDER = "oidc"


async def get_jwks_client():
    meta = httpx.get(f"{settings.OIDC_ISSUER}/.well-known/openid-configuration").json()
    return PyJWKClient(meta["jwks_uri"])


async def get_claims(
    token: str = Security(
        APIKeyCookie(name=settings.ACCESS_COOKIE_NAME, auto_error=False)
    ),
):
    if not token:
        raise HTTPException(401, "Not authenticated")
    try:
        signing_key = (await get_jwks_client()).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.OIDC_CLIENT_ID,
            issuer=settings.OIDC_ISSUER,
        )
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {e}")
    return claims


oauth = OAuth()
oauth.register(
    name=PROVIDER,
    server_metadata_url=f"{settings.OIDC_ISSUER}/.well-known/openid-configuration",
    client_id=settings.OIDC_CLIENT_ID,
    client_secret=settings.OIDC_CLIENT_SECRET,
    client_kwargs={"scope": "openid profile email offline_access"},
)

client = oauth.create_client(PROVIDER)

router = APIRouter()


def build_return_url(app: str | None, next_path: str | None) -> str:
    app = app if app in settings.ALLOWED_APPS else None

    path = next_path or "/"
    if not path.startswith("/") or path.startswith("//"):
        path = "/"
    parts = urlsplit(path)
    if parts.scheme or parts.netloc:
        path = "/"
    else:
        path = parts.path + (f"?{parts.query}" if parts.query else "")

    scheme = "https" if settings.MODE != "dev" else "http"
    return (
        f"{scheme}://{app}.{settings.BASE_DOMAIN}{path}"
        if app
        else f"{scheme}://{settings.BASE_DOMAIN}{path}"
    )


def set_auth_cookies(resp, token: dict) -> None:

    common = {
        "domain": settings.COOKIE_DOMAIN,
        "httponly": True,
        "secure": settings.MODE != "dev",
        "samesite": "lax",
        "path": "/",
    }

    resp.set_cookie(settings.ACCESS_COOKIE_NAME, token["access_token"], **common)
    resp.set_cookie(settings.ID_COOKIE_NAME, token["id_token"], **common)
    if token.get("refresh_token"):
        resp.set_cookie(
            settings.REFRESH_COOKIE_NAME,
            token["refresh_token"],
            max_age=60 * 60 * 24 * 30,
            **common,
        )


def clear_auth_cookies(resp) -> None:
    for name in (
        settings.ACCESS_COOKIE_NAME,
        settings.ID_COOKIE_NAME,
        settings.REFRESH_COOKIE_NAME,
    ):
        resp.delete_cookie(name, domain=settings.COOKIE_DOMAIN, path="/")


@router.get("/login")
async def login(request: Request, app: str | None = None, next: str = "/"):
    request.session["return_url"] = build_return_url(app, next)
    return await client.authorize_redirect(request, settings.OIDC_REDIRECT_URL)


@router.post("/refresh")
async def refresh(request: Request):
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(401, "No refresh token")

    try:
        token = await client.fetch_access_token(
            refresh_token=refresh_token,
            grant_type="refresh_token",
        )
    except Exception as e:
        raise HTTPException(401, "Refresh failed") from e

    resp = JSONResponse({"status": "ok"})
    set_auth_cookies(resp, token)
    return resp


@router.get("/callback")
async def callback(request: Request):
    token = await client.authorize_access_token(request)
    return_url = request.session.get("return_url", "/")
    request.session.clear()

    resp = RedirectResponse(url=return_url)
    set_auth_cookies(resp, token)
    return resp


@router.get("/logout")
async def logout(request: Request, app: str | None = None, next: str = "/"):
    request.session["return_url"] = build_return_url(app, next)
    id_token = request.cookies.get(settings.ID_COOKIE_NAME)

    meta = await client.load_server_metadata()
    params = {"post_logout_redirect_uri": settings.OIDC_POST_LOGOUT_REDIRECT_URL}
    if id_token:
        params["id_token_hint"] = id_token

    resp = RedirectResponse(url=f"{meta['end_session_endpoint']}?{urlencode(params)}")
    clear_auth_cookies(resp)
    return resp


@router.get("/logout/done")
async def logout_done(request: Request):
    return_url = request.session.get("return_url", "/")
    request.session.clear()

    resp = RedirectResponse(url=return_url)
    clear_auth_cookies(resp)
    return resp


@router.get("/me")
async def me(claims: Annotated[dict, Depends(get_claims)]):
    return claims
