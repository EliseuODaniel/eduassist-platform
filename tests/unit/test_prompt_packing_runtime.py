from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.prompt_packing_runtime import (
    pack_calendar_lines,
    pack_evidence_lines,
    pack_recent_history,
    pack_recent_history_lines,
)


def _settings() -> SimpleNamespace:
    return SimpleNamespace(
        grounded_public_history_budget_tokens=40,
        grounded_public_evidence_budget_tokens=52,
        stack_local_llm_history_budget_tokens=44,
        stack_local_llm_evidence_budget_tokens=56,
        stack_local_llm_calendar_budget_tokens=28,
    )


def test_pack_recent_history_prefers_most_recent_messages() -> None:
    packed = pack_recent_history(
        settings=_settings(),
        conversation_context={
            "recent_messages": [
                {"sender_type": "user", "content": "primeira mensagem bem longa"},
                {"sender_type": "assistant", "content": "segunda mensagem com algum detalhe"},
                {"sender_type": "user", "content": "terceira curta"},
            ]
        },
    )

    assert "terceira curta" in packed
    assert "- nenhum" not in packed


def test_pack_recent_history_lines_keeps_recent_tail() -> None:
    packed = pack_recent_history_lines(
        settings=_settings(),
        recent_messages=[
            "mensagem antiga com bastante detalhe",
            "mensagem intermediaria",
            "mensagem mais recente",
        ],
    )

    assert "mensagem mais recente" in packed


def test_pack_evidence_lines_trims_but_keeps_first_supported_items() -> None:
    packed = pack_evidence_lines(
        settings=_settings(),
        evidence_lines=[
            "Primeira evidencia bastante relevante",
            "Segunda evidencia adicional",
            "Terceira evidencia extra",
        ],
        empty_text="- nenhuma",
    )

    assert "Primeira evidencia" in packed
    assert "- nenhuma" not in packed


def test_pack_calendar_lines_returns_empty_label_when_no_events() -> None:
    packed = pack_calendar_lines(
        settings=_settings(),
        calendar_lines=[],
        empty_text="- nenhum evento estruturado",
    )

    assert packed == "- nenhum evento estruturado"
