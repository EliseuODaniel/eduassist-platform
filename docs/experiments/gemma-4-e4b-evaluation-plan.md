# Avaliação futura: Gemma 4 E4B

## Objetivo

Registrar o que seria necessário para testar o modelo [`google/gemma-4-E4B-it`](https://huggingface.co/google/gemma-4-E4B-it) no **EduAssist Platform atual**, sem alterar a arquitetura ativa antes de existir evidência clara de custo-benefício.

Este documento é um plano de experimento. Não é uma decisão de migração.

Revisão desta versão:

- validada contra o código atual do repositório em abril de 2026;
- revisada com base em documentação oficial e primária do Gemma 4 e de serving OpenAI-compatible.

## Pergunta principal

Vale a pena adicionar suporte ao `Gemma 4 E4B` como alternativa **local** aos modelos hospedados atuais, considerando:

- complexidade de implementação no código real do EduAssist;
- custo operacional na máquina local;
- impacto esperado na qualidade da resposta;
- adequação ao workload real do projeto;
- ROI comparado ao baseline atual.

## Estado atual do projeto

Hoje o EduAssist Platform opera com arquitetura `dedicated-first`, com:

- quatro runtimes dedicados: `langgraph`, `python_functions`, `llamaindex`, `specialist_supervisor`;
- `semantic ingress` compartilhado;
- `control plane` separado do serving principal;
- superfícies de avaliação por smoke, parity, multi-turn, long-memory, Telegram real e promotion gate.

O desenho funcional que precisa ser preservado é:

1. LLM de entrada: classificar;
2. stack: resolver;
3. LLM de saída: lapidar.

## O que o código atual já oferece

O repositório hoje já está **mais preparado** para um experimento de modelo local do que uma leitura superficial sugeriria.

### Configuração de provider/modelo já existente

O `ai-orchestrator` já expõe configuração central por ambiente em:

- [`apps/ai-orchestrator/src/ai_orchestrator/service_settings.py`](../../apps/ai-orchestrator/src/ai_orchestrator/service_settings.py)
- [`infra/compose/compose.yaml`](../../infra/compose/compose.yaml)
- [`.env.example`](../../.env.example)

Parâmetros já disponíveis:

- `LLM_PROVIDER`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `GOOGLE_API_BASE_URL`
- `GOOGLE_MODEL`

Estado observado hoje:

- baseline padrão no Compose: `LLM_PROVIDER=google`
- modelo padrão no Compose: `GOOGLE_MODEL=gemini-2.5-flash`
- caminho `openai` já aceita `OPENAI_BASE_URL`, o que abre espaço para um backend local compatível com a API da OpenAI

### Abstração de chamadas já implementada

Grande parte das chamadas já passa por uma camada compartilhada em:

- [`apps/ai-orchestrator/src/ai_orchestrator/llm_provider.py`](../../apps/ai-orchestrator/src/ai_orchestrator/llm_provider.py)

Esse módulo já suporta, no runtime principal:

- caminho `openai` via `AsyncOpenAI(..., base_url=settings.openai_base_url)`
- caminho `google/gemini`

Além disso, o código atual usa **OpenAI Responses API** em vários pontos críticos, por exemplo:

- classificação e composição de `semantic ingress`
- grounded composition
- `answer_experience`
- `context_repair`

### Evidência prática de provider local no próprio repo

O repositório já possui um trilho experimental para provider local em:

- [`tools/graphrag-benchmark/README.md`](../../tools/graphrag-benchmark/README.md)

Esse benchmark já documenta uso de:

- endpoint `OpenAI-compatible`
- chat local via `llama.cpp`
- embeddings locais via `Ollama`

Isso reduz o risco arquitetural do experimento: o workspace já convive com a ideia de backend local compatível com OpenAI.

## O que ainda falta no código

Apesar da boa base, o suporte a `Gemma 4 E4B` **ainda não está pronto** para o runtime principal.

Faltam principalmente:

1. um perfil operacional claro para `Gemma 4 E4B` local no serving principal;
2. validação de compatibilidade entre o backend local escolhido e o uso atual de `Responses API`;
3. benchmark comparativo do EduAssist com os quatro caminhos ativos;
4. observabilidade explícita do provider local na trilha principal, não só em benchmark lateral;
5. rollout experimental limitado por stack/superfície.

Conclusão importante:

- **a abstração de provider já existe em boa parte**
- o que falta não é “inventar uma arquitetura nova”
- o que falta é **fechar a compatibilidade operacional e medir**

## O que o Gemma 4 E4B oferece

Segundo a documentação oficial:

- os modelos pequenos da família Gemma 4 têm **128K** de contexto;
- E2B e E4B suportam texto, imagem e áudio;
- a família traz suporte a **system role**;
- a família traz suporte a **function calling**;
- a arquitetura foi desenhada para casos agentic e para ser eficiente em contexto longo e uso on-device.

Fontes:

- Google AI for Developers, Gemma 4 overview: <https://ai.google.dev/gemma/docs/core>
- Hugging Face blog, Gemma 4: <https://huggingface.co/blog/gemma4>
- Model card do `google/gemma-4-E4B-it`: <https://huggingface.co/google/gemma-4-E4B-it>

Pontos oficiais relevantes:

- a página oficial do Gemma 4 informa que os modelos pequenos têm janela de **128K**;
- a mesma página informa requisitos aproximados de memória de inferência para E4B:
  - `15 GB` em BF16
  - `7.5 GB` em SFP8
  - `5 GB` em `Q4_0`

Isso é especialmente importante para a máquina local alvo.

## O que o EduAssist realmente exige do modelo

O workload atual pede principalmente:

- roteamento correto entre intents públicas, protegidas e fora de escopo;
- aderência forte a instruções em PT-BR;
- estabilidade no uso de tools e respostas determinísticas onde o fluxo pede isso;
- robustez em mensagens curtas, ambíguas, multilíngues e de correção de contexto;
- pouca alucinação em perguntas fora de escopo;
- comportamento seguro quando a pergunta não pertence ao domínio escolar.

O projeto hoje **não** exige:

- contexto de `1M` tokens;
- RAG massivo com centenas de páginas por requisição;
- multimodalidade pesada em produção;
- memória de horizonte muito longo no estilo copiloto generalista.

Conclusão:

- `128K` já é suficiente para o workload atual;
- o gargalo principal não é contexto;
- o gargalo principal é consistência em routing, tool use, guardrails e resposta segura.

## Comparação prática com o baseline atual

### Baseline real do código hoje

O baseline atual do runtime principal é:

- provider padrão: `google`
- modelo padrão: `gemini-2.5-flash`

Isso está refletido em:

- [`infra/compose/compose.yaml`](../../infra/compose/compose.yaml)
- [`.env.example`](../../.env.example)
- [`service_settings.py`](../../apps/ai-orchestrator/src/ai_orchestrator/service_settings.py)

### Baseline hospedado atual

Pontos fortes para este projeto:

- integração já pronta;
- baixa complexidade operacional;
- boa disciplina de instrução;
- forte encaixe com flows que dependem de tool use, guardrails e resposta estável;
- nenhuma responsabilidade local de inferência.

Pontos fracos:

- dependência de provider hospedado;
- menor controle sobre a inferência;
- custo recorrente por uso, ainda que baixo.

### Gemma 4 E4B local

Pontos fortes:

- modelo open-weight;
- 128K de contexto, suficiente para o workload atual;
- capacidade agentic interessante para o tamanho;
- possibilidade real de execução local;
- bom encaixe com experimentação controlada e soberania futura do stack.

Pontos fracos:

- maior responsabilidade operacional;
- maior risco de latência e instabilidade local;
- menor margem de robustez do que o baseline hospedado em casos difíceis;
- necessidade de quantização para caber com folga no hardware local.

## Perda de qualidade esperada

A expectativa mais provável, antes de benchmark próprio, é:

- `semantic ingress`: perda pequena a moderada;
- FAQ pública: perda pequena a moderada;
- routing de intenção: perda moderada;
- flows protegidos com tools: perda moderada a relevante;
- `answer_experience` e `context_repair`: risco moderado de maior variabilidade.

O risco maior não é fluência de texto. É:

- classificar pior perguntas ambíguas;
- usar tools com menos consistência;
- errar mais em casos fora do padrão;
- piorar `fallback` seguro e negação de escopo.

## Complexidade de implementação no código atual

### Cenário A: experimento via servidor local OpenAI-compatible

Este é o caminho de **melhor ROI**.

Por que:

- o repo já tem `OPENAI_BASE_URL`;
- o runtime principal já usa `AsyncOpenAI(..., base_url=...)`;
- o vLLM expõe servidor OpenAI-compatible com suporte a `Responses API`;
- o próprio ecossistema Gemma 4 já aparece com caminhos locais e HTTP-compatible em tooling atual.

Fontes:

- vLLM OpenAI-Compatible Server: <https://docs.vllm.ai/en/latest/serving/openai_compatible_server/>
- Gemma 4 no Hugging Face: <https://huggingface.co/blog/gemma4>

Impacto estimado:

- **complexidade: média**, não alta

Porque ainda restam:

1. ajustar env/profile para provider local;
2. validar compatibilidade real com `Responses API`;
3. validar tool use e structured outputs nas superfícies críticas;
4. adicionar smoke/eval dedicados para o experimento.

Mas, ao contrário do que o documento sugeria antes, isso **não** exige começar do zero.

### Cenário B: integração nativa via `transformers` / backend bespoke

Este caminho tem ROI pior.

Impacto estimado:

- **complexidade: alta**

Porque exigiria:

1. criar runtime próprio de inferência;
2. manter transporte, autenticação e timeouts;
3. adaptar respostas estruturadas e tool calling;
4. assumir operação de GPU e observabilidade de um serviço novo.

Esse cenário só faz sentido se o objetivo for:

- reduzir ao máximo dependência de protocolo OpenAI-compatible;
- ou otimizar de forma mais profunda o serving local.

## Impacto na máquina alvo

Máquina informada:

- `RTX 4070` laptop
- `8 GB` de VRAM
- `32 GB` de RAM

Leitura prática com base na documentação oficial do Gemma 4:

- em BF16, o E4B **não** é uma boa aposta para essa VRAM;
- em SFP8, ele entra no limite;
- em `Q4_0`, ele fica viável no papel;
- ainda assim, o orçamento real precisa considerar:
  - KV cache;
  - contexto;
  - concorrência;
  - outros processos locais no WSL.

Conclusão prática:

- **viável para teste**
- **viável para uso local controlado**
- **apertado para virar backend principal do dia a dia sem disciplina operacional**

Isso combina com a evidência já registrada no próprio benchmark local de GraphRAG do projeto: com GPU local de `8 GiB`, o caminho mais realista tende a ser modelos menores e/ou quantizados.

## ROI atualizado

### ROI alto

Vale a pena se o objetivo for:

- testar uma rota open-weight;
- reduzir dependência futura de provider hospedado;
- aprender e comparar custo de inferência local vs API;
- criar um caminho experimental para `semantic ingress` e FAQs públicas;
- abrir espaço para execução local em modo laboratório.

### ROI médio

Vale a pena com cautela se o objetivo for:

- usar Gemma local apenas em superfícies públicas e de menor risco;
- comparar robustez semântica e latência contra o baseline hospedado;
- manter o baseline atual como fallback principal.

### ROI baixo ou incerto

Vale menos a pena se o objetivo for:

- trocar o sistema inteiro rapidamente;
- melhorar qualidade média de resposta sem benchmark próprio;
- substituir o baseline principal em flows protegidos;
- economizar custo sem assumir custo operacional local.

## Recomendação atual

Não migrar o sistema inteiro para `Gemma 4 E4B`.

O melhor caminho hoje é:

1. manter `gemini-2.5-flash` como baseline ativo;
2. testar `Gemma 4 E4B` primeiro via **servidor local OpenAI-compatible**;
3. aplicar o experimento primeiro em superfícies de menor risco;
4. só depois decidir se vale ampliar o escopo.

## Estratégia de implementação sugerida

### Fase 1: perfil experimental local

Criar um perfil de ambiente para `Gemma 4 E4B` local com:

- `LLM_PROVIDER=openai`
- `OPENAI_BASE_URL=<endpoint local>`
- `OPENAI_MODEL=google/gemma-4-E4B-it` ou identificador equivalente do runtime escolhido

Objetivo:

- reutilizar a infraestrutura já existente do caminho `openai`;
- evitar criação prematura de um provider bespoke.

### Fase 2: escopo inicial de baixo risco

Aplicar `Gemma 4 E4B` primeiro em:

- `semantic ingress`;
- atos públicos curtos;
- perguntas públicas documentais simples;
- eventualmente `answer_experience` público, se a latência permitir.

### Fase 3: benchmark formal do EduAssist

Rodar benchmark próprio com:

- qualidade por stack;
- latência;
- taxa de fallback indevido;
- comportamento em PT-BR;
- robustez em input curto, follow-up e negação segura;
- impacto operacional na máquina local.

### Fase 4: decisão de promoção

Só considerar expansão para flows protegidos se:

- o modelo mantiver routing forte;
- não piorar tool use;
- não aumentar fallback indevido;
- e não tornar o uso local operacionalmente frágil.

## Critérios de sucesso

O experimento com Gemma só deve avançar se mostrar:

- qualidade próxima do baseline atual nas superfícies públicas;
- robustez semântica em mensagens curtas e ambíguas;
- nenhuma regressão séria de segurança ou escopo;
- latência utilizável na máquina local;
- custo operacional justificável;
- compatibilidade suficiente com o caminho OpenAI-compatible já usado pelo projeto.

## Critérios de reprovação

Abortar a adoção se houver:

- degradação clara em routing ou guardrails;
- piora de fallback seguro;
- regressão forte em tool use;
- latência ruim para uso real;
- custo operacional local desproporcional ao ganho;
- necessidade de manutenção bespoke alta demais para o benefício observado.

## Veredito

O documento anterior estava **parcialmente desatualizado** para o código atual.

Atualização principal desta revisão:

- o repo **já tem abstração suficiente** para um experimento com provider local ser mais barato do que parecia;
- o melhor caminho não é criar um provider totalmente novo de primeira;
- o melhor ROI é **experimentar Gemma 4 E4B via endpoint local OpenAI-compatible**, com rollout restrito e benchmark próprio;
- ainda assim, para o estado atual do EduAssist, `Gemma 4 E4B` tem perfil melhor como **experimento controlado** do que como substituto imediato do baseline principal.
