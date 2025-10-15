from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", case_sensitive=False)

    cors_allow_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    db_url: str = "postgresql+psycopg://user:pass@postgres:5432/app"
    redis_url: str = "redis://redis:6379/0"
    s3_endpoint: str = "http://minio:9000"
    s3_bucket: str = "artifacts"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    auth_secret: str = "change-me"
    auth_cookie_name: str = "psphn_session"
    auth_cookie_secure: bool = False
    webhook_secret: str = "change-me"
    runpod_api_key: str = "change-me"

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: List[str] | str) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_settings_cached() -> Settings:
    return get_settings()


settings = get_settings()
