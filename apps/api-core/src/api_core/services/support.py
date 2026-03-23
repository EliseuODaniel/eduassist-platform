from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from math import ceil
from time import monotonic

from eduassist_observability import record_counter, record_histogram, set_span_attributes, start_span
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from api_core.contracts import (
    ActorContext,
    SupportConversationMessageEntry,
    SupportHandoffCreateResponse,
    SupportHandoffEntry,
    SupportHandoffFilters,
    SupportHandoffPagination,
)
from api_core.db.models import Conversation, Handoff, Message, User

INTERNAL_OPERATOR_ROLES = frozenset({'staff', 'finance', 'coordinator', 'admin'})
OPEN_HANDOFF_STATUSES = frozenset({'queued', 'in_progress'})
SUPPORTED_HANDOFF_STATUSES = frozenset({'queued', 'in_progress', 'resolved', 'cancelled'})
SUPPORTED_HANDOFF_ASSIGNMENTS = frozenset({'mine', 'unassigned', 'assigned'})
SUPPORTED_HANDOFF_SLA_STATES = frozenset({'on_track', 'attention', 'breached', 'closed', 'unknown'})


def build_ticket_code(*, handoff_id: uuid.UUID, created_at) -> str:
    return f'ATD-{created_at:%Y%m%d}-{str(handoff_id).split("-")[0].upper()}'


def resolve_support_scope(actor: ActorContext) -> str:
    if actor.role_code in INTERNAL_OPERATOR_ROLES:
        return 'global'
    return 'self'


def _truncate_excerpt(text: str | None, *, limit: int = 180) -> str | None:
    if not text:
        return None
    compact = ' '.join(text.split())
    if len(compact) <= limit:
        return compact
    return f'{compact[: limit - 1].rstrip()}...'


def _priority_for_queue(queue_name: str) -> str:
    normalized = queue_name.strip().lower()
    priorities = {
        'coordenacao': 'high',
        'financeiro': 'high',
        'secretaria': 'standard',
        'atendimento': 'standard',
    }
    return priorities.get(normalized, 'standard')


def _sla_deadlines(*, priority_code: str, anchor: datetime) -> tuple[datetime, datetime]:
    if priority_code == 'urgent':
        return anchor + timedelta(minutes=30), anchor + timedelta(hours=4)
    if priority_code == 'high':
        return anchor + timedelta(hours=1), anchor + timedelta(hours=8)
    return anchor + timedelta(hours=4), anchor + timedelta(hours=24)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def calculate_handoff_sla_state(handoff: Handoff) -> str:
    if handoff.status in {'resolved', 'cancelled'}:
        return 'closed'

    now = datetime.now(timezone.utc)
    started_at = _as_utc(handoff.created_at)
    target = _as_utc(handoff.response_due_at if handoff.status == 'queued' else handoff.resolution_due_at)
    if target is None:
        return 'unknown'

    remaining = target - now
    if remaining <= timedelta(0):
        return 'breached'

    if started_at is None:
        return 'attention' if remaining <= timedelta(minutes=30) else 'on_track'

    total_window = target - started_at
    if total_window > timedelta(0) and remaining <= total_window / 4:
        return 'attention'
    return 'on_track'


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
    rows: list[tuple[Handoff, Conversation, str | None, str | None, str | None, str | None]],
) -> list[SupportHandoffEntry]:
    conversation_ids = [conversation.id for _, conversation, _, _, _, _ in rows]
    latest_messages = _load_latest_user_messages(session, conversation_ids=conversation_ids)

    return [
        SupportHandoffEntry(
            handoff_id=handoff.id,
            conversation_id=conversation.id,
            ticket_code=build_ticket_code(handoff_id=handoff.id, created_at=handoff.created_at),
            channel=conversation.channel,
            external_thread_id=conversation.external_thread_id,
            queue_name=handoff.queue_name,
            priority_code=handoff.priority_code,
            status=handoff.status,
            summary=handoff.summary,
            requester_name=requester_name,
            requester_role=requester_role,
            assigned_user_id=handoff.assigned_user_id,
            assigned_operator_name=assigned_operator_name,
            assigned_operator_external_code=assigned_operator_external_code,
            assigned_at=handoff.assigned_at,
            response_due_at=handoff.response_due_at,
            resolution_due_at=handoff.resolution_due_at,
            sla_state=calculate_handoff_sla_state(handoff),
            last_message_excerpt=_truncate_excerpt(latest_messages.get(conversation.id)),
            created_at=handoff.created_at,
            updated_at=handoff.updated_at,
        )
        for (
            handoff,
            conversation,
            requester_name,
            requester_role,
            assigned_operator_name,
            assigned_operator_external_code,
        ) in rows
    ]


