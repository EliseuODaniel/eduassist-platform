from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.models import (
    AccessTier,
    IntentClassification,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    RetrievalBackend,
    RetrievalProfile,
)
from ai_orchestrator.retrieval_capability_policy import (
    build_retrieval_trace_metadata,
    infer_retrieval_capability_id,
    resolve_retrieval_execution_policy,
)


def _preview(domain: QueryDomain) -> OrchestrationPreview:
    return OrchestrationPreview(
        mode=OrchestrationMode.hybrid_retrieval,
        classification=IntentClassification(
            domain=domain,
            access_tier=AccessTier.public,
            confidence=0.95,
            reason="test",
        ),
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
        selected_tools=["search_documents"],
        graph_path=["test"],
        risk_flags=[],
        reason="test",
        output_contract="test",
    )


def test_infers_capability_from_schedule_public_plan() -> None:
    public_plan = SimpleNamespace(
        conversation_act="schedule",
        focus_hint="shift_offers",
        requested_attribute="start_time",
    )

    assert infer_retrieval_capability_id(public_plan=public_plan) == "public.schedule.class_start_time"


def test_public_documents_use_deep_profile() -> None:
    turn_frame = SimpleNamespace(capability_id="public.enrollment.required_documents")

    policy = resolve_retrieval_execution_policy(
        query="Quais documentos preciso para matricula?",
        visibility="public",
        baseline_top_k=4,
        preview=_preview(QueryDomain.institution),
        turn_frame=turn_frame,
    )

    assert policy.profile is RetrievalProfile.deep
    assert policy.top_k == 5
    assert policy.reason == "capability:public.enrollment.required_documents"


def test_public_library_hours_use_cheap_profile() -> None:
    turn_frame = SimpleNamespace(capability_id="public.facilities.library.hours")

    policy = resolve_retrieval_execution_policy(
        query="Que horas fecha a biblioteca?",
        visibility="public",
        baseline_top_k=4,
        preview=_preview(QueryDomain.institution),
        turn_frame=turn_frame,
    )

    assert policy.profile is RetrievalProfile.cheap
    assert policy.top_k == 3


def test_calendar_domain_defaults_to_deep_without_capability() -> None:
    policy = resolve_retrieval_execution_policy(
        query="Quando comecam as aulas?",
        visibility="public",
        baseline_top_k=4,
        preview=_preview(QueryDomain.calendar),
    )

    assert policy.profile is RetrievalProfile.deep
    assert policy.top_k == 5
    assert policy.category == "calendar"


def test_restricted_visibility_prefers_deep_profile() -> None:
    policy = resolve_retrieval_execution_policy(
        query="Quero ver o manual interno",
        visibility="restricted",
        baseline_top_k=3,
        preview=_preview(QueryDomain.institution),
    )

    assert policy.profile is RetrievalProfile.deep
    assert policy.top_k == 5


def test_builds_retrieval_trace_metadata_with_query_plan_and_answerability() -> None:
    policy = resolve_retrieval_execution_policy(
        query="Que horas fecha a biblioteca?",
        visibility="public",
        baseline_top_k=4,
        preview=_preview(QueryDomain.institution),
        turn_frame=SimpleNamespace(capability_id="public.facilities.library.hours"),
    )
    search = SimpleNamespace(
        total_hits=4,
        document_groups=[object(), object()],
        query_plan=SimpleNamespace(
            intent="contact_lookup",
            profile=RetrievalProfile.cheap,
            coverage_ratio=0.75,
            reranker_applied=True,
            corrective_retry_applied=False,
            citation_first_recommended=False,
            category_bias="calendar",
            canonical_lane="library_hours",
        ),
    )
    answerability = SimpleNamespace(
        enough_support=True,
        coverage_ratio=1.0,
        unsupported_terms={"cidade"},
    )

    metadata = build_retrieval_trace_metadata(
        visibility="public",
        policy=policy,
        search=search,
        selected_hit_count=2,
        citations_count=2,
        query_hints={"biblioteca", "fecha"},
        hints_supported=True,
        canonical_lane="library_hours",
        answerability=answerability,
    )

    assert metadata["retrieval_policy"]["capability_id"] == "public.facilities.library.hours"
    assert metadata["retrieval_result"]["selected_hit_count"] == 2
    assert metadata["retrieval_result"]["query_plan_profile"] == "cheap"
    assert metadata["retrieval_result"]["answerable"] is True
    assert metadata["retrieval_result"]["unsupported_term_count"] == 1
