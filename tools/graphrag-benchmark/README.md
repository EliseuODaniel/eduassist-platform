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
- `make graphrag-benchmark-bootstrap-local`
- `make graphrag-benchmark-local-check`
- `make graphrag-benchmark-index-dry-run`
- `make graphrag-benchmark-baseline`
- `make graphrag-benchmark-run`

Fluxo recomendado com provider remoto:

1. `make graphrag-benchmark-bootstrap`
2. editar `artifacts/graphrag/eduassist-public-benchmark/.env` com `GRAPHRAG_API_KEY`
3. `make graphrag-benchmark-index`
4. `make graphrag-benchmark-run`

Fluxo recomendado com GPU local:

1. subir um endpoint compativel com OpenAI, como `Ollama`, no host local;
2. garantir que o endpoint responda em `http://127.0.0.1:11434/v1` ou ajustar `GRAPHRAG_LOCAL_API_BASE`;
3. `make graphrag-benchmark-bootstrap-local`
4. revisar `artifacts/graphrag/eduassist-public-benchmark/.env`
5. `make graphrag-benchmark-local-check`
6. `make graphrag-benchmark-index`
7. `make graphrag-benchmark-run`

Observacoes importantes:

- para corpus em portugues, o benchmark de qualidade deve priorizar `GRAPHRAG_INDEX_METHOD=standard`;
- o modo `fast` e mais barato para experimentar, mas a extracao `regex_english` padrao do `GraphRAG` tende a ser menos adequada para portugues;
- o template local nasce com `qwen2.5:7b` para chat e `nomic-embed-text` para embeddings, mas voce pode trocar ambos no `.env`;
- para GPU local com `8 GiB`, o caminho mais realista e usar modelos menores/quantizados no provider local e tratar `GraphRAG` como benchmark experimental, nao como baseline operacional;
- os resultados do benchmark sao salvos em `artifacts/graphrag/benchmark-runs`.
