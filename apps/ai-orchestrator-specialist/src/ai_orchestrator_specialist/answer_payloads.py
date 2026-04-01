from __future__ import annotations

from typing import Any

from eduassist_observability import canonicalize_evidence_strategy, canonicalize_risk_flags

from .models import (
    JudgeVerdict,
    ManagerDraft,
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageIntentClassification,
    MessageResponseCitation,
    MessageResponseSuggestedReply,
    SpecialistResult,
    SupervisorAnswerPayload,
    SupervisorPlan,
)


def _safe_excerpt(text: str | None, *, limit: int = 180) -> str | None:
    cleaned = str(text or "").strip()
    if not cleaned:
        return None
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 3].rstrip()}..."


def aggregate_citations(results: list[SpecialistResult]) -> list[MessageResponseCitation]:
    seen: set[tuple[str, str]] = set()
    citations: list[MessageResponseCitation] = []
    for result in results:
        for citation in result.citations:
            key = (citation.document_title, citation.chunk_id)
            if key in seen:
                continue
            seen.add(key)
            citations.append(citation)
    return citations[:6]


def build_evidence_pack(plan: SupervisorPlan, results: list[SpecialistResult]) -> MessageEvidencePack:
    supports: list[MessageEvidenceSupport] = []
    for result in results:
        supports.append(
            MessageEvidenceSupport(
                kind="specialist",
                label=result.specialist_id,
                detail=result.evidence_summary,
                excerpt=_safe_excerpt(result.answer_text),
            )
        )
        for point in result.support_points[:2]:
            supports.append(
                MessageEvidenceSupport(
                    kind="support_point",
                    label=result.specialist_id,
                    excerpt=_safe_excerpt(point),
                )
            )
        for citation in result.citations[:2]:
            supports.append(
                MessageEvidenceSupport(
                    kind="citation",
                    label=citation.document_title,
                    detail=f"{citation.version_label} · {citation.chunk_id}",
                    excerpt=_safe_excerpt(citation.excerpt),
                )
            )
    return MessageEvidencePack(
        strategy=canonicalize_evidence_strategy(plan.retrieval_strategy),
        summary=f"Resposta coordenada pelo specialist supervisor com {len(results)} especialista(s).",
        source_count=len(aggregate_citations(results)) or len(results),
        support_count=len(supports),
        supports=supports[:8],
    )


def default_suggested_replies(domain: str) -> list[MessageResponseSuggestedReply]:
    suggestions_by_domain = {
        "institution": ["Quais documentos preciso para matricula?", "Quero agendar uma visita", "Qual o horario da biblioteca?", "A escola segue a BNCC?"],
        "academic": ["E as faltas?", "E as proximas provas?", "Quanto falta para passar?", "E do outro aluno?"],
        "finance": ["Tem boleto em aberto?", "Qual o proximo vencimento?", "Quanto seria a matricula para 3 filhos?", "E do outro aluno?"],
        "support": ["Qual o status do protocolo?", "Quero remarcar a visita", "Quero cancelar a visita", "Resume meu pedido"],
    }
    return [MessageResponseSuggestedReply(text=text) for text in suggestions_by_domain.get(domain, suggestions_by_domain["institution"])[:4]]


def mode_from_strategy(strategy: str) -> str:
    if strategy == "graph_rag":
        return "graph_rag"
    if strategy in {"hybrid_retrieval", "document_search"}:
        return "hybrid_retrieval"
    if strategy == "clarify":
        return "clarify"
    if strategy == "deny":
        return "deny"
    return "structured_tool"


def retrieval_backend_from_strategy(strategy: str) -> str:
    if strategy == "graph_rag":
        return "graph_rag"
    if strategy in {"hybrid_retrieval", "document_search"}:
        return "qdrant_hybrid"
    return "none"


def access_tier_for_domain(domain: str, authenticated: bool) -> str:
    if domain in {"academic", "finance"}:
        return "authenticated" if authenticated else "public"
    if domain in {"support", "workflow"}:
        return "authenticated" if authenticated else "public"
    if authenticated:
        return "authenticated"
    return "public"


def safe_supervisor_fallback_answer(
    *,
    preview_hint: dict[str, Any] | None,
    authenticated: bool,
    reason: str,
) -> SupervisorAnswerPayload:
    preview = preview_hint or {}
    classification = preview.get("classification") if isinstance(preview.get("classification"), dict) else {}
    domain = str(classification.get("domain") or "institution").strip().lower() or "institution"
    if authenticated:
        message_text = (
            "Nao consegui consolidar essa resposta premium com seguranca agora. "
            "Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo."
        )
    else:
        message_text = (
            "Nao consegui concluir essa resposta premium agora. "
            "Se quiser, reformule em uma frase mais direta ou repita em instantes."
        )
    return SupervisorAnswerPayload(
        message_text=message_text,
        mode="clarify",
        classification=MessageIntentClassification(
            domain=domain,
            access_tier=access_tier_for_domain(domain, authenticated),
            confidence=0.0,
            reason=reason,
        ),
        suggested_replies=default_suggested_replies(domain),
        graph_path=["specialist_supervisor", "safe_fallback"],
        risk_flags=["dependency_unavailable"],
        reason=reason,
    )


