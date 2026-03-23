from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from api_core.db.models import AccessDecision, AuditEvent


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
