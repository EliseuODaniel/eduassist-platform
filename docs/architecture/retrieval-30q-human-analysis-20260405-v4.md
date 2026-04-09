# Leitura Humana da Bateria 30Q Final

## Contexto

Este relatório registra a leitura humana da bateria `30Q` inédita, rodada após a consolidação da arquitetura final do EduAssistAI.

Artefatos-base:

- dataset: [retrieval_30q_probe_cases.generated.20260405.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_30q_probe_cases.generated.20260405.json)
- relatório quantitativo: [retrieval-30q-cross-path-report-20260405-v4.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-30q-cross-path-report-20260405-v4.md)
- relatório quantitativo json: [retrieval-30q-cross-path-report-20260405-v4.json](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-30q-cross-path-report-20260405-v4.json)

Resultado global:

- `langgraph`: `30/30`, `quality_avg 100.0`
- `python_functions`: `30/30`, `quality_avg 100.0`
- `llamaindex`: `30/30`, `quality_avg 100.0`
- `specialist_supervisor`: `30/30`, `quality_avg 100.0`

## Leitura geral

As respostas finais ficaram boas de verdade, não apenas alinhadas ao rubric automático. O sistema chegou a um ponto em que:

- respostas públicas canônicas saem no domínio certo;
- follow-ups protegidos agregados por família funcionam;
- perguntas de `known unknown` assumem explicitamente quando a escola não publica o dado;
- projeções públicas e comparações processuais respondem de modo concreto;
- não houve misroute grave, vazamento de assunto anterior ou clarificação desnecessária persistente.

## Agrupamento por tipo de pergunta

### 1. Políticas públicas e encadeamentos institucionais

Casos:

- `public_policy_bridge`
- `public_conduct_frequency_punctuality`
- `public_health_emergency_bundle`
- `public_outings_authorizations`

Leitura:

- As respostas conectam corretamente política, fluxo e consequência prática.
- O texto não fica genérico nem “motivacional”; ele mantém tom institucional grounded.
- O sistema deixou de responder só com trechos soltos de regulamento e passou a costurar o protocolo de forma útil.

### 2. Timeline, onboarding e fronteira público/autenticado

Casos:

- `public_timeline`
- `public_family_new_bundle`
- `public_year_three_phases`
- `public_visibility_boundary`
- `public_first_month_risks`

Leitura:

- O eixo público ficou muito forte.
- As respostas organizam o ciclo de entrada, início de aulas, reuniões e agenda de avaliação de forma cronológica e concreta.
- A fronteira entre `portal/calendário público` e `autenticação` ficou finalmente clara.

### 3. Apoio pedagógico, facilities e permanência

Casos:

- `public_permanence_support`
- `public_deep_multi_doc`
- `public_section_aware`
- `public_integral_study_support`
- `public_transport_uniform_bundle`
- `public_inclusion_accessibility`

Leitura:

- As respostas ficaram adaptadas à pergunta, sem cair em bundle errado.
- O sistema consegue ligar biblioteca, laboratórios, monitoria, contraturno e rotina de estudos sem parecer busca keyword-based.
- Em inclusão, acessibilidade e segurança, a resposta ficou sintética e institucionalmente plausível.

### 4. Pricing, bolsas e processos

Casos:

- `public_bolsas_and_processes`
- `public_pricing_projection`

Leitura:

- Esse era um dos piores grupos em ciclos anteriores e ficou resolvido.
- `bolsas + rematrícula + transferência + cancelamento` agora responde como panorama processual, não como tabela de preços.
- A projeção para `3 filhos` passou a incluir corretamente matrícula total e mensalidade de referência por mês.

### 5. Known unknowns

Casos:

- `public_known_unknown_total_teachers`
- `public_known_unknown_library_books`
- `public_known_unknown_cafeteria_menu`

Leitura:

- O sistema agora responde com honestidade forte: “a pergunta é válida, mas esse dado não está publicado oficialmente”.
- Isso melhorou muito a experiência e a credibilidade do bot.
- A resposta não parece evasiva nem inventa valor ausente.

### 6. SQL/protected estruturado

Casos:

- `protected_structured_academic`
- `protected_structured_followup`
- `protected_structured_finance`
- `protected_structured_admin`
- `protected_structured_upcoming_assessments`
- `protected_structured_upcoming_assessments_followup`

Leitura:

- O sistema ficou finalmente forte em agregados protegidos.
- `meus dois filhos` produz panorama acadêmico agregado e destaca quem está mais perto do corte.
- `Agora foque só na Ana` recorta corretamente.
- Financeiro familiar resume aberto, vencido e próximo vencimento.
- Administrativo responde pendência concreta e próximo passo.
- Próximas avaliações dos dois filhos e follow-up individual passaram a funcionar de modo natural.

### 7. Restrito interno

Caso:

- `restricted_doc_positive`

Leitura:

- A resposta continua segura e grounded.
- Como o conteúdo interno específico não foi localizado, o sistema assume limitação concreta em vez de improvisar.
- Para um benchmark com apenas um caso restrito, o comportamento ficou correto; ainda assim, a cobertura restrita mais ampla segue melhor representada pela `50Q` histórica.

## Síntese interpretativa

A leitura humana desta rodada é que o sistema entrou em um estágio de maturidade diferente do observado nos ciclos anteriores:

- o problema já não é mais “respostas erradas e mecânicas”;
- o problema de misroute grosseiro praticamente desapareceu nesta bateria;
- os quatro caminhos convergiram qualitativamente porque a camada compartilhada de estado, repair, retrieval e grounded answer experience amadureceu.

Isso também muda a interpretação metodológica:

- a comparação deixa de ser sobre “qual stack responde certo ou errado”;
- e passa a ser sobre `latência`, `governança`, `estilo de orquestração` e `custo operacional`, já que a qualidade final convergiu.

## Veredito humano

Como leitura humana global, a `30Q v4` é consistente com um benchmark final pronto para sustentação acadêmica:

- respostas satisfatórias;
- boa adaptação à pergunta;
- grounding preservado;
- ausência de erros graves de domínio;
- follow-up protegido funcionando;
- noções explícitas de limite da base quando necessário.

Em termos práticos, esta bateria já pode ser usada como benchmark de referência no TCC.
