from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.candidate_builder import build_response_candidate
from ai_orchestrator.candidate_chooser import choose_best_candidate
from ai_orchestrator.models import ConversationChannel, MessageResponseRequest
from ai_orchestrator.retrieval_aware_router import build_public_evidence_probe
from ai_orchestrator.serving_policy import LoadSnapshot, build_public_serving_policy


def _settings(**overrides: object) -> SimpleNamespace:
    payload = {
        'public_response_cache_enabled': True,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _request(message: str) -> MessageResponseRequest:
    return MessageResponseRequest(message=message, channel=ConversationChannel.telegram)


def test_candidate_chooser_prefers_deterministic_when_bundle_confident() -> None:
    message = 'Como a familia organiza calendario, matricula e avaliacoes no primeiro bimestre?'
    probe = build_public_evidence_probe(
        message=message,
        canonical_lane='public_bundle.family_new_calendar_assessment_enrollment',
        primary_act='canonical_fact',
        secondary_acts=('timeline',),
        evidence_pack=None,
        retrieval_search=None,
    )
    policy = build_public_serving_policy(
        settings=_settings(),
        stack_name='langgraph',
        request=_request(message),
        probe=probe,
        load_snapshot=LoadSnapshot(),
    )
    deterministic = build_response_candidate(
        kind='deterministic',
        text='Resposta canônica grounded.',
        reason='public_profile_deterministic',
        source_count=2,
        support_count=2,
    )
    documentary = build_response_candidate(
        kind='documentary_synthesis',
        text='Resposta documental sintetizada.',
        reason='public_open_documentary_synthesis',
        used_llm=True,
        llm_stages=('answer_composition',),
        source_count=2,
        support_count=2,
    )
    chosen = choose_best_candidate(
        candidates=[deterministic, documentary],
        probe=probe,
        policy=policy,
    )
    assert chosen is not None
    assert chosen.candidate.kind == 'deterministic'


def test_candidate_chooser_prefers_documentary_for_open_documentary_topic() -> None:
    message = 'Sem repetir slogans, que arquitetura de rotina escolar aparece quando se combinam turno estendido, oficinas, refeicao, estudo acompanhado e permanencia no contraturno?'
    probe = build_public_evidence_probe(
        message=message,
        canonical_lane=None,
        primary_act='highlight',
        secondary_acts=('features', 'schedule'),
        evidence_pack=None,
        retrieval_search=None,
        summary_store_hits=2,
    )
    policy = build_public_serving_policy(
        settings=_settings(),
        stack_name='langgraph',
        request=_request(message),
        probe=probe,
        load_snapshot=LoadSnapshot(),
    )
    deterministic = build_response_candidate(
        kind='deterministic',
        text='Resposta genérica de perfil institucional.',
        reason='public_profile',
        source_count=1,
        support_count=1,
    )
    documentary = build_response_candidate(
        kind='documentary_synthesis',
        text='Resposta sintética sobre contraturno, oficinas, alimentação e permanência.',
        reason='public_open_documentary_synthesis',
        used_llm=True,
        llm_stages=('answer_composition',),
        source_count=3,
        support_count=3,
    )
    chosen = choose_best_candidate(
        candidates=[deterministic, documentary],
        probe=probe,
        policy=policy,
    )
    assert chosen is not None
    assert chosen.candidate.kind == 'documentary_synthesis'


def test_candidate_chooser_uses_topic_coverage_to_escape_weak_deterministic_bundle() -> None:
    message = 'Sem repetir slogans, que arquitetura de rotina escolar aparece quando se combinam turno estendido, oficinas, refeicao, estudo acompanhado e permanencia no contraturno?'
    probe = build_public_evidence_probe(
        message=message,
        canonical_lane='public_bundle.integral_study_support',
        primary_act='features',
        secondary_acts=('features', 'schedule'),
        evidence_pack=None,
        retrieval_search=None,
        summary_store_hits=2,
    )
    policy = build_public_serving_policy(
        settings=_settings(),
        stack_name='langgraph',
        request=_request(message),
        probe=probe,
        load_snapshot=LoadSnapshot(),
    )
    deterministic = build_response_candidate(
        kind='deterministic',
        text='Periodo integral e estudo orientado se completam como camadas de apoio ao estudante.',
        reason='public_profile_deterministic',
        source_count=1,
        support_count=1,
    )
    documentary = build_response_candidate(
        kind='documentary_synthesis',
        text='No contraturno, a rotina ampliada combina permanencia, estudo acompanhado, oficinas e refeicao no tempo estendido.',
        reason='public_open_documentary_synthesis',
        used_llm=True,
        llm_stages=('answer_composition',),
        source_count=3,
        support_count=3,
    )
    chosen = choose_best_candidate(
        candidates=[deterministic, documentary],
        probe=probe,
        policy=policy,
    )
    assert chosen is not None
    assert chosen.candidate.kind == 'documentary_synthesis'


def test_serving_policy_penalizes_llamaindex_when_recent_tail_is_high() -> None:
    message = 'Como a escola conecta saude, segunda chamada e reorganizacao pedagogica?'
    probe = build_public_evidence_probe(
        message=message,
        canonical_lane=None,
        primary_act='policy',
        secondary_acts=('timeline',),
        evidence_pack=None,
        retrieval_search=None,
        summary_store_hits=0,
    )
    policy = build_public_serving_policy(
        settings=_settings(),
        stack_name='llamaindex',
        request=_request(message),
        probe=probe,
        load_snapshot=LoadSnapshot(
            recent_request_count=10,
            recent_p95_latency_ms=5500.0,
            recent_timeout_rate=0.2,
        ),
    )
    assert policy.documentary_cost_penalty > 1.0
