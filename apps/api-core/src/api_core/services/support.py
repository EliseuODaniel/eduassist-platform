from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from api_core.contracts import (
    ActorContext,
    SupportConversationMessageEntry,
    SupportHandoffCreateResponse,
    SupportHandoffEntry,
)
from api_core.db.models import Conversation, Handoff, Message, User

OPEN_HANDOFF_STATUSES = frozenset({'queued', 'in_progress'})
SUPPORTED_HANDOFF_STATUSES = frozenset({'queued', 'in_progress', 'resolved', 'cancelled'})


def build_ticket_code(*, handoff_id: uuid.UUID, created_at) -> str:
    return f'ATD-{created_at:%Y%m%d}-{str(handoff_id).split("-")[0].upper()}'


def resolve_support_scope(actor: ActorContext) -> str:
    if actor.role_code in {'staff', 'finance', 'coordinator', 'admin'}:
        return 'global'
    return 'self'


def _truncate_excerpt(text: str | None, *, limit: int = 180) -> str | None:
    if not text:
        return None
    compact = ' '.join(text.split())
    if len(compact) <= limit:
        return compact
    return f'{compact[: limit - 1].rstrip()}...'


def _load_latest_user_messages(
    session: Session,
    *,
    conversation_ids: list[uuid.UUID],
) -> dict[uuid.UUID, str]:
    if not conversation_ids:
        return {}

    rows = session.execute(
        select(Message.conversation_id, Message.content)
        .where(Message.conversation_id.in_(conversation_ids))
        .where(Message.sender_type == 'user')
        .order_by(Message.conversation_id.asc(), Message.created_at.desc())
    ).all()

    latest_messages: dict[uuid.UUID, str] = {}
    for conversation_id, content in rows:
        if conversation_id not in latest_messages:
            latest_messages[conversation_id] = content
    return latest_messages


def _serialize_handoff_rows(
    session: Session,
    rows: list[tuple[Handoff, Conversation, str | None, str | None]],
) -> list[SupportHandoffEntry]:
    conversation_ids = [conversation.id for _, conversation, _, _ in rows]
    latest_messages = _load_latest_user_messages(session, conversation_ids=conversation_ids)

    return [
        SupportHandoffEntry(
            handoff_id=handoff.id,
            conversation_id=conversation.id,
            ticket_code=build_ticket_code(handoff_id=handoff.id, created_at=handoff.created_at),
            channel=conversation.channel,
            external_thread_id=conversation.external_thread_id,
            queue_name=handoff.queue_name,
            status=handoff.status,
            summary=handoff.summary,
            requester_name=requester_name,
            requester_role=requester_role,
            last_message_excerpt=_truncate_excerpt(latest_messages.get(conversation.id)),
            created_at=handoff.created_at,
            updated_at=handoff.updated_at,
        )
        for handoff, conversation, requester_name, requester_role in rows
    ]


def list_support_handoffs(
    session: Session,
    *,
    actor: ActorContext,
    scope: str,
    limit: int = 10,
) -> tuple[dict[str, int], list[SupportHandoffEntry]]:
    requester = aliased(User)
    base_stmt = (
        select(Handoff, Conversation, requester.full_name, requester.role_code)
        .join(Conversation, Conversation.id == Handoff.conversation_id)
        .outerjoin(requester, requester.id == Conversation.user_id)
    )

    if scope == 'self':
        base_stmt = base_stmt.where(Conversation.user_id == actor.user_id)

    rows = session.execute(
        base_stmt.order_by(Handoff.updated_at.desc(), Handoff.created_at.desc()).limit(limit)
    ).all()

    count_stmt = (
        select(Handoff.status, func.count())
        .join(Conversation, Conversation.id == Handoff.conversation_id)
        .group_by(Handoff.status)
    )
    if scope == 'self':
        count_stmt = count_stmt.where(Conversation.user_id == actor.user_id)

    counts = {status: int(total) for status, total in session.execute(count_stmt).all()}
    items = _serialize_handoff_rows(session, rows)
    return counts, items


