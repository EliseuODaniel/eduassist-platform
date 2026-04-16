# Four-Path Chatbot Comparison Report

Date: 2026-04-15T04:16:04.610370+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle1.json`

LLM forced: `False`

Run prefix: `debug:four-path:normal:20260415T040512Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency | Final polish |
| --- | --- | --- | --- | --- | --- |
| `langgraph` | `19/30` | `14/30` | `58.5` | `17046.9 ms` | `0/30` |
| `python_functions` | `21/30` | `17/30` | `65.5` | `17880.1 ms` | `0/30` |
| `llamaindex` | `21/30` | `17/30` | `65.2` | `16477.6 ms` | `4/30` |
| `specialist_supervisor` | `25/30` | `21/30` | `79.2` | `8537.5 ms` | `1/30` |

## By Slice

- `protected`
  - `langgraph`: ok 9/13, keyword pass 7/13, quality 66.2, latency 18815.7ms, final polish 0/13
  - `python_functions`: ok 10/13, keyword pass 9/13, quality 75.4, latency 13239.6ms, final polish 0/13
  - `llamaindex`: ok 10/13, keyword pass 9/13, quality 75.4, latency 12970.0ms, final polish 0/13
  - `specialist_supervisor`: ok 12/13, keyword pass 11/13, quality 90.8, latency 5967.8ms, final polish 0/13
- `public`
  - `langgraph`: ok 4/11, keyword pass 3/11, quality 30.5, latency 19040.0ms, final polish 0/11
  - `python_functions`: ok 6/11, keyword pass 5/11, quality 47.7, latency 27074.5ms, final polish 0/11
  - `llamaindex`: ok 5/11, keyword pass 4/11, quality 37.7, latency 27882.8ms, final polish 4/11
  - `specialist_supervisor`: ok 7/11, keyword pass 6/11, quality 57.7, latency 15106.4ms, final polish 1/11
- `restricted`
  - `langgraph`: ok 6/6, keyword pass 4/6, quality 93.3, latency 9560.4ms, final polish 0/6
  - `python_functions`: ok 5/6, keyword pass 3/6, quality 76.7, latency 11077.9ms, final polish 0/6
  - `llamaindex`: ok 6/6, keyword pass 4/6, quality 93.3, latency 3168.2ms, final polish 0/6
  - `specialist_supervisor`: ok 6/6, keyword pass 4/6, quality 93.3, latency 2062.6ms, final polish 0/6

## Error Types

- `langgraph`: forbidden_entity_or_value=1, missing_expected_keyword=5, request_failed=11
- `python_functions`: forbidden_entity_or_value=1, missing_expected_keyword=4, request_failed=9, weak_actionability=1
- `llamaindex`: forbidden_entity_or_value=1, missing_expected_keyword=4, request_failed=9, weak_actionability=2
- `specialist_supervisor`: forbidden_entity_or_value=1, missing_expected_keyword=4, request_failed=5

## Prompt Results

### Sem sair do escopo do projeto, a escola tem documento interno sobre excursao internacional com hospedagem para o ensino medio?

- Slice: `restricted`
- Thread: `retrieval_restricted_no_match` turn `1`
- `langgraph`: status 200, latency 30718.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_restricted_doc_no_match`
  answer: Nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio nos documentos internos disponiveis. Na pratica, o proximo passo e consultar o setor responsavel por esse protocolo interno ou eu posso trazer apenas o correspondente publico.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_no_match:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > turn_frame:input_clarification > langgraph_response_workflow > restricted_retrieval
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=qdrant_hybrid, strategy=structured_tool, sources=1, supports=1, citations=0
reason: langgraph_restricted_doc_no_match
final_polish_reason: none
answer_experience_reason: none
context_repair_reason: none
- `python_functions`: status 599, latency 40068.6ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `llamaindex`: status 200, latency 819.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_restricted_doc_no_match`
  answer: Nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio nos documentos internos disponiveis. Na pratica, o proximo passo e consultar o setor responsavel por esse protocolo interno ou eu posso trazer apenas o correspondente publico.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_no_match:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:unknown > mode:hybrid_retrieval > llamaindex:restricted > llamaindex:restricted_doc_fast_path > kernel:llamaindex
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
- `specialist_supervisor`: status 200, latency 326.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:restricted_document_no_match`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:restricted_document_no_match`
  answer: Nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio nos documentos internos disponiveis do Colegio Horizonte. Na pratica, o proximo passo e consultar o setor responsavel por esse protocolo interno ou pedir apenas o correspondente publico.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_no_match:specialist_supervisor
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

### Nao e a biblioteca da escola: me diga o horario da biblioteca publica municipal.

- Slice: `public`
- Thread: `retrieval_public_external_library_boundary` turn `1`
- `langgraph`: status 200, latency 701.0ms, keyword pass `False`, quality `35`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_turn_frame:scope_boundary`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: A biblioteca se chama Biblioteca Aurora e funciona Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_external_library_boundary:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > public_slice > structured_tool_call > turn_frame:public.facilities.library.hours > langgraph_response_workflow > semantic_ingress
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:get_public_school_profile, support:scope:public_school_profile, support:profile_fact:school_name, support:profile_fact:shift_offers, support:tool:get_public_school_profile
retrieval: backend=none, strategy=direct_answer, sources=6, supports=6, citations=0
reason: langgraph_turn_frame:scope_boundary
final_polish_reason: none
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `python_functions`: status 200, latency 14309.6ms, keyword pass `False`, quality `35`, used_llm `True`, llm_stages `turn_frame_classifier, public_answer_composer`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_public_compound`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_public_compound`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: A biblioteca se chama Biblioteca Aurora e funciona Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_external_library_boundary:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > turn_frame:public.facilities.library.hours > turn_frame:public.facilities.library.hours > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier, public_answer_composer)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_public_compound
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `llamaindex`: status 200, latency 533.5ms, keyword pass `False`, quality `35`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `contextual_public_boundary_fast_path`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_contextual_public_boundary_fast_path`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: A biblioteca se chama Biblioteca Aurora e funciona Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_external_library_boundary:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > turn_frame:public.facilities.library.hours > llamaindex:public > llamaindex:contextual_public_boundary_fast_path > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_contextual_public_boundary_fast_path
final_polish_reason: none
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 4569.3ms, keyword pass `False`, quality `35`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `True`, final_polish_mode `grounded_public_composition`, final_polish_reason `public_answer_composer`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:library_hours`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:library_hours`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: A biblioteca pública municipal não foi mencionada nas evidências.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_external_library_boundary:specialist_supervisor
ingress: none:none
path: specialist_supervisor > fast_path > library_hours
llm: yes (public_answer_composer)
final_polish: grounded_public_composition (applied)
retrieval: backend=none, strategy=direct_answer, sources=1, supports=1, citations=0
reason: specialist_supervisor_fast_path:library_hours
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:profile_fact:Biblioteca Aurora

### Existe numero publico de professores na escola ou esse dado nao e informado oficialmente?

