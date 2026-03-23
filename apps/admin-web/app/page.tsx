import { LinkChallengePanel } from './link-challenge-panel';
import { getPortalSession, type PortalActor } from '../lib/auth';

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

type HomePageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

export default async function HomePage({ searchParams }: HomePageProps) {
  const params = (await searchParams) ?? {};
  const authErrorValue = params.authError;
  const authError =
    typeof authErrorValue === 'string' && authErrorValue.length > 0
      ? formatAuthError(authErrorValue)
      : null;

  const { session, error } = await getPortalSession();
  const accessHighlights = session ? buildAccessHighlights(session.actor) : [];

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
    </main>
  );
}
