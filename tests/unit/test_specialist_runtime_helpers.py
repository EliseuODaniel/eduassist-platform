from __future__ import annotations

from ai_orchestrator_specialist.public_query_patterns import (
    _extract_teacher_subject,
    _looks_like_admin_finance_combo_query,
    _looks_like_health_second_call_query,
)
from ai_orchestrator_specialist.restricted_doc_matching import (
    _internal_doc_hit_score,
    _looks_like_internal_document_query,
)


def test_extract_teacher_subject_stops_at_conjunction() -> None:
    assert _extract_teacher_subject('Qual o nome do professor de matematica ou da coordenacao?') == 'matematica'


def test_admin_finance_combo_query_detects_regularidade_and_finance() -> None:
    assert _looks_like_admin_finance_combo_query(
        'Quero a regularidade documental e a situacao financeira com boletos e mensalidades.'
    )


def test_health_second_call_query_detects_attested_exam_miss() -> None:
    assert _looks_like_health_second_call_query(
        'Se eu perder uma prova por motivo de saude com atestado, como funciona a segunda chamada?'
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
