from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import AccessTier, MessageResponseRequest, OrchestrationMode, QueryDomain, RetrievalBackend


@dataclass(frozen=True)
class FinalPolishDecision:
    eligible: bool
    apply_polish: bool
    run_response_critic: bool
    mode: str
    reason: str
    preserve_entities: bool = True
    preserve_dates: bool = True
    preserve_codes: bool = True
    max_delta_ratio: float = 0.25
    budget_ms: int = 600


def _configured_stacks(settings: Any) -> set[str]:
    raw = str(getattr(settings, 'feature_flag_final_polish_stacks', '') or '')
    return {item.strip().lower() for item in raw.split(',') if item.strip()}


def _is_public_surface(*, preview: Any, request: MessageResponseRequest) -> bool:
    return (
        preview.classification.access_tier is AccessTier.public
        and not preview.needs_authentication
        and request.channel.value in {'telegram', 'web'}
    )


def _is_canonical_or_deterministic_reason(reason: str) -> bool:
    normalized = str(reason or '').strip()
    deterministic_prefixes = (
        'langgraph_public_canonical_lane:',
        'llamaindex_public_canonical_lane:',
        'specialist_supervisor_local_public_canonical_lane:',
        'specialist_supervisor_preflight:',
        'specialist_supervisor_fast_path:',
        'specialist_supervisor_tool_first:',
        'python_functions_native_contextual_public_answer',
        'contextual_public_direct_answer',
        'llamaindex_restricted_doc_',
        'langgraph_hitl_pending_review',
    )
    deterministic_contains = (
        'deterministic',
        'known_unknown',
        'teacher deterministic native answer',
    )
    return normalized.startswith(deterministic_prefixes) or any(marker in normalized for marker in deterministic_contains)


def _looks_like_multidoc(*, citations_count: int, support_count: int) -> bool:
    return citations_count >= 2 or support_count >= 2


def build_final_polish_decision(
    *,
    settings: Any,
    stack_name: str,
    request: MessageResponseRequest,
    preview: Any,
    response_reason: str,
    llm_stages: list[str] | None,
    citations_count: int,
    support_count: int,
    retrieval_backend: RetrievalBackend,
) -> FinalPolishDecision:
    normalized_stack = str(stack_name or '').strip().lower()
    if not bool(getattr(settings, 'feature_flag_final_polish_enabled', False)):
        return FinalPolishDecision(False, False, False, 'skip', 'feature_flag_disabled')
    if normalized_stack not in _configured_stacks(settings):
        return FinalPolishDecision(False, False, False, 'skip', 'stack_not_enabled')
    if bool(getattr(settings, 'feature_flag_final_polish_telegram_only', False)) and request.channel.value != 'telegram':
        return FinalPolishDecision(False, False, False, 'skip', 'channel_not_enabled')
    if preview.mode in {OrchestrationMode.deny, OrchestrationMode.clarify, OrchestrationMode.handoff}:
        return FinalPolishDecision(False, False, False, 'skip', 'mode_not_polishable')
    if _is_canonical_or_deterministic_reason(response_reason):
        return FinalPolishDecision(False, False, False, 'skip', 'deterministic_answer')
    if normalized_stack == 'specialist_supervisor':
        return FinalPolishDecision(False, False, False, 'skip', 'quality_first_path')
    if preview.classification.access_tier is not AccessTier.public:
        if not bool(getattr(settings, 'feature_flag_final_polish_protected_enabled', False)):
            return FinalPolishDecision(False, False, False, 'skip', 'protected_disabled')
        return FinalPolishDecision(False, False, False, 'skip', 'sensitive_surface')
    if not _is_public_surface(preview=preview, request=request):
        return FinalPolishDecision(False, False, False, 'skip', 'surface_not_enabled')

    llm_stage_set = {str(item).strip() for item in (llm_stages or []) if str(item).strip()}
    multi_doc = _looks_like_multidoc(citations_count=citations_count, support_count=support_count)
    public_doc_like = preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}

    if normalized_stack == 'python_functions':
        if preview.mode is OrchestrationMode.hybrid_retrieval and public_doc_like and multi_doc:
            return FinalPolishDecision(True, True, False, 'light_polish', 'python_functions_public_multidoc')
        return FinalPolishDecision(False, False, False, 'skip', 'python_functions_prefers_deterministic')

    if normalized_stack == 'langgraph':
        if public_doc_like and preview.mode in {OrchestrationMode.structured_tool, OrchestrationMode.hybrid_retrieval}:
            if 'answer_composition' in llm_stage_set:
                return FinalPolishDecision(
                    True,
                    False,
                    False,
                    'skip',
                    'langgraph_candidate_synthesis_already_used',
                )
            return FinalPolishDecision(
                True,
                True,
                bool(getattr(settings, 'llm_provider', '') == 'openai'),
                'light_polish',
                'langgraph_public_noncanonical',
            )
        return FinalPolishDecision(False, False, False, 'skip', 'langgraph_not_eligible')

    if normalized_stack == 'llamaindex':
        if public_doc_like and (multi_doc or 'answer_composition' in llm_stage_set or retrieval_backend is RetrievalBackend.qdrant_hybrid):
            return FinalPolishDecision(
                True,
                True,
                bool(getattr(settings, 'llm_provider', '') == 'openai') and multi_doc,
                'light_polish',
                'llamaindex_documentary_synthesis',
            )
        return FinalPolishDecision(False, False, False, 'skip', 'llamaindex_not_eligible')

    return FinalPolishDecision(False, False, False, 'skip', 'stack_without_policy')
