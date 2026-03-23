from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from api_core.contracts import AccessDecisionFeedEntry, ActorContext, AuditEventFeedEntry
from api_core.db.models import (
    AccessDecision,
    AttendanceRecord,
    AuditEvent,
    CalendarEvent,
    Class,
    Contract,
    Document,
    DocumentChunk,
    Enrollment,
    FederatedIdentity,
    Grade,
    GradeItem,
    Guardian,
    Invoice,
    Student,
    Teacher,
    TelegramAccount,
    User,
    UserTelegramLink,
)

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
