# Avaliação futura: Gemma 4 E4B

## Objetivo

Registrar o que seria necessário para testar o modelo [`google/gemma-4-E4B-it`](https://huggingface.co/google/gemma-4-E4B-it) neste projeto no futuro, sem alterar a arquitetura ativa antes de existir evidência de custo-benefício.

Este documento é um plano de experimento, não uma decisão de migração.

## Pergunta principal

Vale a pena adicionar suporte ao `Gemma 4 E4B` como alternativa aos modelos hospedados hoje, considerando:

- complexidade de implementação
- custo operacional
- qualidade da resposta
- adequação ao workload real do projeto
- capacidade da máquina alvo

## Estado atual do projeto

Hoje o EduAssist Platform opera com uma arquitetura `dedicated-first`, com:

- quatro runtimes dedicados (`langgraph`, `python_functions`, `llamaindex`, `specialist_supervisor`);
- `semantic ingress` compartilhado;
- `control plane` separado do serving principal;
- superfícies de avaliação por smoke, parity, multi-turn, long-memory, Telegram real e promotion gate.

O uso de LLM está espalhado principalmente pelos runtimes dedicados e pelos pacotes compartilhados em:

- [`apps/ai-orchestrator/`](../../apps/ai-orchestrator/)
- [`apps/ai-orchestrator-specialist/`](../../apps/ai-orchestrator-specialist/)
- [`packages/semantic-ingress/`](../../packages/semantic-ingress/)

A eventual adoção de `Gemma 4 E4B` exigiria preservar esse desenho:

1. LLM de entrada: classificar;
2. stack: resolver;
3. LLM de saída: lapidar.

## O que o Gemma 4 E4B oferece

Segundo a model card do Hugging Face:

- `128K` de contexto
- suporte a `text`, `image` e `audio`
- `system role` nativo
- `function calling` nativo
- modo de `thinking`
- foco em execução local e on-device
- `4.5B effective params` e `8B total params with embeddings`

Referência:

- https://huggingface.co/google/gemma-4-E4B-it

## O que o projeto realmente exige do modelo

O workload atual pede principalmente:

- roteamento correto entre intents públicas, protegidas e fora de escopo;
- aderência a instruções em PT-BR;
- estabilidade no uso de tools e respostas determinísticas onde o fluxo pede isso;
- resposta curta, consistente e segura;
- pouca alucinação em perguntas fora de escopo;
- robustez em classificações de entrada, follow-ups e correções de contexto.

O projeto hoje **não** exige:

- contexto de `1M` tokens;
- RAG massivo de documentos muito longos;
- multimodalidade pesada em produção;
- memória de horizonte muito longo no estilo copiloto generalista.

Conclusão:

- `128K` de contexto já é suficiente para o workload atual;
- o gargalo principal não é contexto;
- o gargalo principal é consistência em routing, tool use, guardrails e resposta segura.

## Comparação prática

### Baseline hospedado atual

Pontos fortes para este projeto:

- integração hospedada e simples
- custo muito baixo
- baixa complexidade operacional
- forte disciplina de instrução
- melhor caminho natural para apps com tools, guardrails e respostas estáveis

Pontos fracos:

- dependência de provider hospedado
- menor controle sobre a inferência

### Gemma 4 E4B

Pontos fortes:

- open-weight
- 128K de contexto
- suporte a system role e function calling
- bom equilíbrio entre tamanho e capacidade
- possibilidade de rodar localmente

Pontos fracos:

- maior complexidade para integrar nesta arquitetura
- maior responsabilidade operacional
- risco maior de latência e instabilidade local
- provável perda de qualidade média em routing e flows tool-heavy quando comparado ao baseline hospedado

## Perda de qualidade esperada

A expectativa mais provável é:

- `FAQ`: perda pequena a moderada
- `intent routing`: perda moderada
- `financial` e `academic`: perda moderada a relevante

O risco maior não é fluência do texto. É:

- classificar pior perguntas ambíguas
- usar tools com menos consistência
- errar mais em casos fora do padrão

## Impacto de engenharia

### Se a mudança for só uma feature flag

Baixa complexidade.

Seria necessário:

- centralizar seleção de provider e modelo
- remover hardcodes locais onde ainda existirem
- introduzir variáveis de ambiente como:
  - `MODEL_PROVIDER`
  - `MODEL_NAME`
  - `MODEL_PROFILE`

### Se a mudança incluir suporte real a `Gemma 4 E4B`

Complexidade média a alta.

Além da feature flag, seria necessário:

1. escolher um runtime de inferência:
   - `Transformers`
   - `vLLM`
   - `TGI`
   - ou outro servidor compatível com a integração adotada
2. criar uma integração nova para o projeto usar esse runtime
3. adaptar a escolha de provider por ambiente sem quebrar os quatro caminhos
4. medir impacto em latência e memória
5. validar function calling, structured outputs e comportamento com tools

## Impacto na máquina alvo

Máquina informada:

- `RTX 4070` laptop
- `8GB` de VRAM
- `32GB` de RAM

Leitura prática:

- **viável para teste**, com quantização e contexto controlado
- **apertado** para uso confortável como backend principal
- **mais arriscado** se o notebook estiver rodando também navegador, Next.js, Genkit, Telegram e outras ferramentas ao mesmo tempo

O principal cuidado aqui é:

- VRAM
- KV cache
- contexto longo
- latência quando houver tool-heavy prompts

Conclusão prática:

- serve para experimento local
- não é a aposta mais confortável para virar backend principal do sistema

## ROI

### ROI alto

Vale a pena se o objetivo for:

- testar uma rota open-weight
- reduzir dependência futura de provider hospedado
- aprender e comparar custo de inferência local vs API
- ter um caminho experimental para FAQ e roteamento

### ROI baixo ou incerto

Vale menos a pena se o objetivo for:

- trocar tudo rapidamente
- melhorar qualidade de resposta
- reduzir custo sem assumir operação nova

## Recomendação

Não migrar o sistema inteiro para `Gemma 4 E4B` sem benchmark próprio do EduAssist.

A melhor ordem de execução futura é:

1. implementar feature flag de provider/model
2. manter o caminho atual Google como baseline
3. adicionar Gemma como backend experimental
4. testar primeiro atos de entrada e fluxos públicos de menor risco
5. deixar flows protegidos, long-memory e recortes com tools para a segunda fase
6. só comparar qualidade depois de garantir paridade mínima de tracing e observabilidade

## Estratégia de implementação sugerida

### Fase 1: abstração de provider/modelo

Criar uma camada central de resolução de provider/modelo.

Responsabilidade:

- ler `MODEL_PROVIDER`;
- ler `MODEL_NAME`;
- ler `MODEL_PROFILE`;
- selecionar provider e modelo sem acoplamento aos quatro caminhos.

### Fase 2: experimento restrito

Aplicar `Gemma 4 E4B` primeiro em superfícies de menor risco:

- `semantic ingress`;
- atos públicos curtos;
- perguntas públicas documentais simples.

### Fase 3: comparação formal

Rodar benchmark próprio com:

- qualidade por stack;
- latência;
- taxa de fallback indevido;
- comportamento em PT-BR;
- robustez em input curto, follow-up e negação segura.

## Critérios de sucesso

O experimento com Gemma só deve avançar se mostrar:

- qualidade próxima do baseline atual nas superfícies públicas;
- robustez semântica em mensagens curtas e ambíguas;
- nenhuma regressão séria de segurança ou escopo;
- latência utilizável na máquina local;
- custo operacional justificável.

## Critérios de reprovação

Abortar a adoção se houver:

- degradação clara em flows protegidos;
- aumento forte de complexidade sem ganho visível;
- latência ruim para uso real;
- piora de fallback, routing ou guardrails em comparação com o baseline.
- uso de memória que torne o ambiente local instável

## Resposta objetiva para o futuro

Se a intenção for testar:

- **sim, faz sentido documentar e experimentar**

Se a intenção for substituir o stack atual:

- **não sem benchmark A/B no próprio app**

## Fontes

- Hugging Face model card: https://huggingface.co/google/gemma-4-E4B-it
- Gemini models overview: https://ai.google.dev/gemini-api/docs/models
- Gemini 2.5 Flash family: https://ai.google.dev/gemini-api/docs/models/gemini-v2
- Gemini pricing: https://ai.google.dev/pricing
- Gemini quotas and rate limits: https://ai.google.dev/gemini-api/docs/quota
