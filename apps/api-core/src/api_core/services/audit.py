from __future__ import annotations

import uuid
from functools import lru_cache
from datetime import datetime, timedelta, timezone

from eduassist_observability import get_meter
from opentelemetry.metrics import Observation
from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from api_core.contracts import (
    AccessDecisionFeedEntry,
    ActorContext,
    AuditEventFeedEntry,
    HandoffAlertEntry,
    HandoffObservabilityOverview,
    HandoffOperationsOverview,
    HandoffOperatorOverviewEntry,
    HandoffQueueOverviewEntry,
    HandoffTrendPoint,
)
from api_core.db.models import (
    AccessDecision,
    AttendanceRecord,
    AuditEvent,
    CalendarEvent,
    Class,
    Conversation,
    Contract,
    Document,
    DocumentChunk,
    Enrollment,
    FederatedIdentity,
    Grade,
    GradeItem,
    Guardian,
    Handoff,
    Invoice,
    Student,
    Teacher,
    TelegramAccount,
    User,
    UserTelegramLink,
)
from api_core.db.session import apply_rls_service_context
from api_core.services.support import calculate_handoff_sla_state

INTERNAL_OPERATIONS_ROLES = frozenset({'staff', 'finance', 'coordinator', 'admin'})


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_queue_metric_label(queue_name: str | None) -> str:
    if not queue_name:
        return 'unknown'
    return queue_name.strip().lower()


def _priority_weight(priority_code: str) -> int:
    weights = {
        'urgent': 3,
        'high': 2,
        'standard': 1,
    }
    return weights.get(priority_code, 0)


def _handoff_alert_flags(*, sla_state: str, priority_code: str, assigned_user_id: uuid.UUID | None) -> list[str]:
    flags: list[str] = []
    if sla_state == 'breached':
        flags.append('sla_breached')
    elif sla_state == 'attention':
        flags.append('sla_attention')

    if priority_code in {'urgent', 'high'}:
        flags.append(f'priority_{priority_code}')

    if assigned_user_id is None:
        flags.append('unassigned')
    return flags


def _handoff_alert_sort_key(
    *,
    sla_state: str,
    priority_code: str,
    assigned_user_id: uuid.UUID | None,
    due_at: datetime | None,
    updated_at: datetime,
) -> tuple[int, int, int, datetime, datetime]:
    severity = {
        'breached': 0,
        'attention': 1,
        'on_track': 2,
        'closed': 3,
        'unknown': 4,
    }.get(sla_state, 5)
    unassigned_rank = 0 if assigned_user_id is None else 1
    priority_rank = -_priority_weight(priority_code)
    due_rank = due_at or updated_at
    return severity, unassigned_rank, priority_rank, due_rank, updated_at


def record_access_decision(
    session: Session,
    *,
    actor_user_id: uuid.UUID | None,
    resource_type: str,
    action: str,
    decision: str,
    reason: str,
) -> None:
    session.add(
        AccessDecision(
            actor_user_id=actor_user_id,
            resource_type=resource_type,
            action=action,
            decision=decision,
            reason=reason,
        )
    )


def record_audit_event(
    session: Session,
    *,
    actor_user_id: uuid.UUID | None,
    event_type: str,
    resource_type: str,
    resource_id: str | None = None,
    metadata: dict[str, object] | None = None,
) -> None:
    session.add(
        AuditEvent(
            actor_user_id=actor_user_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_json=dict(metadata or {}),
        )
    )


def resolve_operations_scope(actor: ActorContext) -> str:
    return 'global' if actor.role_code in INTERNAL_OPERATIONS_ROLES else 'self'


def list_recent_audit_events(
    session: Session,
    *,
    actor_user_id: uuid.UUID | None = None,
    limit: int = 8,
) -> list[AuditEventFeedEntry]:
    actor_user = aliased(User)
    stmt = (
        select(
            AuditEvent.created_at,
            AuditEvent.actor_user_id,
            actor_user.external_code,
            actor_user.full_name,
            AuditEvent.event_type,
            AuditEvent.resource_type,
            AuditEvent.resource_id,
            AuditEvent.metadata_json,
        )
        .select_from(AuditEvent)
        .outerjoin(actor_user, actor_user.id == AuditEvent.actor_user_id)
        .order_by(AuditEvent.created_at.desc())
        .limit(limit)
    )
    if actor_user_id is not None:
        stmt = stmt.where(AuditEvent.actor_user_id == actor_user_id)

    return [
        AuditEventFeedEntry(
            occurred_at=occurred_at,
            actor_user_id=row_actor_user_id,
            actor_external_code=actor_external_code,
            actor_full_name=actor_full_name,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
        )
        for occurred_at, row_actor_user_id, actor_external_code, actor_full_name, event_type, resource_type, resource_id, metadata in session.execute(stmt).all()
    ]


