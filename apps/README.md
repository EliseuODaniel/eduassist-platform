# Apps

Diretório reservado para aplicações executáveis do projeto:

- `admin-web`
- `api-core`
- `telegram-gateway`
- `ai-orchestrator`
- `ai-orchestrator-langgraph`
- `ai-orchestrator-python-functions`
- `ai-orchestrator-llamaindex`
- `ai-orchestrator-specialist`
- `worker`

No bootstrap atual:

- os serviços Python usam `FastAPI` com `uv`;
- o painel usa `Next.js`;
- todos os apps já possuem `Dockerfile` e endpoints/comportamentos mínimos para validação da stack;
- o `api-core` já possui schema foundation, migracao Alembic e endpoint de resumo do banco;
- o `ai-orchestrator` central opera como `control plane/router`;
- os runtimes dedicados executam o serving principal por stack;
- o `telegram-gateway` deve apontar para um runtime dedicado;
- os quatro caminhos compartilham guardrails, observabilidade, retrieval e `semantic ingress`, mas preservam suas diferenças de resolução e polish.
