from __future__ import annotations

import signal
import time
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = 'development'
    log_level: str = 'INFO'
    database_url: str = 'postgresql://eduassist:eduassist@postgres:5432/eduassist'
    redis_url: str = 'redis://redis:6379/0'


READY_FILE = Path('/tmp/worker-ready')
RUNNING = True


def _stop(*_: object) -> None:
    global RUNNING
    RUNNING = False


def main() -> None:
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    settings = Settings()
    READY_FILE.write_text(
        f'worker running in {settings.app_env} with database {settings.database_url}\n',
        encoding='utf-8',
    )

    print('[worker] bootstrap background loop started')
    while RUNNING:
        time.sleep(5)

    if READY_FILE.exists():
        READY_FILE.unlink()
    print('[worker] shutdown complete')


if __name__ == '__main__':
    main()

