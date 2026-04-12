# Documentação

Este diretório concentra a documentação formal do projeto.

## Índice

- [ADR 0001 - Rebuild do zero](adr/0001-greenfield-rebuild.md)
- [ADR 0002 - Retrieval e runtime agêntico](adr/0002-retrieval-and-agent-runtime.md)
- [PRD](prd/product-requirements.md)
- [Arquitetura do sistema](architecture/system-architecture.md)
- [Guia visual macro do runtime dual stack](architecture/dual-stack-runtime-visual-guide.md)
- [Guia visual do LangGraph](architecture/langgraph-runtime-visual-guide.md)
- [Strict benchmark mode e advanced retrieval](architecture/strict-benchmark-and-advanced-retrieval.md)
- [Plano next-gen de comparação entre stacks](architecture/next-gen-chatbot-comparison-plan.md)
- [Simplificação do runtime e guardrails de qualidade](architecture/runtime-simplification-and-quality-guardrails-20260402.md)
- [Estado de referência dedicated-first](architecture/dedicated-first-reference-state.md)
- [Arquitetura dos orquestradores independentes](architecture/independent-orchestrators-architecture-20260406.md)
- [Fechamento da rodada dedicada-first](architecture/independent-orchestrators-eval-closeout-20260406.md)
- [Catálogo de serviços](architecture/service-catalog.md)
- [Segurança da informação](security/security-architecture.md)
- [Matriz de controle de acesso](security/access-control-matrix.md)
- [Modelo de dados](data/data-model.md)
- [Operação local](operations/local-development.md)
- [Workflow de Codex, MCP, Skills e AGENTS.md](operations/codex-workflow.md)
- [Pesquisa de tecnologias de IA](research/ai-technology-review.md)
- [Roadmap de implementação](roadmap/implementation-roadmap.md)

## Observação

Materiais acadêmicos de TCC, textos de banca e anotações relacionadas são mantidos apenas no ambiente local de desenvolvimento e não fazem parte da documentação pública publicada neste repositório.

## Leitura recomendada hoje

Se você estiver chegando agora ao projeto, a ordem mais útil é:

1. [Arquitetura do sistema](architecture/system-architecture.md)
2. [Estado de referência dedicated-first](architecture/dedicated-first-reference-state.md)
3. [Operação local](operations/local-development.md)
4. [Segurança da informação](security/security-architecture.md)

Essa sequência já reflete a arquitetura atual com:

- `control plane` central;
- runtimes dedicados como caminho principal de serving;
- `semantic ingress` compartilhado para atos de entrada críticos;
- e a superfície de aceite baseada em smoke, memória longa, Telegram real, parity e promotion gate.
