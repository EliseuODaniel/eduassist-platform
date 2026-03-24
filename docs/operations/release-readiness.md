# Release Readiness

Este documento registra os gates minimos para considerar o projeto pronto para demo local, handoff tecnico ou fechamento de etapa.

## Gate principal

Use:

- `make release-readiness`

Esse comando consolida:

- `make db-check-runtime-role`
- `make db-check-rls`
- `make eval-orchestrator`
- `make smoke-all`
- `make graphrag-benchmark-baseline`

Artefatos:

- `artifacts/readiness/release-readiness-<timestamp>.json`
- `artifacts/readiness/release-readiness-<timestamp>.md`

## Modo estrito

Use:

- `make release-readiness-strict`

Esse modo exige, alem dos gates obrigatorios, um benchmark completo de `GraphRAG` concluido com sucesso.

Para esse criterio, o gate considera o benchmark mais recente com execucao real de `GraphRAG`, sem confundir o baseline comparativo que roda com `skip-graphrag`.

Na pratica, ele depende de:

1. `make graphrag-benchmark-bootstrap` ou `make graphrag-benchmark-bootstrap-local`
2. preencher `artifacts/graphrag/eduassist-public-benchmark/.env` com provider remoto ou local compativel
3. se for fluxo local com GPU, subir `make graphrag-local-runtime-up`
4. `make graphrag-benchmark-index`
5. `make graphrag-benchmark-run` ou `make graphrag-benchmark-run-smoke`

## Interpretacao

### Pronto para demo local

Quando `make release-readiness` retorna `ok: true`.

Significa que:

- o runtime do banco nao esta em papel superuser;
- as politicas de `RLS` estao funcionando;
- o `ai-orchestrator` passou na suite formal de evals;
- os fluxos principais, autorizacao e cenarios adversariais passaram;
- existe baseline comparativo do benchmark de `GraphRAG`;
- o runtime principal com provider externo e o caminho `GraphRAG` local podem ser exercitados sem ajuste manual de codigo.

### Pronto para comparacao completa de retrieval avancado

Quando `make release-readiness-strict` retorna `ok: true`.

Significa, alem do baseline local:

- o benchmark completo de `GraphRAG` foi executado;
- existe material concreto para decidir se `GraphRAG` entra em algum fluxo real.

## Estado esperado atual

Sem provider `GraphRAG` configurado e acessivel, o gate padrao deve passar e o gate estrito deve falhar.

Com provider local ou remoto configurado corretamente, o gate estrito deve passar.

Esse comportamento e intencional:

- o produto principal nao depende de `GraphRAG` para funcionar;
- `GraphRAG` continua sendo uma trilha avancada, medida e seletiva, ainda que o runtime principal ja consiga executa-la quando habilitada.
