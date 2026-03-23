const services = [
  {
    name: 'api-core',
    description: 'Regras de negócio, policy checks e domínio principal.',
  },
  {
    name: 'ai-orchestrator',
    description: 'Tool calling, retrieval e composição governada de respostas.',
  },
  {
    name: 'telegram-gateway',
    description: 'Webhook do Telegram, normalização e segurança do canal.',
  },
  {
    name: 'worker',
    description: 'Jobs assíncronos para ingestão, seeds e tarefas de manutenção.',
  },
];

export default function HomePage() {
  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">EduAssist Platform</p>
        <h1>Bootstrap técnico do ecossistema escolar com IA.</h1>
        <p className="lede">
          Esta interface confirma que o novo repositório já tem espinha dorsal real:
          serviços containerizados, bases de infraestrutura e uma separação explícita
          entre canal, domínio, IA e segurança.
        </p>
      </section>

      <section className="grid">
        {services.map((service) => (
          <article className="card" key={service.name}>
            <h2>{service.name}</h2>
            <p>{service.description}</p>
          </article>
        ))}
      </section>

      <section className="footnote">
        <p>
          Próximo marco: conectar autenticação, modelagem relacional, geração de dados
          mockados e a primeira vertical funcional de FAQ pública.
        </p>
      </section>
    </main>
  );
}