- Slice: `public`
- Thread: `retrieval_public_known_unknown_total_teachers` turn `1`
- `langgraph`: status 599, latency 40144.9ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 200, latency 13690.9ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_public_unpublished_fact`
  answer: Hoje os canais publicos de Colegio Horizonte nao informam a quantidade total de professores. Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_known_unknown_total_teachers:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:unknown > mode:clarify > turn_frame:input_clarification > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:python_functions_native_runtime, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_public_unpublished_fact
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `llamaindex`: status 599, latency 40082.4ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `specialist_supervisor`: status 200, latency 197.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:public_known_unknown`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:public_known_unknown`
  answer: Hoje os canais publicos de Colegio Horizonte nao informam a quantidade total de professores. Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_known_unknown_total_teachers:specialist_supervisor
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

### De que forma os documentos publicos ligam biblioteca, laboratorios e estudo orientado como suporte ao ensino medio. Responda de forma direta.

- Slice: `public`
- Thread: `retrieval_public_facilities_study` turn `1`
- `langgraph`: status 599, latency 1587.2ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 200, latency 22481.9ms, keyword pass `True`, quality `90`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_canonical_lane:public_bundle.facilities_study_support`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_canonical_lane:public_bundle.facilities_study_support`
  errors: weak_actionability
  answer: A biblioteca oferece apoio para pesquisa e leitura, enquanto os laboratórios são usados para experimentação e produção prática. O estudo orientado complementa esses espaços, auxiliando na organização da rotina de estudos, o que se conecta ao Ensino Médio através de monitorias, pesquisa e projetos práticos no contraturno.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_facilities_study:python_functions
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
- `llamaindex`: status 200, latency 18708.0ms, keyword pass `True`, quality `90`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `True`, final_polish_mode `grounded_public_composition`, final_polish_reason `public_answer_composer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.facilities_study_support`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`
  errors: weak_actionability
  answer: A biblioteca, os laboratórios e o estudo orientado funcionam como apoios complementares ao currículo do Ensino Médio. A biblioteca apoia pesquisa e leitura, os laboratórios são usados para experimentação e produção prática, e o estudo orientado ajuda na organização da rotina de estudos.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_facilities_study:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > llamaindex:public > llamaindex:canonical_public_lane_fast_path:public_bundle.facilities_study_support > kernel:llamaindex
llm: yes (public_answer_composer)
final_polish: grounded_public_composition (applied)
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_public_canonical_lane:public_bundle.facilities_study_support
final_polish_reason: public_answer_composer
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 257.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:facilities_study_support`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:facilities_study_support`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno. Na pratica, biblioteca, laboratorios e estudo orientado funcionam como tres apoios complementares: pesquisa e leitura, experimentacao e producao, e organizacao da rotina de estudo. Se a necessidade principal for pesquisa, leitura ou projeto escrito, a referencia mais direta e a biblioteca. Se o foco for aula pratica, prototipo ou experimento, o caminho mais aderente sao os laboratorios. Se a duvida for organizar tarefas, leitura e habitos de estudo, o estudo orientado entra como apoio mais direto.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_facilities_study:specialist_supervisor
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

### Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?

- Slice: `protected`
- Thread: `retrieval_protected_admin_docs` turn `1`
- `langgraph`: status 200, latency 2062.9ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_protected_finance_surface`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  errors: missing_expected_keyword
  answer: Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_admin_docs:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > protected_domain_rescue
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_financial_summary, support:tool:get_financial_summary
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_protected_finance_surface
context_repair_reason: none
- `python_functions`: status 200, latency 1908.6ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:supplemental_focus_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_structured:institution`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:institution`
  answer: Ana Oliveira ainda tem pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_admin_docs:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > turn_frame:protected.administrative.status > protected_domain_rescue > turn_frame:protected.administrative.status > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_student_administrative_status, tool:get_administrative_status, tool:python_functions_native_runtime, support:tool:get_student_administrative_status, support:tool:get_administrative_status
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_structured:institution
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:supplemental_focus_direct
context_repair_reason: none
- `llamaindex`: status 200, latency 1864.4ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:supplemental_focus_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_turn_frame:protected.administrative.status`
  answer: Ana Oliveira ainda tem pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_admin_docs:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > turn_frame:protected.administrative.status > protected_domain_rescue > turn_frame:protected.administrative.status > kernel:llamaindex
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_student_administrative_status, tool:get_administrative_status, support:tool:get_student_administrative_status, support:tool:get_administrative_status
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: llamaindex_turn_frame:protected.administrative.status
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:supplemental_focus_direct
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 434.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:administrative_status`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:administrative_status`
  answer: Hoje Ana Oliveira ainda tem pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_admin_docs:specialist_supervisor
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

### Pensando no caso pratico, quais criterios o playbook interno usa para conduzir negociacao financeira com a familia?

