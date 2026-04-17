# Non-Specialist Answer Surface Rollout - 2026-04-17

## Objetivo

Promover para `langgraph`, `python_functions` e `llamaindex` o mesmo principio arquitetural ja aplicado ao `specialist_supervisor`: toda resposta elegivel deve passar por algum momento LLM-aware no fluxo final, inclusive quando a superficie principal vem de caminho deterministico.

## Implementacao

- o `answer_surface_refiner` do `specialist` permaneceu como baseline da stack especializada;
- as stacks non-specialist passaram a usar um gancho compartilhado de pos-processamento em `stack_postprocessing.py`;
- esse gancho chama `stack_answer_surface_refiner.py`, que:
  - respeita `FEATURE_FLAG_ANSWER_SURFACE_REFINER_ENABLED`;
  - restringe rollout por stack e canal;
  - envia pergunta original + resposta atual + evidencias para a LLM;
  - valida a nova superficie antes de aceitá-la;
  - preserva literalmente o texto original quando a verbalizacao nao for segura.

## Validacao automatizada

- `uv run pytest tests/unit/test_stack_runtime_profiles.py tests/unit/test_answer_surface_refiner.py tests/unit/test_source_mode_settings.py -q`
  - `19 passed, 1 skipped`
- `uv run pytest tests/unit/test_runtime_policies.py tests/unit/test_stack_runtime_profiles.py tests/unit/test_answer_surface_refiner.py tests/unit/test_source_mode_settings.py tests/unit/test_llm_provider_openai_compat.py tests/unit/test_specialist_runtime_helpers.py tests/unit/test_semantic_ingress.py -q`
  - `459 passed, 1 skipped`

## Validacao manual em runtime

Pergunta publica factual: `qual horário de fechamento da biblioteca?`

- `langgraph`
  - resposta funcional preservada
  - `llm_stages`: `turn_frame_classifier`, `structured_polish`, `answer_surface_refiner`
  - `answer_experience_reason`: `structured_grounded_answer:public_direct_answer:validation_rejected`
- `python_functions`
  - resposta funcional preservada
  - `llm_stages`: `turn_frame_classifier`, `answer_surface_refiner`
  - `answer_experience_reason`: `structured_grounded_answer:public_direct_answer:validation_rejected`
- `llamaindex`
  - resposta funcional preservada
  - `llm_stages`: `public_answer_composer`, `answer_surface_refiner`
  - `answer_experience_reason`: `structured_grounded_answer:public_direct_answer:validation_rejected`

Pergunta fora de escopo: `me ajuda a escolher um filme para ver com a família?`

- as tres stacks preservaram o limite de escopo escolar;
- as tres mostraram `answer_surface_refiner` no rastro final;
- o validador recusou reformulacoes inseguras e manteve a resposta grounded.

## Conclusao

O rollout foi bem-sucedido.

- o requisito arquitetural de "sempre haver um momento LLM no fluxo final" agora vale tambem para as stacks non-specialist;
- a qualidade atual foi preservada porque o validador aceitou apenas refinamentos seguros;
- na rodada manual desta data, o efeito dominante foi de **guardrail positivo**: a LLM entrou no fluxo, mas o texto original continuou sendo preservado na maioria dos casos observados, o que e consistente com a meta de nao perder grounding.
