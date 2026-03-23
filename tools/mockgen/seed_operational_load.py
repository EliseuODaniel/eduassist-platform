from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from api_core.db.models import AuditEvent, Conversation, Handoff, Message, ToolCall, User
from api_core.db.session import session_scope


@dataclass(frozen=True)
class HandoffSeedScenario:
    thread_id: str
    user_external_code: str | None
    queue_name: str
    priority_code: str
    status: str
    summary: str
    user_message: str
    created_offset: timedelta
    assigned_offset: timedelta | None = None
    updated_offset: timedelta | None = None
    assignee_external_code: str | None = None
    operator_message: str | None = None
    add_tool_call: bool = False
    close_conversation: bool = False


def _set_timestamps(record, *, created_at: datetime, updated_at: datetime | None = None) -> None:
    record.created_at = created_at
    record.updated_at = updated_at or created_at


def _priority_windows(priority_code: str) -> tuple[timedelta, timedelta]:
    if priority_code == 'urgent':
        return timedelta(minutes=30), timedelta(hours=4)
    if priority_code == 'high':
        return timedelta(hours=1), timedelta(hours=8)
    return timedelta(hours=4), timedelta(hours=24)


def _event(
    *,
    actor_user_id,
    event_type: str,
    resource_id: str,
    occurred_at: datetime,
    metadata: dict[str, object],
) -> AuditEvent:
    event = AuditEvent(
        actor_user_id=actor_user_id,
        event_type=event_type,
        resource_type='support_handoff',
        resource_id=resource_id,
        metadata_json=metadata,
    )
    _set_timestamps(event, created_at=occurred_at, updated_at=occurred_at)
    return event


SCENARIOS = [
    HandoffSeedScenario(
        thread_id='ops-seed-001',
        user_external_code='USR-GUARD-001',
        queue_name='financeiro',
        priority_code='high',
        status='queued',
        summary='Responsável pediu revisão de multa e juros da mensalidade de Ana Oliveira.',
        user_message='Preciso revisar a fatura da Ana porque entrou multa indevida.',
        created_offset=timedelta(minutes=55),
    ),
    HandoffSeedScenario(
        thread_id='ops-seed-002',
        user_external_code='USR-GUARD-002',
        queue_name='secretaria',
        priority_code='standard',
        status='queued',
        summary='Pai solicitou declaração escolar com urgência para o filho Bruno Santos.',
        user_message='Preciso de uma declaração escolar para o Bruno ainda hoje.',
        created_offset=timedelta(hours=6, minutes=30),
    ),
    HandoffSeedScenario(
        thread_id='ops-seed-003',
        user_external_code='USR-TEACH-001',
        queue_name='coordenacao',
        priority_code='high',
        status='in_progress',
        summary='Professora pediu apoio da coordenação para revisar fechamento de notas.',
        user_message='Quero confirmar o procedimento para fechamento das notas da turma 1EM-A.',
        created_offset=timedelta(hours=3, minutes=20),
        assigned_offset=timedelta(minutes=25),
        updated_offset=timedelta(minutes=18),
        assignee_external_code='USR-STAFF-001',
        operator_message='Coordenação assumiu o atendimento e vai revisar o diário com você.',
        add_tool_call=True,
    ),
    HandoffSeedScenario(
        thread_id='ops-seed-004',
        user_external_code=None,
        queue_name='atendimento',
        priority_code='standard',
        status='queued',
        summary='Visitante anônimo quer falar com humano sobre regras de matrícula.',
        user_message='Quero falar com alguém sobre matrícula e documentação.',
        created_offset=timedelta(minutes=20),
    ),
    HandoffSeedScenario(
        thread_id='ops-seed-005',
        user_external_code='USR-GUARD-001',
        queue_name='financeiro',
        priority_code='high',
        status='in_progress',
        summary='Responsável contesta boleto em atraso e pede negociação imediata.',
        user_message='Quero negociar o boleto atrasado do Lucas hoje.',
        created_offset=timedelta(hours=26),
        assigned_offset=timedelta(hours=1, minutes=10),
        updated_offset=timedelta(minutes=32),
        assignee_external_code='USR-FIN-001',
        operator_message='Financeiro assumiu e está preparando a proposta de negociação.',
        add_tool_call=True,
    ),
    HandoffSeedScenario(
        thread_id='ops-seed-006',
        user_external_code='USR-STUD-003',
        queue_name='secretaria',
        priority_code='standard',
        status='queued',
        summary='Aluno pediu histórico parcial para processo externo.',
        user_message='Preciso do meu histórico parcial e queria confirmar o prazo.',
        created_offset=timedelta(hours=1, minutes=45),
        assigned_offset=timedelta(minutes=40),
        assignee_external_code='USR-STAFF-001',
        operator_message='Secretaria registrou o pedido e confirmou o prazo de emissão.',
    ),
    HandoffSeedScenario(
        thread_id='ops-seed-007',
        user_external_code='USR-GUARD-001',
        queue_name='financeiro',
        priority_code='high',
        status='resolved',
        summary='Pedido de segunda via foi concluído pelo financeiro.',
        user_message='Consegue me enviar a segunda via da mensalidade da Ana?',
        created_offset=timedelta(days=2, hours=3),
        assigned_offset=timedelta(minutes=28),
        updated_offset=timedelta(days=1, hours=20),
        assignee_external_code='USR-FIN-001',
        operator_message='Segunda via emitida e enviada para o e-mail cadastrado.',
        close_conversation=True,
        add_tool_call=True,
    ),
    HandoffSeedScenario(
        thread_id='ops-seed-008',
        user_external_code='USR-TEACH-002',
        queue_name='coordenacao',
        priority_code='standard',
        status='resolved',
        summary='Coordenação validou ajuste de calendário para o 2o ano.',
        user_message='Preciso ajustar a data do simulado do 2o ano.',
        created_offset=timedelta(days=3, hours=4),
        assigned_offset=timedelta(minutes=42),
        updated_offset=timedelta(days=3, hours=1, minutes=20),
        assignee_external_code='USR-STAFF-001',
        operator_message='Calendário ajustado e comunicado disparado para a turma.',
        close_conversation=True,
    ),
    HandoffSeedScenario(
        thread_id='ops-seed-009',
        user_external_code=None,
        queue_name='coordenacao',
        priority_code='urgent',
        status='queued',
        summary='Contato externo sinalizou ocorrência crítica envolvendo aluno no portão.',
        user_message='Preciso falar urgentemente com a coordenação agora.',
        created_offset=timedelta(minutes=48),
    ),
    HandoffSeedScenario(
        thread_id='ops-seed-010',
        user_external_code='USR-GUARD-002',
        queue_name='atendimento',
        priority_code='standard',
        status='cancelled',
        summary='Responsável desistiu do atendimento após receber orientação automática.',
        user_message='Na verdade já consegui a informação, obrigado.',
        created_offset=timedelta(days=1, hours=2),
        updated_offset=timedelta(days=1, hours=1, minutes=40),
        close_conversation=True,
    ),
]


