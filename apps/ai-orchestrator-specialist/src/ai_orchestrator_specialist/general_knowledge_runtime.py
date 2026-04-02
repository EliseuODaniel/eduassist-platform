from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from agents import Agent, ModelSettings, Runner

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


def build_general_knowledge_agent(model: Any) -> Agent[Any]:
    return Agent[Any](
        name="General Knowledge Specialist",
        model=model,
        model_settings=ModelSettings(temperature=0.0, verbosity="low"),
        instructions=(
            "Responda em portugues do Brasil a perguntas simples e benignas de conhecimento geral. "
            "Se a pergunta tiver uma resposta factual direta e amplamente estavel, responda de forma curta e objetiva. "
            "Nao mencione detalhes internos do modelo nem do provedor. "
            "Se a pergunta for insegura, especializada demais, juridica, medica ou incerta, diga brevemente que prefere nao responder fora do dominio."
        ),
    )


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
    agent = build_general_knowledge_agent(deps.agent_model(ctx.settings))
    result = await Runner.run(
        agent,
        ctx.request.message,
        context=ctx,
        max_turns=3,
        run_config=deps.run_config(ctx.settings, conversation_id=deps.effective_conversation_id(ctx.request)),
    )
    final_output = getattr(result, "final_output", "")
    answer_text = str(final_output or "").strip()
    if not answer_text:
        return None
    return SupervisorAnswerPayload(
        message_text=answer_text,
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain="unknown",
            access_tier="public",
            confidence=0.88,
            reason="specialist_supervisor_fast_path:general_knowledge",
        ),
        evidence_pack=MessageEvidencePack(
            strategy="direct_answer",
            summary="Resposta curta para conhecimento geral benigno fora do dominio escolar.",
            source_count=0,
            support_count=1,
            supports=[
                MessageEvidenceSupport(
                    kind="general_knowledge",
                    label="Conhecimento geral",
                    excerpt=deps.safe_excerpt(answer_text, limit=180),
                )
            ],
        ),
        suggested_replies=deps.default_suggested_replies("institution"),
        graph_path=["specialist_supervisor", "fast_path", "general_knowledge"],
        reason="specialist_supervisor_fast_path:general_knowledge",
    )
