from typing import Annotated
from urllib.parse import urlsplit

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
        APIKeyCookie(name=settings.SESSION_COOKIE_NAME, auto_error=False)
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
    client_kwargs={"scope": "openid profile email"},
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


@router.get("/login")
async def login(request: Request, app: str | None = None, next: str = "/"):
    request.session["return_url"] = build_return_url(app, next)
    return await client.authorize_redirect(request, settings.OIDC_REDIRECT_URL)


@router.get("/callback")
async def callback(request: Request):
    token = await client.authorize_access_token(request)
    id_token = token["id_token"]
    return_url = request.session.get("return_url", "/")
    request.session.clear()
    resp = RedirectResponse(url=return_url)
    resp.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=id_token,
        httponly=True,
        secure=settings.MODE == "prod",
        samesite="lax",
    )
    return resp


@router.get("/logout")
async def logout():
    resp = JSONResponse({"status": "200"})
    resp.delete_cookie(settings.SESSION_COOKIE_NAME)
    return resp


@router.get("/me")
async def me(claims: Annotated[dict, Depends(get_claims)]):
    return claims
