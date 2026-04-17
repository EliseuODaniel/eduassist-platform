# ruff: noqa: F401

from __future__ import annotations

import asyncio
import base64
import io
import re
import unicodedata
from collections.abc import Callable
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from time import monotonic
from types import SimpleNamespace
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from PIL import Image, ImageDraw, ImageFont

from eduassist_observability import (
    canonicalize_evidence_strategy,
    canonicalize_risk_flags,
    record_counter,
    record_histogram,
    set_span_attributes,
    start_span,
)
from eduassist_semantic_ingress import (
    looks_like_language_preference_feedback,
    looks_like_school_scope_message,
    looks_like_scope_boundary_candidate,
)

from .candidate_builder import build_response_candidate
from .candidate_chooser import choose_best_candidate
from .entity_resolution import resolve_entity_hints
from .evidence_pack import (
    build_direct_answer_evidence_pack,
    build_known_unknown_evidence_pack,
    build_retrieval_evidence_pack,
    build_structured_tool_evidence_pack,
)
from .final_polish_policy import build_final_polish_decision
from .graph import to_preview
from .graph_rag_runtime import graph_rag_workspace_ready, run_graph_rag_query
from .langgraph_local_llm import (
    compose_langgraph_public_grounded_with_provider,
    compose_langgraph_with_provider,
    polish_langgraph_with_provider,
    resolve_langgraph_public_semantic_with_provider,
    revise_langgraph_with_provider,
    verify_langgraph_answer_against_contract,
)
from .langgraph_runtime import (
    get_langgraph_artifacts,
    get_orchestration_state_snapshot,
    invoke_orchestration_graph,
    resolve_langgraph_thread_id,
)
from .langgraph_trace import build_langgraph_trace_sections
from .llm_provider import judge_answer_relevance_with_provider
from .models import (
    AccessTier,
    AnswerVerificationResult,
    CalendarEventCard,
    ConversationContextBundle,
    ConversationSlotMemory,
    IntentClassification,
    InternalSpecialistPlan,
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageResponse,
    MessageResponseCitation,
    MessageResponseRequest,
    MessageResponseSuggestedReply,
    MessageResponseVisualAsset,
    OrchestrationMode,
    OrchestrationPreview,
    OrchestrationRequest,
    ProtectedAttributeRequest,
    PublicActRule,
    PublicAnswerabilityAssessment,
    PublicInstitutionPlan,
    PublicProfileContext,
    QueryDomain,
    RetrievalBackend,
    RetrievalProfile,
    StructuredAnswerFrame,
    UserContext,
    UserRole,
)
from .public_agentic_engine import build_public_evidence_bundle
from .public_doc_knowledge import (
    compose_public_bolsas_and_processes,
    compose_public_calendar_visibility,
    compose_public_canonical_lane_answer,
    compose_public_conduct_policy_contextual_answer,
    compose_public_family_new_calendar_assessment_enrollment,
    compose_public_first_month_risks,
    compose_public_health_authorizations_bridge,
    compose_public_health_second_call,
    compose_public_outings_authorizations,
    compose_public_permanence_and_family_support,
    compose_public_process_compare,
    compose_public_transport_uniform_bundle,
    match_public_canonical_lane,
)
from .public_known_unknowns import (
    compose_public_known_unknown_answer,
    detect_public_known_unknown_key,
)
from .request_intent_guardrails import (
    looks_like_explicit_admin_status_query,
    looks_like_school_domain_request,
)
from .response_cache import get_cached_public_response, store_cached_public_response
from .retrieval import (
    can_read_restricted_documents,
    compose_restricted_document_grounded_answer_for_query,
    compose_restricted_document_no_match_answer,
    get_retrieval_service,
    looks_like_restricted_document_query,
    select_relevant_restricted_hits,
)
from .retrieval_aware_router import build_public_evidence_probe, build_routing_decision
from .runtime_core_constants import *  # noqa: F403
from .serving_policy import LoadSnapshot, build_public_serving_policy
from .serving_telemetry import get_stack_telemetry_snapshot, record_stack_outcome
from .specialist_trace import build_specialist_trace_sections

DEFAULT_PUBLIC_HELP = (
    'Posso ajudar com informacoes publicas da escola, como calendario, matricula, '
    'documentos exigidos e regras de atendimento digital.'
)
_PUBLIC_RESOURCE_CACHE_TTL_SECONDS = 120.0
_PUBLIC_RESOURCE_CACHE: dict[str, dict[str, Any]] = {}


def _llm_forced_mode_enabled(
    *, settings: Any, request: MessageResponseRequest | Any | None = None
) -> bool:
    if bool(getattr(settings, 'feature_flag_final_polish_force_llm', False)):
        return True
    debug_options = getattr(request, 'debug_options', None)
    if isinstance(debug_options, dict):
        return bool(debug_options.get('llm_forced_mode'))
    return False

# Extracted bridge modules. Imported at the end so the shared runtime helper
# namespace is fully defined before the bridge modules reuse it.


def _export_module_namespace(module: object) -> None:
    for name, value in vars(module).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


from . import runtime_api as _runtime_api  # noqa: E402

_export_module_namespace(_runtime_api)

from . import conversation_focus_runtime as _conversation_focus_runtime  # noqa: E402

_export_module_namespace(_conversation_focus_runtime)

from . import intent_analysis_runtime as _intent_analysis_runtime  # noqa: E402

_export_module_namespace(_intent_analysis_runtime)

from . import analysis_context_runtime as _analysis_context_runtime  # noqa: E402

_export_module_namespace(_analysis_context_runtime)

from . import public_act_rules_runtime as _public_act_rules_runtime  # noqa: E402

_export_module_namespace(_public_act_rules_runtime)

from . import student_scope_runtime as _student_scope_runtime  # noqa: E402

_export_module_namespace(_student_scope_runtime)

from . import protected_domain_runtime as _protected_domain_runtime  # noqa: E402

_export_module_namespace(_protected_domain_runtime)

from . import protected_summary_runtime as _protected_summary_runtime  # noqa: E402

_export_module_namespace(_protected_summary_runtime)

from . import public_orchestration_runtime as _public_orchestration_runtime  # noqa: E402

_export_module_namespace(_public_orchestration_runtime)

from . import workflow_runtime as _workflow_runtime  # noqa: E402

_export_module_namespace(_workflow_runtime)

from . import public_profile_runtime as _public_profile_runtime  # noqa: E402

_export_module_namespace(_public_profile_runtime)

from . import reply_experience_runtime as _reply_experience_runtime  # noqa: E402

_export_module_namespace(_reply_experience_runtime)

from . import answer_verification_runtime as _answer_verification_runtime  # noqa: E402

_export_module_namespace(_answer_verification_runtime)

from . import protected_records_runtime as _protected_records_runtime  # noqa: E402

_export_module_namespace(_protected_records_runtime)

from . import structured_tool_runtime as _structured_tool_runtime  # noqa: E402

_export_module_namespace(_structured_tool_runtime)

from . import message_response_runtime as _message_response_runtime  # noqa: E402

_export_module_namespace(_message_response_runtime)
