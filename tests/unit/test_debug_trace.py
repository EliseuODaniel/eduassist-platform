from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.main import _build_debug_trace, _format_telegram_debug_footer
from ai_orchestrator.models import (
    AccessTier,
    ConversationChannel,
    IntentClassification,
    MessageEvidencePack,
    MessageResponse,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
)


def _response(*, used_llm: bool, llm_stages: list[str], final_polish_mode: str | None = None, final_polish_reason: str | None = None, final_polish_applied: bool = False) -> MessageResponse:
    return MessageResponse(
        message_text='ok',
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=1.0,
            reason='test',
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=['get_public_school_profile'],
        evidence_pack=MessageEvidencePack(strategy='direct_answer', summary='x'),
        reason='test_reason',
        graph_path=['structured_tool'],
        used_llm=used_llm,
        llm_stages=llm_stages,
        final_polish_eligible=final_polish_mode is not None,
        final_polish_applied=final_polish_applied,
        final_polish_mode=final_polish_mode,
        final_polish_reason=final_polish_reason,
    )


def test_build_debug_trace_exposes_used_llm() -> None:
    request = SimpleNamespace(channel=ConversationChannel.telegram)
    bundle = SimpleNamespace(primary=SimpleNamespace(name='python_functions'), mode='python_functions')
    trace = _build_debug_trace(request=request, response=_response(used_llm=True, llm_stages=['answer_composition']), bundle=bundle)
    assert trace['used_llm'] is True
    assert trace['llm_stages'] == ['answer_composition']


def test_format_telegram_debug_footer_renders_llm_status() -> None:
    footer = _format_telegram_debug_footer({
        'stack': 'python_functions',
        'bundle_mode': 'python_functions',
        'path': ['python_functions', 'kernel:python_functions'],
        'agents': [],
        'resources': [],
        'retrieval': {'backend': 'none', 'strategy': 'direct_answer', 'source_count': 0, 'support_count': 0, 'citation_count': 0},
        'reason': 'test_reason',
        'used_llm': True,
        'llm_stages': ['answer_composition', 'response_critic'],
    })
    assert 'llm: yes (answer_composition, response_critic)' in footer


def test_build_debug_trace_exposes_final_polish_metadata() -> None:
    request = SimpleNamespace(channel=ConversationChannel.telegram)
    bundle = SimpleNamespace(primary=SimpleNamespace(name='langgraph'), mode='langgraph')
    trace = _build_debug_trace(
        request=request,
        response=_response(
            used_llm=True,
            llm_stages=['answer_composition', 'structured_polish'],
            final_polish_mode='light_polish',
            final_polish_reason='langgraph_public_noncanonical',
            final_polish_applied=True,
        ),
        bundle=bundle,
    )
    assert trace['final_polish_mode'] == 'light_polish'
    assert trace['final_polish_reason'] == 'langgraph_public_noncanonical'
    assert trace['final_polish_applied'] is True


def test_format_telegram_debug_footer_renders_final_polish_status() -> None:
    footer = _format_telegram_debug_footer({
        'stack': 'langgraph',
        'bundle_mode': 'langgraph',
        'path': ['langgraph'],
        'agents': [],
        'resources': [],
        'retrieval': {'backend': 'qdrant_hybrid', 'strategy': 'retrieval', 'source_count': 2, 'support_count': 2, 'citation_count': 2},
        'reason': 'langgraph_public_retrieval',
        'used_llm': True,
        'llm_stages': ['answer_composition', 'structured_polish'],
        'final_polish_eligible': True,
        'final_polish_applied': True,
        'final_polish_mode': 'light_polish',
        'final_polish_reason': 'langgraph_public_noncanonical',
        'final_polish_preserved_fallback': False,
    })
    assert 'final_polish: light_polish (applied)' in footer
    assert 'final_polish_reason: langgraph_public_noncanonical' in footer
