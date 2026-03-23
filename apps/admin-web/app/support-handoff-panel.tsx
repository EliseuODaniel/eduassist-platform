'use client';

import { useRouter } from 'next/navigation';
import { useState, useTransition } from 'react';

import type { SupportHandoffItem } from '../lib/auth';

type Props = {
  items: SupportHandoffItem[];
  counts: Record<string, number>;
  scope: string;
  canManage: boolean;
  selectedHandoffId: string | null;
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

export function SupportHandoffPanel({
  items,
  counts,
  scope,
  canManage,
  selectedHandoffId,
}: Props) {
  const router = useRouter();
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  function handleSelect(handoffId: string) {
    const params = new URLSearchParams(window.location.search);
    params.set('handoff', handoffId);
    router.push(`/?${params.toString()}`, { scroll: false });
  }

  function handleStatusUpdate(handoffId: string, status: 'in_progress' | 'resolved') {
    startTransition(async () => {
      setError(null);
      setPendingId(handoffId);

      const response = await fetch(`/api/support-handoffs/${handoffId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({ status }),
      });

      setPendingId(null);

      if (!response.ok) {
        setError(
          response.status === 401
            ? 'Sua sessão expirou. Faça login novamente para gerenciar a fila.'
            : 'Não consegui atualizar o status do handoff agora.',
        );
        return;
      }

      router.refresh();
    });
  }

  return (
    <section className="panel panel-strong section-stack">
      <div className="section-head">
        <div>
          <p className="eyebrow">Handoff humano</p>
          <h2>{scope === 'global' ? 'Fila operacional recente' : 'Seus atendimentos recentes'}</h2>
        </div>
        <span className="status-chip is-linked">{items.length} itens</span>
      </div>

      <div className="tag-row">
        {Object.entries(counts).map(([status, total]) => (
          <span className="event-tag" key={status}>
            {formatStatus(status)}: {total}
          </span>
        ))}
      </div>

      {error ? <p className="feedback error-text">{error}</p> : null}

      {items.length === 0 ? (
        <p className="muted-copy">
          Ainda não há handoffs abertos neste escopo. Quando o bot encaminhar uma conversa humana,
          ela aparecerá aqui.
        </p>
      ) : (
        <ul className="feed-list">
          {items.map((item) => {
            const busy = isPending && pendingId === item.handoff_id;
            const selected = item.handoff_id === selectedHandoffId;

            return (
              <li className={`feed-item ${selected ? 'is-selected' : ''}`} key={item.handoff_id}>
                <div className="feed-head">
                  <div>
                    <strong>{item.ticket_code}</strong>
                    <p className="muted-copy">
                      {formatQueue(item.queue_name)} · {formatStatus(item.status)}
                    </p>
                  </div>
                  <span
                    className={`status-chip ${
                      item.status === 'resolved' ? 'is-linked' : 'is-pending'
                    }`}
                  >
                    {formatStatus(item.status)}
                  </span>
                </div>

                <p className="feed-copy">{item.summary}</p>

                <div className="tag-row">
                  <span className="event-tag">Canal: {item.channel}</span>
                  <span className="event-tag">{formatPriority(item.priority_code)}</span>
                  <span className="event-tag">{formatSlaState(item.sla_state)}</span>
                  {item.requester_name ? (
                    <span className="event-tag">
                      Solicitante: {item.requester_name}
                      {item.requester_role ? ` (${item.requester_role})` : ''}
                    </span>
                  ) : (
                    <span className="event-tag">Solicitante: visitante do bot</span>
                  )}
                  {item.assigned_operator_name ? (
                    <span className="event-tag">
                      Responsável: {item.assigned_operator_name}
                    </span>
                  ) : (
                    <span className="event-tag">Responsável: fila livre</span>
                  )}
                  <span className="event-tag">Atualizado: {formatDateTime(item.updated_at)}</span>
                </div>

                {item.last_message_excerpt ? (
                  <p className="feed-foot">Última mensagem: {item.last_message_excerpt}</p>
                ) : null}

                <div className="action-row">
                  <button
                    className={selected ? 'primary-button' : 'secondary-button'}
                    onClick={() => handleSelect(item.handoff_id)}
                    type="button"
                  >
                    {selected ? 'Conversa aberta' : 'Abrir conversa'}
                  </button>

                  {canManage && item.status !== 'resolved' && item.status !== 'cancelled' ? (
                    <>
                      {item.status === 'queued' ? (
                        <button
                          className="secondary-button"
                          disabled={busy}
                          onClick={() => handleStatusUpdate(item.handoff_id, 'in_progress')}
                          type="button"
                        >
                          {busy ? 'Atualizando...' : 'Iniciar atendimento'}
                        </button>
                      ) : null}
                      <button
                        className="primary-button"
                        disabled={busy}
                        onClick={() => handleStatusUpdate(item.handoff_id, 'resolved')}
                        type="button"
                      >
                        {busy ? 'Atualizando...' : 'Marcar como resolvido'}
                      </button>
                    </>
                  ) : null}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