def normalize_support_handoff_filters(filters: SupportHandoffFilters) -> SupportHandoffFilters:
    status = filters.status.strip().lower() if filters.status else None
    if status not in SUPPORTED_HANDOFF_STATUSES:
        status = None

    queue_name = filters.queue_name.strip().lower() if filters.queue_name else None
    if queue_name == '':
        queue_name = None

    assignment = filters.assignment.strip().lower() if filters.assignment else None
    if assignment not in SUPPORTED_HANDOFF_ASSIGNMENTS:
        assignment = None

    sla_state = filters.sla_state.strip().lower() if filters.sla_state else None
    if sla_state not in SUPPORTED_HANDOFF_SLA_STATES:
        sla_state = None

    search = ' '.join(filters.search.split()) if filters.search else None
    if not search:
        search = None

    page = max(1, int(filters.page or 1))
    limit = max(1, min(int(filters.limit or 10), 25))
    return SupportHandoffFilters(
        status=status,
        queue_name=queue_name,
        assignment=assignment,
        sla_state=sla_state,
        search=search,
        page=page,
        limit=limit,
    )


def _matches_handoff_filters(
    item: SupportHandoffEntry,
    *,
    actor: ActorContext,
    filters: SupportHandoffFilters,
) -> bool:
    if filters.status and item.status != filters.status:
        return False

    if filters.queue_name and item.queue_name != filters.queue_name:
        return False

    if filters.assignment == 'mine' and item.assigned_user_id != actor.user_id:
        return False
    if filters.assignment == 'unassigned' and item.assigned_user_id is not None:
        return False
    if filters.assignment == 'assigned' and item.assigned_user_id is None:
        return False

    if filters.sla_state and item.sla_state != filters.sla_state:
        return False

    if filters.search:
        haystack = ' '.join(
            value
            for value in [
                item.ticket_code,
                item.summary,
                item.requester_name or '',
                item.assigned_operator_name or '',
                item.last_message_excerpt or '',
            ]
            if value
        ).lower()
        if filters.search.lower() not in haystack:
            return False

    return True


def _base_handoff_stmt(*, actor: ActorContext, scope: str):
    requester = aliased(User)
    assignee = aliased(User)
    stmt = (
        select(
            Handoff,
            Conversation,
            requester.full_name,
            requester.role_code,
            assignee.full_name,
            assignee.external_code,
        )
        .join(Conversation, Conversation.id == Handoff.conversation_id)
        .outerjoin(requester, requester.id == Conversation.user_id)
        .outerjoin(assignee, assignee.id == Handoff.assigned_user_id)
    )

    if scope == 'self':
        stmt = stmt.where(Conversation.user_id == actor.user_id)
    return stmt


def list_support_handoffs(
    session: Session,
    *,
    actor: ActorContext,
    scope: str,
    filters: SupportHandoffFilters,
) -> tuple[dict[str, int], list[SupportHandoffEntry], SupportHandoffFilters, SupportHandoffPagination]:
    with start_span(
        'eduassist.support.list_handoffs',
        tracer_name='eduassist.api_core.support',
        **{
            'eduassist.actor.role': actor.role_code,
            'eduassist.support.scope': scope,
        },
    ):
        normalized_filters = normalize_support_handoff_filters(filters)
        set_span_attributes(
            **{
                'eduassist.support.filter.status': normalized_filters.status,
                'eduassist.support.filter.queue': normalized_filters.queue_name,
                'eduassist.support.filter.assignment': normalized_filters.assignment,
                'eduassist.support.filter.sla_state': normalized_filters.sla_state,
                'eduassist.support.filter.search_present': normalized_filters.search is not None,
                'eduassist.support.page': normalized_filters.page,
                'eduassist.support.limit': normalized_filters.limit,
            }
        )
        rows = session.execute(
            _base_handoff_stmt(actor=actor, scope=scope).order_by(Handoff.updated_at.desc(), Handoff.created_at.desc())
        ).all()

        items = _serialize_handoff_rows(session, rows)
        filtered_items = [
            item for item in items if _matches_handoff_filters(item, actor=actor, filters=normalized_filters)
        ]
        counts = {
            status: sum(1 for item in filtered_items if item.status == status)
            for status in SUPPORTED_HANDOFF_STATUSES
        }
        total_items = len(filtered_items)
        total_pages = max(1, ceil(total_items / normalized_filters.limit)) if total_items > 0 else 1
        effective_page = min(normalized_filters.page, total_pages)
        start = (effective_page - 1) * normalized_filters.limit
        end = start + normalized_filters.limit
        paged_items = filtered_items[start:end]
        visible_from = start + 1 if total_items > 0 and paged_items else 0
        visible_to = start + len(paged_items) if paged_items else 0
        pagination = SupportHandoffPagination(
            page=effective_page,
            page_size=normalized_filters.limit,
            total_items=total_items,
            total_pages=total_pages,
            has_previous_page=effective_page > 1,
            has_next_page=effective_page < total_pages,
            visible_from=visible_from,
            visible_to=visible_to,
        )
        normalized_filters = SupportHandoffFilters(
            status=normalized_filters.status,
            queue_name=normalized_filters.queue_name,
            assignment=normalized_filters.assignment,
            sla_state=normalized_filters.sla_state,
            search=normalized_filters.search,
            page=effective_page,
            limit=normalized_filters.limit,
        )
        set_span_attributes(
            **{
                'eduassist.support.total_rows': len(rows),
                'eduassist.support.result_count': total_items,
                'eduassist.support.page_result_count': len(paged_items),
                'eduassist.support.result_statuses': [status for status, count in counts.items() if count > 0],
                'eduassist.support.total_pages': total_pages,
            }
        )
        return counts, paged_items, normalized_filters, pagination