def list_recent_access_decisions(
    session: Session,
    *,
    actor_user_id: uuid.UUID | None = None,
    limit: int = 8,
) -> list[AccessDecisionFeedEntry]:
    actor_user = aliased(User)
    stmt = (
        select(
            AccessDecision.created_at,
            AccessDecision.actor_user_id,
            actor_user.external_code,
            actor_user.full_name,
            AccessDecision.resource_type,
            AccessDecision.action,
            AccessDecision.decision,
            AccessDecision.reason,
        )
        .select_from(AccessDecision)
        .outerjoin(actor_user, actor_user.id == AccessDecision.actor_user_id)
        .order_by(AccessDecision.created_at.desc())
        .limit(limit)
    )
    if actor_user_id is not None:
        stmt = stmt.where(AccessDecision.actor_user_id == actor_user_id)

    return [
        AccessDecisionFeedEntry(
            occurred_at=occurred_at,
            actor_user_id=row_actor_user_id,
            actor_external_code=actor_external_code,
            actor_full_name=actor_full_name,
            resource_type=resource_type,
            action=action,
            decision=decision,
            reason=reason,
        )
        for occurred_at, row_actor_user_id, actor_external_code, actor_full_name, resource_type, action, decision, reason in session.execute(stmt).all()
    ]


def build_operations_metrics(
    session: Session,
    *,
    actor: ActorContext,
    scope: str,
    recent_days: int = 7,
) -> dict[str, int]:
    since = datetime.utcnow() - timedelta(days=recent_days)

    audit_stmt = select(func.count()).select_from(AuditEvent).where(AuditEvent.created_at >= since)
    access_stmt = select(func.count()).select_from(AccessDecision).where(AccessDecision.created_at >= since)
    deny_stmt = (
        select(func.count())
        .select_from(AccessDecision)
        .where(AccessDecision.created_at >= since)
        .where(AccessDecision.decision == 'deny')
    )

    if scope == 'self':
        audit_stmt = audit_stmt.where(AuditEvent.actor_user_id == actor.user_id)
        access_stmt = access_stmt.where(AccessDecision.actor_user_id == actor.user_id)
        deny_stmt = deny_stmt.where(AccessDecision.actor_user_id == actor.user_id)

    metrics = {
        'recent_audit_events': int(session.execute(audit_stmt).scalar_one() or 0),
        'recent_access_decisions': int(session.execute(access_stmt).scalar_one() or 0),
        'recent_denials': int(session.execute(deny_stmt).scalar_one() or 0),
        'telegram_linked': 1 if actor.telegram_linked else 0,
    }

    if scope == 'global':
        total_users = int(session.execute(select(func.count()).select_from(User)).scalar_one() or 0)
        linked_users = int(
            session.execute(
                select(func.count(func.distinct(UserTelegramLink.user_id))).select_from(UserTelegramLink)
            ).scalar_one()
            or 0
        )
        metrics.update(
            {
                'active_users': total_users,
                'linked_telegram_accounts': linked_users,
                'pending_telegram_links': max(total_users - linked_users, 0),
            }
        )
    else:
        metrics.update(
            {
                'linked_students': len(actor.linked_students),
                'accessible_classes': len(actor.accessible_classes),
            }
        )

    return metrics


