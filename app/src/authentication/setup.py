import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI
from jwt import PyJWKClient
from src.setting import settings

DISCOVERY_URL = f"{settings.OIDC_ISSUER}/.well-known/openid-configuration"


async def setup_auth(app: FastAPI, http: httpx.AsyncClient) -> None:
    resp = await http.get(DISCOVERY_URL)
    resp.raise_for_status()
    app.state.jwks = PyJWKClient(resp.json()["jwks_uri"], cache_keys=True)

    oauth = OAuth()
    oauth.register(
        name="oidc",
        server_metadata_url=DISCOVERY_URL,
        client_id=settings.OIDC_CLIENT_ID,
        client_secret=settings.OIDC_CLIENT_SECRET,
        client_kwargs={"scope": "openid profile email offline_access"},
    )
    app.state.oauth_client = oauth.create_client("oidc")