- Slice: `restricted`
- Thread: `retrieval_restricted_finance_playbook` turn `1`
- `langgraph`: status 200, latency 1794.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_restricted_doc_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei um criterio interno especifico de negociacao financeira com a familia para esse recorte. Na pratica, o proximo passo e validar essa orientacao com o financeiro responsavel.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_finance_playbook:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > turn_frame:scope_boundary > langgraph_response_workflow > restricted_retrieval
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=qdrant_hybrid, strategy=structured_tool, sources=1, supports=1, citations=0
reason: langgraph_restricted_doc_no_match
final_polish_reason: none
answer_experience_reason: none
context_repair_reason: none
- `python_functions`: status 200, latency 4085.4ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier, grounded_answer_experience`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:unknown`
  answer: Não encontrei informações sobre os critérios que o playbook interno utiliza para conduzir negociações financeiras com as famílias.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_finance_playbook:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:unknown > mode:hybrid_retrieval > turn_frame:scope_boundary > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier, grounded_answer_experience)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:search_documents, tool:python_functions_native_runtime, support:tool:search_documents
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_structured:unknown
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer
context_repair_reason: none
- `llamaindex`: status 200, latency 2431.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_restricted_doc_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei um criterio interno especifico de negociacao financeira com a familia para esse recorte. Na pratica, o proximo passo e validar essa orientacao com o financeiro responsavel.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_finance_playbook:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:unknown > mode:hybrid_retrieval > llamaindex:restricted > llamaindex:restricted_doc_fast_path > kernel:llamaindex
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
- `specialist_supervisor`: status 200, latency 681.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:restricted_document_no_match`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, quais criterios o playbook interno usa para conduzir negociacao financeira com a familia". Na pratica, o proximo passo e consultar o setor responsavel ou pedir apenas o material publico correspondente.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_finance_playbook:specialist_supervisor
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

### Sem sair do escopo do projeto, existe canal publico com nome ou contato do professor de matematica, ou isso vai pela coordenacao pedagogica?

- Slice: `public`
- Thread: `retrieval_public_teacher_directory` turn `1`
- `langgraph`: status 599, latency 40127.6ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 599, latency 40102.8ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `llamaindex`: status 599, latency 40079.6ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `specialist_supervisor`: status 200, latency 185.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:teacher_directory_boundary`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:teacher_directory_boundary`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional. Na pratica, o proximo passo e registrar a demanda pelo canal oficial da secretaria ou da coordenacao, para que a escola devolva pelo fluxo institucional.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_teacher_directory:specialist_supervisor
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

### Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?

- Slice: `public`
- Thread: `retrieval_public_open_world_out_of_scope` turn `1`
- `langgraph`: status 599, latency 40172.5ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 599, latency 40143.1ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `llamaindex`: status 599, latency 40116.4ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `specialist_supervisor`: status 599, latency 40076.6ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 

### Quero minhas notas sem passar por login. O que acontece nesse caso?

- Slice: `protected`
- Thread: `retrieval_protected_boundary_auth_needed` turn `1`
- `langgraph`: status 599, latency 40204.3ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 599, latency 40165.3ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `llamaindex`: status 599, latency 40123.4ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `specialist_supervisor`: status 599, latency 40088.5ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 

### Sem sair do escopo do projeto, pelo manual interno do professor, qual e a regra para registro de avaliacoes e comunicacao com foco pedagogico?

- Slice: `restricted`
- Thread: `retrieval_restricted_teacher_manual` turn `1`
- `langgraph`: status 200, latency 2219.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_restricted_doc_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Sem sair do escopo do projeto, pelo manual interno do professor, qual e a regra para registro de avaliacoes e comunicacao com foco pedagogico". Na pratica, esta base nao trouxe detalhe interno suficiente para responder com seguranca; o proximo passo e consultar o setor responsavel ou pedir apenas o material publico correspondente.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_teacher_manual:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > langgraph_response_workflow > restricted_retrieval
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, support:tool:get_student_academic_summary, +4 more
retrieval: backend=qdrant_hybrid, strategy=structured_tool, sources=5, supports=5, citations=0
reason: langgraph_restricted_doc_no_match
final_polish_reason: none
answer_experience_reason: none
context_repair_reason: none
- `python_functions`: status 200, latency 2887.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `kernel_restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Sem sair do escopo do projeto, pelo manual interno do professor, qual e a regra para registro de avaliacoes e comunicacao com foco pedagogico". Na pratica, esta base nao trouxe detalhe interno suficiente para responder com seguranca; o proximo passo e consultar o setor responsavel ou pedir apenas o material publico correspondente.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_teacher_manual:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:hybrid_retrieval > kernel:python_functions
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:search_documents
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=0, supports=0, citations=0
reason: kernel_restricted_document_no_match
final_polish_reason: sensitive_surface
answer_experience_reason: none
context_repair_reason: none
- `llamaindex`: status 200, latency 1906.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_restricted_doc_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Sem sair do escopo do projeto, pelo manual interno do professor, qual e a regra para registro de avaliacoes e comunicacao com foco pedagogico". Na pratica, esta base nao trouxe detalhe interno suficiente para responder com seguranca; o proximo passo e consultar o setor responsavel ou pedir apenas o material publico correspondente.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_teacher_manual:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:academic > mode:hybrid_retrieval > llamaindex:restricted > llamaindex:restricted_doc_fast_path > kernel:llamaindex
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
- `specialist_supervisor`: status 200, latency 712.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:restricted_document_no_match`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:restricted_document_no_match`
  answer: Consultei o material interno do professor do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para: "Sem sair do escopo do projeto, pelo manual interno do professor, qual e a regra para registro de avaliacoes e comunicacao com foco pedagogico". Na pratica, o proximo passo e confirmar se voce quer o recorte por avaliacao, comunicacao pedagogica ou devolutiva de aprendizagem, para eu tentar uma busca interna mais focal.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_teacher_manual:specialist_supervisor
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

### Cruze regulamentos gerais, politica de avaliacao e orientacao ao estudante para explicar como disciplina, frequencia e recuperacao se influenciam. Traga a resposta de forma concreta.

- Slice: `public`
- Thread: `retrieval_public_discipline_recovery` turn `1`
- `langgraph`: status 200, latency 1267.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.academic_policy_overview`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_public_canonical_lane:public_bundle.academic_policy_overview`
  answer: Na pratica, convivencia, frequencia, recuperacao e promocao precisam ser lidas como um mesmo fluxo academico. O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia. Primeiro a familia acompanha criterio, devolutiva e frequencia; depois usa segunda chamada e recuperacao quando houver impacto academico; e, por fim, observa a decisao final de promocao pelo canal oficial.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_discipline_recovery:langgraph
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
- `python_functions`: status 599, latency 40120.3ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `llamaindex`: status 200, latency 39218.6ms, keyword pass `True`, quality `90`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `True`, final_polish_mode `grounded_public_composition`, final_polish_reason `public_answer_composer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.academic_policy_overview`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`
  errors: weak_actionability
  answer: A disciplina, a frequência e a recuperação formam um fluxo acadêmico integrado. O processo avaliativo considera o desempenho global, que é influenciado pela frequência mínima de 75,0% por componente e pelo desempenho geral. Caso o desempenho esteja abaixo do esperado, a escola pode oferecer recuperação paralela, monitoria ou avaliação substitutiva. A promoção considera esses três fatores em conjunto, sendo fundamental que a família acompanhe o desempenho, a frequência e as devolutivas pedagógicas.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_discipline_recovery:llamaindex
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
- `specialist_supervisor`: status 200, latency 235.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:academic_policy_overview`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:academic_policy_overview`
  answer: Na pratica, convivencia, frequencia, recuperacao e promocao precisam ser lidas como um mesmo fluxo academico. O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia. Primeiro a familia acompanha criterio, devolutiva e frequencia; depois usa segunda chamada e recuperacao quando houver impacto academico; e, por fim, observa a decisao final de promocao pelo canal oficial.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_discipline_recovery:specialist_supervisor
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

### Na rotina interna de negociacao financeira, quais validacoes antecedem qualquer promessa de quitacao?

- Slice: `restricted`
- Thread: `retrieval_staff_finance_protocol` turn `1`
- `langgraph`: status 200, latency 19835.3ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `grounded_answer_experience`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `mode_not_polishable`, answer_experience_applied `True`, answer_experience_reason `clarify_repair_grounded_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  errors: missing_expected_keyword
  answer: Não tenho informações detalhadas sobre a rotina interna de negociação financeira, pois esse assunto foge do escopo das informações públicas e documentais que tenho acesso. Posso ajudar com informações sobre matrícula, calendário escolar, regras públicas, visitas, notas, frequência ou outros tópicos gerais da escola.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_staff_finance_protocol:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > clarify
