# Avaliação prática: Gemma 4 E4B local no EduAssist

## Status

Este experimento foi **implementado e validado** no `eduassist-platform` em 12 de abril de 2026.

O objetivo foi responder a uma pergunta prática:

- vale a pena, em termos de ROI, adicionar um backend **local** para alternar entre:
  - `gemini-2.5-flash-lite`
  - `Gemma 4 E4B`

A conclusão curta é:

- **sim**, vale a pena ter esse caminho por feature flag;
- **não**, ainda não vale trocar o baseline inteiro para Gemma local;
- o melhor uso hoje é como **modo experimental controlado**, não como default do sistema.

## Resumo executivo

O experimento deu certo em quatro frentes:

1. a alternância por feature flag foi implementada sem bifurcar a arquitetura;
2. o `Gemma 4 E4B` rodou localmente na máquina alvo;
3. os quatro runtimes dedicados responderam corretamente sob o perfil local;
4. a stack voltou para `gemini_flash_lite` usando só configuração, sem novos patches.

O ROI final ficou assim:

- **alto** para laboratório, benchmarking, soberania tecnológica e comparação de qualidade;
- **médio** para uso diário local individual;
- **baixo** para substituir imediatamente o baseline hospedado em toda a plataforma.

## Pergunta de negócio

O EduAssist hoje precisa de um modelo que seja bom em:

- classificação semântica de entrada;
- roteamento de intenção;
- robustez em PT-BR;
- uso consistente de tools;
- respostas seguras quando não sabe;
- baixa taxa de fallback indevido.

O sistema **não** precisa hoje de:

- janela de 1 milhão de tokens;
- multimodalidade pesada em produção;
- throughput alto em múltiplos usuários simultâneos na máquina local.

Portanto, a pergunta não era “o Gemma cabe no contexto?”.

A pergunta real era:

- ele cabe **operacionalmente** na máquina?
- e entrega qualidade suficiente para o tipo de inferência que o EduAssist pede?

## Linha de base comparada

### Override hospedado

O override hospedado para comparação e fallback fica em:

- `LLM_MODEL_PROFILE=gemini_flash_lite`
- provider efetivo: `google`
- modelo efetivo: `gemini-2.5-flash-lite`

### Backend local experimental

O backend local implementado foi:

- `LLM_MODEL_PROFILE=gemma4e4b_local`
- provider efetivo: `openai`
- modo OpenAI: `chat_completions`
- servidor local OpenAI-compatible
- runtime de inferência: `llama.cpp`
- modelo: `google/gemma-4-E4B-it`
- quantização usada: `Q4_K_M` em GGUF

No estado atual do repositório, `gemma4e4b_local` passou a ser o default operacional local; `gemini_flash_lite` permanece como feature flag explícita para comparação.

## Por que o caminho escolhido foi este

Antes da implementação, a melhor hipótese de ROI era:

- reutilizar a trilha `openai` já existente no código;
- apontá-la para um endpoint local OpenAI-compatible;
- evitar criar um provider bespoke novo.

Depois da validação prática, essa hipótese se confirmou.

O melhor caminho **não** foi:

- `transformers` bespoke no app;
- provider separado por código customizado;
- refactor grande no runtime principal.

O melhor caminho foi:

- **feature flag + servidor OpenAI-compatible local**.

## Pesquisa resumida e decisão de modelo

Modelos menores poderiam ter ROI operacional ainda melhor em uma RTX 4070 Laptop com 8 GB de VRAM, especialmente para pura classificação ou FAQ curta.

Mesmo assim, o `Gemma 4 E4B` continuou sendo a melhor escolha para este experimento porque:

- era o alvo explícito do estudo;
- tem suporte oficial a `system role` e `function calling`;
- oferece `128K` de contexto, mais do que suficiente para o workload atual;
- fica numa faixa de qualidade mais compatível com o tipo de pipeline agentic do EduAssist do que modelos locais muito menores;
- possui disponibilidade em GGUF quantizado adequada para a máquina.

Então a decisão final foi:

- **não trocar de modelo-alvo neste experimento**;
- **implementar Gemma 4 E4B local de forma reversível**.

## O que foi implementado

### 1. Feature flag de perfil de modelo

Foi criado suporte explícito a perfis de modelo em:

- [`apps/ai-orchestrator/src/ai_orchestrator/service_settings.py`](../../apps/ai-orchestrator/src/ai_orchestrator/service_settings.py)
- [`apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/main.py`](../../apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/main.py)

Perfis suportados:

- `gemini_flash_lite`
- `gemma4e4b_local`

### 2. Compatibilidade OpenAI-compatible local

Foi endurecido o provider OpenAI compartilhado em:

