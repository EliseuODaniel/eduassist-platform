from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from eduassist_observability import record_counter, set_span_attributes

from .models import QueryDomain, RetrievalProfile
from .turn_frame_policy import turn_frame_capability_id


@dataclass(frozen=True)
class RetrievalExecutionPolicy:
    profile: RetrievalProfile | None
    top_k: int
    category: str | None
    reason: str
    capability_id: str | None = None


@dataclass(frozen=True)
class _CapabilityPolicyDefaults:
    profile: RetrievalProfile
    top_k: int
    category: str | None = None


_CAPABILITY_POLICY_DEFAULTS: dict[str, _CapabilityPolicyDefaults] = {
    "public.contacts.leadership": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.cheap,
        top_k=3,
    ),
    "public.facilities.library.exists": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.cheap,
        top_k=3,
    ),
    "public.facilities.library.hours": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.cheap,
        top_k=3,
    ),
    "public.schedule.class_start_time": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.cheap,
        top_k=3,
        category="calendar",
    ),
    "public.schedule.class_end_time": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.cheap,
        top_k=3,
        category="calendar",
    ),
    "public.schedule.shift_offers": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.default,
        top_k=4,
        category="calendar",
    ),
    "public.calendar.year_start": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.deep,
        top_k=5,
        category="calendar",
    ),
    "public.enrollment.required_documents": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.deep,
        top_k=5,
    ),
    "public.enrollment.pricing": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.deep,
        top_k=5,
    ),
    "public.curriculum.overview": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.deep,
        top_k=5,
    ),
    "public.identity.confessional": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.deep,
        top_k=4,
    ),
    "public.web.news": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.deep,
        top_k=5,
    ),
    "protected.finance.summary": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.default,
        top_k=4,
    ),
    "protected.finance.next_due": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.cheap,
        top_k=3,
    ),
    "protected.academic.grades": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.default,
        top_k=4,
    ),
    "protected.academic.attendance": _CapabilityPolicyDefaults(
        profile=RetrievalProfile.default,
        top_k=4,
    ),
}

_RESTRICTED_QUERY_COMPLEXITY_HINTS = {
    "telegram",
    "escopo",
    "parcial",
    "professor",
    "devolutiva",
    "pedagogica",
    "pedagógica",
    "comunicacao",
    "comunicação",
    "avaliacoes",
    "avaliações",
    "negociacao",
    "negociação",
    "financeira",
    "financeiro",
    "intercambio",
    "intercâmbio",
    "internacional",
    "hospedagem",
    "viagem",
    "excursao",
    "excursão",
}


