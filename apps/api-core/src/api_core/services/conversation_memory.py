from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api_core.contracts import (
    InternalConversationAppendResponse,
    InternalConversationContextResponse,
    InternalConversationMessageCreate,
    InternalConversationMessageEntry,
)
from api_core.db.models import Conversation, Message


def _resolve_or_create_conversation(
    session: Session,
    *,
    channel: str,
    conversation_external_id: str,
    actor_user_id: uuid.UUID | None,
) -> Conversation:
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
        return conversation

    if actor_user_id is not None and conversation.user_id is None:
        conversation.user_id = actor_user_id

    return conversation


def append_conversation_messages(
    session: Session,
    *,
    channel: str,
    conversation_external_id: str,
    actor_user_id: uuid.UUID | None,
    messages: list[InternalConversationMessageCreate],
) -> InternalConversationAppendResponse:
    conversation = _resolve_or_create_conversation(
        session,
        channel=channel,
        conversation_external_id=conversation_external_id,
        actor_user_id=actor_user_id,
    )

    stored_messages = 0
    deduplicated_messages = 0
    for payload in messages:
        latest_message = session.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(1)
        ).scalar_one_or_none()
        if (
            latest_message is not None
            and latest_message.sender_type == payload.sender_type
            and latest_message.content == payload.content
        ):
            deduplicated_messages += 1
            continue

        session.add(
            Message(
                conversation_id=conversation.id,
                sender_type=payload.sender_type,
                content=payload.content,
            )
        )
        stored_messages += 1

    conversation.status = 'open'
    session.flush()

    message_count = int(
        session.execute(
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conversation.id)
        ).scalar_one()
    )

    return InternalConversationAppendResponse(
        channel=channel,
        conversation_external_id=conversation_external_id,
        stored_messages=stored_messages,
        deduplicated_messages=deduplicated_messages,
        message_count=message_count,
    )


def get_conversation_context(
    session: Session,
    *,
    channel: str,
    conversation_external_id: str,
    limit: int = 6,
) -> InternalConversationContextResponse:
    conversation = session.execute(
        select(Conversation)
        .where(Conversation.channel == channel)
        .where(Conversation.external_thread_id == conversation_external_id)
        .order_by(Conversation.created_at.desc())
    ).scalar_one_or_none()

    if conversation is None:
        return InternalConversationContextResponse(
            channel=channel,
            conversation_external_id=conversation_external_id,
            conversation_status=None,
            message_count=0,
            recent_messages=[],
        )

    message_count = int(
        session.execute(
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conversation.id)
        ).scalar_one()
    )
    rows = session.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(limit)
    ).scalars()
    recent_messages = [
        InternalConversationMessageEntry(
            sender_type=row.sender_type,
            content=row.content,
            created_at=row.created_at,
        )
        for row in reversed(list(rows))
    ]

    return InternalConversationContextResponse(
        channel=channel,
        conversation_external_id=conversation_external_id,
        conversation_status=conversation.status,
        message_count=message_count,
        recent_messages=recent_messages,
    )
