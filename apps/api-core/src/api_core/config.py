from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    if url.startswith('postgresql+psycopg://'):
        return url
    if url.startswith('postgresql://'):
        return url.replace('postgresql://', 'postgresql+psycopg://', 1)
    if url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql+psycopg://', 1)
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    database_url: str = 'postgresql://eduassist:eduassist@postgres:5432/eduassist'
    redis_url: str = 'redis://redis:6379/0'
    opa_url: str = 'http://opa:8181'
    foundation_seed: int = 20260323

    @property
    def sqlalchemy_database_url(self) -> str:
        return normalize_database_url(self.database_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
