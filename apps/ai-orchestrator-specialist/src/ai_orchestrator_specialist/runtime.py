from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

import httpx
from agents import (
    Agent,
    ModelSettings,
    RunHooks,
)

from .admin_status_answers import (
    _compose_actor_admin_status_answer,
    _compose_admin_status_answer,
)
from .agent_builders import (
    SpecialistAgentDeps,
    academic_specialist as _academic_specialist_module,
    build_guardrail_agent as _build_guardrail_agent_module,
    build_judge_agent as _build_judge_agent_module,
    build_manager_agent as _build_manager_agent_module,
    build_repair_agent as _build_repair_agent_module,
    document_specialist as _document_specialist_module,
    finance_specialist as _finance_specialist_module,
    institution_specialist as _institution_specialist_module,
    judge_instructions as _judge_instructions_module,
    manager_instructions as _manager_instructions_module,
    manager_result_contract as _manager_result_contract_module,
    repair_instructions as _repair_instructions_module,
    repair_result_contract as _repair_result_contract_module,
    specialist_result_contract as _specialist_result_contract_module,
    supports_tool_json_outputs as _supports_tool_json_outputs_module,
    tool_model_settings as _tool_model_settings_module,
    workflow_specialist as _workflow_specialist_module,
)
from .answer_payloads import (
    access_tier_for_domain as _access_tier_for_domain,
)
from .answer_payloads import (
    build_answer_payload as _build_answer_payload,
)
from .answer_payloads import (
    default_suggested_replies as _default_suggested_replies,
)
from .answer_payloads import (
    grounding_gate_answer as _grounding_gate_answer,
)
from .answer_payloads import (
    safe_supervisor_fallback_answer as _safe_supervisor_fallback_answer,
)
from .execution_budget import ExecutionBudget
from .fast_path_answers import (
    FastPathDeps,
    build_fast_path_answer as _build_fast_path_answer_module,
)
from .general_knowledge_runtime import (
    GeneralKnowledgeDeps,
    general_knowledge_fast_path_answer as _general_knowledge_fast_path_answer_module,
)
from .grounding_answer_helpers import (
    GroundingAnswerDeps,
    compose_internal_doc_grounded_answer as _compose_internal_doc_grounded_answer_module,
    compose_internal_doc_no_match_answer as _compose_internal_doc_no_match_answer_module,
    compose_public_graph_rag_fallback_answer as _compose_public_graph_rag_fallback_answer_module,
    supports_from_public_graph_rag_fallback_hits as _supports_from_public_graph_rag_fallback_hits_module,
)
from .guardrail_runtime import run_input_guardrail as _run_input_guardrail_stage
from .intent_resolution import (
    IntentResolutionDeps,
    build_operational_memory as _build_operational_memory_module,
    looks_like_general_knowledge_query as _looks_like_general_knowledge_query_module,
    resolve_turn_intent as _resolve_turn_intent_module,
    school_domain_terms as _school_domain_terms_module,
)
from .llm_runtime import (
    agent_model as _agent_model,
    agent_model_for_role as _agent_model_for_role,
)
from .llm_runtime import (
    effective_llm_model_name,
    resolve_llm_provider,
)
from .llm_runtime import (
    run_config as _run_config,
)
from .manager_flow import needs_manager as _needs_manager
from .manager_flow import run_manager_stack as _run_manager_stack
from .models import (
    JudgeVerdict,
    ManagerDraft,
    MessageEvidenceSupport,
    MessageResponseCitation,
    OperationalMemory,
    RepairDraft,
    ResolvedTurnIntent,
    RetrievalPlannerAdvice,
    SpecialistResult,
    SpecialistSupervisorRequest,
    SupervisorAnswerPayload,
    SupervisorPlan,
    UserContext,
)
from .operational_memory_answers import (
    OperationalMemoryDeps,
    maybe_operational_memory_follow_up_answer as _maybe_operational_memory_follow_up_answer_module,
)
from .planner_policy import execution_budget_metadata as _execution_budget_metadata
from .planner_policy import resolve_plan_and_budget as _resolve_plan_and_budget
from .planner_policy import run_retrieval_planner as _run_retrieval_planner_stage
from .protected_answer_helpers import (
    ProtectedAnswerDeps,
    academic_grade_requirement as _academic_grade_requirement_module,
    build_academic_finance_combo_payload as _build_academic_finance_combo_payload_module,
    build_academic_student_selection_clarify as _build_academic_student_selection_clarify_module,
    build_third_party_student_data_denial as _build_third_party_student_data_denial_module,
    compose_academic_aggregate_answer as _compose_academic_aggregate_answer_module,
    compose_academic_progression_answer as _compose_academic_progression_answer_module,
    compose_family_next_due_answer as _compose_family_next_due_answer_module,
    compose_finance_aggregate_answer as _compose_finance_aggregate_answer_module,
    compose_finance_installments_answer as _compose_finance_installments_answer_module,
    compose_academic_risk_answer as _compose_academic_risk_answer_module,
    compose_academic_snapshot_lines as _compose_academic_snapshot_lines_module,
    compose_authenticated_scope_answer as _compose_authenticated_scope_answer_module,
    compose_named_attendance_answer as _compose_named_attendance_answer_module,
    compose_named_grade_answer as _compose_named_grade_answer_module,
    compose_named_subject_grade_answer as _compose_named_subject_grade_answer_module,
    looks_like_academic_risk_followup as _looks_like_academic_risk_followup_module,
    looks_like_academic_progression_followup as _looks_like_academic_progression_followup_module,
    looks_like_family_academic_aggregate_query as _looks_like_family_academic_aggregate_query_module,
    looks_like_family_attendance_aggregate_query as _looks_like_family_attendance_aggregate_query_module,
    looks_like_family_finance_aggregate_query as _looks_like_family_finance_aggregate_query_module,
    looks_like_third_party_student_data_request as _looks_like_third_party_student_data_request_module,
    needs_specific_academic_student_clarification as _needs_specific_academic_student_clarification_module,
    resolved_academic_target_name as _resolved_academic_target_name_module,
)
from .public_bundle_fast_paths import (
    _preflight_public_doc_bundle_answer,
)
from .public_doc_knowledge import (
    compose_public_bolsas_and_processes,
    compose_public_health_second_call,
)
from .public_query_patterns import (
    _looks_like_admin_finance_combo_query,
    _looks_like_health_second_call_query,
    _looks_like_public_doc_bundle_request,
    _looks_like_service_routing_query,
)
from .registry import get_specialist_registry
from .restricted_doc_matching import (
    _internal_doc_hit_score,
    _looks_like_internal_document_query,
)
from .restricted_doc_tool_first import maybe_restricted_document_tool_first_answer
from .runtime_io import (
    fetch_actor_context as _fetch_actor_context,
)
from .resolved_intent_answers import (
    build_grade_requirement_answer as _build_grade_requirement_answer_module,
    maybe_academic_grade_fast_path_answer as _maybe_academic_grade_fast_path_answer_module,
    maybe_resolved_intent_answer as _maybe_resolved_intent_answer_module,
)
from .runtime_dependency_builders import (
    build_resolved_intent_deps as _build_resolved_intent_deps_module,
    build_supervisor_run_flow_deps as _build_supervisor_run_flow_deps_module,
    build_tool_first_structured_deps as _build_tool_first_structured_deps_module,
)
from .runtime_io import (
    fetch_conversation_context as _fetch_conversation_context,
)
from .runtime_io import (
    fetch_public_payload as _fetch_public_payload,
)
from .runtime_io import (
    fetch_public_school_profile as _fetch_public_school_profile,
)
from .runtime_io import (
    orchestrator_graph_rag_query as _orchestrator_graph_rag_query,
)
from .runtime_io import (
    orchestrator_preview as _orchestrator_preview,
)
from .runtime_io import (
    orchestrator_retrieval_search as _orchestrator_retrieval_search,
)
from .runtime_io import (
    persist_final_answer as _persist_final_answer_io,
)
from .specialist_executor import (
    build_execution_specialists as _build_budgeted_execution_specialists,
)
from .specialist_executor import (
    execute_planned_specialists as _execute_budgeted_specialists,
)
from .specialist_compose import (
    budgeted_no_manager_candidate as _budgeted_no_manager_candidate_module,
)
from .specialist_compose import (
    build_direct_answer_from_specialist as _build_direct_answer_from_specialist_module,
)
from .specialist_compose import (
    build_multi_specialist_answer_from_results as _build_multi_specialist_answer_from_results_module,
)
from .specialist_compose import (
    direct_compose_candidate as _direct_compose_candidate_module,
)
from .specialist_compose import (
    merge_specialist_results as _merge_specialist_results_module,
)
from .specialist_compose import (
    parse_specialist_results as _parse_specialist_results_module,
)
from .specialist_tools import (
    SpecialistToolDeps,
    build_specialist_tools as _build_specialist_tools_module,
)
from .support_workflow_helpers import (
    _build_support_handoff_summary,
    _detect_support_handoff_queue,
)
from .support_workflow_io import (
    _create_institutional_request_payload as _create_institutional_request_payload_io,
)
from .support_workflow_io import (
    _create_support_handoff_payload as _create_support_handoff_payload_io,
)
from .support_workflow_io import (
    _create_visit_booking_payload as _create_visit_booking_payload_io,
)
from .support_workflow_io import (
    _workflow_status_payload as _workflow_status_payload_io,
)
from .supervisor_run_flow import (
    run_specialist_supervisor as _run_specialist_supervisor_module,
)
from .student_context_helpers import (
    StudentContextDeps,
    fetch_academic_summary_payload as _fetch_academic_summary_payload_module,
    fetch_financial_summary_payload as _fetch_financial_summary_payload_module,
    looks_like_other_student_followup as _looks_like_other_student_followup_module,
    other_linked_student as _other_linked_student_module,
    recent_student_from_context_with_memory as _recent_student_from_context_with_memory_module,
    recent_subject_from_context as _recent_subject_from_context_module,
    resolve_student as _resolve_student_module,
    student_from_memory as _student_from_memory_module,
    student_hint_from_message as _student_hint_from_message_module,
    subject_code_from_hint as _subject_code_from_hint_module,
    subject_hint_from_text as _subject_hint_from_text_module,
    unknown_explicit_student_reference as _unknown_explicit_student_reference_module,
)
from .teacher_fast_paths import maybe_teacher_scope_fast_path_answer
from .tool_first_answers import (
    maybe_tool_first_structured_answer as _maybe_tool_first_structured_answer_module,
)