def main() -> None:
    now = datetime.now(UTC)

    with session_scope() as session:
        existing_seed = session.scalar(
            select(Conversation).where(Conversation.external_thread_id == 'ops-seed-001')
        )
        if existing_seed is not None:
            print('operational load seed already present; skipping')
            return

        users = {
            user.external_code: user
            for user in session.execute(select(User).where(User.external_code.is_not(None)))
            .scalars()
            .all()
        }

        inserted = 0
        for scenario in SCENARIOS:
            created_at = now - scenario.created_offset
            updated_at = now - (scenario.updated_offset or scenario.created_offset)
            response_window, resolution_window = _priority_windows(scenario.priority_code)
            assigned_user = (
                users.get(scenario.assignee_external_code)
                if scenario.assignee_external_code
                else None
            )
            owner = users.get(scenario.user_external_code) if scenario.user_external_code else None
            assigned_at = (
                created_at + scenario.assigned_offset if scenario.assigned_offset else None
            )

            conversation = Conversation(
                user_id=owner.id if owner else None,
                channel='telegram',
                external_thread_id=scenario.thread_id,
                status='closed'
                if scenario.close_conversation or scenario.status in {'resolved', 'cancelled'}
                else 'open',
            )
            _set_timestamps(conversation, created_at=created_at, updated_at=updated_at)
            session.add(conversation)
            session.flush()

            user_message = Message(
                conversation_id=conversation.id,
                sender_type='user',
                content=scenario.user_message,
            )
            _set_timestamps(user_message, created_at=created_at + timedelta(minutes=1))
            session.add(user_message)

            if scenario.operator_message:
                operator_message = Message(
                    conversation_id=conversation.id,
                    sender_type='operator',
                    content=scenario.operator_message,
                )
                operator_created_at = assigned_at or (created_at + timedelta(minutes=15))
                _set_timestamps(
                    operator_message, created_at=operator_created_at, updated_at=operator_created_at
                )
                session.add(operator_message)

            if scenario.add_tool_call:
                tool_call = ToolCall(
                    conversation_id=conversation.id,
                    tool_name='support_context_lookup',
                    status='completed',
                    request_payload={
                        'thread_id': scenario.thread_id,
                        'queue_name': scenario.queue_name,
                    },
                    response_payload={
                        'summary_available': True,
                        'priority_code': scenario.priority_code,
                    },
                )
                tool_created_at = assigned_at or (created_at + timedelta(minutes=10))
                _set_timestamps(tool_call, created_at=tool_created_at, updated_at=tool_created_at)
                session.add(tool_call)

            handoff = Handoff(
                conversation_id=conversation.id,
                queue_name=scenario.queue_name,
                priority_code=scenario.priority_code,
                assigned_user_id=assigned_user.id if assigned_user else None,
                assigned_at=assigned_at,
                response_due_at=created_at + response_window,
                resolution_due_at=(assigned_at or created_at) + resolution_window,
                status=scenario.status,
                summary=scenario.summary,
            )
            _set_timestamps(handoff, created_at=created_at, updated_at=updated_at)
            session.add(handoff)
            session.flush()

            session.add(
                _event(
                    actor_user_id=owner.id if owner else None,
                    event_type='support_handoff.created',
                    resource_id=str(handoff.id),
                    occurred_at=created_at,
                    metadata={
                        'status': 'queued',
                        'queue_name': scenario.queue_name,
                        'priority_code': scenario.priority_code,
                    },
                )
            )

            if assigned_at is not None and scenario.status in {'in_progress', 'resolved'}:
                session.add(
                    _event(
                        actor_user_id=assigned_user.id if assigned_user else None,
                        event_type='support_handoff.status_updated',
                        resource_id=str(handoff.id),
                        occurred_at=assigned_at,
                        metadata={
                            'status': 'in_progress',
                            'queue_name': scenario.queue_name,
                            'priority_code': scenario.priority_code,
                        },
                    )
                )

            if scenario.status in {'resolved', 'cancelled'}:
                session.add(
                    _event(
                        actor_user_id=assigned_user.id if assigned_user else None,
                        event_type='support_handoff.status_updated',
                        resource_id=str(handoff.id),
                        occurred_at=updated_at,
                        metadata={
                            'status': scenario.status,
                            'queue_name': scenario.queue_name,
                            'priority_code': scenario.priority_code,
                        },
                    )
                )

            inserted += 1

    print(f'operational load seed inserted successfully; handoffs={inserted}')


if __name__ == '__main__':
    main()
