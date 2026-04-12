from __future__ import annotations

import asyncio
from types import SimpleNamespace

from ai_orchestrator_specialist.general_knowledge_runtime import (
    GeneralKnowledgeDeps,
    general_knowledge_fast_path_answer,
)


def test_general_knowledge_fast_path_abstains_out_of_scope_queries() -> None:
    deps = GeneralKnowledgeDeps(
        looks_like_general_knowledge_query=lambda _message: True,
        agent_model=lambda _settings: None,
        run_config=lambda *_args, **_kwargs: None,
        effective_conversation_id=lambda _request: "conv-general",
        safe_excerpt=lambda text, limit=180: str(text or "")[:limit],
        default_suggested_replies=lambda _domain: [],
    )
    ctx = SimpleNamespace(
        request=SimpleNamespace(message="Qual o melhor filme do ano?"),
        resolved_turn=None,
        operational_memory=None,
        settings=SimpleNamespace(),
    )

    answer = asyncio.run(
        general_knowledge_fast_path_answer(
            ctx,
            deps=deps,
        )
    )

    assert answer is not None
    assert answer.reason == "specialist_supervisor_fast_path:out_of_scope_abstention"
    assert answer.used_llm is False
    assert answer.llm_stages == []
    assert "Nao tenho base confiavel" in answer.message_text
