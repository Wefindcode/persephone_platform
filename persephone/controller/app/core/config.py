"""Application configuration and settings."""
from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime configuration derived from environment variables."""

    api_key: str = Field("dev-secret", alias="PERSEPHONE_API_KEY")
    catalog_mode: Literal["mock", "runpod"] = Field(
        "mock", alias="PERSEPHONE_CATALOG_MODE"
    )
    runpod_api_key: Optional[str] = Field(default=None, alias="RUNPOD_API_KEY")
    agent_image: str = Field(
        "registry/persephone-agent:0.1", alias="PERSEPHONE_IMAGE_AGENT"
    )
    request_timeout_s: int = Field(900, alias="PERSEPHONE_REQUEST_TIMEOUT_S")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
