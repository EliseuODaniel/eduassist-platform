from functools import lru_cache

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    llm_provider: str = 'openai'
    openai_base_url: str = 'https://api.openai.com/v1'
    openai_model: str = 'gpt-5.4'
    google_model: str = 'gemini-2.5-pro'


@lru_cache
def get_settings() -> Settings:
    return Settings()


class HealthResponse(BaseModel):
    status: str
    service: str
    provider: str


app = FastAPI(
    title='EduAssist AI Orchestrator',
    version='0.1.0',
    summary='AI orchestration bootstrap for EduAssist Platform.',
)


@app.get('/healthz', response_model=HealthResponse)
async def healthz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status='ok',
        service='ai-orchestrator',
        provider=settings.llm_provider,
    )


@app.get('/meta')
async def meta() -> dict[str, str]:
    settings = get_settings()
    return {
        'service': 'ai-orchestrator',
        'environment': settings.app_env,
        'provider': settings.llm_provider,
        'openaiBaseUrl': settings.openai_base_url,
        'openaiModel': settings.openai_model,
        'googleModel': settings.google_model,
    }


@app.get('/v1/status')
async def status() -> dict[str, object]:
    return {
        'service': 'ai-orchestrator',
        'ready': True,
        'capabilities': [
            'tool-routing',
            'retrieval-bootstrap',
            'provider-abstraction',
        ],
    }

