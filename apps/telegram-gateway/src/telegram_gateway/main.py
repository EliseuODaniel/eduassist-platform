from functools import lru_cache

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    telegram_webhook_secret: str = 'change-me'
    api_core_url: str = 'http://api-core:8000'


@lru_cache
def get_settings() -> Settings:
    return Settings()


class HealthResponse(BaseModel):
    status: str
    service: str
    api_core_url: str


app = FastAPI(
    title='EduAssist Telegram Gateway',
    version='0.1.0',
    summary='Telegram ingress bootstrap for EduAssist Platform.',
)


@app.get('/healthz', response_model=HealthResponse)
async def healthz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status='ok',
        service='telegram-gateway',
        api_core_url=settings.api_core_url,
    )


@app.get('/meta')
async def meta() -> dict[str, str]:
    settings = get_settings()
    return {
        'service': 'telegram-gateway',
        'environment': settings.app_env,
        'apiCoreUrl': settings.api_core_url,
    }


@app.get('/webhooks/telegram')
async def webhook_info() -> dict[str, object]:
    return {
        'service': 'telegram-gateway',
        'ready': True,
        'message': 'Use POST on this endpoint for Telegram updates.',
    }


@app.post('/webhooks/telegram')
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, object]:
    settings = get_settings()
    if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=401, detail='Invalid Telegram webhook secret.')

    payload = await request.json()
    return {
        'accepted': True,
        'service': 'telegram-gateway',
        'payloadKeys': sorted(payload.keys()),
    }

