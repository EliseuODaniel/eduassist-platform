#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / '.env', override=False)

from ai_orchestrator_specialist.main import Settings
from ai_orchestrator_specialist.models import SpecialistSupervisorRequest
from ai_orchestrator_specialist.runtime import run_specialist_supervisor


async def _main() -> int:
    payload = json.loads(sys.stdin.read() or '{}')
    request = SpecialistSupervisorRequest.model_validate(payload.get('request') or {})
    settings = Settings(
        api_core_url=str(payload.get('api_core_url') or os.getenv('API_CORE_URL') or 'http://127.0.0.1:8001'),
        orchestrator_url=str(
            payload.get('orchestrator_url')
            or os.getenv('CONTROL_PLANE_ORCHESTRATOR_URL')
            or os.getenv('AI_ORCHESTRATOR_URL')
            or 'http://127.0.0.1:8002'
        ),
        internal_api_token=str(payload.get('internal_api_token') or os.getenv('INTERNAL_API_TOKEN') or 'dev-internal-token'),
        openai_api_key=payload.get('openai_api_key') or os.getenv('OPENAI_API_KEY'),
        google_api_key=payload.get('google_api_key') or os.getenv('GOOGLE_API_KEY'),
    )
    response = await run_specialist_supervisor(request=request, settings=settings)
    print(json.dumps(response, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(_main()))