llm: yes (grounded_answer_experience)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: support:clarify:needs_clarification
retrieval: backend=none, strategy=clarify, sources=1, supports=1, citations=0
reason: a intencao esta ambigua e exige clarificacao antes de recuperar contexto
final_polish_reason: mode_not_polishable
answer_experience_reason: clarify_repair_grounded_answer
context_repair_reason: none
- `python_functions`: status 200, latency 16687.0ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `turn_frame_classifier, grounded_answer_experience`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:unknown`
  errors: missing_expected_keyword
  answer: Não há informações disponíveis sobre as validações internas de negociação financeira no material fornecido.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_staff_finance_protocol:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:unknown > mode:clarify > turn_frame:scope_boundary > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier, grounded_answer_experience)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:python_functions_native_runtime
retrieval: backend=none, strategy=structured_tool, sources=0, supports=0, citations=0
reason: python_functions_native_structured:unknown
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer
context_repair_reason: none
- `llamaindex`: status 200, latency 11985.4ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `grounded_answer_experience`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `contextual_public_direct_answer`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `contextual_public_direct_answer`
  errors: missing_expected_keyword
  answer: Não tenho informações sobre os procedimentos internos de negociação financeira, como as validações que antecedem uma promessa de quitação. Meu atendimento se restringe a informações públicas sobre a escola, como matrícula, calendário, regras gerais, informações sobre visitas, notas, frequência ou questões financeiras gerais.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_staff_finance_protocol:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:unknown > mode:clarify > llamaindex:public > llamaindex:contextual_public_direct > kernel:llamaindex
llm: yes (grounded_answer_experience)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: contextual_public_direct_answer
final_polish_reason: none
answer_experience_reason: structured_grounded_answer
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 9651.7ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `request_failed_fallback`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_request_failed_fallback`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_request_failed_fallback`
  errors: missing_expected_keyword
  answer: Tive uma falha interna ao tentar montar essa resposta. Para nao te devolver algo inconsistente, fiquei no fallback seguro: posso responder apenas o que estiver sustentado no material publico ou reabrir a pergunta em um recorte mais especifico.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_staff_finance_protocol:specialist_supervisor
ingress: none:none
path: specialist_supervisor > fallback > request_failed
llm: no
final_polish: skip
retrieval: backend=none, strategy=deny, sources=0, supports=1, citations=0
reason: specialist_supervisor_request_failed_fallback
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:runtime_fallback:Falha interna controlada

### Sem sair do escopo do projeto, como esta a situacao financeira da familia neste momento, incluindo atrasos, vencimentos proximos e proximo passo?

- Slice: `protected`
- Thread: `retrieval_protected_finance_panorama` turn `1`
- `langgraph`: status 200, latency 2408.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:protected_finance_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de março de 2026 (1450.00).
- Mensalidade: neste recorte, o financeiro mostra 3 cobranca(s) em aberto e 0 vencida(s) nas faturas escolares.
- Taxa: nao apareceu taxa separada no resumo financeiro desta conta.
- Atraso: nao ha fatura vencida agora; o foco fica nos proximos vencimentos.
- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro.
- Proximo passo recomendado: acompanhar os vencimentos mais proximos e manter os comprovantes em dia.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_finance_panorama:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > protected_domain_rescue
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_financial_summary, support:tool:get_financial_summary
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:protected_finance_direct
context_repair_reason: none
- `python_functions`: status 200, latency 2250.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:protected_finance_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `python_functions_native_structured:finance`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de março de 2026 (1450.00).
- Mensalidade: neste recorte, o financeiro mostra 3 cobranca(s) em aberto e 0 vencida(s) nas faturas escolares.
- Taxa: nao apareceu taxa separada no resumo financeiro desta conta.
- Atraso: nao ha fatura vencida agora; o foco fica nos proximos vencimentos.
- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro.
- Proximo passo recomendado: acompanhar os vencimentos mais proximos e manter os comprovantes em dia.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_finance_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:finance > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_financial_summary, tool:python_functions_native_runtime, support:tool:get_financial_summary
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: python_functions_native_structured:finance
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:protected_finance_direct
context_repair_reason: none
- `llamaindex`: status 200, latency 2024.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:protected_finance_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_local_protected:finance`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de março de 2026 (1450.00).
- Mensalidade: neste recorte, o financeiro mostra 3 cobranca(s) em aberto e 0 vencida(s) nas faturas escolares.
- Taxa: nao apareceu taxa separada no resumo financeiro desta conta.
- Atraso: nao ha fatura vencida agora; o foco fica nos proximos vencimentos.
- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro.
- Proximo passo recomendado: acompanhar os vencimentos mais proximos e manter os comprovantes em dia.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_finance_panorama:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:finance > mode:structured_tool > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_financial_summary, support:tool:get_financial_summary
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_local_protected:finance
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:protected_finance_direct
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 478.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_resolved_intent:financial_summary_aggregate`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_resolved_intent:financial_summary_aggregate`
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
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_finance_panorama:specialist_supervisor
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

### Se o acesso falhou bem na hora de enviar documentos, como portal, credenciais e secretaria devem ser tratados na sequencia correta. Traga a resposta de forma concreta.

- Slice: `public`
- Thread: `retrieval_public_docs_credentials` turn `1`
- `langgraph`: status 200, latency 1244.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.secretaria_portal_credentials`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`
  answer: Para documentos, portal e credenciais, a familia precisa olhar tudo como um fluxo unico e em ordem. Primeiro entram secretaria, envio de documentos e prazos tipicos da matricula ou da declaracao pedida. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Depois entram portal, aplicativo e credenciais pessoais para acompanhar a rotina sem depender de atendimento manual. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Se houver perda de acesso ou erro de cadastro, o proximo passo e acionar recuperacao e suporte. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_docs_credentials:langgraph
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
- `python_functions`: status 200, latency 8839.2ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_canonical_lane:public_bundle.secretaria_portal_credentials`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_canonical_lane:public_bundle.secretaria_portal_credentials`
  answer: Primeiro, a família deve tratar o envio de documentos, que pode ser feito pelo portal, e-mail ou presencialmente, seguindo os prazos específicos. Depois, deve-se utilizar o portal e as credenciais pessoais para acompanhar a rotina. Em caso de falha de acesso ou erro de cadastro, o próximo passo é acionar a recuperação e o suporte institucional, entrando em contato com a secretaria.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_docs_credentials:python_functions
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
- `llamaindex`: status 200, latency 3896.3ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `True`, final_polish_mode `grounded_public_composition`, final_polish_reason `public_answer_composer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.secretaria_portal_credentials`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials`
  answer: Primeiro, a família deve tratar o envio de documentos, que pode ser feito pelo portal, e-mail ou presencialmente, seguindo os prazos específicos. Depois, deve-se utilizar o portal e as credenciais pessoais para acompanhar a rotina. Em caso de falha de acesso ou erro de cadastro, o próximo passo é acionar a recuperação e o suporte institucional, entrando em contato com a secretaria ou pelo suporte institucional.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_docs_credentials:llamaindex
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
- `specialist_supervisor`: status 200, latency 240.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:service_credentials_bundle`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:service_credentials_bundle`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_docs_credentials:specialist_supervisor
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

### Mostre o manual interno do professor para mim. Seja objetivo e grounded.

- Slice: `restricted`
- Thread: `retrieval_restricted_denied` turn `1`
- `langgraph`: status 200, latency 720.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `mode_not_polishable`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal, porque este perfil nao tem acesso a esse material restrito. Se quiser, eu posso orientar pelo material publico correspondente.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_denied:langgraph
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
- `python_functions`: status 200, latency 661.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `mode_not_polishable`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_access_deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal, porque este perfil nao tem acesso a esse material restrito. Se quiser, eu posso orientar pelo material publico correspondente.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_denied:python_functions
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
- `llamaindex`: status 200, latency 426.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_restricted_doc_access_deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal, porque este perfil nao tem acesso a esse material restrito. Se quiser, eu posso orientar pelo material publico correspondente.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_denied:llamaindex
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
- `specialist_supervisor`: status 200, latency 203.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:restricted_document_denied`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola sobre manual interno do professor. Seu perfil nao tem acesso a esse material restrito. Se voce quiser, eu posso explicar apenas o que e publico sobre esse mesmo tema ou abrir um handoff.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_denied:specialist_supervisor
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

