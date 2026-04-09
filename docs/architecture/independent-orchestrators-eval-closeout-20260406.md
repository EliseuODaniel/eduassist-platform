# Fechamento da Rodada de Avaliacao da Branch de Orquestradores Independentes

Data: 2026-04-06

## O que foi implementado nesta rodada

1. `50Q` executada na branch independente.
2. Analise qualitativa dedicada da `50Q`.
3. Rubrica automatica fortalecida para perguntas compostas e respostas pouco
   acionaveis.
4. Nova bateria `multi-turn` criada e executada.
5. Refinos por stack em linha com a forca natural de cada caminho.
6. Retrieval reforcado com melhor cobertura por subtitulo e sinalizacao de
   `citation-first`.
7. Pacote cego de revisao humana gerado a partir da `50Q`.
8. Arquitetura independente documentada formalmente.

## Artefatos principais

### 50Q

- `docs/architecture/independent-orchestrators-50q-report-20260406-r1.md`
- `docs/architecture/independent-orchestrators-50q-report-20260406-r1.json`
- `docs/architecture/independent-orchestrators-50q-human-analysis-20260406-r1.md`

### Multi-turn

- `tests/evals/datasets/retrieval_multiturn_probe_threads.generated.20260406.json`
- `docs/architecture/independent-orchestrators-multiturn-report-20260406.md`
- `docs/architecture/independent-orchestrators-multiturn-report-20260406.json`
- `docs/architecture/independent-orchestrators-multiturn-human-analysis-20260406.md`

### Benchmark cego

- `docs/architecture/independent-orchestrators-50q-blind-review-20260406-r1.md`
- `docs/architecture/independent-orchestrators-50q-blind-review-key-20260406-r1.json`

### Arquitetura

- `docs/architecture/independent-orchestrators-architecture-20260406.md`

## Leitura consolidada

### Prompt isolado

A `50Q` mostrou que os quatro caminhos independentes estao estaveis e fortes em
prompt isolado. O backlog principal ficou em:

- completude de perguntas compostas;
- respostas pouco acionaveis;
- wording de `known unknowns`;
- alguns casos protegidos ambivalentes.

### Conversa continua

A bateria `multi-turn` foi bem mais dura e mostrou que o maior gap atual nao e
mais de retrieval bruto, e sim de continuidade conversacional:

- follow-up curto;
- troca de foco;
- reparo de contexto;
- reorientacao depois de negacao;
- perguntas meta.

## Implicacao tecnica

Depois desta rodada, a branch ja separa bem dois tipos de qualidade:

1. qualidade de resposta isolada;
2. qualidade de orquestracao conversacional.

Isso e importante porque evita misturar problemas diferentes sob o mesmo score.

## Proximo ciclo recomendado

1. fortalecer memoria curta por thread;
2. melhorar politicas locais de follow-up e resposta meta;
3. rerrodar `multi-turn`;
4. somente depois decidir se vale uma `50Q r2` ou se o foco deve migrar para
   uso real via Telegram.