def build_handoff_operations_overview(
    session: Session,
    *,
    actor: ActorContext,
    scope: str,
) -> HandoffOperationsOverview | None:
    if scope != 'global':
        return None

    requester = aliased(User)
    assignee = aliased(User)
    rows = session.execute(
        select(
            Handoff,
            requester.full_name,
            assignee.id,
            assignee.external_code,
            assignee.full_name,
        )
        .select_from(Handoff)
        .join(Conversation, Conversation.id == Handoff.conversation_id)
        .outerjoin(requester, requester.id == Conversation.user_id)
        .outerjoin(assignee, assignee.id == Handoff.assigned_user_id)
        .where(Handoff.status.in_(('queued', 'in_progress')))
        .order_by(Handoff.updated_at.desc(), Handoff.created_at.desc())
    ).all()

    queue_stats: dict[str, dict[str, int]] = {}
    operator_stats: dict[uuid.UUID, dict[str, object]] = {}
    alert_candidates: list[tuple[tuple[int, int, int, datetime, datetime], HandoffAlertEntry]] = []
    overview = HandoffOperationsOverview()

    for handoff, requester_name, operator_user_id, operator_external_code, operator_name in rows:
        sla_state = calculate_handoff_sla_state(handoff)
        due_at = handoff.response_due_at if handoff.status == 'queued' else handoff.resolution_due_at
        alert_flags = _handoff_alert_flags(
            sla_state=sla_state,
            priority_code=handoff.priority_code,
            assigned_user_id=handoff.assigned_user_id,
        )
        queue_name = handoff.queue_name
        queue_entry = queue_stats.setdefault(
            queue_name,
            {
                'open_count': 0,
                'queued_count': 0,
                'in_progress_count': 0,
                'attention_count': 0,
                'breached_count': 0,
                'unassigned_count': 0,
            },
        )

        overview.open_total += 1
        queue_entry['open_count'] += 1

        if handoff.status == 'queued':
            overview.queued_total += 1
            queue_entry['queued_count'] += 1
        elif handoff.status == 'in_progress':
            overview.in_progress_total += 1
            queue_entry['in_progress_count'] += 1

        if sla_state == 'attention':
            overview.attention_total += 1
            queue_entry['attention_count'] += 1
        elif sla_state == 'breached':
            overview.breached_total += 1
            queue_entry['breached_count'] += 1

        if handoff.assigned_user_id is None:
            overview.unassigned_total += 1
            queue_entry['unassigned_count'] += 1
        elif operator_user_id and operator_external_code and operator_name:
            operator_entry = operator_stats.setdefault(
                operator_user_id,
                {
                    'operator_external_code': operator_external_code,
                    'operator_name': operator_name,
                    'assigned_count': 0,
                    'queued_count': 0,
                    'in_progress_count': 0,
                    'attention_count': 0,
                    'breached_count': 0,
                },
            )
            operator_entry['assigned_count'] += 1
            if handoff.status == 'queued':
                operator_entry['queued_count'] += 1
            elif handoff.status == 'in_progress':
                operator_entry['in_progress_count'] += 1
            if sla_state == 'attention':
                operator_entry['attention_count'] += 1
            elif sla_state == 'breached':
                operator_entry['breached_count'] += 1

        if alert_flags:
            alert_entry = HandoffAlertEntry(
                handoff_id=handoff.id,
                ticket_code=f'ATD-{handoff.created_at:%Y%m%d}-{str(handoff.id).split("-")[0].upper()}',
                queue_name=handoff.queue_name,
                priority_code=handoff.priority_code,
                status=handoff.status,
                summary=handoff.summary,
                requester_name=requester_name,
                assigned_operator_name=operator_name,
                updated_at=handoff.updated_at,
                response_due_at=handoff.response_due_at,
                resolution_due_at=handoff.resolution_due_at,
                sla_state=sla_state,
                alert_flags=alert_flags,
            )
            alert_candidates.append(
                (
                    _handoff_alert_sort_key(
                        sla_state=sla_state,
                        priority_code=handoff.priority_code,
                        assigned_user_id=handoff.assigned_user_id,
                        due_at=due_at,
                        updated_at=handoff.updated_at,
                    ),
                    alert_entry,
                )
            )

    overview.queues = [
        HandoffQueueOverviewEntry(queue_name=queue_name, **stats)
        for queue_name, stats in sorted(
            queue_stats.items(),
            key=lambda item: (-item[1]['open_count'], item[0]),
        )
    ]
    overview.operators = [
        HandoffOperatorOverviewEntry(operator_user_id=operator_user_id, **stats)
        for operator_user_id, stats in sorted(
            operator_stats.items(),
            key=lambda item: (-int(item[1]['assigned_count']), str(item[1]['operator_name'])),
        )
    ]
    overview.alerts = [entry for _, entry in sorted(alert_candidates, key=lambda item: item[0])[:6]]
    overview.critical_total = len(alert_candidates)
    overview.observability = build_handoff_observability_overview(session)
    return overview


