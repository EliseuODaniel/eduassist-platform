from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from api_core.db.models import AccessDecision


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
