#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AI_ORCHESTRATOR_SRC = REPO_ROOT / 'apps/ai-orchestrator/src'
if str(AI_ORCHESTRATOR_SRC) not in sys.path:
    sys.path.insert(0, str(AI_ORCHESTRATOR_SRC))

from ai_orchestrator.models import RetrievalProfile
from ai_orchestrator.retrieval import _build_query_plan
from ai_orchestrator.graph_rag_runtime import select_graph_rag_method


CASES = [
    {
        'id': 'policy_eval',
        'query': 'Como funciona a politica de avaliacao, recuperacao e promocao da escola?',
        'expected_intent': 'policy_lookup',
        'expected_category_bias': 'policy',
        'expected_graph_rag_candidate': False,
        'expected_profile': 'default',
    },
    {
        'id': 'service_credentials',
        'query': 'Sintetize tudo o que uma familia precisa entender sobre secretaria, portal, credenciais e envio de documentos.',
        'expected_intent': 'corpus_overview',
        'expected_category_bias': 'institutional',
        'expected_graph_rag_candidate': True,
        'expected_graph_rag_method': 'global',
        'expected_profile': 'deep',
    },
    {
        'id': 'admissions_workflow',
        'query': 'Compare rematricula, transferencia e cancelamento destacando o que muda em prazo, documentos e consequencias.',
        'expected_intent': 'corpus_overview',
        'expected_graph_rag_candidate': True,
        'expected_graph_rag_method': 'global',
        'expected_profile': 'cheap',
        'expected_canonical_lane': 'public_bundle.process_compare',
    },
    {
        'id': 'family_survival_guide',
        'query': 'Se eu fosse um aluno novo e muito esquecido, quais regras e prazos eu mais correria risco de perder no primeiro mes?',
        'expected_intent': 'fact_lookup',
        'expected_graph_rag_method': 'global',
        'expected_profile': 'cheap',
        'expected_canonical_lane': 'public_bundle.first_month_risks',
    },
]


def main() -> int:
    results: list[dict[str, object]] = []
    for case in CASES:
        plan = _build_query_plan(
            query=str(case['query']),
            top_k=6,
            category=None,
            visibility='public',
            enable_query_variants=True,
            candidate_pool_size=12,
            cheap_candidate_pool_size=8,
            deep_candidate_pool_size=18,
            profile_override=None,
        )
        graph_method = select_graph_rag_method(str(case['query']))
        results.append(
            {
                'id': case['id'],
                'query': case['query'],
                'intent': plan.intent,
                'profile': plan.profile.value,
                'category_bias': plan.category_bias,
                'canonical_lane': plan.canonical_lane,
                'graph_rag_candidate': plan.graph_rag_candidate,
                'graph_rag_method': graph_method,
                'passed': (
                    plan.intent == case.get('expected_intent', plan.intent)
                    and plan.profile is RetrievalProfile(case.get('expected_profile', plan.profile.value))
                    and plan.category_bias == case.get('expected_category_bias', plan.category_bias)
                    and plan.canonical_lane == case.get('expected_canonical_lane', plan.canonical_lane)
                    and plan.graph_rag_candidate == case.get('expected_graph_rag_candidate', plan.graph_rag_candidate)
                    and graph_method == case.get('expected_graph_rag_method', graph_method)
                ),
            }
        )
    passed = sum(1 for item in results if item['passed'])
    payload = {'passed': passed, 'total': len(results), 'results': results}
    report_path = REPO_ROOT / 'artifacts/retrieval-query-plan-probe.json'
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(report_path)
    print(f'passed={passed}/{len(results)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
