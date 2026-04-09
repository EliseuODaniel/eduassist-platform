from __future__ import annotations

from time import monotonic
from typing import Any

import httpx
from eduassist_observability import record_counter, record_histogram, set_span_attributes, start_span

from api_core.contracts import ActorContext, PolicyDecision
from api_core.config import get_settings


def _local_policy_decision(
    *,
    action: str,
    actor: ActorContext,
    resource: dict[str, Any] | None = None,
) -> PolicyDecision:
    resource = resource or {}
    role = str(actor.role_code or "").strip()
    student_id = str(resource.get("student_id") or "").strip()
    class_id = str(resource.get("class_id") or "").strip()
    teacher_id = str(resource.get("teacher_id") or "").strip()
    user_id = str(resource.get("user_id") or "").strip()
    scope = str(resource.get("scope") or "").strip()

    if action == "health.read":
        return PolicyDecision(allow=True, reason="health_check", source="local_fallback")

    if action == "identity.context.read" and actor.authenticated:
        return PolicyDecision(
            allow=True,
            reason="identity_context_for_authenticated_actor",
            source="local_fallback",
        )

    if action == "calendar.read" and resource.get("visibility") == "public":
        return PolicyDecision(allow=True, reason="public_calendar", source="local_fallback")

    if action == "ticket.create":
        return PolicyDecision(allow=True, reason="public_ticket_creation", source="local_fallback")

    if action == "student.academic.read":
        if actor.authenticated and role == "guardian" and student_id in {str(item) for item in actor.academic_student_ids}:
            return PolicyDecision(allow=True, reason="guardian_linked_academic_access", source="local_fallback")
        if actor.authenticated and role == "student" and student_id and student_id == str(actor.student_id or ""):
            return PolicyDecision(allow=True, reason="student_self_academic_access", source="local_fallback")
        if actor.authenticated and role == "teacher" and class_id and class_id in {str(item) for item in actor.accessible_class_ids}:
            return PolicyDecision(allow=True, reason="teacher_class_academic_access", source="local_fallback")
        if actor.authenticated and role in {"coordinator", "admin"}:
            return PolicyDecision(allow=True, reason="coordination_academic_access", source="local_fallback")
        return PolicyDecision(allow=False, reason="no_matching_policy", source="local_fallback")

    if action == "student.finance.read":
        if actor.authenticated and role == "guardian" and student_id in {str(item) for item in actor.financial_student_ids}:
            return PolicyDecision(allow=True, reason="guardian_linked_finance_access", source="local_fallback")
        if actor.authenticated and role == "student" and student_id and student_id == str(actor.student_id or ""):
            return PolicyDecision(allow=True, reason="student_self_finance_access", source="local_fallback")
        if actor.authenticated and role in {"finance", "admin"}:
            return PolicyDecision(allow=True, reason="finance_team_access", source="local_fallback")
        return PolicyDecision(allow=False, reason="no_matching_policy", source="local_fallback")

    if action == "student.admin.read":
        if actor.authenticated and role == "guardian" and student_id in {str(item) for item in actor.linked_student_ids}:
            return PolicyDecision(allow=True, reason="guardian_linked_admin_access", source="local_fallback")
        if actor.authenticated and role == "student" and student_id and student_id == str(actor.student_id or ""):
            return PolicyDecision(allow=True, reason="student_self_admin_access", source="local_fallback")
        if actor.authenticated and role in {"coordinator", "admin"}:
            return PolicyDecision(allow=True, reason="coordination_admin_access", source="local_fallback")
        return PolicyDecision(allow=False, reason="no_matching_policy", source="local_fallback")

    if action == "teacher.schedule.read":
        if actor.authenticated and role == "teacher" and teacher_id and teacher_id == str(actor.teacher_id or ""):
            return PolicyDecision(allow=True, reason="teacher_own_schedule", source="local_fallback")
        if actor.authenticated and role in {"coordinator", "admin"}:
            return PolicyDecision(allow=True, reason="admin_schedule_access", source="local_fallback")
        return PolicyDecision(allow=False, reason="no_matching_policy", source="local_fallback")

    if action == "actor.administrative.read":
        if actor.authenticated and user_id and user_id == str(actor.user_id):
            return PolicyDecision(allow=True, reason="self_administrative_status_read", source="local_fallback")
        return PolicyDecision(allow=False, reason="no_matching_policy", source="local_fallback")

    if action == "operations.overview.read":
        if actor.authenticated and scope == "self":
            return PolicyDecision(allow=True, reason="self_operations_overview", source="local_fallback")
        if actor.authenticated and scope == "global" and role in {"staff", "finance", "coordinator", "admin"}:
            return PolicyDecision(allow=True, reason="global_operations_overview", source="local_fallback")
        return PolicyDecision(allow=False, reason="no_matching_policy", source="local_fallback")

    if action == "support.handoffs.read":
        if actor.authenticated and scope == "self":
            return PolicyDecision(allow=True, reason="self_support_handoffs_read", source="local_fallback")
        if actor.authenticated and scope == "global" and role in {"staff", "finance", "coordinator", "admin"}:
            return PolicyDecision(allow=True, reason="global_support_handoffs_read", source="local_fallback")
        return PolicyDecision(allow=False, reason="no_matching_policy", source="local_fallback")

    if action == "support.handoffs.manage":
        if actor.authenticated and role in {"staff", "finance", "coordinator", "admin"}:
            return PolicyDecision(allow=True, reason="manage_support_handoffs", source="local_fallback")
        return PolicyDecision(allow=False, reason="no_matching_policy", source="local_fallback")

    return PolicyDecision(allow=False, reason="no_matching_policy", source="local_fallback")


