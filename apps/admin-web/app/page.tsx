import Link from 'next/link';
import { redirect } from 'next/navigation';

import { ConversationHistoryPanel } from './conversation-history-panel';
import { LinkChallengePanel } from './link-challenge-panel';
import { SupportHandoffDetailPanel } from './support-handoff-detail-panel';
import { SupportHandoffPanel } from './support-handoff-panel';
import {
  getSupportConversationDetail,
  getSupportConversations,
  getSupportHandoffDetail,
  getOperationsOverview,
  getPortalSession,
  getSupportHandoffs,
  type AccessDecisionFeedEntry,
  type AuditEventFeedEntry,
  type HandoffOperationsOverview,
  type OperationsOverview,
  type PortalActor,
  type SupportHandoffFilters,
} from '../lib/auth';

export const dynamic = 'force-dynamic';

const landingHighlights = [
  'Atendimento integrado',
  'Telegram conectado',
  'Acesso seguro',
];

const demoAccounts = [
  { role: 'Responsável', username: 'maria.oliveira', password: 'Eduassist123!' },
  { role: 'Professora', username: 'helena.rocha', password: 'Eduassist123!' },
  { role: 'Financeiro', username: 'carla.nogueira', password: 'Eduassist123!' },
];

type DashboardView = 'overview' | 'handoffs' | 'conversation' | 'account' | 'details';

function formatRole(roleCode: string): string {
  const labels: Record<string, string> = {
    guardian: 'Responsável',
    student: 'Aluno',
    teacher: 'Professor',
    staff: 'Secretaria',
    finance: 'Financeiro',
    coordinator: 'Coordenação',
    admin: 'Administração',
  };
  return labels[roleCode] ?? roleCode;
}

function formatAuthError(code: string): string {
  const messages: Record<string, string> = {
    access_denied: 'O login foi cancelado no provedor de identidade.',
    authorization_code_missing: 'O callback do provedor voltou sem código de autorização.',
    invalid_login_state: 'A validação do login expirou ou ficou inconsistente. Tente novamente.',
    token_exchange_failed: 'Não consegui concluir a troca do código por tokens no Keycloak.',
  };
  return messages[code] ?? 'Não consegui concluir o login agora. Tente novamente.';
}

function getStringSearchParam(
  value: string | string[] | undefined,
): string | null {
  if (typeof value === 'string') {
    return value.length > 0 ? value : null;
  }
  if (Array.isArray(value) && value.length > 0) {
    return value[0] || null;
  }
  return null;
}

function buildAccessHighlights(actor: PortalActor): string[] {
  if (actor.role_code === 'guardian' || actor.role_code === 'student') {
    return actor.linked_students.map((student) => {
      const scopes = [
        student.can_view_academic ? 'acadêmico' : null,
        student.can_view_finance ? 'financeiro' : null,
      ]
        .filter(Boolean)
        .join(' + ');

      return `${student.full_name} · ${student.class_name ?? 'sem turma'} · ${scopes}`;
    });
  }

  if (actor.role_code === 'teacher') {
    return actor.accessible_classes.map((item) => {
      const subject = item.subject_name ? ` · ${item.subject_name}` : '';
      return `${item.class_name}${subject}`;
    });
  }

  return [];
}

function formatMetricLabel(metricKey: string): string {
  const labels: Record<string, string> = {
    recent_audit_events: 'Eventos recentes',
    recent_access_decisions: 'Decisões recentes',
    recent_denials: 'Negativas recentes',
    telegram_linked: 'Telegram vinculado',
    linked_students: 'Alunos vinculados',
    accessible_classes: 'Turmas acessíveis',
    active_users: 'Usuários ativos',
    linked_telegram_accounts: 'Contas Telegram vinculadas',
    pending_telegram_links: 'Vínculos pendentes',
    open_handoffs: 'Handoffs abertos',
    queued_handoffs: 'Na fila',
    in_progress_handoffs: 'Em atendimento',
    handoff_sla_attention: 'SLA em atenção',
    handoff_sla_breached: 'SLA estourado',
    handoffs_without_assignee: 'Sem responsável',
    critical_handoffs: 'Exceções críticas',
  };
  return labels[metricKey] ?? formatTokenLabel(metricKey);
}

function formatScope(scope: string): string {
  return scope === 'global' ? 'Visão operacional global' : 'Visão operacional pessoal';
}

function buildRoleSummary(actor: PortalActor): string {
  if (actor.role_code === 'guardian') {
    return 'Acompanhe informações acadêmicas, financeiro, atendimento e o vínculo com o Telegram em uma experiência mais direta e organizada.';
  }

  if (actor.role_code === 'student') {
    return 'Consulte sua conta, acompanhe o atendimento e mantenha o acesso ao bot conectado com o que importa no dia a dia.';
  }

  if (actor.role_code === 'teacher') {
    return 'Veja suas turmas, acompanhe o atendimento e mantenha seus acessos organizados sem excesso de informação na tela.';
  }

  if (actor.role_code === 'staff' || actor.role_code === 'finance' || actor.role_code === 'coordinator') {
    return 'Centralize filas, atendimentos e contexto operacional em uma interface mais limpa, com os detalhes certos no momento certo.';
  }

  return 'Acompanhe sua conta, o atendimento e os recursos disponíveis em um portal mais claro e focado no essencial.';
}

