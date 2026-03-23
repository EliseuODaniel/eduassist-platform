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
          <h2>Vincular conta do bot</h2>
        </div>
        <span className={`status-chip ${initiallyLinked ? 'is-linked' : 'is-pending'}`}>
          {initiallyLinked ? 'Conta já vinculada' : 'Vínculo pendente'}
        </span>
      </div>

      <p className="section-copy">
        Gere um código temporário para associar esta sessão web à conta do Telegram. O
        vínculo é concluído pelo comando enviado ao bot.
      </p>

      <button
        className="primary-button"
        disabled={isPending}
        onClick={handleGenerateChallenge}
        type="button"
      >
        {isPending ? 'Gerando código...' : initiallyLinked ? 'Gerar novo código' : 'Gerar código'}
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
              Abrir deep link do Telegram
            </a>
          ) : null}

          <p className="challenge-note">
            Envie o comando ao bot para concluir o vínculo. Se já existir uma conta ligada,
            este novo código substitui a tentativa anterior.
          </p>
        </div>
      ) : null}
    </article>
  );
}
