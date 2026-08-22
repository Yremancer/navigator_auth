from typing import Any
from urllib.parse import urlencode, urlsplit

import jwt
from authlib.integrations.base_client import OAuthError
from jwt import PyJWKClient
from src.authentication.exceptions import InvalidTokenError, RefreshFailedError
from src.setting import settings
from src.user.models import User
from src.user.service import UserService
from starlette.requests import Request
from starlette.responses import RedirectResponse


class AuthService:
    def __init__(
        self, oauth_client: Any, jwks: PyJWKClient, users: UserService
    ) -> None:
        self._oauth = oauth_client
        self._jwks = jwks
        self._users = users

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            signing_key = self._jwks.get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.OIDC_CLIENT_ID,
                issuer=settings.OIDC_ISSUER,
            )
        except jwt.PyJWTError as e:
            raise InvalidTokenError from e

    def build_return_url(self, app: str | None, next_path: str | None) -> str:
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
        host = f"{app}.{settings.BASE_DOMAIN}" if app else settings.BASE_DOMAIN
        return f"{scheme}://{host}{path}"

    async def authorize_redirect(self, request: Request) -> RedirectResponse:
        return await self._oauth.authorize_redirect(request, settings.OIDC_REDIRECT_URL)

    async def handle_callback(self, request: Request) -> tuple[User, dict[str, Any]]:
        token = await self._oauth.authorize_access_token(request)
        claims = token["userinfo"]

        user = await self._users.get_or_add(
            external_id=claims["sub"],
            email=claims["email"],
            full_name=claims["name"],
        )
        return user, token

    async def refresh(self, refresh_token: str) -> dict[str, Any]:
        try:
            return await self._oauth.fetch_access_token(
                refresh_token=refresh_token, grant_type="refresh_token"
            )
        except OAuthError as e:
            raise RefreshFailedError from e

    async def end_session_url(self, id_token: str | None) -> str:
        meta = await self._oauth.load_server_metadata()
        params = {"post_logout_redirect_uri": settings.OIDC_POST_LOGOUT_REDIRECT_URL}
        if id_token:
            params["id_token_hint"] = id_token
        return f"{meta['end_session_endpoint']}?{urlencode(params)}"
