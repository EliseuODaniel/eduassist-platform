from __future__ import annotations

import copy
import secrets
import uuid
from datetime import date

from fastapi import FastAPI, Header, HTTPException, Query, Request
from pydantic import BaseModel
from eduassist_observability import (
    bridge_spiffe_identity_to_internal_token,
    configure_observability,
)

from api_core.config import get_settings
from api_core.contracts import (
    ActorContext,
    AuthPrincipal,
    AuthSessionResponse,
    CalendarEventsResponse,
    InternalWorkflowStatusResponse,
    InstitutionalRequestActionResponse,
    InstitutionalRequestCreateResponse,
    InternalConversationAppendRequest,
    InternalConversationAppendResponse,
    InternalConversationToolCallAppendRequest,
    InternalConversationToolCallAppendResponse,
    InternalConversationContextResponse,
    InternalInstitutionalRequestActionRequest,
    InternalInstitutionalRequestCreateRequest,
    InternalSupportHandoffCreateRequest,
    InternalVisitBookingActionRequest,
    InternalVisitBookingCreateRequest,
    OperationsOverviewResponse,
    PolicyCheckRequest,
    PolicyCheckResponse,
    PublicAssistantCapabilitiesResponse,
    PublicOrgDirectoryResponse,
    PublicSchoolProfileResponse,
    PublicServiceDirectoryResponse,
    PublicTimelineResponse,
    SupportConversationDetailResponse,
    SupportConversationListResponse,
    SupportHandoffCreateResponse,
    SupportHandoffDetailResponse,
    SupportHandoffFilters,
    SupportHandoffListResponse,
    SupportHandoffStatusUpdateRequest,
    SupportHandoffUpdateResponse,
    TelegramLinkChallengeResponse,
    TelegramLinkConsumeRequest,
    TelegramLinkConsumeResponse,
    VisitBookingActionResponse,
    VisitBookingCreateResponse,
)
from api_core.db.session import apply_rls_actor_context, apply_rls_service_context, get_engine, session_scope
from api_core.services.audit import (
    build_handoff_operations_overview,
    build_operations_metrics,
    get_foundation_counts,
    list_recent_access_decisions,
    list_recent_audit_events,
    record_audit_event,
    record_access_decision,
    register_support_operational_metrics,
    resolve_operations_scope,
)
from api_core.services.auth import decode_access_token, extract_bearer_token
from api_core.services.conversation_memory import (
    append_conversation_messages,
    append_conversation_tool_calls,
    get_conversation_context,
)
from api_core.services.domain import (
    get_actor_administrative_status,
    get_public_assistant_capabilities,
    get_public_org_directory,
    get_student_academic_summary,
    get_student_administrative_status,
    get_student_attendance_timeline,
    get_student_financial_summary,
    get_student_upcoming_assessments,
    get_teacher_schedule,
    get_public_school_profile,
    get_public_service_directory,
    get_public_timeline,
    list_public_calendar_events,
)
from api_core.services.identity import resolve_actor_context
from api_core.services.institutional_workflows import (
    create_institutional_request,
    create_visit_booking,
    get_workflow_status,
    update_institutional_request,
    update_visit_booking,
)
from api_core.services.policy import decide_policy
from api_core.services.support import (
    create_support_handoff,
    get_support_conversation_detail,
    get_support_handoff_detail,
    list_support_conversations,
    list_support_handoffs,
    resolve_support_scope,
    update_support_handoff_status,
)
from api_core.services.telegram_link import create_telegram_link_challenge, consume_telegram_link_challenge


class HealthResponse(BaseModel):
    status: str
    service: str
    ready: bool


PUBLIC_CALENDAR_DATE_FROM_QUERY = Query(default=None)
PUBLIC_CALENDAR_DATE_TO_QUERY = Query(default=None)
PUBLIC_CALENDAR_LIMIT_QUERY = Query(default=6, ge=1, le=20)


app = FastAPI(
    title='EduAssist API Core',
    version='0.3.0',
    summary='Core domain API for identity, policy, audit and school data services.',
)


@app.middleware('http')
async def _bridge_internal_workload_identity(request: Request, call_next):
    settings = get_settings()
    decision = bridge_spiffe_identity_to_internal_token(
        request.scope,
        expected_token=settings.internal_api_token,
        mode=settings.internal_workload_identity_mode,
        allowed_spiffe_ids=settings.internal_spiffe_allowed_ids,
    )
    if decision.authenticated and decision.mechanism == 'spiffe_id':
        request.state.internal_workload_identity = {
            'mechanism': decision.mechanism,
            'spiffe_id': decision.spiffe_id,
        }
    return await call_next(request)

configure_observability(
    service_name='api-core',
    service_version=app.version,
    environment=get_settings().app_env,
    app=app,
    sqlalchemy_engine=get_engine(),
    excluded_urls='/healthz,/meta',
)
register_support_operational_metrics()


def _resolve_request_context(
    *,
    authorization: str | None,
    telegram_chat_id: int | None,
    user_external_code: str | None,
    x_internal_api_token: str | None = None,
) -> tuple[ActorContext, AuthPrincipal | None, str]:
    settings = get_settings()
    bearer_token = extract_bearer_token(authorization)

    if telegram_chat_id is not None:
        _require_internal_api_token(x_internal_api_token)

    if user_external_code is not None:
        _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        if bearer_token:
            principal = decode_access_token(bearer_token)
            actor = resolve_actor_context(
                session,
                federated_provider=principal.provider,
                federated_subject=principal.subject,
            )
            if actor is None:
                raise HTTPException(status_code=404, detail='actor_not_found_for_token')
            return actor, principal, 'bearer_token'

        if user_external_code and not settings.allow_test_identity_overrides:
            raise HTTPException(status_code=403, detail='test_identity_overrides_disabled')

        actor = resolve_actor_context(
            session,
            telegram_chat_id=telegram_chat_id,
            user_external_code=user_external_code,
        )

    if actor is None:
        raise HTTPException(status_code=404, detail='actor_not_found')

    auth_mode = 'telegram_chat' if telegram_chat_id is not None else 'test_override_external_code'
    return actor, None, auth_mode


