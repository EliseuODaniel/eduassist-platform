from __future__ import annotations

import asyncio
from types import SimpleNamespace

from ai_orchestrator_specialist.general_knowledge_runtime import (
    GeneralKnowledgeDeps,
    general_knowledge_fast_path_answer,
)
from ai_orchestrator_specialist.intent_resolution import IntentResolutionDeps, looks_like_general_knowledge_query


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


def test_general_knowledge_fast_path_overrides_school_memory_for_explicit_open_world_query() -> None:
    deps = GeneralKnowledgeDeps(
        looks_like_general_knowledge_query=lambda _message: True,
        agent_model=lambda _settings: None,
        run_config=lambda *_args, **_kwargs: None,
        effective_conversation_id=lambda _request: "conv-general-memory",
        safe_excerpt=lambda text, limit=180: str(text or "")[:limit],
        default_suggested_replies=lambda _domain: [],
    )
    ctx = SimpleNamespace(
        request=SimpleNamespace(message="Qual o melhor filme de ficcao cientifica?"),
        resolved_turn=SimpleNamespace(domain="institution"),
        operational_memory=SimpleNamespace(pending_kind="public_follow_up", active_domain="institution"),
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


def test_looks_like_general_knowledge_query_accepts_explicit_out_of_scope_movie_prompt() -> None:
    deps = IntentResolutionDeps(
        normalize_text=lambda s: " ".join(str(s or "").lower().split()),
        contains_any=lambda text, terms: any(term in text for term in terms),
        preview_domain=lambda _preview: "",
        linked_students=lambda *_args, **_kwargs: [],
        resolve_student=lambda *_args, **_kwargs: None,
        subject_hint_from_text=lambda _message: None,
        pending_kind_from_answer=lambda _answer: None,
        topic_from_reason=lambda _reason: None,
        effective_multi_intent_domains=lambda *_args: [],
        student_hint_from_message=lambda *_args, **_kwargs: None,
        unknown_explicit_student_reference=lambda *_args, **_kwargs: None,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        find_student_by_hint=lambda *_args, **_kwargs: None,
        looks_like_other_student_followup=lambda _message: False,
        student_from_memory=lambda *_args, **_kwargs: None,
        other_linked_student=lambda *_args, **_kwargs: None,
        looks_like_student_pronoun_followup=lambda _message: False,
        looks_like_subject_followup=lambda _message: False,
    )

    assert (
        looks_like_general_knowledge_query(
            "Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?",
            deps=deps,
        )
        is True
    )


def test_looks_like_general_knowledge_query_accepts_open_world_recommendation_prompt_without_question_mark() -> None:
    deps = IntentResolutionDeps(
        normalize_text=lambda s: " ".join(str(s or "").lower().split()),
        contains_any=lambda text, terms: any(term in text for term in terms),
        preview_domain=lambda _preview: "",
        linked_students=lambda *_args, **_kwargs: [],
        resolve_student=lambda *_args, **_kwargs: None,
        subject_hint_from_text=lambda _message: None,
        pending_kind_from_answer=lambda _answer: None,
        topic_from_reason=lambda _reason: None,
        effective_multi_intent_domains=lambda *_args: [],
        student_hint_from_message=lambda *_args, **_kwargs: None,
        unknown_explicit_student_reference=lambda *_args, **_kwargs: None,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        find_student_by_hint=lambda *_args, **_kwargs: None,
        looks_like_other_student_followup=lambda _message: False,
        student_from_memory=lambda *_args, **_kwargs: None,
        other_linked_student=lambda *_args, **_kwargs: None,
        looks_like_student_pronoun_followup=lambda _message: False,
        looks_like_subject_followup=lambda _message: False,
    )

    assert (
        looks_like_general_knowledge_query(
            "Me ajuda a escolher um filme para o fim de semana.",
            deps=deps,
        )
        is True
    )


def test_looks_like_general_knowledge_query_rejects_school_holiday_calendar_prompt() -> None:
    deps = IntentResolutionDeps(
        normalize_text=lambda s: " ".join(str(s or "").lower().split()),
        contains_any=lambda text, terms: any(term in text for term in terms),
        preview_domain=lambda _preview: "",
        linked_students=lambda *_args, **_kwargs: [],
        resolve_student=lambda *_args, **_kwargs: None,
        subject_hint_from_text=lambda _message: None,
        pending_kind_from_answer=lambda _answer: None,
        topic_from_reason=lambda _reason: None,
        effective_multi_intent_domains=lambda *_args: [],
        student_hint_from_message=lambda *_args, **_kwargs: None,
        unknown_explicit_student_reference=lambda *_args, **_kwargs: None,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        find_student_by_hint=lambda *_args, **_kwargs: None,
        looks_like_other_student_followup=lambda _message: False,
        student_from_memory=lambda *_args, **_kwargs: None,
        other_linked_student=lambda *_args, **_kwargs: None,
        looks_like_student_pronoun_followup=lambda _message: False,
        looks_like_subject_followup=lambda _message: False,
    )

    assert (
        looks_like_general_knowledge_query(
            "Quais os feriados desse ano?",
            deps=deps,
        )
        is False
    )
