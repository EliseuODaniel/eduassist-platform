from __future__ import annotations

from eduassist_semantic_ingress.context_budget import (
    ContextBudgetSnapshot,
    build_context_section_budget,
    estimate_text_tokens,
    pack_context_items,
    pack_context_json_items,
)


def test_estimate_text_tokens_returns_zero_for_blank_input() -> None:
    assert estimate_text_tokens("") == 0
    assert estimate_text_tokens(None) == 0


def test_estimate_text_tokens_returns_positive_count_for_real_text() -> None:
    assert estimate_text_tokens("A biblioteca abre às 7h30.") > 0


def test_build_context_section_budget_marks_truncation_when_used_is_lower_than_total() -> None:
    budget = build_context_section_budget(
        rendered_text="- user: oi\n- assistant: ola",
        total_items=7,
        used_items=4,
    )

    assert budget.truncated is True
    assert budget.total_items == 7
    assert budget.used_items == 4
    assert budget.estimated_tokens > 0


def test_context_budget_snapshot_carries_optional_sections() -> None:
    snapshot = ContextBudgetSnapshot(
        pipeline="turn_router",
        stack_label="python_functions",
        estimated_prompt_tokens=120,
        estimated_instruction_tokens=40,
        estimated_request_tokens=8,
        estimated_candidate_tokens=24,
        candidate_count=3,
        history=build_context_section_budget(
            rendered_text="- user: que horas abre a biblioteca?",
            total_items=5,
            used_items=4,
        ),
    )

    assert snapshot.pipeline == "turn_router"
    assert snapshot.candidate_count == 3
    assert snapshot.history is not None
    assert snapshot.history.truncated is True


def test_pack_context_items_keeps_most_recent_lines_within_budget() -> None:
    packed = pack_context_items(
        [
            "- user: primeira mensagem bem longa para consumir alguns tokens",
            "- assistant: segunda mensagem com algum contexto",
            "- user: terceira mensagem curta",
        ],
        token_budget=18,
        empty_text="- nenhum",
        keep_last=True,
    )

    assert packed.used_items >= 1
    assert packed.total_items == 3
    assert packed.truncated is True
    assert "terceira mensagem curta" in packed.rendered_text


def test_pack_context_json_items_trims_candidates_by_budget() -> None:
    payloads, packed = pack_context_json_items(
        [
            {"capability_id": "a", "reason": "primeira capability com texto"},
            {"capability_id": "b", "reason": "segunda capability com texto"},
            {"capability_id": "c", "reason": "terceira capability com texto"},
        ],
        token_budget=28,
        empty_text="[]",
    )

    assert payloads
    assert packed.total_items == 3
    assert packed.used_items < 3
    assert packed.truncated is True