def _require_internal_api_token(x_internal_api_token: str | None) -> None:
    settings = get_settings()
    if not x_internal_api_token or not secrets.compare_digest(x_internal_api_token, settings.internal_api_token):
        raise HTTPException(status_code=401, detail='invalid_internal_api_token')


def _sanitize_actor_for_external_response(actor: ActorContext, *, auth_mode: str) -> ActorContext:
    sanitized = copy.deepcopy(actor)
    if auth_mode == 'telegram_chat':
        sanitized.telegram_chat_id = None
    return sanitized


async def _student_academic_summary_payload(
    *,
    actor: ActorContext,
    auth_mode: str,
    student_id: uuid.UUID,
) -> dict[str, object]:
    decision = None
    if actor.role_code != 'teacher':
        decision = await decide_policy(
            action='student.academic.read',
            actor=actor,
            resource={
                'student_id': str(student_id),
                'class_id': None,
                'resource_type': 'student_academic_summary',
            },
        )

    with session_scope() as session:
        if decision is not None:
            record_access_decision(
                session,
                actor_user_id=actor.user_id,
                resource_type='student_academic_summary',
                action='student.academic.read',
                decision='allow' if decision.allow else 'deny',
                reason=decision.reason,
            )
            if not decision.allow:
                raise HTTPException(status_code=403, detail=decision.reason)

        apply_rls_actor_context(session, actor)
        summary = get_student_academic_summary(session, student_id)
        if summary is None:
            raise HTTPException(status_code=404, detail='student_not_found')

        if actor.role_code == 'teacher':
            decision = await decide_policy(
                action='student.academic.read',
                actor=actor,
                resource={
                    'student_id': str(summary.student_id),
                    'class_id': str(summary.class_id) if summary.class_id else None,
                    'resource_type': 'student_academic_summary',
                },
            )
            record_access_decision(
                session,
                actor_user_id=actor.user_id,
                resource_type='student_academic_summary',
                action='student.academic.read',
                decision='allow' if decision.allow else 'deny',
                reason=decision.reason,
            )
        if decision is None:
            raise HTTPException(status_code=500, detail='policy_decision_missing')
        response = {
            'service': 'api-core',
            'auth_mode': auth_mode,
            'actor': _sanitize_actor_for_external_response(actor, auth_mode=auth_mode).model_dump(mode='json'),
            'decision': decision.model_dump(mode='json'),
            'summary': summary.model_dump(mode='json'),
        }

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    return response


async def _student_attendance_timeline_payload(
    *,
    actor: ActorContext,
    auth_mode: str,
    student_id: uuid.UUID,
    subject_code: str | None = None,
) -> dict[str, object]:
    decision = None
    if actor.role_code != 'teacher':
        decision = await decide_policy(
            action='student.academic.read',
            actor=actor,
            resource={
                'student_id': str(student_id),
                'class_id': None,
                'resource_type': 'student_attendance_timeline',
            },
        )

    with session_scope() as session:
        if decision is not None:
            record_access_decision(
                session,
                actor_user_id=actor.user_id,
                resource_type='student_attendance_timeline',
                action='student.academic.read',
                decision='allow' if decision.allow else 'deny',
                reason=decision.reason,
            )
            if not decision.allow:
                raise HTTPException(status_code=403, detail=decision.reason)

        apply_rls_actor_context(session, actor)
        summary = get_student_attendance_timeline(session, student_id, subject_code=subject_code)
        if summary is None:
            raise HTTPException(status_code=404, detail='student_not_found')

        if actor.role_code == 'teacher':
            decision = await decide_policy(
                action='student.academic.read',
                actor=actor,
                resource={
                    'student_id': str(summary.student_id),
                    'class_id': str(summary.class_id) if summary.class_id else None,
                    'resource_type': 'student_attendance_timeline',
                },
            )
            record_access_decision(
                session,
                actor_user_id=actor.user_id,
                resource_type='student_attendance_timeline',
                action='student.academic.read',
                decision='allow' if decision.allow else 'deny',
                reason=decision.reason,
            )
        if decision is None:
            raise HTTPException(status_code=500, detail='policy_decision_missing')

        response = {
            'service': 'api-core',
            'auth_mode': auth_mode,
            'actor': _sanitize_actor_for_external_response(actor, auth_mode=auth_mode).model_dump(mode='json'),
            'decision': decision.model_dump(mode='json'),
            'summary': summary.model_dump(mode='json'),
        }

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    return response


async def _student_upcoming_assessments_payload(
    *,
    actor: ActorContext,
    auth_mode: str,
    student_id: uuid.UUID,
    subject_code: str | None = None,
) -> dict[str, object]:
    decision = None
    if actor.role_code != 'teacher':
        decision = await decide_policy(
            action='student.academic.read',
            actor=actor,
            resource={
                'student_id': str(student_id),
                'class_id': None,
                'resource_type': 'student_upcoming_assessments',
            },
        )

    with session_scope() as session:
        if decision is not None:
            record_access_decision(
                session,
                actor_user_id=actor.user_id,
                resource_type='student_upcoming_assessments',
                action='student.academic.read',
                decision='allow' if decision.allow else 'deny',
                reason=decision.reason,
            )
            if not decision.allow:
                raise HTTPException(status_code=403, detail=decision.reason)

        apply_rls_actor_context(session, actor)
        summary = get_student_upcoming_assessments(session, student_id, subject_code=subject_code)
        if summary is None:
            raise HTTPException(status_code=404, detail='student_not_found')

        if actor.role_code == 'teacher':
            decision = await decide_policy(
                action='student.academic.read',
                actor=actor,
                resource={
                    'student_id': str(summary.student_id),
                    'class_id': str(summary.class_id) if summary.class_id else None,
                    'resource_type': 'student_upcoming_assessments',
                },
            )
            record_access_decision(
                session,
                actor_user_id=actor.user_id,
                resource_type='student_upcoming_assessments',
                action='student.academic.read',
                decision='allow' if decision.allow else 'deny',
                reason=decision.reason,
            )
        if decision is None:
            raise HTTPException(status_code=500, detail='policy_decision_missing')

        response = {
            'service': 'api-core',
            'auth_mode': auth_mode,
            'actor': _sanitize_actor_for_external_response(actor, auth_mode=auth_mode).model_dump(mode='json'),
            'decision': decision.model_dump(mode='json'),
            'summary': summary.model_dump(mode='json'),
        }

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    return response


