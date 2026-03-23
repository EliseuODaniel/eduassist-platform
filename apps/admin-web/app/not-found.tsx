import Link from 'next/link';

export default function NotFound() {
  return (
    <main className="console-shell">
      <section className="masthead">
        <div>
          <p className="eyebrow">EduAssist Operator Console</p>
          <h1>Página não encontrada</h1>
          <p className="lede">
            O recurso solicitado não existe neste painel operacional. Use a navegação principal
            ou volte para a home autenticada.
          </p>
        </div>
        <Link className="primary-button" href="/">
          Voltar ao painel
        </Link>
      </section>
    </main>
  );
}