def build_answer_payload(
    *,
    authenticated: bool,
    plan: SupervisorPlan,
    draft: ManagerDraft,
    judge: JudgeVerdict,
    specialist_results: list[SpecialistResult],
) -> SupervisorAnswerPayload:
    final_text = (
        judge.clarification_question
        if judge.needs_clarification and judge.clarification_question
        else judge.revised_answer_text or draft.answer_text
    )
    stable_reason = f"specialist_supervisor_manager_judge:{plan.primary_domain}:{plan.retrieval_strategy}"
    mode = "clarify" if judge.needs_clarification else mode_from_strategy(plan.retrieval_strategy)
    citations = aggregate_citations(specialist_results)
    suggested = judge.recommended_replies or draft.suggested_replies
    suggested_replies = [MessageResponseSuggestedReply(text=text[:80]) for text in suggested[:4]] or default_suggested_replies(plan.primary_domain)
    graph_path = ["specialist_supervisor", "input_guardrail", "planner", *plan.specialists, "judge"]
    return SupervisorAnswerPayload(
        message_text=final_text,
        mode=mode,
        classification=MessageIntentClassification(
            domain=plan.primary_domain,
            access_tier=access_tier_for_domain(plan.primary_domain, authenticated),
            confidence=max(plan.confidence, judge.grounding_score),
            reason=stable_reason,
        ),
        retrieval_backend=retrieval_backend_from_strategy(plan.retrieval_strategy),
        selected_tools=sorted({tool for item in specialist_results for tool in item.tool_names}),
        citations=citations,
        suggested_replies=suggested_replies,
        evidence_pack=build_evidence_pack(plan, specialist_results),
        needs_authentication=not authenticated and plan.primary_domain in {"academic", "finance"},
        graph_path=graph_path,
        risk_flags=canonicalize_risk_flags(judge.issues[:4] if judge.issues else []),
        reason=stable_reason,
    )


def grounding_gate_answer(
    *,
    authenticated: bool,
    plan: SupervisorPlan,
    judge: JudgeVerdict,
    specialist_results: list[SpecialistResult],
) -> SupervisorAnswerPayload | None:
    requires_grounded_specialists = bool(plan.specialists) or plan.retrieval_strategy in {
        "structured_tools",
        "hybrid_retrieval",
        "graph_rag",
        "document_search",
        "workflow_status",
        "pricing_projection",
    }
    has_grounding = bool(specialist_results)
    if judge.approved and (not requires_grounded_specialists or has_grounding):
        return None
    if judge.needs_clarification and judge.clarification_question:
        return SupervisorAnswerPayload(
            message_text=judge.clarification_question,
            mode="clarify",
            classification=MessageIntentClassification(
                domain=plan.primary_domain,
                access_tier=access_tier_for_domain(plan.primary_domain, authenticated),
                confidence=max(plan.confidence, 0.6),
                reason="specialist_supervisor_grounding_gate:clarify",
            ),
            suggested_replies=default_suggested_replies(plan.primary_domain),
            evidence_pack=MessageEvidencePack(
                strategy="clarify",
                summary="O judge bloqueou uma resposta sem grounding suficiente e pediu clarificacao.",
                source_count=0,
                support_count=1,
                supports=[MessageEvidenceSupport(kind="grounding_gate", label="Clarificacao", detail="Faltou grounding suficiente para responder com seguranca.")],
            ),
            graph_path=["specialist_supervisor", "grounding_gate", "clarify"],
            risk_flags=["grounding_insufficient"],
            reason="specialist_supervisor_grounding_gate:clarify",
        )
    return SupervisorAnswerPayload(
        message_text=(
            "Ainda nao consegui sustentar essa resposta com evidencias suficientes por aqui. "
            "Se quiser, reformule em uma frase mais direta ou me diga o assunto exato para eu buscar o canal certo."
        ),
        mode="clarify",
        classification=MessageIntentClassification(
            domain=plan.primary_domain,
            access_tier=access_tier_for_domain(plan.primary_domain, authenticated),
            confidence=max(plan.confidence, 0.55),
            reason="specialist_supervisor_grounding_gate:safe_clarify",
        ),
        suggested_replies=default_suggested_replies(plan.primary_domain),
        evidence_pack=MessageEvidencePack(
            strategy="clarify",
            summary="O judge bloqueou uma resposta nao grounded.",
            source_count=0,
            support_count=1,
            supports=[MessageEvidenceSupport(kind="grounding_gate", label="Resposta bloqueada", detail="A resposta do manager nao veio sustentada por specialist_results validos.")],
        ),
        graph_path=["specialist_supervisor", "grounding_gate", "safe_clarify"],
        risk_flags=["grounding_insufficient"],
        reason="specialist_supervisor_grounding_gate:safe_clarify",
    )