def get_support_handoff_detail(
    session: Session,
    *,
    actor: ActorContext,
    scope: str,
    handoff_id: uuid.UUID,
) -> tuple[SupportHandoffEntry, str, list[SupportConversationMessageEntry]] | None:
    with start_span(
        'eduassist.support.get_handoff_detail',
        tracer_name='eduassist.api_core.support',
        **{
            'eduassist.actor.role': actor.role_code,
            'eduassist.support.scope': scope,
            'eduassist.support.handoff_id': handoff_id,
        },
    ):
        row = session.execute(
            _base_handoff_stmt(actor=actor, scope=scope).where(Handoff.id == handoff_id)
        ).first()
        if row is None:
            set_span_attributes(**{'eduassist.support.found': False})
            return None

        handoff, conversation, requester_name, requester_role, assigned_name, assigned_code = row
        item = _serialize_handoff_rows(
            session,
            [(handoff, conversation, requester_name, requester_role, assigned_name, assigned_code)],
        )[0]
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
        set_span_attributes(
            **{
                'eduassist.support.found': True,
                'eduassist.support.status': conversation.status,
                'eduassist.support.message_count': len(messages),
                'eduassist.queue.name': item.queue_name,
                'eduassist.support.sla_state': item.sla_state,
            }
        )
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
    started_at = monotonic()
    with start_span(
        'eduassist.support.create_handoff',
        tracer_name='eduassist.api_core.support',
        **{
            'eduassist.channel': channel,
            'eduassist.queue.name': queue_name,
            'eduassist.support.has_actor': actor_user_id is not None,
            'eduassist.support.has_user_message': bool(user_message),
        },
    ):
        conversation = session.execute(
            select(Conversation)
            .where(Conversation.channel == channel)
            .where(Conversation.external_thread_id == conversation_external_id)
            .order_by(Conversation.created_at.desc())
        ).scalar_one_or_none()

        reused_conversation = conversation is not None
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

        priority_code = _priority_for_queue(queue_name)
        created = handoff is None
        if handoff is None:
            handoff = Handoff(
                conversation_id=conversation.id,
                queue_name=queue_name,
                priority_code=priority_code,
                status='queued',
                summary=summary,
            )
            session.add(handoff)
            session.flush()
            response_due_at, resolution_due_at = _sla_deadlines(
                priority_code=priority_code,
                anchor=handoff.created_at,
            )
            handoff.response_due_at = response_due_at
            handoff.resolution_due_at = resolution_due_at
        else:
            handoff.queue_name = queue_name
            handoff.priority_code = priority_code
            handoff.summary = summary
            if handoff.response_due_at is None or handoff.resolution_due_at is None:
                response_due_at, resolution_due_at = _sla_deadlines(
                    priority_code=priority_code,
                    anchor=handoff.created_at,
                )
                handoff.response_due_at = response_due_at
                handoff.resolution_due_at = resolution_due_at

        conversation.status = 'open'
        session.flush()

        requester = session.execute(
            select(User.full_name, User.role_code).where(User.id == conversation.user_id)
        ).first()
        requester_name = requester[0] if requester else None
        requester_role = requester[1] if requester else None
        assignee = session.execute(
            select(User.full_name, User.external_code).where(User.id == handoff.assigned_user_id)
        ).first()
        assigned_name = assignee[0] if assignee else None
        assigned_code = assignee[1] if assignee else None

        item = _serialize_handoff_rows(
            session,
            [(handoff, conversation, requester_name, requester_role, assigned_name, assigned_code)],
        )[0]
        set_span_attributes(
            **{
                'eduassist.support.created': created,
                'eduassist.support.deduplicated': not created,
                'eduassist.support.conversation_reused': reused_conversation,
                'eduassist.support.status': item.status,
                'eduassist.support.priority': item.priority_code,
                'eduassist.support.sla_state': item.sla_state,
            }
        )
        metric_attributes = {
            'event': 'created' if created else 'deduplicated',
            'queue_name': item.queue_name,
            'priority': item.priority_code,
            'status': item.status,
            'channel': channel,
        }
        record_counter(
            'eduassist_support_handoff_events',
            attributes=metric_attributes,
            description='Support handoff lifecycle events.',
        )
        record_histogram(
            'eduassist_support_handoff_latency_ms',
            (monotonic() - started_at) * 1000,
            attributes={'operation': 'create', 'queue_name': item.queue_name},
            description='Latency of support handoff operations in milliseconds.',
        )
        return SupportHandoffCreateResponse(created=created, deduplicated=not created, item=item)