async def _student_financial_summary_payload(
    *,
    actor: ActorContext,
    auth_mode: str,
    student_id: uuid.UUID,
) -> dict[str, object]:
    decision = await decide_policy(
        action='student.finance.read',
        actor=actor,
        resource={
            'student_id': str(student_id),
            'resource_type': 'student_financial_summary',
        },
    )

    with session_scope() as session:
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type='student_financial_summary',
            action='student.finance.read',
            decision='allow' if decision.allow else 'deny',
            reason=decision.reason,
        )
        if not decision.allow:
            raise HTTPException(status_code=403, detail=decision.reason)

        apply_rls_actor_context(session, actor)
        summary = get_student_financial_summary(session, student_id)
        if summary is None:
            raise HTTPException(status_code=404, detail='student_not_found')
        response = {
            'service': 'api-core',
            'auth_mode': auth_mode,
            'actor': _sanitize_actor_for_external_response(actor, auth_mode=auth_mode).model_dump(mode='json'),
            'decision': decision.model_dump(mode='json'),
            'summary': summary.model_dump(mode='json'),
        }

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    return response


async def _student_administrative_status_payload(
    *,
    actor: ActorContext,
    auth_mode: str,
    student_id: uuid.UUID,
) -> dict[str, object]:
    decision = await decide_policy(
        action='student.admin.read',
        actor=actor,
        resource={
            'student_id': str(student_id),
            'resource_type': 'student_administrative_status',
        },
    )

    with session_scope() as session:
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type='student_administrative_status',
            action='student.admin.read',
            decision='allow' if decision.allow else 'deny',
            reason=decision.reason,
        )
        if not decision.allow:
            raise HTTPException(status_code=403, detail=decision.reason)

        apply_rls_actor_context(session, actor)
        summary = get_student_administrative_status(session, student_id)
        if summary is None:
            raise HTTPException(status_code=404, detail='student_not_found')
        response = {
            'service': 'api-core',
            'auth_mode': auth_mode,
            'actor': _sanitize_actor_for_external_response(actor, auth_mode=auth_mode).model_dump(mode='json'),
            'decision': decision.model_dump(mode='json'),
            'summary': summary.model_dump(mode='json'),
        }

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    return response


async def _teacher_schedule_payload(
    *,
    actor: ActorContext,
    auth_mode: str,
) -> dict[str, object]:
    with session_scope() as session:
        apply_rls_actor_context(session, actor)
        summary = get_teacher_schedule(session, actor.user_id)
        if summary is None:
            raise HTTPException(status_code=404, detail='teacher_not_found')

        decision = await decide_policy(
            action='teacher.schedule.read',
            actor=actor,
            resource={
                'teacher_id': str(summary.teacher_id),
                'resource_type': 'teacher_schedule',
            },
        )
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type='teacher_schedule',
            action='teacher.schedule.read',
            decision='allow' if decision.allow else 'deny',
            reason=decision.reason,
        )
        response = {
            'service': 'api-core',
            'auth_mode': auth_mode,
            'actor': _sanitize_actor_for_external_response(actor, auth_mode=auth_mode).model_dump(mode='json'),
            'decision': decision.model_dump(mode='json'),
            'summary': summary.model_dump(mode='json'),
        }

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    return response


async def _administrative_status_payload(
    *,
    actor: ActorContext,
    auth_mode: str,
) -> dict[str, object]:
    decision = await decide_policy(
        action='actor.administrative.read',
        actor=actor,
        resource={
            'user_id': str(actor.user_id),
            'resource_type': 'actor_administrative_status',
        },
    )

    with session_scope() as session:
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type='actor_administrative_status',
            action='actor.administrative.read',
            decision='allow' if decision.allow else 'deny',
            reason=decision.reason,
        )
        if not decision.allow:
            raise HTTPException(status_code=403, detail=decision.reason)

        apply_rls_actor_context(session, actor)
        summary = get_actor_administrative_status(session, actor)
        response = {
            'service': 'api-core',
            'auth_mode': auth_mode,
            'actor': _sanitize_actor_for_external_response(actor, auth_mode=auth_mode).model_dump(mode='json'),
            'decision': decision.model_dump(mode='json'),
            'summary': summary.model_dump(mode='json'),
        }

    return response


@app.get('/healthz', response_model=HealthResponse)
async def healthz() -> HealthResponse:
    return HealthResponse(
        status='ok',
        service='api-core',
        ready=True,
    )


@app.get('/meta')
async def meta(
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, str | bool]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    return {
        'service': 'api-core',
        'environment': settings.app_env,
        'logLevel': settings.log_level,
        'authProvider': 'keycloak',
        'policyProvider': 'opa',
        'allowTestIdentityOverrides': settings.allow_test_identity_overrides,
    }


@app.get('/v1/status')
async def status() -> dict[str, object]:
    return {
        'service': 'api-core',
        'ready': True,
        'capabilities': [
            'authz-gateway',
            'identity-resolution',
            'policy-decision',
            'audit-trail',
            'schema-foundation',
            'bearer-token-auth',
            'telegram-link-challenge',
        ],
    }


@app.get('/v1/foundation/summary')
async def foundation_summary() -> dict[str, object]:
    counts: dict[str, int] = {}

    try:
        with session_scope() as session:
            counts = get_foundation_counts(session)
        database = 'reachable'
    except Exception as exc:  # pragma: no cover - bootstrap resilience path
        database = f'unavailable: {exc.__class__.__name__}'

    return {
        'service': 'api-core',
        'database': database,
        'counts': counts,
    }


@app.get('/v1/public/school-profile', response_model=PublicSchoolProfileResponse)
async def public_school_profile() -> PublicSchoolProfileResponse:
    with session_scope() as session:
        profile = get_public_school_profile(session)
    if profile is None:
        raise HTTPException(status_code=404, detail='public_school_profile_not_found')
    return PublicSchoolProfileResponse(profile=profile)


