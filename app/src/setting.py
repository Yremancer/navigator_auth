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
    BASE_DOMAIN: str
    APPS: str
    SESSION_COOKIE_NAME: str
    SESSION_SECRET: str

    MODE: str

    @property
    def ORIGINS(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def ALLOWED_APPS(self) -> set[str]:
        return {a.strip() for a in self.APPS.split(",") if a.strip()}


settings = Settings()
