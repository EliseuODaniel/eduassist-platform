from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from api_core.contracts import (
    AccessDecisionFeedEntry,
    ActorContext,
    AuditEventFeedEntry,
    HandoffOperationsOverview,
    HandoffOperatorOverviewEntry,
    HandoffQueueOverviewEntry,
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
from api_core.services.support import calculate_handoff_sla_state

INTERNAL_OPERATIONS_ROLES = frozenset({'staff', 'finance', 'coordinator', 'admin'})


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

    assignee = aliased(User)
    rows = session.execute(
        select(Handoff, assignee.id, assignee.external_code, assignee.full_name)
        .select_from(Handoff)
        .join(Conversation, Conversation.id == Handoff.conversation_id)
        .outerjoin(assignee, assignee.id == Handoff.assigned_user_id)
        .where(Handoff.status.in_(('queued', 'in_progress')))
        .order_by(Handoff.updated_at.desc(), Handoff.created_at.desc())
    ).all()

    queue_stats: dict[str, dict[str, int]] = {}
    operator_stats: dict[uuid.UUID, dict[str, object]] = {}
    overview = HandoffOperationsOverview()

    for handoff, operator_user_id, operator_external_code, operator_name in rows:
        sla_state = calculate_handoff_sla_state(handoff)
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
    return overview


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
