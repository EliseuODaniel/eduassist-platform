from __future__ import annotations

import asyncio
from types import SimpleNamespace

from eduassist_semantic_ingress.answer_surface_refiner import refine_answer_surface_with_provider


def test_answer_surface_refiner_uses_plain_text_fallback_when_structured_attempt_is_empty(monkeypatch) -> None:
    calls: list[str] = []

    async def _fake_call_refiner_provider(*, instructions: str, **_kwargs):
        calls.append(instructions)
        if "Devolva somente JSON valido" in instructions:
            return None
        return "Resumo academico de Lucas Oliveira:\n- Matematica: media parcial 6,2"

    monkeypatch.setattr(
        "eduassist_semantic_ingress.answer_surface_refiner._call_refiner_provider",
        _fake_call_refiner_provider,
    )

    result = asyncio.run(
        refine_answer_surface_with_provider(
            settings=SimpleNamespace(
                llm_provider="openai",
                openai_api_key="local-llm",
                openai_base_url="http://127.0.0.1:18081/v1",
                openai_model="dummy",
                openai_api_mode="chat_completions",
                llm_model_profile="test",
                grounded_public_history_budget_tokens=180,
                grounded_public_evidence_budget_tokens=320,
            ),
            stack_label="specialist_supervisor",
            request_message="quero um resumo academico do Lucas Oliveira",
            original_text="Notas de Lucas Oliveira:\n- Matematica: media parcial 6,2",
            answer_mode="answer",
            answer_reason="specialist_supervisor_fast_path:academic_summary_followup",
            domain="academic",
            access_tier="protected",
            evidence_lines=["Notas de Lucas Oliveira: Matematica 6,2"],
            conversation_context={"recent_messages": []},
            target_names=["Lucas Oliveira"],
            active_subject=None,
        )
    )

    assert len(calls) == 2
    assert result.used_llm is True
    assert result.changed is True
    assert "Resumo academico de Lucas Oliveira" in result.answer_text
