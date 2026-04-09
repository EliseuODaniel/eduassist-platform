from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.final_polish_policy import build_final_polish_decision
from ai_orchestrator.models import (
    AccessTier,
    ConversationChannel,
    IntentClassification,
    MessageResponseRequest,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    RetrievalBackend,
)


def _settings(**overrides: object) -> SimpleNamespace:
    payload = {
        'feature_flag_final_polish_enabled': True,
        'feature_flag_final_polish_protected_enabled': False,
        'feature_flag_final_polish_stacks': 'langgraph,llamaindex,python_functions',
        'feature_flag_final_polish_telegram_only': False,
        'llm_provider': 'openai',
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _request() -> MessageResponseRequest:
    return MessageResponseRequest(
        message='Quero uma leitura ampla e comparativa do material publico sobre apoio, inclusao e rotina escolar.',
        channel=ConversationChannel.telegram,
    )


def _preview(*, mode: OrchestrationMode, access_tier: AccessTier = AccessTier.public, domain: QueryDomain = QueryDomain.institution, reason: str = 'test') -> OrchestrationPreview:
    return OrchestrationPreview(
        mode=mode,
        classification=IntentClassification(
            domain=domain,
            access_tier=access_tier,
            confidence=0.9,
            reason=reason,
        ),
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
        selected_tools=['search_documents'],
        reason=reason,
        output_contract='message',
    )


def test_langgraph_public_noncanonical_allows_light_polish() -> None:
    decision = build_final_polish_decision(
        settings=_settings(),
        stack_name='langgraph',
        request=_request(),
        preview=_preview(mode=OrchestrationMode.hybrid_retrieval, reason='langgraph_public_retrieval'),
        response_reason='langgraph_public_retrieval',
        llm_stages=[],
        citations_count=2,
        support_count=2,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
    )
    assert decision.apply_polish is True
    assert decision.run_response_critic is True
    assert decision.mode == 'light_polish'


def test_langgraph_skips_polish_when_candidate_synthesis_already_used() -> None:
    decision = build_final_polish_decision(
        settings=_settings(),
        stack_name='langgraph',
        request=_request(),
        preview=_preview(mode=OrchestrationMode.hybrid_retrieval, reason='langgraph_public_retrieval'),
        response_reason='langgraph_public_retrieval',
        llm_stages=['answer_composition'],
        citations_count=2,
        support_count=2,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
    )
    assert decision.apply_polish is False
    assert decision.reason == 'langgraph_candidate_synthesis_already_used'


def test_python_functions_deterministic_contextual_answer_skips_polish() -> None:
    decision = build_final_polish_decision(
        settings=_settings(),
        stack_name='python_functions',
        request=_request(),
        preview=_preview(mode=OrchestrationMode.structured_tool, reason='python_functions_native_contextual_public_answer'),
        response_reason='python_functions_native_contextual_public_answer',
        llm_stages=[],
        citations_count=0,
        support_count=0,
        retrieval_backend=RetrievalBackend.none,
    )
    assert decision.apply_polish is False
    assert decision.reason == 'deterministic_answer'


def test_llamaindex_multidoc_documentary_allows_light_polish() -> None:
    decision = build_final_polish_decision(
        settings=_settings(),
        stack_name='llamaindex',
        request=_request(),
        preview=_preview(mode=OrchestrationMode.hybrid_retrieval, reason='llamaindex_public_direct_retrieval'),
        response_reason='llamaindex_public_direct_retrieval',
        llm_stages=['answer_composition'],
        citations_count=3,
        support_count=2,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
    )
    assert decision.apply_polish is True
    assert decision.mode == 'light_polish'


def test_specialist_quality_first_always_skips() -> None:
    decision = build_final_polish_decision(
        settings=_settings(feature_flag_final_polish_stacks='langgraph,llamaindex,python_functions,specialist_supervisor'),
        stack_name='specialist_supervisor',
        request=_request(),
        preview=_preview(mode=OrchestrationMode.structured_tool, reason='specialist_supervisor_direct:institution_specialist'),
        response_reason='specialist_supervisor_direct:institution_specialist',
        llm_stages=['specialist_execution'],
        citations_count=2,
        support_count=2,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
    )
    assert decision.apply_polish is False
    assert decision.reason == 'quality_first_path'