### Sem tabela, diga minha melhor disciplina, a pior e quanto ainda falta para eu fechar a media em fisica.

- Slice: `protected`
- Thread: `retrieval_student_academic_self` turn `1`
- `langgraph`: status 599, latency 40120.4ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 599, latency 40095.2ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `llamaindex`: status 599, latency 40070.5ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `specialist_supervisor`: status 200, latency 30272.4ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `specialist_execution`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_direct:academic_specialist`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_direct:academic_specialist`
  answer: Para fornecer a disciplina melhor, a pior, ou calcular quantos pontos faltam para você fechar a média em Física, preciso saber a qual aluno você se refere. Por favor, forneça o nome completo do estudante para que eu possa acessar os dados acadêmicos corretos.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_student_academic_self:specialist_supervisor
ingress: none:none
path: specialist_supervisor > retrieval_planner > specialist_direct > academic_specialist
llm: yes (specialist_execution)
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=1, supports=2, citations=0
reason: specialist_supervisor_direct:academic_specialist
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor, retrieval_planner, specialist_direct, academic_specialist
resources: tool:fetch_actor_identity, support:specialist:academic_specialist, support:support_point:academic_specialist

### Pela referencia publica de precos, qual seria a matricula total e o valor mensal para 3 filhos. Traga a resposta de forma concreta.

- Slice: `public`
- Thread: `retrieval_public_pricing_projection` turn `1`
- `langgraph`: status 599, latency 40135.7ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 200, latency 29780.8ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_pricing_projection`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_pricing_projection`
  answer: Hoje a escola publica mais de uma referencia combinada de matricula e mensalidade. Para essa simulacao, os totais por segmento ficam assim:
- Ensino Fundamental II (Manha): matricula 3 x R$ 350,00 = R$ 1.050,00; mensalidade por mes 3 x R$ 1.280,00 = R$ 3.840,00.
- Ensino Medio (Manha): matricula 3 x R$ 350,00 = R$ 1.050,00; mensalidade por mes 3 x R$ 1.450,00 = R$ 4.350,00.
Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.
A base publica tambem menciona: Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_pricing_projection:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > turn_frame:public.enrollment.pricing > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:project_public_pricing, tool:python_functions_native_runtime, support:tool:get_public_school_profile, support:tool:project_public_pricing
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_pricing_projection
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer:preserve_pricing_projection
context_repair_reason: none
- `llamaindex`: status 599, latency 40073.1ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `specialist_supervisor`: status 599, latency 40044.4ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 

### Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.

- Slice: `protected`
- Thread: `retrieval_protected_access_scope` turn `1`
- `langgraph`: status 599, latency 40157.6ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 200, latency 1173.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_access_scope`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `python_functions_native_authenticated_account_scope`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_authenticated_account_scope`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_access_scope:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:finance > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_financial_summary, tool:get_actor_identity_context, tool:python_functions_native_runtime, support:tool:get_financial_summary, support:tool:get_actor_identity_context
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_authenticated_account_scope
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_access_scope
context_repair_reason: none
- `llamaindex`: status 200, latency 1140.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_access_scope`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_local_protected:finance`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_access_scope:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:finance > mode:structured_tool > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_financial_summary, support:tool:get_financial_summary
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: llamaindex_local_protected:finance
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_access_scope
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 305.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:access_scope`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:access_scope`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Neste canal eu consigo consultar academico e financeiro dos alunos vinculados dentro das permissoes da conta.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiroSe quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro da Ana".
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_access_scope:specialist_supervisor
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

### Como o protocolo interno de escopo parcial descreve as restricoes de acesso no Telegram para esse tipo de responsavel. Responda de forma direta.

- Slice: `restricted`
- Thread: `retrieval_restricted_scope_protocol` turn `1`
- `langgraph`: status 200, latency 2074.9ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_restricted_doc_no_match`
  errors: missing_expected_keyword
  answer: Consultei os documentos internos disponiveis, mas nao encontrei um protocolo interno compartilhavel para responsaveis com escopo parcial. No que e publico, a diferenca principal e esta: a base aberta explica apenas orientacoes gerais, enquanto regras operacionais de permissao, restricao e encaminhamento continuam internas. Na pratica, o proximo passo e pedir ao setor responsavel que confirme o procedimento aplicavel ao perfil autorizado.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_scope_protocol:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > langgraph_response_workflow > restricted_retrieval
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: langgraph_response_workflow
resources: tool:get_public_school_profile, support:tool:get_public_school_profile
retrieval: backend=qdrant_hybrid, strategy=structured_tool, sources=1, supports=1, citations=0
reason: langgraph_restricted_doc_no_match
final_polish_reason: none
answer_experience_reason: none
context_repair_reason: none
- `python_functions`: status 200, latency 2077.5ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `deterministic`, candidate_reason `deterministic_candidate_selected:topic_coverage=0.50`, probe_topic `governance_channels`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_restricted_document_no_match`
  errors: missing_expected_keyword
  answer: Consultei os documentos internos disponiveis, mas nao encontrei um protocolo interno compartilhavel para responsaveis com escopo parcial. No que e publico, a diferenca principal e esta: a base aberta explica apenas orientacoes gerais, enquanto regras operacionais de permissao, restricao e encaminhamento continuam internas. Na pratica, o proximo passo e pedir ao setor responsavel que confirme o procedimento aplicavel ao perfil autorizado.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_scope_protocol:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:unknown > mode:hybrid_retrieval > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: eligible (none/none)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:search_documents, tool:python_functions_native_runtime, support:tool:search_documents
retrieval: backend=qdrant_hybrid, strategy=hybrid_retrieval, sources=1, supports=1, citations=0
reason: python_functions_native_restricted_document_no_match
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: none
context_repair_reason: none
- `llamaindex`: status 200, latency 1440.1ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_restricted_doc_no_match`
  errors: missing_expected_keyword
  answer: Consultei os documentos internos disponiveis, mas nao encontrei um protocolo interno compartilhavel para responsaveis com escopo parcial. No que e publico, a diferenca principal e esta: a base aberta explica apenas orientacoes gerais, enquanto regras operacionais de permissao, restricao e encaminhamento continuam internas. Na pratica, o proximo passo e pedir ao setor responsavel que confirme o procedimento aplicavel ao perfil autorizado.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_scope_protocol:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:unknown > mode:hybrid_retrieval > llamaindex:restricted > llamaindex:restricted_doc_fast_path > kernel:llamaindex
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
- `specialist_supervisor`: status 200, latency 800.4ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:restricted_document_no_match`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:restricted_document_no_match`
  errors: missing_expected_keyword
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei um protocolo interno compartilhavel para responsaveis com escopo parcial. No que e publico, a diferenca principal e esta: o material aberto explica apenas o que a escola publica para familias em geral; o detalhamento de permissoes, restricoes e encaminhamento operacional da equipe continua restrito aos canais internos e ao perfil autenticado autorizado. Na pratica, o proximo passo e pedir ao setor responsavel que confirme o procedimento aplicavel ao perfil autorizado.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_restricted_scope_protocol:specialist_supervisor
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

### Quero um quadro unico com as proximas avaliacoes dos meus filhos.

- Slice: `protected`
- Thread: `retrieval_protected_upcoming_assessments` turn `1`
- `langgraph`: status 200, latency 4068.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
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
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_upcoming_assessments:langgraph
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
- `python_functions`: status 200, latency 3844.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
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
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_upcoming_assessments:python_functions
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
reason: python_functions_native_structured:academic
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:preserve_family_aggregate
context_repair_reason: none
- `llamaindex`: status 200, latency 3803.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_local_protected:academic`
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
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_upcoming_assessments:llamaindex
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
- `specialist_supervisor`: status 200, latency 1880.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:upcoming_assessments_aggregate`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:upcoming_assessments_aggregate`
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
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_upcoming_assessments:specialist_supervisor
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

