# Auditoria do Walkthrough Versus Codigo Real

## Escopo

Este documento compara `tmp/walkthrough.md` com o estado real do codigo em `main` no repositorio canônico `eduassist-platform`, usando como referencia adicional a documentacao oficial de OpenTelemetry, LangGraph, LlamaIndex e Qdrant.

## O que o walkthrough acerta

- a arquitetura deixou de ser centrada num unico entrypoint de serving e passou a ser `dedicated-first`;
- `ai-orchestrator` hoje atua como `control plane/router`, nao como caminho principal de serving;
- existem quatro superfícies de execução relevantes:
  - `langgraph`
  - `python_functions`
  - `llamaindex`
  - `specialist_supervisor`
- o contrato compartilhado de `semantic ingress` existe de fato e hoje cobre atos de alta precedencia como `greeting`, `input_clarification`, `language_preference` e `scope_boundary`;
- a superfície de seguranca continua forte, com `OPA`, `RLS`, tokens internos e testes regressivos de autorizacao;
- a validacao do sistema nao depende mais de um benchmark unico: smoke dedicado, multi-turn, memoria longa, semantic ingress, Telegram real e parity operacional ja fazem parte do estado de referencia.

## O que o walkthrough já estava desatualizado

### Retrieval

O walkthrough ainda descrevia a ausência de um reranker explicito como gap principal de retrieval. Isso nao e mais verdade no codigo atual.

Hoje o repo ja possui suporte configuravel a `late interaction rerank`, incluindo:

- `retrieval_enable_late_interaction_rerank = true`
- `retrieval_late_interaction_model = answerdotai/answerai-colbert-small-v1`

Esse suporte aparece no orquestrador principal e no `specialist`, o que torna o comentario de “sem cross-encoder explicito” desatualizado como diagnostico principal.

### Documentacao arquitetural oficial

O walkthrough estava mais atualizado do que a propria documentacao canônica do repo em dois pontos:

- `docs/architecture/system-architecture.md` ainda descrevia um desenho quase monolitico;
- `docs/architecture/service-catalog.md` ainda tratava `ai-orchestrator` como servico central demais.

### Benchmarks e links locais

O walkthrough também carregava:

- números antigos de benchmark;
- referencias locais `file:///...` que nao devem ser tratadas como caminho canônico de documentacao do projeto.

## Gaps reais restantes antes desta rodada

Antes desta implementação, os gaps com melhor ROI eram estes:

1. observabilidade GenAI ainda sem convencoes padrão OpenTelemetry;
2. ausência de métricas de uso de tokens e custo estimado por provider/modelo;
3. `otel-collector` sem `tail sampling` para privilegiar traces caros, lentos ou com erro;
4. drift entre codigo e docs arquiteturais principais;
5. `runtime.py` ainda excessivamente grande, com contratos auxiliares definidos dentro do arquivo.

## O que não foi tratado nesta rodada por decisao explícita

- substituição de `TryCloudflare` por borda pública estável;
- redução de latencia do `specialist_supervisor`.

Esses dois itens seguem relevantes, mas foram explicitamente excluídos desta etapa.

## Referencias externas usadas

- OpenTelemetry GenAI semantic conventions
- OpenTelemetry Collector tail sampling
- LangGraph workflows and graph routing
- LlamaIndex workflows/router patterns
- Qdrant late interaction reranking
