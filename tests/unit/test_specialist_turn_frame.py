from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator_specialist.intent_resolution import IntentResolutionDeps, resolve_turn_intent
from ai_orchestrator_specialist.runtime_io import orchestrator_preview


def _deps() -> IntentResolutionDeps:
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


def test_resolve_turn_intent_prefers_turn_frame_for_public_shift_offer() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            message="Que horas começa a aula de manhã?",
            user=SimpleNamespace(authenticated=False),
        ),
        preview_hint={
            "turn_frame": {
                "capability_id": "public.schedule.class_start_time",
                "access_tier": "public",
                "confidence": 0.91,
            }
        },
        operational_memory=None,
        actor=None,
        resolved_turn=None,
    )

    resolved = resolve_turn_intent(ctx, deps=_deps())

    assert resolved.key == "institution.shift_offers"
    assert resolved.capability == "institution.shift_offers"
    assert resolved.rationale == "turn_frame:public.schedule.class_start_time"


def test_resolve_turn_intent_prefers_turn_frame_for_finance_followup() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            message="Qual o proximo vencimento?",
            user=SimpleNamespace(authenticated=True),
        ),
        preview_hint={
            "turn_frame": {
                "capability_id": "protected.finance.next_due",
                "access_tier": "authenticated",
                "confidence": 0.87,
            }
        },
        operational_memory=None,
        actor=None,
        resolved_turn=None,
    )

    resolved = resolve_turn_intent(ctx, deps=_deps())

    assert resolved.key == "finance.student_summary"
    assert resolved.capability == "finance.student_summary"
    assert resolved.access_tier == "authenticated"


def test_resolve_turn_intent_prefers_turn_frame_for_public_curriculum() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            message="Qual o conteúdo ensinado em biologia?",
            user=SimpleNamespace(authenticated=False),
        ),
        preview_hint={
            "turn_frame": {
                "capability_id": "public.curriculum.overview",
                "access_tier": "public",
                "confidence": 0.9,
            }
        },
        operational_memory=None,
        actor=None,
        resolved_turn=None,
    )

    resolved = resolve_turn_intent(ctx, deps=_deps())

    assert resolved.key == "institution.facilities"
    assert resolved.rationale == "turn_frame:public.curriculum.overview"


def test_orchestrator_preview_converts_public_turn_frame_into_structured_tool(monkeypatch) -> None:
    async def fake_semantic_ingress_plan(**_kwargs):
        return None

    async def fake_turn_frame(**_kwargs):
        return {
            "capability_id": "public.schedule.class_start_time",
            "domain": "institution",
            "access_tier": "public",
            "scope": "public",
            "public_conversation_act": "schedule",
            "confidence": 0.91,
        }

    monkeypatch.setattr(
        "ai_orchestrator_specialist.semantic_ingress_runtime.maybe_resolve_semantic_ingress_plan",
        fake_semantic_ingress_plan,
    )
    monkeypatch.setattr(
        "ai_orchestrator_specialist.semantic_ingress_runtime.maybe_resolve_turn_frame",
        fake_turn_frame,
    )

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            message="Que horas começa a aula de manhã?",
            conversation_id="conv-preview",
            telegram_chat_id=None,
            channel=SimpleNamespace(value="api"),
            user=SimpleNamespace(authenticated=True, role=SimpleNamespace(value="guardian"), scopes=[]),
            allow_graph_rag=True,
            allow_handoff=True,
        ),
        settings=SimpleNamespace(
            orchestrator_preview_cache_ttl_seconds=1.0,
        ),
        conversation_context=None,
        http_client=None,
    )

    import asyncio

    preview = asyncio.run(orchestrator_preview(ctx))

    assert preview is not None
    assert preview["mode"] == "structured_tool"
    assert preview["retrieval_backend"] == "none"
    assert "get_public_profile_bundle" in preview["selected_tools"]
    assert preview["classification"]["reason"] == "specialist_turn_frame:public.schedule.class_start_time"
