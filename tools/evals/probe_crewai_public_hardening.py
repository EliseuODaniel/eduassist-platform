#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from time import perf_counter


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
AI_ORCHESTRATOR_SRC = REPO_ROOT / 'apps/ai-orchestrator/src'
if str(AI_ORCHESTRATOR_SRC) not in sys.path:
    sys.path.insert(0, str(AI_ORCHESTRATOR_SRC))

from ai_orchestrator.engine_selector import build_engine_bundle
from ai_orchestrator.main import Settings
from ai_orchestrator.models import ConversationChannel, MessageResponseRequest, UserContext, UserRole


CASES = [
    {
        'id': 'service_routing_multi',
        'prompt': 'Com quem eu falo sobre bolsa, com quem eu falo sobre boletos e com quem eu falo sobre bullying?',
        'expected_keywords': ['admissions', 'financeiro', 'orientacao educacional'],
    },
    {
        'id': 'leadership_name',
        'prompt': 'Qual e o nome do diretor da escola?',
        'expected_keywords': ['Helena Martins', 'Diretora geral'],
    },
    {
        'id': 'interval_schedule',
        'prompt': 'Quais os horarios de intervalo?',
        'expected_keywords': ['Ensino Fundamental II', '09:35', 'Ensino Medio', '09:40'],
    },
    {
        'id': 'project_of_life',
        'prompt': 'O que e Projeto de vida?',
        'expected_keywords': ['Projeto de vida', 'autoconhecimento'],
    },
    {
        'id': 'unpublished_classrooms',
        'prompt': 'Quantas salas de aula o colegio tem?',
        'expected_keywords': ['dado nao esta publicado oficialmente'],
    },
    {
        'id': 'shift_offers',
        'prompt': 'A escola tem quais turmas? ensino matutino, vespertino ou noturno?',
        'expected_keywords': ['Ensino Fundamental II', 'Manha', 'Ensino Medio', 'Nao ha turno noturno'],
    },
]


def _settings() -> Settings:
    return Settings(
        orchestrator_engine='langgraph',
        feature_flag_primary_orchestration_stack='crewai',
        strict_framework_isolation_enabled=True,
        orchestrator_experiment_enabled=False,
        langgraph_checkpointer_enabled=False,
        api_core_url='http://127.0.0.1:8001',
        qdrant_url='http://127.0.0.1:6333',
        database_url='postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist',
        crewai_pilot_url=os.getenv('CREWAI_PILOT_URL', 'http://127.0.0.1:8004'),
        specialist_supervisor_pilot_url=os.getenv('SPECIALIST_SUPERVISOR_PILOT_URL', 'http://127.0.0.1:8005'),
    )


async def _run_case(case: dict[str, object]) -> dict[str, object]:
    settings = _settings()
    request = MessageResponseRequest(
        message=str(case['prompt']),
        conversation_id=f"probe:crewai-public:{case['id']}",
        telegram_chat_id=777101,
        channel=ConversationChannel.telegram,
        user=UserContext(role=UserRole.anonymous, authenticated=False),
        allow_graph_rag=True,
        allow_handoff=True,
    )
    bundle = build_engine_bundle(settings, request=request)
    started = perf_counter()
    response = await asyncio.wait_for(
        bundle.primary.respond(request=request, settings=settings, engine_mode=bundle.mode),
        timeout=45.0,
    )
    latency_ms = round((perf_counter() - started) * 1000, 1)
    answer = response.message_text
    normalized = answer.casefold()
    passed = all(str(keyword).casefold() in normalized for keyword in case['expected_keywords'])
    return {
        'id': case['id'],
        'prompt': case['prompt'],
        'passed': passed,
        'latency_ms': latency_ms,
        'reason': response.reason,
        'graph_path': list(response.graph_path),
        'answer': answer,
    }


async def _main() -> int:
    results = [await _run_case(case) for case in CASES]
    passed = sum(1 for item in results if item['passed'])
    payload = {
        'passed': passed,
        'total': len(results),
        'results': results,
    }
    report_path = REPO_ROOT / 'artifacts/crewai-public-hardening-probe.json'
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(report_path)
    print(f'passed={passed}/{len(results)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(_main()))
