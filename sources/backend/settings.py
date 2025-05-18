from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENVIRONMENT: Literal["PROD", "DEV", "TEST"] = "PROD"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    # typing cannot be better cause it can be a docker container name, ip address or url
    JWT_STRATEGY_SECRET: SecretStr
    RESET_PASSWORD_TOKEN_SECRET: SecretStr
    VERIFICATION_TOKEN_SECRET: SecretStr
    POSTGRES_HOST: str = "project_base_postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "dev"
    POSTGRES_PASSWORD: str = "dev"  # todo use SecretStr
    POSTGRES_DB: str = "dev"  # todo use SercretStr
