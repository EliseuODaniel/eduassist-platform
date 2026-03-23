from __future__ import annotations

from functools import lru_cache
from typing import Iterable

from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    if url.startswith('postgresql+psycopg://'):
        return url
    if url.startswith('postgresql://'):
        return url.replace('postgresql://', 'postgresql+psycopg://', 1)
    if url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql+psycopg://', 1)
    return url


def parse_csv(value: str | Iterable[str]) -> list[str]:
    if isinstance(value, str):
        items = value.split(',')
    else:
        items = list(value)
    return [item.strip() for item in items if item.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    database_url: str = 'postgresql://eduassist:eduassist@postgres:5432/eduassist'
    redis_url: str = 'redis://redis:6379/0'
    opa_url: str = 'http://opa:8181'
    keycloak_internal_url: str = 'http://keycloak:8080'
    keycloak_public_url: str = 'http://localhost:8080'
    keycloak_realm: str = 'eduassist'
    keycloak_allowed_clients: str = 'eduassist-web,eduassist-cli'
    internal_api_token: str = 'dev-internal-token'
    allow_test_identity_overrides: bool = True
    telegram_link_ttl_minutes: int = 15
    telegram_bot_username: str | None = None
    foundation_seed: int = 20260323

    @property
    def sqlalchemy_database_url(self) -> str:
        return normalize_database_url(self.database_url)

    @property
    def keycloak_issuer(self) -> str:
        return f'{self.keycloak_public_url}/realms/{self.keycloak_realm}'

    @property
    def keycloak_jwks_url(self) -> str:
        return f'{self.keycloak_internal_url}/realms/{self.keycloak_realm}/protocol/openid-connect/certs'

    @property
    def keycloak_token_url(self) -> str:
        return f'{self.keycloak_public_url}/realms/{self.keycloak_realm}/protocol/openid-connect/token'

    @property
    def allowed_keycloak_clients(self) -> list[str]:
        return parse_csv(self.keycloak_allowed_clients)


@lru_cache
def get_settings() -> Settings:
    return Settings()
