import Link from 'next/link';

import type { SupportConversationDetail, SupportConversationThread } from '../lib/auth';

type ConversationThreadWithHref = SupportConversationThread & {
  href: string;
  is_active: boolean;
};

type Props = {
  items: ConversationThreadWithHref[];
  detail: SupportConversationDetail | null;
};

function formatDateTime(value: string | null): string {
  if (!value) {
    return 'n/d';
  }
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
    open: 'Aberta',
    closed: 'Fechada',
    queued: 'Na fila',
    in_progress: 'Em atendimento',
    resolved: 'Resolvido',
    cancelled: 'Cancelado',
  };
  return labels[status] ?? status;
}

function formatSender(senderType: string): string {
  const labels: Record<string, string> = {
    user: 'Você',
    operator: 'Equipe',
    assistant: 'EduAssist',
    system: 'Sistema',
  };
  return labels[senderType] ?? senderType;
}

function formatQueue(queueName: string | null): string {
  if (!queueName) {
    return 'Atendimento';
  }
  const labels: Record<string, string> = {
    atendimento: 'Atendimento',
    secretaria: 'Secretaria',
    financeiro: 'Financeiro',
    coordenacao: 'Coordenação',
    direcao: 'Direção',
    admissoes: 'Admissões',
  };
  return labels[queueName] ?? queueName;
}

function formatThreadTitle(externalThreadId: string): string {
  if (externalThreadId.startsWith('telegram:')) {
    const suffix = externalThreadId.replace(/^telegram:/, '');
    return `Telegram ${suffix}`;
  }
  if (externalThreadId.startsWith('tg-')) {
    return `Telegram ${externalThreadId.replace(/^tg-/, '')}`;
  }
  return externalThreadId;
}

export function ConversationHistoryPanel({ items, detail }: Props) {
  if (items.length === 0) {
    return (
      <section className="panel panel-strong empty-state-panel">
        <p className="eyebrow">Conversa</p>
        <h2>Nenhuma conversa do Telegram foi encontrada.</h2>
        <p className="muted-copy">
          Quando houver mensagens associadas a esta conta, o histórico vai aparecer aqui com o
          conteúdo da conversa e os atendimentos relacionados.
        </p>
      </section>
    );
  }

  return (
    <section className="conversation-browser">
      <aside className="panel conversation-list-panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Conversa</p>
            <h2>Histórico recente</h2>
          </div>
        </div>

        <div className="conversation-list">
          {items.map((item) => (
            <Link
              className={`conversation-list-link ${item.is_active ? 'is-active' : ''}`}
              href={item.href}
              key={item.conversation_id}
            >
              <div className="conversation-list-head">
                <strong>{formatThreadTitle(item.external_thread_id)}</strong>
                <span className="timestamp-chip">{formatDateTime(item.latest_message_at ?? item.updated_at)}</span>
              </div>
              <p className="muted-copy">
                {item.last_message_excerpt ?? 'Sem mensagens visíveis neste histórico.'}
              </p>
              <div className="tag-row">
                <span className="event-tag">{formatStatus(item.conversation_status)}</span>
                <span className="event-tag">{item.message_count} mensagens</span>
                {item.linked_ticket_code ? (
                  <span className="event-tag">{item.linked_ticket_code}</span>
                ) : null}
              </div>
            </Link>
          ))}
        </div>
      </aside>

      <article className="panel panel-strong">
        {detail ? (
          <>
            <div className="section-head">
              <div>
                <p className="eyebrow">Conversa em foco</p>
                <h2>{formatThreadTitle(detail.item.external_thread_id)}</h2>
                <p className="muted-copy">
                  {formatStatus(detail.item.conversation_status)} · Última atividade em{' '}
                  {formatDateTime(detail.item.latest_message_at ?? detail.item.updated_at)}
                </p>
              </div>
              <span className="status-chip is-linked">{detail.item.message_count} mensagens</span>
            </div>

            <div className="detail-grid">
              <div>
                <p className="label">Canal</p>
                <strong>{detail.item.channel}</strong>
              </div>
              <div>
                <p className="label">Atendimento vinculado</p>
                <strong>
                  {detail.item.linked_ticket_code
                    ? `${detail.item.linked_ticket_code} · ${formatQueue(detail.item.linked_queue_name)}`
                    : 'Sem encaminhamento humano'}
                </strong>
              </div>
              <div>
                <p className="label">Criada em</p>
                <strong>{formatDateTime(detail.item.created_at)}</strong>
              </div>
              <div>
                <p className="label">Atualizada em</p>
                <strong>{formatDateTime(detail.item.updated_at)}</strong>
              </div>
            </div>

            {detail.item.linked_ticket_code ? (
              <div className="tag-row">
                <span className="event-tag">{detail.item.linked_ticket_code}</span>
                <span className="event-tag">{formatQueue(detail.item.linked_queue_name)}</span>
                <span className="event-tag">
                  {formatStatus(detail.item.linked_ticket_status ?? detail.item.conversation_status)}
                </span>
              </div>
            ) : null}

            <div className="section-block">
              <p className="label">Mensagens</p>
              {detail.messages.length === 0 ? (
                <p className="muted-copy">Ainda não há mensagens visíveis neste histórico.</p>
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
          </>
        ) : (
          <section className="empty-state-panel">
            <p className="eyebrow">Conversa</p>
            <h2>Escolha uma conversa para ver o histórico.</h2>
            <p className="muted-copy">
              O conteúdo da conversa aparece aqui assim que você selecionar um item na lista ao
              lado.
            </p>
          </section>
        )}
      </article>
    </section>
  );
}
