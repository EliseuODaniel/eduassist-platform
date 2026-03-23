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