logger = logging.getLogger(__name__)
PASSING_GRADE_TARGET = Decimal("7.0")
EXECUTION_SPECIALISTS = {
    "institution_specialist",
    "academic_specialist",
    "finance_specialist",
    "workflow_specialist",
    "document_specialist",
}

@dataclass
class SupervisorTrace:
    agent_events: list[dict[str, Any]] = field(default_factory=list)
    tool_events: list[dict[str, Any]] = field(default_factory=list)
    stage_timings_ms: dict[str, float] = field(default_factory=dict)


@dataclass
class SupervisorRunContext:
    request: SpecialistSupervisorRequest
    settings: Any
    http_client: httpx.AsyncClient
    actor: dict[str, Any] | None
    conversation_context: dict[str, Any] | None
    operational_memory: OperationalMemory | None
    retrieval_advice: RetrievalPlannerAdvice | None
    school_profile: dict[str, Any] | None
    preview_hint: dict[str, Any] | None
    resolved_turn: ResolvedTurnIntent | None
    specialist_registry: dict[str, Any]
    execution_budget: ExecutionBudget | None = None
    trace: SupervisorTrace = field(default_factory=SupervisorTrace)


class SupervisorHooks(RunHooks[SupervisorRunContext]):
    async def on_agent_start(self, context, agent) -> None:
        context.context.trace.agent_events.append(
            {"event": "agent_start", "agent": agent.name}
        )

    async def on_agent_end(self, context, agent, output) -> None:
        rendered = output.model_dump(mode="json") if hasattr(output, "model_dump") else str(output)
        context.context.trace.agent_events.append(
            {"event": "agent_end", "agent": agent.name, "output": rendered}
        )

    async def on_tool_start(self, context, agent, tool) -> None:
        context.context.trace.tool_events.append(
            {"event": "tool_start", "agent": agent.name, "tool": getattr(tool, "name", str(tool))}
        )

    async def on_tool_end(self, context, agent, tool, result: str) -> None:
        context.context.trace.tool_events.append(
            {
                "event": "tool_end",
                "agent": agent.name,
                "tool": getattr(tool, "name", str(tool)),
                "result": result,
            }
        )


def _record_stage_timing(ctx: SupervisorRunContext, stage: str, elapsed_ms: float) -> None:
    normalized_stage = str(stage or "").strip()
    if not normalized_stage:
        return
    ctx.trace.stage_timings_ms[normalized_stage] = round(float(elapsed_ms), 1)


def _normalize_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _strip_none(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


def _safe_excerpt(value: str | None, *, limit: int = 220) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def _contains_any(text: str, terms: set[str] | tuple[str, ...]) -> bool:
    normalized = _normalize_text(text)
    return any(term in normalized for term in terms)


def _can_read_restricted_documents(user: UserContext) -> bool:
    scopes = {str(item).strip().lower() for item in user.scopes}
    role = str(getattr(user.role, "value", user.role) or "").strip().lower()
    return user.authenticated and (
        "documents:private:read" in scopes
        or "documents:restricted:read" in scopes
        or role in {"staff", "teacher"}
    )


def _select_relevant_internal_doc_hits(query: str, hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[tuple[float, int, dict[str, Any]]] = []
    for index, hit in enumerate(hits):
        score = _internal_doc_hit_score(query, hit)
        if score > 0.18:
            scored.append((score, index, hit))
    scored.sort(key=lambda item: (item[0], -item[1]), reverse=True)
    selected: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    for _, _, hit in scored:
        title_key = _normalize_text(str(hit.get('document_title') or hit.get('chunk_id') or ''))
        if title_key in seen_titles:
            continue
        selected.append(hit)
        seen_titles.add(title_key)
        if len(selected) >= 3:
            break
    return selected


def _citation_from_retrieval_hit(hit: dict[str, Any]) -> MessageResponseCitation | None:
    document_title = str(hit.get("document_title") or "").strip()
    chunk_id = str(hit.get("chunk_id") or "").strip()
    storage_path = str(hit.get("storage_path") or "").strip()
    if not document_title or not chunk_id:
        return None
    return MessageResponseCitation(
        document_title=document_title,
        version_label=str(hit.get("version_label") or "atual"),
        storage_path=storage_path or "inline",
        chunk_id=chunk_id,
        excerpt=str(hit.get("text_excerpt") or hit.get("contextual_summary") or "").strip() or "evidencia restrita",
    )


def _select_public_graph_rag_fallback_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    for hit in hits:
        if not isinstance(hit, dict):
            continue
        title = str(hit.get("document_title") or "").strip()
        excerpt = str(hit.get("text_excerpt") or hit.get("contextual_summary") or "").strip()
        if not title or not excerpt or title in seen_titles:
            continue
        selected.append(hit)
        seen_titles.add(title)
        if len(selected) >= 4:
            break
    return selected


def _grounding_answer_deps() -> GroundingAnswerDeps:
    return GroundingAnswerDeps(
        normalize_text=_normalize_text,
        safe_excerpt=_safe_excerpt,
        school_name=_school_name,
        looks_like_health_second_call_query=_looks_like_health_second_call_query,
        compose_public_health_second_call=compose_public_health_second_call,
    )


def _compose_public_graph_rag_fallback_answer(query: str, hits: list[dict[str, Any]]) -> str:
    return _compose_public_graph_rag_fallback_answer_module(
        query,
        hits,
        deps=_grounding_answer_deps(),
    )


def _supports_from_public_graph_rag_fallback_hits(hits: list[dict[str, Any]]) -> list[MessageEvidenceSupport]:
    return _supports_from_public_graph_rag_fallback_hits_module(hits, deps=_grounding_answer_deps())


def _internal_doc_domain_hint(message: str) -> str:
    normalized = _normalize_text(message)
    if any(term in normalized for term in ("financeiro", "quitacao", "quitação", "negociacao", "negociação", "pagamento")):
        return "finance"
    if any(term in normalized for term in ("professor", "segunda chamada", "saude", "saúde", "frequencia", "frequência")):
        return "academic"
    if any(term in normalized for term in ("transferencia", "transferência", "secretaria", "documento")):
        return "workflow"
    return "institution"


def _compose_internal_doc_grounded_answer(query: str, hits: list[dict[str, Any]]) -> str:
    return _compose_internal_doc_grounded_answer_module(query, hits)


def _compose_internal_doc_no_match_answer(message: str, profile: dict[str, Any] | None) -> str:
    return _compose_internal_doc_no_match_answer_module(
        message,
        profile,
        deps=_grounding_answer_deps(),
    )


def _is_simple_greeting(message: str) -> bool:
    return _normalize_text(message) in {
        "oi",
        "ola",
        "olá",
        "bom dia",
        "boa tarde",
        "boa noite",
        "e ai",
        "e aí",
        "opa",
    }


def _school_name(profile: dict[str, Any] | None) -> str:
    return str((profile or {}).get("school_name") or "Colegio Horizonte").strip() or "Colegio Horizonte"


def _compose_assistant_identity_answer(profile: dict[str, Any] | None) -> str:
    school_name = _school_name(profile)
    return (
        f"Voce esta falando com o EduAssist, o assistente institucional do {school_name}. "
        "Eu consigo te orientar por aqui, consultar informacoes da escola e abrir solicitacoes com protocolo. "
        "Se precisar, eu tambem te encaminho para secretaria, matricula e atendimento comercial, coordenacao, orientacao educacional, financeiro ou direcao."
    )


def _compose_auth_guidance_answer(profile: dict[str, Any] | None) -> str:
    school_name = _school_name(profile)
    return (
        "Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram "
        f"ao portal do {school_name}. No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando "
        "`/start link_<codigo>`. Depois disso, eu passo a consultar seus dados autorizados por este canal."
    )


def _is_assistant_identity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    normalized_simple = normalized.strip(" ?!.")
    if normalized_simple in {"com quem eu falo", "pra quem eu falo", "para quem eu falo"}:
        return True
    if _looks_like_service_routing_query(message):
        return False
    return any(
        term in normalized
        for term in {
            "quem e voce",
            "quem é voce",
            "quem e você",
            "quem é você",
            "o que voce faz",
            "o que você faz",
        }
    )


def _is_auth_guidance_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        term in normalized
        for term in {
            "como vinculo minha conta",
            "como vincular minha conta",
            "como eu vinculo minha conta",
            "como eu vinculo meu telegram",
            "como vinculo meu telegram",
            "como vinculo o telegram",
            "telegram a minha conta",
            "telegram a minha conta da escola",
            "vincular telegram",
            "como faco para vincular",
            "como faço para vincular",
            "como conecto minha conta",
            "como ativo minha conta",
            "como acesso minhas notas",
            "como vejo minhas notas",
            "como consultar minhas notas",
        }
    )


def _school_domain_terms() -> set[str]:
    return _school_domain_terms_module()


def _looks_like_general_knowledge_query(message: str) -> bool:
    return _looks_like_general_knowledge_query_module(
        message,
        deps=_intent_resolution_deps(),
    )


def _normalized_recent_user_messages(conversation_context: dict[str, Any] | None) -> list[str]:
    return [_normalize_text(item) for item in _extract_recent_user_messages(conversation_context)]


def _effective_conversation_id(request: SpecialistSupervisorRequest) -> str:
    if request.conversation_id:
        return request.conversation_id
    if request.channel == "telegram" and request.telegram_chat_id is not None:
        return f"telegram:{request.telegram_chat_id}"
    return f"{request.channel}:anonymous"


def _stringify_payload_value(value: Any, *, preferred_keys: tuple[str, ...] = ()) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value).strip()
    if isinstance(value, dict):
        for key in preferred_keys:
            candidate = _stringify_payload_value(value.get(key), preferred_keys=())
            if candidate:
                return candidate
        for fallback_key in ("text", "summary", "detail", "excerpt", "message", "reason", "issue", "note", "name", "label", "id"):
            candidate = _stringify_payload_value(value.get(fallback_key), preferred_keys=())
            if candidate:
                return candidate
        try:
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        except Exception:
            return str(value).strip()
    if isinstance(value, list):
        parts = [_stringify_payload_value(item, preferred_keys=preferred_keys) for item in value]
        return "; ".join(part for part in parts if part)
    return str(value).strip()


