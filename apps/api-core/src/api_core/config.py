from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable

from pydantic import model_validator
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


_ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / '.env'
_INTERNAL_API_TOKEN_PLACEHOLDERS = {'', 'dev-internal-token', 'change-me-internal-token'}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=('/workspace/.env', str(_ROOT_ENV_FILE), '.env'),
        env_ignore_empty=True,
        extra='ignore',
    )

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
    internal_workload_identity_mode: str = 'token'
    internal_spiffe_allowed_ids: str = ''
    allow_insecure_internal_api_token: bool = False
    allow_test_identity_overrides: bool = False
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

    @model_validator(mode='after')
    def _validate_internal_api_token(self) -> 'Settings':
        token = str(self.internal_api_token or '').strip()
        if token not in _INTERNAL_API_TOKEN_PLACEHOLDERS:
            return self
        if self.allow_insecure_internal_api_token or self.app_env in {'test'}:
            return self
        raise ValueError(
            'internal_api_token must be set to a non-placeholder value; '
            'set INTERNAL_API_TOKEN or explicitly opt into ALLOW_INSECURE_INTERNAL_API_TOKEN=true for isolated tests.'
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
