from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator_specialist.public_query_patterns import (
    _extract_teacher_subject,
    _looks_like_admin_finance_combo_query,
    _looks_like_calendar_week_query,
    _looks_like_health_second_call_query,
)
from ai_orchestrator_specialist.restricted_doc_matching import (
    _internal_doc_hit_score,
    _looks_like_internal_document_query,
)
from ai_orchestrator_specialist.support_workflow_helpers import (
    _detect_support_handoff_queue,
    _looks_like_human_handoff_request,
)


def test_extract_teacher_subject_stops_at_conjunction() -> None:
    assert _extract_teacher_subject('Qual o nome do professor de matematica ou da coordenacao?') == 'matematica'


def test_extract_teacher_subject_stops_at_followup_clause() -> None:
    assert (
        _extract_teacher_subject('Vocês divulgam o nome ou contato direto do professor de matematica? Se nao, para onde a familia deve ir?')
        == 'matematica'
    )


def test_admin_finance_combo_query_detects_regularidade_and_finance() -> None:
    assert _looks_like_admin_finance_combo_query(
        'Quero a regularidade documental e a situacao financeira com boletos e mensalidades.'
    )


def test_health_second_call_query_detects_attested_exam_miss() -> None:
    assert _looks_like_health_second_call_query(
        'Se eu perder uma prova por motivo de saude com atestado, como funciona a segunda chamada?'
    )


def test_calendar_week_query_detects_generic_public_calendar_prompt() -> None:
    assert _looks_like_calendar_week_query(
        'Dentro do calendario publico, quais eventos parecem mais importantes para familias e responsaveis?'
    )


def test_internal_document_query_and_hit_score_favor_specific_hits() -> None:
    query = 'O protocolo interno para responsaveis com escopo parcial fala algo sobre Telegram?'
    assert _looks_like_internal_document_query(query)
    strong_hit = {
        'title': 'Protocolo interno para responsaveis com escopo parcial no Telegram',
        'summary': 'Limites de acesso e uso do Telegram por responsaveis com escopo parcial.',
        'content': 'Telegram, escopo parcial e regras operacionais.',
        'document_score': 0.4,
    }
    weak_hit = {
        'title': 'Manual interno do professor',
        'summary': 'Registro de avaliacoes.',
        'content': 'Fluxos academicos gerais.',
        'document_score': 0.4,
    }
    assert _internal_doc_hit_score(query, strong_hit) > _internal_doc_hit_score(query, weak_hit)


def test_internal_document_query_matches_material_interno_prompt() -> None:
    assert _looks_like_internal_document_query(
        'No material interno do professor, como a escola orienta o registro de avaliacoes?'
    )


def test_internal_document_query_matches_orientacao_interna_prompt() -> None:
    assert _looks_like_internal_document_query(
        'Existe alguma orientacao interna sobre excursao internacional com hospedagem para o ensino medio?'
    )


def test_human_handoff_request_detects_explicit_secretaria_request() -> None:
    assert _looks_like_human_handoff_request('Quero falar com a secretaria agora.')


def test_detect_support_handoff_queue_routes_financial_message() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(message='Preciso falar sobre boletos e mensalidades.'),
        specialist_registry={},
        operational_memory=None,
    )
    assert _detect_support_handoff_queue(ctx) == 'financeiro'
