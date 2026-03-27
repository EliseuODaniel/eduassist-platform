from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api_core.contracts import (
    InternalConversationAppendResponse,
    InternalConversationToolCallAppendResponse,
    InternalConversationToolCallCreate,
    InternalConversationContextResponse,
    InternalConversationMessageCreate,
    InternalConversationMessageEntry,
    InternalConversationToolCallEntry,
)
from api_core.db.models import Conversation, Message, ToolCall


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

    incoming_batch = [
        (payload.sender_type, payload.content)
        for payload in messages
    ]
    if incoming_batch:
        latest_rows = session.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(len(incoming_batch))
        ).scalars()
        latest_batch = [
            (row.sender_type, row.content)
            for row in reversed(list(latest_rows))
        ]
        if len(latest_batch) == len(incoming_batch) and sorted(latest_batch) == sorted(incoming_batch):
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
                stored_messages=0,
                deduplicated_messages=len(incoming_batch),
                message_count=message_count,
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


def append_conversation_tool_calls(
    session: Session,
    *,
    channel: str,
    conversation_external_id: str,
    actor_user_id: uuid.UUID | None,
    tool_calls: list[InternalConversationToolCallCreate],
) -> InternalConversationToolCallAppendResponse:
    conversation = _resolve_or_create_conversation(
        session,
        channel=channel,
        conversation_external_id=conversation_external_id,
        actor_user_id=actor_user_id,
    )

    stored_tool_calls = 0
    for payload in tool_calls:
        session.add(
            ToolCall(
                conversation_id=conversation.id,
                tool_name=payload.tool_name,
                status=payload.status,
                request_payload=payload.request_payload,
                response_payload=payload.response_payload,
            )
        )
        stored_tool_calls += 1

    conversation.status = 'open'
    session.flush()

    return InternalConversationToolCallAppendResponse(
        channel=channel,
        conversation_external_id=conversation_external_id,
        stored_tool_calls=stored_tool_calls,
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
            recent_tool_calls=[],
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
    tool_call_rows = session.execute(
        select(ToolCall)
        .where(ToolCall.conversation_id == conversation.id)
        .order_by(ToolCall.created_at.desc(), ToolCall.id.desc())
        .limit(limit)
    ).scalars()
    recent_tool_calls = [
        InternalConversationToolCallEntry(
            tool_name=row.tool_name,
            status=row.status,
            request_payload=row.request_payload if isinstance(row.request_payload, dict) else {},
            response_payload=row.response_payload if isinstance(row.response_payload, dict) else {},
            created_at=row.created_at,
        )
        for row in reversed(list(tool_call_rows))
    ]

    return InternalConversationContextResponse(
        channel=channel,
        conversation_external_id=conversation_external_id,
        conversation_status=conversation.status,
        message_count=message_count,
        recent_messages=recent_messages,
        recent_tool_calls=recent_tool_calls,
    )
