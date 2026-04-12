from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from .answer_payloads import (
    access_tier_for_domain as _access_tier_for_domain,
)
from .answer_payloads import (
    default_suggested_replies as _default_suggested_replies,
)
from .models import (
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageIntentClassification,
    SupervisorAnswerPayload,
)
from .public_bundle_fast_paths import (
    _looks_like_first_month_risks_query,
    _looks_like_health_authorization_bridge_query,
    _looks_like_permanence_family_query,
    _looks_like_process_compare_query,
    _looks_like_public_graph_rag_query,
)
from .public_doc_knowledge import (
    compose_public_academic_policy_overview,
    compose_public_bolsas_and_processes,
    compose_public_conduct_policy_contextual_answer,
    compose_public_conduct_frequency_punctuality,
    compose_public_first_month_risks,
    compose_public_health_authorizations_bridge,
    compose_public_health_second_call,
    compose_public_permanence_and_family_support,
    compose_public_process_compare,
)
from .public_profile_answers import (
    _compose_attendance_policy_answer,
    _compose_calendar_week_answer,
    _compose_eval_calendar_answer,
    _compose_first_bimester_answer,
    _compose_passing_policy_answer,
    _compose_project_of_life_answer,
    _compose_timeline_bundle_answer,
    _compose_travel_planning_answer,
    _compose_year_three_phases_answer,
)
from .public_query_patterns import (
    _looks_like_attendance_policy_query,
    _looks_like_bolsas_and_processes_query,
    _looks_like_calendar_week_query,
    _looks_like_conduct_frequency_punctuality_query,
    _looks_like_enrollment_documents_query,
    _looks_like_eval_calendar_query,
    _looks_like_first_bimester_timeline_query,
    _looks_like_health_second_call_query,
    _looks_like_passing_policy_query,
    _looks_like_project_of_life_query,
    _looks_like_public_academic_policy_overview_query,
    _looks_like_timeline_lifecycle_query,
    _looks_like_travel_planning_query,
    _looks_like_year_three_phases_query,
)


@dataclass(frozen=True)
class ToolFirstPublicDeps:
    fetch_public_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    http_get: Callable[..., Awaitable[dict[str, Any] | None]]
    orchestrator_graph_rag_query: Callable[..., Awaitable[dict[str, Any] | None]]
    orchestrator_retrieval_search: Callable[..., Awaitable[dict[str, Any] | None]]
    citation_from_retrieval_hit: Callable[[dict[str, Any]], Any | None]
    select_public_graph_rag_fallback_hits: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    compose_public_graph_rag_fallback_answer: Callable[[str, list[dict[str, Any]]], str]
    supports_from_public_graph_rag_fallback_hits: Callable[[list[dict[str, Any]]], list[MessageEvidenceSupport]]
    safe_excerpt: Callable[..., str]
    timeline_entry: Callable[..., dict[str, Any] | None]
    format_brl: Callable[[Any], str]


def _build_public_tool_payload(
    *,
    message_text: str,
    domain: str,
    access_tier: str,
    confidence: float,
    reason: str,
    summary: str,
    supports: list[MessageEvidenceSupport],
    graph_leaf: str,
    suggested_domain: str | None = None,
    mode: str = "structured_tool",
    retrieval_backend: str | None = None,
    citations: list[Any] | None = None,
    risk_flags: list[str] | None = None,
) -> SupervisorAnswerPayload:
    strategy = "graph_rag" if mode == "graph_rag" else "structured_tools"
    if mode == "hybrid_retrieval":
        strategy = "hybrid_retrieval"
    resolved_retrieval_backend = str(retrieval_backend or "none")
    return SupervisorAnswerPayload(
        message_text=message_text,
        mode=mode,
        classification=MessageIntentClassification(
            domain=domain,
            access_tier=access_tier,
            confidence=confidence,
            reason=reason,
        ),
        retrieval_backend=resolved_retrieval_backend,
        citations=citations or [],
        evidence_pack=MessageEvidencePack(
            strategy=strategy,
            summary=summary,
            source_count=max(len(citations or supports), 1 if supports or citations else 0),
            support_count=len(supports),
            supports=supports,
        ),
        suggested_replies=_default_suggested_replies(suggested_domain or domain),
        graph_path=["specialist_supervisor", "tool_first", graph_leaf],
        risk_flags=risk_flags or [],
        reason=reason,
    )


