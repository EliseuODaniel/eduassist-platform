from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.models import MessageResponseRequest, UserContext, UserRole
from ai_orchestrator.python_functions_runtime import build_python_functions_plan
from ai_orchestrator.llamaindex_path_runtime import build_llamaindex_plan
from ai_orchestrator_specialist.intent_resolution import IntentResolutionDeps, resolve_turn_intent
from eduassist_semantic_ingress import build_turn_frame_hint


class _Settings:
    graph_rag_enabled = False


def _specialist_deps() -> IntentResolutionDeps:
    return IntentResolutionDeps(
        normalize_text=lambda value: (value or "").lower(),
        contains_any=lambda text, terms: any(term in text for term in terms),
        preview_domain=lambda preview: str((preview or {}).get("classification", {}).get("domain") or ""),
        linked_students=lambda *_args, **_kwargs: [],
        resolve_student=lambda *_args, **_kwargs: None,
        subject_hint_from_text=lambda _text: None,
        pending_kind_from_answer=lambda _answer: None,
        topic_from_reason=lambda _reason: None,
        effective_multi_intent_domains=lambda _memory, _message: [],
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


def test_turn_frame_cross_stack_public_schedule_alignment() -> None:
    message = "Que horas começa a aula de manhã?"
    request = MessageResponseRequest(
        message=message,
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    frame = build_turn_frame_hint(
        message=message,
        conversation_context=None,
        preview=None,
        authenticated=True,
    )
    python_plan = build_python_functions_plan(request=request, settings=_Settings(), mode="python_functions")
    llamaindex_plan = build_llamaindex_plan(request=request, settings=_Settings(), mode="llamaindex")
    resolved = resolve_turn_intent(
        SimpleNamespace(
            request=SimpleNamespace(message=message, user=SimpleNamespace(authenticated=True)),
            preview_hint={
                "turn_frame": {
                    "capability_id": frame.capability_id,
                    "access_tier": frame.access_tier,
                    "confidence": frame.confidence,
                }
            },
            operational_memory=None,
            actor=None,
            resolved_turn=None,
        ),
        deps=_specialist_deps(),
    )

    assert frame is not None
    assert frame.capability_id == "public.schedule.class_start_time"
    assert "turn_frame=public.schedule.class_start_time" in python_plan.preview.reason
    assert "turn_frame=public.schedule.class_start_time" in llamaindex_plan.preview.reason
    assert resolved.key == "institution.shift_offers"


def test_turn_frame_cross_stack_protected_finance_followup_alignment() -> None:
    message = "Qual o proximo vencimento?"
    conversation_context = {
        "messages": [
            {"role": "user", "content": "Quero ver meu financeiro"},
            {"role": "assistant", "content": "Resumo financeiro da familia."},
        ]
    }
    request = MessageResponseRequest(
        message=message,
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    frame = build_turn_frame_hint(
        message=message,
        conversation_context=conversation_context,
        preview=None,
        authenticated=True,
    )
    python_plan = build_python_functions_plan(request=request, settings=_Settings(), mode="python_functions")
    llamaindex_plan = build_llamaindex_plan(request=request, settings=_Settings(), mode="llamaindex")
    resolved = resolve_turn_intent(
        SimpleNamespace(
            request=SimpleNamespace(message=message, user=SimpleNamespace(authenticated=True)),
            preview_hint={
                "turn_frame": {
                    "capability_id": "protected.finance.next_due",
                    "access_tier": "authenticated",
                    "confidence": 0.88,
                }
            },
            operational_memory=None,
            actor=None,
            resolved_turn=None,
        ),
        deps=_specialist_deps(),
    )

    assert frame is not None
    assert frame.capability_id == "protected.finance.next_due"
    assert python_plan.preview.classification.domain.value == "finance"
    assert llamaindex_plan.preview.classification.domain.value == "finance"
    assert resolved.key == "finance.student_summary"
