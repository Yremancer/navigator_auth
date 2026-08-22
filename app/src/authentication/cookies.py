from typing import Any

from src.setting import settings
from starlette.responses import Response


class AuthCookies:
    @staticmethod
    def _common() -> dict[str, Any]:
        return {
            "domain": settings.COOKIE_DOMAIN,
            "httponly": True,
            "secure": settings.MODE != "dev",
            "samesite": "lax",
            "path": "/",
        }

    @classmethod
    def set(cls, resp: Response, token: dict[str, Any]) -> None:
        common = cls._common()
        resp.set_cookie(settings.ACCESS_COOKIE_NAME, token["access_token"], **common)
        resp.set_cookie(settings.ID_COOKIE_NAME, token["id_token"], **common)

        if token.get("refresh_token"):
            resp.set_cookie(
                settings.REFRESH_COOKIE_NAME,
                token["refresh_token"],
                max_age=settings.REFRESH_MAX_AGE,
                **common,
            )

    @classmethod
    def clear(cls, resp: Response) -> None:
        for name in (
            settings.ACCESS_COOKIE_NAME,
            settings.ID_COOKIE_NAME,
            settings.REFRESH_COOKIE_NAME,
        ):
            resp.delete_cookie(name, domain=settings.COOKIE_DOMAIN, path="/")
