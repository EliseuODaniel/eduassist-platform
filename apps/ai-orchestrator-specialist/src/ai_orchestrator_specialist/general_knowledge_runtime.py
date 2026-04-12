from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .models import (
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageIntentClassification,
    SupervisorAnswerPayload,
)


@dataclass(frozen=True)
class GeneralKnowledgeDeps:
    looks_like_general_knowledge_query: Callable[[str], bool]
    agent_model: Callable[[Any], Any]
    run_config: Callable[..., Any]
    effective_conversation_id: Callable[[Any], str]
    safe_excerpt: Callable[..., str | None]
    default_suggested_replies: Callable[[str], list[Any]]


async def general_knowledge_fast_path_answer(
    ctx: Any,
    *,
    deps: GeneralKnowledgeDeps,
) -> SupervisorAnswerPayload | None:
    if not deps.looks_like_general_knowledge_query(ctx.request.message):
        return None
    if ctx.resolved_turn is not None and ctx.resolved_turn.domain != "unknown":
        return None
    if ctx.operational_memory is not None and (
        ctx.operational_memory.pending_kind
        or ctx.operational_memory.active_domain in {"institution", "academic", "finance", "support"}
    ):
        return None
    answer_text = (
        "Nao tenho base confiavel aqui para responder conhecimento geral fora do escopo da escola. "
        "Posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro."
    )
    return SupervisorAnswerPayload(
        message_text=answer_text,
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain="unknown",
            access_tier="public",
            confidence=0.97,
            reason="specialist_supervisor_fast_path:out_of_scope_abstention",
        ),
        evidence_pack=MessageEvidencePack(
            strategy="direct_answer",
            summary="Abstencao segura para pergunta fora do dominio escolar.",
            source_count=0,
            support_count=1,
            supports=[
                MessageEvidenceSupport(
                    kind="scope_boundary",
                    label="Limite de escopo do assistente",
                    excerpt=deps.safe_excerpt(answer_text, limit=180),
                )
            ],
        ),
        suggested_replies=deps.default_suggested_replies("institution"),
        graph_path=["specialist_supervisor", "fast_path", "out_of_scope_abstention"],
        reason="specialist_supervisor_fast_path:out_of_scope_abstention",
        used_llm=False,
        llm_stages=[],
    )
