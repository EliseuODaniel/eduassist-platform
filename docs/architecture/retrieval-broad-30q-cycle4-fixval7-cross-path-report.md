# Four-Path Chatbot Comparison Report

Date: 2026-04-16T02:12:06.459893+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle4.json`

LLM forced: `False`

Run prefix: `debug:four-path:normal:20260416T020511Z`

Stack execution mode: `parallel`

Stack concurrency: `4`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency | Final polish |
| --- | --- | --- | --- | --- | --- |
| `langgraph` | `30/30` | `27/30` | `97.2` | `12230.7 ms` | `0/30` |
| `python_functions` | `30/30` | `27/30` | `98.0` | `7954.6 ms` | `0/30` |
| `llamaindex` | `30/30` | `27/30` | `97.2` | `9341.5 ms` | `5/30` |
| `specialist_supervisor` | `30/30` | `30/30` | `99.7` | `4390.6 ms` | `1/30` |

## By Slice

- `protected`
  - `langgraph`: ok 13/13, keyword pass 11/13, quality 96.9, latency 8224.8ms, final polish 0/13
  - `python_functions`: ok 13/13, keyword pass 10/13, quality 95.4, latency 4493.6ms, final polish 0/13
  - `llamaindex`: ok 13/13, keyword pass 11/13, quality 96.9, latency 5924.6ms, final polish 1/13
  - `specialist_supervisor`: ok 13/13, keyword pass 13/13, quality 99.2, latency 552.7ms, final polish 0/13
- `public`
  - `langgraph`: ok 11/11, keyword pass 10/11, quality 95.9, latency 22197.5ms, final polish 0/11
  - `python_functions`: ok 11/11, keyword pass 11/11, quality 100.0, latency 14888.1ms, final polish 0/11
  - `llamaindex`: ok 11/11, keyword pass 10/11, quality 95.9, latency 16699.0ms, final polish 4/11
  - `specialist_supervisor`: ok 11/11, keyword pass 11/11, quality 100.0, latency 10477.7ms, final polish 1/11
- `restricted`
  - `langgraph`: ok 6/6, keyword pass 6/6, quality 100.0, latency 2637.8ms, final polish 0/6
  - `python_functions`: ok 6/6, keyword pass 6/6, quality 100.0, latency 2742.1ms, final polish 0/6
  - `llamaindex`: ok 6/6, keyword pass 6/6, quality 100.0, latency 3255.8ms, final polish 0/6
  - `specialist_supervisor`: ok 6/6, keyword pass 6/6, quality 100.0, latency 1546.2ms, final polish 0/6

## Error Types

- `langgraph`: forbidden_entity_or_value=1, missing_expected_keyword=2
- `python_functions`: missing_expected_keyword=3
- `llamaindex`: forbidden_entity_or_value=1, missing_expected_keyword=2
- `specialist_supervisor`: weak_actionability=1

## Prompt Results

### No procedimento interno de pagamento parcial e negociacao, o que o financeiro deve validar antes de prometer quitacao?

- Slice: `restricted`
- Thread: `retrieval_staff_finance_protocol` turn `1`
- `langgraph`: status 200, latency 5612.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_restricted_document_surface`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_restricted_doc_grounded`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para pagamento parcial e negociacao:
Secao relevante: Procedimento interno para pagamento parcial e negociacao.
Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Complemento interno (Procedimento interno para pagamento parcial e negociacao
- Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_staff_finance_protocol:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > turn_frame:protected.documents.restricted_lookup > langgraph_response_workflow > restricted_retrieval
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:retrieve_restricted_documents, support:citation:Procedimento interno para pagamento parcial e negociacao, doc:Procedimento interno para pagamento parcial e negociacao
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=1, supports=1, citations=1
reason: langgraph_restricted_doc_grounded
final_polish_reason: none
answer_experience_reason: protected_grounded_answer:preserve_restricted_document_surface
context_repair_reason: none
- `python_functions`: status 200, latency 5516.1ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_restricted_document_surface`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_restricted_document_search`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_restricted_document_search`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para pagamento parcial e negociacao:
Secao relevante: Procedimento interno para pagamento parcial e negociacao.
Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Complemento interno (Procedimento interno para pagamento parcial e negociacao
- Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.

Fontes:
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_staff_finance_protocol:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:support > mode:hybrid_retrieval > turn_frame:protected.documents.restricted_lookup > turn_frame:protected.documents.restricted_lookup > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:retrieve_restricted_documents, tool:search_documents, tool:python_functions_native_runtime, support:citation:Procedimento interno para pagamento parcial e negociacao, doc:Procedimento interno para pagamento parcial e negociacao
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=1, supports=1, citations=1
reason: python_functions_native_restricted_document_search
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_restricted_document_surface
context_repair_reason: none
- `llamaindex`: status 200, latency 9385.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_restricted_document_surface`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_restricted_doc_fast_path`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para pagamento parcial e negociacao:
Secao relevante: Procedimento interno para pagamento parcial e negociacao.
Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Complemento interno (Procedimento interno para pagamento parcial e negociacao
- Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_staff_finance_protocol:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:support > mode:hybrid_retrieval > turn_frame:protected.documents.restricted_lookup > llamaindex:restricted > llamaindex:restricted_doc_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:search_documents, support:citation:Procedimento interno para pagamento parcial e negociacao, doc:Procedimento interno para pagamento parcial e negociacao
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=2, supports=2, citations=2
reason: llamaindex_restricted_doc_fast_path
final_polish_reason: none
answer_experience_reason: protected_grounded_answer:preserve_restricted_document_surface
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 1794.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:restricted_document_search`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:restricted_document_search`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para pagamento parcial e negociacao:
Secao relevante: Procedimento interno para pagamento parcial e negociacao.
Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Complemento interno (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_staff_finance_protocol:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > restricted_document_search
llm: no
final_polish: skip
retrieval: backend=qdrant_hybrid, strategy=document_search, sources=2, supports=2, citations=2
reason: specialist_supervisor_tool_first:restricted_document_search
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:citation:Procedimento interno para pagamento parcial e negociacao, doc:Procedimento interno para pagamento parcial e negociacao

### De forma bem objetiva, me de uma visao rapida das proximas avaliacoes dos meus dois filhos.

- Slice: `protected`
- Thread: `retrieval_protected_upcoming_assessments` turn `1`
- `langgraph`: status 200, latency 2136.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Proximas avaliacoes das contas vinculadas:
- Lucas Oliveira (1o Ano A)
- Biologia
- Trabalho B1: 2026-04-18
- Historia
- Trabalho B1: 2026-04-18
- Ingles
- Trabalho B1: 2026-04-18
- Matematica
- Trabalho B1: 2026-04-18
- Ana Oliveira (1o Ano A)
- Biologia
- Trabalho B1: 2026-04-18
- Historia
- Trabalho B1: 2026-04-18
- Ingles
- Trabalho B1: 2026-04-18
- Matematica
- Trabalho B1: 2026-04-18
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_upcoming_assessments:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, support:tool:get_student_academic_summary, +4 more
retrieval: backend=none, strategy=structured_tool, sources=5, supports=5, citations=0
reason: dados estruturados devem passar por service deterministico
final_polish_reason: deterministic_answer
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `python_functions`: status 200, latency 2043.6ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
  answer: Proximas avaliacoes das contas vinculadas:
- Lucas Oliveira (1o Ano A)
- Biologia
- Trabalho B1: 2026-04-18
- Historia
- Trabalho B1: 2026-04-18
- Ingles
- Trabalho B1: 2026-04-18
- Matematica
- Trabalho B1: 2026-04-18
- Ana Oliveira (1o Ano A)
- Biologia
- Trabalho B1: 2026-04-18
- Historia
- Trabalho B1: 2026-04-18
- Ingles
- Trabalho B1: 2026-04-18
- Matematica
- Trabalho B1: 2026-04-18
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_upcoming_assessments:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:structured_tool > turn_frame:protected.academic.upcoming_assessments > turn_frame:protected.academic.upcoming_assessments > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_student_academic_summary, tool:get_student_upcoming_assessments, tool:python_functions_native_runtime, support:tool:get_student_academic_summary, support:tool:get_student_upcoming_assessments
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_structured:academic
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `llamaindex`: status 200, latency 2028.5ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_turn_frame:protected.academic.upcoming_assessments`
  answer: Proximas avaliacoes das contas vinculadas:
- Lucas Oliveira (1o Ano A)
- Biologia
- Trabalho B1: 2026-04-18
- Historia
- Trabalho B1: 2026-04-18
- Ingles
- Trabalho B1: 2026-04-18
- Matematica
- Trabalho B1: 2026-04-18
- Ana Oliveira (1o Ano A)
- Biologia
- Trabalho B1: 2026-04-18
- Historia
- Trabalho B1: 2026-04-18
- Ingles
- Trabalho B1: 2026-04-18
- Matematica
- Trabalho B1: 2026-04-18
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_upcoming_assessments:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:academic > mode:structured_tool > turn_frame:protected.academic.upcoming_assessments > turn_frame:protected.academic.upcoming_assessments > kernel:llamaindex
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_student_academic_summary, tool:get_student_upcoming_assessments, support:tool:get_student_academic_summary, support:tool:get_student_upcoming_assessments
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: llamaindex_turn_frame:protected.academic.upcoming_assessments
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 1490.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:upcoming_assessments_aggregate`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:upcoming_assessments_aggregate`
  answer: Proximas avaliacoes das contas vinculadas:
- Lucas Oliveira (1o Ano A)
  - Biologia - Trabalho B1: 2026-04-18
  - Historia - Trabalho B1: 2026-04-18
  - Ingles - Trabalho B1: 2026-04-18
  - Matematica - Trabalho B1: 2026-04-18
- Ana Oliveira (1o Ano A)
  - Biologia - Trabalho B1: 2026-04-18
  - Historia - Trabalho B1: 2026-04-18
  - Ingles - Trabalho B1: 2026-04-18
  - Matematica - Trabalho B1: 2026-04-18
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_upcoming_assessments:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > upcoming_assessments_aggregate
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: specialist_supervisor_tool_first:upcoming_assessments_aggregate
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:upcoming_assessments:Lucas Oliveira, support:upcoming_assessments:Ana Oliveira

### Pensando no caso pratico, existe canal publico com nome ou contato do professor de matematica, ou isso vai pela coordenacao pedagogica?

- Slice: `public`
- Thread: `retrieval_public_teacher_directory` turn `1`
- `langgraph`: status 200, latency 44236.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `documentary_candidate_selected:topic_coverage=0.25`, probe_topic `governance_channels`, cache_hit `False`, cache_kind `none`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional. Na pratica, o proximo passo e registrar a demanda pelo canal oficial da secretaria ou da coordenacao, para que a escola devolva pelo fluxo institucional.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_teacher_directory:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call
llm: no
final_polish: light_polish (eligible)
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_org_directory, tool:get_public_school_profile, support:scope:public_school_profile, support:tool:get_org_directory, support:tool:get_public_school_profile
retrieval: backend=none, strategy=direct_answer, sources=3, supports=3, citations=0
reason: fato institucional canonico deve vir de fonte estruturada
final_polish_reason: langgraph_public_noncanonical
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `python_functions`: status 200, latency 35904.0ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected:topic_coverage=0.50`, probe_topic `governance_channels`, cache_hit `False`, cache_kind `none`, reason `deterministic_teacher_directory_boundary`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional. Na pratica, o proximo passo e registrar a demanda pelo canal oficial da secretaria ou da coordenacao, para que a escola devolva pelo fluxo institucional.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_teacher_directory:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > turn_frame:input_clarification > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:policy:deterministic_teacher_directory_boundary
retrieval: backend=none, strategy=deterministic_public_guardrail, sources=1, supports=1, citations=0
reason: deterministic_teacher_directory_boundary
final_polish_reason: deterministic_answer
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `llamaindex`: status 200, latency 19124.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_public_guardrail_fast_path`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_deterministic_public_guardrail_fast_path`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional. Na pratica, o proximo passo e registrar a demanda pelo canal oficial da secretaria ou da coordenacao, para que a escola devolva pelo fluxo institucional.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_teacher_directory:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > llamaindex:public > llamaindex:deterministic_public_guardrail_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_deterministic_public_guardrail_fast_path
final_polish_reason: none
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 128.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:teacher_directory_boundary`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:teacher_directory_boundary`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional. Na pratica, o proximo passo e registrar a demanda pelo canal oficial da secretaria ou da coordenacao, para que a escola devolva pelo fluxo institucional.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_teacher_directory:specialist_supervisor
ingress: none:none
path: specialist_supervisor > preflight > teacher_directory_boundary
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=1, supports=1, citations=0
reason: specialist_supervisor_preflight:teacher_directory_boundary
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:profile:Diretorio publico

### Estou autenticado como quem e com qual escopo? Quero saber o que consigo ver de academico e financeiro.

- Slice: `protected`
- Thread: `retrieval_protected_access_scope` turn `1`
- `langgraph`: status 200, latency 1180.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_access_scope`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_access_scope:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_actor_identity_context, support:tool:get_actor_identity_context
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_access_scope
context_repair_reason: none
- `python_functions`: status 200, latency 844.4ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_access_scope`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_authenticated_account_scope`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_authenticated_account_scope`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_access_scope:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:clarify > turn_frame:protected.account.access_scope > turn_frame:protected.account.access_scope > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_actor_identity_context, tool:python_functions_native_runtime, support:tool:get_actor_identity_context
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_authenticated_account_scope
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_access_scope
context_repair_reason: none
- `llamaindex`: status 200, latency 839.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_access_scope`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_protected_records_fast_path`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_access_scope:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:clarify > turn_frame:protected.account.access_scope > llamaindex:protected > llamaindex:protected_records_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_administrative_status, tool:get_student_administrative_status, support:tool:get_administrative_status, support:tool:get_student_administrative_status
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: llamaindex_protected_records_fast_path
final_polish_reason: none
answer_experience_reason: protected_grounded_answer:preserve_access_scope
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 234.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:access_scope`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:access_scope`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Neste canal eu consigo consultar academico e financeiro dos alunos vinculados dentro das permissoes da conta.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiroSe quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro da Ana".
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_access_scope:specialist_supervisor
ingress: none:none
path: specialist_supervisor > fast_path > access_scope
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=1, supports=1, citations=0
reason: specialist_supervisor_fast_path:access_scope
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:account_scope:Conta vinculada

### Pensando no caso pratico, no playbook interno de negociacao financeira, quais criterios orientam uma negociacao com a familia?

- Slice: `restricted`
- Thread: `retrieval_restricted_finance_playbook` turn `1`
- `langgraph`: status 200, latency 1884.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei um criterio interno especifico de negociacao financeira com a familia para esse recorte. Na pratica, o proximo passo e validar essa orientacao com o financeiro responsavel.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_finance_playbook:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=qdrant_hybrid, strategy=structured_tool, sources=1, supports=1, citations=0
reason: langgraph_restricted_document_no_match
final_polish_reason: sensitive_surface
answer_experience_reason: none
context_repair_reason: none
- `python_functions`: status 200, latency 2858.3ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_restricted_document_surface`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_restricted_document_search`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_restricted_document_search`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para pagamento parcial e negociacao:
Secao relevante: Procedimento interno para pagamento parcial e negociacao.
Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

Fontes:
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_finance_playbook:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:support > mode:hybrid_retrieval > turn_frame:protected.documents.restricted_lookup > turn_frame:protected.documents.restricted_lookup > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:retrieve_restricted_documents, tool:search_documents, tool:python_functions_native_runtime, support:citation:Procedimento interno para pagamento parcial e negociacao, doc:Procedimento interno para pagamento parcial e negociacao
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=1, supports=1, citations=1
reason: python_functions_native_restricted_document_search
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_restricted_document_surface
context_repair_reason: none
- `llamaindex`: status 200, latency 2350.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_restricted_document_surface`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_restricted_doc_fast_path`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para pagamento parcial e negociacao:
Secao relevante: Procedimento interno para pagamento parcial e negociacao.
Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_finance_playbook:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:support > mode:hybrid_retrieval > turn_frame:protected.documents.restricted_lookup > llamaindex:restricted > llamaindex:restricted_doc_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:search_documents, support:citation:Procedimento interno para pagamento parcial e negociacao, doc:Procedimento interno para pagamento parcial e negociacao
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=1, supports=1, citations=1
reason: llamaindex_restricted_doc_fast_path
final_polish_reason: none
answer_experience_reason: protected_grounded_answer:preserve_restricted_document_surface
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 1221.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:restricted_document_search`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:restricted_document_search`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Documento principal: Procedimento interno para pagamento parcial e negociacao.
Secao relevante: Procedimento interno para pagamento parcial e negociacao.
Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_finance_playbook:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > restricted_document_search
llm: no
final_polish: skip
retrieval: backend=qdrant_hybrid, strategy=document_search, sources=1, supports=1, citations=1
reason: specialist_supervisor_tool_first:restricted_document_search
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:citation:Procedimento interno para pagamento parcial e negociacao, doc:Procedimento interno para pagamento parcial e negociacao

### Quero um panorama financeiro da familia com boletos, atrasos e o que precisa ser feito agora. Traga a resposta de forma concreta.

- Slice: `protected`
- Thread: `retrieval_protected_finance_panorama` turn `1`
- `langgraph`: status 200, latency 2125.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- Mensalidade: neste recorte, o financeiro mostra 3 cobranca(s) em aberto e 0 vencida(s) nas faturas escolares.
- Taxa: nao apareceu taxa separada no resumo financeiro desta conta.
- Atraso: nao ha fatura vencida agora; o foco fica nos proximos vencimentos.
- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro.
- Na pratica, hoje nao ha bloqueio por atraso vencido; o proximo passo e acompanhar os vencimentos mais proximos e manter os comprovantes em dia.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_finance_panorama:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_financial_summary, support:tool:get_financial_summary
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: dados estruturados devem passar por service deterministico
final_polish_reason: deterministic_answer
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `python_functions`: status 200, latency 1977.2ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_structured:finance`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- Mensalidade: neste recorte, o financeiro mostra 3 cobranca(s) em aberto e 0 vencida(s) nas faturas escolares.
- Taxa: nao apareceu taxa separada no resumo financeiro desta conta.
- Atraso: nao ha fatura vencida agora; o foco fica nos proximos vencimentos.
- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro.
- Na pratica, hoje nao ha bloqueio por atraso vencido; o proximo passo e acompanhar os vencimentos mais proximos e manter os comprovantes em dia.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_finance_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:finance > mode:structured_tool > turn_frame:protected.finance.summary > turn_frame:protected.finance.summary > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_financial_summary, tool:python_functions_native_runtime, support:tool:get_financial_summary
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_structured:finance
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `llamaindex`: status 200, latency 1922.3ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_turn_frame:protected.finance.summary`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- Mensalidade: neste recorte, o financeiro mostra 3 cobranca(s) em aberto e 0 vencida(s) nas faturas escolares.
- Taxa: nao apareceu taxa separada no resumo financeiro desta conta.
- Atraso: nao ha fatura vencida agora; o foco fica nos proximos vencimentos.
- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro.
- Na pratica, hoje nao ha bloqueio por atraso vencido; o proximo passo e acompanhar os vencimentos mais proximos e manter os comprovantes em dia.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_finance_panorama:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:finance > mode:structured_tool > turn_frame:protected.finance.summary > turn_frame:protected.finance.summary > kernel:llamaindex
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_financial_summary, support:tool:get_financial_summary
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_turn_frame:protected.finance.summary
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 588.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_resolved_intent:financial_summary_aggregate`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_resolved_intent:financial_summary_aggregate`
  answer: Hoje nao ha bloqueio financeiro por atraso vencido no recorte da familia.
Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Mensalidade: neste recorte, o financeiro mostra 3 cobranca(s) em aberto e 0 vencida(s) nas faturas escolares.
- Taxa: nao apareceu taxa separada neste recorte financeiro das contas vinculadas.
- Atraso: nao ha fatura vencida agora, so acompanhamento dos proximos vencimentos.
- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro.
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00
Proximo passo: acompanhar os vencimentos mais proximos e manter os comprovantes em dia.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_finance_panorama:specialist_supervisor
ingress: none:none
path: specialist_supervisor > resolved_intent > financial_summary_aggregate
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: specialist_supervisor_resolved_intent:financial_summary_aggregate
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:finance_summary:Lucas Oliveira, support:finance_summary:Ana Oliveira

### Quero saber se a escola publica a quantidade total de professores ou se esse dado nao esta disponivel. Traga a resposta de forma concreta.

- Slice: `public`
- Thread: `retrieval_public_known_unknown_total_teachers` turn `1`
- `langgraph`: status 200, latency 712.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `early_return`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje os canais publicos de Colegio Horizonte nao informam a quantidade total de professores. Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_known_unknown_total_teachers:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_public_school_profile, support:scope:public_profile, support:tool:get_public_school_profile, support:known_unknown:total_teachers
retrieval: backend=none, strategy=direct_answer, sources=3, supports=3, citations=0
reason: fato institucional canonico deve vir de fonte estruturada
final_polish_reason: early_return
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `python_functions`: status 200, latency 9333.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `deterministic_public_known_unknown`
  answer: Hoje os canais publicos de Colegio Horizonte nao informam a quantidade total de professores. Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_known_unknown_total_teachers:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:unknown > mode:clarify > turn_frame:input_clarification > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:policy:deterministic_public_known_unknown
retrieval: backend=none, strategy=deterministic_public_guardrail, sources=1, supports=1, citations=0
reason: deterministic_public_known_unknown
final_polish_reason: deterministic_answer
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `llamaindex`: status 200, latency 21612.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_public_guardrail_fast_path`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_deterministic_public_guardrail_fast_path`
  answer: Hoje os canais publicos de Colegio Horizonte nao informam a quantidade total de professores. Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_known_unknown_total_teachers:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:unknown > mode:clarify > llamaindex:public > llamaindex:deterministic_public_guardrail_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_deterministic_public_guardrail_fast_path
final_polish_reason: none
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 172.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:public_known_unknown`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:public_known_unknown`
  answer: Hoje os canais publicos de Colegio Horizonte nao informam a quantidade total de professores. Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_known_unknown_total_teachers:specialist_supervisor
ingress: none:none
path: specialist_supervisor > preflight > public_known_unknown
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=1, supports=1, citations=0
reason: specialist_supervisor_preflight:public_known_unknown
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:known_unknown:total_teachers

### Sem sair do escopo do projeto, para uma familia entrando agora, como manual de matricula, calendario e agenda de avaliacoes se combinam no inicio do ano?

- Slice: `public`
- Thread: `retrieval_public_family_new_bundle` turn `1`
- `langgraph`: status 200, latency 1429.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares, e fazem mais sentido quando lidos em ordem. Primeiro entram matricula, documentacao inicial, envio digital e canais de atendimento. Depois entram calendario letivo e inicio das aulas, para organizar o comeco do ano. Na sequencia entram agenda de avaliacoes, devolutivas e recuperacoes, para a familia nao perder os marcos pedagogicos. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, a familia usa o manual para entrar corretamente, o calendario para se orientar antes e logo depois do inicio das aulas, e a agenda para acompanhar provas, comunicados e recuperacoes.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_family_new_bundle:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_public_timeline, tool:get_public_school_profile, support:scope:public_school_profile, support:profile_fact:school_name, support:profile_fact:segments, support:profile_fact:highlights, +1 more
retrieval: backend=none, strategy=direct_answer, sources=6, supports=6, citations=0
reason: langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment
final_polish_reason: deterministic_answer
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `python_functions`: status 200, latency 975.5ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares, e fazem mais sentido quando lidos em ordem. Primeiro entram matricula, documentacao inicial, envio digital e canais de atendimento. Depois entram calendario letivo e inicio das aulas, para organizar o comeco do ano. Na sequencia entram agenda de avaliacoes, devolutivas e recuperacoes, para a familia nao perder os marcos pedagogicos. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, a familia usa o manual para entrar corretamente, o calendario para se orientar antes e logo depois do inicio das aulas, e a agenda para acompanhar provas, comunicados e recuperacoes.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_family_new_bundle:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: yes (public_answer_composer)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:project_public_pricing, tool:python_functions_native_runtime, support:tool:get_public_school_profile, support:tool:project_public_pricing
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `llamaindex`: status 200, latency 968.1ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `True`, final_polish_mode `grounded_public_composition`, final_polish_reason `public_answer_composer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares, e fazem mais sentido quando lidos em ordem. Primeiro entram matricula, documentacao inicial, envio digital e canais de atendimento. Depois entram calendario letivo e inicio das aulas, para organizar o comeco do ano. Na sequencia entram agenda de avaliacoes, devolutivas e recuperacoes, para a familia nao perder os marcos pedagogicos. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, a familia usa o manual para entrar corretamente, o calendario para se orientar antes e logo depois do inicio das aulas, e a agenda para acompanhar provas, comunicados e recuperacoes.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_family_new_bundle:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > llamaindex:public > llamaindex:canonical_public_lane_fast_path:public_bundle.family_new_calendar_assessment_enrollment > kernel:llamaindex
llm: yes (public_answer_composer)
final_polish: grounded_public_composition (applied)
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, tool:project_public_pricing, support:tool:get_public_school_profile, support:tool:project_public_pricing
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: llamaindex_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment
final_polish_reason: public_answer_composer
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 198.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:family_new_calendar_enrollment`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares, e fazem mais sentido quando lidos em ordem. Primeiro entram matricula, documentacao inicial, envio digital e canais de atendimento. Depois entram calendario letivo e inicio das aulas, para organizar o comeco do ano. Na sequencia entram agenda de avaliacoes, devolutivas e recuperacoes, para a familia nao perder os marcos pedagogicos. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, a familia usa o manual para entrar corretamente, o calendario para se orientar antes e logo depois do inicio das aulas, e a agenda para acompanhar provas, comunicados e recuperacoes.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_family_new_bundle:specialist_supervisor
ingress: none:none
path: specialist_supervisor > preflight > family_new_calendar_enrollment
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=3, supports=3, citations=0
reason: specialist_supervisor_preflight:family_new_calendar_enrollment
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:document:Calendario Letivo 2026, support:document:Agenda de Avaliacoes 2026, support:document:Manual de Matricula

### Entre meus filhos, quem esta mais vulneravel academicamente hoje? Me de um panorama curto. Seja objetivo e grounded.

- Slice: `protected`
- Thread: `retrieval_protected_family_panorama` turn `1`
- `langgraph`: status 200, latency 1941.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:protected_academic_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Comparando Lucas Oliveira com Ana Oliveira: Lucas Oliveira tem o ponto academico mais sensivel em Fisica, com media parcial 5,9/10, enquanto Ana Oliveira aparece com menor media em Fisica, com 6,4/10. Hoje quem esta mais perto da media minima entre os dois e Lucas Oliveira, puxado por Fisica.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_family_panorama:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, support:tool:get_student_academic_summary, +4 more
retrieval: backend=none, strategy=structured_tool, sources=5, supports=5, citations=0
reason: dados estruturados devem passar por service deterministico
final_polish_reason: deterministic_answer
answer_experience_reason: protected_grounded_answer:protected_academic_direct
context_repair_reason: none
- `python_functions`: status 200, latency 1167.9ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_scope_boundary_surface`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `deterministic_scope_boundary`
  errors: missing_expected_keyword
  answer: Nao tenho base confiavel aqui no EduAssist do Colegio Horizonte para responder esse tema fora do escopo da escola. Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_family_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:structured_tool > turn_frame:protected.academic.family_comparison > turn_frame:protected.academic.family_comparison > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_student_academic_summary, tool:get_public_school_profile, tool:python_functions_native_runtime, support:policy:deterministic_scope_boundary
retrieval: backend=none, strategy=deterministic_public_guardrail, sources=1, supports=1, citations=0
reason: deterministic_scope_boundary
final_polish_reason: deterministic_answer
answer_experience_reason: structured_grounded_answer:preserve_scope_boundary_surface
context_repair_reason: none
- `llamaindex`: status 200, latency 1518.3ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:protected_academic_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `contextual_public_direct_answer`
  answer: Comparando Lucas Oliveira com Ana Oliveira: Lucas Oliveira tem o ponto academico mais sensivel em Fisica, com media parcial 5,9/10, enquanto Ana Oliveira aparece com menor media em Fisica, com 6,4/10. Hoje quem esta mais perto da media minima entre os dois e Lucas Oliveira, puxado por Fisica.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_family_panorama:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:academic > mode:structured_tool > turn_frame:protected.academic.family_comparison > turn_frame:protected.academic.family_comparison > kernel:llamaindex
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_student_academic_summary, tool:get_public_school_profile, support:tool:get_student_academic_summary, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: contextual_public_direct_answer
final_polish_reason: deterministic_answer
answer_experience_reason: protected_grounded_answer:protected_academic_direct
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 710.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:academic_summary_aggregate`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4
Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_family_panorama:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > academic_summary_aggregate
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: specialist_supervisor_tool_first:academic_summary_aggregate
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:academic_summary:Lucas Oliveira, support:academic_summary:Ana Oliveira

### Pensando no caso pratico, mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.

- Slice: `protected`
- Thread: `retrieval_protected_family_panorama` turn `1`
- `langgraph`: status 200, latency 1980.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:protected_academic_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje, a disciplina em que Ana Oliveira aparece com a menor media parcial e Fisica, com 6,4/10, Na sequencia aparecem Educacao Fisica 7,0, Geografia 7,0.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_family_panorama:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, support:tool:get_student_academic_summary, +4 more
retrieval: backend=none, strategy=structured_tool, sources=5, supports=5, citations=0
reason: dados estruturados devem passar por service deterministico
final_polish_reason: deterministic_answer
answer_experience_reason: protected_grounded_answer:protected_academic_direct
context_repair_reason: none
- `python_functions`: status 200, latency 1492.1ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:protected_academic_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
  answer: Hoje, a disciplina em que Ana Oliveira aparece com a menor media parcial e Fisica, com 6,4/10, Na sequencia aparecem Educacao Fisica 7,0, Geografia 7,0.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_family_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:structured_tool > turn_frame:protected.academic.family_comparison > turn_frame:protected.academic.family_comparison > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_student_academic_summary, tool:python_functions_native_runtime, support:tool:get_student_academic_summary
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_structured:academic
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:protected_academic_direct
context_repair_reason: none
- `llamaindex`: status 200, latency 1604.6ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:protected_academic_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_turn_frame:protected.academic.family_comparison`
  answer: Hoje, a disciplina em que Ana Oliveira aparece com a menor media parcial e Fisica, com 6,4/10, Na sequencia aparecem Educacao Fisica 7,0, Geografia 7,0.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_family_panorama:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:academic > mode:structured_tool > turn_frame:protected.academic.family_comparison > turn_frame:protected.academic.family_comparison > kernel:llamaindex
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_student_academic_summary, support:tool:get_student_academic_summary
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_turn_frame:protected.academic.family_comparison
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:protected_academic_direct
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 486.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:academic_summary`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:academic_summary`
  answer: As disciplinas que mais preocupam academicamente em Ana Oliveira hoje sao:
- Fisica: media parcial 6,4
- Educacao Fisica: media parcial 7,0
- Filosofia: media parcial 7,5
A menor nota parcial neste recorte aparece em Fisica, com media 6,4.
Esses componentes merecem acompanhamento primeiro no proximo ciclo de estudo.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_family_panorama:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > academic_summary
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: specialist_supervisor_tool_first:academic_summary
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:academic_summary:Ana Oliveira

### Como regulamentos, frequencia minima e recuperacao se conectam quando o aluno entra em dificuldade academica. Responda de forma direta.

- Slice: `public`
- Thread: `retrieval_public_discipline_recovery` turn `1`
- `langgraph`: status 200, latency 1141.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.academic_policy_overview`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_public_canonical_lane:public_bundle.academic_policy_overview`
  answer: Na pratica, convivencia, frequencia, recuperacao e promocao precisam ser lidas como um mesmo fluxo academico. O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia. Primeiro a familia acompanha criterio, devolutiva e frequencia; depois usa segunda chamada e recuperacao quando houver impacto academico; e, por fim, observa a decisao final de promocao pelo canal oficial.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_discipline_recovery:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_public_school_profile, support:scope:public_school_profile, support:profile_fact:school_name, support:profile_fact:segments, support:profile_fact:highlights, support:tool:get_public_school_profile
retrieval: backend=none, strategy=direct_answer, sources=6, supports=6, citations=0
reason: langgraph_public_canonical_lane:public_bundle.academic_policy_overview
final_polish_reason: deterministic_answer
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `python_functions`: status 200, latency 1032.2ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_canonical_lane:public_bundle.academic_policy_overview`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_canonical_lane:public_bundle.academic_policy_overview`
  answer: Na pratica, convivencia, frequencia, recuperacao e promocao precisam ser lidas como um mesmo fluxo academico. O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia. Primeiro a familia acompanha criterio, devolutiva e frequencia; depois usa segunda chamada e recuperacao quando houver impacto academico; e, por fim, observa a decisao final de promocao pelo canal oficial.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_discipline_recovery:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: yes (public_answer_composer)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_canonical_lane:public_bundle.academic_policy_overview
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `llamaindex`: status 200, latency 865.1ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `True`, final_polish_mode `grounded_public_composition`, final_polish_reason `public_answer_composer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.academic_policy_overview`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`
  answer: Na pratica, convivencia, frequencia, recuperacao e promocao precisam ser lidas como um mesmo fluxo academico. O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia. Primeiro a familia acompanha criterio, devolutiva e frequencia; depois usa segunda chamada e recuperacao quando houver impacto academico; e, por fim, observa a decisao final de promocao pelo canal oficial.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_discipline_recovery:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > llamaindex:public > llamaindex:canonical_public_lane_fast_path:public_bundle.academic_policy_overview > kernel:llamaindex
llm: yes (public_answer_composer)
final_polish: grounded_public_composition (applied)
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_public_canonical_lane:public_bundle.academic_policy_overview
final_polish_reason: public_answer_composer
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 224.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:academic_policy_overview`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:academic_policy_overview`
  answer: Na pratica, convivencia, frequencia, recuperacao e promocao precisam ser lidas como um mesmo fluxo academico. O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia. Primeiro a familia acompanha criterio, devolutiva e frequencia; depois usa segunda chamada e recuperacao quando houver impacto academico; e, por fim, observa a decisao final de promocao pelo canal oficial.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_discipline_recovery:specialist_supervisor
ingress: none:none
path: specialist_supervisor > preflight > academic_policy_overview
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=2, supports=2, citations=0
reason: specialist_supervisor_preflight:academic_policy_overview
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:policy:Academic policy, support:document:Politica de Avaliacao

### O manual interno do professor diz o que sobre registro de avaliacoes e comunicacao pedagogica. Seja objetivo e grounded.

- Slice: `restricted`
- Thread: `retrieval_restricted_teacher_manual` turn `1`
- `langgraph`: status 200, latency 2230.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_restricted_doc_grounded`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_teacher_manual:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > turn_frame:protected.documents.restricted_lookup > langgraph_response_workflow > restricted_retrieval
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:retrieve_restricted_documents, support:citation:Manual interno do professor, doc:Manual interno do professor
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=1, supports=1, citations=1
reason: langgraph_restricted_doc_grounded
final_polish_reason: none
answer_experience_reason: none
context_repair_reason: none
- `python_functions`: status 200, latency 1739.3ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_restricted_document_search`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_restricted_document_search`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

Fontes:
- Manual interno do professor (v1)
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_teacher_manual:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:support > mode:hybrid_retrieval > turn_frame:protected.documents.restricted_lookup > turn_frame:protected.documents.restricted_lookup > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:retrieve_restricted_documents, tool:search_documents, tool:python_functions_native_runtime, support:citation:Manual interno do professor, doc:Manual interno do professor
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=1, supports=1, citations=1
reason: python_functions_native_restricted_document_search
final_polish_reason: sensitive_surface
answer_experience_reason: none
context_repair_reason: none
- `llamaindex`: status 200, latency 1984.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_restricted_doc_fast_path`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_teacher_manual:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:support > mode:hybrid_retrieval > turn_frame:protected.documents.restricted_lookup > llamaindex:restricted > llamaindex:restricted_doc_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:search_documents, support:citation:Manual interno do professor, doc:Manual interno do professor
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=1, supports=1, citations=1
reason: llamaindex_restricted_doc_fast_path
final_polish_reason: none
answer_experience_reason: none
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 2311.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:restricted_document_search`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:restricted_document_search`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Documento principal: Manual interno do professor.
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_teacher_manual:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > restricted_document_search
llm: no
final_polish: skip
retrieval: backend=qdrant_hybrid, strategy=document_search, sources=1, supports=1, citations=1
reason: specialist_supervisor_tool_first:restricted_document_search
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:citation:Manual interno do professor, doc:Manual interno do professor

### Pensando no caso pratico, quero acessar o manual interno do professor pelo bot.

- Slice: `restricted`
- Thread: `retrieval_restricted_denied` turn `1`
- `langgraph`: status 200, latency 1115.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `mode_not_polishable`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal, porque este perfil nao tem acesso a esse material restrito. Se quiser, eu posso orientar pelo material publico correspondente.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_denied:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > deny
llm: no
final_polish: skip
answer_experience: off (none/none)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: support:guardrail:access_control
retrieval: backend=none, strategy=deny, sources=1, supports=1, citations=0
reason: documentos internos exigem perfil com autorizacao explicita para leitura restrita
final_polish_reason: mode_not_polishable
answer_experience_reason: none
context_repair_reason: none
- `python_functions`: status 200, latency 790.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `mode_not_polishable`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_access_deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal, porque este perfil nao tem acesso a esse material restrito. Se quiser, eu posso orientar pelo material publico correspondente.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_denied:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:unknown > mode:clarify > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: off (none/none)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:search_documents, tool:python_functions_native_runtime, support:guardrail:restricted_documents
retrieval: backend=none, strategy=deny, sources=1, supports=1, citations=0
reason: python_functions_native_access_deny
final_polish_reason: mode_not_polishable
answer_experience_reason: none
context_repair_reason: none
- `llamaindex`: status 200, latency 720.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_restricted_doc_access_deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal, porque este perfil nao tem acesso a esse material restrito. Se quiser, eu posso orientar pelo material publico correspondente.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_denied:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:unknown > mode:clarify > llamaindex:restricted_doc_deny
llm: no
final_polish: skip
answer_experience: off (none/none)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner
resources: tool:search_documents, support:guardrail:restricted_documents
retrieval: backend=none, strategy=deny, sources=1, supports=1, citations=0
reason: llamaindex_restricted_doc_access_deny
final_polish_reason: none
answer_experience_reason: none
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 312.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:restricted_document_denied`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola sobre manual interno do professor. Seu perfil nao tem acesso a esse material restrito. Se voce quiser, eu posso explicar apenas o que e publico sobre esse mesmo tema ou abrir um handoff.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_denied:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > restricted_document_denied
llm: no
final_polish: skip
retrieval: backend=none, strategy=deny, sources=1, supports=1, citations=0
reason: specialist_supervisor_tool_first:restricted_document_denied
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:policy:Documento restrito

### Mostre minha grade docente do ano juntando turmas e disciplinas que ficaram sob minha responsabilidade.

- Slice: `protected`
- Thread: `retrieval_teacher_schedule_panorama` turn `1`
- `langgraph`: status 200, latency 25373.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `teacher_role_rescue`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. No uso do calendario publico da escola, priorize datas institucionais abertas a familias e equipe, como reunioes, simulados, conselhos e janelas letivas publicadas. Nos canais oficiais da escola, a secretaria continua sendo o contato institucional mais seguro para comunicacao geral; para alinhamentos pedagogicos, o fluxo correto passa por coordenacao e orientacao conforme o assunto.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_teacher_schedule_panorama:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > teacher_role_rescue
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_teacher_schedule, support:tool:get_teacher_schedule
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: teacher_role_rescue
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `python_functions`: status 200, latency 7010.0ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_teacher_schedule`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_teacher_schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. No uso do calendario publico da escola, priorize datas institucionais abertas a familias e equipe, como reunioes, simulados, conselhos e janelas letivas publicadas. Nos canais oficiais da escola, a secretaria continua sendo o contato institucional mais seguro para comunicacao geral; para alinhamentos pedagogicos, o fluxo correto passa por coordenacao e orientacao conforme o assunto.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_teacher_schedule_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:structured_tool > turn_frame:protected.teacher.schedule > turn_frame:protected.teacher.schedule > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_teacher_schedule, tool:python_functions_native_runtime, support:tool:get_teacher_schedule
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_teacher_schedule
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `llamaindex`: status 200, latency 13038.6ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_turn_frame:protected.teacher.schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. No uso do calendario publico da escola, priorize datas institucionais abertas a familias e equipe, como reunioes, simulados, conselhos e janelas letivas publicadas. Nos canais oficiais da escola, a secretaria continua sendo o contato institucional mais seguro para comunicacao geral; para alinhamentos pedagogicos, o fluxo correto passa por coordenacao e orientacao conforme o assunto.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_teacher_schedule_panorama:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:academic > mode:structured_tool > turn_frame:protected.teacher.schedule > turn_frame:protected.teacher.schedule > kernel:llamaindex
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_teacher_schedule, support:tool:get_teacher_schedule
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_turn_frame:protected.teacher.schedule
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 269.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:teacher_schedule`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. No uso do calendario, priorize datas institucionais abertas a familias e equipe, como reunioes, simulados, conselhos e janelas letivas publicadas. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, o fluxo correto passa por coordenacao e orientacao conforme o assunto.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_teacher_schedule_panorama:specialist_supervisor
ingress: none:none
path: specialist_supervisor > fast_path > teacher_schedule
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: specialist_supervisor_fast_path:teacher_schedule
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:teacher_schedule:Grade docente

### Agora recorte so o que eu tenho no ensino medio.

- Slice: `protected`
- Thread: `retrieval_teacher_schedule_panorama` turn `1`
- `langgraph`: status 200, latency 19465.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `teacher_role_rescue`
  answer: Grade docente de Fernando Azevedo no Ensino Medio:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_teacher_schedule_panorama:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call > teacher_role_rescue
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_teacher_schedule, support:tool:get_teacher_schedule
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: teacher_role_rescue
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `python_functions`: status 200, latency 7325.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_teacher_schedule`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_teacher_schedule`
  answer: Grade docente de Fernando Azevedo no Ensino Medio:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_teacher_schedule_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:unknown > mode:clarify > turn_frame:protected.teacher.schedule > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_teacher_schedule, tool:python_functions_native_runtime, support:tool:get_teacher_schedule
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_teacher_schedule
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `llamaindex`: status 200, latency 13418.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_teacher_schedule_direct`
  answer: Grade docente de Fernando Azevedo no Ensino Medio:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_teacher_schedule_panorama:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:unknown > mode:clarify > llamaindex:workflow > llamaindex:teacher > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, llamaindex:workflow, kernel:llamaindex
resources: tool:get_teacher_schedule, support:tool:get_teacher_schedule
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_teacher_schedule_direct
final_polish_reason: none
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 516.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:teacher_schedule`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Grade docente de Fernando Azevedo no Ensino Medio:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_teacher_schedule_panorama:specialist_supervisor
ingress: none:none
path: specialist_supervisor > fast_path > teacher_schedule
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: specialist_supervisor_fast_path:teacher_schedule
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:teacher_schedule:Grade docente

### Como a escola descreve publicamente a passagem entre coordenacao, direcao e protocolo institucional. Seja objetivo e grounded.

- Slice: `public`
- Thread: `retrieval_public_governance_protocol` turn `1`
- `langgraph`: status 200, latency 63896.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.governance_protocol`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_public_canonical_lane:public_bundle.governance_protocol`
  answer: Na base publica do Colegio Horizonte, a trilha institucional fica mais clara quando secretaria, coordenacao, direcao e canais oficiais aparecem como etapas complementares de encaminhamento e protocolo. Na pratica, o protocolo formal costuma seguir esta ordem: secretaria para registrar e orientar, coordenacao para acompanhar o tema pedagogico ou de convivio, e direcao como instancia de escalonamento institucional quando o assunto sai da rotina normal. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar. Se a familia precisar formalizar um impasse, o proximo passo e abrir o protocolo pelo canal oficial e guardar o registro para o escalonamento ate a direcao.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_governance_protocol:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_org_directory, tool:get_public_school_profile, support:scope:public_school_profile, support:profile_fact:school_name, support:profile_fact:segments, support:profile_fact:highlights, +1 more
retrieval: backend=none, strategy=direct_answer, sources=6, supports=6, citations=0
reason: langgraph_public_canonical_lane:public_bundle.governance_protocol
final_polish_reason: deterministic_answer
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `python_functions`: status 200, latency 23914.2ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier, public_answer_composer`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_canonical_lane:public_bundle.governance_protocol`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_canonical_lane:public_bundle.governance_protocol`
  answer: Na base publica do Colegio Horizonte, a trilha institucional fica mais clara quando secretaria, coordenacao, direcao e canais oficiais aparecem como etapas complementares de encaminhamento e protocolo. Na pratica, o protocolo formal costuma seguir esta ordem: secretaria para registrar e orientar, coordenacao para acompanhar o tema pedagogico ou de convivio, e direcao como instancia de escalonamento institucional quando o assunto sai da rotina normal. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar. Se a familia precisar formalizar um impasse, o proximo passo e abrir o protocolo pelo canal oficial e guardar o registro para o escalonamento ate a direcao.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_governance_protocol:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > turn_frame:input_clarification > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier, public_answer_composer)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_canonical_lane:public_bundle.governance_protocol
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `llamaindex`: status 200, latency 44394.0ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `True`, final_polish_mode `grounded_public_composition`, final_polish_reason `public_answer_composer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.governance_protocol`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_public_canonical_lane:public_bundle.governance_protocol`
  answer: Na base publica do Colegio Horizonte, a trilha institucional fica mais clara quando secretaria, coordenacao, direcao e canais oficiais aparecem como etapas complementares de encaminhamento e protocolo. Na pratica, o protocolo formal costuma seguir esta ordem: secretaria para registrar e orientar, coordenacao para acompanhar o tema pedagogico ou de convivio, e direcao como instancia de escalonamento institucional quando o assunto sai da rotina normal. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar. Se a familia precisar formalizar um impasse, o proximo passo e abrir o protocolo pelo canal oficial e guardar o registro para o escalonamento ate a direcao.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_governance_protocol:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > llamaindex:public > llamaindex:canonical_public_lane_fast_path:public_bundle.governance_protocol > kernel:llamaindex
llm: yes (public_answer_composer)
final_polish: grounded_public_composition (applied)
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_public_canonical_lane:public_bundle.governance_protocol
final_polish_reason: public_answer_composer
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 197.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:governance_protocol`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:governance_protocol`
  answer: Na base publica do Colegio Horizonte, a trilha institucional fica mais clara quando secretaria, coordenacao, direcao e canais oficiais aparecem como etapas complementares de encaminhamento e protocolo. Na pratica, o protocolo formal costuma seguir esta ordem: secretaria para registrar e orientar, coordenacao para acompanhar o tema pedagogico ou de convivio, e direcao como instancia de escalonamento institucional quando o assunto sai da rotina normal. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar. Se a familia precisar formalizar um impasse, o proximo passo e abrir o protocolo pelo canal oficial e guardar o registro para o escalonamento ate a direcao.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_governance_protocol:specialist_supervisor
ingress: none:none
path: specialist_supervisor > preflight > governance_protocol
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=1, supports=1, citations=0
reason: specialist_supervisor_preflight:governance_protocol
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:document:Governanca e Lideranca Institucional

### Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento. Seja objetivo e grounded.

- Slice: `protected`
- Thread: `retrieval_protected_admin_finance_combo` turn `1`
- `langgraph`: status 200, latency 2434.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:supplemental_focus_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje ainda existe bloqueio administrativo ou documental neste recorte. Cadastro e documentacao: Situacao administrativa do seu cadastro hoje: com pendencias.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise. Financeiro: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- Mensalidade: neste recorte, o financeiro mostra 3 cobranca(s) em aberto e 0 vencida(s) nas faturas escolares.
- Taxa: nao apareceu taxa separada no resumo financeiro desta conta.
- Atraso: nao ha fatura vencida agora; o foco fica nos proximos vencimentos.
- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro. - Na pratica, hoje nao ha bloqueio por atraso vencido; o proximo passo e acompanhar os vencimentos mais proximos e manter os comprovantes em dia.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_admin_finance_combo:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_administrative_status, tool:get_student_administrative_status, support:tool:get_administrative_status, support:tool:get_student_administrative_status
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: status administrativo autenticado exige service deterministico
final_polish_reason: deterministic_answer
answer_experience_reason: protected_grounded_answer:supplemental_focus_direct
context_repair_reason: none
- `python_functions`: status 200, latency 2281.5ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:supplemental_focus_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_structured:institution`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:institution`
  answer: Hoje ainda existe bloqueio administrativo ou documental neste recorte. Cadastro e documentacao: Situacao administrativa do seu cadastro hoje: com pendencias.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise. Financeiro: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- Mensalidade: neste recorte, o financeiro mostra 3 cobranca(s) em aberto e 0 vencida(s) nas faturas escolares.
- Taxa: nao apareceu taxa separada no resumo financeiro desta conta.
- Atraso: nao ha fatura vencida agora; o foco fica nos proximos vencimentos.
- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro. - Na pratica, hoje nao ha bloqueio por atraso vencido; o proximo passo e acompanhar os vencimentos mais proximos e manter os comprovantes em dia.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_admin_finance_combo:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > turn_frame:protected.institution.admin_finance_status > turn_frame:protected.institution.admin_finance_status > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_administrative_status, tool:get_financial_summary, tool:python_functions_native_runtime, support:tool:get_administrative_status, support:tool:get_financial_summary
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_structured:institution
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:supplemental_focus_direct
context_repair_reason: none
- `llamaindex`: status 200, latency 2259.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:supplemental_focus_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_turn_frame:protected.institution.admin_finance_status`
  answer: Hoje ainda existe bloqueio administrativo ou documental neste recorte. Cadastro e documentacao: Situacao administrativa do seu cadastro hoje: com pendencias.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise. Financeiro: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- Mensalidade: neste recorte, o financeiro mostra 3 cobranca(s) em aberto e 0 vencida(s) nas faturas escolares.
- Taxa: nao apareceu taxa separada no resumo financeiro desta conta.
- Atraso: nao ha fatura vencida agora; o foco fica nos proximos vencimentos.
- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro. - Na pratica, hoje nao ha bloqueio por atraso vencido; o proximo passo e acompanhar os vencimentos mais proximos e manter os comprovantes em dia.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_admin_finance_combo:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > turn_frame:protected.institution.admin_finance_status > turn_frame:protected.institution.admin_finance_status > kernel:llamaindex
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_administrative_status, tool:get_financial_summary, support:tool:get_administrative_status, support:tool:get_financial_summary
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: llamaindex_turn_frame:protected.institution.admin_finance_status
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:supplemental_focus_direct
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 728.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:admin_finance_overview`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:admin_finance_overview`
  answer: Hoje ainda existe bloqueio administrativo ou documental neste recorte.
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_admin_finance_combo:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > admin_finance_overview
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: specialist_supervisor_tool_first:admin_finance_overview
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:administrative_status:Documentacao, support:finance_summary:Financeiro

### Sem sair do escopo do projeto, na referencia publica atual, quanto fica a matricula e o total por mes para 3 filhos?

- Slice: `public`
- Thread: `retrieval_public_pricing_projection` turn `1`
- `langgraph`: status 200, latency 29673.3ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_pricing_projection`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_turn_frame:public_answer`
  answer: Hoje a escola publica mais de uma referencia combinada de matricula e mensalidade. Para essa simulacao, os totais por segmento ficam assim:
- Ensino Fundamental II (Manha): matricula 3 x R$ 350,00 = R$ 1.050,00; mensalidade por mes 3 x R$ 1.280,00 = R$ 3.840,00.
- Ensino Medio (Manha): matricula 3 x R$ 350,00 = R$ 1.050,00; mensalidade por mes 3 x R$ 1.450,00 = R$ 4.350,00.
Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.
A base publica tambem menciona: Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_pricing_projection:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call > turn_frame:public.enrollment.pricing > langgraph_response_workflow > semantic_ingress
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:get_public_school_profile, tool:project_public_pricing, support:scope:public_school_profile, support:profile_fact:school_name, support:profile_fact:tuition_reference, support:tool:get_public_school_profile
retrieval: backend=none, strategy=direct_answer, sources=6, supports=6, citations=0
reason: langgraph_turn_frame:public_answer
final_polish_reason: none
answer_experience_reason: structured_grounded_answer:preserve_pricing_projection
context_repair_reason: none
- `python_functions`: status 200, latency 43398.3ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `light_polish`, final_polish_reason `python_functions_semantic_ingress_terminal`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_pricing_projection`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_semantic_ingress:pricing`
  answer: Hoje a escola publica mais de uma referencia combinada de matricula e mensalidade. Para essa simulacao, os totais por segmento ficam assim:
- Ensino Fundamental II (Manha): matricula 3 x R$ 350,00 = R$ 1.050,00; mensalidade por mes 3 x R$ 1.280,00 = R$ 3.840,00.
- Ensino Medio (Manha): matricula 3 x R$ 350,00 = R$ 1.050,00; mensalidade por mes 3 x R$ 1.450,00 = R$ 4.350,00.
Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.
A base publica tambem menciona: Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_pricing_projection:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > turn_frame:public.enrollment.pricing > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: light_polish (eligible)
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:project_public_pricing, tool:python_functions_native_runtime, support:tool:get_public_school_profile, support:tool:project_public_pricing
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_semantic_ingress:pricing
final_polish_reason: python_functions_semantic_ingress_terminal
answer_experience_reason: structured_grounded_answer:preserve_pricing_projection
context_repair_reason: none
- `llamaindex`: status 200, latency 20658.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_pricing_projection`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `contextual_public_pricing_fast_path`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_contextual_public_pricing_fast_path`
  answer: Hoje a escola publica mais de uma referencia combinada de matricula e mensalidade. Para essa simulacao, os totais por segmento ficam assim:
- Ensino Fundamental II (Manha): matricula 3 x R$ 350,00 = R$ 1.050,00; mensalidade por mes 3 x R$ 1.280,00 = R$ 3.840,00.
- Ensino Medio (Manha): matricula 3 x R$ 350,00 = R$ 1.050,00; mensalidade por mes 3 x R$ 1.450,00 = R$ 4.350,00.
Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.
A base publica tambem menciona: Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_pricing_projection:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > llamaindex:public > llamaindex:contextual_public_pricing_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, tool:project_public_pricing, support:tool:get_public_school_profile, support:tool:project_public_pricing
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: llamaindex_contextual_public_pricing_fast_path
final_polish_reason: none
answer_experience_reason: structured_grounded_answer:preserve_pricing_projection
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 39480.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:pricing_projection`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:pricing_projection`
  answer: Hoje a escola publica mais de uma referencia combinada de matricula e mensalidade. Para essa simulacao, os totais por segmento ficam assim:
- Ensino Fundamental II (Manha): matricula 3 x R$ 350,00 = R$ 1.050,00; mensalidade por mes 3 x R$ 1.280,00 = R$ 3.840,00,
- Ensino Medio (Manha): matricula 3 x R$ 350,00 = R$ 1.050,00; mensalidade por mes 3 x R$ 1.450,00 = R$ 4.350,00,
Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_pricing_projection:specialist_supervisor
ingress: none:none
path: specialist_supervisor > fast_path > pricing_projection
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=2, supports=2, citations=0
reason: specialist_supervisor_fast_path:pricing_projection
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:pricing_reference:Tabela publica de valores, support:pricing_reference:Quantidade simulada

### Quero uma recomendacao de filme, sem relacao com escola.

- Slice: `public`
- Thread: `retrieval_public_open_world_out_of_scope` turn `1`
- `langgraph`: status 200, latency 30852.9ms, keyword pass `False`, quality `55`, used_llm `True`, llm_stages `grounded_answer_experience`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `early_return`, answer_experience_applied `True`, answer_experience_reason `retrieval_grounded_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  errors: forbidden_entity_or_value
  answer: Não tenho informações sobre recomendações de filmes, pois meu foco é fornecer suporte institucional do Colégio Horizonte. Posso ajudar com informações sobre matrícula, calendário escolar, regras públicas, visitas ou qualquer outro assunto relacionado à escola.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_open_world_out_of_scope:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > hybrid_retrieval
llm: yes (grounded_answer_experience)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:search_public_documents, support:scope:public_school_profile, support:profile_fact:school_name, support:profile_fact:segments, support:profile_fact:highlights, support:tool:search_public_documents
retrieval: backend=qdrant_hybrid, strategy=direct_answer, sources=6, supports=6, citations=0
reason: retrieval hibrido e o caminho padrao para faq e documentos
final_polish_reason: early_return
answer_experience_reason: retrieval_grounded_answer
context_repair_reason: none
- `python_functions`: status 200, latency 17151.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_scope_boundary_surface`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `deterministic_scope_boundary`
  answer: Nao tenho base confiavel aqui no EduAssist do Colegio Horizonte para responder esse tema fora do escopo da escola. Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_open_world_out_of_scope:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:unknown > mode:clarify > turn_frame:input_clarification > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:policy:deterministic_scope_boundary
retrieval: backend=none, strategy=deterministic_public_guardrail, sources=1, supports=1, citations=0
reason: deterministic_scope_boundary
final_polish_reason: deterministic_answer
answer_experience_reason: structured_grounded_answer:preserve_scope_boundary_surface
context_repair_reason: none
- `llamaindex`: status 200, latency 31781.9ms, keyword pass `False`, quality `55`, used_llm `True`, llm_stages `grounded_answer_experience`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_public_guardrail_fast_path`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_deterministic_public_guardrail_fast_path`
  errors: forbidden_entity_or_value
  answer: Não tenho informações sobre recomendações de filmes, pois meu foco é exclusivamente o atendimento escolar do Colégio Horizonte. Posso ajudar com informações sobre matrícula, calendário, regras públicas, visitas ou qualquer outro assunto relacionado à escola.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_open_world_out_of_scope:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:unknown > mode:clarify > llamaindex:public > llamaindex:deterministic_public_guardrail_fast_path > kernel:llamaindex
llm: yes (grounded_answer_experience)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_deterministic_public_guardrail_fast_path
final_polish_reason: none
answer_experience_reason: structured_grounded_answer
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 8399.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:scope_boundary`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:scope_boundary`
  answer: Nao tenho base confiavel aqui no EduAssist do Colegio Horizonte para responder esse tema fora do escopo da escola. Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_open_world_out_of_scope:specialist_supervisor
ingress: none:none
path: specialist_supervisor > fast_path > scope_boundary
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=1, supports=1, citations=0
reason: specialist_supervisor_fast_path:scope_boundary
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:assistant_identity:EduAssist

### Sem sair do escopo do projeto, que limite de acesso no Telegram aparece no protocolo interno para responsaveis com escopo parcial?

- Slice: `restricted`
- Thread: `retrieval_restricted_scope_protocol` turn `1`
- `langgraph`: status 200, latency 2912.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_restricted_doc_grounded`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial.
Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
Complemento interno (Protocolo interno para responsaveis com escopo parcial
- Protocolo interno para responsaveis com escopo parcial): Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_scope_protocol:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > turn_frame:protected.documents.restricted_lookup > langgraph_response_workflow > restricted_retrieval
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:retrieve_restricted_documents, support:citation:Protocolo interno para responsaveis com escopo parcial, doc:Protocolo interno para responsaveis com escopo parcial
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=1, supports=1, citations=1
reason: langgraph_restricted_doc_grounded
final_polish_reason: none
answer_experience_reason: none
context_repair_reason: none
- `python_functions`: status 200, latency 3481.2ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_restricted_document_search`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_restricted_document_search`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial.
Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
Complemento interno (Protocolo interno para responsaveis com escopo parcial
- Protocolo interno para responsaveis com escopo parcial): Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_scope_protocol:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:support > mode:hybrid_retrieval > turn_frame:protected.documents.restricted_lookup > turn_frame:protected.documents.restricted_lookup > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:retrieve_restricted_documents, tool:search_documents, tool:python_functions_native_runtime, support:citation:Protocolo interno para responsaveis com escopo parcial, doc:Protocolo interno para responsaveis com escopo parcial
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=1, supports=1, citations=1
reason: python_functions_native_restricted_document_search
final_polish_reason: sensitive_surface
answer_experience_reason: none
context_repair_reason: none
- `llamaindex`: status 200, latency 3218.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_restricted_doc_fast_path`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial.
Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
Complemento interno (Protocolo interno para responsaveis com escopo parcial
- Protocolo interno para responsaveis com escopo parcial): Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_scope_protocol:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:support > mode:hybrid_retrieval > turn_frame:protected.documents.restricted_lookup > llamaindex:restricted > llamaindex:restricted_doc_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:search_documents, support:citation:Protocolo interno para responsaveis com escopo parcial, doc:Protocolo interno para responsaveis com escopo parcial
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=2, supports=2, citations=2
reason: llamaindex_restricted_doc_fast_path
final_polish_reason: none
answer_experience_reason: none
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 1652.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:restricted_document_search`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:restricted_document_search`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Documento principal: Protocolo interno para responsaveis com escopo parcial.
Secao relevante: Protocolo interno para responsaveis com escopo parcial.
Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
Complemento interno (Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial): Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_scope_protocol:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > restricted_document_search
llm: no
final_polish: skip
retrieval: backend=qdrant_hybrid, strategy=document_search, sources=2, supports=2, citations=2
reason: specialist_supervisor_tool_first:restricted_document_search
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:citation:Protocolo interno para responsaveis com escopo parcial, doc:Protocolo interno para responsaveis com escopo parcial

### Sem autenticar, eu consigo puxar minhas notas por este chat?

- Slice: `protected`
- Thread: `retrieval_protected_boundary_auth_needed` turn `1`
- `langgraph`: status 200, latency 6660.8ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier, grounded_answer_experience`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_turn_frame:public_answer`
  answer: Para consultar notas, faltas ou qualquer dado acadêmico protegido, é necessário que você vincule sua conta do Telegram ao portal da escola. Você deve gerar o código de vinculação no portal autenticado e, em seguida, enviar aqui o comando /start link_<código>. Somente após essa etapa é que poderei consultar seus dados autorizados por este canal.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_boundary_auth_needed:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > deny > turn_frame:auth_guidance > langgraph_response_workflow > semantic_ingress
llm: yes (turn_frame_classifier, grounded_answer_experience)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:get_public_school_profile, support:scope:public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=direct_answer, sources=2, supports=2, citations=0
reason: langgraph_turn_frame:public_answer
final_polish_reason: none
answer_experience_reason: structured_grounded_answer
context_repair_reason: none
- `python_functions`: status 200, latency 9807.5ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier, grounded_answer_experience`, final_polish_applied `False`, final_polish_mode `light_polish`, final_polish_reason `python_functions_semantic_ingress_terminal`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_semantic_ingress:auth_guidance`
  answer: Para consultar notas, faltas ou qualquer informação acadêmica protegida, é necessário vincular sua conta do Telegram ao portal da escola. Você deve fazer isso no portal autenticado, gerar o código de vinculação e, em seguida, enviar o comando /start link_<código> por aqui. Somente após essa etapa eu poderei consultar seus dados autorizados por este canal.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_boundary_auth_needed:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > turn_frame:auth_guidance > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier, grounded_answer_experience)
final_polish: light_polish (eligible)
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_semantic_ingress:auth_guidance
final_polish_reason: python_functions_semantic_ingress_terminal
answer_experience_reason: structured_grounded_answer
context_repair_reason: none
- `llamaindex`: status 200, latency 8185.2ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `semantic_ingress_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `semantic_ingress_terminal`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `semantic_ingress:auth_guidance`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_semantic_ingress:auth_guidance`
  answer: Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal da escola. No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando /start link_<codigo>. Depois disso, eu passo a consultar seus dados autorizados por este canal.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_boundary_auth_needed:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:hybrid_retrieval > turn_frame:auth_guidance > llamaindex:public > llamaindex:semantic_ingress:auth_guidance > kernel:llamaindex
llm: yes (semantic_ingress_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_semantic_ingress:auth_guidance
final_polish_reason: semantic_ingress_terminal
answer_experience_reason: structured_grounded_answer:fallback_to_original
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 300.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:auth_guidance`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:auth_guidance`
  answer: Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal do Colegio Horizonte. No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`. Depois disso, eu passo a consultar seus dados autorizados por este canal.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_boundary_auth_needed:specialist_supervisor
ingress: none:none
path: specialist_supervisor > fast_path > auth_guidance
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=1, supports=1, citations=0
reason: specialist_supervisor_fast_path:auth_guidance
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:auth_guidance:Vinculacao Telegram

### Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.

- Slice: `protected`
- Thread: `retrieval_student_academic_self` turn `1`
- `langgraph`: status 200, latency 38272.6ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Hoje Miguel Pereira ainda tem pendencias na documentacao.
Proximo passo: Aguarde a conferencia final da secretaria ou envie o comprovante solicitado, se houver retorno do setor.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_student_academic_self:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_administrative_status, tool:get_student_administrative_status, support:tool:get_administrative_status, support:tool:get_student_administrative_status
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: dados estruturados devem passar por service deterministico
final_polish_reason: deterministic_answer
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `python_functions`: status 200, latency 19866.0ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `python_functions_native_structured:institution`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:institution`
  errors: missing_expected_keyword
  answer: Hoje Miguel Pereira ainda tem pendencias na documentacao.
Proximo passo: Aguarde a conferencia final da secretaria ou envie o comprovante solicitado, se houver retorno do setor.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_student_academic_self:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_administrative_status, tool:get_student_administrative_status, tool:python_functions_native_runtime, support:tool:get_administrative_status, support:tool:get_student_administrative_status
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_structured:institution
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `llamaindex`: status 200, latency 25830.9ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_local_protected:academic`
  errors: missing_expected_keyword
  answer: Sem problema, ajustei isso por aqui.

Hoje Miguel Pereira ainda tem pendencias na documentacao.
Proximo passo: Aguarde a conferencia final da secretaria ou envie o comprovante solicitado, se houver retorno do setor.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_student_academic_self:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:academic > mode:structured_tool > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_administrative_status, tool:get_student_administrative_status, support:tool:get_administrative_status, support:tool:get_student_administrative_status
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: llamaindex_local_protected:academic
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 363.8ms, keyword pass `True`, quality `90`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:academic_progression`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:academic_progression`
  errors: weak_actionability
  answer: Hoje, a melhor disciplina de Miguel Pereira e Portugues, com media parcial 8,7. A pior disciplina aparece em Fisica, com media parcial 8,0. Em Fisica, faltam 0,0 ponto(s) para atingir 7,0; a media parcial atual ja esta em 8,0.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_student_academic_self:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > academic_progression
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: specialist_supervisor_tool_first:academic_progression
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:academic_summary:Miguel Pereira

### Como biblioteca e laboratorios entram nas regras de uso e no apoio ao estudo do ensino medio. Responda de forma direta.

- Slice: `public`
- Thread: `retrieval_public_facilities_study` turn `1`
- `langgraph`: status 200, latency 1120.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.facilities_study_support`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_public_canonical_lane:public_bundle.facilities_study_support`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno. Na pratica, biblioteca, laboratorios e estudo orientado funcionam como tres apoios complementares: pesquisa e leitura, experimentacao e producao, e organizacao da rotina de estudo. Se a necessidade principal for pesquisa, leitura ou projeto escrito, a referencia mais direta e a biblioteca. Se o foco for aula pratica, prototipo ou experimento, o caminho mais aderente sao os laboratorios. Se a duvida for organizar tarefas, leitura e habitos de estudo, o estudo orientado entra como apoio mais direto.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_facilities_study:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_public_school_profile, support:scope:public_school_profile, support:profile_fact:school_name, support:profile_fact:segments, support:profile_fact:highlights, support:tool:get_public_school_profile
retrieval: backend=none, strategy=direct_answer, sources=6, supports=6, citations=0
reason: langgraph_public_canonical_lane:public_bundle.facilities_study_support
final_polish_reason: deterministic_answer
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `python_functions`: status 200, latency 804.2ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_canonical_lane:public_bundle.facilities_study_support`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_canonical_lane:public_bundle.facilities_study_support`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno. Na pratica, biblioteca, laboratorios e estudo orientado funcionam como tres apoios complementares: pesquisa e leitura, experimentacao e producao, e organizacao da rotina de estudo. Se a necessidade principal for pesquisa, leitura ou projeto escrito, a referencia mais direta e a biblioteca. Se o foco for aula pratica, prototipo ou experimento, o caminho mais aderente sao os laboratorios. Se a duvida for organizar tarefas, leitura e habitos de estudo, o estudo orientado entra como apoio mais direto.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_facilities_study:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: yes (public_answer_composer)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_canonical_lane:public_bundle.facilities_study_support
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `llamaindex`: status 200, latency 723.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.facilities_study_support`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno. Na pratica, biblioteca, laboratorios e estudo orientado funcionam como tres apoios complementares: pesquisa e leitura, experimentacao e producao, e organizacao da rotina de estudo. Se a necessidade principal for pesquisa, leitura ou projeto escrito, a referencia mais direta e a biblioteca. Se o foco for aula pratica, prototipo ou experimento, o caminho mais aderente sao os laboratorios. Se a duvida for organizar tarefas, leitura e habitos de estudo, o estudo orientado entra como apoio mais direto.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_facilities_study:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > llamaindex:public > llamaindex:canonical_public_lane_fast_path:public_bundle.facilities_study_support > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_public_canonical_lane:public_bundle.facilities_study_support
final_polish_reason: none
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 184.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:facilities_study_support`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:facilities_study_support`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno. Na pratica, biblioteca, laboratorios e estudo orientado funcionam como tres apoios complementares: pesquisa e leitura, experimentacao e producao, e organizacao da rotina de estudo. Se a necessidade principal for pesquisa, leitura ou projeto escrito, a referencia mais direta e a biblioteca. Se o foco for aula pratica, prototipo ou experimento, o caminho mais aderente sao os laboratorios. Se a duvida for organizar tarefas, leitura e habitos de estudo, o estudo orientado entra como apoio mais direto.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_facilities_study:specialist_supervisor
ingress: none:none
path: specialist_supervisor > preflight > facilities_study_support
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=2, supports=2, citations=0
reason: specialist_supervisor_preflight:facilities_study_support
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:document:Servicos e Espacos Escolares, support:document:Programa de Periodo Integral e Estudo Orientado

### Quero ver o quadro documental da Ana: o que esta pendente e o que a familia precisa fazer em seguida. Seja objetivo e grounded.

- Slice: `protected`
- Thread: `retrieval_protected_admin_docs` turn `1`
- `langgraph`: status 200, latency 2084.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `status administrativo autenticado exige service deterministico`
  answer: Panorama documental das contas vinculadas:
- Lucas Oliveira: situacao documental regular.
- Ana Oliveira: situacao documental com pendencias. Ponto pendente: Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
Quem ainda tem pendencia documental mais clara neste recorte: Ana Oliveira.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_admin_docs:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_administrative_status, tool:get_student_administrative_status, support:tool:get_administrative_status, support:tool:get_student_administrative_status
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: status administrativo autenticado exige service deterministico
final_polish_reason: deterministic_answer
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `python_functions`: status 200, latency 1559.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `python_functions_native_structured:institution`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:institution`
  answer: Panorama documental das contas vinculadas:
- Lucas Oliveira: situacao documental regular.
- Ana Oliveira: situacao documental com pendencias. Ponto pendente: Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
Quem ainda tem pendencia documental mais clara neste recorte: Ana Oliveira.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_admin_docs:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_administrative_status, tool:get_student_administrative_status, tool:python_functions_native_runtime, support:tool:get_administrative_status, support:tool:get_student_administrative_status
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_structured:institution
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `llamaindex`: status 200, latency 1767.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_local_protected:institution`
  answer: Panorama documental das contas vinculadas:
- Lucas Oliveira: situacao documental regular.
- Ana Oliveira: situacao documental com pendencias. Ponto pendente: Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
Quem ainda tem pendencia documental mais clara neste recorte: Ana Oliveira.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_admin_docs:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_administrative_status, tool:get_student_administrative_status, support:tool:get_administrative_status, support:tool:get_student_administrative_status
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: llamaindex_local_protected:institution
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 472.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:administrative_status`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:administrative_status`
  answer: Hoje Ana Oliveira ainda tem pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_admin_docs:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > administrative_status
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: specialist_supervisor_tool_first:administrative_status
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:administrative_status:Ana Oliveira

### Sem sair do escopo do projeto, os documentos internos mencionam algum protocolo para excursao internacional com pernoite no ensino medio?

- Slice: `restricted`
- Thread: `retrieval_restricted_no_match` turn `1`
- `langgraph`: status 200, latency 2071.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_restricted_doc_no_match`
  answer: Nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio nos documentos internos disponiveis. Na pratica, o proximo passo e consultar o setor responsavel por esse protocolo interno ou eu posso trazer apenas o correspondente publico.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_no_match:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > turn_frame:protected.documents.restricted_lookup > langgraph_response_workflow > restricted_retrieval
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:retrieve_restricted_documents, support:tool:retrieve_restricted_documents
retrieval: backend=qdrant_hybrid, strategy=structured_tool, sources=1, supports=1, citations=0
reason: langgraph_restricted_doc_no_match
final_polish_reason: none
answer_experience_reason: none
context_repair_reason: none
- `python_functions`: status 200, latency 2067.1ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_restricted_document_no_match`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_restricted_document_no_match`
  answer: Nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio nos documentos internos disponiveis. Na pratica, o proximo passo e consultar o setor responsavel por esse protocolo interno ou eu posso trazer apenas o correspondente publico.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_no_match:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:support > mode:hybrid_retrieval > turn_frame:protected.documents.restricted_lookup > turn_frame:protected.documents.restricted_lookup > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:retrieve_restricted_documents, tool:search_documents, tool:python_functions_native_runtime, support:tool:retrieve_restricted_documents, support:tool:search_documents
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=2, supports=2, citations=0
reason: python_functions_native_restricted_document_no_match
final_polish_reason: sensitive_surface
answer_experience_reason: none
context_repair_reason: none
- `llamaindex`: status 200, latency 1875.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_restricted_doc_no_match`
  answer: Nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio nos documentos internos disponiveis. Na pratica, o proximo passo e consultar o setor responsavel por esse protocolo interno ou eu posso trazer apenas o correspondente publico.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_no_match:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:support > mode:hybrid_retrieval > turn_frame:protected.documents.restricted_lookup > llamaindex:restricted > llamaindex:restricted_doc_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:search_documents, support:tool:search_documents
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=1, supports=1, citations=0
reason: llamaindex_restricted_doc_no_match
final_polish_reason: none
answer_experience_reason: none
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 1984.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:restricted_document_no_match`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:restricted_document_no_match`
  answer: Nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio nos documentos internos disponiveis do Colegio Horizonte. Na pratica, o proximo passo e consultar o setor responsavel por esse protocolo interno ou pedir apenas o correspondente publico.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_restricted_no_match:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > restricted_document_no_match
llm: no
final_polish: skip
retrieval: backend=qdrant_hybrid, strategy=document_search, sources=0, supports=1, citations=0
reason: specialist_supervisor_tool_first:restricted_document_no_match
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:retrieval:Documentos restritos

### De forma bem objetiva, por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola?

- Slice: `public`
- Thread: `retrieval_public_service_routing` turn `1`
- `langgraph`: status 200, latency 64911.8ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_service_routing`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_public_compound_contextual_direct`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Direcao geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br. Contatos diretos: email direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, matricula e atendimento comercial, whatsapp comercial ou visita guiada. Contatos diretos: email admissoes@colegiohorizonte.edu.br | telefone (11) 3333-4201 | WhatsApp (11) 97500-2040.
- Financeiro: bot, financeiro, portal autenticado ou email institucional. Contatos diretos: email financeiro@colegiohorizonte.edu.br | telefone (11) 3333-4203.

Voce pode falar com a direcao geral pelo canal institucional direcao@colegiohorizonte.edu.br. Atende por agenda institucional e participa dos encontros de familias a cada bimestre.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_service_routing:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call > turn_frame:input_clarification > langgraph_response_workflow > public_compound_contextual_direct
llm: yes (public_answer_composer)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:get_public_school_profile, tool:get_service_directory, tool:get_org_directory, support:tool:get_public_school_profile, support:tool:get_service_directory, support:tool:get_org_directory
retrieval: backend=none, strategy=structured_tool, sources=3, supports=3, citations=0
reason: langgraph_public_compound_contextual_direct
final_polish_reason: none
answer_experience_reason: structured_grounded_answer:preserve_service_routing
context_repair_reason: none
- `python_functions`: status 200, latency 29649.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier, public_answer_composer`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_service_routing`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_public_compound`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_public_compound`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Direcao geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br. Contatos diretos: email direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, matricula e atendimento comercial, whatsapp comercial ou visita guiada. Contatos diretos: email admissoes@colegiohorizonte.edu.br | telefone (11) 3333-4201 | WhatsApp (11) 97500-2040.
- Financeiro: bot, financeiro, portal autenticado ou email institucional. Contatos diretos: email financeiro@colegiohorizonte.edu.br | telefone (11) 3333-4203.

Voce pode falar com a direcao geral pelo canal institucional direcao@colegiohorizonte.edu.br. Atende por agenda institucional e participa dos encontros de familias a cada bimestre.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_service_routing:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > turn_frame:input_clarification > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier, public_answer_composer)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:project_public_pricing, tool:python_functions_native_runtime, support:tool:get_public_school_profile, support:tool:project_public_pricing
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_public_compound
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer:preserve_service_routing
context_repair_reason: none
- `llamaindex`: status 200, latency 41983.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_service_routing`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `contextual_public_direct_fast_path`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_contextual_public_direct_fast_path`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Direcao geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br. Contatos diretos: email direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada. Contatos diretos: email admissoes@colegiohorizonte.edu.br | telefone (11) 3333-4201 | WhatsApp (11) 97500-2040.
- Financeiro: bot, financeiro, portal autenticado ou email institucional. Contatos diretos: email financeiro@colegiohorizonte.edu.br | telefone (11) 3333-4203.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_service_routing:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > llamaindex:public > llamaindex:contextual_public_direct_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, tool:project_public_pricing, support:tool:get_public_school_profile, support:tool:project_public_pricing
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: llamaindex_contextual_public_direct_fast_path
final_polish_reason: none
answer_experience_reason: structured_grounded_answer:preserve_service_routing
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 65867.3ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `True`, final_polish_mode `grounded_public_composition`, final_polish_reason `public_answer_composer`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:service_routing`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:service_routing`
  answer: Para falar com o setor financeiro, você pode usar o bot, o canal financeiro, o portal autenticado ou o e-mail institucional. Para a direção, utilize o bot, a ouvidoria ou o protocolo institucional.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_service_routing:specialist_supervisor
ingress: none:none
path: specialist_supervisor > fast_path > service_routing
llm: yes (public_answer_composer)
final_polish: grounded_public_composition (applied)
retrieval: backend=none, strategy=direct_answer, sources=1, supports=1, citations=0
reason: specialist_supervisor_fast_path:service_routing
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:service_routing:Setores

### Nao e a biblioteca da escola: me diga o horario da biblioteca publica municipal.

- Slice: `public`
- Thread: `retrieval_public_external_library_boundary` turn `1`
- `langgraph`: status 200, latency 5114.5ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_scope_boundary_surface`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_turn_frame:external_public_facility_boundary`
  answer: No EduAssist do Colegio Horizonte, eu consigo responder apenas sobre servicos, documentos e canais da escola. Como sua pergunta fala de uma biblioteca publica externa, esse assunto fica fora do escopo da escola e eu nao tenho base aqui para informar esse dado externo. Se quiser, eu posso te dizer o equivalente publicado sobre a estrutura ou os canais do colegio.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_external_library_boundary:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call > turn_frame:scope_boundary > langgraph_response_workflow > semantic_ingress
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: langgraph_turn_frame:external_public_facility_boundary
final_polish_reason: none
answer_experience_reason: structured_grounded_answer:preserve_scope_boundary_surface
context_repair_reason: none
- `python_functions`: status 200, latency 870.4ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_scope_boundary_surface`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_external_public_facility_boundary`
  answer: No EduAssist do Colegio Horizonte, eu consigo responder apenas sobre servicos, documentos e canais da escola. Como sua pergunta fala de uma biblioteca publica externa, esse assunto fica fora do escopo da escola e eu nao tenho base aqui para informar esse dado externo. Se quiser, eu posso te dizer o equivalente publicado sobre a estrutura ou os canais do colegio.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_external_library_boundary:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:unknown > mode:clarify > turn_frame:scope_boundary > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:policy:external_public_facility_boundary
retrieval: backend=none, strategy=scope_boundary, sources=1, supports=1, citations=0
reason: python_functions_native_external_public_facility_boundary
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer:preserve_scope_boundary_surface
context_repair_reason: none
- `llamaindex`: status 200, latency 856.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_scope_boundary_surface`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `external_public_facility_boundary_fast_path`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_external_public_facility_boundary_fast_path`
  answer: No EduAssist do Colegio Horizonte, eu consigo responder apenas sobre servicos, documentos e canais da escola. Como sua pergunta fala de uma biblioteca publica externa, esse assunto fica fora do escopo da escola e eu nao tenho base aqui para informar esse dado externo. Se quiser, eu posso te dizer o equivalente publicado sobre a estrutura ou os canais do colegio.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_external_library_boundary:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:unknown > mode:structured_tool > llamaindex:public > llamaindex:external_public_facility_boundary_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_external_public_facility_boundary_fast_path
final_polish_reason: none
answer_experience_reason: structured_grounded_answer:preserve_scope_boundary_surface
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 247.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:scope_boundary`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:scope_boundary`
  answer: No EduAssist do Colegio Horizonte, eu consigo responder apenas sobre servicos e canais da escola. Como sua pergunta fala de uma biblioteca publica externa, esse assunto fica fora do escopo da escola e eu nao tenho base aqui para informar esse horario. Se quiser, eu posso te dizer o horario da biblioteca do colegio.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_external_library_boundary:specialist_supervisor
ingress: none:none
path: specialist_supervisor > fast_path > scope_boundary
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=1, supports=1, citations=0
reason: specialist_supervisor_fast_path:scope_boundary
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:assistant_identity:EduAssist

### Sem sair do escopo do projeto, se eu ficar sem acesso e ainda precisar mandar documentos, qual e a ordem mais segura entre portal, credenciais e secretaria?

- Slice: `public`
- Thread: `retrieval_public_docs_credentials` turn `1`
- `langgraph`: status 200, latency 1082.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.secretaria_portal_credentials`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`
  answer: Para documentos, portal e credenciais, a familia precisa olhar tudo como um fluxo unico e em ordem. Primeiro entram secretaria, envio de documentos e prazos tipicos da matricula ou da declaracao pedida. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Depois entram portal, aplicativo e credenciais pessoais para acompanhar a rotina sem depender de atendimento manual. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Se houver perda de acesso ou erro de cadastro, o proximo passo e acionar recuperacao e suporte. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_docs_credentials:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_service_directory, tool:get_public_school_profile, support:scope:public_school_profile, support:profile_fact:school_name, support:profile_fact:segments, support:profile_fact:highlights, +1 more
retrieval: backend=none, strategy=direct_answer, sources=6, supports=6, citations=0
reason: langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials
final_polish_reason: deterministic_answer
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `python_functions`: status 200, latency 735.1ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_canonical_lane:public_bundle.secretaria_portal_credentials`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_canonical_lane:public_bundle.secretaria_portal_credentials`
  answer: Para documentos, portal e credenciais, a familia precisa olhar tudo como um fluxo unico e em ordem. Primeiro entram secretaria, envio de documentos e prazos tipicos da matricula ou da declaracao pedida. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Depois entram portal, aplicativo e credenciais pessoais para acompanhar a rotina sem depender de atendimento manual. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Se houver perda de acesso ou erro de cadastro, o proximo passo e acionar recuperacao e suporte. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_docs_credentials:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: yes (public_answer_composer)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_canonical_lane:public_bundle.secretaria_portal_credentials
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `llamaindex`: status 200, latency 722.0ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `True`, final_polish_mode `grounded_public_composition`, final_polish_reason `public_answer_composer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.secretaria_portal_credentials`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials`
  answer: Para documentos, portal e credenciais, a familia precisa olhar tudo como um fluxo unico e em ordem. Primeiro entram secretaria, envio de documentos e prazos tipicos da matricula ou da declaracao pedida. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Depois entram portal, aplicativo e credenciais pessoais para acompanhar a rotina sem depender de atendimento manual. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Se houver perda de acesso ou erro de cadastro, o proximo passo e acionar recuperacao e suporte. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_docs_credentials:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > llamaindex:public > llamaindex:canonical_public_lane_fast_path:public_bundle.secretaria_portal_credentials > kernel:llamaindex
llm: yes (public_answer_composer)
final_polish: grounded_public_composition (applied)
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials
final_polish_reason: public_answer_composer
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 155.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:service_credentials_bundle`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:service_credentials_bundle`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_public_docs_credentials:specialist_supervisor
ingress: none:none
path: specialist_supervisor > preflight > service_credentials_bundle
llm: no
final_polish: skip
retrieval: backend=none, strategy=direct_answer, sources=2, supports=2, citations=0
reason: specialist_supervisor_preflight:service_credentials_bundle
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:document:Secretaria, Documentacao e Prazos, support:document:Politica de Uso do Portal, Aplicativo e Credenciais

### Nao quero so os numeros: olhando meus dois filhos, quem merece o alerta de frequencia mais urgente agora?

- Slice: `protected`
- Thread: `retrieval_protected_attendance_panorama` turn `1`
- `langgraph`: status 200, latency 1962.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama de frequencia das contas vinculadas:
- Lucas Oliveira: 6 falta(s), 7 atraso(s), 19 presenca(s), 370 minuto(s) de ausencia. Ponto mais sensivel: Biologia (1 falta(s), 0 atraso(s)).
- Ana Oliveira: 6 falta(s), 9 atraso(s), 17 presenca(s), 410 minuto(s) de ausencia. Ponto mais sensivel: Portugues (1 falta(s), 1 atraso(s)).
Quem exige maior atencao agora: Ana Oliveira. O ponto mais sensivel aparece em Portugues.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_attendance_panorama:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, support:tool:get_student_academic_summary, +4 more
retrieval: backend=none, strategy=structured_tool, sources=5, supports=5, citations=0
reason: dados estruturados devem passar por service deterministico
final_polish_reason: deterministic_answer
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `python_functions`: status 200, latency 1844.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `python_functions_native_family_attendance_aggregate`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_family_attendance_aggregate`
  answer: Panorama de frequencia das contas vinculadas:
- Lucas Oliveira: 6 falta(s), 7 atraso(s), 19 presenca(s), 370 minuto(s) de ausencia. Ponto mais sensivel: Biologia (1 falta(s), 0 atraso(s)).
- Ana Oliveira: 6 falta(s), 9 atraso(s), 17 presenca(s), 410 minuto(s) de ausencia. Ponto mais sensivel: Portugues (1 falta(s), 1 atraso(s)).
Quem exige maior atencao agora: Ana Oliveira. O ponto mais sensivel aparece em Portugues.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_attendance_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, tool:python_functions_native_runtime, +5 more
retrieval: backend=none, strategy=structured_tool, sources=5, supports=5, citations=0
reason: python_functions_native_family_attendance_aggregate
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `llamaindex`: status 200, latency 1688.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_local_protected:academic`
  answer: Panorama de frequencia das contas vinculadas:
- Lucas Oliveira: 6 falta(s), 7 atraso(s), 19 presenca(s), 370 minuto(s) de ausencia. Ponto mais sensivel: Biologia (1 falta(s), 0 atraso(s)).
- Ana Oliveira: 6 falta(s), 9 atraso(s), 17 presenca(s), 410 minuto(s) de ausencia. Ponto mais sensivel: Portugues (1 falta(s), 1 atraso(s)).
Quem exige maior atencao agora: Ana Oliveira. O ponto mais sensivel aparece em Portugues.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_attendance_panorama:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:academic > mode:structured_tool > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, support:tool:get_student_academic_summary, +4 more
retrieval: backend=none, strategy=structured_tool, sources=5, supports=5, citations=0
reason: llamaindex_local_protected:academic
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 557.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:attendance_summary_aggregate`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:attendance_summary_aggregate`
  answer: Panorama de frequencia das contas vinculadas:
- Na frequencia de Lucas Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 7 atraso(s) e 19 presenca(s) neste recorte.
- Na frequencia de Ana Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 9 atraso(s) e 17 presenca(s) neste recorte.
Quem exige maior atencao agora: Ana Oliveira.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_attendance_panorama:specialist_supervisor
ingress: none:none
path: specialist_supervisor > tool_first > attendance_summary_aggregate
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: specialist_supervisor_tool_first:attendance_summary_aggregate
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:academic_summary:Lucas Oliveira, support:academic_summary:Ana Oliveira

### Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia.

- Slice: `protected`
- Thread: `retrieval_protected_attendance_panorama` turn `1`
- `langgraph`: status 200, latency 1305.4ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.conduct_frequency_punctuality`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_public_canonical_lane:public_bundle.conduct_frequency_punctuality`
  errors: missing_expected_keyword
  answer: Pontualidade, frequencia e convivencia aparecem juntas nos documentos publicos da escola. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. Na pratica, o proximo passo e justificar faltas no prazo, alinhar pontualidade e acionar a coordenacao assim que a frequencia comecar a comprometer a rotina academica.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_attendance_panorama:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call > protected_domain_rescue
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, tool:get_public_school_profile, +6 more
retrieval: backend=none, strategy=structured_tool, sources=6, supports=6, citations=0
reason: langgraph_public_canonical_lane:public_bundle.conduct_frequency_punctuality
final_polish_reason: deterministic_answer
answer_experience_reason: protected_grounded_answer:public_direct_answer
context_repair_reason: none
- `python_functions`: status 200, latency 1197.2ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `surface_not_enabled`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:institution`
  errors: missing_expected_keyword
  answer: Pontualidade, frequencia e convivencia aparecem juntas nos documentos publicos da escola. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. Na pratica, o proximo passo e justificar faltas no prazo, alinhar pontualidade e acionar a coordenacao assim que a frequencia comecar a comprometer a rotina academica.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_attendance_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_structured:institution
final_polish_reason: surface_not_enabled
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `llamaindex`: status 200, latency 2917.5ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `True`, final_polish_mode `grounded_public_composition`, final_polish_reason `public_answer_composer`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.conduct_frequency_punctuality`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_public_canonical_lane:public_bundle.conduct_frequency_punctuality`
  errors: missing_expected_keyword
  answer: Pontualidade, frequencia e convivencia aparecem juntas nos documentos publicos da escola. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. Na pratica, o proximo passo e justificar faltas no prazo, alinhar pontualidade e acionar a coordenacao assim que a frequencia comecar a comprometer a rotina academica.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_attendance_panorama:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > llamaindex:public > llamaindex:canonical_public_lane_fast_path:public_bundle.conduct_frequency_punctuality > kernel:llamaindex
llm: yes (public_answer_composer)
final_polish: grounded_public_composition (applied)
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_public_canonical_lane:public_bundle.conduct_frequency_punctuality
final_polish_reason: public_answer_composer
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 466.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_resolved_intent:attendance_summary`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_resolved_intent:attendance_summary`
  answer: Na frequencia de Lucas Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 7 atraso(s) e 19 presenca(s) neste recorte.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260416T020511Z:retrieval_protected_attendance_panorama:specialist_supervisor
ingress: none:none
path: specialist_supervisor > resolved_intent > attendance_summary
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: specialist_supervisor_resolved_intent:attendance_summary
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:academic_summary:Lucas Oliveira

