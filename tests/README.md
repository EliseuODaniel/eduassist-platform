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
  - verificacao basica de `Tempo`, `Grafana` e `Loki`
- `tests/e2e/authz_regression.py` cobre regressao de seguranca funcional:
  - negacao para usuario anonimo em fluxo protegido
  - clarificacao de responsavel com mais de um aluno
  - `403` de policy no `api-core`
  - `401` por secret invalido no webhook
  - `401` para rota web protegida sem bearer
