from __future__ import annotations

import copy
import secrets
import uuid
from datetime import date

from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel

from api_core.config import get_settings
from api_core.contracts import (
    ActorContext,
    AuthPrincipal,
    AuthSessionResponse,
    CalendarEventsResponse,
    OperationsOverviewResponse,
    PolicyCheckRequest,
    PolicyCheckResponse,
    TelegramLinkChallengeResponse,
    TelegramLinkConsumeRequest,
    TelegramLinkConsumeResponse,
)
from api_core.db.session import session_scope
from api_core.services.audit import (
    build_operations_metrics,
    get_foundation_counts,
    list_recent_access_decisions,
    list_recent_audit_events,
    record_access_decision,
    resolve_operations_scope,
)
from api_core.services.auth import decode_access_token, extract_bearer_token
from api_core.services.domain import (
    get_student_academic_summary,
    get_student_financial_summary,
    get_teacher_schedule,
    list_public_calendar_events,
)
from api_core.services.identity import resolve_actor_context
from api_core.services.policy import decide_policy
from api_core.services.telegram_link import create_telegram_link_challenge, consume_telegram_link_challenge


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    database: str


app = FastAPI(
    title='EduAssist API Core',
    version='0.3.0',
    summary='Core domain API for identity, policy, audit and school data services.',
)


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
    with session_scope() as session:
        summary = get_student_academic_summary(session, student_id)
        if summary is None:
            raise HTTPException(status_code=404, detail='student_not_found')

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
    with session_scope() as session:
        summary = get_student_financial_summary(session, student_id)
        if summary is None:
            raise HTTPException(status_code=404, detail='student_not_found')

        decision = await decide_policy(
            action='student.finance.read',
            actor=actor,
            resource={
                'student_id': str(summary.student_id),
                'resource_type': 'student_financial_summary',
            },
        )
        record_access_decision(
            session,
            actor_user_id=actor.user_id,
            resource_type='student_financial_summary',
            action='student.finance.read',
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


async def _teacher_schedule_payload(
    *,
    actor: ActorContext,
    auth_mode: str,
) -> dict[str, object]:
    with session_scope() as session:
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


@app.get('/healthz', response_model=HealthResponse)
async def healthz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status='ok',
        service='api-core',
        environment=settings.app_env,
        database='configured',
    )


@app.get('/meta')
async def meta() -> dict[str, str | bool]:
    settings = get_settings()
    return {
        'service': 'api-core',
        'environment': settings.app_env,
        'logLevel': settings.log_level,
        'databaseUrl': settings.database_url,
        'redisUrl': settings.redis_url,
        'opaUrl': settings.opa_url,
        'keycloakIssuer': settings.keycloak_issuer,
        'keycloakJwksUrl': settings.keycloak_jwks_url,
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
            actor_user_id = None if scope == 'global' else actor.user_id
            overview = OperationsOverviewResponse(
                actor=_sanitize_actor_for_external_response(actor, auth_mode=auth_mode),
                scope=scope,
                metrics=build_operations_metrics(session, actor=actor, scope=scope),
                foundation_counts=get_foundation_counts(session) if scope == 'global' else None,
                audit_events=list_recent_audit_events(session, actor_user_id=actor_user_id),
                access_decisions=list_recent_access_decisions(session, actor_user_id=actor_user_id),
            )

    if not decision.allow:
        raise HTTPException(status_code=403, detail=decision.reason)
    if overview is None:
        raise HTTPException(status_code=500, detail='operations_overview_unavailable')
    return overview


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


@app.get('/v1/calendar/public', response_model=CalendarEventsResponse)
async def public_calendar_events(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: int = Query(default=6, ge=1, le=20),
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
