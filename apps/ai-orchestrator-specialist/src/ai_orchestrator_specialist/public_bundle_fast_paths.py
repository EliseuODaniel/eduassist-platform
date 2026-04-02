from __future__ import annotations

import re
import unicodedata
from typing import Any

from .answer_payloads import default_suggested_replies
from .models import (
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageIntentClassification,
    SupervisorAnswerPayload,
)
from .public_doc_knowledge import (
    compose_public_family_new_calendar_assessment_enrollment,
    compose_public_first_month_risks,
    compose_public_health_authorizations_bridge,
    compose_public_permanence_and_family_support,
    compose_public_process_compare,
)


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text.lower()).strip()
    return text


def _looks_like_family_new_calendar_enrollment_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(term in normalized for term in {"familia nova", "família nova", "pais novos", "responsavel novo", "responsável novo"})
        and any(term in normalized for term in {"calendario", "calendário", "rotina", "datas"})
        and any(term in normalized for term in {"matricula", "matrícula", "avaliacao", "avaliação", "provas"})
    )


def _looks_like_permanence_family_query(message: str) -> bool:
    normalized = _normalize_text(message)
    family_terms = {
        "familia",
        "família",
        "responsaveis",
        "responsáveis",
        "acompanhamento da familia",
        "acompanhamento da família",
        "acompanhe",
    }
    permanence_terms = {
        "permanencia",
        "permanência",
        "vida escolar",
        "apoio",
        "orientacao",
        "orientação",
    }
    return (
        any(term in normalized for term in family_terms)
        and sum(1 for term in permanence_terms if term in normalized) >= 2
    )


def _looks_like_health_authorization_bridge_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return all(
        term in normalized
        for term in {"saude", "medicacao", "segunda chamada", "saidas pedagogicas", "autorizacoes"}
    )


def _looks_like_first_month_risks_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return "primeiro mes" in normalized and any(term in normalized for term in {"riscos", "esquecido", "prazo"})


def _looks_like_process_compare_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(term in normalized for term in {"rematricula", "rematrícula"}) and any(
        term in normalized for term in {"transferencia", "transferência", "cancelamento"}
    ) and any(term in normalized for term in {"compare", "destacando", "o que muda"})


def _looks_like_public_graph_rag_query(message: str) -> bool:
    if any(
        detector(message)
        for detector in (
            _looks_like_permanence_family_query,
            _looks_like_health_authorization_bridge_query,
            _looks_like_first_month_risks_query,
            _looks_like_process_compare_query,
        )
    ):
        return True

    normalized = _normalize_text(message)
    relational_terms = {
        "mapa de dependencias",
        "dependencias",
        "relações indiretas",
        "relacoes indiretas",
        "se influenciam",
        "mostrando como",
        "repercutir",
        "repercute",
        "ao longo do ano",
        "transversal",
        "conecte",
    }
    topic_terms = {
        "calendario",
        "avaliacao",
        "avaliacoes",
        "recuperacao",
        "portal",
        "credenciais",
        "autorizacoes",
        "biblioteca",
        "laboratorios",
        "laboratorio",
        "comunicacao",
        "responsaveis",
        "rotinas operacionais",
        "canais digitais",
        "regulamentos",
        "politicas",
    }
    topic_count = sum(1 for term in topic_terms if term in normalized)
    return topic_count >= 3 and any(term in normalized for term in relational_terms)


def _institution_preflight_answer(
    *,
    answer_text: str,
    reason: str,
    graph_leaf: str,
    summary: str,
    supports: list[MessageEvidenceSupport],
) -> SupervisorAnswerPayload:
    return SupervisorAnswerPayload(
        message_text=answer_text,
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain="institution",
            access_tier="public",
            confidence=0.99,
            reason=reason,
        ),
        evidence_pack=MessageEvidencePack(
            strategy="direct_answer",
            summary=summary,
            source_count=len(supports),
            support_count=len(supports),
            supports=supports,
        ),
        suggested_replies=default_suggested_replies("institution"),
        graph_path=["specialist_supervisor", "preflight", graph_leaf],
        reason=reason,
    )


