from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from agents import RunContextWrapper, function_tool


@dataclass(frozen=True)
class SpecialistToolDeps:
    fetch_public_school_profile: Callable[..., Awaitable[dict[str, Any] | None]]
    fetch_public_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    http_get: Callable[..., Awaitable[dict[str, Any] | None]]
    school_name: Callable[[dict[str, Any] | None], str]
    orchestrator_retrieval_search: Callable[..., Awaitable[dict[str, Any] | None]]
    orchestrator_graph_rag_query: Callable[..., Awaitable[dict[str, Any] | None]]
    pricing_projection: Callable[..., dict[str, Any]]
    fetch_academic_summary_payload: Callable[..., Awaitable[dict[str, Any]]]
    fetch_financial_summary_payload: Callable[..., Awaitable[dict[str, Any]]]
    subject_code_from_hint: Callable[..., tuple[str | None, str | None]]
    academic_grade_requirement: Callable[..., dict[str, Any]]
    strip_none: Callable[[dict[str, Any]], dict[str, Any]]
    effective_conversation_id: Callable[[Any], str]
    detect_support_handoff_queue: Callable[[Any], str]
    build_support_handoff_summary: Callable[..., str]
    create_support_handoff_payload: Callable[..., Awaitable[dict[str, Any]]]
    http_post: Callable[..., Awaitable[dict[str, Any] | None]]


@dataclass(frozen=True)
class SpecialistTools:
    fetch_actor_identity: Any
    get_public_profile_bundle: Any
    fetch_academic_policy: Any
    search_public_documents: Any
    search_private_documents: Any
    run_graph_rag_query: Any
    project_public_pricing: Any
    fetch_academic_summary: Any
    fetch_upcoming_assessments: Any
    fetch_attendance_timeline: Any
    calculate_grade_requirement: Any
    fetch_financial_summary: Any
    fetch_workflow_status: Any
    create_support_handoff: Any
    create_visit_booking: Any
    update_visit_booking: Any
    create_institutional_request: Any
    update_institutional_request: Any