def _normalize_string_list(
    value: Any,
    *,
    preferred_keys: tuple[str, ...] = (),
) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text_value = value.strip()
        return [text_value] if text_value else []
    if isinstance(value, list):
        normalized_items: list[str] = []
        for item in value:
            text_value = _stringify_payload_value(item, preferred_keys=preferred_keys)
            if text_value:
                normalized_items.append(text_value)
        return normalized_items
    text_value = _stringify_payload_value(value, preferred_keys=preferred_keys)
    return [text_value] if text_value else []


def _intent_resolution_deps() -> IntentResolutionDeps:
    return IntentResolutionDeps(
        normalize_text=_normalize_text,
        contains_any=_contains_any,
        preview_domain=_preview_domain,
        linked_students=_linked_students,
        resolve_student=_resolve_student,
        subject_hint_from_text=_subject_hint_from_text,
        pending_kind_from_answer=_pending_kind_from_answer,
        topic_from_reason=_topic_from_reason,
        effective_multi_intent_domains=_effective_multi_intent_domains,
        student_hint_from_message=_student_hint_from_message,
        unknown_explicit_student_reference=_unknown_explicit_student_reference,
        is_student_name_only_followup=_is_student_name_only_followup,
        find_student_by_hint=_find_student_by_hint,
        looks_like_other_student_followup=_looks_like_other_student_followup,
        student_from_memory=_student_from_memory,
        other_linked_student=_other_linked_student,
        looks_like_student_pronoun_followup=_looks_like_student_pronoun_followup,
        looks_like_subject_followup=_looks_like_subject_followup,
    )


async def _http_get(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    path: str,
    token: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    response = await client.get(
        f"{base_url.rstrip('/')}{path}",
        params=params,
        headers={"X-Internal-Api-Token": token},
    )
    if response.status_code in {403, 404}:
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        if isinstance(payload, dict):
            return {**payload, "_status_code": response.status_code}
        return {"_status_code": response.status_code}
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, dict) else None