def _load_live_support_metric_rows(session: Session) -> list[tuple[Handoff, str | None, str | None]]:
    assignee = aliased(User)
    return session.execute(
        select(Handoff, assignee.external_code, assignee.full_name)
        .select_from(Handoff)
        .outerjoin(assignee, assignee.id == Handoff.assigned_user_id)
        .where(Handoff.status.in_(('queued', 'in_progress')))
    ).all()


def _support_backlog_observations(_: object) -> list[Observation]:
    from api_core.db.session import session_scope

    with session_scope() as session:
        apply_rls_service_context(session, service_name='support-metrics')
        rows = _load_live_support_metric_rows(session)

    counts: dict[tuple[str, str, str], int] = {}
    for handoff, _, _ in rows:
        queue_name = _normalize_queue_metric_label(handoff.queue_name)
        sla_state = calculate_handoff_sla_state(handoff)
        key = (queue_name, handoff.status, sla_state)
        counts[key] = counts.get(key, 0) + 1

    observations: list[Observation] = []
    total_open = 0
    for (queue_name, status, sla_state), count in counts.items():
        total_open += count
        observations.append(
            Observation(
                count,
                {
                    'queue_name': queue_name,
                    'status': status,
                    'sla_state': sla_state,
                },
            )
        )
    observations.append(
        Observation(
            total_open,
            {
                'queue_name': 'all',
                'status': 'all',
                'sla_state': 'all',
            },
        )
    )
    return observations


def _support_unassigned_observations(_: object) -> list[Observation]:
    from api_core.db.session import session_scope

    with session_scope() as session:
        apply_rls_service_context(session, service_name='support-metrics')
        rows = _load_live_support_metric_rows(session)

    counts: dict[str, int] = {}
    total_unassigned = 0
    for handoff, _, _ in rows:
        if handoff.assigned_user_id is not None:
            continue
        queue_name = _normalize_queue_metric_label(handoff.queue_name)
        counts[queue_name] = counts.get(queue_name, 0) + 1
        total_unassigned += 1

    observations = [
        Observation(count, {'queue_name': queue_name})
        for queue_name, count in sorted(counts.items())
    ]
    observations.append(Observation(total_unassigned, {'queue_name': 'all'}))
    return observations


def _support_operator_observations(_: object) -> list[Observation]:
    from api_core.db.session import session_scope

    with session_scope() as session:
        apply_rls_service_context(session, service_name='support-metrics')
        rows = _load_live_support_metric_rows(session)

    counts: dict[tuple[str, str, str], int] = {}
    total_assigned = 0
    for handoff, operator_external_code, operator_name in rows:
        if handoff.assigned_user_id is None:
            continue
        operator_code = operator_external_code or 'unknown'
        operator_label = operator_name or operator_code
        key = (operator_code, operator_label, handoff.status)
        counts[key] = counts.get(key, 0) + 1
        total_assigned += 1

    observations = [
        Observation(
            count,
            {
                'operator_external_code': operator_code,
                'operator_name': operator_name,
                'status': status,
            },
        )
        for (operator_code, operator_name, status), count in sorted(counts.items())
    ]
    observations.append(
        Observation(
            total_assigned,
            {
                'operator_external_code': 'all',
                'operator_name': 'all',
                'status': 'all',
            },
        )
    )
    return observations


@lru_cache(maxsize=1)
def register_support_operational_metrics() -> bool:
    meter = get_meter('eduassist.api_core.support.live')
    meter.create_observable_gauge(
        'eduassist_support_backlog_current',
        callbacks=[_support_backlog_observations],
        description='Current open handoffs grouped by queue, status and SLA state.',
    )
    meter.create_observable_gauge(
        'eduassist_support_unassigned_current',
        callbacks=[_support_unassigned_observations],
        description='Current unassigned handoffs grouped by queue.',
    )
    meter.create_observable_gauge(
        'eduassist_support_operator_active_current',
        callbacks=[_support_operator_observations],
        description='Current assigned handoffs grouped by operator and status.',
    )
    return True