### Quero um panorama de frequencia dos meus filhos e quem esta mais vulneravel por faltas.

- Slice: `protected`
- Thread: `retrieval_protected_attendance_panorama` turn `1`
- `langgraph`: status 200, latency 2284.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama de frequencia das contas vinculadas:
- Lucas Oliveira: 6 falta(s), 7 atraso(s), 19 presenca(s), 370 minuto(s) de ausencia. Ponto mais sensivel: Biologia (1 falta(s), 0 atraso(s)).
- Ana Oliveira: 6 falta(s), 9 atraso(s), 17 presenca(s), 410 minuto(s) de ausencia. Ponto mais sensivel: Portugues (1 falta(s), 1 atraso(s)).
Quem exige maior atencao agora: Ana Oliveira. O ponto mais sensivel aparece em Portugues.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_attendance_panorama:langgraph
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
- `python_functions`: status 200, latency 4939.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `python_functions_native_family_attendance_aggregate`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_family_attendance_aggregate`
  answer: Panorama de frequencia das contas vinculadas:
- Lucas Oliveira: 6 falta(s), 7 atraso(s), 19 presenca(s), 370 minuto(s) de ausencia. Ponto mais sensivel: Biologia (1 falta(s), 0 atraso(s)).
- Ana Oliveira: 6 falta(s), 9 atraso(s), 17 presenca(s), 410 minuto(s) de ausencia. Ponto mais sensivel: Portugues (1 falta(s), 1 atraso(s)).
Quem exige maior atencao agora: Ana Oliveira. O ponto mais sensivel aparece em Portugues.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_attendance_panorama:python_functions
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
- `llamaindex`: status 200, latency 1954.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:preserve_family_aggregate`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_local_protected:academic`
  answer: Panorama de frequencia das contas vinculadas:
- Lucas Oliveira: 6 falta(s), 7 atraso(s), 19 presenca(s), 370 minuto(s) de ausencia. Ponto mais sensivel: Biologia (1 falta(s), 0 atraso(s)).
- Ana Oliveira: 6 falta(s), 9 atraso(s), 17 presenca(s), 410 minuto(s) de ausencia. Ponto mais sensivel: Portugues (1 falta(s), 1 atraso(s)).
Quem exige maior atencao agora: Ana Oliveira. O ponto mais sensivel aparece em Portugues.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_attendance_panorama:llamaindex
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
- `specialist_supervisor`: status 200, latency 609.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:attendance_summary_aggregate`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:attendance_summary_aggregate`
  answer: Panorama de frequencia das contas vinculadas:
- Na frequencia de Lucas Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 7 atraso(s) e 19 presenca(s) neste recorte.
- Na frequencia de Ana Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 9 atraso(s) e 17 presenca(s) neste recorte.
Quem exige maior atencao agora: Ana Oliveira.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_attendance_panorama:specialist_supervisor
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

### Agora foque so no Lucas e diga o que mais preocupa na frequencia dele.

- Slice: `protected`
- Thread: `retrieval_protected_attendance_panorama` turn `1`
- `langgraph`: status 200, latency 24839.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:supplemental_focus_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: No recorte atual, Lucas Oliveira tem 19 presença(s), 6 falta(s) e 7 atraso(s) registrados.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_attendance_panorama:langgraph
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
answer_experience_reason: protected_grounded_answer:supplemental_focus_direct
context_repair_reason: none
- `python_functions`: status 200, latency 10647.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:supplemental_focus_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
  answer: No recorte atual, Lucas Oliveira tem 19 presença(s), 6 falta(s) e 7 atraso(s) registrados.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_attendance_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:structured_tool > turn_frame:protected.academic.attendance > python_functions:native_runtime > kernel:python_functions
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_student_attendance, tool:get_student_attendance_timeline, tool:python_functions_native_runtime, support:tool:get_student_attendance, support:tool:get_student_attendance_timeline
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_structured:academic
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:supplemental_focus_direct
context_repair_reason: none
- `llamaindex`: status 200, latency 12471.4ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `turn_frame_classifier`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:supplemental_focus_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_turn_frame:protected.academic.attendance`
  answer: No recorte atual, Lucas Oliveira tem 19 presença(s), 6 falta(s) e 7 atraso(s) registrados.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_attendance_panorama:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:academic > mode:structured_tool > turn_frame:protected.academic.attendance > kernel:llamaindex
llm: yes (turn_frame_classifier)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_student_attendance, tool:get_student_attendance_timeline, support:tool:get_student_attendance, support:tool:get_student_attendance_timeline
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: llamaindex_turn_frame:protected.academic.attendance
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:supplemental_focus_direct
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 734.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_resolved_intent:attendance_summary`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_resolved_intent:attendance_summary`
  answer: Na frequencia de Lucas Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 7 atraso(s) e 19 presenca(s) neste recorte.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_attendance_panorama:specialist_supervisor
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

### Pensando no caso pratico, estamos fazendo a primeira matricula da familia: como calendario, agenda de avaliacoes e processo de ingresso se organizam no primeiro bimestre?