async def maybe_tool_first_public_answer(
    ctx: Any,
    *,
    normalized: str,
    profile: dict[str, Any],
    deps: ToolFirstPublicDeps,
) -> SupervisorAnswerPayload | None:
    if (
        _looks_like_timeline_lifecycle_query(ctx.request.message)
        or
        _looks_like_calendar_week_query(ctx.request.message)
        or _looks_like_first_bimester_timeline_query(ctx.request.message)
        or _looks_like_eval_calendar_query(ctx.request.message)
        or _looks_like_travel_planning_query(ctx.request.message)
        or _looks_like_year_three_phases_query(ctx.request.message)
    ):
        timeline_payload, calendar_payload = await asyncio.gather(
            deps.fetch_public_payload(ctx, "/v1/public/timeline", "timeline"),
            deps.http_get(
                ctx.http_client,
                base_url=ctx.settings.api_core_url,
                path="/v1/calendar/public",
                token=ctx.settings.internal_api_token,
                params={"date_from": "2026-01-01", "date_to": "2026-12-31", "limit": 20},
            ),
        )
        entries = timeline_payload.get("entries") if isinstance(timeline_payload, dict) else []
        events = calendar_payload.get("events") if isinstance(calendar_payload, dict) else []
        answer_text = None
        reason = "specialist_supervisor_tool_first:public_calendar"
        support_label = "Calendario publico"
        if _looks_like_timeline_lifecycle_query(ctx.request.message):
            answer_text = _compose_timeline_bundle_answer(profile, ctx.request.message)
            reason = "specialist_supervisor_tool_first:timeline_lifecycle"
            support_label = "Linha do tempo publica"
        elif _looks_like_calendar_week_query(ctx.request.message):
            answer_text = _compose_calendar_week_answer(events if isinstance(events, list) else [])
            reason = "specialist_supervisor_tool_first:calendar_week"
            support_label = "Eventos publicos para familias"
        elif _looks_like_first_bimester_timeline_query(ctx.request.message):
            answer_text = _compose_first_bimester_answer(entries if isinstance(entries, list) else [], events if isinstance(events, list) else [])
            reason = "specialist_supervisor_tool_first:first_bimester_timeline"
            support_label = "Primeiro bimestre"
        elif _looks_like_eval_calendar_query(ctx.request.message):
            answer_text = _compose_eval_calendar_answer(events if isinstance(events, list) else [])
            reason = "specialist_supervisor_tool_first:eval_calendar"
            support_label = "Reunioes, simulados e provas"
        elif _looks_like_travel_planning_query(ctx.request.message):
            answer_text = _compose_travel_planning_answer(entries if isinstance(entries, list) else [], events if isinstance(events, list) else [])
            reason = "specialist_supervisor_tool_first:travel_planning"
            support_label = "Marcos de calendario"
        elif _looks_like_year_three_phases_query(ctx.request.message):
            answer_text = _compose_year_three_phases_answer(entries if isinstance(entries, list) else [], events if isinstance(events, list) else [])
            reason = "specialist_supervisor_tool_first:year_three_phases"
            support_label = "Fases do ano escolar"
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="calendar",
                access_tier="public",
                confidence=0.99,
                reason=reason,
                summary="Resposta deterministica baseada na timeline publica e no calendario publico.",
                supports=[
                    MessageEvidenceSupport(kind="timeline", label="Timeline publica", detail="v1/public/timeline"),
                    MessageEvidenceSupport(kind="calendar", label=support_label, detail="v1/calendar/public"),
                ],
                graph_leaf="public_calendar",
                suggested_domain="institution",
            )

    if _looks_like_enrollment_documents_query(ctx.request.message):
        admissions_docs = profile.get("admissions_required_documents") if isinstance(profile, dict) else None
        if isinstance(admissions_docs, list) and admissions_docs:
            lines = ["Hoje os documentos exigidos para matricula publicados pela escola sao:"]
            lines.extend(f"- {str(item).strip()}" for item in admissions_docs if str(item).strip())
            return _build_public_tool_payload(
                message_text="\n".join(lines),
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_tool_first:admissions_documents",
                summary="Resposta deterministica baseada na lista publica de documentos de matricula.",
                supports=[MessageEvidenceSupport(kind="profile", label="Documentos de matricula", detail="admissions_required_documents")],
                graph_leaf="admissions_documents",
            )

    if (
        not _looks_like_health_second_call_query(ctx.request.message)
        and _looks_like_public_academic_policy_overview_query(ctx.request.message)
    ):
        answer_text = compose_public_academic_policy_overview(profile)
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="academic",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_tool_first:academic_policy_overview",
                summary="Resposta deterministica combinando politica academica publica e corpus documental versionado.",
                supports=[
                    MessageEvidenceSupport(kind="policy", label="Academic policy", detail="academic_policy"),
                    MessageEvidenceSupport(kind="document", label="Politica de Avaliacao, Recuperacao e Promocao", detail="data/corpus/public/politica-avaliacao-recuperacao-e-promocao.md"),
                ],
                graph_leaf="academic_policy_overview",
                suggested_domain="academic",
            )

    if _looks_like_conduct_frequency_punctuality_query(ctx.request.message):
        answer_text = (
            compose_public_conduct_policy_contextual_answer(ctx.request.message, profile=profile)
            or compose_public_conduct_frequency_punctuality(profile)
        )
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="academic",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_tool_first:conduct_frequency_punctuality",
                summary="Resposta deterministica baseada no manual de regulamentos e na politica publica de frequencia.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Manual de Regulamentos Gerais", detail="data/corpus/public/manual-regulamentos-gerais.md"),
                    MessageEvidenceSupport(kind="policy", label="Politica de frequencia", detail="academic_policy.attendance_policy"),
                ],
                graph_leaf="conduct_frequency_punctuality",
                suggested_domain="academic",
            )

    if _looks_like_bolsas_and_processes_query(ctx.request.message):
        answer_text = compose_public_bolsas_and_processes(profile)
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_tool_first:bolsas_and_processes",
                summary="Resposta deterministica combinando edital de bolsas e documento de rematricula/transferencia/cancelamento.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Edital de Bolsas e Descontos 2026", detail="data/corpus/public/edital-bolsas-e-descontos-2026.md"),
                    MessageEvidenceSupport(kind="document", label="Rematricula, Transferencia e Cancelamento 2026", detail="data/corpus/public/rematricula-transferencia-e-cancelamento-2026.md"),
                ],
                graph_leaf="bolsas_and_processes",
            )

    if _looks_like_health_second_call_query(ctx.request.message):
        answer_text = compose_public_health_second_call()
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="academic",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_tool_first:health_second_call",
                summary="Resposta deterministica combinando protocolo de saude e politica de segunda chamada.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Protocolo de Saude, Medicacao e Emergencias", detail="data/corpus/public/protocolo-saude-medicacao-e-emergencias.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Avaliacao, Recuperacao e Promocao", detail="data/corpus/public/politica-avaliacao-recuperacao-e-promocao.md"),
                ],
                graph_leaf="health_second_call",
                suggested_domain="academic",
            )

    if _looks_like_permanence_family_query(ctx.request.message):
        answer_text = compose_public_permanence_and_family_support(profile)
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_tool_first:permanence_family_support",
                summary="Resposta deterministica baseada em apoio ao estudante, comunicacao com familias e politica publica de frequencia.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Orientacao, Apoio e Vida Escolar", detail="data/corpus/public/orientacao-apoio-e-vida-escolar.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Avaliacao, Recuperacao e Promocao", detail="data/corpus/public/politica-avaliacao-recuperacao-e-promocao.md"),
                    MessageEvidenceSupport(kind="policy", label="Projeto de vida", detail="academic_policy.project_of_life_summary"),
                ],
                graph_leaf="permanence_family_support",
            )

    if _looks_like_health_authorization_bridge_query(ctx.request.message):
        answer_text = compose_public_health_authorizations_bridge()
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_tool_first:health_authorizations_bridge",
                summary="Resposta deterministica cruzando saude, segunda chamada e autorizacoes de saida.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Protocolo de Saude, Medicacao e Emergencias", detail="data/corpus/public/protocolo-saude-medicacao-e-emergencias.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Avaliacao, Recuperacao e Promocao", detail="data/corpus/public/politica-avaliacao-recuperacao-e-promocao.md"),
                    MessageEvidenceSupport(kind="document", label="Saidas Pedagogicas, Eventos e Autorizacoes", detail="data/corpus/public/saidas-pedagogicas-eventos-e-autorizacoes.md"),
                ],
                graph_leaf="health_authorizations_bridge",
            )

    if _looks_like_first_month_risks_query(ctx.request.message):
        answer_text = compose_public_first_month_risks(profile)
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_tool_first:first_month_risks",
                summary="Resposta deterministica baseada em secretaria, credenciais, vinculacao e frequencia.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Secretaria, Documentacao e Prazos", detail="data/corpus/public/secretaria-documentacao-e-prazos.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Uso do Portal, Aplicativo e Credenciais", detail="data/corpus/public/politica-uso-do-portal-aplicativo-e-credenciais.md"),
                    MessageEvidenceSupport(kind="document", label="Manual de Regulamentos Gerais", detail="data/corpus/public/manual-regulamentos-gerais.md"),
                ],
                graph_leaf="first_month_risks",
            )

    if _looks_like_process_compare_query(ctx.request.message):
        answer_text = compose_public_process_compare()
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_tool_first:process_compare",
                summary="Resposta deterministica baseada no documento publico de rematricula, transferencia e cancelamento.",
                supports=[MessageEvidenceSupport(kind="document", label="Rematricula, Transferencia e Cancelamento 2026", detail="data/corpus/public/rematricula-transferencia-e-cancelamento-2026.md")],
                graph_leaf="process_compare",
            )

    if ctx.request.allow_graph_rag and _looks_like_public_graph_rag_query(ctx.request.message):
        graph_rag_payload = await deps.orchestrator_graph_rag_query(ctx, query=ctx.request.message)
        result = graph_rag_payload.get("result") if isinstance(graph_rag_payload, dict) else None
        if isinstance(result, dict) and str(result.get("text") or "").strip():
            requested_method = str(result.get("requested_method") or result.get("method") or "global").strip()
            attempted_methods = result.get("attempted_methods")
            attempt_detail = ", ".join(str(item).strip() for item in attempted_methods if str(item).strip()) if isinstance(attempted_methods, list) else requested_method
            return _build_public_tool_payload(
                message_text=str(result.get("text") or "").strip(),
                domain="institution",
                access_tier="public",
                confidence=0.96,
                reason="specialist_supervisor_tool_first:graph_rag",
                summary="Resposta direta via GraphRAG compartilhado, sem loop manager/judge.",
                supports=[
                    MessageEvidenceSupport(kind="graph_rag", label="Metodo", detail=str(result.get("method") or requested_method)),
                    MessageEvidenceSupport(kind="graph_rag", label="Tentativas", detail=attempt_detail),
                ],
                graph_leaf="graph_rag",
                mode="graph_rag",
                retrieval_backend="graph_rag",
            )
        retrieval_payload = await deps.orchestrator_retrieval_search(
            ctx,
            query=ctx.request.message,
            visibility="public",
            category=None,
            top_k=6,
        )
        fallback_hits = deps.select_public_graph_rag_fallback_hits(
            retrieval_payload.get("hits") if isinstance(retrieval_payload, dict) and isinstance(retrieval_payload.get("hits"), list) else []
        )
        if fallback_hits:
            citations = [citation for hit in fallback_hits if (citation := deps.citation_from_retrieval_hit(hit)) is not None]
            supports = deps.supports_from_public_graph_rag_fallback_hits(fallback_hits)
            return _build_public_tool_payload(
                message_text=deps.compose_public_graph_rag_fallback_answer(ctx.request.message, fallback_hits),
                domain="institution",
                access_tier="public",
                confidence=0.9,
                reason="specialist_supervisor_tool_first:graph_rag_fallback_hybrid",
                summary="GraphRAG compartilhado nao fechou no budget sincrono; resposta grounded por retrieval publico.",
                supports=supports,
                graph_leaf="graph_rag_fallback_hybrid",
                mode="hybrid_retrieval",
                retrieval_backend="qdrant_hybrid",
                citations=citations,
                risk_flags=["graphrag_unavailable"],
            )

    if profile and _looks_like_project_of_life_query(ctx.request.message):
        answer_text = _compose_project_of_life_answer(profile)
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="institution",
                access_tier=_access_tier_for_domain("institution", ctx.request.user.authenticated),
                confidence=0.99,
                reason="specialist_supervisor_tool_first:project_of_life_policy",
                summary="Resposta deterministica baseada na politica academica publica da escola.",
                supports=[MessageEvidenceSupport(kind="policy", label="Projeto de vida", detail=deps.safe_excerpt(answer_text, limit=180))],
                graph_leaf="project_of_life_policy",
            )

    if profile and _looks_like_attendance_policy_query(ctx.request.message):
        answer_text = _compose_attendance_policy_answer(profile, message=ctx.request.message)
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="academic",
                access_tier=_access_tier_for_domain("academic", ctx.request.user.authenticated),
                confidence=0.99,
                reason="specialist_supervisor_tool_first:attendance_policy",
                summary="Resposta deterministica baseada na politica publica de frequencia.",
                supports=[MessageEvidenceSupport(kind="policy", label="Politica de frequencia", detail=deps.safe_excerpt(answer_text, limit=180))],
                graph_leaf="attendance_policy",
                suggested_domain="academic",
            )

    if profile and _looks_like_passing_policy_query(ctx.request.message):
        answer_text = _compose_passing_policy_answer(profile, authenticated=ctx.request.user.authenticated)
        if answer_text:
            return _build_public_tool_payload(
                message_text=answer_text,
                domain="academic",
                access_tier=_access_tier_for_domain("academic", ctx.request.user.authenticated),
                confidence=0.99,
                reason="specialist_supervisor_tool_first:passing_policy",
                summary="Resposta deterministica baseada na politica publica de aprovacao.",
                supports=[MessageEvidenceSupport(kind="policy", label="Meta de aprovacao", detail="media publica 7,0/10")],
                graph_leaf="passing_policy",
                suggested_domain="academic",
            )

    if profile and (
        "mandar documentos" in normalized
        or "enviar documentos" in normalized
        or ("canais" in normalized and "documentos" in normalized)
        or ("prazos" in normalized and "secretaria" in normalized and ("documentos" in normalized or "declaracoes" in normalized or "atualizacoes cadastrais" in normalized))
    ):
        policy = profile.get("document_submission_policy")
        if isinstance(policy, dict):
            channels = policy.get("accepted_channels") if isinstance(policy.get("accepted_channels"), list) else []
            rendered_channels = ", ".join(str(item).strip() for item in channels if str(item).strip())
            warning = str(policy.get("warning") or "").strip()
            notes = str(policy.get("notes") or "").strip()
            service_catalog = (profile or {}).get("service_catalog")
            secretaria_eta = ""
            if isinstance(service_catalog, list):
                secretaria_entry = next(
                    (
                        item
                        for item in service_catalog
                        if isinstance(item, dict) and str(item.get("service_key") or "").strip() == "secretaria_escolar"
                    ),
                    None,
                )
                if isinstance(secretaria_entry, dict):
                    secretaria_eta = str(secretaria_entry.get("typical_eta") or "").strip()
            return _build_public_tool_payload(
                message_text=(
                    "Voce pode mandar documentos pelo portal institucional, pelo email da secretaria "
                    "ou levar na secretaria presencial para conferencia final. "
                    + (f"Prazo esperado da secretaria: {secretaria_eta}. " if secretaria_eta else "")
                    + f"{notes} {warning}"
                ).strip(),
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_tool_first:document_submission_policy",
                summary="Resposta deterministica baseada na politica publica de envio documental.",
                supports=[
                    MessageEvidenceSupport(kind="policy", label="Canais aceitos", detail=rendered_channels),
                    MessageEvidenceSupport(kind="policy", label="Observacao", detail=deps.safe_excerpt(warning or notes)),
                ],
                graph_leaf="document_submission_policy",
            )

    timeline_query = (
        any(term in normalized for term in {"matricula de 2026", "matrícula de 2026", "abre a matricula", "abre a matrícula"})
        or any(
            term in normalized
            for term in {
                "quando comecam as aulas",
                "quando começam as aulas",
                "comeco das aulas",
                "começo das aulas",
                "inicio das aulas",
                "início das aulas",
                "quando comeca o ano letivo",
                "quando começa o ano letivo",
                "inicio do ano letivo",
                "início do ano letivo",
            }
        )
        or (
            any(term in normalized for term in {"ordene", "ordem", "sequencia", "sequência"})
            and "matricula" in normalized
            and any(term in normalized for term in {"aulas", "ano letivo"})
        )
    )
    if timeline_query:
        timeline_payload = await deps.fetch_public_payload(ctx, "/v1/public/timeline", "timeline")
        entries = timeline_payload.get("entries") if isinstance(timeline_payload, dict) else None
        if isinstance(entries, list):
            recent_messages = (
                ctx.conversation_context.get("recent_messages", [])
                if isinstance(ctx.conversation_context, dict)
                else []
            )
            recent_user_messages = [
                str(item.get("content") or "").strip()
                for item in recent_messages[-6:]
                if isinstance(item, dict) and str(item.get("sender_type") or "").lower() == "user"
            ]
            combined_answer = _compose_timeline_bundle_answer(
                {"public_timeline": entries},
                ctx.request.message,
                recent_user_messages=recent_user_messages,
            )
            if combined_answer:
                return _build_public_tool_payload(
                    message_text=combined_answer,
                    domain="calendar",
                    access_tier="public",
                    confidence=0.99,
                    reason="specialist_supervisor_tool_first:public_timeline_bundle",
                    summary="Resposta deterministica combinando matricula e inicio das aulas.",
                    supports=[MessageEvidenceSupport(kind="timeline", label="Linha do tempo publica", detail=deps.safe_excerpt(combined_answer))],
                    graph_leaf="public_timeline_bundle",
                    suggested_domain="institution",
                )
            item = deps.timeline_entry(entries, topic_fragment="admissions_opening" if any(term in normalized for term in {"matricula", "matrícula"}) else "school_year_start")
            if isinstance(item, dict):
                summary = str(item.get("summary") or "").strip()
                notes = str(item.get("notes") or "").strip()
                answer_text = f"{summary} {notes}".strip()
                return _build_public_tool_payload(
                    message_text=answer_text,
                    domain="calendar",
                    access_tier="public",
                    confidence=0.99,
                    reason="specialist_supervisor_tool_first:public_timeline",
                    summary="Resposta deterministica baseada na timeline publica institucional.",
                    supports=[MessageEvidenceSupport(kind="timeline", label=str(item.get("title") or "Timeline"), detail=deps.safe_excerpt(answer_text))],
                    graph_leaf="public_timeline",
                    suggested_domain="institution",
                )

    if profile and "mensalidade" in normalized and "ensino medio" in normalized:
        rows = profile.get("tuition_reference")
        if isinstance(rows, list):
            chosen = next((row for row in rows if isinstance(row, dict) and "ensino medio" in str(row.get("segment", "")).lower()), None)
            if isinstance(chosen, dict):
                monthly = deps.format_brl(chosen.get("monthly_amount"))
                enrollment = deps.format_brl(chosen.get("enrollment_fee"))
                notes = str(chosen.get("notes") or "").strip()
                return _build_public_tool_payload(
                    message_text=(
                        f"Para Ensino Medio no turno {chosen.get('shift_label', 'Manha')}, a mensalidade publica de referencia em 2026 "
                        f"e {monthly} e a taxa de matricula e {enrollment}. {notes}"
                    ).strip(),
                    domain="finance",
                    access_tier="public",
                    confidence=0.99,
                    reason="specialist_supervisor_tool_first:public_pricing_reference",
                    summary="Resposta deterministica baseada na tabela publica de valores.",
                    supports=[
                        MessageEvidenceSupport(
                            kind="pricing_reference",
                            label=str(chosen.get("segment") or "Tabela publica"),
                            detail=f"mensalidade {monthly} · matricula {enrollment}",
                        )
                    ],
                    graph_leaf="public_pricing_reference",
                    suggested_domain="finance",
                )

    return None