def build_handoff_observability_overview(session: Session) -> HandoffObservabilityOverview:
    now = datetime.utcnow()
    now_utc = now.replace(tzinfo=timezone.utc)
    since_24h = now - timedelta(hours=24)
    since_7d = now - timedelta(days=7)
    since_24h_utc = now_utc - timedelta(hours=24)
    start_of_today = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    timeline_starts = [start_of_today - timedelta(days=offset) for offset in range(6, -1, -1)]
    timeline = {
        point.date(): HandoffTrendPoint(
            period_start=point,
            label=point.strftime('%d/%m'),
        )
        for point in timeline_starts
    }

    event_rows = session.execute(
        select(AuditEvent.created_at, AuditEvent.event_type, AuditEvent.metadata_json)
        .where(AuditEvent.resource_type == 'support_handoff')
        .where(AuditEvent.created_at >= since_7d)
        .where(
            AuditEvent.event_type.in_(
                (
                    'support_handoff.created',
                    'support_handoff.status_updated',
                )
            )
        )
        .order_by(AuditEvent.created_at.asc())
    ).all()

    opened_last_24h = 0
    started_last_24h = 0
    resolved_last_24h = 0
    opened_last_7d = 0
    started_last_7d = 0
    resolved_last_7d = 0

    for occurred_at, event_type, metadata in event_rows:
        event_at = _as_utc(occurred_at)
        bucket = timeline.get(event_at.date())
        event_status = (metadata or {}).get('status')

        if event_type == 'support_handoff.created':
            opened_last_7d += 1
            if event_at >= since_24h_utc:
                opened_last_24h += 1
            if bucket is not None:
                bucket.opened_count += 1
            continue

        if event_type == 'support_handoff.status_updated' and event_status == 'in_progress':
            started_last_7d += 1
            if event_at >= since_24h_utc:
                started_last_24h += 1
            if bucket is not None:
                bucket.started_count += 1
            continue

        if event_type == 'support_handoff.status_updated' and event_status == 'resolved':
            resolved_last_7d += 1
            if event_at >= since_24h_utc:
                resolved_last_24h += 1
            if bucket is not None:
                bucket.resolved_count += 1

    resolved_rows = session.execute(
        select(Handoff.created_at, Handoff.assigned_at, Handoff.updated_at, Handoff.status)
        .where(Handoff.updated_at >= since_7d)
    ).all()

    assignment_durations: list[float] = []
    resolution_durations: list[float] = []
    for created_at, assigned_at, updated_at, status in resolved_rows:
        created_utc = _as_utc(created_at)
        if assigned_at is not None:
            assigned_utc = _as_utc(assigned_at)
            assignment_durations.append(max((assigned_utc - created_utc).total_seconds() / 60, 0.0))

        if status in {'resolved', 'cancelled'}:
            updated_utc = _as_utc(updated_at)
            resolution_durations.append(max((updated_utc - created_utc).total_seconds() / 60, 0.0))

    return HandoffObservabilityOverview(
        opened_last_24h=opened_last_24h,
        started_last_24h=started_last_24h,
        resolved_last_24h=resolved_last_24h,
        opened_last_7d=opened_last_7d,
        started_last_7d=started_last_7d,
        resolved_last_7d=resolved_last_7d,
        avg_assignment_minutes_7d=round(sum(assignment_durations) / len(assignment_durations), 1)
        if assignment_durations
        else None,
        avg_resolution_minutes_7d=round(sum(resolution_durations) / len(resolution_durations), 1)
        if resolution_durations
        else None,
        timeline=[timeline[key.date()] for key in timeline_starts],
    )


def get_foundation_counts(session: Session) -> dict[str, int]:
    count_targets = {
        'users': User,
        'telegram_accounts': TelegramAccount,
        'federated_identities': FederatedIdentity,
        'students': Student,
        'guardians': Guardian,
        'teachers': Teacher,
        'classes': Class,
        'enrollments': Enrollment,
        'grade_items': GradeItem,
        'grades': Grade,
        'attendance_records': AttendanceRecord,
        'contracts': Contract,
        'invoices': Invoice,
        'calendar_events': CalendarEvent,
        'documents': Document,
        'document_chunks': DocumentChunk,
    }

    return {
        key: int(session.execute(select(func.count()).select_from(model)).scalar_one() or 0)
        for key, model in count_targets.items()
    }