async def _http_post(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    path: str,
    token: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    response = await client.post(
        f"{base_url.rstrip('/')}{path}",
        headers={
            "X-Internal-Api-Token": token,
            "Content-Type": "application/json",
        },
        json=payload,
    )
    response.raise_for_status()
    body = response.json()
    return body if isinstance(body, dict) else None


async def _fetch_academic_summary_payload(
    ctx: SupervisorRunContext,
    *,
    student_name_hint: str | None = None,
) -> dict[str, Any]:
    return await _fetch_academic_summary_payload_module(
        ctx,
        student_name_hint=student_name_hint,
        deps=_student_context_deps(),
    )


async def _fetch_financial_summary_payload(
    ctx: SupervisorRunContext,
    *,
    student_name_hint: str | None = None,
) -> dict[str, Any]:
    return await _fetch_financial_summary_payload_module(
        ctx,
        student_name_hint=student_name_hint,
        deps=_student_context_deps(),
    )


async def _fetch_upcoming_assessments_payload(
    ctx: SupervisorRunContext,
    *,
    student_name_hint: str | None = None,
) -> dict[str, Any]:
    academic_payload = await _fetch_academic_summary_payload(
        ctx,
        student_name_hint=student_name_hint,
    )
    student = academic_payload.get("student") if isinstance(academic_payload, dict) else None
    if not isinstance(student, dict):
        return academic_payload if isinstance(academic_payload, dict) else {"error": "student_not_found"}
    payload = await _http_get(
        ctx.http_client,
        base_url=ctx.settings.api_core_url,
        path=f"/v1/students/{student['student_id']}/upcoming-assessments",
        token=ctx.settings.internal_api_token,
        params={"telegram_chat_id": ctx.request.telegram_chat_id},
    )
    return {
        "student": student,
        "summary": payload.get("summary") if isinstance(payload, dict) else None,
        "decision": payload.get("decision") if isinstance(payload, dict) else None,
    }


async def _fetch_attendance_timeline_payload(
    ctx: SupervisorRunContext,
    *,
    student_name_hint: str | None = None,
) -> dict[str, Any]:
    academic_payload = await _fetch_academic_summary_payload(
        ctx,
        student_name_hint=student_name_hint,
    )
    student = academic_payload.get("student") if isinstance(academic_payload, dict) else None
    if not isinstance(student, dict):
        return academic_payload if isinstance(academic_payload, dict) else {"error": "student_not_found"}
    payload = await _http_get(
        ctx.http_client,
        base_url=ctx.settings.api_core_url,
        path=f"/v1/students/{student['student_id']}/attendance-timeline",
        token=ctx.settings.internal_api_token,
        params={"telegram_chat_id": ctx.request.telegram_chat_id},
    )
    return {
        "student": student,
        "summary": payload.get("summary") if isinstance(payload, dict) else None,
        "decision": payload.get("decision") if isinstance(payload, dict) else None,
    }


def _compose_upcoming_assessments_lines(summary: dict[str, Any]) -> list[str]:
    assessments = summary.get("assessments")
    if not isinstance(assessments, list) or not assessments:
        return ["- Nao encontrei proximas avaliacoes registradas neste recorte."]
    lines: list[str] = []
    for assessment in assessments[:6]:
        if not isinstance(assessment, dict):
            continue
        lines.append(
            "- {subject_name} - {item_title}: {due_date}".format(
                subject_name=assessment.get("subject_name", "Disciplina"),
                item_title=assessment.get("item_title", "Avaliacao"),
                due_date=assessment.get("due_date", "data nao informada"),
            )
        )
    return lines or ["- Nao encontrei proximas avaliacoes registradas neste recorte."]


def _compose_attendance_timeline_lines(summary: dict[str, Any]) -> list[str]:
    records = summary.get("records")
    if not isinstance(records, list) or not records:
        return ["- Nao encontrei faltas ou registros recentes com data neste recorte."]
    lines: list[str] = []
    for record in records[:8]:
        if not isinstance(record, dict):
            continue
        status = str(record.get("status", "nao informado")).lower()
        status_label = {
            "present": "presenca",
            "late": "atraso",
            "absent": "falta",
        }.get(status, status)
        suffix = ""
        minutes_absent = int(record.get("minutes_absent", 0) or 0)
        if minutes_absent > 0:
            suffix = f" ({minutes_absent} min)"
        lines.append(
            "- {record_date} - {subject_name}: {status_label}{suffix}".format(
                record_date=record.get("record_date", "data nao informada"),
                subject_name=record.get("subject_name", "Disciplina"),
                status_label=status_label,
                suffix=suffix,
            )
        )
    return lines or ["- Nao encontrei faltas ou registros recentes com data neste recorte."]


def _pending_kind_from_answer(answer: SupervisorAnswerPayload) -> str | None:
    normalized_reason = _normalize_text(answer.reason)
    normalized_text = _normalize_text(answer.message_text)
    if "academic_subject_clarify" in normalized_reason:
        return "academic_subject"
    if "upcoming_assessments_student_clarify" in normalized_reason:
        return "upcoming_assessments_student_selection"
    if "attendance_student_clarify" in normalized_reason:
        return "attendance_student_selection"
    if "academic_student_clarify" in normalized_reason:
        return "academic_student_selection"
    if "clarify" in normalized_reason and any(term in normalized_text for term in {"qual aluno", "qual deles", "confirme o aluno"}):
        return "student_selection"
    if "workflow_date_clarify" in normalized_reason:
        return "workflow_date"
    return None

def _build_operational_memory(
    ctx: SupervisorRunContext,
    *,
    answer: SupervisorAnswerPayload,
    route: str,
) -> OperationalMemory:
    return _build_operational_memory_module(
        ctx,
        answer=answer,
        route=route,
        deps=_intent_resolution_deps(),
    )




async def _persist_final_answer(
    ctx: SupervisorRunContext,
    *,
    answer: SupervisorAnswerPayload,
    route: str,
    metadata: dict[str, Any] | None = None,
    trace_payload: tuple[SupervisorPlan, ManagerDraft, JudgeVerdict] | None = None,
    repair_payload: tuple[RepairDraft, JudgeVerdict] | None = None,
    timeout_seconds: float | None = None,
) -> None:
    operational_memory = _build_operational_memory(ctx, answer=answer, route=route)
    await _persist_final_answer_io(
        ctx,
        answer=answer,
        route=route,
        operational_memory=operational_memory,
        metadata=metadata,
        trace_payload=trace_payload,
        repair_payload=repair_payload,
        timeout_seconds=timeout_seconds,
    )


def _metadata_with_runtime_observability(
    ctx: SupervisorRunContext,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(metadata or {})
    if ctx.trace.stage_timings_ms:
        payload["stage_timings_ms"] = dict(ctx.trace.stage_timings_ms)
    return payload


def _linked_students(actor: dict[str, Any] | None, *, capability: str) -> list[dict[str, Any]]:
    linked = actor.get("linked_students") if isinstance(actor, dict) else None
    if not isinstance(linked, list):
        return []
    key = "can_view_finance" if capability == "finance" else "can_view_academic"
    items = []
    for item in linked:
        if not isinstance(item, dict):
            continue
        if capability in {"academic", "finance"} and not bool(item.get(key)):
            continue
        items.append(item)
    return items


def _student_context_deps() -> StudentContextDeps:
    return StudentContextDeps(
        normalize_text=_normalize_text,
        linked_students=_linked_students,
        http_get=_http_get,
    )


def _recent_student_from_context_with_memory(
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    *,
    operational_memory: OperationalMemory | None,
    capability: str = "academic",
) -> dict[str, Any] | None:
    return _recent_student_from_context_with_memory_module(
        actor,
        conversation_context,
        operational_memory=operational_memory,
        capability=capability,
        deps=_student_context_deps(),
    )


def _student_hint_from_message(actor: dict[str, Any] | None, message: str) -> str | None:
    return _student_hint_from_message_module(actor, message, deps=_student_context_deps())


def _unknown_explicit_student_reference(actor: dict[str, Any] | None, message: str) -> str | None:
    return _unknown_explicit_student_reference_module(actor, message, deps=_student_context_deps())


def _resolve_student(
    actor: dict[str, Any] | None,
    *,
    capability: str,
    student_name_hint: str | None,
    conversation_context: dict[str, Any] | None,
    operational_memory: OperationalMemory | None,
    current_message: str | None,
) -> dict[str, Any] | None:
    return _resolve_student_module(
        actor,
        capability=capability,
        student_name_hint=student_name_hint,
        conversation_context=conversation_context,
        operational_memory=operational_memory,
        current_message=current_message,
        deps=_student_context_deps(),
    )


def _looks_like_student_pronoun_followup(message: str) -> bool:
    normalized = _normalize_text(message)
    return bool(re.search(r"\b(dele|dela|dele\?|dela\?)\b", normalized))


def _looks_like_subject_followup(message: str) -> bool:
    normalized = _normalize_text(message)
    subject_hint = _subject_hint_from_text(message)
    if not subject_hint:
        return False
    if any(term in normalized for term in {"por que", "porque", "essa resposta", "resposta aqui", "nao e", "não é"}):
        return False
    if normalized.startswith("e de ") or normalized.startswith("e em "):
        return True
    if len(normalized.split()) <= 3 and not any(term in normalized for term in {"qual", "quais", "quando", "data", "datas", "provas", "avaliac"}):
        return True
    return bool(re.search(r"\b(de historia|de matemática|de matematica|de fisica|de física|de portugues|de português)\b", normalized))


def _preview_domain(preview_hint: dict[str, Any] | None) -> str:
    preview = preview_hint if isinstance(preview_hint, dict) else {}
    classification = preview.get("classification")
    if not isinstance(classification, dict):
        return ""
    return str(classification.get("domain") or "").strip().lower()


def _preview_classification_dict(preview_hint: dict[str, Any] | None) -> dict[str, Any]:
    preview = preview_hint if isinstance(preview_hint, dict) else {}
    classification = preview.get("classification")
    return classification if isinstance(classification, dict) else {}
def _resolve_turn_intent(ctx: SupervisorRunContext) -> ResolvedTurnIntent:
    return _resolve_turn_intent_module(ctx, deps=_intent_resolution_deps())


def _subject_code_from_hint(summary: dict[str, Any], subject_hint: str | None) -> tuple[str | None, str | None]:
    return _subject_code_from_hint_module(summary, subject_hint, deps=_student_context_deps())


def _pricing_projection(profile: dict[str, Any] | None, *, quantity: int, segment_hint: str | None = None) -> dict[str, Any]:
    quantity_value = max(1, int(quantity))
    tuition_rows = profile.get("tuition_reference") if isinstance(profile, dict) else []
    if not isinstance(tuition_rows, list):
        tuition_rows = []
    normalized_segment_hint = _normalize_text(segment_hint)
    chosen = None
    for row in tuition_rows:
        if not isinstance(row, dict):
            continue
        segment_label = _normalize_text(row.get("segment"))
        if normalized_segment_hint and normalized_segment_hint in segment_label:
            chosen = row
            break
    if chosen is None:
        chosen = next((row for row in tuition_rows if isinstance(row, dict) and str(row.get("enrollment_fee", "")).strip()), None)
    if chosen is None and tuition_rows:
        chosen = next((row for row in tuition_rows if isinstance(row, dict)), None)
    enrollment_fee = Decimal(str((chosen or {}).get("enrollment_fee", "0") or "0"))
    monthly_amount = Decimal(str((chosen or {}).get("monthly_amount", "0") or "0"))
    return {
        "quantity": quantity_value,
        "segment": (chosen or {}).get("segment"),
        "shift_label": (chosen or {}).get("shift_label"),
        "per_student_enrollment_fee": str(enrollment_fee),
        "per_student_monthly_amount": str(monthly_amount),
        "total_enrollment_fee": str(enrollment_fee * quantity_value),
        "total_monthly_amount": str(monthly_amount * quantity_value),
        "notes": (chosen or {}).get("notes"),
    }


def _format_brl(value: Any) -> str:
    amount = Decimal(str(value or "0")).quantize(Decimal("0.01"))
    rendered = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {rendered}"


def _timeline_entry(entries: list[dict[str, Any]], *, topic_fragment: str) -> dict[str, Any] | None:
    for item in entries:
        if not isinstance(item, dict):
            continue
        if topic_fragment in str(item.get("topic_key", "") or ""):
            return item
    return None


def _extract_recent_user_messages(conversation_context: dict[str, Any] | None) -> list[str]:
    items = conversation_context.get("recent_messages") if isinstance(conversation_context, dict) else None
    if not isinstance(items, list):
        return []
    return [str(item.get("content") or "").strip() for item in items if isinstance(item, dict) and item.get("sender_type") == "user"]


def _extract_recent_tool_calls(conversation_context: dict[str, Any] | None) -> list[dict[str, Any]]:
    items = conversation_context.get("recent_tool_calls") if isinstance(conversation_context, dict) else None
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _memory_from_payload(payload: Any) -> OperationalMemory | None:
    if not isinstance(payload, dict):
        return None
    try:
        return OperationalMemory.model_validate(payload)
    except Exception:
        return None


def _subject_hint_from_text(message: str) -> str | None:
    return _subject_hint_from_text_module(message, deps=_student_context_deps())


def _topic_from_reason(reason: str) -> str | None:
    normalized = _normalize_text(reason)
    if "academic_grade_requirement" in normalized:
        return "grade_requirement"
    if "upcoming_assessments" in normalized:
        return "upcoming_assessments"
    if "attendance_timeline" in normalized:
        return "attendance"
    if "attendance_policy" in normalized:
        return "attendance_policy"
    if "passing_policy" in normalized:
        return "passing_policy"
    if "academic_summary" in normalized:
        return "grades"
    if "administrative_status" in normalized:
        return "administrative_status"
    if "financial_summary" in normalized:
        return "finance_summary"
    if "academic_finance_combo" in normalized:
        return "academic_finance_combo"
    if "workflow" in normalized or "visit" in normalized:
        return "workflow"
    if "project_of_life_policy" in normalized:
        return "project_of_life"
    if "shift_offers" in normalized:
        return "shift_offers"
    if "interval_schedule" in normalized:
        return "interval_schedule"
    if "curriculum" in normalized:
        return "curriculum"
    return None


def _detect_multi_intent_domains(message: str) -> list[str]:
    normalized = _normalize_text(message)
    domains: list[str] = []
    if any(term in normalized for term in {"nota", "notas", "falta", "faltas", "prova", "boletim", "aprova", "disciplina"}):
        domains.append("academic")
    if any(term in normalized for term in {"boleto", "boletos", "fatura", "faturas", "parcela", "parcelas", "mensalidade", "financeiro", "vencimento"}):
        domains.append("finance")
    if any(term in normalized for term in {"visita", "agendar", "remarcar", "cancelar", "protocolo", "status"}):
        domains.append("support")
    return domains


def _effective_multi_intent_domains(memory: OperationalMemory | None, message: str) -> list[str]:
    detected = _detect_multi_intent_domains(message)
    normalized = _normalize_text(message)
    if len(detected) >= 2:
        return detected
    if any(term in normalized for term in {"tambem", "também", "tambem?", "também?", "e os", "e as", "e o", "e a"}):
        merged = list(
            dict.fromkeys(
                detected
                + list(memory.multi_intent_domains if memory is not None else [])
                + list(memory.active_domains if memory is not None else [])
                + ([str(memory.active_domain)] if memory is not None and str(memory.active_domain or "").strip() else [])
            )
        )
        if "academic" in merged and "finance" in merged:
            return ["academic", "finance"]
        if "support" in merged and "finance" in merged:
            return ["support", "finance"]
        if "support" in merged and "academic" in merged:
            return ["academic", "support"]
    return detected


def _load_operational_memory(conversation_context: dict[str, Any] | None) -> OperationalMemory | None:
    tool_calls = _extract_recent_tool_calls(conversation_context)
    for item in reversed(tool_calls):
        if str(item.get("tool_name") or "") != "specialist_supervisor.trace":
            continue
        response_payload = item.get("response_payload")
        if not isinstance(response_payload, dict):
            continue
        memory = _memory_from_payload(response_payload.get("operational_memory"))
        if memory is not None:
            return memory
    return None


def _student_from_memory(actor: dict[str, Any] | None, memory: OperationalMemory | None, *, capability: str) -> dict[str, Any] | None:
    return _student_from_memory_module(
        actor,
        memory,
        capability=capability,
        deps=_student_context_deps(),
    )


def _other_linked_student(actor: dict[str, Any] | None, *, capability: str, current_student_id: str | None) -> dict[str, Any] | None:
    return _other_linked_student_module(
        actor,
        capability=capability,
        current_student_id=current_student_id,
        deps=_student_context_deps(),
    )


def _looks_like_other_student_followup(message: str) -> bool:
    return _looks_like_other_student_followup_module(message, deps=_student_context_deps())


def _is_student_name_only_followup(actor: dict[str, Any] | None, message: str) -> str | None:
    normalized = _normalize_text(message)
    if not normalized or len(normalized.split()) > 4:
        return None
    if not re.fullmatch(r"(?:do|da|de)?\s*[a-zà-ÿ]+(?:\s+[a-zà-ÿ]+)?", normalized):
        return None
    return _student_hint_from_message(actor, message)


def _find_student_by_hint(actor: dict[str, Any] | None, *, capability: str, hint: str | None) -> dict[str, Any] | None:
    return _resolve_student(
        actor,
        capability=capability,
        student_name_hint=hint,
        conversation_context=None,
        operational_memory=None,
        current_message=None,
    )


def _protected_answer_deps() -> ProtectedAnswerDeps:
    return ProtectedAnswerDeps(
        normalize_text=_normalize_text,
        linked_students=_linked_students,
        subject_hint_from_text=_subject_hint_from_text,
        subject_code_from_hint=_subject_code_from_hint,
        access_tier_for_domain=_access_tier_for_domain,
        default_suggested_replies=_default_suggested_replies,
        student_hint_from_message=_student_hint_from_message,
        unknown_explicit_student_reference=_unknown_explicit_student_reference,
        is_student_name_only_followup=_is_student_name_only_followup,
        looks_like_student_pronoun_followup=_looks_like_student_pronoun_followup,
        looks_like_subject_followup=_looks_like_subject_followup,
        recent_subject_from_context=_recent_subject_from_context,
        format_brl=_format_brl,
        passing_grade_target=PASSING_GRADE_TARGET,
    )


def _compose_academic_snapshot_lines(summary: dict[str, Any]) -> list[str]:
    return _compose_academic_snapshot_lines_module(summary, deps=_protected_answer_deps())


def _compose_named_grade_answer(summary: dict[str, Any]) -> str:
    return _compose_named_grade_answer_module(summary, deps=_protected_answer_deps())


def _looks_like_academic_risk_followup(message: str) -> bool:
    return _looks_like_academic_risk_followup_module(message, deps=_protected_answer_deps())


def _compose_academic_risk_answer(summary: dict[str, Any]) -> str | None:
    return _compose_academic_risk_answer_module(summary, deps=_protected_answer_deps())


def _looks_like_academic_progression_followup(message: str) -> bool:
    return _looks_like_academic_progression_followup_module(message, deps=_protected_answer_deps())


def _compose_academic_progression_answer(
    summary: dict[str, Any],
    *,
    message: str,
) -> str | None:
    return _compose_academic_progression_answer_module(
        summary,
        message=message,
        deps=_protected_answer_deps(),
    )


def _compose_named_subject_grade_answer(summary: dict[str, Any], *, subject_hint: str | None) -> str | None:
    return _compose_named_subject_grade_answer_module(
        summary,
        subject_hint=subject_hint,
        deps=_protected_answer_deps(),
    )


def _compose_named_attendance_answer(summary: dict[str, Any], *, subject_hint: str | None = None) -> str | None:
    return _compose_named_attendance_answer_module(
        summary,
        subject_hint=subject_hint,
        deps=_protected_answer_deps(),
    )


def _build_academic_student_selection_clarify(
    ctx: SupervisorRunContext,
    *,
    reason: str,
    graph_path: list[str],
    confidence: float = 0.97,
) -> SupervisorAnswerPayload:
    return _build_academic_student_selection_clarify_module(
        ctx,
        reason=reason,
        graph_path=graph_path,
        confidence=confidence,
        deps=_protected_answer_deps(),
    )


def _resolved_academic_target_name(
    ctx: SupervisorRunContext,
    *,
    resolved: ResolvedTurnIntent | None = None,
) -> str | None:
    return _resolved_academic_target_name_module(
        ctx,
        resolved=resolved,
        deps=_protected_answer_deps(),
    )


def _needs_specific_academic_student_clarification(
    ctx: SupervisorRunContext,
    *,
    target_name: str | None,
    subject_hint: str | None,
) -> bool:
    return _needs_specific_academic_student_clarification_module(
        ctx,
        target_name=target_name,
        subject_hint=subject_hint,
        deps=_protected_answer_deps(),
    )


def _build_academic_finance_combo_payload(
    *,
    academic_summary: dict[str, Any],
    finance_summary: dict[str, Any],
    reason: str,
    graph_path: list[str],
) -> SupervisorAnswerPayload:
    return _build_academic_finance_combo_payload_module(
        academic_summary=academic_summary,
        finance_summary=finance_summary,
        reason=reason,
        graph_path=graph_path,
        deps=_protected_answer_deps(),
    )


def _compose_finance_aggregate_answer(summaries: list[dict[str, Any]]) -> str:
    return _compose_finance_aggregate_answer_module(summaries, deps=_protected_answer_deps())


def _compose_family_next_due_answer(summaries: list[dict[str, Any]]) -> str | None:
    return _compose_family_next_due_answer_module(summaries, deps=_protected_answer_deps())


def _compose_academic_aggregate_answer(summaries: list[dict[str, Any]]) -> str:
    return _compose_academic_aggregate_answer_module(summaries, deps=_protected_answer_deps())


def _looks_like_family_finance_aggregate_query(message: str) -> bool:
    return _looks_like_family_finance_aggregate_query_module(message, deps=_protected_answer_deps())


def _looks_like_family_academic_aggregate_query(message: str) -> bool:
    return _looks_like_family_academic_aggregate_query_module(message, deps=_protected_answer_deps())


def _looks_like_family_attendance_aggregate_query(message: str) -> bool:
    return _looks_like_family_attendance_aggregate_query_module(message, deps=_protected_answer_deps())


def _compose_finance_installments_answer(summary: dict[str, Any]) -> str:
    return _compose_finance_installments_answer_module(summary, deps=_protected_answer_deps())


def _resolved_intent_deps():
    return _build_resolved_intent_deps_module(
        normalize_text=_normalize_text,
        looks_like_subject_followup=_looks_like_subject_followup,
        looks_like_academic_risk_followup=_looks_like_academic_risk_followup,
        looks_like_family_finance_aggregate_query=_looks_like_family_finance_aggregate_query,
        looks_like_family_attendance_aggregate_query=_looks_like_family_attendance_aggregate_query,
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=_fetch_financial_summary_payload,
        fetch_upcoming_assessments_payload=_fetch_upcoming_assessments_payload,
        resolved_academic_target_name=_resolved_academic_target_name,
        needs_specific_academic_student_clarification=_needs_specific_academic_student_clarification,
        build_academic_student_selection_clarify=_build_academic_student_selection_clarify,
        compose_academic_risk_answer=_compose_academic_risk_answer,
        compose_named_subject_grade_answer=_compose_named_subject_grade_answer,
        compose_named_grade_answer=_compose_named_grade_answer,
        compose_named_attendance_answer=_compose_named_attendance_answer,
        compose_academic_snapshot_lines=_compose_academic_snapshot_lines,
        compose_academic_aggregate_answer=_compose_academic_aggregate_answer,
        compose_finance_aggregate_answer=_compose_finance_aggregate_answer,
        compose_family_next_due_answer=_compose_family_next_due_answer,
        compose_finance_installments_answer=_compose_finance_installments_answer,
        linked_students=_linked_students,
        safe_excerpt=_safe_excerpt,
        subject_hint_from_text=_subject_hint_from_text,
        recent_subject_from_context=_recent_subject_from_context,
        subject_code_from_hint=_subject_code_from_hint,
        student_hint_from_message=_student_hint_from_message,
        is_student_name_only_followup=_is_student_name_only_followup,
        compose_upcoming_assessments_lines=_compose_upcoming_assessments_lines,
    )


def _build_grade_requirement_answer(
    *,
    student: dict[str, Any],
    summary: dict[str, Any],
    subject_hint: str | None,
) -> SupervisorAnswerPayload:
    return _build_grade_requirement_answer_module(
        student=student,
        summary=summary,
        subject_hint=subject_hint,
        deps=_resolved_intent_deps(),
    )


def _compose_authenticated_scope_answer(actor: dict[str, Any] | None) -> str:
    return _compose_authenticated_scope_answer_module(actor, deps=_protected_answer_deps())


def _looks_like_third_party_student_data_request(message: str) -> bool:
    return _looks_like_third_party_student_data_request_module(message, deps=_protected_answer_deps())


def _build_third_party_student_data_denial() -> SupervisorAnswerPayload:
    return _build_third_party_student_data_denial_module()


def _recent_subject_from_context(
    summary: dict[str, Any],
    conversation_context: dict[str, Any] | None,
    *,
    operational_memory: OperationalMemory | None = None,
) -> str | None:
    return _recent_subject_from_context_module(
        summary,
        conversation_context,
        operational_memory=operational_memory,
        deps=_student_context_deps(),
    )


async def _create_visit_booking_payload(ctx: SupervisorRunContext) -> dict[str, Any]:
    return await _create_visit_booking_payload_io(
        ctx,
        http_post=_http_post,
        effective_conversation_id=_effective_conversation_id,
    )


async def _create_institutional_request_payload(
    ctx: SupervisorRunContext,
    *,
    target_area: str,
    category: str = "handoff",
) -> dict[str, Any]:
    return await _create_institutional_request_payload_io(
        ctx,
        target_area=target_area,
        category=category,
        http_post=_http_post,
        effective_conversation_id=_effective_conversation_id,
    )


async def _create_support_handoff_payload(
    ctx: SupervisorRunContext,
    *,
    queue_name: str,
    summary: str | None = None,
) -> dict[str, Any]:
    return await _create_support_handoff_payload_io(
        ctx,
        queue_name=queue_name,
        summary=summary,
        build_support_handoff_summary=_build_support_handoff_summary,
        http_post=_http_post,
        effective_conversation_id=_effective_conversation_id,
    )


async def _workflow_status_payload(
    ctx: SupervisorRunContext,
    *,
    workflow_kind: str | None = None,
    protocol_code_hint: str | None = None,
) -> dict[str, Any]:
    return await _workflow_status_payload_io(
        ctx,
        workflow_kind=workflow_kind,
        protocol_code_hint=protocol_code_hint,
        http_get=_http_get,
        effective_conversation_id=_effective_conversation_id,
    )


def _hypothetical_children_quantity(message: str) -> int | None:
    match = re.search(r"\b(\d{1,2})\s+filh(?:o|os)\b", _normalize_text(message))
    if not match:
        return None
    try:
        return max(1, int(match.group(1)))
    except Exception:
        return None


def _fast_path_answer(ctx: SupervisorRunContext) -> SupervisorAnswerPayload | None:
    return _build_fast_path_answer_module(
        ctx,
        FastPathDeps(
            normalize_text=_normalize_text,
            normalized_recent_user_messages=_normalized_recent_user_messages,
            is_simple_greeting=_is_simple_greeting,
            is_auth_guidance_query=_is_auth_guidance_query,
            compose_auth_guidance_answer=_compose_auth_guidance_answer,
            linked_students=_linked_students,
            compose_authenticated_scope_answer=_compose_authenticated_scope_answer,
            is_assistant_identity_query=_is_assistant_identity_query,
            compose_assistant_identity_answer=_compose_assistant_identity_answer,
            school_name=_school_name,
            safe_excerpt=_safe_excerpt,
            format_brl=_format_brl,
            hypothetical_children_quantity=_hypothetical_children_quantity,
            pricing_projection=_pricing_projection,
            compose_public_bolsas_and_processes=compose_public_bolsas_and_processes,
        ),
    )


def _tool_first_structured_deps():
    return _build_tool_first_structured_deps_module(
        normalize_text=_normalize_text,
        effective_multi_intent_domains=_effective_multi_intent_domains,
        create_support_handoff_payload=_create_support_handoff_payload,
        maybe_restricted_document_tool_first_answer=maybe_restricted_document_tool_first_answer,
        public_kwargs=dict(
            fetch_public_payload=_fetch_public_payload,
            http_get=_http_get,
            orchestrator_graph_rag_query=_orchestrator_graph_rag_query,
            orchestrator_retrieval_search=_orchestrator_retrieval_search,
            citation_from_retrieval_hit=_citation_from_retrieval_hit,
            select_public_graph_rag_fallback_hits=_select_public_graph_rag_fallback_hits,
            compose_public_graph_rag_fallback_answer=_compose_public_graph_rag_fallback_answer,
            supports_from_public_graph_rag_fallback_hits=_supports_from_public_graph_rag_fallback_hits,
            safe_excerpt=_safe_excerpt,
            timeline_entry=_timeline_entry,
            format_brl=_format_brl,
        ),
        workflow_kwargs=dict(
            http_post=_http_post,
            strip_none=_strip_none,
            effective_conversation_id=_effective_conversation_id,
            create_institutional_request_payload=_create_institutional_request_payload,
            create_visit_booking_payload=_create_visit_booking_payload,
            workflow_status_payload=_workflow_status_payload,
        ),
        protected_kwargs=dict(
            normalize_text=_normalize_text,
            contains_any=_contains_any,
            looks_like_admin_finance_combo_query=_looks_like_admin_finance_combo_query,
            looks_like_family_finance_aggregate_query=_looks_like_family_finance_aggregate_query,
            unknown_explicit_student_reference=_unknown_explicit_student_reference,
            student_hint_from_message=_student_hint_from_message,
            looks_like_student_pronoun_followup=_looks_like_student_pronoun_followup,
            fetch_financial_summary_payload=_fetch_financial_summary_payload,
            linked_students=_linked_students,
            compose_finance_installments_answer=_compose_finance_installments_answer,
            compose_finance_aggregate_answer=_compose_finance_aggregate_answer,
            compose_family_next_due_answer=_compose_family_next_due_answer,
            looks_like_academic_risk_followup=_looks_like_academic_risk_followup,
            looks_like_academic_progression_followup=_looks_like_academic_progression_followup,
            looks_like_family_academic_aggregate_query=_looks_like_family_academic_aggregate_query,
            looks_like_family_attendance_aggregate_query=_looks_like_family_attendance_aggregate_query,
            looks_like_upcoming_assessments_query=lambda message: any(
                term in _normalize_text(message)
                for term in {
                    "proxima prova",
                    "próxima prova",
                    "proxima avaliacao",
                    "próxima avaliação",
                    "proximas avaliacoes",
                    "próximas avaliações",
                    "proximas provas",
                    "próximas provas",
                    "provas e entregas",
                    "entregas",
                    "datas das provas",
                    "data das provas",
                    "datas das avaliacoes",
                    "datas das avaliações",
                    "datas das entregas",
                    "quando sao as proximas provas",
                    "quando são as próximas provas",
                    "quais as proximas datas",
                    "quais as próximas datas",
                }
            ),
            looks_like_attendance_timeline_query=lambda message: any(
                term in _normalize_text(message)
                for term in {
                    "faltas recentes",
                    "ausencias recentes",
                    "ausências recentes",
                    "frequencia dele",
                    "frequência dele",
                    "frequencia dela",
                    "frequência dela",
                }
            ),
            subject_hint_from_text=_subject_hint_from_text,
            looks_like_subject_followup=_looks_like_subject_followup,
            resolved_academic_target_name=_resolved_academic_target_name,
            needs_specific_academic_student_clarification=_needs_specific_academic_student_clarification,
            build_academic_student_selection_clarify=_build_academic_student_selection_clarify,
            fetch_academic_summary_payload=_fetch_academic_summary_payload,
            fetch_upcoming_assessments_payload=_fetch_upcoming_assessments_payload,
            fetch_attendance_timeline_payload=_fetch_attendance_timeline_payload,
            compose_academic_risk_answer=_compose_academic_risk_answer,
            compose_academic_progression_answer=_compose_academic_progression_answer,
            compose_named_subject_grade_answer=_compose_named_subject_grade_answer,
            compose_named_grade_answer=_compose_named_grade_answer,
            compose_named_attendance_answer=_compose_named_attendance_answer,
            compose_academic_snapshot_lines=_compose_academic_snapshot_lines,
            compose_academic_aggregate_answer=_compose_academic_aggregate_answer,
            compose_upcoming_assessments_lines=_compose_upcoming_assessments_lines,
            compose_attendance_timeline_lines=_compose_attendance_timeline_lines,
            safe_excerpt=_safe_excerpt,
            http_get=_http_get,
            compose_actor_admin_status_answer=_compose_actor_admin_status_answer,
            recent_student_from_context_with_memory=_recent_student_from_context_with_memory,
            compose_admin_status_answer=_compose_admin_status_answer,
            find_student_by_hint=_find_student_by_hint,
        ),
        student_hint_from_message=_student_hint_from_message,
        is_student_name_only_followup=_is_student_name_only_followup,
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=_fetch_financial_summary_payload,
        build_academic_finance_combo_payload=_build_academic_finance_combo_payload,
        safe_excerpt=_safe_excerpt,
        fetch_public_payload=_fetch_public_payload,
        format_brl=_format_brl,
    )


async def _tool_first_structured_answer(ctx: SupervisorRunContext) -> SupervisorAnswerPayload | None:
    return await _maybe_tool_first_structured_answer_module(
        ctx,
        deps=_tool_first_structured_deps(),
    )


async def _resolved_intent_answer(ctx: SupervisorRunContext) -> SupervisorAnswerPayload | None:
    return await _maybe_resolved_intent_answer_module(ctx, deps=_resolved_intent_deps())


def _academic_grade_requirement(summary: dict[str, Any], *, subject_hint: str | None) -> dict[str, Any]:
    return _academic_grade_requirement_module(
        summary,
        subject_hint=subject_hint,
        deps=_protected_answer_deps(),
    )


async def _academic_grade_fast_path_answer(ctx: SupervisorRunContext) -> SupervisorAnswerPayload | None:
    return await _maybe_academic_grade_fast_path_answer_module(ctx, deps=_resolved_intent_deps())


def _specialist_tool_deps() -> SpecialistToolDeps:
    return SpecialistToolDeps(
        fetch_public_school_profile=_fetch_public_school_profile,
        fetch_public_payload=_fetch_public_payload,
        http_get=_http_get,
        school_name=_school_name,
        orchestrator_retrieval_search=_orchestrator_retrieval_search,
        orchestrator_graph_rag_query=_orchestrator_graph_rag_query,
        pricing_projection=_pricing_projection,
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=_fetch_financial_summary_payload,
        subject_code_from_hint=_subject_code_from_hint,
        academic_grade_requirement=_academic_grade_requirement,
        strip_none=_strip_none,
        effective_conversation_id=_effective_conversation_id,
        detect_support_handoff_queue=_detect_support_handoff_queue,
        build_support_handoff_summary=_build_support_handoff_summary,
        create_support_handoff_payload=_create_support_handoff_payload,
        http_post=_http_post,
    )


def _specialist_tools():
    return _build_specialist_tools_module(deps=_specialist_tool_deps())


def _operational_memory_deps() -> OperationalMemoryDeps:
    return OperationalMemoryDeps(
        normalize_text=_normalize_text,
        looks_like_public_doc_bundle_request=_looks_like_public_doc_bundle_request,
        is_student_name_only_followup=_is_student_name_only_followup,
        effective_multi_intent_domains=_effective_multi_intent_domains,
        subject_hint_from_text=_subject_hint_from_text,
        looks_like_subject_followup=_looks_like_subject_followup,
        looks_like_student_pronoun_followup=_looks_like_student_pronoun_followup,
        student_hint_from_message=_student_hint_from_message,
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=_fetch_financial_summary_payload,
        fetch_upcoming_assessments_payload=_fetch_upcoming_assessments_payload,
        build_academic_finance_combo_payload=_build_academic_finance_combo_payload,
        build_grade_requirement_answer=_build_grade_requirement_answer,
        compose_academic_risk_answer=_compose_academic_risk_answer,
        compose_named_subject_grade_answer=_compose_named_subject_grade_answer,
        compose_upcoming_assessments_lines=_compose_upcoming_assessments_lines,
        safe_excerpt=_safe_excerpt,
        looks_like_academic_risk_followup=_looks_like_academic_risk_followup,
        looks_like_other_student_followup=_looks_like_other_student_followup,
        other_linked_student=_other_linked_student,
        compose_admin_status_answer=_compose_admin_status_answer,
        compose_named_grade_answer=_compose_named_grade_answer,
        compose_finance_installments_answer=_compose_finance_installments_answer,
        compose_family_next_due_answer=_compose_family_next_due_answer,
        linked_students=_linked_students,
    )


async def _operational_memory_follow_up_answer(ctx: SupervisorRunContext) -> SupervisorAnswerPayload | None:
    return await _maybe_operational_memory_follow_up_answer_module(
        ctx,
        deps=_operational_memory_deps(),
    )


async def _general_knowledge_fast_path_answer(ctx: SupervisorRunContext) -> SupervisorAnswerPayload | None:
    return await _general_knowledge_fast_path_answer_module(
        ctx,
        deps=GeneralKnowledgeDeps(
            looks_like_general_knowledge_query=_looks_like_general_knowledge_query,
            agent_model=_agent_model,
            run_config=_run_config,
            effective_conversation_id=_effective_conversation_id,
            safe_excerpt=_safe_excerpt,
            default_suggested_replies=_default_suggested_replies,
        ),
    )


def _specialist_agent_deps() -> SpecialistAgentDeps:
    tools = _specialist_tools()
    return SpecialistAgentDeps(
        resolve_llm_provider=resolve_llm_provider,
        get_public_profile_bundle=tools.get_public_profile_bundle,
        fetch_academic_policy=tools.fetch_academic_policy,
        search_public_documents=tools.search_public_documents,
        search_private_documents=tools.search_private_documents,
        run_graph_rag_query=tools.run_graph_rag_query,
        project_public_pricing=tools.project_public_pricing,
        fetch_actor_identity=tools.fetch_actor_identity,
        fetch_academic_summary=tools.fetch_academic_summary,
        fetch_upcoming_assessments=tools.fetch_upcoming_assessments,
        fetch_attendance_timeline=tools.fetch_attendance_timeline,
        calculate_grade_requirement=tools.calculate_grade_requirement,
        fetch_financial_summary=tools.fetch_financial_summary,
        fetch_workflow_status=tools.fetch_workflow_status,
        create_support_handoff=tools.create_support_handoff,
        create_visit_booking=tools.create_visit_booking,
        update_visit_booking=tools.update_visit_booking,
        create_institutional_request=tools.create_institutional_request,
        update_institutional_request=tools.update_institutional_request,
    )


def _build_guardrail_agent(model: Any) -> Agent[SupervisorRunContext]:
    return _build_guardrail_agent_module(model)


def _supports_tool_json_outputs(settings: Any) -> bool:
    return _supports_tool_json_outputs_module(settings, deps=_specialist_agent_deps())


def _tool_model_settings(settings: Any, *, require_tool_use: bool = True) -> ModelSettings:
    return _tool_model_settings_module(
        settings,
        deps=_specialist_agent_deps(),
        require_tool_use=require_tool_use,
    )


def _specialist_result_contract() -> str:
    return _specialist_result_contract_module()


def _manager_result_contract() -> str:
    return _manager_result_contract_module()


def _repair_result_contract() -> str:
    return _repair_result_contract_module()


def _sorted_specialist_ids(ctx: SupervisorRunContext, specialist_ids: list[str]) -> list[str]:
    return sorted(
        [item for item in specialist_ids if item in EXECUTION_SPECIALISTS],
        key=lambda item: (
            int(getattr(ctx.specialist_registry.get(item), "execution_priority", 100)),
            item,
        ),
    )


def _parse_specialist_results(trace: SupervisorTrace) -> list[SpecialistResult]:
    return _parse_specialist_results_module(trace)


def _merge_specialist_results(
    precomputed_results: list[SpecialistResult],
    traced_results: list[SpecialistResult],
) -> list[SpecialistResult]:
    return _merge_specialist_results_module(precomputed_results, traced_results)


def _direct_compose_candidate(
    ctx: SupervisorRunContext,
    *,
    plan: SupervisorPlan,
    specialist_results: list[SpecialistResult],
) -> SpecialistResult | None:
    return _direct_compose_candidate_module(
        ctx,
        plan=plan,
        specialist_results=specialist_results,
        normalize_text=_normalize_text,
    )


def _build_multi_specialist_answer_from_results(
    ctx: SupervisorRunContext,
    *,
    plan: SupervisorPlan,
    specialist_results: list[SpecialistResult],
) -> SupervisorAnswerPayload | None:
    return _build_multi_specialist_answer_from_results_module(
        ctx,
        plan=plan,
        specialist_results=specialist_results,
        normalize_text=_normalize_text,
        safe_excerpt=_safe_excerpt,
    )


def _build_direct_answer_from_specialist(
    ctx: SupervisorRunContext,
    *,
    plan: SupervisorPlan,
    result: SpecialistResult,
) -> SupervisorAnswerPayload:
    return _build_direct_answer_from_specialist_module(
        ctx,
        plan=plan,
        result=result,
        safe_excerpt=_safe_excerpt,
    )


def _budgeted_no_manager_candidate(
    ctx: SupervisorRunContext,
    *,
    specialist_results: list[SpecialistResult],
) -> SpecialistResult | None:
    return _budgeted_no_manager_candidate_module(
        ctx,
        specialist_results=specialist_results,
        normalize_text=_normalize_text,
    )


def _institution_specialist(settings: Any, model: Any) -> Agent[SupervisorRunContext]:
    return _institution_specialist_module(settings, model, deps=_specialist_agent_deps())


def _academic_specialist(settings: Any, model: Any) -> Agent[SupervisorRunContext]:
    return _academic_specialist_module(settings, model, deps=_specialist_agent_deps())


def _finance_specialist(settings: Any, model: Any) -> Agent[SupervisorRunContext]:
    return _finance_specialist_module(settings, model, deps=_specialist_agent_deps())


def _workflow_specialist(settings: Any, model: Any) -> Agent[SupervisorRunContext]:
    return _workflow_specialist_module(settings, model, deps=_specialist_agent_deps())


def _document_specialist(settings: Any, model: Any) -> Agent[SupervisorRunContext]:
    return _document_specialist_module(settings, model, deps=_specialist_agent_deps())


def _manager_instructions(plan: SupervisorPlan) -> str:
    return _manager_instructions_module(plan)


def _judge_instructions() -> str:
    return _judge_instructions_module()


def _repair_instructions() -> str:
    return _repair_instructions_module()

def _build_manager_agent(*, settings: Any, model: Any, plan: SupervisorPlan, specialist_tools: list[Any]) -> Agent[SupervisorRunContext]:
    return _build_manager_agent_module(
        settings=settings,
        model=model,
        plan=plan,
        specialist_tools=specialist_tools,
        deps=_specialist_agent_deps(),
    )


def _build_judge_agent(model: Any) -> Agent[SupervisorRunContext]:
    return _build_judge_agent_module(model)


def _build_repair_agent(settings: Any, model: Any) -> Agent[SupervisorRunContext]:
    return _build_repair_agent_module(settings, model, deps=_specialist_agent_deps())


def _log_execution_budget(plan: SupervisorPlan, execution_budget: ExecutionBudget) -> None:
    logger.info(
        "specialist_supervisor_execution_budget",
        extra={
            "primary_domain": plan.primary_domain,
            "specialists": list(plan.specialists),
            "strategy": plan.retrieval_strategy,
            "budget_tier": execution_budget.tier,
            "budget_reasons": list(execution_budget.reasons),
            "allow_manager": execution_budget.allow_manager,
            "allow_judge": execution_budget.allow_judge,
            "allow_repair": execution_budget.allow_repair,
            "target_latency_ms": execution_budget.target_latency_ms,
        },
    )


def _supervisor_run_flow_deps():
    return _build_supervisor_run_flow_deps_module(
        run_context_cls=SupervisorRunContext,
        get_specialist_registry=get_specialist_registry,
        preflight_public_doc_bundle_answer=_preflight_public_doc_bundle_answer,
        looks_like_internal_document_query=_looks_like_internal_document_query,
        fetch_actor_context=_fetch_actor_context,
        fetch_conversation_context=_fetch_conversation_context,
        load_operational_memory=_load_operational_memory,
        resolve_turn_intent=_resolve_turn_intent,
        tool_first_structured_answer=_tool_first_structured_answer,
        persist_final_answer=_persist_final_answer,
        fetch_public_school_profile=_fetch_public_school_profile,
        orchestrator_preview=_orchestrator_preview,
        teacher_scope_fast_path_answer=maybe_teacher_scope_fast_path_answer,
        academic_grade_fast_path_answer=_academic_grade_fast_path_answer,
        looks_like_third_party_student_data_request=_looks_like_third_party_student_data_request,
        build_third_party_student_data_denial=_build_third_party_student_data_denial,
        operational_memory_follow_up_answer=_operational_memory_follow_up_answer,
        fast_path_answer=_fast_path_answer,
        resolved_intent_answer=_resolved_intent_answer,
        general_knowledge_fast_path_answer=_general_knowledge_fast_path_answer,
        resolve_llm_provider=resolve_llm_provider,
        effective_llm_model_name=effective_llm_model_name,
        default_suggested_replies=_default_suggested_replies,
        run_input_guardrail_stage=_run_input_guardrail_stage,
        run_retrieval_planner_stage=_run_retrieval_planner_stage,
        resolve_plan_and_budget=_resolve_plan_and_budget,
        execution_budget_metadata=_execution_budget_metadata,
        metadata_with_runtime_observability=_metadata_with_runtime_observability,
        build_budgeted_execution_specialists=_build_budgeted_execution_specialists,
        agent_model_for_role=_agent_model_for_role,
        execute_budgeted_specialists=_execute_budgeted_specialists,
        build_multi_specialist_answer_from_results=_build_multi_specialist_answer_from_results,
        direct_compose_candidate=_direct_compose_candidate,
        build_direct_answer_from_specialist=_build_direct_answer_from_specialist,
        budgeted_no_manager_candidate=_budgeted_no_manager_candidate,
        needs_manager=_needs_manager,
        run_manager_stack=_run_manager_stack,
        merge_specialist_results=_merge_specialist_results,
        parse_specialist_results=_parse_specialist_results,
        grounding_gate_answer=_grounding_gate_answer,
        build_answer_payload=_build_answer_payload,
        safe_supervisor_fallback_answer=_safe_supervisor_fallback_answer,
        access_tier_for_domain=_access_tier_for_domain,
        log_execution_budget=_log_execution_budget,
    )


async def run_specialist_supervisor(
    *,
    request: SpecialistSupervisorRequest,
    settings: Any,
) -> dict[str, Any]:
    return await _run_specialist_supervisor_module(
        request=request,
        settings=settings,
        deps=_supervisor_run_flow_deps(),
    )
