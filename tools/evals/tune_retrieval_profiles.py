#!/usr/bin/env python3
from __future__ import annotations

import json
from urllib.parse import urlparse, urlunparse
from pathlib import Path
import sys
from time import monotonic


REPO_ROOT = Path(__file__).resolve().parents[2]
AI_ORCHESTRATOR_SRC = REPO_ROOT / 'apps/ai-orchestrator/src'
if str(AI_ORCHESTRATOR_SRC) not in sys.path:
    sys.path.insert(0, str(AI_ORCHESTRATOR_SRC))

from ai_orchestrator.models import RetrievalProfile
from ai_orchestrator.retrieval import get_retrieval_service


CASES = [
    {
        'id': 'policy_lookup',
        'query': 'Como funciona a politica de avaliacao, recuperacao e promocao da escola?',
        'visibility': 'public',
        'expected_documents': ['Politica de Avaliacao, Recuperacao e Promocao'],
        'expected_profile': 'default',
    },
    {
        'id': 'family_new_bundle',
        'query': 'Compare o calendario letivo, a agenda de avaliacoes e o manual de matricula do ponto de vista de uma familia nova.',
        'visibility': 'public',
        'expected_documents': [
            'Calendario Letivo 2026',
            'Agenda de Avaliacoes, Recuperacoes e Simulados 2026',
            'Manual de Matricula do Ensino Medio',
        ],
        'expected_profile': 'cheap',
        'expected_canonical_lane': 'public_bundle.family_new_calendar_assessment_enrollment',
    },
    {
        'id': 'service_credentials_bundle',
        'query': 'Sintetize tudo o que uma familia precisa entender sobre secretaria, portal, credenciais e envio de documentos.',
        'visibility': 'public',
        'expected_documents': [
            'Secretaria, Documentacao e Prazos',
            'Politica de Uso do Portal, Aplicativo e Credenciais',
        ],
        'expected_profile': 'deep',
        'expected_canonical_lane': 'public_bundle.secretaria_portal_credentials',
    },
    {
        'id': 'permanence_family_support',
        'query': 'Quais temas atravessam varios documentos publicos quando o assunto e permanencia escolar e acompanhamento da familia?',
        'visibility': 'public',
        'expected_documents': [
            'Orientacao, Apoio e Vida Escolar',
            'Politica de Avaliacao, Recuperacao e Promocao',
        ],
        'expected_profile': 'cheap',
        'expected_canonical_lane': 'public_bundle.permanence_family_support',
    },
]


CONFIGS = [
    {
        'id': 'baseline',
        'candidate_pool_size': 12,
        'cheap_candidate_pool_size': 8,
        'deep_candidate_pool_size': 18,
        'rerank_fused_weight': 0.4,
        'rerank_late_interaction_weight': 0.6,
    },
    {
        'id': 'high_recall',
        'candidate_pool_size': 14,
        'cheap_candidate_pool_size': 8,
        'deep_candidate_pool_size': 22,
        'rerank_fused_weight': 0.35,
        'rerank_late_interaction_weight': 0.65,
    },
    {
        'id': 'balanced_fast',
        'candidate_pool_size': 10,
        'cheap_candidate_pool_size': 6,
        'deep_candidate_pool_size': 16,
        'rerank_fused_weight': 0.45,
        'rerank_late_interaction_weight': 0.55,
    },
]


def _load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    env_file = REPO_ROOT / '.env'
    if not env_file.exists():
        return env
    for line in env_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        env[key.strip()] = value.strip()
    return env


def _replace_url_host(value: str, *, replacements: dict[str, str]) -> str:
    normalized = str(value or '').strip()
    if not normalized:
        return normalized
    parsed = urlparse(normalized)
    host = (parsed.hostname or '').strip().lower()
    replacement_host = replacements.get(host)
    if replacement_host is None:
        return normalized
    netloc = replacement_host
    if parsed.port is not None:
        netloc = f'{replacement_host}:{parsed.port}'
    if parsed.username:
        auth = parsed.username
        if parsed.password:
            auth = f'{auth}:{parsed.password}'
        netloc = f'{auth}@{netloc}'
    return urlunparse(parsed._replace(netloc=netloc))


