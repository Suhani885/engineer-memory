from __future__ import annotations

import os
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
    # GitHub App
    # -----------------------------------------------------------------------
    github_app_id: str = ""
    github_app_private_key: str = ""  # Can be raw PEM content OR a file path ending in .pem
    github_webhook_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""

    # -----------------------------------------------------------------------
    # OpenAI
    # -----------------------------------------------------------------------
    openai_api_key: str | None = None

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

    @property
    def github_private_key_content(self) -> str:
        """Return raw PEM key content — resolves file paths automatically."""
        raw = self.github_app_private_key
        if not raw:
            return ""
        # If it ends with .pem or looks like a file path, try to read it
        if raw.endswith(".pem") or (os.sep in raw) or ("/" in raw and "-----BEGIN" not in raw):
            # Resolve relative to backend directory
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            candidate = os.path.join(base, raw)
            if os.path.isfile(candidate):
                with open(candidate) as f:
                    return f.read()
        return raw

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
