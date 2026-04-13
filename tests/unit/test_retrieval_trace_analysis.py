from __future__ import annotations

from datetime import UTC, datetime

from tools.evals.analyze_retrieval_run_traces import (
    RetrievalTraceRow,
    _aggregate_trace_items,
    _extract_trace_key,
    _trace_item,
)


def test_extract_trace_key_parses_stack_and_thread_id() -> None:
    parsed = _extract_trace_key(
        external_thread_id="debug:retrieval20:20260413T120000Z:thread_abc:python_functions",
        run_prefix="debug:retrieval20:20260413T120000Z",
    )

    assert parsed == ("python_functions", "thread_abc")


def test_trace_item_extracts_retrieval_policy_and_eval_fields() -> None:
    row = RetrievalTraceRow(
        created_at=datetime.now(UTC),
        conversation_id="debug:retrieval20:20260413T120000Z:thread_abc:langgraph",
        stack="langgraph",
        thread_id="thread_abc",
        turn_index=1,
        request_payload={
            "langgraph": {
                "retrieval_policy": {
                    "capability_id": "public.facilities.library.hours",
                    "profile": "cheap",
                    "top_k": 3,
                    "category": "all",
                    "reason": "capability:public.facilities.library.hours",
                }
            }
        },
        response_payload={
            "langgraph": {
                "retrieval_result": {
                    "total_hits": 4,
                    "selected_hit_count": 2,
                    "coverage_ratio": 0.75,
                    "answerability_coverage_ratio": 1.0,
                    "answerable": True,
                    "reranker_applied": True,
                }
            }
        },
    )

    item = _trace_item(
        row=row,
        eval_row={
            "quality_score": 100,
            "keyword_pass": True,
            "latency_ms": 840.0,
            "retrieval_type": "public_section_aware",
            "prompt": "Que horas fecha a biblioteca?",
            "reason": "langgraph_public_direct_answer",
            "error_types": [],
        },
    )

    assert item["capability_id"] == "public.facilities.library.hours"
    assert item["profile"] == "cheap"
    assert item["top_k"] == 3
    assert item["selected_hit_count"] == 2
    assert item["answerable"] is True
    assert item["quality_score"] == 100


def test_aggregate_trace_items_computes_actionable_summary() -> None:
    items = [
        {
            "stack": "python_functions",
            "capability_id": "public.enrollment.required_documents",
            "profile": "deep",
            "policy_reason": "capability:public.enrollment.required_documents",
            "top_k": 5,
            "total_hits": 5,
            "selected_hit_count": 2,
            "document_group_count": 2,
            "citations_count": 2,
            "answerable": False,
            "coverage_ratio": 0.3,
            "answerability_coverage_ratio": 0.3,
            "reranker_applied": True,
            "corrective_retry_applied": False,
            "citation_first_recommended": True,
            "query_plan_profile": "deep",
            "query_plan_intent": "document_lookup",
            "canonical_lane": "required_documents",
            "quality_score": 70,
            "keyword_pass": False,
            "latency_ms": 1100.0,
            "retrieval_type": "public_documents_credentials",
            "prompt": "Quais documentos preciso?",
            "reason": "python_functions_native_contextual_public_answer",
            "error_types": ["missing_expected_keyword"],
        },
        {
            "stack": "langgraph",
            "capability_id": "public.enrollment.required_documents",
            "profile": "deep",
            "policy_reason": "capability:public.enrollment.required_documents",
            "top_k": 5,
            "total_hits": 5,
            "selected_hit_count": 3,
            "document_group_count": 2,
            "citations_count": 2,
            "answerable": False,
            "coverage_ratio": 0.35,
            "answerability_coverage_ratio": 0.35,
            "reranker_applied": True,
            "corrective_retry_applied": False,
            "citation_first_recommended": True,
            "query_plan_profile": "deep",
            "query_plan_intent": "document_lookup",
            "canonical_lane": "required_documents",
            "quality_score": 72,
            "keyword_pass": False,
            "latency_ms": 1200.0,
            "retrieval_type": "public_documents_credentials",
            "prompt": "Quais documentos preciso?",
            "reason": "langgraph_public_direct_answer",
            "error_types": ["missing_expected_keyword"],
        },
        {
            "stack": "llamaindex",
            "capability_id": "public.enrollment.required_documents",
            "profile": "deep",
            "policy_reason": "capability:public.enrollment.required_documents",
            "top_k": 5,
            "total_hits": 5,
            "selected_hit_count": 3,
            "document_group_count": 2,
            "citations_count": 2,
            "answerable": False,
            "coverage_ratio": 0.4,
            "answerability_coverage_ratio": 0.4,
            "reranker_applied": True,
            "corrective_retry_applied": False,
            "citation_first_recommended": True,
            "query_plan_profile": "deep",
            "query_plan_intent": "document_lookup",
            "canonical_lane": "required_documents",
            "quality_score": 75,
            "keyword_pass": False,
            "latency_ms": 1300.0,
            "retrieval_type": "public_documents_credentials",
            "prompt": "Quais documentos preciso?",
            "reason": "llamaindex_contextual_public_direct_answer",
            "error_types": ["missing_expected_keyword"],
        },
        {
            "stack": "specialist_supervisor",
            "capability_id": "public.enrollment.required_documents",
            "profile": "unknown",
            "policy_reason": "unknown",
            "top_k": 0,
            "total_hits": 0,
            "selected_hit_count": 0,
            "document_group_count": 0,
            "citations_count": 0,
            "answerable": False,
            "coverage_ratio": 0.0,
            "answerability_coverage_ratio": 0.0,
            "reranker_applied": False,
            "corrective_retry_applied": False,
            "citation_first_recommended": False,
            "query_plan_profile": "unknown",
            "query_plan_intent": "unknown",
            "canonical_lane": "",
            "quality_score": 78,
            "keyword_pass": False,
            "latency_ms": 1500.0,
            "retrieval_type": "public_documents_credentials",
            "prompt": "Quais documentos preciso?",
            "reason": "specialist_supervisor_safe_fallback",
            "error_types": ["missing_expected_keyword"],
        },
    ]

    summary = _aggregate_trace_items(items)

    capability_summary = summary["by_capability"]["public.enrollment.required_documents"]
    assert capability_summary["count"] == 4
    assert capability_summary["answerable_rate"] == 0.0
    assert summary["recommendations"]
    assert "top_k" in summary["recommendations"][0]