def build_specialist_tools(*, deps: SpecialistToolDeps) -> SpecialistTools:
    @function_tool
    async def fetch_actor_identity(context: RunContextWrapper[Any]) -> dict[str, Any]:
        """Fetch the authenticated actor and linked students for the current conversation."""
        actor = context.context.actor or {}
        return {
            "actor": actor,
            "linked_students": actor.get("linked_students", []) if isinstance(actor, dict) else [],
        }

    @function_tool
    async def get_public_profile_bundle(context: RunContextWrapper[Any]) -> dict[str, Any]:
        """Fetch the core public institutional profile, directories, timeline and calendar bundle."""
        ctx = context.context
        school_profile = ctx.school_profile or await deps.fetch_public_school_profile(ctx)
        org_directory = await deps.fetch_public_payload(ctx, "/v1/public/org-directory", "directory")
        service_directory = await deps.fetch_public_payload(ctx, "/v1/public/service-directory", "directory")
        timeline = await deps.fetch_public_payload(ctx, "/v1/public/timeline", "timeline")
        calendar_payload = await deps.http_get(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/calendar/public",
            token=ctx.settings.internal_api_token,
            params={"date_from": "2026-01-01", "date_to": "2026-12-31", "limit": 12},
        )
        return {
            "profile": school_profile,
            "org_directory": org_directory,
            "service_directory": service_directory,
            "timeline": timeline,
            "calendar_events": calendar_payload.get("events", []) if isinstance(calendar_payload, dict) else [],
        }

    @function_tool
    async def fetch_academic_policy(context: RunContextWrapper[Any]) -> dict[str, Any]:
        """Fetch the public academic policy bundle for attendance, passing threshold and projeto de vida."""
        ctx = context.context
        school_profile = ctx.school_profile or await deps.fetch_public_school_profile(ctx)
        if not isinstance(school_profile, dict):
            return {"error": "school_profile_unavailable"}
        policy = school_profile.get("academic_policy")
        if not isinstance(policy, dict):
            return {"error": "academic_policy_unavailable", "school_name": deps.school_name(school_profile)}
        return {
            "school_name": deps.school_name(school_profile),
            "academic_policy": policy,
        }

    @function_tool
    async def search_public_documents(
        context: RunContextWrapper[Any],
        query: str,
        category: str | None = None,
        top_k: int = 4,
    ) -> dict[str, Any]:
        """Run shared public hybrid retrieval with citations."""
        payload = await deps.orchestrator_retrieval_search(context.context, query=query, visibility="public", category=category, top_k=top_k)
        return payload or {"query": query, "total_hits": 0, "hits": []}

    @function_tool
    async def search_private_documents(
        context: RunContextWrapper[Any],
        query: str,
        audience: str | None = None,
        top_k: int = 4,
    ) -> dict[str, Any]:
        """Run authenticated/private retrieval when allowed; otherwise return a safe empty result."""
        ctx = context.context
        if not ctx.request.user.authenticated:
            return {"query": query, "total_hits": 0, "hits": [], "note": "not_authenticated"}
        scopes = {str(item).strip().lower() for item in ctx.request.user.scopes}
        normalized_audience = str(audience or "").strip().lower()
        role = str(getattr(ctx.request.user.role, "value", ctx.request.user.role) or "").strip().lower()
        can_read_private = (
            "documents:private:read" in scopes
            or "documents:restricted:read" in scopes
            or role in {"staff", "teacher"}
        )
        visibility = "restricted" if can_read_private and normalized_audience != "public" else "public"
        payload = await deps.orchestrator_retrieval_search(
            ctx,
            query=query,
            visibility=visibility,
            category=None,
            top_k=top_k,
        )
        return payload or {"query": query, "total_hits": 0, "hits": []}

    @function_tool
    async def run_graph_rag_query(context: RunContextWrapper[Any], query: str) -> dict[str, Any]:
        """Run GraphRAG through the shared orchestrator when available."""
        payload = await deps.orchestrator_graph_rag_query(context.context, query=query)
        return payload or {"query": query, "available": False}

    @function_tool
    async def project_public_pricing(
        context: RunContextWrapper[Any],
        quantity: int,
        segment_hint: str | None = None,
    ) -> dict[str, Any]:
        """Project public enrollment and monthly pricing using the shared public school profile."""
        ctx = context.context
        profile = ctx.school_profile or await deps.fetch_public_school_profile(ctx)
        return deps.pricing_projection(profile, quantity=quantity, segment_hint=segment_hint)

    @function_tool
    async def fetch_academic_summary(
        context: RunContextWrapper[Any],
        student_name_hint: str | None = None,
    ) -> dict[str, Any]:
        """Fetch the academic summary for an authorized linked student."""
        return await deps.fetch_academic_summary_payload(context.context, student_name_hint=student_name_hint)

    @function_tool
    async def fetch_upcoming_assessments(
        context: RunContextWrapper[Any],
        student_name_hint: str | None = None,
        subject_hint: str | None = None,
    ) -> dict[str, Any]:
        """Fetch upcoming assessments for an authorized linked student."""
        ctx = context.context
        academic_payload = await deps.fetch_academic_summary_payload(context.context, student_name_hint=student_name_hint)
        if not isinstance(academic_payload, dict) or not isinstance(academic_payload.get("summary"), dict):
            return academic_payload if isinstance(academic_payload, dict) else {"error": "student_not_found"}
        student = academic_payload["student"]
        summary = academic_payload["summary"]
        subject_code, subject_name = deps.subject_code_from_hint(summary, subject_hint)
        payload = await deps.http_get(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path=f"/v1/students/{student['student_id']}/upcoming-assessments",
            token=ctx.settings.internal_api_token,
            params=deps.strip_none({"telegram_chat_id": ctx.request.telegram_chat_id, "subject_code": subject_code}),
        )
        return {
            "student": student,
            "subject_name": subject_name or subject_hint,
            "summary": payload.get("summary") if isinstance(payload, dict) else None,
        }

    @function_tool
    async def fetch_attendance_timeline(
        context: RunContextWrapper[Any],
        student_name_hint: str | None = None,
        subject_hint: str | None = None,
    ) -> dict[str, Any]:
        """Fetch attendance timeline rows for an authorized linked student."""
        ctx = context.context
        academic_payload = await deps.fetch_academic_summary_payload(context.context, student_name_hint=student_name_hint)
        if not isinstance(academic_payload, dict) or not isinstance(academic_payload.get("summary"), dict):
            return academic_payload if isinstance(academic_payload, dict) else {"error": "student_not_found"}
        student = academic_payload["student"]
        summary = academic_payload["summary"]
        subject_code, subject_name = deps.subject_code_from_hint(summary, subject_hint)
        payload = await deps.http_get(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path=f"/v1/students/{student['student_id']}/attendance-timeline",
            token=ctx.settings.internal_api_token,
            params=deps.strip_none({"telegram_chat_id": ctx.request.telegram_chat_id, "subject_code": subject_code}),
        )
        return {
            "student": student,
            "subject_name": subject_name or subject_hint,
            "summary": payload.get("summary") if isinstance(payload, dict) else None,
        }

    @function_tool
    async def calculate_grade_requirement(
        context: RunContextWrapper[Any],
        student_name_hint: str | None = None,
        subject_hint: str | None = None,
    ) -> dict[str, Any]:
        """Calculate how many points are still needed to reach the passing threshold in a subject."""
        academic_payload = await deps.fetch_academic_summary_payload(context.context, student_name_hint=student_name_hint)
        if not isinstance(academic_payload, dict) or not isinstance(academic_payload.get("summary"), dict):
            return academic_payload if isinstance(academic_payload, dict) else {"error": "student_not_found"}
        summary = academic_payload["summary"]
        result = deps.academic_grade_requirement(summary, subject_hint=subject_hint)
        result["student"] = academic_payload["student"]
        return result

    @function_tool
    async def fetch_financial_summary(
        context: RunContextWrapper[Any],
        student_name_hint: str | None = None,
    ) -> dict[str, Any]:
        """Fetch the financial summary for an authorized linked student."""
        return await deps.fetch_financial_summary_payload(context.context, student_name_hint=student_name_hint)

    @function_tool
    async def fetch_workflow_status(
        context: RunContextWrapper[Any],
        protocol_code_hint: str | None = None,
        workflow_kind: str | None = None,
    ) -> dict[str, Any]:
        """Fetch the latest workflow/protocol status for the active conversation."""
        ctx = context.context
        return await deps.http_get(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/internal/workflows/status",
            token=ctx.settings.internal_api_token,
            params=deps.strip_none(
                {
                    "conversation_external_id": deps.effective_conversation_id(ctx.request),
                    "channel": ctx.request.channel.value,
                    "protocol_code": protocol_code_hint,
                    "workflow_kind": workflow_kind,
                }
            ),
        ) or {"found": False}

    @function_tool
    async def create_support_handoff(
        context: RunContextWrapper[Any],
        queue_name: str | None = None,
        summary: str | None = None,
    ) -> dict[str, Any]:
        """Open or reuse a real human-support handoff with protocol and queue."""
        ctx = context.context
        effective_queue = str(queue_name or "").strip() or deps.detect_support_handoff_queue(ctx)
        return await deps.create_support_handoff_payload(
            ctx,
            queue_name=effective_queue,
            summary=summary or deps.build_support_handoff_summary(ctx, queue_name=effective_queue),
        )

    @function_tool
    async def create_visit_booking(
        context: RunContextWrapper[Any],
        preferred_date: str | None = None,
        preferred_window: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Create a new school visit workflow entry."""
        ctx = context.context
        return await deps.http_post(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/internal/workflows/visit-bookings",
            token=ctx.settings.internal_api_token,
            payload=deps.strip_none(
                {
                    "conversation_external_id": deps.effective_conversation_id(ctx.request),
                    "channel": ctx.request.channel.value,
                    "telegram_chat_id": ctx.request.telegram_chat_id,
                    "preferred_date": preferred_date,
                    "preferred_window": preferred_window,
                    "notes": notes or ctx.request.message,
                }
            ),
        ) or {"error": "visit_booking_failed"}

    @function_tool
    async def update_visit_booking(
        context: RunContextWrapper[Any],
        action: str,
        preferred_date: str | None = None,
        preferred_window: str | None = None,
        protocol_code_hint: str | None = None,
    ) -> dict[str, Any]:
        """Reschedule or cancel an existing visit booking workflow."""
        ctx = context.context
        return await deps.http_post(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/internal/workflows/visit-bookings/actions",
            token=ctx.settings.internal_api_token,
            payload=deps.strip_none(
                {
                    "conversation_external_id": deps.effective_conversation_id(ctx.request),
                    "channel": ctx.request.channel.value,
                    "telegram_chat_id": ctx.request.telegram_chat_id,
                    "protocol_code": protocol_code_hint,
                    "action": action,
                    "preferred_date": preferred_date,
                    "preferred_window": preferred_window,
                    "notes": ctx.request.message,
                }
            ),
        ) or {"error": "visit_booking_update_failed"}

    @function_tool
    async def create_institutional_request(
        context: RunContextWrapper[Any],
        target_area: str | None = None,
        category: str | None = None,
        subject: str | None = None,
        details: str | None = None,
    ) -> dict[str, Any]:
        """Create a new institutional workflow request."""
        ctx = context.context
        return await deps.http_post(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/internal/workflows/institutional-requests",
            token=ctx.settings.internal_api_token,
            payload=deps.strip_none(
                {
                    "conversation_external_id": deps.effective_conversation_id(ctx.request),
                    "channel": ctx.request.channel.value,
                    "telegram_chat_id": ctx.request.telegram_chat_id,
                    "target_area": target_area,
                    "category": category,
                    "subject": subject,
                    "details": details or ctx.request.message,
                }
            ),
        ) or {"error": "institutional_request_failed"}

    @function_tool
    async def update_institutional_request(
        context: RunContextWrapper[Any],
        details: str,
        protocol_code_hint: str | None = None,
    ) -> dict[str, Any]:
        """Append new details to an existing institutional workflow request."""
        ctx = context.context
        return await deps.http_post(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/internal/workflows/institutional-requests/actions",
            token=ctx.settings.internal_api_token,
            payload=deps.strip_none(
                {
                    "conversation_external_id": deps.effective_conversation_id(ctx.request),
                    "channel": ctx.request.channel.value,
                    "telegram_chat_id": ctx.request.telegram_chat_id,
                    "protocol_code": protocol_code_hint,
                    "action": "append_details",
                    "details": details,
                }
            ),
        ) or {"error": "institutional_request_update_failed"}

    return SpecialistTools(
        fetch_actor_identity=fetch_actor_identity,
        get_public_profile_bundle=get_public_profile_bundle,
        fetch_academic_policy=fetch_academic_policy,
        search_public_documents=search_public_documents,
        search_private_documents=search_private_documents,
        run_graph_rag_query=run_graph_rag_query,
        project_public_pricing=project_public_pricing,
        fetch_academic_summary=fetch_academic_summary,
        fetch_upcoming_assessments=fetch_upcoming_assessments,
        fetch_attendance_timeline=fetch_attendance_timeline,
        calculate_grade_requirement=calculate_grade_requirement,
        fetch_financial_summary=fetch_financial_summary,
        fetch_workflow_status=fetch_workflow_status,
        create_support_handoff=create_support_handoff,
        create_visit_booking=create_visit_booking,
        update_visit_booking=update_visit_booking,
        create_institutional_request=create_institutional_request,
        update_institutional_request=update_institutional_request,
    )
