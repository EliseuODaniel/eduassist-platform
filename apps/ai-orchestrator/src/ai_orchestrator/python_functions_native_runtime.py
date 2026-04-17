from __future__ import annotations

from time import monotonic
from typing import Any

from . import runtime as rt
from .path_profiles import (
    PathExecutionProfile,
    get_path_execution_profile as _python_functions_get_path_execution_profile,
)
from .python_functions_kernel import KernelPlan, KernelReflection, KernelRunResult
from .candidate_builder import build_response_candidate as _python_functions_build_response_candidate
from .candidate_chooser import choose_best_candidate as _python_functions_choose_best_candidate
from .evidence_pack import (
    build_direct_answer_evidence_pack as _python_functions_build_direct_answer_evidence_pack,
    build_retrieval_evidence_pack as _python_functions_build_retrieval_evidence_pack,
    build_structured_tool_evidence_pack as _python_functions_build_structured_tool_evidence_pack,
)
from .final_polish_policy import build_final_polish_decision as _python_functions_build_final_polish_decision
from .python_functions_kernel_runtime import (
    _maybe_contextual_public_direct_answer as _python_functions_maybe_contextual_public_direct_answer,
    _maybe_hypothetical_public_pricing_answer as _python_functions_maybe_hypothetical_public_pricing_answer,
    _maybe_public_unpublished_direct_answer as _python_functions_maybe_public_unpublished_direct_answer,
)
from .models import (
    AccessTier,
    IntentClassification,
    MessageEvidenceSupport,
    MessageResponse,
    MessageResponseCitation,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
    RetrievalProfile,
)
from .python_functions_local_llm import (
    compose_python_functions_with_provider as _compose_python_functions_with_provider,
    polish_python_functions_with_provider as _polish_python_functions_with_provider,
    revise_python_functions_with_provider as _revise_python_functions_with_provider,
    verify_python_functions_answer_against_contract as _verify_python_functions_answer_against_contract,
)
from .python_functions_public_knowledge import (
    compose_public_canonical_lane_answer as _compose_public_canonical_lane_answer,
    compose_public_conduct_policy_contextual_answer as _compose_public_conduct_policy_contextual_answer,
    match_public_canonical_lane as _match_public_canonical_lane,
)
from .python_functions_retrieval import (
    can_read_restricted_documents as _python_functions_can_read_restricted_documents,
    compose_restricted_document_grounded_answer_for_query as _compose_restricted_document_grounded_answer_for_query,
    compose_restricted_document_no_match_answer as _compose_restricted_document_no_match_answer,
    get_retrieval_service as _python_functions_get_retrieval_service,
    looks_like_restricted_document_query as _python_functions_looks_like_restricted_document_query,
    retrieve_relevant_restricted_hits_with_fallback as _python_functions_retrieve_relevant_restricted_hits_with_fallback,
)
from .python_functions_retrieval_probe import (
    build_public_evidence_probe as _python_functions_build_public_evidence_probe,
)
from .response_cache import store_cached_public_response as _python_functions_store_cached_public_response
from .semantic_ingress_runtime import (
    apply_semantic_ingress_preview as _python_functions_apply_semantic_ingress_preview,
    build_semantic_ingress_public_plan as _python_functions_build_semantic_ingress_public_plan,
    is_terminal_semantic_ingress_plan as _python_functions_is_terminal_semantic_ingress_plan,
    maybe_resolve_semantic_ingress_plan as _python_functions_maybe_resolve_semantic_ingress_plan,
)
from .serving_policy import (
    LoadSnapshot as _python_functions_load_snapshot,
    build_public_serving_policy as _python_functions_build_public_serving_policy,
)
from .serving_telemetry import record_stack_outcome as _python_functions_record_stack_outcome
from .serving_telemetry import (
    get_stack_telemetry_snapshot as _python_functions_get_stack_telemetry_snapshot,
)

