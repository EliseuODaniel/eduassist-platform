from __future__ import annotations

import json
import uuid
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from functools import lru_cache
from typing import TYPE_CHECKING

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from api_core.config import get_settings

if TYPE_CHECKING:
    from api_core.contracts import ActorContext


@lru_cache
def get_engine():
    settings = get_settings()
    return create_engine(settings.sqlalchemy_database_url, future=True, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def apply_rls_identity_context(
    session: Session,
    *,
    user_id: uuid.UUID,
    role_code: str,
) -> None:
    apply_rls_context(
        session,
        context_payload={
            'user_id': str(user_id),
            'role_code': role_code,
        },
    )


def apply_rls_actor_context(session: Session, actor: ActorContext) -> None:
    payload: dict[str, object] = {
        'user_id': str(actor.user_id),
        'role_code': actor.role_code,
        'guardian_id': str(actor.guardian_id) if actor.guardian_id else None,
        'student_id': str(actor.student_id) if actor.student_id else None,
        'teacher_id': str(actor.teacher_id) if actor.teacher_id else None,
        'linked_student_ids': _serialize_uuid_sequence(actor.linked_student_ids),
        'academic_student_ids': _serialize_uuid_sequence(actor.academic_student_ids),
        'financial_student_ids': _serialize_uuid_sequence(actor.financial_student_ids),
        'accessible_class_ids': _serialize_uuid_sequence(actor.accessible_class_ids),
    }
    apply_rls_context(session, context_payload=payload)


def apply_rls_context(session: Session, *, context_payload: Mapping[str, object]) -> None:
    session.execute(
        text("select set_config('eduassist.actor_context', :context_payload, true)"),
        {'context_payload': json.dumps(context_payload, separators=(',', ':'), sort_keys=True)},
    )


def _serialize_uuid_sequence(values: Sequence[uuid.UUID]) -> list[str]:
    return [str(value) for value in values]
