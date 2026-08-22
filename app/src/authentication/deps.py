from typing import Annotated, Any

from fastapi import Depends, Request, Security
from fastapi.security import APIKeyCookie
from jwt import PyJWKClient
from src.authentication.exceptions import NotAuthenticatedError
from src.authentication.service import AuthService
from src.setting import settings
from src.user.deps import UserServiceDep
from src.user.exceptions import UserInactiveError, UserNotFoundError
from src.user.models import User


def get_oauth_client(request: Request) -> Any:
    return request.app.state.oauth_client


def get_jwks(request: Request) -> PyJWKClient:
    return request.app.state.jwks


def get_auth_service(
    oauth: Annotated[Any, Depends(get_oauth_client)],
    jwks: Annotated[PyJWKClient, Depends(get_jwks)],
    users: UserServiceDep,
) -> AuthService:
    return AuthService(oauth, jwks, users)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_claims(
    service: AuthServiceDep,
    token: Annotated[
        str | None,
        Security(APIKeyCookie(name=settings.ACCESS_COOKIE_NAME, auto_error=False)),
    ] = None,
) -> dict[str, Any]:
    if not token:
        raise NotAuthenticatedError
    return service.decode_token(token)


async def get_current_user(
    claims: Annotated[dict, Depends(get_claims)],
    users: UserServiceDep,
) -> User:
    user = await users.get_by_external_id(external_id=claims["sub"])
    if user is None:
        raise UserNotFoundError(external_id=claims["sub"])
    if not user.is_active:
        raise UserInactiveError(id=user.id)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
