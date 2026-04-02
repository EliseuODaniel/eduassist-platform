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
    compose_public_calendar_visibility,
    compose_public_canonical_lane_answer,
    compose_public_conduct_frequency_recovery_bridge,
    compose_public_facilities_and_study_support,
    compose_public_family_new_calendar_assessment_enrollment,
    compose_public_first_month_risks,
    compose_public_health_authorizations_bridge,
    compose_public_permanence_and_family_support,
    compose_public_process_compare,
    compose_public_transversal_year_bundle,
    match_public_canonical_lane,
)


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text.lower()).strip()
    return text


def _looks_like_family_new_calendar_enrollment_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(
            term in normalized
            for term in {
                "familia nova",
                "família nova",
                "pais novos",
                "responsavel novo",
                "responsável novo",
                "familia entrando agora",
                "família entrando agora",
                "familia entrando este ano",
                "família entrando este ano",
                "familia chegando agora",
                "família chegando agora",
                "primeira vez",
                "vai entrar este ano",
                "vai entrar pela primeira vez",
                "pais estreando",
                "pais estreando na escola",
                "pais entrando agora",
                "entrando agora",
                "chegando agora",
                "primeiro filho",
                "primeira matricula",
                "primeira matrícula",
                "comeco das aulas",
                "começo das aulas",
            }
        )
        and any(term in normalized for term in {"calendario", "calendário", "rotina", "datas", "inicio do ano", "início do ano", "primeiro bimestre", "aulas"})
        and any(term in normalized for term in {"matricula", "matrícula", "avaliacao", "avaliação", "provas", "processo de ingresso", "ingresso"})
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
    return (
        any(term in normalized for term in {"primeiro mes", "primeiro mês", "comeco do ano", "começo do ano", "primeiras semanas"})
        and any(term in normalized for term in {"riscos", "esquecido", "prazo", "deslizes", "erros", "problema", "problemas", "comprometem", "baguncam", "bagunçam"})
        and any(term in normalized for term in {"credenciais", "documentos", "documentacao", "rotina"})
    )


def _looks_like_process_compare_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(term in normalized for term in {"rematricula", "rematrícula"})
        and any(term in normalized for term in {"transferencia", "transferência", "cancelamento"})
        and any(term in normalized for term in {"compare", "destacando", "o que muda", "na pratica", "na prática", "se diferenciam"})
    )


def _looks_like_conduct_frequency_recovery_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(term in normalized for term in {"disciplina", "regulamentos", "regulamento", "convivencia", "convivência"})
        and any(term in normalized for term in {"frequencia", "frequência", "faltas", "falta"})
        and any(term in normalized for term in {"recuperacao", "recuperação"})
    )


def _looks_like_transversal_year_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(term in normalized for term in {"responsaveis", "responsáveis", "familia", "família", "relacionamento com responsaveis", "relacionamento com responsáveis"})
        and any(term in normalized for term in {"avaliacoes", "avaliações", "avaliacao", "avaliação", "provas"})
        and any(term in normalized for term in {"estudo orientado", "canais digitais", "portal", "telegram", "digitais", "comunicados digitais", "comunicacao digital", "comunicação digital"})
    )


def _looks_like_facilities_study_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(term in normalized for term in {"biblioteca", "laboratorios", "laboratório", "laboratorio", "laboratórios"})
        and any(term in normalized for term in {"estudo", "apoio", "ensino medio", "ensino médio"})
    )


def _looks_like_visibility_boundary_query(message: str) -> bool:
    normalized = _normalize_text(message)
    has_visibility_channel = any(
        term in normalized
        for term in {"canais digitais", "portal", "calendario", "calendário", "canais oficiais"}
    )
    has_public_visibility = any(
        term in normalized
        for term in {"publico", "público", "publica", "pública", "aberto", "aberta", "fronteira", "limite"}
    )
    has_auth_visibility = any(
        term in normalized
        for term in {
            "autenticacao",
            "autenticação",
            "autenticado",
            "autenticada",
            "login",
            "senha",
            "exige autenticacao",
            "exige autenticação",
            "depende de autenticacao",
            "depende de autenticação",
        }
    )
    return has_visibility_channel and has_public_visibility and has_auth_visibility


