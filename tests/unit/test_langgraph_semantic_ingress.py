from __future__ import annotations

import asyncio
from types import SimpleNamespace

from eduassist_semantic_ingress import IngressSemanticPlan

from ai_orchestrator.langgraph_message_workflow import _bootstrap_context, _semantic_ingress
from ai_orchestrator.models import (
    AccessTier,
    IntentClassification,
    MessageEvidencePack,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    RetrievalBackend,
)


def test_langgraph_semantic_ingress_resolves_then_polishes(monkeypatch) -> None:
    def fake_compose_public_profile_answer(*_args, **_kwargs):
        return "Ola. Como posso ajudar voce hoje?"

    async def fake_polish(**_kwargs):
        return "Olá! Como posso ajudar você hoje?"

    async def fake_persist_trace(**_kwargs):
        return None

    async def fake_persist_turn(**_kwargs):
        return None

    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.build_semantic_ingress_public_plan",
        lambda _plan: SimpleNamespace(conversation_act="greeting"),
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._compose_public_profile_answer",
        fake_compose_public_profile_answer,
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.polish_langgraph_with_provider",
        fake_polish,
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._build_suggested_replies",
        lambda **_kwargs: [],
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._build_runtime_evidence_pack",
        lambda **_kwargs: MessageEvidencePack(strategy="semantic_ingress", summary="ok"),
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._persist_operational_trace",
        fake_persist_trace,
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._persist_conversation_turn",
        fake_persist_turn,
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._build_runtime_risk_flags",
        lambda **_kwargs: [],
    )

    preview = SimpleNamespace(
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.97,
            reason="langgraph_semantic_ingress:greeting",
        ),
        selected_tools=["get_public_school_profile"],
        graph_path=["langgraph", "semantic_ingress:greeting"],
    )
    state = {
        "request": SimpleNamespace(message="boa madruga", channel=SimpleNamespace(value="telegram")),
        "settings": SimpleNamespace(),
        "preview": preview,
        "actor": None,
        "conversation_context": {"recent_messages": []},
        "school_profile": {"school_name": "Colegio Horizonte"},
        "effective_conversation_id": "conv-semantic-ingress",
        "engine_name": "langgraph",
        "engine_mode": "dedicated",
        "semantic_ingress_plan": SimpleNamespace(conversation_act="greeting"),
        "langgraph_trace_metadata": {},
    }

    result = asyncio.run(_semantic_ingress(state))
    response = result["response"]

    assert response.message_text == "Olá! Como posso ajudar você hoje?"
    assert response.used_llm is True
    assert response.llm_stages == ["semantic_ingress_classifier", "structured_polish"]
    assert response.reason == "langgraph_semantic_ingress:greeting"


def test_langgraph_semantic_ingress_language_preference_stays_terminal(monkeypatch) -> None:
    def fake_compose_public_profile_answer(*_args, **_kwargs):
        return "Perfeito. Eu sigo em portugues. Quando eu mencionar admissions, leia como matricula e atendimento comercial."

    async def fake_polish(**_kwargs):
        return None

    async def fake_persist_trace(**_kwargs):
        return None

    async def fake_persist_turn(**_kwargs):
        return None

    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.build_semantic_ingress_public_plan",
        lambda _plan: SimpleNamespace(conversation_act="language_preference"),
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._compose_public_profile_answer",
        fake_compose_public_profile_answer,
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.polish_langgraph_with_provider",
        fake_polish,
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._build_suggested_replies",
        lambda **_kwargs: [],
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._build_runtime_evidence_pack",
        lambda **_kwargs: MessageEvidencePack(strategy="semantic_ingress", summary="ok"),
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._persist_operational_trace",
        fake_persist_trace,
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._persist_conversation_turn",
        fake_persist_turn,
    )
    monkeypatch.setattr(
        "ai_orchestrator.langgraph_message_workflow.rt._build_runtime_risk_flags",
        lambda **_kwargs: [],
    )

    preview = SimpleNamespace(
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.97,
            reason="langgraph_semantic_ingress:language_preference",
        ),
        selected_tools=["get_public_school_profile"],
        graph_path=["langgraph", "semantic_ingress:language_preference"],
    )
    state = {
        "request": SimpleNamespace(message="Por que admissions ta em ingles", channel=SimpleNamespace(value="telegram")),
        "settings": SimpleNamespace(),
        "preview": preview,
        "actor": {"role_code": "guardian"},
        "conversation_context": {"recent_messages": []},
        "school_profile": {"school_name": "Colegio Horizonte"},
        "effective_conversation_id": "conv-language-preference",
        "engine_name": "langgraph",
        "engine_mode": "dedicated",
        "semantic_ingress_plan": SimpleNamespace(conversation_act="language_preference"),
        "langgraph_trace_metadata": {},
    }

    result = asyncio.run(_semantic_ingress(state))
    response = result["response"]

    assert "matricula e atendimento comercial" in response.message_text.casefold()
    assert "lingua inglesa" not in response.message_text.casefold()
    assert response.reason == "langgraph_semantic_ingress:language_preference"
    assert response.llm_stages == ["semantic_ingress_classifier"]