def update_support_handoff_status(
    session: Session,
    *,
    handoff_id: uuid.UUID,
    actor_user_id: uuid.UUID | None,
    status: str | None = None,
    operator_note: str | None = None,
    assigned_user_id: uuid.UUID | None = None,
    clear_assignment: bool = False,
) -> SupportHandoffEntry | None:
    started_at = monotonic()
    with start_span(
        'eduassist.support.update_handoff',
        tracer_name='eduassist.api_core.support',
        **{
            'eduassist.support.handoff_id': handoff_id,
            'eduassist.support.requested_status': status,
            'eduassist.support.has_operator_note': bool(operator_note),
            'eduassist.support.clear_assignment': clear_assignment,
            'eduassist.support.assigned_user_requested': assigned_user_id is not None,
        },
    ):
        if status is not None and status not in SUPPORTED_HANDOFF_STATUSES:
            raise ValueError('unsupported_handoff_status')
        if assigned_user_id is not None and clear_assignment:
            raise ValueError('conflicting_assignment_change')
        if status is None and not operator_note and assigned_user_id is None and not clear_assignment:
            raise ValueError('empty_handoff_update')

        requester = aliased(User)
        assignee_alias = aliased(User)
        row = session.execute(
            select(
                Handoff,
                Conversation,
                requester.full_name,
                requester.role_code,
                assignee_alias.full_name,
                assignee_alias.external_code,
            )
            .join(Conversation, Conversation.id == Handoff.conversation_id)
            .outerjoin(requester, requester.id == Conversation.user_id)
            .outerjoin(assignee_alias, assignee_alias.id == Handoff.assigned_user_id)
            .where(Handoff.id == handoff_id)
        ).first()
        if row is None:
            set_span_attributes(**{'eduassist.support.found': False})
            return None

        handoff, conversation, requester_name, requester_role, assigned_name, assigned_code = row

        if clear_assignment:
            handoff.assigned_user_id = None
            handoff.assigned_at = None
        elif assigned_user_id is not None:
            assignee = session.get(User, assigned_user_id)
            if assignee is None or assignee.role_code not in INTERNAL_OPERATOR_ROLES:
                raise ValueError('unsupported_assignee')
            handoff.assigned_user_id = assignee.id
            handoff.assigned_at = datetime.now(timezone.utc)
            assigned_name = assignee.full_name
            assigned_code = assignee.external_code
        elif status == 'in_progress' and handoff.assigned_user_id is None and actor_user_id is not None:
            assignee = session.get(User, actor_user_id)
            if assignee is not None and assignee.role_code in INTERNAL_OPERATOR_ROLES:
                handoff.assigned_user_id = assignee.id
                handoff.assigned_at = datetime.now(timezone.utc)
                assigned_name = assignee.full_name
                assigned_code = assignee.external_code

        if status is not None:
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
        item = _serialize_handoff_rows(
            session,
            [(handoff, conversation, requester_name, requester_role, assigned_name, assigned_code)],
        )[0]
        set_span_attributes(
            **{
                'eduassist.support.found': True,
                'eduassist.support.status': item.status,
                'eduassist.support.priority': item.priority_code,
                'eduassist.support.sla_state': item.sla_state,
                'eduassist.support.assigned': item.assigned_user_id is not None,
            }
        )
        record_counter(
            'eduassist_support_handoff_events',
            attributes={
                'event': 'updated',
                'queue_name': item.queue_name,
                'priority': item.priority_code,
                'status': item.status,
                'assigned': item.assigned_user_id is not None,
            },
            description='Support handoff lifecycle events.',
        )
        record_histogram(
            'eduassist_support_handoff_latency_ms',
            (monotonic() - started_at) * 1000,
            attributes={'operation': 'update', 'queue_name': item.queue_name},
            description='Latency of support handoff operations in milliseconds.',
        )
        return item
