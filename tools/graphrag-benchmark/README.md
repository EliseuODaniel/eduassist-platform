# GraphRAG Benchmark

Ferramentas experimentais para medir `GraphRAG` de forma seletiva sobre o corpus institucional publico do projeto, sem trocar o runtime principal.

Objetivo:

- comparar o baseline atual `Qdrant + PostgreSQL FTS` com `GraphRAG`;
- medir ganho real antes de decidir qualquer integracao ao produto;
- manter uma trilha opt-in e separada do fluxo diario do sistema.

Workspace padrao:

- `artifacts/graphrag/eduassist-public-benchmark`

Comandos principais:

- `make graphrag-benchmark-bootstrap`
- `make graphrag-benchmark-index-dry-run`
- `make graphrag-benchmark-baseline`
- `make graphrag-benchmark-run`

Fluxo recomendado:

1. `make graphrag-benchmark-bootstrap`
2. editar `artifacts/graphrag/eduassist-public-benchmark/.env` com `GRAPHRAG_API_KEY`
3. `make graphrag-benchmark-index`
4. `make graphrag-benchmark-run`

Observacoes importantes:

- para corpus em portugues, o benchmark de qualidade deve priorizar `GRAPHRAG_INDEX_METHOD=standard`;
- o modo `fast` e mais barato para experimentar, mas a extracao `regex_english` padrao do `GraphRAG` tende a ser menos adequada para portugues;
- os resultados do benchmark sao salvos em `artifacts/graphrag/benchmark-runs`.