@app.get('/v1/public/assistant-capabilities', response_model=PublicAssistantCapabilitiesResponse)
async def public_assistant_capabilities() -> PublicAssistantCapabilitiesResponse:
    with session_scope() as session:
        capabilities = get_public_assistant_capabilities(session)
    if capabilities is None:
        raise HTTPException(status_code=404, detail='public_assistant_capabilities_not_found')
    return PublicAssistantCapabilitiesResponse(capabilities=capabilities)


@app.get('/v1/public/org-directory', response_model=PublicOrgDirectoryResponse)
async def public_org_directory() -> PublicOrgDirectoryResponse:
    with session_scope() as session:
        directory = get_public_org_directory(session)
    if directory is None:
        raise HTTPException(status_code=404, detail='public_org_directory_not_found')
    return PublicOrgDirectoryResponse(directory=directory)


@app.get('/v1/public/service-directory', response_model=PublicServiceDirectoryResponse)
async def public_service_directory() -> PublicServiceDirectoryResponse:
    with session_scope() as session:
        directory = get_public_service_directory(session)
    if directory is None:
        raise HTTPException(status_code=404, detail='public_service_directory_not_found')
    return PublicServiceDirectoryResponse(directory=directory)


@app.get('/v1/public/timeline', response_model=PublicTimelineResponse)
async def public_timeline() -> PublicTimelineResponse:
    with session_scope() as session:
        timeline = get_public_timeline(session)
    if timeline is None:
        raise HTTPException(status_code=404, detail='public_timeline_not_found')
    return PublicTimelineResponse(timeline=timeline)


@app.get('/v1/operations/overview', response_model=OperationsOverviewResponse)
async def operations_overview(
    authorization: str | None = Header(default=None, alias='Authorization'),
) -> OperationsOverviewResponse:
    if extract_bearer_token(authorization) is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    actor, principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=None,
        user_external_code=None,
    )
    if principal is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    scope = resolve_operations_scope(actor)
    decision = await decide_policy(
        action='operations.overview.read',
        actor=actor,
        resource={
            'resource_type': 'operations_overview',
            'scope': scope,
        },
    )

    overview: OperationsOverviewResponse | None = None
    with session_scope() as session:
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type='operations_overview',
            action='operations.overview.read',
            decision='allow' if decision.allow else 'deny',
            reason=decision.reason,
        )
        if decision.allow:
            apply_rls_actor_context(session, actor)
            actor_user_id = None if scope == 'global' else actor.user_id
            metrics = build_operations_metrics(session, actor=actor, scope=scope)
            handoff_overview = build_handoff_operations_overview(session, actor=actor, scope=scope)
            if handoff_overview is not None:
                metrics.update(
                    {
                        'open_handoffs': handoff_overview.open_total,
                        'queued_handoffs': handoff_overview.queued_total,
                        'in_progress_handoffs': handoff_overview.in_progress_total,
                        'handoff_sla_attention': handoff_overview.attention_total,
                        'handoff_sla_breached': handoff_overview.breached_total,
                        'handoffs_without_assignee': handoff_overview.unassigned_total,
                        'critical_handoffs': handoff_overview.critical_total,
                    }
                )
            overview = OperationsOverviewResponse(
                actor=_sanitize_actor_for_external_response(actor, auth_mode=auth_mode),
                scope=scope,
                metrics=metrics,
                foundation_counts=get_foundation_counts(session) if scope == 'global' else None,
                audit_events=list_recent_audit_events(session, actor_user_id=actor_user_id),
                access_decisions=list_recent_access_decisions(session, actor_user_id=actor_user_id),
                handoff_overview=handoff_overview,
            )

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    if overview is None:
        raise HTTPException(status_code=500, detail='operations_overview_unavailable')
    return overview


@app.get('/v1/support/handoffs', response_model=SupportHandoffListResponse)
async def support_handoffs(
    authorization: str | None = Header(default=None, alias='Authorization'),
    status: str | None = Query(default=None),
    queue_name: str | None = Query(default=None),
    assignment: str | None = Query(default=None),
    sla_state: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=25),
) -> SupportHandoffListResponse:
    if extract_bearer_token(authorization) is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    actor, principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=None,
        user_external_code=None,
    )
    if principal is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    scope = resolve_support_scope(actor)
    decision = await decide_policy(
        action='support.handoffs.read',
        actor=actor,
        resource={
            'resource_type': 'support_handoff_list',
            'scope': scope,
        },
    )

    filters = SupportHandoffFilters(
        status=status,
        queue_name=queue_name,
        assignment=assignment,
        sla_state=sla_state,
        search=search,
        page=page,
        limit=limit,
    )

    response_payload: SupportHandoffListResponse | None = None
    with session_scope() as session:
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type='support_handoff_list',
            action='support.handoffs.read',
            decision='allow' if decision.allow else 'deny',
            reason=decision.reason,
        )

        if decision.allow:
            apply_rls_actor_context(session, actor)
            counts, items, filters, pagination = list_support_handoffs(
                session,
                actor=actor,
                scope=scope,
                filters=filters,
            )
            response_payload = SupportHandoffListResponse(
                actor=_sanitize_actor_for_external_response(actor, auth_mode=auth_mode),
                scope=scope,
                counts=counts,
                filters=filters,
                pagination=pagination,
                items=items,
            )

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    if response_payload is None:
        raise HTTPException(status_code=500, detail='support_handoffs_unavailable')
    return response_payload