function getPreferredMetricOrder(roleCode: string): string[] {
  const shared = [
    'telegram_linked',
    'pending_telegram_links',
    'recent_denials',
    'recent_access_decisions',
    'recent_audit_events',
  ];

  if (roleCode === 'guardian' || roleCode === 'student') {
    return ['linked_students', 'telegram_linked', 'recent_access_decisions', 'recent_audit_events', ...shared];
  }

  if (roleCode === 'teacher') {
    return ['accessible_classes', 'telegram_linked', 'recent_access_decisions', 'recent_audit_events', ...shared];
  }

  return [
    'critical_handoffs',
    'handoff_sla_breached',
    'handoff_sla_attention',
    'open_handoffs',
    'queued_handoffs',
    'in_progress_handoffs',
    'handoffs_without_assignee',
    ...shared,
  ];
}

function orderMetricEntries(
  metricEntries: Array<[string, number]>,
  roleCode: string,
): Array<[string, number]> {
  const valueByKey = new Map(metricEntries);
  const seen = new Set<string>();
  const ordered: Array<[string, number]> = [];

  for (const key of getPreferredMetricOrder(roleCode)) {
    const value = valueByKey.get(key);
    if (value === undefined || seen.has(key)) {
      continue;
    }
    seen.add(key);
    ordered.push([key, value]);
  }

  for (const entry of metricEntries) {
    if (seen.has(entry[0])) {
      continue;
    }
    ordered.push(entry);
  }

  return ordered;
}

function formatTimestamp(value: string): string {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value));
}

function formatTokenLabel(value: string): string {
  return value
    .replace(/[._]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function buildHandoffHref(filters: {
  view?: DashboardView | null;
  handoff?: string | null;
  conversationId?: string | null;
  status?: string | null;
  queue?: string | null;
  assignment?: string | null;
  sla?: string | null;
  search?: string | null;
  page?: number | null;
  limit?: number | null;
}): string {
  const params = new URLSearchParams();
  if (filters.view) {
    params.set('view', filters.view);
  }
  if (filters.handoff) {
    params.set('handoff', filters.handoff);
  }
  if (filters.conversationId) {
    params.set('conversationId', filters.conversationId);
  }
  if (filters.status) {
    params.set('handoffStatus', filters.status);
  }
  if (filters.queue) {
    params.set('handoffQueue', filters.queue);
  }
  if (filters.assignment) {
    params.set('handoffAssignment', filters.assignment);
  }
  if (filters.sla) {
    params.set('handoffSla', filters.sla);
  }
  if (filters.search) {
    params.set('handoffSearch', filters.search);
  }
  if (typeof filters.page === 'number' && filters.page > 0) {
    params.set('handoffPage', String(filters.page));
  }
  if (typeof filters.limit === 'number' && filters.limit > 0) {
    params.set('handoffLimit', String(filters.limit));
  }
  const query = params.toString();
  return query ? `/?${query}` : '/';
}

function getDashboardView(value: string | null): DashboardView {
  if (
    value === 'overview' ||
    value === 'handoffs' ||
    value === 'conversation' ||
    value === 'account' ||
    value === 'details'
  ) {
    return value;
  }
  return 'overview';
}

function buildReturnToPath(
  params: Record<string, string | string[] | undefined>,
): string {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (typeof value === 'string' && value.length > 0) {
      query.set(key, value);
      continue;
    }
    if (Array.isArray(value)) {
      for (const entry of value) {
        if (entry.length > 0) {
          query.append(key, entry);
        }
      }
    }
  }

  const serialized = query.toString();
  return serialized ? `/?${serialized}` : '/';
}

function renderCompactHandoffSummary(handoffOverview: HandoffOperationsOverview) {
  return (
    <section className="panel panel-strong compact-ops-card">
      <div className="section-head">
        <div>
          <p className="eyebrow">Fila humana</p>
          <h2>Panorama rápido</h2>
        </div>
        <Link
          className="secondary-link"
          href={buildHandoffHref({
            view: 'handoffs',
            status: 'queued',
          })}
        >
          Abrir fila
        </Link>
      </div>

      <div className="metric-strip">
        <article className="metric-card">
          <p className="label">Ativos</p>
          <strong>{handoffOverview.open_total}</strong>
        </article>
        <article className="metric-card">
          <p className="label">Em atenção</p>
          <strong>{handoffOverview.attention_total}</strong>
        </article>
        <article className="metric-card">
          <p className="label">Críticos</p>
          <strong>{handoffOverview.critical_total}</strong>
        </article>
        <article className="metric-card">
          <p className="label">Sem responsável</p>
          <strong>{handoffOverview.unassigned_total}</strong>
        </article>
      </div>
    </section>
  );
}

function renderAuditMetadata(metadata: Record<string, unknown>) {
  const entries = Object.entries(metadata).slice(0, 3);
  if (entries.length === 0) {
    return null;
  }

  return (
    <div className="tag-row">
      {entries.map(([key, rawValue]) => (
        <span className="event-tag" key={key}>
          {formatTokenLabel(key)}: {String(rawValue)}
        </span>
      ))}
    </div>
  );
}

function renderAuditFeed(events: AuditEventFeedEntry[], overview: OperationsOverview) {
  if (events.length === 0) {
    return <p className="muted-copy">Ainda não há eventos auditáveis no escopo desta conta.</p>;
  }

  return (
    <ul className="feed-list">
      {events.map((event) => {
        const actorLabel =
          overview.scope === 'global'
            ? event.actor_full_name ?? event.actor_external_code ?? 'ator do sistema'
            : 'sua conta';

        return (
          <li className="feed-item" key={`${event.occurred_at}-${event.event_type}-${event.resource_type}`}>
            <div className="feed-head">
              <div>
                <strong>{formatTokenLabel(event.event_type)}</strong>
                <p className="muted-copy">
                  {actorLabel} · {formatTokenLabel(event.resource_type)}
                </p>
              </div>
              <span className="timestamp-chip">{formatTimestamp(event.occurred_at)}</span>
            </div>
            {renderAuditMetadata(event.metadata)}
          </li>
        );
      })}
    </ul>
  );
}

function renderAccessDecisions(decisions: AccessDecisionFeedEntry[], overview: OperationsOverview) {
  if (decisions.length === 0) {
    return <p className="muted-copy">Nenhuma decisão de acesso recente foi registrada neste escopo.</p>;
  }

  return (
    <ul className="feed-list">
      {decisions.map((item) => {
        const actorLabel =
          overview.scope === 'global'
            ? item.actor_full_name ?? item.actor_external_code ?? 'ator do sistema'
            : 'sua conta';

        return (
          <li className="feed-item" key={`${item.occurred_at}-${item.action}-${item.resource_type}`}>
            <div className="feed-head">
              <div>
                <strong>{formatTokenLabel(item.action)}</strong>
                <p className="muted-copy">
                  {actorLabel} · {formatTokenLabel(item.resource_type)}
                </p>
              </div>
              <span
                className={`status-chip ${item.decision === 'allow' ? 'is-linked' : 'is-pending'}`}
              >
                {item.decision === 'allow' ? 'Permitido' : 'Negado'}
              </span>
            </div>
            <p className="feed-copy">{item.reason ? formatTokenLabel(item.reason) : 'Sem justificativa informada.'}</p>
            <p className="feed-foot">{formatTimestamp(item.occurred_at)}</p>
          </li>
        );
      })}
    </ul>
  );
}

function formatQueueName(queueName: string): string {
  const labels: Record<string, string> = {
    atendimento: 'Atendimento',
    secretaria: 'Secretaria',
    financeiro: 'Financeiro',
    coordenacao: 'Coordenação',
  };
  return labels[queueName] ?? formatTokenLabel(queueName);
}

function formatPriority(priorityCode: string): string {
  const labels: Record<string, string> = {
    urgent: 'Urgente',
    high: 'Alta prioridade',
    standard: 'Prioridade padrão',
  };
  return labels[priorityCode] ?? formatTokenLabel(priorityCode);
}

function formatSlaState(slaState: string): string {
  const labels: Record<string, string> = {
    breached: 'SLA estourado',
    attention: 'SLA em atenção',
    on_track: 'SLA em dia',
    closed: 'SLA encerrado',
    unknown: 'SLA indefinido',
  };
  return labels[slaState] ?? formatTokenLabel(slaState);
}

function formatAlertFlag(flag: string): string {
  const labels: Record<string, string> = {
    sla_breached: 'SLA estourado',
    sla_attention: 'SLA em atenção',
    priority_urgent: 'Urgente',
    priority_high: 'Alta prioridade',
    unassigned: 'Sem responsável',
  };
  return labels[flag] ?? formatTokenLabel(flag);
}

function formatDueLabel(alert: HandoffOperationsOverview['alerts'][number]): string {
  const dueAt = alert.status === 'queued' ? alert.response_due_at : alert.resolution_due_at;
  if (!dueAt) {
    return 'Sem prazo calculado';
  }
  return `Prazo: ${formatTimestamp(dueAt)}`;
}

function formatDurationMinutes(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return 'Sem base suficiente';
  }

  if (value >= 60) {
    const hours = value / 60;
    return `${hours.toFixed(1)} h`;
  }

  return `${Math.round(value)} min`;
}