def _preflight_public_doc_bundle_answer(profile: dict[str, Any] | None, message: str) -> SupervisorAnswerPayload | None:
    normalized = _normalize_text(message)

    if _looks_like_family_new_calendar_enrollment_query(message):
        answer_text = compose_public_family_new_calendar_assessment_enrollment()
        if answer_text:
            return _institution_preflight_answer(
                answer_text=answer_text,
                reason="specialist_supervisor_preflight:family_new_calendar_enrollment",
                graph_leaf="family_new_calendar_enrollment",
                summary="Sintese deterministica de familia nova antes do loop premium.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Calendario Letivo 2026", detail="data/corpus/public/calendario-letivo-2026.md"),
                    MessageEvidenceSupport(kind="document", label="Agenda de Avaliacoes 2026", detail="data/corpus/public/agenda-avaliacoes-recuperacoes-e-simulados-2026.md"),
                    MessageEvidenceSupport(kind="document", label="Manual de Matricula", detail="data/corpus/public/manual-matricula-ensino-medio.md"),
                ],
            )

    if _looks_like_permanence_family_query(message):
        answer_text = compose_public_permanence_and_family_support(profile)
        if answer_text:
            return _institution_preflight_answer(
                answer_text=answer_text,
                reason="specialist_supervisor_preflight:permanence_family_support",
                graph_leaf="permanence_family_support",
                summary="Sintese deterministica sobre permanencia escolar e acompanhamento da familia.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Orientacao, Apoio e Vida Escolar", detail="data/corpus/public/orientacao-apoio-e-vida-escolar.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Avaliacao, Recuperacao e Promocao", detail="data/corpus/public/politica-avaliacao-recuperacao-e-promocao.md"),
                    MessageEvidenceSupport(kind="policy", label="Projeto de vida", detail="academic_policy.project_of_life_summary"),
                ],
            )

    if _looks_like_health_authorization_bridge_query(message):
        answer_text = compose_public_health_authorizations_bridge()
        if answer_text:
            return _institution_preflight_answer(
                answer_text=answer_text,
                reason="specialist_supervisor_preflight:health_authorizations_bridge",
                graph_leaf="health_authorizations_bridge",
                summary="Sintese deterministica cruzando saude, medicacao, segunda chamada e autorizacoes.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Protocolo de Saude, Medicacao e Emergencias", detail="data/corpus/public/protocolo-saude-medicacao-e-emergencias.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Avaliacao, Recuperacao e Promocao", detail="data/corpus/public/politica-avaliacao-recuperacao-e-promocao.md"),
                    MessageEvidenceSupport(kind="document", label="Saidas Pedagogicas, Eventos e Autorizacoes", detail="data/corpus/public/saidas-pedagogicas-eventos-e-autorizacoes.md"),
                ],
            )

    if _looks_like_first_month_risks_query(message):
        answer_text = compose_public_first_month_risks(profile)
        if answer_text:
            return _institution_preflight_answer(
                answer_text=answer_text,
                reason="specialist_supervisor_preflight:first_month_risks",
                graph_leaf="first_month_risks",
                summary="Sintese deterministica dos riscos operacionais do primeiro mes.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Secretaria, Documentacao e Prazos", detail="data/corpus/public/secretaria-documentacao-e-prazos.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Uso do Portal, Aplicativo e Credenciais", detail="data/corpus/public/politica-uso-do-portal-aplicativo-e-credenciais.md"),
                    MessageEvidenceSupport(kind="document", label="Manual de Regulamentos Gerais", detail="data/corpus/public/manual-regulamentos-gerais.md"),
                ],
            )

    if _looks_like_process_compare_query(message):
        answer_text = compose_public_process_compare()
        if answer_text:
            return _institution_preflight_answer(
                answer_text=answer_text,
                reason="specialist_supervisor_preflight:process_compare",
                graph_leaf="process_compare",
                summary="Comparacao deterministica de rematricula, transferencia e cancelamento.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Rematricula, Transferencia e Cancelamento 2026", detail="data/corpus/public/rematricula-transferencia-e-cancelamento-2026.md"),
                ],
            )

    if "secretaria" in normalized and "credencia" in normalized and "document" in normalized:
        answer_text = (
            "Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; "
            "o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca."
        )
        return _institution_preflight_answer(
            answer_text=answer_text,
            reason="specialist_supervisor_preflight:service_credentials_bundle",
            graph_leaf="service_credentials_bundle",
            summary="Resumo publico deterministico sobre secretaria, portal, credenciais e documentos.",
            supports=[
                MessageEvidenceSupport(kind="document", label="Secretaria, Documentacao e Prazos", detail="data/corpus/public/secretaria-documentacao-e-prazos.md"),
                MessageEvidenceSupport(kind="document", label="Politica de Uso do Portal, Aplicativo e Credenciais", detail="data/corpus/public/politica-uso-do-portal-aplicativo-e-credenciais.md"),
            ],
        )

    return None
