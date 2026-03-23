import Link from 'next/link';

import { LinkChallengePanel } from './link-challenge-panel';
import { SupportHandoffDetailPanel } from './support-handoff-detail-panel';
import { SupportHandoffPanel } from './support-handoff-panel';
import {
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

const demoAccounts = [
  { role: 'Responsável', username: 'maria.oliveira' },
  { role: 'Professora', username: 'helena.rocha' },
  { role: 'Financeiro', username: 'carla.nogueira' },
];

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
                <Link className="secondary-link" href={`/?handoff=${alert.handoff_id}`}>
                  Abrir ticket
                </Link>
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

function renderHandoffOverview(handoffOverview: HandoffOperationsOverview) {
  return (
    <>
      <section className="panel panel-strong section-stack">
        <div className="section-head">
          <div>
            <p className="eyebrow">Handoff Ops</p>
            <h2>Saúde operacional da fila humana</h2>
          </div>
          <span className="status-chip is-linked">{handoffOverview.open_total} ativos</span>
        </div>

        <div className="summary-grid summary-grid-compact">
          <article className="metric-card">
            <p className="label">Na fila</p>
            <strong>{handoffOverview.queued_total}</strong>
          </article>
          <article className="metric-card">
            <p className="label">Em atendimento</p>
            <strong>{handoffOverview.in_progress_total}</strong>
          </article>
          <article className="metric-card">
            <p className="label">SLA em atenção</p>
            <strong>{handoffOverview.attention_total}</strong>
          </article>
          <article className="metric-card">
            <p className="label">SLA estourado</p>
            <strong>{handoffOverview.breached_total}</strong>
          </article>
          <article className="metric-card">
            <p className="label">Sem responsável</p>
            <strong>{handoffOverview.unassigned_total}</strong>
          </article>
        </div>
      </section>

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

export default async function HomePage({ searchParams }: HomePageProps) {
  const params = (await searchParams) ?? {};
  const authErrorValue = getStringSearchParam(params.authError);
  const requestedHandoffId = getStringSearchParam(params.handoff);
  const authError = authErrorValue ? formatAuthError(authErrorValue) : null;
  const handoffFilters: Partial<SupportHandoffFilters> = {
    status: getStringSearchParam(params.handoffStatus),
    queue_name: getStringSearchParam(params.handoffQueue),
    assignment: getStringSearchParam(params.handoffAssignment),
    sla_state: getStringSearchParam(params.handoffSla),
    search: getStringSearchParam(params.handoffSearch),
  };

  const { session, error } = await getPortalSession();
  const { overview, error: overviewError } = session
    ? await getOperationsOverview()
    : { overview: null, error: null };
  const { handoffs, error: handoffsError } = session
    ? await getSupportHandoffs(handoffFilters)
    : { handoffs: null, error: null };
  const selectedHandoffId = requestedHandoffId ?? handoffs?.items[0]?.handoff_id ?? null;
  const highlightedHandoffId =
    selectedHandoffId && handoffs?.items.some((item) => item.handoff_id === selectedHandoffId)
      ? selectedHandoffId
      : null;
  const { detail: handoffDetail, error: handoffDetailError } =
    session && selectedHandoffId
      ? await getSupportHandoffDetail(selectedHandoffId)
      : { detail: null, error: null };
  const accessHighlights = session ? buildAccessHighlights(session.actor) : [];
  const metricEntries = overview ? Object.entries(overview.metrics) : [];
  const foundationEntries = overview?.foundation_counts
    ? Object.entries(overview.foundation_counts).sort(([left], [right]) => left.localeCompare(right))
    : [];

  if (!session) {
    return (
      <main className="console-shell">
        <section className="masthead">
          <div>
            <p className="eyebrow">EduAssist Operator Console</p>
            <h1>Painel seguro para operar o chatbot escolar e vincular o Telegram.</h1>
          </div>
          <a className="primary-button" href="/auth/login">
            Entrar com Keycloak
          </a>
        </section>

        {authError ? <p className="feedback error-text">{authError}</p> : null}
        {error ? (
          <p className="feedback warning-text">
            {error === 'session_expired'
              ? 'Sua sessão expirou. Faça login novamente para continuar.'
              : 'O painel não conseguiu validar a sessão atual contra o api-core.'}
          </p>
        ) : null}

        <section className="hero-panel">
          <div className="hero-copy">
            <p className="eyebrow">Primeira vertical operacional</p>
            <h2>Login real, sessão autenticada e emissão de challenge para o bot.</h2>
            <p>
              Esta interface usa o `Keycloak` local como provedor OIDC, consome a sessão
              autenticada do `api-core` e permite gerar o código temporário que o usuário
              envia ao bot via `/start link_...`.
            </p>
          </div>

          <aside className="credential-panel">
            <h3>Contas mockadas para teste local</h3>
            <p className="muted-copy">Senha padrão para as contas abaixo: `Eduassist123!`</p>
            <ul className="account-list">
              {demoAccounts.map((account) => (
                <li key={account.username}>
                  <strong>{account.role}</strong>
                  <span>{account.username}</span>
                </li>
              ))}
            </ul>
          </aside>
        </section>
      </main>
    );
  }

  return (
    <main className="console-shell">
      <section className="masthead">
        <div>
          <p className="eyebrow">EduAssist Operator Console</p>
          <h1>{session.actor.full_name}</h1>
          <p className="lede">
            Sessão autenticada via {session.auth_mode}. Este painel já reflete as permissões
            do perfil e opera sobre o vínculo do Telegram.
          </p>
        </div>

        <form action="/auth/logout" method="post">
          <button className="secondary-button" type="submit">
            Encerrar sessão
          </button>
        </form>
      </section>

      <section className="summary-grid">
        <article className="panel metric-card">
          <p className="label">Papel</p>
          <strong>{formatRole(session.actor.role_code)}</strong>
        </article>
        <article className="panel metric-card">
          <p className="label">Usuário</p>
          <strong>{session.principal.preferred_username ?? session.actor.external_code}</strong>
        </article>
        <article className="panel metric-card">
          <p className="label">Código interno</p>
          <strong>{session.actor.external_code}</strong>
        </article>
        <article className="panel metric-card">
          <p className="label">Telegram</p>
          <strong>{session.actor.telegram_linked ? 'Vinculado' : 'Pendente'}</strong>
        </article>
      </section>

      <section className="workspace-grid">
        <article className="panel panel-strong">
          <div className="section-head">
            <div>
              <p className="eyebrow">Sessão</p>
              <h2>Escopo operacional ativo</h2>
            </div>
            <span className="status-chip is-linked">{session.principal.provider}</span>
          </div>

          <div className="detail-grid">
            <div>
              <p className="label">Email</p>
              <strong>{session.principal.email ?? 'não informado'}</strong>
            </div>
            <div>
              <p className="label">Cliente OIDC</p>
              <strong>{session.principal.azp ?? 'n/d'}</strong>
            </div>
          </div>

          <div className="section-block">
            <p className="label">Acessos visíveis nesta conta</p>
            {accessHighlights.length > 0 ? (
              <ul className="access-list">
                {accessHighlights.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="muted-copy">
                Este perfil não tem vínculos acadêmicos ou turmas listadas no resumo atual.
              </p>
            )}
          </div>
        </article>

        <LinkChallengePanel initiallyLinked={session.actor.telegram_linked} />
      </section>

      {overviewError ? (
        <p className="feedback warning-text">
          O painel autenticou corretamente, mas não conseguiu carregar o overview operacional do
          `api-core`.
        </p>
      ) : null}

      {overview ? (
        <>
          {handoffsError ? (
            <p className="feedback warning-text">
              O overview operacional carregou, mas a fila de handoffs não respondeu agora.
            </p>
          ) : null}

          <section className="panel panel-strong section-stack">
            <div className="section-head">
              <div>
                <p className="eyebrow">Operação</p>
                <h2>{formatScope(overview.scope)}</h2>
              </div>
              <span className="status-chip is-linked">{formatRole(overview.actor.role_code)}</span>
            </div>

            <div className="summary-grid summary-grid-compact">
              {metricEntries.map(([metricKey, value]) => (
                <article className="metric-card" key={metricKey}>
                  <p className="label">{formatMetricLabel(metricKey)}</p>
                  <strong>{value}</strong>
                </article>
              ))}
            </div>

            {foundationEntries.length > 0 ? (
              <div className="section-block">
                <p className="label">Contagem estrutural do ambiente</p>
                <div className="count-grid">
                  {foundationEntries.map(([key, value]) => (
                    <div className="count-item" key={key}>
                      <span>{formatMetricLabel(key)}</span>
                      <strong>{value}</strong>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </section>

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

          {overview.handoff_overview ? renderHandoffOverview(overview.handoff_overview) : null}

          {handoffs ? (
            <>
              <SupportHandoffPanel
                canManage={handoffs.scope === 'global'}
                counts={handoffs.counts}
                filters={handoffs.filters}
                items={handoffs.items}
                scope={handoffs.scope}
                selectedHandoffId={highlightedHandoffId}
              />

              {handoffDetailError ? (
                <p className="feedback warning-text">
                  A fila carregou, mas o detalhe da conversa selecionada não respondeu agora.
                </p>
              ) : null}

              {handoffDetail ? (
                <SupportHandoffDetailPanel
                  canManage={handoffs.scope === 'global'}
                  detail={handoffDetail}
                />
              ) : null}
            </>
          ) : null}
        </>
      ) : null}
    </main>
  );
}