function renderHandoffObservability(handoffOverview: HandoffOperationsOverview) {
  const observability = handoffOverview.observability;
  if (!observability) {
    return null;
  }

  const maxTimelineValue = Math.max(
    1,
    ...observability.timeline.flatMap((point) => [
      point.opened_count,
      point.started_count,
      point.resolved_count,
    ]),
  );

  return (
    <section className="workspace-grid">
      <article className="panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Ritmo operacional</p>
            <h2>Volume recente de handoffs</h2>
          </div>
        </div>

        <div className="summary-grid summary-grid-compact">
          <article className="metric-card">
            <p className="label">Abertos 24h</p>
            <strong>{observability.opened_last_24h}</strong>
          </article>
          <article className="metric-card">
            <p className="label">Assumidos 24h</p>
            <strong>{observability.started_last_24h}</strong>
          </article>
          <article className="metric-card">
            <p className="label">Resolvidos 24h</p>
            <strong>{observability.resolved_last_24h}</strong>
          </article>
          <article className="metric-card">
            <p className="label">Abertos 7d</p>
            <strong>{observability.opened_last_7d}</strong>
          </article>
          <article className="metric-card">
            <p className="label">Assumidos 7d</p>
            <strong>{observability.started_last_7d}</strong>
          </article>
          <article className="metric-card">
            <p className="label">Resolvidos 7d</p>
            <strong>{observability.resolved_last_7d}</strong>
          </article>
        </div>

        <div className="timeline-list">
          {observability.timeline.map((point) => (
            <div className="timeline-row" key={point.period_start}>
              <div className="timeline-labels">
                <strong>{point.label}</strong>
                <span className="muted-copy">
                  {point.opened_count} abertos · {point.started_count} assumidos · {point.resolved_count} resolvidos
                </span>
              </div>
              <div className="timeline-bars">
                <span
                  className="timeline-bar timeline-bar-opened"
                  style={{ width: `${(point.opened_count / maxTimelineValue) * 100}%` }}
                />
                <span
                  className="timeline-bar timeline-bar-started"
                  style={{ width: `${(point.started_count / maxTimelineValue) * 100}%` }}
                />
                <span
                  className="timeline-bar timeline-bar-resolved"
                  style={{ width: `${(point.resolved_count / maxTimelineValue) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </article>

      <article className="panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Tempo de resposta</p>
            <h2>Eficiência operacional recente</h2>
          </div>
        </div>

        <div className="summary-grid summary-grid-compact">
          <article className="metric-card">
            <p className="label">Atribuição média 7d</p>
            <strong>{formatDurationMinutes(observability.avg_assignment_minutes_7d)}</strong>
          </article>
          <article className="metric-card">
            <p className="label">Resolução média 7d</p>
            <strong>{formatDurationMinutes(observability.avg_resolution_minutes_7d)}</strong>
          </article>
          <article className="metric-card">
            <p className="label">Backlog crítico</p>
            <strong>{handoffOverview.critical_total}</strong>
          </article>
          <article className="metric-card">
            <p className="label">Tickets sem dono</p>
            <strong>{handoffOverview.unassigned_total}</strong>
          </article>
        </div>

        <p className="muted-copy section-copy">
          Esses indicadores usam eventos auditados do próprio domínio de handoff para mostrar ritmo
          de abertura, assunção e resolução, além do tempo médio até alguém assumir ou concluir um
          atendimento.
        </p>
      </article>
    </section>
  );
}

function renderHandoffAlertFeed(handoffOverview: HandoffOperationsOverview) {
  return (
    <section className="panel panel-strong section-stack">
      <div className="section-head">
        <div>
          <p className="eyebrow">Exceções</p>
          <h2>Fila crítica e tickets prioritários</h2>
        </div>
        <span className="status-chip is-pending">{handoffOverview.critical_total} alertas</span>
      </div>

      {handoffOverview.alerts.length === 0 ? (
        <p className="muted-copy">
          Não há exceções abertas no momento. Quando surgir um SLA em atenção, breach ou ticket
          prioritário, ele aparecerá aqui.
        </p>
      ) : (
        <ul className="feed-list">
          {handoffOverview.alerts.map((alert) => (
            <li className="feed-item" key={alert.handoff_id}>
              <div className="feed-head">
                <div>
                  <strong>{alert.ticket_code}</strong>
                  <p className="muted-copy">
                    {formatQueueName(alert.queue_name)} · {formatPriority(alert.priority_code)} ·{' '}
                    {formatSlaState(alert.sla_state)}
                  </p>
                </div>
                <div className="action-row action-row-tight">
                  <Link
                    className="secondary-link"
                    href={buildHandoffHref({
                      handoff: alert.handoff_id,
                    })}
                  >
                    Abrir ticket
                  </Link>
                  <Link
                    className="secondary-link"
                    href={buildHandoffHref({
                      handoff: alert.handoff_id,
                      status: alert.status,
                      queue: alert.queue_name,
                      sla: alert.sla_state,
                    })}
                  >
                    Filtrar fila
                  </Link>
                </div>
              </div>

              <p className="feed-copy">{alert.summary}</p>

              <div className="tag-row">
                <span className="event-tag">{formatDueLabel(alert)}</span>
                <span className="event-tag">
                  Solicitante: {alert.requester_name ?? 'Visitante do bot'}
                </span>
                <span className="event-tag">
                  Responsável: {alert.assigned_operator_name ?? 'Fila livre'}
                </span>
              </div>

              <div className="tag-row">
                {alert.alert_flags.map((flag) => (
                  <span className="event-tag" key={flag}>
                    {formatAlertFlag(flag)}
                  </span>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function renderHandoffBacklogSignals(handoffOverview: HandoffOperationsOverview) {
  return (
    <section className="workspace-grid">
      <article className="panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Prioridade</p>
            <h2>Mix operacional da fila</h2>
          </div>
        </div>

        {handoffOverview.priorities.length === 0 ? (
          <p className="muted-copy">Ainda não há handoffs ativos para segmentar por prioridade.</p>
        ) : (
          <ul className="feed-list">
            {handoffOverview.priorities.map((priority) => (
              <li className="feed-item" key={priority.priority_code}>
                <div className="feed-head">
                  <div>
                    <strong>{formatPriority(priority.priority_code)}</strong>
                    <p className="muted-copy">{priority.open_count} handoffs ativos</p>
                  </div>
                </div>
                <div className="tag-row">
                  <span className="event-tag">Na fila: {priority.queued_count}</span>
                  <span className="event-tag">Em atendimento: {priority.in_progress_count}</span>
                  <span className="event-tag">Atenção: {priority.attention_count}</span>
                  <span className="event-tag">Estourado: {priority.breached_count}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </article>

      <article className="panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Envelhecimento</p>
            <h2>Idade do backlog aberto</h2>
          </div>
        </div>

        <div className="summary-grid summary-grid-compact">
          <article className="metric-card">
            <p className="label">Ticket mais antigo</p>
            <strong>{handoffOverview.oldest_open_ticket_code ?? 'Sem backlog aberto'}</strong>
          </article>
          <article className="metric-card">
            <p className="label">Idade do mais antigo</p>
            <strong>{formatDurationMinutes(handoffOverview.oldest_open_minutes)}</strong>
          </article>
        </div>

        {handoffOverview.aging_buckets.length === 0 ? (
          <p className="muted-copy">Ainda não há handoffs ativos para segmentar por idade.</p>
        ) : (
          <ul className="feed-list">
            {handoffOverview.aging_buckets.map((bucket) => (
              <li className="feed-item" key={bucket.bucket_code}>
                <div className="feed-head">
                  <div>
                    <strong>{bucket.label}</strong>
                    <p className="muted-copy">{bucket.open_count} handoffs ativos</p>
                  </div>
                </div>
                <div className="tag-row">
                  <span className="event-tag">Na fila: {bucket.queued_count}</span>
                  <span className="event-tag">Em atendimento: {bucket.in_progress_count}</span>
                  <span className="event-tag">Atenção: {bucket.attention_count}</span>
                  <span className="event-tag">Estourado: {bucket.breached_count}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </article>
    </section>
  );
}

function renderHandoffOverview(handoffOverview: HandoffOperationsOverview) {
  return (
    <>
      <section className="panel panel-strong section-stack section-anchor" id="handoff-ops">
        <div className="section-head">
          <div>
            <p className="eyebrow">Handoff Ops</p>
            <h2>Saúde operacional da fila humana</h2>
          </div>
          <span className="status-chip is-linked">{handoffOverview.open_total} ativos</span>
        </div>

        <div className="summary-grid summary-grid-compact">
          <Link className="metric-card metric-link-card" href={buildHandoffHref({ status: 'queued' })}>
            <p className="label">Na fila</p>
            <strong>{handoffOverview.queued_total}</strong>
          </Link>
          <Link
            className="metric-card metric-link-card"
            href={buildHandoffHref({ status: 'in_progress' })}
          >
            <p className="label">Em atendimento</p>
            <strong>{handoffOverview.in_progress_total}</strong>
          </Link>
          <Link
            className="metric-card metric-link-card"
            href={buildHandoffHref({ sla: 'attention' })}
          >
            <p className="label">SLA em atenção</p>
            <strong>{handoffOverview.attention_total}</strong>
          </Link>
          <Link
            className="metric-card metric-link-card"
            href={buildHandoffHref({ sla: 'breached' })}
          >
            <p className="label">SLA estourado</p>
            <strong>{handoffOverview.breached_total}</strong>
          </Link>
          <Link
            className="metric-card metric-link-card"
            href={buildHandoffHref({ assignment: 'unassigned' })}
          >
            <p className="label">Sem responsável</p>
            <strong>{handoffOverview.unassigned_total}</strong>
          </Link>
        </div>
      </section>

      {renderHandoffObservability(handoffOverview)}

      {renderHandoffBacklogSignals(handoffOverview)}

      {renderHandoffAlertFeed(handoffOverview)}

      <section className="workspace-grid">
        <article className="panel">
          <div className="section-head">
            <div>
              <p className="eyebrow">Por fila</p>
              <h2>Distribuição por setor</h2>
            </div>
          </div>

          {handoffOverview.queues.length === 0 ? (
            <p className="muted-copy">Ainda não há handoffs ativos para agregar por fila.</p>
          ) : (
            <ul className="feed-list">
              {handoffOverview.queues.map((queue) => (
                <li className="feed-item" key={queue.queue_name}>
                  <div className="feed-head">
                    <div>
                      <strong>{formatQueueName(queue.queue_name)}</strong>
                      <p className="muted-copy">{queue.open_count} handoffs ativos</p>
                    </div>
                  </div>
                  <div className="tag-row">
                    <span className="event-tag">Fila: {queue.queued_count}</span>
                    <span className="event-tag">Em atendimento: {queue.in_progress_count}</span>
                    <span className="event-tag">Atenção: {queue.attention_count}</span>
                    <span className="event-tag">Estourado: {queue.breached_count}</span>
                    <span className="event-tag">Sem responsável: {queue.unassigned_count}</span>
                  </div>
                  <div className="action-row">
                    <Link
                      className="secondary-link"
                      href={buildHandoffHref({ queue: queue.queue_name })}
                    >
                      Ver fila
                    </Link>
                    {queue.breached_count > 0 ? (
                      <Link
                        className="secondary-link"
                        href={buildHandoffHref({ queue: queue.queue_name, sla: 'breached' })}
                      >
                        Ver críticos
                      </Link>
                    ) : null}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="panel">
          <div className="section-head">
            <div>
              <p className="eyebrow">Por operador</p>
              <h2>Carga da equipe</h2>
            </div>
          </div>

          {handoffOverview.operators.length === 0 ? (
            <p className="muted-copy">
              Nenhum operador assumiu handoffs ativos ainda. Os atendimentos não atribuídos
              aparecem como fila livre.
            </p>
          ) : (
            <ul className="feed-list">
              {handoffOverview.operators.map((operator) => (
                <li className="feed-item" key={operator.operator_user_id}>
                  <div className="feed-head">
                    <div>
                      <strong>{operator.operator_name}</strong>
                      <p className="muted-copy">{operator.operator_external_code}</p>
                    </div>
                    <span className="status-chip is-linked">{operator.assigned_count} ativos</span>
                  </div>
                  <div className="tag-row">
                    <span className="event-tag">Fila: {operator.queued_count}</span>
                    <span className="event-tag">Em atendimento: {operator.in_progress_count}</span>
                    <span className="event-tag">Atenção: {operator.attention_count}</span>
                    <span className="event-tag">Estourado: {operator.breached_count}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </article>
      </section>
    </>
  );
}

type HomePageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

function getPositiveIntegerSearchParam(
  value: string | string[] | undefined,
  fallback: number,
): number {
  const raw = getStringSearchParam(value);
  if (!raw) {
    return fallback;
  }

  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

export default async function HomePage({ searchParams }: HomePageProps) {
  const params = (await searchParams) ?? {};
  const authErrorValue = getStringSearchParam(params.authError);
  const requestedHandoffId = getStringSearchParam(params.handoff);
  const requestedConversationId = getStringSearchParam(params.conversationId);
  const currentView = getDashboardView(getStringSearchParam(params.view));
  const authError = authErrorValue ? formatAuthError(authErrorValue) : null;
  const handoffFilters: Partial<SupportHandoffFilters> = {
    status: getStringSearchParam(params.handoffStatus),
    queue_name: getStringSearchParam(params.handoffQueue),
    assignment: getStringSearchParam(params.handoffAssignment),
    sla_state: getStringSearchParam(params.handoffSla),
    search: getStringSearchParam(params.handoffSearch),
    page: getPositiveIntegerSearchParam(params.handoffPage, 1),
    limit: getPositiveIntegerSearchParam(params.handoffLimit, 10),
  };

  const returnToPath = buildReturnToPath(params);
  const { session, error } = await getPortalSession({ allowRefresh: false });
  if (error === 'session_refresh_required') {
    redirect(`/auth/refresh?returnTo=${encodeURIComponent(returnToPath)}`);
  }
  const { overview, error: overviewError } = session
    ? await getOperationsOverview({ allowRefresh: false })
    : { overview: null, error: null };
  const { handoffs, error: handoffsError } = session
    ? await getSupportHandoffs(handoffFilters, { allowRefresh: false })
    : { handoffs: null, error: null };
  const { conversations, error: conversationsError } = session
    ? await getSupportConversations({ allowRefresh: false })
    : { conversations: null, error: null };
  const selectedHandoffId =
    requestedHandoffId ?? (currentView === 'handoffs' ? handoffs?.items[0]?.handoff_id ?? null : null);
  const selectedConversationId = requestedConversationId ?? conversations?.items[0]?.conversation_id ?? null;
  const highlightedHandoffId =
    selectedHandoffId && handoffs?.items.some((item) => item.handoff_id === selectedHandoffId)
      ? selectedHandoffId
      : null;
  const { detail: handoffDetail, error: handoffDetailError } =
    session && selectedHandoffId
      ? await getSupportHandoffDetail(selectedHandoffId, { allowRefresh: false })
      : { detail: null, error: null };
  const { detail: conversationDetail, error: conversationDetailError } =
    session && selectedConversationId
      ? await getSupportConversationDetail(selectedConversationId, { allowRefresh: false })
      : { detail: null, error: null };
  if (
    overviewError === 'session_refresh_required' ||
    handoffsError === 'session_refresh_required' ||
    handoffDetailError === 'session_refresh_required' ||
    conversationsError === 'session_refresh_required' ||
    conversationDetailError === 'session_refresh_required'
  ) {
    redirect(`/auth/refresh?returnTo=${encodeURIComponent(returnToPath)}`);
  }
  const accessHighlights = session ? buildAccessHighlights(session.actor) : [];
  const metricEntries = overview && session
    ? orderMetricEntries(Object.entries(overview.metrics), session.actor.role_code)
    : [];
  const primaryMetricEntries = metricEntries.slice(0, 4);
  const secondaryMetricEntries = metricEntries.slice(4);
  const foundationEntries = overview?.foundation_counts
    ? Object.entries(overview.foundation_counts).sort(([left], [right]) => left.localeCompare(right))
    : [];
  const currentViewHref = (view: DashboardView) =>
    buildHandoffHref({
      view,
      handoff: requestedHandoffId,
      conversationId: requestedConversationId,
      status: handoffFilters.status,
      queue: handoffFilters.queue_name,
      assignment: handoffFilters.assignment,
      sla: handoffFilters.sla_state,
      search: handoffFilters.search,
      page: handoffFilters.page,
      limit: handoffFilters.limit,
    });

  if (!session) {
    return (
      <main className="console-shell">
        {authError ? <p className="feedback error-text">{authError}</p> : null}
        {error ? (
          <p className="feedback warning-text">
            {error === 'session_expired'
              ? 'Sua sessão expirou. Faça login novamente para continuar.'
              : 'Não foi possível confirmar sua sessão agora. Tente novamente em instantes.'}
          </p>
        ) : null}

        <section className="landing-stage">
          <div className="landing-copy">
            <p className="eyebrow">Portal EduAssist</p>
            <h1>A vida escolar em um só lugar.</h1>
            <p className="lede">
              Acesse sua conta para acompanhar atendimento, conectar o Telegram e consultar os
              recursos disponíveis no seu perfil.
            </p>

            <div className="landing-actions">
              <a className="primary-button" href="/auth/login">
                Entrar
              </a>
              <div className="login-hint" tabIndex={0}>
                <span className="login-hint-trigger">Acesso de demonstração</span>
                <div className="login-hint-popover">
                  <p className="label">Credenciais de acesso</p>
                  <ul className="login-hint-list">
                    {demoAccounts.map((account) => (
                      <li key={account.username}>
                        <strong>{account.role}</strong>
                        <span>{account.username}</span>
                        <code>{account.password}</code>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            <div className="account-badge-row">
              {landingHighlights.map((item) => (
                <span className="account-badge" key={item}>
                  {item}
                </span>
              ))}
            </div>
          </div>

          <aside className="showcase-card">
            <div className="showcase-surface">
              <div className="showcase-toolbar">
                <span />
                <span />
                <span />
              </div>
              <div className="showcase-kicker">O que você encontra</div>
              <div className="showcase-title">Atendimento, conta e escola com mais clareza.</div>
              <div className="showcase-grid">
                <article className="showcase-mini-card">
                  <p>Conta</p>
                  <strong>Perfil, acesso e sessão</strong>
                </article>
                <article className="showcase-mini-card">
                  <p>Telegram</p>
                  <strong>Conexão com o bot da escola</strong>
                </article>
                <article className="showcase-mini-card">
                  <p>Atendimento</p>
                  <strong>Solicitações, protocolos e fila</strong>
                </article>
                <article className="showcase-mini-card">
                  <p>Escola</p>
                  <strong>Informações e contexto do seu perfil</strong>
                </article>
              </div>
            </div>
          </aside>
        </section>
      </main>
    );
  }

  return (
    <main className="console-shell console-shell-dashboard">
      <section className="masthead masthead-dashboard">
        <div>
          <p className="eyebrow">Portal EduAssist</p>
          <h1>{session.actor.full_name}</h1>
          <p className="lede">{buildRoleSummary(session.actor)}</p>
          <div className="hero-status-row">
            <span className="status-chip is-linked">{formatRole(session.actor.role_code)}</span>
            <span className="status-chip is-linked">{formatScope(overview?.scope ?? 'personal')}</span>
            <span className={`status-chip ${session.actor.telegram_linked ? 'is-linked' : 'is-pending'}`}>
              Telegram {session.actor.telegram_linked ? 'vinculado' : 'pendente'}
            </span>
          </div>
        </div>

        <form action="/auth/logout" method="post">
          <button className="secondary-button" type="submit">
            Encerrar sessão
          </button>
        </form>
      </section>

      <nav aria-label="Navegação do painel" className="section-nav">
        <Link
          className={`section-nav-link ${currentView === 'overview' ? 'is-active' : ''}`}
          href={currentViewHref('overview')}
        >
          Visão geral
        </Link>
        {overview?.handoff_overview ? (
          <Link
            className={`section-nav-link ${currentView === 'handoffs' ? 'is-active' : ''}`}
            href={currentViewHref('handoffs')}
          >
            Fila humana
          </Link>
        ) : null}
        <Link
          className={`section-nav-link ${currentView === 'conversation' ? 'is-active' : ''}`}
          href={currentViewHref('conversation')}
        >
          Conversa
        </Link>
        <Link
          className={`section-nav-link ${currentView === 'account' ? 'is-active' : ''}`}
          href={currentViewHref('account')}
        >
          Conta
        </Link>
        {(secondaryMetricEntries.length > 0 ||
          foundationEntries.length > 0 ||
          overview?.audit_events.length ||
          overview?.access_decisions.length) ? (
          <Link
            className={`section-nav-link ${currentView === 'details' ? 'is-active' : ''}`}
            href={currentViewHref('details')}
          >
            Detalhes
          </Link>
        ) : null}
      </nav>

      {overviewError ? (
        <p className="feedback warning-text">
          Não foi possível atualizar o painel completo agora. Alguns dados podem demorar um pouco
          para aparecer.
        </p>
      ) : null}

      {overview ? (
        <>
          {currentView === 'overview' ? (
            <section className="dashboard-grid">
              <div className="dashboard-main">
                <section className="panel panel-strong dashboard-hero">
                  <div className="section-head">
                    <div>
                      <p className="eyebrow">Prioridades</p>
                      <h2>Resumo do momento</h2>
                      <p className="section-copy">
                        Os principais sinais da sua conta aparecem aqui primeiro, com acesso rápido
                        ao restante do portal.
                      </p>
                    </div>
                    <span className="status-chip is-linked">
                      {formatRole(overview.actor.role_code)}
                    </span>
                  </div>

                  <div className="metric-strip">
                    {primaryMetricEntries.map(([metricKey, value]) => (
                      <article className="metric-card" key={metricKey}>
                        <p className="label">{formatMetricLabel(metricKey)}</p>
                        <strong>{value}</strong>
                      </article>
                    ))}
                  </div>
                </section>

                {overview.handoff_overview ? renderCompactHandoffSummary(overview.handoff_overview) : null}
              </div>

              <aside className="dashboard-rail">
                <article className="panel panel-strong snapshot-panel">
                  <div className="section-head">
                    <div>
                      <p className="eyebrow">Conta</p>
                      <h2>Visão rápida</h2>
                    </div>
                    <span className="status-chip is-linked">{session.principal.provider}</span>
                  </div>

                  <dl className="snapshot-list">
                    <div>
                      <dt>Usuário</dt>
                      <dd>{session.principal.preferred_username ?? session.actor.external_code}</dd>
                    </div>
                    <div>
                      <dt>Email</dt>
                      <dd>{session.principal.email ?? 'não informado'}</dd>
                    </div>
                    <div>
                      <dt>Telegram</dt>
                      <dd>{session.actor.telegram_linked ? 'Conectado' : 'Pendente'}</dd>
                    </div>
                  </dl>
                </article>

                <LinkChallengePanel initiallyLinked={session.actor.telegram_linked} />
              </aside>
            </section>
          ) : null}

          {currentView === 'handoffs' ? (
            <section className="view-stack">
              {handoffsError ? (
                <p className="feedback warning-text">
                  A lista de atendimentos não respondeu agora. Tente novamente em instantes.
                </p>
              ) : null}
              {overview.handoff_overview ? renderHandoffOverview(overview.handoff_overview) : null}
              {handoffs ? (
                <SupportHandoffPanel
                  canManage={handoffs.scope === 'global'}
                  counts={handoffs.counts}
                  filters={handoffs.filters}
                  items={handoffs.items}
                  pagination={handoffs.pagination}
                  scope={handoffs.scope}
                  selectedHandoffId={highlightedHandoffId}
                />
              ) : null}
            </section>
          ) : null}

          {currentView === 'conversation' ? (
            <section className="view-stack">
              {requestedHandoffId && handoffDetailError ? (
                <p className="feedback warning-text">
                  Não foi possível carregar esta conversa agora.
                </p>
              ) : null}
              {conversationsError ? (
                <p className="feedback warning-text">
                  Não foi possível atualizar o histórico de conversas agora.
                </p>
              ) : null}
              {conversationDetailError && !requestedHandoffId ? (
                <p className="feedback warning-text">
                  Não foi possível carregar o histórico selecionado agora.
                </p>
              ) : null}
              {requestedHandoffId && handoffDetail ? (
                <SupportHandoffDetailPanel
                  canManage={handoffs?.scope === 'global'}
                  detail={handoffDetail}
                />
              ) : (
                <ConversationHistoryPanel
                  detail={conversationDetail}
                  items={(conversations?.items ?? []).map((item) => ({
                    ...item,
                    href: buildHandoffHref({
                      view: 'conversation',
                      handoff: null,
                      conversationId: item.conversation_id,
                      status: handoffFilters.status,
                      queue: handoffFilters.queue_name,
                      assignment: handoffFilters.assignment,
                      sla: handoffFilters.sla_state,
                      search: handoffFilters.search,
                      page: handoffFilters.page,
                      limit: handoffFilters.limit,
                    }),
                    is_active: conversationDetail?.item.conversation_id === item.conversation_id,
                  }))}
                />
              )}
            </section>
          ) : null}

          {currentView === 'account' ? (
            <section className="dashboard-grid">
              <div className="dashboard-main">
                <article className="panel panel-strong">
                  <div className="section-head">
                    <div>
                      <p className="eyebrow">Sessão</p>
                      <h2>Conta e acessos</h2>
                    </div>
                    <span className="status-chip is-linked">{session.principal.provider}</span>
                  </div>

                  <dl className="snapshot-list">
                    <div>
                      <dt>Usuário</dt>
                      <dd>{session.principal.preferred_username ?? session.actor.external_code}</dd>
                    </div>
                    <div>
                      <dt>Código interno</dt>
                      <dd>{session.actor.external_code}</dd>
                    </div>
                    <div>
                      <dt>Email</dt>
                      <dd>{session.principal.email ?? 'não informado'}</dd>
                    </div>
                    <div>
                      <dt>Cliente OIDC</dt>
                      <dd>{session.principal.azp ?? 'n/d'}</dd>
                    </div>
                  </dl>

                  <div className="section-block">
                    <p className="label">Acessos disponíveis nesta conta</p>
                    {accessHighlights.length > 0 ? (
                      <ul className="rail-list">
                        {accessHighlights.map((item) => (
                          <li key={item}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="muted-copy">
                        Não há vínculos acadêmicos ou turmas disponíveis neste perfil no momento.
                      </p>
                    )}
                  </div>
                </article>
              </div>

              <aside className="dashboard-rail">
                <LinkChallengePanel initiallyLinked={session.actor.telegram_linked} />
              </aside>
            </section>
          ) : null}

          {currentView === 'details' ? (
            <section className="view-stack">
              {secondaryMetricEntries.length > 0 ? (
                <section className="panel panel-strong">
                  <div className="section-head">
                    <div>
                      <p className="eyebrow">Indicadores</p>
                      <h2>Indicadores complementares</h2>
                    </div>
                  </div>
                  <div className="summary-grid summary-grid-compact">
                    {secondaryMetricEntries.map(([metricKey, value]) => (
                      <article className="metric-card" key={metricKey}>
                        <p className="label">{formatMetricLabel(metricKey)}</p>
                        <strong>{value}</strong>
                      </article>
                    ))}
                  </div>
                </section>
              ) : null}

              {foundationEntries.length > 0 ? (
                <section className="panel">
                  <div className="section-head">
                    <div>
                      <p className="eyebrow">Base estrutural</p>
                      <h2>Base da operação</h2>
                    </div>
                  </div>
                  <div className="count-grid">
                    {foundationEntries.map(([key, value]) => (
                      <div className="count-item" key={key}>
                        <span>{formatMetricLabel(key)}</span>
                        <strong>{value}</strong>
                      </div>
                    ))}
                  </div>
                </section>
              ) : null}

              <section className="workspace-grid">
                <article className="panel">
                  <div className="section-head">
                    <div>
                      <p className="eyebrow">Auditoria</p>
                      <h2>Eventos recentes</h2>
                    </div>
                  </div>
                  {renderAuditFeed(overview.audit_events, overview)}
                </article>

                <article className="panel">
                  <div className="section-head">
                    <div>
                      <p className="eyebrow">Autorização</p>
                      <h2>Decisões recentes</h2>
                    </div>
                  </div>
                  {renderAccessDecisions(overview.access_decisions, overview)}
                </article>
              </section>
            </section>
          ) : null}
        </>
      ) : null}
    </main>
  );
}