def get_support_handoff_detail(
    session: Session,
    *,
    actor: ActorContext,
    scope: str,
    handoff_id: uuid.UUID,
) -> tuple[SupportHandoffEntry, str, list[SupportConversationMessageEntry]] | None:
    requester = aliased(User)
    stmt = (
        select(Handoff, Conversation, requester.full_name, requester.role_code)
        .join(Conversation, Conversation.id == Handoff.conversation_id)
        .outerjoin(requester, requester.id == Conversation.user_id)
        .where(Handoff.id == handoff_id)
    )

    if scope == 'self':
        stmt = stmt.where(Conversation.user_id == actor.user_id)

    row = session.execute(stmt).first()
    if row is None:
        return None

    handoff, conversation, requester_name, requester_role = row
    item = _serialize_handoff_rows(session, [(handoff, conversation, requester_name, requester_role)])[0]
    messages = [
        SupportConversationMessageEntry(
            message_id=message.id,
            sender_type=message.sender_type,
            content=message.content,
            created_at=message.created_at,
        )
        for message in session.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc(), Message.id.asc())
        ).scalars()
    ]
    return item, conversation.status, messages


def create_support_handoff(
    session: Session,
    *,
    actor_user_id: uuid.UUID | None,
    channel: str,
    conversation_external_id: str,
    queue_name: str,
    summary: str,
    user_message: str | None = None,
) -> SupportHandoffCreateResponse:
    conversation = session.execute(
        select(Conversation)
        .where(Conversation.channel == channel)
        .where(Conversation.external_thread_id == conversation_external_id)
        .order_by(Conversation.created_at.desc())
    ).scalar_one_or_none()

    if conversation is None:
        conversation = Conversation(
            user_id=actor_user_id,
            channel=channel,
            external_thread_id=conversation_external_id,
            status='open',
        )
        session.add(conversation)
        session.flush()
    elif actor_user_id is not None and conversation.user_id is None:
        conversation.user_id = actor_user_id

    if user_message:
        latest_message = session.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()
        if latest_message is None or latest_message.content != user_message or latest_message.sender_type != 'user':
            session.add(
                Message(
                    conversation_id=conversation.id,
                    sender_type='user',
                    content=user_message,
                )
            )

    handoff = session.execute(
        select(Handoff)
        .where(Handoff.conversation_id == conversation.id)
        .where(Handoff.status.in_(OPEN_HANDOFF_STATUSES))
        .order_by(Handoff.updated_at.desc(), Handoff.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    created = handoff is None
    if handoff is None:
        handoff = Handoff(
            conversation_id=conversation.id,
            queue_name=queue_name,
            status='queued',
            summary=summary,
        )
        session.add(handoff)
    else:
        handoff.queue_name = queue_name
        handoff.summary = summary

    conversation.status = 'open'
    session.flush()

    requester = session.execute(
        select(User.full_name, User.role_code).where(User.id == conversation.user_id)
    ).first()
    requester_name = requester[0] if requester else None
    requester_role = requester[1] if requester else None

    item = _serialize_handoff_rows(session, [(handoff, conversation, requester_name, requester_role)])[0]
    return SupportHandoffCreateResponse(created=created, deduplicated=not created, item=item)


def update_support_handoff_status(
    session: Session,
    *,
    handoff_id: uuid.UUID,
    status: str,
    operator_note: str | None = None,
) -> SupportHandoffEntry | None:
    if status not in SUPPORTED_HANDOFF_STATUSES:
        raise ValueError('unsupported_handoff_status')

    requester = aliased(User)
    row = session.execute(
        select(Handoff, Conversation, requester.full_name, requester.role_code)
        .join(Conversation, Conversation.id == Handoff.conversation_id)
        .outerjoin(requester, requester.id == Conversation.user_id)
        .where(Handoff.id == handoff_id)
    ).first()
    if row is None:
        return None

    handoff, conversation, requester_name, requester_role = row
    handoff.status = status
    conversation.status = 'closed' if status in {'resolved', 'cancelled'} else 'open'

    if operator_note:
        session.add(
            Message(
                conversation_id=conversation.id,
                sender_type='operator',
                content=operator_note,
            )
        )

    session.flush()
    return _serialize_handoff_rows(session, [(handoff, conversation, requester_name, requester_role)])[0]
