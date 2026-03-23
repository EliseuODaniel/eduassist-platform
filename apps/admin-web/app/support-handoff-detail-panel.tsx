'use client';

import { useEffect, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';

import type { SupportHandoffDetail } from '../lib/auth';

type Props = {
  detail: SupportHandoffDetail;
  canManage: boolean;
};

function formatDateTime(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(parsed);
}

function formatStatus(status: string): string {
  const labels: Record<string, string> = {
    queued: 'Na fila',
    in_progress: 'Em atendimento',
    resolved: 'Resolvido',
    cancelled: 'Cancelado',
    open: 'Aberta',
    closed: 'Fechada',
  };
  return labels[status] ?? status;
}

function formatQueue(queueName: string): string {
  const labels: Record<string, string> = {
    atendimento: 'Atendimento',
    secretaria: 'Secretaria',
    financeiro: 'Financeiro',
    coordenacao: 'Coordenação',
  };
  return labels[queueName] ?? queueName;
}

function formatPriority(priorityCode: string): string {
  const labels: Record<string, string> = {
    urgent: 'Urgente',
    high: 'Alta prioridade',
    standard: 'Prioridade padrão',
  };
  return labels[priorityCode] ?? priorityCode;
}

function formatSlaState(slaState: string): string {
  const labels: Record<string, string> = {
    on_track: 'SLA em dia',
    attention: 'SLA em atenção',
    breached: 'SLA estourado',
    closed: 'SLA encerrado',
    unknown: 'SLA indefinido',
  };
  return labels[slaState] ?? slaState;
}

function formatSender(senderType: string): string {
  const labels: Record<string, string> = {
    user: 'Usuário',
    operator: 'Operador',
    assistant: 'Bot',
    system: 'Sistema',
  };
  return labels[senderType] ?? senderType;
}

export function SupportHandoffDetailPanel({ detail, canManage }: Props) {
  const router = useRouter();
  const [note, setNote] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    setNote('');
    setError(null);
  }, [detail.item.handoff_id, detail.item.updated_at]);

  function submitUpdate(payload: {
    status?: string;
    assigned_user_id?: string;
    clear_assignment?: boolean;
    includeNote?: boolean;
  }) {
    startTransition(async () => {
      setError(null);

      const response = await fetch(`/api/support-handoffs/${detail.item.handoff_id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          status: payload.status,
          assigned_user_id: payload.assigned_user_id,
          clear_assignment: payload.clear_assignment,
          operator_note: payload.includeNote && note.trim() ? note.trim() : undefined,
        }),
      });

      if (!response.ok) {
        setError(
          response.status === 401
            ? 'Sua sessão expirou. Faça login novamente para continuar.'
            : 'Não consegui salvar a atualização do handoff agora.',
        );
        return;
      }

      setNote('');
      router.refresh();
    });
  }

  return (
    <section className="panel panel-strong section-stack">
      <div className="section-head">
        <div>
          <p className="eyebrow">Atendimento em foco</p>
          <h2>{detail.item.ticket_code}</h2>
          <p className="muted-copy">
            {formatQueue(detail.item.queue_name)} · {formatStatus(detail.item.status)} · Conversa{' '}
            {formatStatus(detail.conversation_status)} · {formatSlaState(detail.item.sla_state)}
          </p>
        </div>
        <span
          className={`status-chip ${
            detail.item.status === 'resolved' ? 'is-linked' : 'is-pending'
          }`}
        >
          {formatStatus(detail.item.status)}
        </span>
      </div>

      <div className="detail-grid">
        <div>
          <p className="label">Solicitante</p>
          <strong>
            {detail.item.requester_name ?? 'Visitante do bot'}
            {detail.item.requester_role ? ` (${detail.item.requester_role})` : ''}
          </strong>
        </div>
        <div>
          <p className="label">Canal / thread</p>
          <strong>
            {detail.item.channel} · {detail.item.external_thread_id}
          </strong>
        </div>
        <div>
          <p className="label">Prioridade</p>
          <strong>{formatPriority(detail.item.priority_code)}</strong>
        </div>
        <div>
          <p className="label">Responsável</p>
          <strong>
            {detail.item.assigned_operator_name
              ? `${detail.item.assigned_operator_name}${detail.item.assigned_operator_external_code ? ` · ${detail.item.assigned_operator_external_code}` : ''}`
              : 'Fila livre'}
          </strong>
        </div>
        <div>
          <p className="label">Criado em</p>
          <strong>{formatDateTime(detail.item.created_at)}</strong>
        </div>
        <div>
          <p className="label">Última atualização</p>
          <strong>{formatDateTime(detail.item.updated_at)}</strong>
        </div>
        <div>
          <p className="label">Primeira resposta até</p>
          <strong>
            {detail.item.response_due_at ? formatDateTime(detail.item.response_due_at) : 'n/d'}
          </strong>
        </div>
        <div>
          <p className="label">Resolução até</p>
          <strong>
            {detail.item.resolution_due_at ? formatDateTime(detail.item.resolution_due_at) : 'n/d'}
          </strong>
        </div>
      </div>

      <div className="tag-row">
        <span className="event-tag">{formatSlaState(detail.item.sla_state)}</span>
        {detail.item.assigned_at ? (
          <span className="event-tag">Assumido em: {formatDateTime(detail.item.assigned_at)}</span>
        ) : (
          <span className="event-tag">Ainda sem operador atribuído</span>
        )}
      </div>

      <div className="section-block">
        <p className="label">Resumo do encaminhamento</p>
        <p className="section-copy">{detail.item.summary}</p>
      </div>

      <div className="section-block">
        <p className="label">Histórico da conversa</p>
        {detail.messages.length === 0 ? (
          <p className="muted-copy">
            Ainda não há mensagens persistidas nesta conversa. Novas notas e interações vão
            aparecer aqui.
          </p>
        ) : (
          <ul className="message-thread">
            {detail.messages.map((message) => (
              <li className={`message-bubble is-${message.sender_type}`} key={message.message_id}>
                <div className="feed-head">
                  <strong>{formatSender(message.sender_type)}</strong>
                  <span className="timestamp-chip">{formatDateTime(message.created_at)}</span>
                </div>
                <p className="feed-copy">{message.content}</p>
              </li>
            ))}
          </ul>
        )}
      </div>

      {canManage ? (
        <div className="section-block">
          <p className="label">Nota operacional</p>
          <textarea
            className="operator-note"
            disabled={isPending}
            onChange={(event) => setNote(event.target.value)}
            placeholder="Registre contexto adicional, combinação com a família, encaminhamento interno ou próximos passos."
            rows={4}
            value={note}
          />

          {error ? <p className="feedback error-text">{error}</p> : null}

          <div className="action-row">
            <button
              className="secondary-button"
              disabled={isPending || note.trim().length === 0}
              onClick={() => submitUpdate({ includeNote: true })}
              type="button"
            >
              {isPending ? 'Salvando...' : 'Salvar nota'}
            </button>

            {detail.item.status !== 'resolved' && detail.item.status !== 'cancelled' ? (
              <button
                className="secondary-button"
                disabled={isPending}
                onClick={() =>
                  submitUpdate({
                    assigned_user_id: detail.actor.user_id,
                  })
                }
                type="button"
              >
                {isPending ? 'Atualizando...' : 'Assumir atendimento'}
              </button>
            ) : null}

            {detail.item.assigned_user_id ? (
              <button
                className="secondary-button"
                disabled={isPending}
                onClick={() =>
                  submitUpdate({
                    clear_assignment: true,
                  })
                }
                type="button"
              >
                {isPending ? 'Atualizando...' : 'Liberar atribuição'}
              </button>
            ) : null}

            {detail.item.status === 'queued' ? (
              <button
                className="secondary-button"
                disabled={isPending}
                onClick={() =>
                  submitUpdate({
                    status: 'in_progress',
                    includeNote: true,
                  })
                }
                type="button"
              >
                {isPending ? 'Atualizando...' : 'Iniciar atendimento'}
              </button>
            ) : null}

            {detail.item.status !== 'resolved' && detail.item.status !== 'cancelled' ? (
              <button
                className="primary-button"
                disabled={isPending}
                onClick={() =>
                  submitUpdate({
                    status: 'resolved',
                    includeNote: true,
                  })
                }
                type="button"
              >
                {isPending ? 'Atualizando...' : 'Marcar como resolvido'}
              </button>
            ) : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}
