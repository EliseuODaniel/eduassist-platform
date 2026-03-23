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
  - webhook publico
  - consulta protegida
  - handoff humano
  - verificacao basica de `Tempo`, `Grafana`, `Loki` e `Prometheus`
  - validacao dos dashboards `EduAssist Tracing Overview` e `EduAssist Metrics Overview`
  - validacao das metricas OTEL de `policy`, `retrieval`, `handoff` e `orquestracao`
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