def _looks_like_public_graph_rag_query(message: str) -> bool:
    if any(
        detector(message)
        for detector in (
            _looks_like_permanence_family_query,
            _looks_like_health_authorization_bridge_query,
            _looks_like_first_month_risks_query,
            _looks_like_process_compare_query,
            _looks_like_conduct_frequency_recovery_query,
            _looks_like_transversal_year_query,
            _looks_like_facilities_study_query,
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
    canonical_lane = match_public_canonical_lane(message)
    canonical_supports: dict[str, tuple[str, str, list[MessageEvidenceSupport]]] = {
        "public_bundle.teacher_directory_boundary": (
            "specialist_supervisor_preflight:teacher_directory_boundary",
            "teacher_directory_boundary",
            [
                MessageEvidenceSupport(kind="profile", label="Diretorio publico", detail="leadership_team / service_catalog"),
            ],
        ),
        "public_bundle.calendar_week": (
            "specialist_supervisor_preflight:calendar_week",
            "calendar_week",
            [
                MessageEvidenceSupport(kind="timeline", label="Timeline publica", detail="v1/public/timeline"),
                MessageEvidenceSupport(kind="calendar", label="Calendario publico", detail="v1/calendar/public"),
            ],
        ),
        "public_bundle.year_three_phases": (
            "specialist_supervisor_preflight:year_three_phases",
            "year_three_phases",
            [
                MessageEvidenceSupport(kind="timeline", label="Timeline publica", detail="v1/public/timeline"),
                MessageEvidenceSupport(kind="calendar", label="Calendario publico", detail="v1/calendar/public"),
            ],
        ),
        "public_bundle.academic_policy_overview": (
            "specialist_supervisor_preflight:academic_policy_overview",
            "academic_policy_overview",
            [
                MessageEvidenceSupport(kind="policy", label="Academic policy", detail="academic_policy"),
                MessageEvidenceSupport(kind="document", label="Politica de Avaliacao", detail="data/corpus/public/politica-avaliacao-recuperacao-e-promocao.md"),
            ],
        ),
        "public_bundle.conduct_frequency_punctuality": (
            "specialist_supervisor_preflight:conduct_frequency_punctuality",
            "conduct_frequency_punctuality",
            [
                MessageEvidenceSupport(kind="document", label="Manual de Regulamentos Gerais", detail="data/corpus/public/manual-regulamentos-gerais.md"),
                MessageEvidenceSupport(kind="policy", label="Attendance policy", detail="academic_policy.attendance_policy"),
            ],
        ),
    }
    if canonical_lane in canonical_supports:
        answer_text = compose_public_canonical_lane_answer(canonical_lane, profile=profile)
        if answer_text:
            reason, graph_leaf, supports = canonical_supports[canonical_lane]
            return _institution_preflight_answer(
                answer_text=answer_text,
                reason=reason,
                graph_leaf=graph_leaf,
                summary="Resposta deterministica por canonical public lane antes do loop premium.",
                supports=supports,
            )

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

    if _looks_like_conduct_frequency_recovery_query(message):
        answer_text = compose_public_conduct_frequency_recovery_bridge(profile)
        if answer_text:
            return _institution_preflight_answer(
                answer_text=answer_text,
                reason="specialist_supervisor_preflight:conduct_frequency_recovery",
                graph_leaf="conduct_frequency_recovery",
                summary="Sintese deterministica cruzando regulamentos, frequencia e recuperacao.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Manual de Regulamentos Gerais", detail="data/corpus/public/manual-regulamentos-gerais.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Avaliacao, Recuperacao e Promocao", detail="data/corpus/public/politica-avaliacao-recuperacao-e-promocao.md"),
                    MessageEvidenceSupport(kind="document", label="Orientacao, Apoio e Vida Escolar", detail="data/corpus/public/orientacao-apoio-e-vida-escolar.md"),
                ],
            )

    if _looks_like_transversal_year_query(message):
        answer_text = compose_public_transversal_year_bundle()
        if answer_text:
            return _institution_preflight_answer(
                answer_text=answer_text,
                reason="specialist_supervisor_preflight:transversal_year_bundle",
                graph_leaf="transversal_year_bundle",
                summary="Sintese deterministica transversal entre comunicacao com familias, avaliacoes, estudo orientado e canais digitais.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Agenda de Avaliacoes 2026", detail="data/corpus/public/agenda-avaliacoes-recuperacoes-e-simulados-2026.md"),
                    MessageEvidenceSupport(kind="document", label="Orientacao, Apoio e Vida Escolar", detail="data/corpus/public/orientacao-apoio-e-vida-escolar.md"),
                    MessageEvidenceSupport(kind="document", label="Programa de Periodo Integral e Estudo Orientado", detail="data/corpus/public/programa-periodo-integral-e-estudo-orientado.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Uso do Portal, Aplicativo e Credenciais", detail="data/corpus/public/politica-uso-do-portal-aplicativo-e-credenciais.md"),
                ],
            )

    if _looks_like_visibility_boundary_query(message):
        answer_text = compose_public_calendar_visibility(profile)
        if answer_text:
            return _institution_preflight_answer(
                answer_text=answer_text,
                reason="specialist_supervisor_preflight:visibility_boundary",
                graph_leaf="visibility_boundary",
                summary="Sintese deterministica da fronteira entre conteudo publico e autenticado.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Calendario Letivo 2026", detail="data/corpus/public/calendario-letivo-2026.md"),
                    MessageEvidenceSupport(kind="document", label="Agenda de Avaliacoes 2026", detail="data/corpus/public/agenda-avaliacoes-recuperacoes-e-simulados-2026.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Uso do Portal, Aplicativo e Credenciais", detail="data/corpus/public/politica-uso-do-portal-aplicativo-e-credenciais.md"),
                ],
            )

    if _looks_like_facilities_study_query(message):
        answer_text = compose_public_facilities_and_study_support()
        if answer_text:
            return _institution_preflight_answer(
                answer_text=answer_text,
                reason="specialist_supervisor_preflight:facilities_study_support",
                graph_leaf="facilities_study_support",
                summary="Sintese deterministica sobre biblioteca, laboratorios e apoio ao estudo.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Servicos e Espacos Escolares", detail="data/corpus/public/servicos-e-espacos-escolares.md"),
                    MessageEvidenceSupport(kind="document", label="Programa de Periodo Integral e Estudo Orientado", detail="data/corpus/public/programa-periodo-integral-e-estudo-orientado.md"),
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
