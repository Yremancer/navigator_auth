from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    BACKEND_PORT: int

    ALLOWED_ORIGINS: str

    OIDC_ISSUER: str
    OIDC_CLIENT_ID: str
    OIDC_CLIENT_SECRET: str
    OIDC_REDIRECT_URL: str
    OIDC_POST_LOGOUT_REDIRECT_URL: str
    BASE_DOMAIN: str
    APPS: str
    COOKIE_DOMAIN: str | None = None
    SESSION_SECRET: str
    ACCESS_COOKIE_NAME: str = "nav-access"
    ID_COOKIE_NAME: str = "nav-id"
    REFRESH_COOKIE_NAME: str = "nav-refresh"

    MODE: str

    @property
    def ORIGINS(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def ALLOWED_APPS(self) -> set[str]:
        return {a.strip() for a in self.APPS.split(",") if a.strip()}

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
