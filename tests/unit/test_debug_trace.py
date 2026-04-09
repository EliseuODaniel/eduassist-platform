from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.debug_trace_footer import (
    attach_telegram_debug_trace_for_stack,
    build_debug_trace_for_bundle,
    format_telegram_debug_footer,
)
from ai_orchestrator.models import (
    AccessTier,
    ConversationChannel,
    IntentClassification,
    MessageEvidencePack,
    MessageResponse,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
    UserContext,
)
from ai_orchestrator.service_settings import Settings


def _response(
    *,
    used_llm: bool,
    llm_stages: list[str],
    final_polish_mode: str | None = None,
    final_polish_reason: str | None = None,
    final_polish_applied: bool = False,
    answer_experience_applied: bool = False,
    answer_experience_reason: str | None = None,
    answer_experience_provider: str | None = None,
    answer_experience_model: str | None = None,
) -> MessageResponse:
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
        answer_experience_eligible=answer_experience_reason is not None,
        answer_experience_applied=answer_experience_applied,
        answer_experience_reason=answer_experience_reason,
        answer_experience_provider=answer_experience_provider,
        answer_experience_model=answer_experience_model,
    )


def test_build_debug_trace_exposes_used_llm() -> None:
    request = SimpleNamespace(channel=ConversationChannel.telegram)
    bundle = SimpleNamespace(primary=SimpleNamespace(name='python_functions'), mode='python_functions')
    trace = build_debug_trace_for_bundle(request=request, response=_response(used_llm=True, llm_stages=['answer_composition']), bundle=bundle)
    assert trace['used_llm'] is True
    assert trace['llm_stages'] == ['answer_composition']


def test_format_telegram_debug_footer_renders_llm_status() -> None:
    footer = format_telegram_debug_footer({
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
    trace = build_debug_trace_for_bundle(
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
    footer = format_telegram_debug_footer({
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


def test_build_debug_trace_exposes_answer_experience_metadata() -> None:
    request = SimpleNamespace(channel=ConversationChannel.telegram)
    bundle = SimpleNamespace(primary=SimpleNamespace(name='specialist_supervisor'), mode='specialist_supervisor')
    trace = build_debug_trace_for_bundle(
        request=request,
        response=_response(
            used_llm=True,
            llm_stages=['grounded_answer_experience'],
            answer_experience_applied=True,
            answer_experience_reason='protected_grounded_answer',
            answer_experience_provider='google',
            answer_experience_model='gemini-2.5-flash',
        ),
        bundle=bundle,
    )
    assert trace['answer_experience_applied'] is True
    assert trace['answer_experience_reason'] == 'protected_grounded_answer'
    assert trace['answer_experience_provider'] == 'google'


def test_format_telegram_debug_footer_renders_answer_experience_status() -> None:
    footer = format_telegram_debug_footer({
        'stack': 'specialist_supervisor',
        'bundle_mode': 'specialist_supervisor',
        'path': ['specialist_supervisor'],
        'agents': [],
        'resources': [],
        'retrieval': {'backend': 'none', 'strategy': 'structured_tool', 'source_count': 1, 'support_count': 1, 'citation_count': 0},
        'reason': 'protected_academic_detail',
        'used_llm': True,
        'llm_stages': ['grounded_answer_experience'],
        'final_polish_eligible': False,
        'final_polish_applied': False,
        'final_polish_mode': 'skip',
        'final_polish_reason': 'skip',
        'answer_experience_eligible': True,
        'answer_experience_applied': True,
        'answer_experience_reason': 'protected_grounded_answer',
        'answer_experience_provider': 'google',
        'answer_experience_model': 'gemini-2.5-flash',
    })
    assert 'answer_experience: applied (google/gemini-2.5-flash)' in footer
    assert 'answer_experience_reason: protected_grounded_answer' in footer


def test_attach_telegram_debug_trace_for_dedicated_stack_appends_footer() -> None:
    request = MessageResponseRequest(
        message='oi',
        conversation_id='conv-1',
        channel=ConversationChannel.telegram,
        user=UserContext(authenticated=True),
    )
    response = _response(
        used_llm=True,
        llm_stages=['answer_composition'],
        answer_experience_applied=True,
        answer_experience_reason='grounded_answer',
        answer_experience_provider='google',
        answer_experience_model='gemini-2.5-flash',
    )
    settings = Settings(feature_flag_telegram_debug_trace_footer_enabled=True)
    updated = attach_telegram_debug_trace_for_stack(
        request=request,
        response=response,
        stack_name='python_functions',
        settings=settings,
    )
    assert '[debug]' in updated.message_text
    assert 'stack: python_functions' in updated.message_text
    assert updated.debug_trace is not None
    assert updated.debug_trace['stack'] == 'python_functions'
