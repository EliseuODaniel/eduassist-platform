from __future__ import annotations

import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api_core.contracts import (
    InternalWorkflowStatusResponse,
    InstitutionalRequestActionResponse,
    InstitutionalRequestCreateResponse,
    InstitutionalRequestEntry,
    VisitBookingActionResponse,
    VisitBookingCreateResponse,
    VisitBookingEntry,
    WorkflowStatusEntry,
)
from api_core.db.models import Conversation, Handoff, InstitutionalRequest, Message, VisitBooking
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


def _resolve_visit_booking(
    session: Session,
    *,
    channel: str,
    conversation_external_id: str,
    protocol_code: str | None,
) -> VisitBooking | None:
    normalized_protocol = protocol_code.strip().upper() if protocol_code else None
    if normalized_protocol:
        return session.execute(
            select(VisitBooking)
            .where(VisitBooking.protocol_code == normalized_protocol)
            .order_by(VisitBooking.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()

    conversation = session.execute(
        select(Conversation)
        .where(Conversation.channel == channel)
        .where(Conversation.external_thread_id == conversation_external_id)
        .order_by(Conversation.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    if conversation is None:
        return None
    return session.execute(
        select(VisitBooking)
        .where(VisitBooking.conversation_id == conversation.id)
        .order_by(VisitBooking.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()


def update_visit_booking(
    session: Session,
    *,
    channel: str,
    conversation_external_id: str,
    protocol_code: str | None,
    action: str,
    preferred_date: date | None,
    preferred_window: str | None,
    notes: str | None,
) -> VisitBookingActionResponse:
    booking = _resolve_visit_booking(
        session,
        channel=channel,
        conversation_external_id=conversation_external_id,
        protocol_code=protocol_code,
    )
    if booking is None:
        raise HTTPException(status_code=404, detail='visit_booking_not_found')

    normalized_action = action.strip().lower()
    if normalized_action not in {'reschedule', 'cancel'}:
        raise HTTPException(status_code=422, detail='unsupported_visit_booking_action')

    handoff = session.get(Handoff, booking.linked_handoff_id) if booking.linked_handoff_id else None

    if normalized_action == 'cancel':
        booking.status = 'cancelled'
        if notes:
            booking.notes = notes.strip()
        if handoff is not None and handoff.status not in {'resolved', 'cancelled'}:
            handoff.status = 'cancelled'
        session.flush()
        return VisitBookingActionResponse(
            action='cancel',
            item=VisitBookingEntry(
                booking_id=booking.id,
                protocol_code=booking.protocol_code,
                status=booking.status,
                queue_name=handoff.queue_name if handoff is not None else 'admissoes',
                linked_ticket_code=_ticket_code_or_none(handoff),
                audience_name=booking.audience_name,
                interested_segment=booking.interested_segment,
                preferred_date=booking.preferred_date,
                preferred_window=booking.preferred_window,
                slot_label=booking.slot_label,
                created_at=booking.created_at,
            ),
        )

    if preferred_date is None and not preferred_window:
        raise HTTPException(status_code=422, detail='visit_booking_reschedule_requires_slot')

    booking.status = 'requested'
    if preferred_date is not None:
        booking.preferred_date = preferred_date
    if preferred_window:
        booking.preferred_window = preferred_window
    slot_label_parts: list[str] = []
    if booking.preferred_date is not None:
        slot_label_parts.append(booking.preferred_date.strftime('%d/%m/%Y'))
    if booking.preferred_window:
        slot_label_parts.append(booking.preferred_window)
    booking.slot_label = ' - '.join(slot_label_parts) if slot_label_parts else None
    if notes:
        booking.notes = notes.strip()

    if handoff is not None:
        handoff.status = 'queued'
        handoff.summary = _build_visit_summary(
            audience_name=booking.audience_name,
            interested_segment=booking.interested_segment,
            preferred_date=booking.preferred_date,
            preferred_window=booking.preferred_window,
            attendee_count=booking.attendee_count,
        )
    session.flush()
    return VisitBookingActionResponse(
        action='reschedule',
        item=VisitBookingEntry(
            booking_id=booking.id,
            protocol_code=booking.protocol_code,
            status=booking.status,
            queue_name=handoff.queue_name if handoff is not None else 'admissoes',
            linked_ticket_code=_ticket_code_or_none(handoff),
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


def _resolve_institutional_request(
    session: Session,
    *,
    channel: str,
    conversation_external_id: str,
    protocol_code: str | None,
) -> InstitutionalRequest | None:
    normalized_protocol = protocol_code.strip().upper() if protocol_code else None
    if normalized_protocol:
        return session.execute(
            select(InstitutionalRequest)
            .where(InstitutionalRequest.protocol_code == normalized_protocol)
            .order_by(InstitutionalRequest.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()

    conversation = session.execute(
        select(Conversation)
        .where(Conversation.channel == channel)
        .where(Conversation.external_thread_id == conversation_external_id)
        .order_by(Conversation.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    if conversation is None:
        return None
    return session.execute(
        select(InstitutionalRequest)
        .where(InstitutionalRequest.conversation_id == conversation.id)
        .order_by(InstitutionalRequest.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()


def update_institutional_request(
    session: Session,
    *,
    channel: str,
    conversation_external_id: str,
    protocol_code: str | None,
    action: str,
    details: str | None,
) -> InstitutionalRequestActionResponse:
    institutional_request = _resolve_institutional_request(
        session,
        channel=channel,
        conversation_external_id=conversation_external_id,
        protocol_code=protocol_code,
    )
    if institutional_request is None:
        raise HTTPException(status_code=404, detail='institutional_request_not_found')

    normalized_action = action.strip().lower()
    if normalized_action != 'append_note':
        raise HTTPException(status_code=422, detail='unsupported_institutional_request_action')

    detail_text = (details or '').strip()
    if not detail_text:
        raise HTTPException(status_code=422, detail='institutional_request_append_requires_details')

    complement_prefix = 'Complemento registrado'
    if complement_prefix.lower() not in institutional_request.details.lower():
        institutional_request.details = f'{institutional_request.details}\n\n{complement_prefix}: {detail_text}'.strip()
    else:
        institutional_request.details = f'{institutional_request.details}\n{complement_prefix}: {detail_text}'.strip()
    institutional_request.status = 'queued'

    handoff = (
        session.get(Handoff, institutional_request.linked_handoff_id)
        if institutional_request.linked_handoff_id
        else None
    )
    if handoff is not None:
        handoff.status = 'queued'
        handoff.summary = (
            f'Solicitacao institucional para {institutional_request.target_area}: {institutional_request.subject}. '
            f'Complemento: {detail_text}'
        )

    session.flush()
    return InstitutionalRequestActionResponse(
        action='append_note',
        item=InstitutionalRequestEntry(
            request_id=institutional_request.id,
            protocol_code=institutional_request.protocol_code,
            target_area=institutional_request.target_area,
            category=institutional_request.category,
            subject=institutional_request.subject,
            status=_effective_status(own_status=institutional_request.status, handoff=handoff),
            queue_name=handoff.queue_name if handoff is not None else institutional_request.target_area.lower(),
            linked_ticket_code=_ticket_code_or_none(handoff),
            created_at=institutional_request.created_at,
        ),
    )


def _ticket_code_or_none(handoff: Handoff | None) -> str | None:
    if handoff is None:
        return None
    return build_ticket_code(handoff_id=handoff.id, created_at=handoff.created_at)


def _effective_status(*, own_status: str, handoff: Handoff | None) -> str:
    if handoff is not None and handoff.status:
        return handoff.status
    return own_status


def _workflow_entry_from_visit(booking: VisitBooking, handoff: Handoff | None) -> WorkflowStatusEntry:
    return WorkflowStatusEntry(
        workflow_type='visit_booking',
        protocol_code=booking.protocol_code,
        status=_effective_status(own_status=booking.status, handoff=handoff),
        queue_name=handoff.queue_name if handoff is not None else 'admissoes',
        linked_ticket_code=_ticket_code_or_none(handoff),
        subject='Visita institucional',
        summary=booking.notes,
        preferred_date=booking.preferred_date,
        preferred_window=booking.preferred_window,
        slot_label=booking.slot_label,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


def _workflow_entry_from_request(
    institutional_request: InstitutionalRequest,
    handoff: Handoff | None,
) -> WorkflowStatusEntry:
    return WorkflowStatusEntry(
        workflow_type='institutional_request',
        protocol_code=institutional_request.protocol_code,
        status=_effective_status(own_status=institutional_request.status, handoff=handoff),
        queue_name=handoff.queue_name if handoff is not None else institutional_request.target_area.lower(),
        linked_ticket_code=_ticket_code_or_none(handoff),
        subject=institutional_request.subject,
        summary=institutional_request.details,
        target_area=institutional_request.target_area,
        created_at=institutional_request.created_at,
        updated_at=institutional_request.updated_at,
    )


def _workflow_entry_from_handoff(handoff: Handoff) -> WorkflowStatusEntry:
    return WorkflowStatusEntry(
        workflow_type='support_handoff',
        protocol_code=build_ticket_code(handoff_id=handoff.id, created_at=handoff.created_at),
        status=handoff.status,
        queue_name=handoff.queue_name,
        linked_ticket_code=build_ticket_code(handoff_id=handoff.id, created_at=handoff.created_at),
        subject='Atendimento institucional',
        summary=handoff.summary,
        created_at=handoff.created_at,
        updated_at=handoff.updated_at,
    )


def _match_handoff_by_ticket_code(session: Session, *, ticket_code: str) -> Handoff | None:
    rows = session.execute(select(Handoff).order_by(Handoff.created_at.desc())).scalars()
    for handoff in rows:
        if build_ticket_code(handoff_id=handoff.id, created_at=handoff.created_at) == ticket_code:
            return handoff
    return None


def _latest_workflow_candidates(
    session: Session,
    *,
    conversation_id,
    workflow_kind: str | None,
) -> list[tuple[object, Handoff | None, int]]:
    candidates: list[tuple[object, Handoff | None, int]] = []

    if workflow_kind in {None, 'visit_booking'}:
        booking = session.execute(
            select(VisitBooking)
            .where(VisitBooking.conversation_id == conversation_id)
            .order_by(VisitBooking.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()
        if booking is not None:
            handoff = session.get(Handoff, booking.linked_handoff_id) if booking.linked_handoff_id else None
            candidates.append((booking, handoff, 3))

    if workflow_kind in {None, 'institutional_request'}:
        institutional_request = session.execute(
            select(InstitutionalRequest)
            .where(InstitutionalRequest.conversation_id == conversation_id)
            .order_by(InstitutionalRequest.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()
        if institutional_request is not None:
            handoff = (
                session.get(Handoff, institutional_request.linked_handoff_id)
                if institutional_request.linked_handoff_id
                else None
            )
            candidates.append((institutional_request, handoff, 2))

    if workflow_kind in {None, 'support_handoff'}:
        handoff = session.execute(
            select(Handoff)
            .where(Handoff.conversation_id == conversation_id)
            .order_by(Handoff.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()
        if handoff is not None:
            candidates.append((handoff, None, 1))

    return candidates


def get_workflow_status(
    session: Session,
    *,
    channel: str,
    conversation_external_id: str,
    protocol_code: str | None = None,
    workflow_kind: str | None = None,
) -> InternalWorkflowStatusResponse:
    normalized_protocol = protocol_code.strip().upper() if protocol_code else None
    normalized_kind = workflow_kind.strip().lower() if workflow_kind else None

    if normalized_protocol:
        if normalized_protocol.startswith('VIS-'):
            booking = session.execute(
                select(VisitBooking)
                .where(VisitBooking.protocol_code == normalized_protocol)
                .order_by(VisitBooking.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()
            if booking is None:
                return InternalWorkflowStatusResponse(found=False)
            handoff = session.get(Handoff, booking.linked_handoff_id) if booking.linked_handoff_id else None
            return InternalWorkflowStatusResponse(found=True, item=_workflow_entry_from_visit(booking, handoff))

        if normalized_protocol.startswith('REQ-'):
            institutional_request = session.execute(
                select(InstitutionalRequest)
                .where(InstitutionalRequest.protocol_code == normalized_protocol)
                .order_by(InstitutionalRequest.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()
            if institutional_request is None:
                return InternalWorkflowStatusResponse(found=False)
            handoff = (
                session.get(Handoff, institutional_request.linked_handoff_id)
                if institutional_request.linked_handoff_id
                else None
            )
            return InternalWorkflowStatusResponse(
                found=True,
                item=_workflow_entry_from_request(institutional_request, handoff),
            )

        if normalized_protocol.startswith('ATD-'):
            handoff = _match_handoff_by_ticket_code(session, ticket_code=normalized_protocol)
            if handoff is None:
                return InternalWorkflowStatusResponse(found=False)
            return InternalWorkflowStatusResponse(found=True, item=_workflow_entry_from_handoff(handoff))

    conversation = session.execute(
        select(Conversation)
        .where(Conversation.channel == channel)
        .where(Conversation.external_thread_id == conversation_external_id)
        .order_by(Conversation.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    if conversation is None:
        return InternalWorkflowStatusResponse(found=False)

    candidates = _latest_workflow_candidates(
        session,
        conversation_id=conversation.id,
        workflow_kind=normalized_kind,
    )
    if not candidates:
        return InternalWorkflowStatusResponse(found=False)

    latest_item, latest_handoff, _ = max(
        candidates,
        key=lambda item: (item[0].created_at, item[2]),
    )
    if isinstance(latest_item, VisitBooking):
        return InternalWorkflowStatusResponse(found=True, item=_workflow_entry_from_visit(latest_item, latest_handoff))
    if isinstance(latest_item, InstitutionalRequest):
        return InternalWorkflowStatusResponse(
            found=True,
            item=_workflow_entry_from_request(latest_item, latest_handoff),
        )
    return InternalWorkflowStatusResponse(found=True, item=_workflow_entry_from_handoff(latest_item))
