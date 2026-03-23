from functools import lru_cache

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    database_url: str = 'postgresql://eduassist:eduassist@postgres:5432/eduassist'
    redis_url: str = 'redis://redis:6379/0'
    opa_url: str = 'http://opa:8181'


@lru_cache
def get_settings() -> Settings:
    return Settings()


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


app = FastAPI(
    title='EduAssist API Core',
    version='0.1.0',
    summary='Core domain API bootstrap for EduAssist Platform.',
)


@app.get('/healthz', response_model=HealthResponse)
async def healthz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status='ok',
        service='api-core',
        environment=settings.app_env,
    )


@app.get('/meta')
async def meta() -> dict[str, str]:
    settings = get_settings()
    return {
        'service': 'api-core',
        'environment': settings.app_env,
        'logLevel': settings.log_level,
        'databaseUrl': settings.database_url,
        'redisUrl': settings.redis_url,
        'opaUrl': settings.opa_url,
    }


@app.get('/v1/status')
async def status() -> dict[str, object]:
    return {
        'service': 'api-core',
        'ready': True,
        'capabilities': [
            'authz-gateway',
            'domain-services',
            'audit-trail',
        ],
    }