build_response_candidate = _python_functions_build_response_candidate
choose_best_candidate = _python_functions_choose_best_candidate
build_direct_answer_evidence_pack = _python_functions_build_direct_answer_evidence_pack
build_retrieval_evidence_pack = _python_functions_build_retrieval_evidence_pack
build_structured_tool_evidence_pack = _python_functions_build_structured_tool_evidence_pack
build_final_polish_decision = _python_functions_build_final_polish_decision
compose_python_functions_with_provider = _compose_python_functions_with_provider
polish_python_functions_with_provider = _polish_python_functions_with_provider
revise_python_functions_with_provider = _revise_python_functions_with_provider
verify_python_functions_answer_against_contract = _verify_python_functions_answer_against_contract
compose_public_canonical_lane_answer = _compose_public_canonical_lane_answer
compose_public_conduct_policy_contextual_answer = _compose_public_conduct_policy_contextual_answer
match_public_canonical_lane = _match_public_canonical_lane
can_read_restricted_documents = _python_functions_can_read_restricted_documents
compose_restricted_document_grounded_answer_for_query = _compose_restricted_document_grounded_answer_for_query
compose_restricted_document_no_match_answer = _compose_restricted_document_no_match_answer
get_retrieval_service = _python_functions_get_retrieval_service
looks_like_restricted_document_query = _python_functions_looks_like_restricted_document_query
retrieve_relevant_restricted_hits_with_fallback = _python_functions_retrieve_relevant_restricted_hits_with_fallback
build_public_evidence_probe = _python_functions_build_public_evidence_probe
store_cached_public_response = _python_functions_store_cached_public_response
apply_semantic_ingress_preview = _python_functions_apply_semantic_ingress_preview
build_semantic_ingress_public_plan = _python_functions_build_semantic_ingress_public_plan
is_terminal_semantic_ingress_plan = _python_functions_is_terminal_semantic_ingress_plan
get_path_execution_profile = _python_functions_get_path_execution_profile
_maybe_contextual_public_direct_answer = _python_functions_maybe_contextual_public_direct_answer
_maybe_hypothetical_public_pricing_answer = _python_functions_maybe_hypothetical_public_pricing_answer
_maybe_public_unpublished_direct_answer = _python_functions_maybe_public_unpublished_direct_answer
maybe_resolve_semantic_ingress_plan = _python_functions_maybe_resolve_semantic_ingress_plan
LoadSnapshot = _python_functions_load_snapshot
build_public_serving_policy = _python_functions_build_public_serving_policy
get_stack_telemetry_snapshot = _python_functions_get_stack_telemetry_snapshot
record_stack_outcome = _python_functions_record_stack_outcome
_PYTHON_FUNCTIONS_NATIVE_MODEL_EXPORTS = (
    IntentClassification,
    MessageEvidenceSupport,
    MessageResponseCitation,
    RetrievalProfile,
)


def _preview_targets_restricted_document_surface(preview: Any) -> bool:
    reason = str(getattr(preview, 'reason', '') or '').strip().lower()
    if any(marker in reason for marker in ('restricted_document', 'restricted_doc', 'protected.documents.restricted_lookup')):
        return True
    graph_path = [str(node).strip().lower() for node in (getattr(preview, 'graph_path', None) or []) if str(node).strip()]
    if any('turn_frame:protected.documents.restricted_lookup' in node for node in graph_path):
        return True
    selected_tools = {
        str(tool).strip().lower()
        for tool in (getattr(preview, 'selected_tools', None) or [])
        if str(tool).strip()
    }
    return 'retrieve_restricted_documents' in selected_tools or (
        'search_documents' in selected_tools and 'restricted' in reason
    )


def _should_use_python_functions_native_path(plan: KernelPlan) -> bool:
    preview = plan.preview
    if _preview_targets_restricted_document_surface(preview):
        return True
    if preview.mode is OrchestrationMode.structured_tool:
        return True
    if (
        preview.mode is OrchestrationMode.hybrid_retrieval
        and preview.classification.access_tier in {AccessTier.authenticated, AccessTier.sensitive}
        and any(
            marker in str(preview.reason).lower()
            for marker in (
                'documento interno',
                'restricted_document',
                'protected.documents.restricted_lookup',
                'restricted_lookup',
            )
        )
    ):
        return True
    if preview.classification.access_tier is AccessTier.public:
        if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar, QueryDomain.unknown}:
            return False
        return preview.mode in {OrchestrationMode.hybrid_retrieval, OrchestrationMode.clarify}
    if preview.mode is not OrchestrationMode.clarify:
        return False
    return preview.classification.domain in {
        QueryDomain.institution,
        QueryDomain.academic,
        QueryDomain.unknown,
    }