def _normalize_local_database_url(value: str) -> str:
    normalized = str(value or '').strip()
    if not normalized:
        return 'postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist'
    return _replace_url_host(
        normalized,
        replacements={
            'postgres': '127.0.0.1',
            'localhost': '127.0.0.1',
        },
    )


def _normalize_local_qdrant_url(value: str) -> str:
    normalized = str(value or '').strip()
    if not normalized:
        return 'http://127.0.0.1:6333'
    return _replace_url_host(
        normalized,
        replacements={
            'qdrant': '127.0.0.1',
            'localhost': '127.0.0.1',
        },
    )


def main() -> int:
    env = _load_env()
    database_url = _normalize_local_database_url(
        env.get('DATABASE_URL_LOCAL')
        or env.get('DATABASE_URL')
        or 'postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist'
    )
    qdrant_url = _normalize_local_qdrant_url(
        env.get('QDRANT_URL_LOCAL')
        or env.get('QDRANT_URL')
        or 'http://127.0.0.1:6333'
    )
    collection_name = env.get('QDRANT_DOCUMENTS_COLLECTION', 'school_documents')
    embedding_model = env.get('DOCUMENT_EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    rerank_model = env.get('RETRIEVAL_LATE_INTERACTION_MODEL', 'answerdotai/answerai-colbert-small-v1')

    report: list[dict[str, object]] = []
    for config in CONFIGS:
        service = get_retrieval_service(
            database_url=database_url,
            qdrant_url=qdrant_url,
            collection_name=collection_name,
            embedding_model=embedding_model,
            enable_query_variants=True,
            enable_late_interaction_rerank=True,
            late_interaction_model=rerank_model,
            candidate_pool_size=int(config['candidate_pool_size']),
            cheap_candidate_pool_size=int(config['cheap_candidate_pool_size']),
            deep_candidate_pool_size=int(config['deep_candidate_pool_size']),
            rerank_fused_weight=float(config['rerank_fused_weight']),
            rerank_late_interaction_weight=float(config['rerank_late_interaction_weight']),
        )
        case_results: list[dict[str, object]] = []
        total_latency_ms = 0.0
        total_match_score = 0.0
        for case in CASES:
            started_at = monotonic()
            response = service.hybrid_search(
                query=str(case['query']),
                top_k=4,
                visibility=str(case['visibility']),
                category=None,
                profile=RetrievalProfile(case['expected_profile']),
            )
            latency_ms = (monotonic() - started_at) * 1000.0
            total_latency_ms += latency_ms
            top_documents = [group.document_title for group in response.document_groups[:3]]
            expected_documents = list(case['expected_documents'])
            matched_documents = [title for title in expected_documents if title in top_documents]
            canonical_lane = response.query_plan.canonical_lane if response.query_plan else None
            expected_canonical_lane = str(case.get('expected_canonical_lane') or '').strip() or None
            coverage = len(matched_documents) / max(1, len(expected_documents))
            if expected_canonical_lane and canonical_lane == expected_canonical_lane:
                coverage = max(coverage, 1.0)
            total_match_score += coverage
            case_results.append(
                {
                    'id': case['id'],
                    'profile': response.query_plan.profile.value if response.query_plan else None,
                    'latency_ms': round(latency_ms, 2),
                    'top_documents': top_documents,
                    'matched_documents': matched_documents,
                    'coverage': round(coverage, 3),
                    'canonical_lane': canonical_lane,
                }
            )

        report.append(
            {
                'config': config,
                'avg_latency_ms': round(total_latency_ms / max(1, len(CASES)), 2),
                'avg_document_coverage': round(total_match_score / max(1, len(CASES)), 3),
                'results': case_results,
            }
        )

    best = sorted(
        report,
        key=lambda item: (-float(item['avg_document_coverage']), float(item['avg_latency_ms'])),
    )[0]
    payload = {
        'configs_tested': len(CONFIGS),
        'cases_tested': len(CASES),
        'best': best,
        'report': report,
    }
    output_path = REPO_ROOT / 'artifacts/retrieval-profile-tuning-report.json'
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output_path)
    print(json.dumps(best, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
