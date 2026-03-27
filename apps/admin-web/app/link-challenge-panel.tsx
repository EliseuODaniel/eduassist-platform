'use client';

import { useState, useTransition } from 'react';

type ChallengePayload = {
  challenge_code: string;
  expires_at: string;
  bot_username: string | null;
  telegram_deep_link: string | null;
  telegram_command: string;
};

type Props = {
  initiallyLinked: boolean;
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

export function LinkChallengePanel({ initiallyLinked }: Props) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [challenge, setChallenge] = useState<ChallengePayload | null>(null);

  function handleGenerateChallenge() {
    startTransition(async () => {
      setError(null);

      const response = await fetch('/api/telegram-link/challenge', {
        method: 'POST',
        headers: {
          Accept: 'application/json',
        },
      });

      const payload = (await response.json()) as Partial<ChallengePayload> & {
        error?: string;
      };

      if (!response.ok) {
        setChallenge(null);
        setError(
          payload.error === 'not_authenticated'
            ? 'Sua sessão do painel expirou. Faça login novamente para gerar o código.'
            : 'Não consegui gerar o código agora. Tente novamente em instantes.',
        );
        return;
      }

      setChallenge(payload as ChallengePayload);
    });
  }

  return (
    <article className="panel panel-strong">
      <div className="section-head">
        <div>
          <p className="eyebrow">Telegram</p>
          <h2>Conectar ao Telegram</h2>
        </div>
        <span className={`status-chip ${initiallyLinked ? 'is-linked' : 'is-pending'}`}>
          {initiallyLinked ? 'Conectado' : 'Pendente'}
        </span>
      </div>

      <p className="section-copy">
        Conecte sua conta ao bot do Telegram para continuar atendimentos e acessar recursos do seu
        perfil também pelo chat.
      </p>

      <button
        className="primary-button"
        disabled={isPending}
        onClick={handleGenerateChallenge}
        type="button"
      >
        {isPending ? 'Gerando código...' : initiallyLinked ? 'Gerar novo código' : 'Gerar código de conexão'}
      </button>

      {error ? <p className="feedback error-text">{error}</p> : null}

      {challenge ? (
        <div className="challenge-card">
          <div className="challenge-grid">
            <div>
              <p className="label">Comando</p>
              <code>{challenge.telegram_command}</code>
            </div>
            <div>
              <p className="label">Expira em</p>
              <strong>{formatDateTime(challenge.expires_at)}</strong>
            </div>
          </div>

          {challenge.telegram_deep_link ? (
            <a className="secondary-link" href={challenge.telegram_deep_link} rel="noreferrer">
              Abrir no Telegram
            </a>
          ) : null}

          <p className="challenge-note">
            Envie o comando ao bot para concluir a conexão. Se você gerar um novo código, o
            anterior deixa de valer.
          </p>
        </div>
      ) : null}
    </article>
  );
}