- Slice: `public`
- Thread: `retrieval_public_family_new_bundle` turn `1`
- `langgraph`: status 200, latency 1194.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:preserve_public_canonical_lane`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares, e fazem mais sentido quando lidos em ordem. Primeiro entram matricula, documentacao inicial, envio digital e canais de atendimento. Depois entram calendario letivo e inicio das aulas, para organizar o comeco do ano. Na sequencia entram agenda de avaliacoes, devolutivas e recuperacoes, para a familia nao perder os marcos pedagogicos. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, a familia usa o manual para entrar corretamente, o calendario para se orientar antes e logo depois do inicio das aulas, e a agenda para acompanhar provas, comunicados e recuperacoes.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_family_new_bundle:langgraph
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
reason: langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment
final_polish_reason: deterministic_answer
answer_experience_reason: structured_grounded_answer:preserve_public_canonical_lane
context_repair_reason: none
- `python_functions`: status 200, latency 8119.8ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `documentary_synthesis`, candidate_reason `python_functions_native_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares, e fazem mais sentido quando lidos em ordem. Primeiro entram matricula, documentacao inicial, envio digital e canais de atendimento. Depois entram calendario letivo e inicio das aulas, para organizar o comeco do ano. Na sequencia entram agenda de avaliacoes, devolutivas e recuperacoes, para a familia nao perder os marcos pedagogicos. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, a familia usa o manual para entrar corretamente, o calendario para se orientar antes e logo depois do inicio das aulas, e a agenda para acompanhar provas, comunicados e recuperacoes.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_family_new_bundle:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:institution > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: yes (public_answer_composer)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_public_school_profile, tool:project_public_pricing, tool:python_functions_native_runtime, support:tool:get_public_school_profile, support:tool:project_public_pricing
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: python_functions_native_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment
final_polish_reason: python_functions_prefers_deterministic
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `llamaindex`: status 200, latency 3824.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `public_answer_composer`, final_polish_applied `True`, final_polish_mode `grounded_public_composition`, final_polish_reason `public_answer_composer`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer:public_direct_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares, e fazem mais sentido quando lidos em ordem. Primeiro entram matricula, documentacao inicial, envio digital e canais de atendimento. Depois entram calendario letivo e inicio das aulas, para organizar o comeco do ano. Na sequencia entram agenda de avaliacoes, devolutivas e recuperacoes, para a familia nao perder os marcos pedagogicos. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, a familia usa o manual para entrar corretamente, o calendario para se orientar antes e logo depois do inicio das aulas, e a agenda para acompanhar provas, comunicados e recuperacoes.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_family_new_bundle:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:institution > mode:structured_tool > llamaindex:public > llamaindex:canonical_public_lane_fast_path:public_bundle.family_new_calendar_assessment_enrollment > kernel:llamaindex
llm: yes (public_answer_composer)
final_polish: grounded_public_composition (applied)
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_public_school_profile, tool:project_public_pricing, support:tool:get_public_school_profile, support:tool:project_public_pricing
retrieval: backend=none, strategy=structured_tool, sources=2, supports=2, citations=0
reason: llamaindex_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment
final_polish_reason: public_answer_composer
answer_experience_reason: structured_grounded_answer:public_direct_answer
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 240.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_preflight:family_new_calendar_enrollment`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares, e fazem mais sentido quando lidos em ordem. Primeiro entram matricula, documentacao inicial, envio digital e canais de atendimento. Depois entram calendario letivo e inicio das aulas, para organizar o comeco do ano. Na sequencia entram agenda de avaliacoes, devolutivas e recuperacoes, para a familia nao perder os marcos pedagogicos. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, a familia usa o manual para entrar corretamente, o calendario para se orientar antes e logo depois do inicio das aulas, e a agenda para acompanhar provas, comunicados e recuperacoes.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_public_family_new_bundle:specialist_supervisor
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

### Quero ver minha alocacao docente atual, com turmas e disciplinas, de forma objetiva.

- Slice: `protected`
- Thread: `retrieval_teacher_schedule_panorama` turn `1`
- `langgraph`: status 200, latency 25791.7ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `early_return`, answer_experience_applied `False`, answer_experience_reason `structured_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `authenticated_public_profile_rescue`
  errors: missing_expected_keyword
  answer: Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_teacher_schedule_panorama:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > authenticated_public_profile_rescue
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_public_school_profile, support:scope:public_school_profile, support:profile_fact:school_name, support:profile_fact:shift_offers, support:tool:get_public_school_profile
retrieval: backend=none, strategy=direct_answer, sources=6, supports=6, citations=0
reason: authenticated_public_profile_rescue
final_polish_reason: early_return
answer_experience_reason: structured_grounded_answer:fallback_to_original
context_repair_reason: none
- `python_functions`: status 200, latency 7444.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `python_functions_native_teacher_schedule`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_teacher_schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. No uso do calendario publico da escola, priorize datas institucionais abertas a familias e equipe, como reunioes, simulados, conselhos e janelas letivas publicadas. Nos canais oficiais da escola, a secretaria continua sendo o contato institucional mais seguro para comunicacao geral; para alinhamentos pedagogicos, o fluxo correto passa por coordenacao e orientacao conforme o assunto.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_teacher_schedule_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, tool:get_teacher_schedule, +7 more
retrieval: backend=none, strategy=structured_tool, sources=6, supports=6, citations=0
reason: python_functions_native_teacher_schedule
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `llamaindex`: status 200, latency 13574.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_local_protected:academic`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. No uso do calendario publico da escola, priorize datas institucionais abertas a familias e equipe, como reunioes, simulados, conselhos e janelas letivas publicadas. Nos canais oficiais da escola, a secretaria continua sendo o contato institucional mais seguro para comunicacao geral; para alinhamentos pedagogicos, o fluxo correto passa por coordenacao e orientacao conforme o assunto.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_teacher_schedule_panorama:llamaindex
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
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 426.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:teacher_schedule`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. No uso do calendario, priorize datas institucionais abertas a familias e equipe, como reunioes, simulados, conselhos e janelas letivas publicadas. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, o fluxo correto passa por coordenacao e orientacao conforme o assunto.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_teacher_schedule_panorama:specialist_supervisor
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

### Sem repetir tudo, isole apenas minhas turmas e disciplinas do ensino medio.

- Slice: `protected`
- Thread: `retrieval_teacher_schedule_panorama` turn `1`
- `langgraph`: status 200, latency 18198.0ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `grounded_answer_experience`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `early_return`, answer_experience_applied `True`, answer_experience_reason `structured_grounded_answer`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `authenticated_public_profile_rescue`
  answer: Para o Ensino Médio, as disciplinas oferecidas incluem: - Língua Portuguesa e produção textual - Matemática - Biologia - Física - Química - História - Geografia - Língua Inglesa - Educação Física - Projeto de vida - Trilhas eletivas e monitorias no contraturno As atividades no turno da manhã ocorrem das 07:15 às 12:50, e as trilhas eletivas, monitorias e laboratórios no contraturno começam a partir das 14h00.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_teacher_schedule_panorama:langgraph
ingress: unknown:none
path: langgraph > classify_request > security_gate > route_request > select_slice > protected_slice > structured_tool_call > authenticated_public_profile_rescue
llm: yes (grounded_answer_experience)
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: langgraph
resources: tool:get_public_school_profile, support:scope:public_school_profile, support:profile_fact:school_name, support:profile_fact:curriculum_basis, support:profile_fact:shift_offers, support:tool:get_public_school_profile
retrieval: backend=none, strategy=direct_answer, sources=6, supports=6, citations=0
reason: authenticated_public_profile_rescue
final_polish_reason: early_return
answer_experience_reason: structured_grounded_answer
context_repair_reason: none
- `python_functions`: status 200, latency 15562.2ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `python_functions_native_teacher_schedule`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_teacher_schedule`
  errors: missing_expected_keyword
  answer: Grade docente de Fernando Azevedo:
- Nenhuma alocacao docente encontrada.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_teacher_schedule_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: eligible (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, tool:get_teacher_schedule, +7 more
retrieval: backend=none, strategy=structured_tool, sources=6, supports=6, citations=0
reason: python_functions_native_teacher_schedule
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `llamaindex`: status 200, latency 7753.9ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `False`, answer_experience_reason `protected_grounded_answer:fallback_to_original`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_local_protected:academic`
  errors: missing_expected_keyword
  answer: Grade docente de Fernando Azevedo:
- Nenhuma alocacao docente encontrada.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_teacher_schedule_panorama:llamaindex
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
answer_experience_reason: protected_grounded_answer:fallback_to_original
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 636.6ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:teacher_schedule`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:teacher_schedule`
  errors: missing_expected_keyword
  answer: Grade docente de Fernando Azevedo:
- Nenhuma alocacao docente encontrada.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_teacher_schedule_panorama:specialist_supervisor
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

### Por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola. Seja objetivo e grounded.

- Slice: `public`
- Thread: `retrieval_public_service_routing` turn `1`
- `langgraph`: status 599, latency 40145.0ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 599, latency 40110.7ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `llamaindex`: status 599, latency 40083.7ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `specialist_supervisor`: status 599, latency 40055.2ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 

### Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.

- Slice: `protected`
- Thread: `retrieval_protected_admin_finance_combo` turn `1`
- `langgraph`: status 599, latency 40142.1ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 599, latency 40111.1ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `llamaindex`: status 599, latency 40085.3ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `specialist_supervisor`: status 200, latency 721.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:admin_finance_overview`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:admin_finance_overview`
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
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_admin_finance_combo:specialist_supervisor
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

### Pelos documentos publicos, como uma familia deve escalar um tema da rotina para direcao e protocolo formal?

- Slice: `public`
- Thread: `retrieval_public_governance_protocol` turn `1`
- `langgraph`: status 599, latency 2719.6ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 599, latency 40120.4ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `llamaindex`: status 599, latency 40094.0ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 
- `specialist_supervisor`: status 599, latency 40067.7ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `exception`
  errors: request_failed
  answer: 

### Faca um resumo academico dos meus dois filhos e destaque qual deles esta mais perto do corte de aprovacao. Responda de forma direta.

- Slice: `protected`
- Thread: `retrieval_protected_family_panorama` turn `1`
- `langgraph`: status 200, latency 2311.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:supplemental_focus_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Biologia 7,9; Educacao Fisica 6,5; Filosofia 7,1; Fisica 5,9
- Ana Oliveira: Biologia 8,0; Educacao Fisica 7,0; Filosofia 7,5; Fisica 6,4 Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_family_panorama:langgraph
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
answer_experience_reason: protected_grounded_answer:supplemental_focus_direct
context_repair_reason: none
- `python_functions`: status 200, latency 2283.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:supplemental_focus_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Biologia 7,9; Educacao Fisica 6,5; Filosofia 7,1; Fisica 5,9
- Ana Oliveira: Biologia 8,0; Educacao Fisica 7,0; Filosofia 7,5; Fisica 6,4 Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_family_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, tool:python_functions_native_runtime, +5 more
retrieval: backend=none, strategy=structured_tool, sources=5, supports=5, citations=0
reason: python_functions_native_structured:academic
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:supplemental_focus_direct
context_repair_reason: none
- `llamaindex`: status 200, latency 2077.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:supplemental_focus_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_local_protected:academic`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Biologia 7,9; Educacao Fisica 6,5; Filosofia 7,1; Fisica 5,9
- Ana Oliveira: Biologia 8,0; Educacao Fisica 7,0; Filosofia 7,5; Fisica 6,4 Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_family_panorama:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:academic > mode:structured_tool > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, support:tool:get_student_academic_summary, +4 more
retrieval: backend=none, strategy=structured_tool, sources=5, supports=5, citations=0
reason: llamaindex_local_protected:academic
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:supplemental_focus_direct
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 470.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_tool_first:academic_summary_aggregate`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4
Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.
[debug]
stack: specialist_supervisor
bundle: specialist_supervisor
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_family_panorama:specialist_supervisor
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

### De forma bem objetiva, quero o mesmo panorama, mas agora isolando a Ana e os pontos academicos que mais preocupam.

- Slice: `protected`
- Thread: `retrieval_protected_family_panorama` turn `1`
- `langgraph`: status 200, latency 2015.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:protected_academic_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Os pontos academicos que mais preocupam em Ana Oliveira hoje sao:
- Fisica: media parcial 6,4
- Educacao Fisica: media parcial 7,0
- Geografia: media parcial 7,0
- Redacao: media parcial 7,1
[debug]
stack: langgraph
bundle: langgraph
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_family_panorama:langgraph
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
- `python_functions`: status 200, latency 1689.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:protected_academic_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `deterministic`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
  answer: Os pontos academicos que mais preocupam em Ana Oliveira hoje sao:
- Fisica: media parcial 6,4
- Educacao Fisica: media parcial 7,0
- Geografia: media parcial 7,0
- Redacao: media parcial 7,1
[debug]
stack: python_functions
bundle: python_functions
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_family_panorama:python_functions
ingress: unknown:none
path: python_functions > python_functions:planner > domain:academic > mode:structured_tool > python_functions:native_runtime > kernel:python_functions
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: python_functions:planner, kernel:python_functions
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, tool:python_functions_native_runtime, +5 more
retrieval: backend=none, strategy=structured_tool, sources=5, supports=5, citations=0
reason: python_functions_native_structured:academic
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:protected_academic_direct
context_repair_reason: none
- `llamaindex`: status 200, latency 1665.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `sensitive_surface`, answer_experience_applied `True`, answer_experience_reason `protected_grounded_answer:protected_academic_direct`, answer_experience_provider `openai`, answer_experience_model `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `llamaindex_local_protected:academic`
  answer: Os pontos academicos que mais preocupam em Ana Oliveira hoje sao:
- Fisica: media parcial 6,4
- Educacao Fisica: media parcial 7,0
- Geografia: media parcial 7,0
- Redacao: media parcial 7,1
[debug]
stack: llamaindex
bundle: llamaindex
corr: none
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_family_panorama:llamaindex
ingress: unknown:none
path: llamaindex > llamaindex:planner > domain:academic > mode:structured_tool > kernel:llamaindex
llm: no
final_polish: skip
answer_experience: applied (openai/ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M)
context_repair: off
retrieval_retry: no
agents: llamaindex:planner, kernel:llamaindex
resources: tool:get_student_academic_summary, tool:get_student_attendance, tool:get_student_grades, tool:get_student_upcoming_assessments, tool:get_student_attendance_timeline, support:tool:get_student_academic_summary, +4 more
retrieval: backend=none, strategy=structured_tool, sources=5, supports=5, citations=0
reason: llamaindex_local_protected:academic
final_polish_reason: sensitive_surface
answer_experience_reason: protected_grounded_answer:protected_academic_direct
context_repair_reason: none
- `specialist_supervisor`: status 200, latency 521.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, answer_experience_applied `False`, answer_experience_reason `none`, answer_experience_provider `none`, answer_experience_model `none`, candidate `specialist_supervisor`, candidate_reason `specialist_supervisor_fast_path:academic_risk`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_fast_path:academic_risk`
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
conversation: debug:four-path:normal:20260415T040512Z:retrieval_protected_family_panorama:specialist_supervisor
ingress: none:none
path: specialist_supervisor > fast_path > academic_risk
llm: no
final_polish: skip
retrieval: backend=none, strategy=structured_tool, sources=1, supports=1, citations=0
reason: specialist_supervisor_fast_path:academic_risk
profile: gemma4e4b_local
provider: openai
agents: specialist_supervisor
resources: support:academic_summary:Ana Oliveira

