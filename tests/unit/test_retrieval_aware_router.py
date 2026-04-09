from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.retrieval_aware_router import (
    build_public_evidence_probe,
    build_routing_decision,
    infer_public_topic,
)


def test_infer_public_topic_detects_governance_channels() -> None:
    topic = infer_public_topic(
        message='Se uma familia precisa entender por onde um tema caminha entre secretaria, coordenacao, direcao e canais oficiais, qual e a trilha institucional?',
        primary_act='service_routing',
        secondary_acts=(),
    )
    assert topic == 'governance_channels'


def test_public_evidence_probe_uses_supports_and_summary_hits() -> None:
    evidence_pack = SimpleNamespace(
        supports=[
            SimpleNamespace(
                label='governance',
                detail='Secretaria faz a triagem inicial, coordenacao acompanha o caso e a direcao recebe escalonamentos formais.',
                excerpt='Secretaria, coordenacao e direcao aparecem como trilha de encaminhamento institucional.',
            )
        ]
    )
    probe = build_public_evidence_probe(
        message='Qual e a trilha entre secretaria, coordenacao e direcao?',
        canonical_lane='public_bundle.governance_protocol',
        primary_act='service_routing',
        secondary_acts=('contacts',),
        evidence_pack=evidence_pack,
        retrieval_search=None,
        summary_store_hits=2,
    )
    assert probe.topic == 'governance_channels'
    assert probe.canonical_lane == 'public_bundle.governance_protocol'
    assert probe.support_count == 1
    assert probe.summary_store_hits == 2
    assert probe.bundle_confidence >= 0.7
    assert probe.topic_match_score > 0.0
    assert probe.evidence_fingerprint


def test_routing_decision_blocks_profile_for_open_documentary_topics() -> None:
    probe = build_public_evidence_probe(
        message='Sem repetir slogans, que arquitetura aparece no contraturno com oficinas, refeicao, estudo acompanhado e permanencia?',
        canonical_lane=None,
        primary_act='highlight',
        secondary_acts=('features', 'schedule'),
        evidence_pack=None,
        retrieval_search=None,
        summary_store_hits=1,
    )
    decision = build_routing_decision(probe=probe, llm_forced_mode=False)
    assert decision.allow_documentary_synthesis is True
    assert decision.block_profile_fallback is True
    assert decision.prefer_deterministic is False


def test_public_evidence_probe_reads_real_retrieval_hits() -> None:
    retrieval_search = SimpleNamespace(
        hits=[
            SimpleNamespace(
                section_title='Rotina da tarde',
                parent_ref_key='programa-periodo-integral',
                labels={'topic': ['contraturno', 'oficinas']},
                text_excerpt='No contraturno, a escola combina estudo acompanhado, oficinas e permanencia.',
                contextual_summary='Programa de periodo integral com refeicao e permanencia.',
                fused_score=0.91,
                document_score=0.88,
            )
        ],
        document_groups=[
            SimpleNamespace(
                section_titles=['Rotina da tarde', 'Atividades complementares'],
                parent_ref_key='programa-periodo-integral',
                category='public_docs',
                primary_excerpt='Contraturno com oficinas e estudo acompanhado.',
                primary_summary='Reflexo da jornada ampliada com refeicao e permanencia.',
                document_score=0.88,
            )
        ],
        query_plan=SimpleNamespace(intent='corpus_overview'),
    )
    probe = build_public_evidence_probe(
        message='Sem repetir slogans, que arquitetura aparece no contraturno com oficinas, refeicao, estudo acompanhado e permanencia?',
        canonical_lane='public_bundle.integral_study_support',
        primary_act='features',
        secondary_acts=('features', 'schedule'),
        evidence_pack=None,
        retrieval_search=retrieval_search,
        summary_store_hits=1,
    )
    assert probe.hit_count == 1
    assert probe.document_group_count == 1
    assert probe.topic_match_score >= 0.5
    assert probe.query_intent == 'corpus_overview'
