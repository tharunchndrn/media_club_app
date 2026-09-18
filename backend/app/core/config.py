from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend configuration, read from environment or backend/.env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://mediaclub:mediaclub@localhost:5433/mediaclub"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
