# Tests

Diretório reservado para:

- testes de integração
- testes end-to-end
- testes de segurança
- datasets de avaliação
- cenários adversariais

Estado atual:

- `tests/e2e/local_smoke.py` cobre o caminho principal local:
  - healthchecks
  - token do `Keycloak`
  - overview global autenticado de handoff
  - webhook publico
  - consulta protegida
  - handoff humano
  - verificacao basica de `Tempo`, `Grafana`, `Loki` e `Prometheus`
  - validacao dos dashboards `EduAssist Tracing Overview`, `EduAssist Metrics Overview` e `EduAssist Ops Control Tower`
  - validacao das metricas OTEL de `policy`, `retrieval`, `handoff` e `orquestracao`
  - validacao dos gauges vivos de backlog, idade do backlog, prioridade e handoffs sem responsavel
  - validacao da paginacao da fila humana em `GET /v1/support/handoffs`
- `tests/e2e/authz_regression.py` cobre regressao de seguranca funcional:
  - negacao para usuario anonimo em fluxo protegido
  - clarificacao de responsavel com mais de um aluno
  - `403` de policy no `api-core`
  - `401` por secret invalido no webhook
  - `401` para rota web protegida sem bearer
- `tests/e2e/adversarial_regression.py` cobre ataques e exfiltracao:
  - tentativa anonima de extrair financeiro de todos os alunos
  - tentativa de responsavel consultar aluno nao vinculado
  - tentativa de professor contornar policy para fluxo financeiro
  - tentativa de revelar prompts/instrucoes internas
  - tentativa de aluno consultar dados academicos de outro aluno
  - verificacao de que o prompt malicioso nao aparece em texto puro no `Loki`
- `tests/evals/orchestrator_quality.py` cobre evals formais do `ai-orchestrator` com dataset versionado em `tests/evals/datasets/orchestrator_cases.json`:
  - grounding publico com citações
  - calendario publico com resposta composta e eventos estruturados
  - negacao segura para fluxo protegido sem vinculo
  - ambiguidade controlada para responsavel com mais de um aluno
  - consultas protegidas academicas e financeiras bem roteadas
  - handoff humano
  - resistencia basica a prompt disclosure
  - retrieval search com verificação de hits documentais
- `tests/evals/datasets/system_question_bank.md` consolida um banco mestre de perguntas para estressar:
  - fatos canonicos estruturados
  - retrieval hibrido
  - `GraphRAG`
  - autenticacao, policy e escopo
  - dados protegidos academicos, financeiros e administrativos
  - fluxo docente
  - workflows, handoff, casos adversariais e perguntas externas com fallback seguro

Comandos uteis:

- `make smoke-local`
- `make smoke-authz`
- `make smoke-adversarial`
- `make smoke-all`
- `make eval-orchestrator`
- `make eval-all`