- [`apps/ai-orchestrator/src/ai_orchestrator/llm_provider.py`](../../apps/ai-orchestrator/src/ai_orchestrator/llm_provider.py)

Isso permitiu:

- manter `Responses API` para OpenAI hospedado quando fizer sentido;
- usar `chat_completions` automaticamente para o backend local compatível;
- reaproveitar a arquitetura existente sem duplicar providers.

### 3. Backend local reproduzível versionado no repo

Foi adicionado um backend local reproduzível em:

- [`infra/compose/local-llm/llama-cpp/Dockerfile`](../../infra/compose/local-llm/llama-cpp/Dockerfile)
- [`infra/compose/local-llm/llama-cpp/run-llama-server.sh`](../../infra/compose/local-llm/llama-cpp/run-llama-server.sh)

Esse backend:

- compila `llama.cpp` atual com CUDA;
- usa arquitetura CUDA otimizada para a GPU alvo (`sm_89`);
- sobe um servidor OpenAI-compatible em container;
- usa GGUF em cache local quando disponível;
- evita rebuild manual fora do repositório.

### 4. Compose e Makefile

Foram adicionados:

- serviço `local-llm-gemma4e4b` no Compose;
- targets:
  - `make compose-up-dedicated-core-gemma4e4b-local`
  - `make compose-up-dedicated-core-gemini-flash-lite`
  - `make local-llm-gemma4e4b-down`
  - `make local-llm-gemma4e4b-logs`

### 5. Cobertura automatizada

Foram adicionados e/ou atualizados testes unitários para:

- seleção de perfil;
- propagação de configuração;
- compatibilidade OpenAI-compatible local.

Arquivos principais:

- [`tests/unit/test_source_mode_settings.py`](../../tests/unit/test_source_mode_settings.py)
- [`tests/unit/test_llm_provider_openai_compat.py`](../../tests/unit/test_llm_provider_openai_compat.py)
- [`tests/unit/test_grounded_answer_experience.py`](../../tests/unit/test_grounded_answer_experience.py)

## Máquina alvo e viabilidade real

Máquina usada:

- `NVIDIA GeForce RTX 4070 Laptop GPU`
- `8 GB` de VRAM
- `32 GB` de RAM

Resultado prático:

- o `Gemma 4 E4B` **rodou localmente com sucesso**;
- a quantização usada coube com folga suficiente para experimento real;
- não houve OOM durante a bateria executada.

## Carga observada na máquina

### Idle com o backend Gemma carregado

Depois do modelo carregado e pronto:

- uso de VRAM observado: aproximadamente `4.4 GB`

Isso significa:

- a GPU fica ocupada de forma relevante mesmo em idle;
- ainda sobra margem razoável dentro dos `8 GB`;
- a máquina continua utilizável, mas com menos folga para outras cargas pesadas simultâneas.

### Sob inferência real do EduAssist

Durante smoke funcional e bateria semântica:

- pico de VRAM observado: `4383 MiB`
- pico de uso de GPU observado: `91%`
- pico de uso de memória da GPU observado: `76%`
- pico de potência observado: `77.99 W`

Leitura operacional:

- a carga foi **alta, mas saudável**;
- não houve sinal de saturação de VRAM;
- a GPU entrou em trabalho real e voltou a idle entre requisições;
- para **baixa concorrência**, a máquina segura bem;
- para uso multitarefa pesado ao mesmo tempo, o modo local pode incomodar.

## Resultados dos testes

### Testes unitários

Rodada focal executada:

- `tests/unit/test_source_mode_settings.py`
- `tests/unit/test_llm_provider_openai_compat.py`
- `tests/unit/test_dedicated_stack_status.py`

Resultado:

- `15 passed`

Observação:

- houve uma falha pré-existente e não relacionada em `test_grounded_answer_experience.py` fora do escopo do experimento, já conhecida no repositório.

### Sanidade do backend local

Validações diretas concluídas:

- `/v1/models` saudável no endpoint local;
- `chat/completions` saudável no endpoint local;
- modelo carregado corretamente como `gemma4`;
- todas as camadas offloaded para GPU na configuração usada.

### Bateria semântica cross-stack

Execução validada por stack:

- `langgraph`
- `python_functions`
- `llamaindex`
- `specialist_supervisor`

Resultado:

- verde nos quatro caminhos

Arquivo de saída:

- [`artifacts/dedicated-stack-semantic-ingress-report.json`](../../artifacts/dedicated-stack-semantic-ingress-report.json)

Observação honesta:

- houve um falso negativo transitório em uma rodada agregada longa do `specialist_supervisor`;
- o replay isolado do mesmo stack passou completamente;
- o comportamento final ficou consistente, então isso foi tratado como instabilidade transitória de execução, não como regressão funcional persistente.

