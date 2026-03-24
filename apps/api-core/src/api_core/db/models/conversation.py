from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api_core.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Conversation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'conversations'
    __table_args__ = {'schema': 'conversation'}

    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('identity.users.id'))
    channel: Mapped[str] = mapped_column(String(30), nullable=False)
    external_thread_id: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='open', nullable=False)


class Message(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'messages'
    __table_args__ = {'schema': 'conversation'}

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('conversation.conversations.id'),
        nullable=False,
    )
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)


class ToolCall(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'tool_calls'
    __table_args__ = {'schema': 'conversation'}

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('conversation.conversations.id'),
        nullable=False,
    )
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    request_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    response_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Handoff(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'handoffs'
    __table_args__ = {'schema': 'conversation'}

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('conversation.conversations.id'),
        nullable=False,
    )
    queue_name: Mapped[str] = mapped_column(String(60), nullable=False)
    priority_code: Mapped[str] = mapped_column(String(20), default='standard', nullable=False)
    assigned_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('identity.users.id'),
    )
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    response_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)


class VisitBooking(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'visit_bookings'
    __table_args__ = {'schema': 'conversation'}

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('conversation.conversations.id'),
        nullable=False,
    )
    requester_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('identity.users.id'),
    )
    linked_handoff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('conversation.handoffs.id'),
    )
    protocol_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default='requested', nullable=False)
    audience_name: Mapped[str | None] = mapped_column(String(160))
    audience_contact: Mapped[str | None] = mapped_column(String(255))
    interested_segment: Mapped[str | None] = mapped_column(String(80))
    preferred_date: Mapped[date | None] = mapped_column(Date)
    preferred_window: Mapped[str | None] = mapped_column(String(80))
    attendee_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    slot_label: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str] = mapped_column(Text, nullable=False)


class InstitutionalRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'institutional_requests'
    __table_args__ = {'schema': 'conversation'}

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('conversation.conversations.id'),
        nullable=False,
    )
    requester_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('identity.users.id'),
    )
    linked_handoff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('conversation.handoffs.id'),
    )
    protocol_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    target_area: Mapped[str] = mapped_column(String(60), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    subject: Mapped[str] = mapped_column(String(160), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    requester_contact: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default='queued', nullable=False)