@app.get('/v1/support/handoffs/{handoff_id}', response_model=SupportHandoffDetailResponse)
async def support_handoff_detail(
    handoff_id: uuid.UUID,
    authorization: str | None = Header(default=None, alias='Authorization'),
) -> SupportHandoffDetailResponse:
    if extract_bearer_token(authorization) is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    actor, principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=None,
        user_external_code=None,
    )
    if principal is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    scope = resolve_support_scope(actor)
    decision = await decide_policy(
        action='support.handoffs.read',
        actor=actor,
        resource={
            'resource_type': 'support_handoff',
            'scope': scope,
            'handoff_id': str(handoff_id),
        },
    )

    response_payload: SupportHandoffDetailResponse | None = None
    with session_scope() as session:
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type='support_handoff',
            action='support.handoffs.read',
            decision='allow' if decision.allow else 'deny',
            reason=decision.reason,
        )

        if decision.allow:
            apply_rls_actor_context(session, actor)
            detail = get_support_handoff_detail(
                session,
                actor=actor,
                scope=scope,
                handoff_id=handoff_id,
            )
            if detail is None:
                raise HTTPException(status_code=404, detail='support_handoff_not_found')

            item, conversation_status, messages = detail
            record_audit_event(
                session,
                actor_user_id=actor.user_id,
                event_type='support_handoff.viewed',
                resource_type='support_handoff',
                resource_id=str(handoff_id),
                metadata={
                    'scope': scope,
                    'queue_name': item.queue_name,
                    'status': item.status,
                },
            )
            response_payload = SupportHandoffDetailResponse(
                actor=_sanitize_actor_for_external_response(actor, auth_mode=auth_mode),
                scope=scope,
                item=item,
                conversation_status=conversation_status,
                messages=messages,
            )

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    if response_payload is None:
        raise HTTPException(status_code=500, detail='support_handoff_detail_unavailable')
    return response_payload


@app.get('/v1/support/conversations', response_model=SupportConversationListResponse)
async def support_conversations(
    authorization: str | None = Header(default=None, alias='Authorization'),
    limit: int = Query(default=12, ge=1, le=20),
) -> SupportConversationListResponse:
    if extract_bearer_token(authorization) is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    actor, principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=None,
        user_external_code=None,
    )
    if principal is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    scope = resolve_support_scope(actor)
    decision = await decide_policy(
        action='support.handoffs.read',
        actor=actor,
        resource={
            'resource_type': 'support_conversation_list',
            'scope': scope,
            'channel': 'telegram',
        },
    )

    response_payload: SupportConversationListResponse | None = None
    with session_scope() as session:
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type='support_conversation_list',
            action='support.handoffs.read',
            decision='allow' if decision.allow else 'deny',
            reason=decision.reason,
        )

        if decision.allow:
            apply_rls_actor_context(session, actor)
            items = list_support_conversations(
                session,
                actor=actor,
                scope=scope,
                limit=limit,
            )
            response_payload = SupportConversationListResponse(
                actor=_sanitize_actor_for_external_response(actor, auth_mode=auth_mode),
                scope=scope,
                items=items,
            )

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    if response_payload is None:
        raise HTTPException(status_code=500, detail='support_conversation_list_unavailable')
    return response_payload


@app.get('/v1/support/conversations/{conversation_id}', response_model=SupportConversationDetailResponse)
async def support_conversation_detail(
    conversation_id: uuid.UUID,
    authorization: str | None = Header(default=None, alias='Authorization'),
) -> SupportConversationDetailResponse:
    if extract_bearer_token(authorization) is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    actor, principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=None,
        user_external_code=None,
    )
    if principal is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    scope = resolve_support_scope(actor)
    decision = await decide_policy(
        action='support.handoffs.read',
        actor=actor,
        resource={
            'resource_type': 'support_conversation',
            'scope': scope,
            'conversation_id': str(conversation_id),
        },
    )

    response_payload: SupportConversationDetailResponse | None = None
    with session_scope() as session:
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type='support_conversation',
            action='support.handoffs.read',
            decision='allow' if decision.allow else 'deny',
            reason=decision.reason,
        )

        if decision.allow:
            apply_rls_actor_context(session, actor)
            detail = get_support_conversation_detail(
                session,
                actor=actor,
                scope=scope,
                conversation_id=conversation_id,
            )
            if detail is None:
                raise HTTPException(status_code=404, detail='support_conversation_not_found')

            item, messages = detail
            record_audit_event(
                session,
                actor_user_id=actor.user_id,
                event_type='support_conversation.viewed',
                resource_type='support_conversation',
                resource_id=str(conversation_id),
                metadata={
                    'scope': scope,
                    'channel': item.channel,
                    'linked_ticket_code': item.linked_ticket_code,
                },
            )
            response_payload = SupportConversationDetailResponse(
                actor=_sanitize_actor_for_external_response(actor, auth_mode=auth_mode),
                scope=scope,
                item=item,
                messages=messages,
            )

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    if response_payload is None:
        raise HTTPException(status_code=500, detail='support_conversation_detail_unavailable')
    return response_payload


@app.patch('/v1/support/handoffs/{handoff_id}', response_model=SupportHandoffUpdateResponse)
async def support_handoff_update(
    handoff_id: uuid.UUID,
    payload: SupportHandoffStatusUpdateRequest,
    authorization: str | None = Header(default=None, alias='Authorization'),
) -> SupportHandoffUpdateResponse:
    if extract_bearer_token(authorization) is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    actor, principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=None,
        user_external_code=None,
    )
    if principal is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    decision = await decide_policy(
        action='support.handoffs.manage',
        actor=actor,
        resource={
            'resource_type': 'support_handoff',
            'handoff_id': str(handoff_id),
            'target_status': payload.status,
            'assigned_user_id': str(payload.assigned_user_id) if payload.assigned_user_id else None,
            'clear_assignment': payload.clear_assignment,
        },
    )

    updated_item = None
    with session_scope() as session:
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type='support_handoff',
            action='support.handoffs.manage',
            decision='allow' if decision.allow else 'deny',
            reason=decision.reason,
        )

        if decision.allow:
            apply_rls_actor_context(session, actor)
            try:
                updated_item = update_support_handoff_status(
                    session,
                    handoff_id=handoff_id,
                    actor_user_id=actor.user_id,
                    status=payload.status,
                    operator_note=payload.operator_note,
                    assigned_user_id=payload.assigned_user_id,
                    clear_assignment=payload.clear_assignment,
                )
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            if updated_item is None:
                raise HTTPException(status_code=404, detail='support_handoff_not_found')

            record_audit_event(
                session,
                actor_user_id=actor.user_id,
                event_type='support_handoff.status_updated',
                resource_type='support_handoff',
                resource_id=str(handoff_id),
                metadata={
                    'status': payload.status or updated_item.status,
                    'queue_name': updated_item.queue_name,
                    'operator_note_attached': bool(payload.operator_note and payload.operator_note.strip()),
                    'priority_code': updated_item.priority_code,
                    'assigned_user_id': str(updated_item.assigned_user_id)
                    if updated_item.assigned_user_id
                    else None,
                    'clear_assignment': payload.clear_assignment,
                },
            )

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    if updated_item is None:
        raise HTTPException(status_code=500, detail='support_handoff_update_unavailable')

    return SupportHandoffUpdateResponse(
        actor=_sanitize_actor_for_external_response(actor, auth_mode=auth_mode),
        item=updated_item,
    )


