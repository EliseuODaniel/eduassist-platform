from __future__ import annotations

from typing import Any

from .resolved_intent_answers import ResolvedIntentDeps
from .supervisor_run_flow import SupervisorRunFlowDeps
from .tool_first_answers import ToolFirstStructuredDeps
from .tool_first_protected_answers import ToolFirstProtectedDeps
from .tool_first_public_answers import ToolFirstPublicDeps
from .tool_first_workflows import ToolFirstWorkflowDeps


def build_resolved_intent_deps(**kwargs: Any) -> ResolvedIntentDeps:
    return ResolvedIntentDeps(**kwargs)


def build_tool_first_structured_deps(
    *,
    normalize_text: Any,
    effective_multi_intent_domains: Any,
    create_support_handoff_payload: Any,
    maybe_restricted_document_tool_first_answer: Any,
    public_kwargs: dict[str, Any],
    workflow_kwargs: dict[str, Any],
    protected_kwargs: dict[str, Any],
    student_hint_from_message: Any,
    is_student_name_only_followup: Any,
    fetch_academic_summary_payload: Any,
    fetch_financial_summary_payload: Any,
    build_academic_finance_combo_payload: Any,
    safe_excerpt: Any,
    fetch_public_payload: Any,
    format_brl: Any,
) -> ToolFirstStructuredDeps:
    return ToolFirstStructuredDeps(
        normalize_text=normalize_text,
        effective_multi_intent_domains=effective_multi_intent_domains,
        create_support_handoff_payload=create_support_handoff_payload,
        maybe_restricted_document_tool_first_answer=maybe_restricted_document_tool_first_answer,
        public_deps=ToolFirstPublicDeps(**public_kwargs),
        workflow_deps=ToolFirstWorkflowDeps(**workflow_kwargs),
        protected_deps=ToolFirstProtectedDeps(**protected_kwargs),
        student_hint_from_message=student_hint_from_message,
        is_student_name_only_followup=is_student_name_only_followup,
        fetch_academic_summary_payload=fetch_academic_summary_payload,
        fetch_financial_summary_payload=fetch_financial_summary_payload,
        build_academic_finance_combo_payload=build_academic_finance_combo_payload,
        safe_excerpt=safe_excerpt,
        fetch_public_payload=fetch_public_payload,
        format_brl=format_brl,
    )


def build_supervisor_run_flow_deps(**kwargs: Any) -> SupervisorRunFlowDeps:
    return SupervisorRunFlowDeps(**kwargs)