def _should_force_public_teacher_boundary_native_path(
    *,
    request: Any,
    plan: KernelPlan,
    conversation_context: dict[str, Any] | None,
) -> bool:
    preview = plan.preview
    if preview.classification.access_tier is not AccessTier.public:
        return False
    if preview.mode is not OrchestrationMode.clarify:
        return False
    return rt._is_public_teacher_identity_query(request.message) or rt._is_public_teacher_directory_follow_up(
        request.message,
        conversation_context,
    )


async def _build_python_functions_direct_result(
    *,
    request: Any,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    preview: Any,
    message_text: str,
    execution_reason: str,
    evidence_pack: Any,
    started_at: float,
    reason_graph_leaf: str,
) -> KernelRunResult:
    effective_conversation_id = rt._effective_conversation_id(request)
    suggested_replies = rt._build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )
    normalized_text = rt._normalize_response_wording(message_text)
    await rt._persist_conversation_turn(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        actor=actor,
        user_message=request.message,
        assistant_message=normalized_text,
    )
    await rt._persist_operational_trace(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        engine_name=engine_name,
        engine_mode=engine_mode,
        actor=actor,
        preview=preview,
        school_profile=school_profile,
        conversation_context=conversation_context,
        public_plan=None,
        request_message=request.message,
        message_text=normalized_text,
        citations_count=0,
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=True,
        answer_verifier_reason=execution_reason,
        answer_verifier_fallback_used=False,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=False,
        langgraph_trace_metadata={
            'python_functions_native_reason': execution_reason,
            'python_functions_evidence_strategy': evidence_pack.strategy if evidence_pack is not None else '',
            'python_functions_evidence_support_count': evidence_pack.support_count if evidence_pack is not None else 0,
        },
    )
    selected_tools = list(
        dict.fromkeys(
            [
                *preview.selected_tools,
                'python_functions_native_runtime',
            ]
        )
    )
    response = MessageResponse(
        message_text=normalized_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=RetrievalBackend.none,
        selected_tools=selected_tools,
        citations=[],
        visual_assets=[],
        suggested_replies=suggested_replies,
        calendar_events=[],
        evidence_pack=evidence_pack,
        needs_authentication=preview.needs_authentication,
        graph_path=[
            *preview.graph_path,
            'python_functions:native_runtime',
            f'python_functions:{reason_graph_leaf}',
            f'kernel:{plan.stack_name}',
        ],
        risk_flags=preview.risk_flags,
        reason=execution_reason,
        used_llm=False,
        llm_stages=[],
        candidate_chosen='deterministic',
        candidate_reason=execution_reason,
    )
    record_stack_outcome(
        stack_name='python_functions',
        latency_ms=(monotonic() - started_at) * 1000,
        success=True,
        timeout=False,
        cache_hit=False,
        used_llm=False,
        candidate_kind='deterministic',
    )
    reflection = KernelReflection(
        grounded=True,
        verifier_reason=execution_reason,
        fallback_used=False,
        answer_judge_used=False,
        notes=[
            f'route:{preview.mode.value}',
            f'slice:{plan.slice_name}',
            f'evidence:{evidence_pack.strategy}' if evidence_pack is not None else 'evidence:none',
            *plan.plan_notes,
        ],
    )
    return KernelRunResult(
        plan=plan.model_copy(update={'preview': preview}),
        reflection=reflection,
        response=response.model_dump(mode='json'),
    )


async def maybe_execute_python_functions_native_plan(
    *,
    request: Any,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
    path_profile: PathExecutionProfile | None = None,
) -> KernelRunResult | None:
    from .python_functions_native_plan_runtime import maybe_execute_python_functions_native_plan as _impl

    return await _impl(
        request=request,
        settings=settings,
        plan=plan,
        engine_name=engine_name,
        engine_mode=engine_mode,
        path_profile=path_profile,
    )
