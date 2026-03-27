import Link from 'next/link';

export default function NotFound() {
  return (
    <main className="console-shell">
      <section className="masthead">
        <div>
          <p className="eyebrow">Portal EduAssist</p>
          <h1>Página não encontrada</h1>
          <p className="lede">
            O conteúdo que você tentou acessar não está disponível neste portal. Volte para a
            página inicial e continue a navegação por lá.
          </p>
        </div>
        <Link className="primary-button" href="/">
          Voltar ao início
        </Link>
      </section>
    </main>
  );
}