def _normalize_text(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _restricted_query_complexity_bonus(query: str) -> int:
    normalized = _normalize_text(query)
    if not normalized:
        return 0
    matched = sum(
        1
        for hint in _RESTRICTED_QUERY_COMPLEXITY_HINTS
        if hint in normalized
    )
    if matched >= 3:
        return 2
    if matched >= 1:
        return 1
    return 0


def _policy_profile_value(policy: RetrievalExecutionPolicy) -> str:
    return policy.profile.value if isinstance(policy.profile, RetrievalProfile) else "baseline"


def _finalize_policy(
    *,
    policy: RetrievalExecutionPolicy,
    visibility: str,
) -> RetrievalExecutionPolicy:
    metric_attributes = {
        "visibility": visibility,
        "reason": policy.reason,
        "profile": _policy_profile_value(policy),
        "category": policy.category or "all",
        "capability_id": policy.capability_id or "none",
    }
    set_span_attributes(
        **{
            "eduassist.retrieval.policy.visibility": visibility,
            "eduassist.retrieval.policy.reason": policy.reason,
            "eduassist.retrieval.policy.profile": _policy_profile_value(policy),
            "eduassist.retrieval.policy.top_k": policy.top_k,
            "eduassist.retrieval.policy.category": policy.category or "",
            "eduassist.retrieval.policy.capability_id": policy.capability_id or "",
        }
    )
    record_counter(
        "eduassist_retrieval_policy_decisions",
        attributes=metric_attributes,
        description="Retrieval policy decisions resolved before hybrid search execution.",
    )
    return policy


def build_retrieval_trace_metadata(
    *,
    visibility: str,
    policy: RetrievalExecutionPolicy,
    search: Any | None = None,
    selected_hit_count: int | None = None,
    citations_count: int | None = None,
    query_hints: set[str] | None = None,
    hints_supported: bool | None = None,
    canonical_lane: str | None = None,
    answerability: Any | None = None,
) -> dict[str, Any]:
    query_plan = getattr(search, "query_plan", None)
    trace_metadata: dict[str, Any] = {
        "retrieval_policy": {
            "visibility": visibility,
            "reason": policy.reason,
            "profile": _policy_profile_value(policy),
            "top_k": int(policy.top_k),
            "category": policy.category or "",
            "capability_id": policy.capability_id or "",
        }
    }
    if search is None:
        return trace_metadata

    trace_metadata["retrieval_result"] = {
        "total_hits": int(getattr(search, "total_hits", 0) or 0),
        "selected_hit_count": int(selected_hit_count if selected_hit_count is not None else getattr(search, "total_hits", 0) or 0),
        "document_group_count": len(getattr(search, "document_groups", []) or []),
        "citations_count": int(citations_count or 0),
        "query_hint_count": len(query_hints or ()),
        "hints_supported": bool(hints_supported) if hints_supported is not None else None,
        "canonical_lane": canonical_lane or "",
        "query_plan_intent": str(getattr(query_plan, "intent", "") or ""),
        "query_plan_profile": str(getattr(getattr(query_plan, "profile", None), "value", getattr(query_plan, "profile", "") or "")),
        "coverage_ratio": float(getattr(query_plan, "coverage_ratio", 0.0) or 0.0),
        "reranker_applied": bool(getattr(query_plan, "reranker_applied", False)),
        "corrective_retry_applied": bool(getattr(query_plan, "corrective_retry_applied", False)),
        "citation_first_recommended": bool(getattr(query_plan, "citation_first_recommended", False)),
        "category_bias": str(getattr(query_plan, "category_bias", "") or ""),
    }
    if answerability is not None:
        trace_metadata["retrieval_result"]["answerable"] = bool(
            getattr(answerability, "enough_support", False)
        )
        trace_metadata["retrieval_result"]["answerability_coverage_ratio"] = float(
            getattr(answerability, "coverage_ratio", 0.0) or 0.0
        )
        trace_metadata["retrieval_result"]["unsupported_term_count"] = len(
            getattr(answerability, "unsupported_terms", ()) or ()
        )
    return trace_metadata


def _domain_from_preview(preview: Any | None) -> QueryDomain | None:
    classification = getattr(preview, "classification", None)
    if classification is None:
        return None
    domain = getattr(classification, "domain", None)
    if isinstance(domain, QueryDomain):
        return domain
    value = str(domain or "").strip().lower()
    return next((item for item in QueryDomain if item.value == value), None)


def _capability_from_public_plan(public_plan: Any | None) -> str | None:
    if public_plan is None:
        return None
    act = str(getattr(public_plan, "conversation_act", "") or "").strip().lower()
    focus = str(getattr(public_plan, "focus_hint", "") or "").strip().lower()
    requested_attribute = str(getattr(public_plan, "requested_attribute", "") or "").strip().lower()

    if act == "leadership":
        return "public.contacts.leadership"
    if act == "document_submission":
        return "public.enrollment.required_documents"
    if act == "pricing":
        return "public.enrollment.pricing"
    if act == "timeline":
        return "public.calendar.year_start"
    if act == "features" and focus == "library":
        return "public.facilities.library.exists"
    if act == "operating_hours" and focus == "library":
        return "public.facilities.library.hours"
    if act == "schedule":
        if requested_attribute == "start_time":
            return "public.schedule.class_start_time"
        if requested_attribute == "end_time":
            return "public.schedule.class_end_time"
        return "public.schedule.shift_offers"
    return None


def infer_retrieval_capability_id(
    *,
    turn_frame: Any | None = None,
    public_plan: Any | None = None,
) -> str | None:
    return turn_frame_capability_id(turn_frame) or _capability_from_public_plan(public_plan)


def _merge_top_k(*, baseline_top_k: int, override_top_k: int, profile: RetrievalProfile) -> int:
    if profile is RetrievalProfile.deep:
        return max(baseline_top_k, override_top_k)
    if profile is RetrievalProfile.cheap:
        return min(baseline_top_k, override_top_k)
    return override_top_k


def resolve_retrieval_execution_policy(
    *,
    query: str,
    visibility: str,
    baseline_top_k: int,
    baseline_category: str | None = None,
    preview: Any | None = None,
    turn_frame: Any | None = None,
    public_plan: Any | None = None,
    profile_override: RetrievalProfile | None = None,
) -> RetrievalExecutionPolicy:
    capability_id = infer_retrieval_capability_id(turn_frame=turn_frame, public_plan=public_plan)
    if profile_override is not None:
        return _finalize_policy(
            visibility=visibility,
            policy=RetrievalExecutionPolicy(
            profile=profile_override,
            top_k=baseline_top_k,
            category=baseline_category,
            reason="explicit_override",
            capability_id=capability_id,
            ),
        )

    if visibility != "public":
        complexity_bonus = _restricted_query_complexity_bonus(query)
        return _finalize_policy(
            visibility=visibility,
            policy=RetrievalExecutionPolicy(
            profile=RetrievalProfile.deep,
            top_k=max(baseline_top_k, 5 + complexity_bonus),
            category=baseline_category,
            reason=(
                "restricted_visibility:complex_query"
                if complexity_bonus
                else "restricted_visibility"
            ),
            capability_id=capability_id,
            ),
        )

    defaults = _CAPABILITY_POLICY_DEFAULTS.get(capability_id or "")
    if defaults is not None:
        return _finalize_policy(
            visibility=visibility,
            policy=RetrievalExecutionPolicy(
            profile=defaults.profile,
            top_k=_merge_top_k(
                baseline_top_k=baseline_top_k,
                override_top_k=defaults.top_k,
                profile=defaults.profile,
            ),
            category=defaults.category if defaults.category is not None else baseline_category,
            reason=f"capability:{capability_id}",
            capability_id=capability_id,
            ),
        )

    domain = _domain_from_preview(preview)
    if domain is QueryDomain.calendar:
        return _finalize_policy(
            visibility=visibility,
            policy=RetrievalExecutionPolicy(
            profile=RetrievalProfile.deep,
            top_k=max(baseline_top_k, 5),
            category=baseline_category or "calendar",
            reason="domain:calendar",
            capability_id=capability_id,
            ),
        )
    if domain is QueryDomain.finance:
        return _finalize_policy(
            visibility=visibility,
            policy=RetrievalExecutionPolicy(
            profile=RetrievalProfile.default,
            top_k=max(3, baseline_top_k),
            category=baseline_category,
            reason="domain:finance",
            capability_id=capability_id,
            ),
        )

    return _finalize_policy(
        visibility=visibility,
        policy=RetrievalExecutionPolicy(
            profile=None,
            top_k=baseline_top_k,
            category=baseline_category,
            reason="baseline_default",
            capability_id=capability_id,
        ),
    )