async def decide_policy(
    *,
    action: str,
    actor: ActorContext,
    resource: dict[str, Any] | None = None,
) -> PolicyDecision:
    settings = get_settings()
    started_at = monotonic()
    payload = {
        'input': {
            'action': action,
            'subject': actor.to_policy_subject(),
            'resource': resource or {},
        }
    }

    with start_span(
        'eduassist.policy.decide',
        tracer_name='eduassist.api_core.policy',
        **{
            'eduassist.policy.action': action,
            'eduassist.actor.role': actor.role_code,
            'eduassist.actor.authenticated': actor.authenticated,
            'eduassist.resource.type': (resource or {}).get('resource_type'),
        },
    ):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(f'{settings.opa_url}/v1/data/eduassist/authz/decision', json=payload)
                response.raise_for_status()
                result = response.json().get('result')
                if isinstance(result, dict) and 'allow' in result:
                    decision = PolicyDecision(
                        allow=bool(result.get('allow', False)),
                        reason=str(result.get('reason', 'no_reason_from_opa')),
                        source='opa',
                    )
                else:
                    decision = _local_policy_decision(
                        action=action,
                        actor=actor,
                        resource=resource,
                    )
                set_span_attributes(
                    **{
                        'http.status_code': response.status_code,
                        'eduassist.policy.allow': decision.allow,
                        'eduassist.policy.reason': decision.reason,
                        'eduassist.policy.source': decision.source,
                    },
                )
                _record_policy_metrics(
                    action=action,
                    actor=actor,
                    decision=decision,
                    resource=resource,
                    latency_ms=(monotonic() - started_at) * 1000,
                )
                return decision
        except Exception as exc:  # pragma: no cover - network fallback path
            decision = _local_policy_decision(
                action=action,
                actor=actor,
                resource=resource,
            )
            set_span_attributes(
                **{
                    'eduassist.policy.allow': decision.allow,
                    'eduassist.policy.reason': f'{decision.reason}|opa_unavailable:{exc.__class__.__name__}',
                    'eduassist.policy.source': decision.source,
                }
            )
            _record_policy_metrics(
                action=action,
                actor=actor,
                decision=decision,
                resource=resource,
                latency_ms=(monotonic() - started_at) * 1000,
            )
            return decision


def _record_policy_metrics(
    *,
    action: str,
    actor: ActorContext,
    decision: PolicyDecision,
    resource: dict[str, Any] | None,
    latency_ms: float,
) -> None:
    metric_attributes = {
        'action': action,
        'allow': decision.allow,
        'source': decision.source,
        'role': actor.role_code,
        'authenticated': actor.authenticated,
        'resource_type': (resource or {}).get('resource_type', 'unknown'),
    }
    record_counter(
        'eduassist_policy_decisions',
        attributes=metric_attributes,
        description='Policy decisions emitted by api-core.',
    )
    record_histogram(
        'eduassist_policy_decision_latency_ms',
        latency_ms,
        attributes={
            'action': action,
            'source': decision.source,
            'allow': decision.allow,
        },
        description='Latency of policy evaluation in milliseconds.',
    )