def test_langgraph_bootstrap_prioritizes_terminal_semantic_ingress_before_protected_rescue(monkeypatch) -> None:
    preview = OrchestrationPreview(
        mode=OrchestrationMode.clarify,
        classification=IntentClassification(
            domain=QueryDomain.unknown,
            access_tier=AccessTier.public,
            confidence=0.35,
            reason="unknown",
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=[],
        citations_required=False,
        needs_authentication=False,
        graph_path=["classify_request", "clarify"],
        reason="unknown",
        output_contract="test",
    )

    async def _fetch_actor_context(**_kwargs):
        return {"linked_students": [{"student_id": "stu-lucas"}]}

    async def _fetch_conversation_context(**_kwargs):
        return {"recent_messages": []}

    async def _fetch_public_school_profile(**_kwargs):
        return {"school_name": "Colegio Horizonte"}

    async def _semantic_ingress(**_kwargs):
        return IngressSemanticPlan(
            conversation_act="greeting",
            use_conversation_context=False,
            confidence_bucket="high",
            reason="saudacao em idioma estrangeiro",
        )

    def _unexpected_rescue(**_kwargs):
        raise AssertionError("protected_domain_rescue_should_not_run")

    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.rt._fetch_actor_context", _fetch_actor_context)
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.rt._merge_user_context", lambda actor, user: user)
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.rt._effective_conversation_id", lambda request: "conv-privet")
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.rt._fetch_conversation_context", _fetch_conversation_context)
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.rt._conversation_context_payload", lambda bundle: {})
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.rt._build_analysis_message", lambda message, bundle: message)
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.rt._fetch_public_school_profile", _fetch_public_school_profile)
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.get_langgraph_artifacts", lambda settings: SimpleNamespace(graph=object()))
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.resolve_langgraph_thread_id", lambda **_kwargs: "thread-1")
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.rt._build_preview_state_input", lambda **_kwargs: {})
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.invoke_orchestration_graph", lambda **_kwargs: {})
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.rt.to_preview", lambda _graph_state: preview)
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.rt._capture_langgraph_trace_metadata", lambda **_kwargs: {})
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.maybe_resolve_semantic_ingress_plan", _semantic_ingress)
    monkeypatch.setattr("ai_orchestrator.langgraph_message_workflow.rt._apply_protected_domain_rescue", _unexpected_rescue)

    state = {
        "request": SimpleNamespace(
            message="Привет",
            telegram_chat_id=1649845499,
            channel=SimpleNamespace(value="telegram"),
            user=SimpleNamespace(authenticated=True),
            model_copy=lambda update=None: SimpleNamespace(
                message=(update or {}).get("message", "Привет"),
                telegram_chat_id=1649845499,
                channel=SimpleNamespace(value="telegram"),
                user=SimpleNamespace(authenticated=True),
            ),
        ),
        "settings": SimpleNamespace(),
    }

    result = asyncio.run(_bootstrap_context(state))

    assert result["route"] == "semantic_ingress"
    assert result["semantic_ingress_plan"].conversation_act == "greeting"
