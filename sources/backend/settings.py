from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    APP_ENVIRONMENT: Literal["PROD", "DEV", "TEST"] = "PROD"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    # typing cannot be better cause it can be a docker container name, ip address or url
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: SecretStr
    JWT_ACCESS_TOKEN_EXPIRATION_MINUTES: int = 60
    RESET_PASSWORD_TOKEN_SECRET: SecretStr
    VERIFICATION_TOKEN_SECRET: SecretStr
    POSTGRES_HOST: str = "project_base_postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "dev"
    POSTGRES_PASSWORD: SecretStr = "dev"
    POSTGRES_DB: str = "dev"
    ALLOWED_CORS_ORIGINS: list[str]


class InitializationSettings(BaseSettings):
    DEFAULT_EMAIL: str | None = None
    DEFAULT_PASSWORD: SecretStr | None = None
