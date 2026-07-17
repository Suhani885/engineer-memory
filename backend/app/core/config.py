from __future__ import annotations

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # -----------------------------------------------------------------------
    # Application
    # -----------------------------------------------------------------------
    app_name: str = "Engineering Memory"
    app_env: str = "development"
    log_level: str = "INFO"
    secret_key: str = "development-only-secret-key"

    # -----------------------------------------------------------------------
    # Database
    # -----------------------------------------------------------------------
    database_url: str = (
        "postgresql+psycopg://engineering_memory:change-me@localhost:5432/engineering_memory"
    )

    # -----------------------------------------------------------------------
    # Redis / Celery
    # -----------------------------------------------------------------------
    redis_url: str = "redis://localhost:6379/0"

    # -----------------------------------------------------------------------
    # CORS
    # -----------------------------------------------------------------------
    cors_origins: str = "http://localhost:3000"

    # -----------------------------------------------------------------------
    # JWT
    # -----------------------------------------------------------------------
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # -----------------------------------------------------------------------
    # GitHub App (populated when GitHub integration is wired up)
    # -----------------------------------------------------------------------
    github_app_id: str = ""
    github_app_private_key: str = ""
    github_webhook_secret: str = ""

    # -----------------------------------------------------------------------
    # OpenAI (populated when AI layer is wired up)
    # -----------------------------------------------------------------------
    openai_api_key: str = ""

    # -----------------------------------------------------------------------
    # Pydantic config
    # -----------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # -----------------------------------------------------------------------
    # Derived properties
    # -----------------------------------------------------------------------

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------

    @model_validator(mode="after")
    def validate_production_settings(self) -> Settings:
        if not self.is_development and self.secret_key == "development-only-secret-key":
            raise ValueError("SECRET_KEY must be set in production environments.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
