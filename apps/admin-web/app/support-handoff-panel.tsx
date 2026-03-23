'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState, useTransition } from 'react';

import type { SupportHandoffFilters, SupportHandoffItem } from '../lib/auth';

type Props = {
  items: SupportHandoffItem[];
  counts: Record<string, number>;
  filters: SupportHandoffFilters;
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
  filters,
  scope,
  canManage,
  selectedHandoffId,
}: Props) {
  const router = useRouter();
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [draftFilters, setDraftFilters] = useState<SupportHandoffFilters>(filters);

  useEffect(() => {
    setDraftFilters(filters);
  }, [filters]);

  function handleSelect(handoffId: string) {
    const params = new URLSearchParams(window.location.search);
    params.set('handoff', handoffId);
    router.push(`/?${params.toString()}`, { scroll: false });
  }

  function handleApplyFilters() {
    const params = new URLSearchParams(window.location.search);
    params.delete('handoff');

    const filterEntries: Array<[string, string | null]> = [
      ['handoffStatus', draftFilters.status],
      ['handoffQueue', draftFilters.queue_name],
      ['handoffAssignment', draftFilters.assignment],
      ['handoffSla', draftFilters.sla_state],
      ['handoffSearch', draftFilters.search],
    ];

    for (const [key, value] of filterEntries) {
      const normalized = value?.trim() ?? '';
      if (normalized) {
        params.set(key, normalized);
      } else {
        params.delete(key);
      }
    }

    router.push(`/?${params.toString()}`, { scroll: false });
  }

  function handleClearFilters() {
    setDraftFilters({
      status: null,
      queue_name: null,
      assignment: null,
      sla_state: null,
      search: null,
      limit: filters.limit,
    });
    router.push('/', { scroll: false });
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

      <div className="filter-shell">
        <div className="filter-grid">
          <label className="filter-field">
            <span>Status</span>
            <select
              value={draftFilters.status ?? ''}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  status: event.target.value || null,
                }))
              }
            >
              <option value="">Todos</option>
              <option value="queued">Na fila</option>
              <option value="in_progress">Em atendimento</option>
              <option value="resolved">Resolvido</option>
              <option value="cancelled">Cancelado</option>
            </select>
          </label>

          <label className="filter-field">
            <span>Fila</span>
            <select
              value={draftFilters.queue_name ?? ''}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  queue_name: event.target.value || null,
                }))
              }
            >
              <option value="">Todas</option>
              <option value="atendimento">Atendimento</option>
              <option value="secretaria">Secretaria</option>
              <option value="financeiro">Financeiro</option>
              <option value="coordenacao">Coordenação</option>
            </select>
          </label>

          <label className="filter-field">
            <span>Atribuição</span>
            <select
              value={draftFilters.assignment ?? ''}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  assignment: event.target.value || null,
                }))
              }
            >
              <option value="">Qualquer</option>
              <option value="mine">Meus tickets</option>
              <option value="unassigned">Sem responsável</option>
              <option value="assigned">Já atribuídos</option>
            </select>
          </label>

          <label className="filter-field">
            <span>SLA</span>
            <select
              value={draftFilters.sla_state ?? ''}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  sla_state: event.target.value || null,
                }))
              }
            >
              <option value="">Todos</option>
              <option value="on_track">Em dia</option>
              <option value="attention">Em atenção</option>
              <option value="breached">Estourado</option>
              <option value="closed">Encerrado</option>
            </select>
          </label>

          <label className="filter-field filter-field-search">
            <span>Busca</span>
            <input
              placeholder="Ticket, solicitante ou resumo"
              type="search"
              value={draftFilters.search ?? ''}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  search: event.target.value || null,
                }))
              }
            />
          </label>
        </div>

        <div className="action-row">
          <button className="secondary-button" onClick={handleApplyFilters} type="button">
            Aplicar filtros
          </button>
          <button className="secondary-button" onClick={handleClearFilters} type="button">
            Limpar
          </button>
        </div>
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