### Smoke funcional por produto

Execução validada:

- `python_functions`
- `specialist_supervisor`
- rodada completa `all`

Arquivo e script:

- [`tests/e2e/dedicated_stack_smoke.py`](../../tests/e2e/dedicated_stack_smoke.py)

Resultado:

- verde nos quatro runtimes dedicados

Isso é importante porque mostra que o Gemma não ficou bom apenas em:

- classificação semântica;

mas também segurou:

- admissions públicas;
- boundary de professor;
- ambiguidade de múltiplos alunos;
- consulta nominal de notas.

## Alternância por feature flag

A alternância entre os dois modos foi validada na prática.

### Perfil Gemma local

Com:

- `make compose-up-dedicated-core-gemma4e4b-local`

os serviços passaram a expor:

- `llmModelProfile = gemma4e4b_local`
- `openaiApiMode = chat_completions`
- `llmProvider = openai`

### Perfil Gemini Flash-Lite

Com:

- `make compose-up-dedicated-core-gemini-flash-lite`

os serviços voltaram a expor:

- `llmModelProfile = gemini_flash_lite`
- `openaiApiMode = responses`
- `llmProvider = google`
- `googleModel = gemini-2.5-flash-lite`

Também foi feito um sanity check real de resposta após o flip para Gemini:

- `python_functions`
- pergunta pública de matrícula
- resposta correta
- latência observada: cerca de `0.314 s`

Isso prova que a feature flag ficou:

- reversível;
- operacional;
- sem dependência de patch adicional.

## O que funcionou bem

1. **A integração exigiu menos refactor do que parecia.**
   - O repo já estava mais preparado do que a leitura inicial sugeria.

2. **A sua máquina aguenta o Gemma 4 E4B nesse formato.**
   - Não é “sobrando”, mas é viável.

3. **O backend local não comprometeu os quatro caminhos dedicados nos testes executados.**

4. **A reversibilidade ficou boa.**
   - Voltar para `gemini_flash_lite` foi simples e limpo.

## Limitações e tradeoffs

1. **O backend local ocupa VRAM mesmo em idle.**
   - Isso pesa no dia a dia.

2. **Cold start existe.**
   - O primeiro boot precisou carregar o GGUF e a healthcheck ficou em `503` até terminar.

3. **O ROI ainda não justifica trocar o baseline todo.**
   - O baseline hospedado continua mais confortável operacionalmente.

4. **A bateria executada foi forte, mas não exaustiva.**
   - Ainda não houve promoção do Gemma local para:
     - gate de release
     - Telegram real como modo padrão
     - ciclo longo de uso humano contínuo

## Veredito de ROI

### Onde o ROI é alto

- laboratório local;
- benchmark comparativo;
- fallback de soberania tecnológica;
- estudo de provider alternativo;
- superfícies públicas e semânticas;
- experimentação controlada por stack.

### Onde o ROI é médio

- uso diário individual em ambiente local;
- demos técnicas;
- validação de arquitetura multi-provider.

### Onde o ROI ainda é baixo

- substituir o baseline inteiro hospedado;
- promover diretamente para produção local como padrão;
- usar como caminho principal sem uma etapa adicional de observação contínua.

## Recomendação final

A recomendação prática para o EduAssist hoje é:

1. manter `gemini_flash_lite` como baseline operacional padrão;
2. manter `gemma4e4b_local` como perfil experimental oficial;
3. usar o Gemma local quando quisermos:
   - comparar qualidade;
   - validar independência de provider;
   - estudar custo local;
   - rodar laboratório agentic no próprio notebook.

Em outras palavras:

- **a implementação valeu a pena**;
- **a feature flag valeu a pena**;
- **o Gemma local virou uma capacidade útil do sistema**;
- mas **não substitui automaticamente o baseline principal**.

## Comandos úteis

Subir com Gemma local:

```bash
make compose-up-dedicated-core-gemma4e4b-local
```

Voltar para Gemini Flash-Lite:

```bash
make compose-up-dedicated-core-gemini-flash-lite
```

Desligar só o backend local do Gemma:

```bash
make local-llm-gemma4e4b-down
```

Ver logs do backend local:

```bash
make local-llm-gemma4e4b-logs
```

## Fontes

- Google AI for Developers, Gemma overview: <https://ai.google.dev/gemma/docs/core>
- Hugging Face blog, Gemma 4: <https://huggingface.co/blog/gemma4>
- Hugging Face model card, `google/gemma-4-E4B-it`: <https://huggingface.co/google/gemma-4-E4B-it>
- llama.cpp repository: <https://github.com/ggml-org/llama.cpp>
