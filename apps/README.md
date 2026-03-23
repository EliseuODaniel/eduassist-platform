# Apps

Diretório reservado para aplicações executáveis do projeto:

- `admin-web`
- `api-core`
- `telegram-gateway`
- `ai-orchestrator`
- `worker`

No bootstrap atual:

- os serviços Python usam `FastAPI` com `uv`;
- o painel usa `Next.js`;
- todos os apps já possuem `Dockerfile` e endpoints/comportamentos mínimos para validação da stack;
- o `api-core` já possui schema foundation, migracao Alembic e endpoint de resumo do banco;
- o `ai-orchestrator` já possui grafo LangGraph, preview de roteamento e catálogo inicial de tools.