@app.post('/v1/internal/support/handoffs', response_model=SupportHandoffCreateResponse)
async def internal_support_handoff_create(
    payload: InternalSupportHandoffCreateRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> SupportHandoffCreateResponse:
    _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        apply_rls_service_context(session, service_name='internal-support-api')
        actor = None
        if payload.telegram_chat_id is not None:
            actor = resolve_actor_context(session, telegram_chat_id=payload.telegram_chat_id)
            apply_rls_service_context(session, service_name='internal-support-api')

        response_payload = create_support_handoff(
            session,
            actor_user_id=actor.user_id if actor else None,
            channel=payload.channel,
            conversation_external_id=payload.conversation_external_id,
            queue_name=payload.queue_name.strip().lower(),
            summary=payload.summary.strip(),
            user_message=payload.user_message.strip() if payload.user_message else None,
        )

        record_audit_event(
            session,
            actor_user_id=actor.user_id if actor else None,
            event_type='support_handoff.created' if response_payload.created else 'support_handoff.reused',
            resource_type='support_handoff',
            resource_id=str(response_payload.item.handoff_id),
            metadata={
                'queue_name': response_payload.item.queue_name,
                'priority_code': response_payload.item.priority_code,
                'channel': response_payload.item.channel,
                'conversation_external_id': response_payload.item.external_thread_id,
                'deduplicated': response_payload.deduplicated,
            },
        )

        return response_payload


@app.post('/v1/internal/workflows/visit-bookings', response_model=VisitBookingCreateResponse)
async def internal_visit_booking_create(
    payload: InternalVisitBookingCreateRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> VisitBookingCreateResponse:
    _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        apply_rls_service_context(session, service_name='internal-workflows-api')
        actor = None
        if payload.telegram_chat_id is not None:
            actor = resolve_actor_context(session, telegram_chat_id=payload.telegram_chat_id)
            apply_rls_service_context(session, service_name='internal-workflows-api')

        response_payload = create_visit_booking(
            session,
            actor_user_id=actor.user_id if actor else None,
            channel=payload.channel,
            conversation_external_id=payload.conversation_external_id,
            audience_name=payload.audience_name,
            audience_contact=payload.audience_contact,
            interested_segment=payload.interested_segment,
            preferred_date=payload.preferred_date,
            preferred_window=payload.preferred_window,
            attendee_count=payload.attendee_count,
            notes=payload.notes.strip(),
        )
        record_audit_event(
            session,
            actor_user_id=actor.user_id if actor else None,
            event_type='visit_booking.created' if response_payload.created else 'visit_booking.updated',
            resource_type='visit_booking',
            resource_id=str(response_payload.item.booking_id),
            metadata={
                'queue_name': response_payload.item.queue_name,
                'preferred_date': response_payload.item.preferred_date.isoformat()
                if response_payload.item.preferred_date
                else None,
                'preferred_window': response_payload.item.preferred_window,
                'interested_segment': response_payload.item.interested_segment,
                'linked_ticket_code': response_payload.item.linked_ticket_code,
            },
        )
        return response_payload


@app.post('/v1/internal/workflows/visit-bookings/actions', response_model=VisitBookingActionResponse)
async def internal_visit_booking_action(
    payload: InternalVisitBookingActionRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> VisitBookingActionResponse:
    _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        apply_rls_service_context(session, service_name='internal-workflows-api')
        actor = None
        if payload.telegram_chat_id is not None:
            actor = resolve_actor_context(session, telegram_chat_id=payload.telegram_chat_id)
            apply_rls_service_context(session, service_name='internal-workflows-api')

        response_payload = update_visit_booking(
            session,
            channel=payload.channel,
            conversation_external_id=payload.conversation_external_id,
            protocol_code=payload.protocol_code.strip() if payload.protocol_code else None,
            action=payload.action,
            preferred_date=payload.preferred_date,
            preferred_window=payload.preferred_window.strip() if payload.preferred_window else None,
            notes=payload.notes.strip() if payload.notes else None,
        )
        record_audit_event(
            session,
            actor_user_id=actor.user_id if actor else None,
            event_type=f'visit_booking.{response_payload.action}',
            resource_type='visit_booking',
            resource_id=str(response_payload.item.booking_id),
            metadata={
                'protocol_code': response_payload.item.protocol_code,
                'queue_name': response_payload.item.queue_name,
                'preferred_date': response_payload.item.preferred_date.isoformat()
                if response_payload.item.preferred_date
                else None,
                'preferred_window': response_payload.item.preferred_window,
                'linked_ticket_code': response_payload.item.linked_ticket_code,
            },
        )
        return response_payload


@app.post('/v1/internal/workflows/institutional-requests', response_model=InstitutionalRequestCreateResponse)
async def internal_institutional_request_create(
    payload: InternalInstitutionalRequestCreateRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> InstitutionalRequestCreateResponse:
    _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        apply_rls_service_context(session, service_name='internal-workflows-api')
        actor = None
        if payload.telegram_chat_id is not None:
            actor = resolve_actor_context(session, telegram_chat_id=payload.telegram_chat_id)
            apply_rls_service_context(session, service_name='internal-workflows-api')

        response_payload = create_institutional_request(
            session,
            actor_user_id=actor.user_id if actor else None,
            channel=payload.channel,
            conversation_external_id=payload.conversation_external_id,
            target_area=payload.target_area.strip(),
            category=payload.category.strip(),
            subject=payload.subject.strip(),
            details=payload.details.strip(),
            requester_contact=payload.requester_contact.strip() if payload.requester_contact else None,
        )
        record_audit_event(
            session,
            actor_user_id=actor.user_id if actor else None,
            event_type='institutional_request.created' if response_payload.created else 'institutional_request.updated',
            resource_type='institutional_request',
            resource_id=str(response_payload.item.request_id),
            metadata={
                'target_area': response_payload.item.target_area,
                'category': response_payload.item.category,
                'queue_name': response_payload.item.queue_name,
                'linked_ticket_code': response_payload.item.linked_ticket_code,
            },
        )
        return response_payload


@app.post('/v1/internal/workflows/institutional-requests/actions', response_model=InstitutionalRequestActionResponse)
async def internal_institutional_request_action(
    payload: InternalInstitutionalRequestActionRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> InstitutionalRequestActionResponse:
    _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        apply_rls_service_context(session, service_name='internal-workflows-api')
        actor = None
        if payload.telegram_chat_id is not None:
            actor = resolve_actor_context(session, telegram_chat_id=payload.telegram_chat_id)
            apply_rls_service_context(session, service_name='internal-workflows-api')

        response_payload = update_institutional_request(
            session,
            channel=payload.channel,
            conversation_external_id=payload.conversation_external_id,
            protocol_code=payload.protocol_code.strip() if payload.protocol_code else None,
            action=payload.action,
            details=payload.details.strip() if payload.details else None,
        )
        record_audit_event(
            session,
            actor_user_id=actor.user_id if actor else None,
            event_type=f'institutional_request.{response_payload.action}',
            resource_type='institutional_request',
            resource_id=str(response_payload.item.request_id),
            metadata={
                'target_area': response_payload.item.target_area,
                'queue_name': response_payload.item.queue_name,
                'linked_ticket_code': response_payload.item.linked_ticket_code,
                'protocol_code': response_payload.item.protocol_code,
            },
        )
        return response_payload


@app.get('/v1/internal/workflows/status', response_model=InternalWorkflowStatusResponse)
async def internal_workflow_status(
    conversation_external_id: str = Query(min_length=3, max_length=120),
    channel: str = Query(default='telegram', min_length=2, max_length=30),
    protocol_code: str | None = Query(default=None, min_length=3, max_length=40),
    workflow_kind: str | None = Query(default=None, min_length=3, max_length=40),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> InternalWorkflowStatusResponse:
    _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        apply_rls_service_context(session, service_name='internal-workflows-api')
        return get_workflow_status(
            session,
            channel=channel,
            conversation_external_id=conversation_external_id,
            protocol_code=protocol_code,
            workflow_kind=workflow_kind,
        )


@app.get('/v1/internal/conversations/context', response_model=InternalConversationContextResponse)
async def internal_conversation_context(
    conversation_external_id: str = Query(min_length=3, max_length=120),
    channel: str = Query(default='telegram', min_length=2, max_length=30),
    limit: int = Query(default=6, ge=1, le=20),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> InternalConversationContextResponse:
    _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        apply_rls_service_context(session, service_name='internal-support-api')
        return get_conversation_context(
            session,
            channel=channel,
            conversation_external_id=conversation_external_id,
            limit=limit,
        )


@app.post('/v1/internal/conversations/messages', response_model=InternalConversationAppendResponse)
async def internal_conversation_append_messages(
    payload: InternalConversationAppendRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> InternalConversationAppendResponse:
    _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        apply_rls_service_context(session, service_name='internal-support-api')
        response_payload = append_conversation_messages(
            session,
            channel=payload.channel,
            conversation_external_id=payload.conversation_external_id,
            actor_user_id=payload.actor_user_id,
            messages=payload.messages,
        )
        session.commit()
        return response_payload


@app.post('/v1/internal/conversations/tool-calls', response_model=InternalConversationToolCallAppendResponse)
async def internal_conversation_append_tool_calls(
    payload: InternalConversationToolCallAppendRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> InternalConversationToolCallAppendResponse:
    _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        apply_rls_service_context(session, service_name='internal-support-api')
        response_payload = append_conversation_tool_calls(
            session,
            channel=payload.channel,
            conversation_external_id=payload.conversation_external_id,
            actor_user_id=payload.actor_user_id,
            tool_calls=payload.tool_calls,
        )
        session.commit()
        return response_payload


@app.get('/v1/auth/session', response_model=AuthSessionResponse)
async def auth_session(
    authorization: str | None = Header(default=None, alias='Authorization'),
) -> AuthSessionResponse:
    if extract_bearer_token(authorization) is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')
    actor, principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=None,
        user_external_code=None,
    )
    if principal is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')
    return AuthSessionResponse(actor=actor, principal=principal, auth_mode=auth_mode)


@app.post('/v1/auth/telegram-link/challenges', response_model=TelegramLinkChallengeResponse)
async def issue_telegram_link_challenge(
    authorization: str | None = Header(default=None, alias='Authorization'),
) -> TelegramLinkChallengeResponse:
    if extract_bearer_token(authorization) is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')
    actor, principal, _auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=None,
        user_external_code=None,
    )
    if principal is None:
        raise HTTPException(status_code=401, detail='bearer_token_required')

    with session_scope() as session:
        actor = resolve_actor_context(
            session,
            federated_provider=principal.provider,
            federated_subject=principal.subject,
        )
        if actor is None:
            raise HTTPException(status_code=404, detail='actor_not_found_for_token')
        challenge = create_telegram_link_challenge(session, actor=actor)

    return challenge


@app.post('/v1/internal/telegram/link/consume', response_model=TelegramLinkConsumeResponse)
async def internal_consume_telegram_link(
    payload: TelegramLinkConsumeRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> TelegramLinkConsumeResponse:
    _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        response = consume_telegram_link_challenge(
            session,
            challenge_code=payload.challenge_code,
            telegram_user_id=payload.telegram_user_id,
            telegram_chat_id=payload.telegram_chat_id,
            username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
    return response


@app.get('/v1/identity/context')
async def identity_context(
    authorization: str | None = Header(default=None, alias='Authorization'),
    telegram_chat_id: int | None = Query(default=None),
    user_external_code: str | None = Query(default=None),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    actor, principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=telegram_chat_id,
        user_external_code=user_external_code,
        x_internal_api_token=x_internal_api_token,
    )
    return {
        'service': 'api-core',
        'actor': _sanitize_actor_for_external_response(actor, auth_mode=auth_mode).model_dump(mode='json'),
        'principal': principal.model_dump(mode='json') if principal else None,
        'auth_mode': auth_mode,
    }


@app.get('/v1/internal/identity/context')
async def internal_identity_context(
    telegram_chat_id: int = Query(...),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)

    with session_scope() as session:
        actor = resolve_actor_context(session, telegram_chat_id=telegram_chat_id)

    return {
        'service': 'api-core',
        'actor': actor.model_dump(mode='json') if actor else None,
        'auth_mode': 'telegram_chat' if actor else 'anonymous',
    }


@app.post('/v1/authz/check', response_model=PolicyCheckResponse)
async def authz_check(
    payload: PolicyCheckRequest,
    authorization: str | None = Header(default=None, alias='Authorization'),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> PolicyCheckResponse:
    actor, _principal, _auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=payload.telegram_chat_id,
        user_external_code=payload.user_external_code,
        x_internal_api_token=x_internal_api_token,
    )
    decision = await decide_policy(action=payload.action, actor=actor, resource=payload.resource)

    with session_scope() as session:
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type=str(payload.resource.get('resource_type', 'generic')),
            action=payload.action,
            decision='allow' if decision.allow else 'deny',
            reason=decision.reason,
        )

    return PolicyCheckResponse(
        actor=_sanitize_actor_for_external_response(
            actor,
            auth_mode='telegram_chat' if payload.telegram_chat_id is not None else 'external',
        ),
        decision=decision,
        action=payload.action,
        resource=payload.resource,
    )


@app.get('/v1/students/{student_id}/academic-summary')
async def student_academic_summary(
    student_id: uuid.UUID,
    authorization: str | None = Header(default=None, alias='Authorization'),
    telegram_chat_id: int | None = Query(default=None),
    user_external_code: str | None = Query(default=None),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    actor, _principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=telegram_chat_id,
        user_external_code=user_external_code,
        x_internal_api_token=x_internal_api_token,
    )
    return await _student_academic_summary_payload(actor=actor, auth_mode=auth_mode, student_id=student_id)


@app.get('/v1/students/{student_id}/financial-summary')
async def student_financial_summary(
    student_id: uuid.UUID,
    authorization: str | None = Header(default=None, alias='Authorization'),
    telegram_chat_id: int | None = Query(default=None),
    user_external_code: str | None = Query(default=None),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    actor, _principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=telegram_chat_id,
        user_external_code=user_external_code,
        x_internal_api_token=x_internal_api_token,
    )
    return await _student_financial_summary_payload(actor=actor, auth_mode=auth_mode, student_id=student_id)


@app.get('/v1/students/{student_id}/administrative-status')
async def student_administrative_status(
    student_id: uuid.UUID,
    authorization: str | None = Header(default=None, alias='Authorization'),
    telegram_chat_id: int | None = Query(default=None),
    user_external_code: str | None = Query(default=None),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    actor, _principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=telegram_chat_id,
        user_external_code=user_external_code,
        x_internal_api_token=x_internal_api_token,
    )
    return await _student_administrative_status_payload(
        actor=actor,
        auth_mode=auth_mode,
        student_id=student_id,
    )


@app.get('/v1/students/{student_id}/upcoming-assessments')
async def student_upcoming_assessments(
    student_id: uuid.UUID,
    subject_code: str | None = Query(default=None),
    authorization: str | None = Header(default=None, alias='Authorization'),
    telegram_chat_id: int | None = Query(default=None),
    user_external_code: str | None = Query(default=None),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    actor, _principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=telegram_chat_id,
        user_external_code=user_external_code,
        x_internal_api_token=x_internal_api_token,
    )
    return await _student_upcoming_assessments_payload(
        actor=actor,
        auth_mode=auth_mode,
        student_id=student_id,
        subject_code=subject_code,
    )


@app.get('/v1/students/{student_id}/attendance-timeline')
async def student_attendance_timeline(
    student_id: uuid.UUID,
    subject_code: str | None = Query(default=None),
    authorization: str | None = Header(default=None, alias='Authorization'),
    telegram_chat_id: int | None = Query(default=None),
    user_external_code: str | None = Query(default=None),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    actor, _principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=telegram_chat_id,
        user_external_code=user_external_code,
        x_internal_api_token=x_internal_api_token,
    )
    return await _student_attendance_timeline_payload(
        actor=actor,
        auth_mode=auth_mode,
        student_id=student_id,
        subject_code=subject_code,
    )


@app.get('/v1/calendar/public', response_model=CalendarEventsResponse)
async def public_calendar_events(
    date_from: date | None = PUBLIC_CALENDAR_DATE_FROM_QUERY,
    date_to: date | None = PUBLIC_CALENDAR_DATE_TO_QUERY,
    limit: int = PUBLIC_CALENDAR_LIMIT_QUERY,
) -> CalendarEventsResponse:
    with session_scope() as session:
        events = list_public_calendar_events(
            session,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
        )
    return CalendarEventsResponse(events=events)


@app.get('/v1/teachers/me/schedule')
async def teacher_schedule(
    authorization: str | None = Header(default=None, alias='Authorization'),
    telegram_chat_id: int | None = Query(default=None),
    user_external_code: str | None = Query(default=None),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    actor, _principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=telegram_chat_id,
        user_external_code=user_external_code,
        x_internal_api_token=x_internal_api_token,
    )
    return await _teacher_schedule_payload(actor=actor, auth_mode=auth_mode)


@app.get('/v1/actors/me/administrative-status')
async def actor_administrative_status(
    authorization: str | None = Header(default=None, alias='Authorization'),
    telegram_chat_id: int | None = Query(default=None),
    user_external_code: str | None = Query(default=None),
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    actor, _principal, auth_mode = _resolve_request_context(
        authorization=authorization,
        telegram_chat_id=telegram_chat_id,
        user_external_code=user_external_code,
        x_internal_api_token=x_internal_api_token,
    )
    return await _administrative_status_payload(actor=actor, auth_mode=auth_mode)
