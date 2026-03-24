from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from api_core.contracts import (
    InstitutionalRequestCreateResponse,
    InstitutionalRequestEntry,
    VisitBookingCreateResponse,
    VisitBookingEntry,
)
from api_core.db.models import Conversation, InstitutionalRequest, Message, VisitBooking
from api_core.services.support import build_ticket_code, create_support_handoff


def _generate_protocol_code(prefix: str) -> str:
    return f'{prefix}-{date.today():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}'


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


def _append_user_message_if_needed(session: Session, *, conversation_id: uuid.UUID, content: str) -> None:
    latest_message = session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if latest_message is not None and latest_message.sender_type == 'user' and latest_message.content == content:
        return
    session.add(
        Message(
            conversation_id=conversation_id,
            sender_type='user',
            content=content,
        )
    )


def _build_visit_summary(
    *,
    audience_name: str | None,
    interested_segment: str | None,
    preferred_date: date | None,
    preferred_window: str | None,
    attendee_count: int,
) -> str:
    requester = audience_name or 'Visitante'
    segment = interested_segment or 'segmento a confirmar'
    slot_parts: list[str] = []
    if preferred_date is not None:
        slot_parts.append(preferred_date.strftime('%d/%m/%Y'))
    if preferred_window:
        slot_parts.append(preferred_window)
    slot = ' - '.join(slot_parts) if slot_parts else 'janela a confirmar'
    return (
        f'{requester} solicitou visita institucional para {segment}. '
        f'Preferencia: {slot}. Participantes previstos: {max(attendee_count, 1)}.'
    )


def _queue_for_target_area(target_area: str) -> str:
    normalized = target_area.strip().lower()
    mapping = {
        'direcao': 'direcao',
        'diretoria': 'direcao',
        'direcao geral': 'direcao',
        'direção': 'direcao',
        'coordenacao': 'coordenacao',
        'coordenação': 'coordenacao',
        'financeiro': 'financeiro',
        'ouvidoria': 'atendimento',
        'secretaria': 'secretaria',
    }
    return mapping.get(normalized, 'atendimento')


def create_visit_booking(
    session: Session,
    *,
    actor_user_id: uuid.UUID | None,
    channel: str,
    conversation_external_id: str,
    audience_name: str | None,
    audience_contact: str | None,
    interested_segment: str | None,
    preferred_date: date | None,
    preferred_window: str | None,
    attendee_count: int,
    notes: str,
) -> VisitBookingCreateResponse:
    conversation = _resolve_or_create_conversation(
        session,
        channel=channel,
        conversation_external_id=conversation_external_id,
        actor_user_id=actor_user_id,
    )
    _append_user_message_if_needed(session, conversation_id=conversation.id, content=notes)

    handoff_response = create_support_handoff(
        session,
        actor_user_id=actor_user_id,
        channel=channel,
        conversation_external_id=conversation_external_id,
        queue_name='admissoes',
        summary=_build_visit_summary(
            audience_name=audience_name,
            interested_segment=interested_segment,
            preferred_date=preferred_date,
            preferred_window=preferred_window,
            attendee_count=attendee_count,
        ),
        user_message=notes,
    )

    linked_handoff_id = handoff_response.item.handoff_id
    booking = session.execute(
        select(VisitBooking)
        .where(VisitBooking.linked_handoff_id == linked_handoff_id)
        .order_by(VisitBooking.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    created = booking is None
    slot_label_parts: list[str] = []
    if preferred_date is not None:
        slot_label_parts.append(preferred_date.strftime('%d/%m/%Y'))
    if preferred_window:
        slot_label_parts.append(preferred_window)
    slot_label = ' - '.join(slot_label_parts) if slot_label_parts else None

    if booking is None:
        booking = VisitBooking(
            conversation_id=conversation.id,
            requester_user_id=actor_user_id,
            linked_handoff_id=linked_handoff_id,
            protocol_code=_generate_protocol_code('VIS'),
            status='requested',
            audience_name=audience_name,
            audience_contact=audience_contact,
            interested_segment=interested_segment,
            preferred_date=preferred_date,
            preferred_window=preferred_window,
            attendee_count=max(attendee_count, 1),
            slot_label=slot_label,
            notes=notes,
        )
        session.add(booking)
    else:
        booking.requester_user_id = actor_user_id or booking.requester_user_id
        booking.audience_name = audience_name
        booking.audience_contact = audience_contact
        booking.interested_segment = interested_segment
        booking.preferred_date = preferred_date
        booking.preferred_window = preferred_window
        booking.attendee_count = max(attendee_count, 1)
        booking.slot_label = slot_label
        booking.notes = notes

    session.flush()
    return VisitBookingCreateResponse(
        created=created,
        item=VisitBookingEntry(
            booking_id=booking.id,
            protocol_code=booking.protocol_code,
            status=booking.status,
            queue_name='admissoes',
            linked_ticket_code=handoff_response.item.ticket_code,
            audience_name=booking.audience_name,
            interested_segment=booking.interested_segment,
            preferred_date=booking.preferred_date,
            preferred_window=booking.preferred_window,
            slot_label=booking.slot_label,
            created_at=booking.created_at,
        ),
    )


def create_institutional_request(
    session: Session,
    *,
    actor_user_id: uuid.UUID | None,
    channel: str,
    conversation_external_id: str,
    target_area: str,
    category: str,
    subject: str,
    details: str,
    requester_contact: str | None,
) -> InstitutionalRequestCreateResponse:
    conversation = _resolve_or_create_conversation(
        session,
        channel=channel,
        conversation_external_id=conversation_external_id,
        actor_user_id=actor_user_id,
    )
    _append_user_message_if_needed(session, conversation_id=conversation.id, content=details)

    queue_name = _queue_for_target_area(target_area)
    handoff_response = create_support_handoff(
        session,
        actor_user_id=actor_user_id,
        channel=channel,
        conversation_external_id=conversation_external_id,
        queue_name=queue_name,
        summary=f'Solicitacao institucional para {target_area}: {subject}',
        user_message=details,
    )

    linked_handoff_id = handoff_response.item.handoff_id
    institutional_request = session.execute(
        select(InstitutionalRequest)
        .where(InstitutionalRequest.linked_handoff_id == linked_handoff_id)
        .order_by(InstitutionalRequest.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    created = institutional_request is None
    if institutional_request is None:
        institutional_request = InstitutionalRequest(
            conversation_id=conversation.id,
            requester_user_id=actor_user_id,
            linked_handoff_id=linked_handoff_id,
            protocol_code=_generate_protocol_code('REQ'),
            target_area=target_area,
            category=category,
            subject=subject,
            details=details,
            requester_contact=requester_contact,
            status='queued',
        )
        session.add(institutional_request)
    else:
        institutional_request.requester_user_id = actor_user_id or institutional_request.requester_user_id
        institutional_request.target_area = target_area
        institutional_request.category = category
        institutional_request.subject = subject
        institutional_request.details = details
        institutional_request.requester_contact = requester_contact

    session.flush()
    return InstitutionalRequestCreateResponse(
        created=created,
        item=InstitutionalRequestEntry(
            request_id=institutional_request.id,
            protocol_code=institutional_request.protocol_code,
            target_area=institutional_request.target_area,
            category=institutional_request.category,
            subject=institutional_request.subject,
            status=institutional_request.status,
            queue_name=queue_name,
            linked_ticket_code=handoff_response.item.ticket_code,
            created_at=institutional_request.created_at,
        ),
    )
