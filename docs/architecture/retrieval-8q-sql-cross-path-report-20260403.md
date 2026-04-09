# Four-Path Chatbot Comparison Report

Date: 2026-04-03T22:32:24.287342+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_8q_sql_probe_cases.generated.20260403.json`

LLM forced: `False`

Run prefix: `debug:four-path:normal:20260403T223206Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency | Final polish |
| --- | --- | --- | --- | --- | --- |
| `langgraph` | `8/8` | `8/8` | `100.0` | `567.8 ms` | `0/8` |
| `python_functions` | `8/8` | `8/8` | `100.0` | `517.4 ms` | `0/8` |
| `llamaindex` | `8/8` | `8/8` | `100.0` | `585.8 ms` | `0/8` |
| `specialist_supervisor` | `8/8` | `8/8` | `100.0` | `480.9 ms` | `0/8` |

## By Slice

- `protected`
  - `langgraph`: ok 8/8, keyword pass 8/8, quality 100.0, latency 567.8ms, final polish 0/8
  - `python_functions`: ok 8/8, keyword pass 8/8, quality 100.0, latency 517.4ms, final polish 0/8
  - `llamaindex`: ok 8/8, keyword pass 8/8, quality 100.0, latency 585.8ms, final polish 0/8
  - `specialist_supervisor`: ok 8/8, keyword pass 8/8, quality 100.0, latency 480.9ms, final polish 0/8

## Error Types

- `langgraph`: nenhum
- `python_functions`: nenhum
- `llamaindex`: nenhum
- `specialist_supervisor`: nenhum

## Prompt Results

### Sem sair do escopo do projeto, quero um panorama academico dos meus filhos com quem esta mais perto da media minima.

- Slice: `protected`
- Thread: `retrieval_protected_family_panorama` turn `1`
- `langgraph`: status 200, latency 550.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `python_functions`: status 200, latency 498.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `protected_disabled`, candidate `deterministic`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `llamaindex`: status 200, latency 618.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `specialist_supervisor`: status 200, latency 557.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4

### Pensando no caso pratico, mantendo o contexto dos meus filhos, filtre para a Ana e mostre as materias em que ela esta mais vulneravel.

- Slice: `protected`
- Thread: `retrieval_protected_family_panorama` turn `1`
- `langgraph`: status 200, latency 597.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Ana Oliveira:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
- `python_functions`: status 200, latency 630.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `protected_disabled`, candidate `deterministic`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
  answer: Notas de Ana Oliveira:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
- `llamaindex`: status 200, latency 677.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Ana Oliveira:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
- `specialist_supervisor`: status 200, latency 390.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_memory:academic_risk_followup`
  answer: Os pontos de maior risco academico de Ana Oliveira hoje sao:
- Historia: media parcial 7,3
- Fisica: media parcial 6,4
- Matematica: media parcial 7,4
Esses componentes merecem acompanhamento primeiro no proximo ciclo de estudo.

### Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro.

- Slice: `protected`
- Thread: `retrieval_protected_admin_finance_combo` turn `1`
- `langgraph`: status 200, latency 899.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `status administrativo autenticado exige service deterministico`
  answer: Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `python_functions`: status 200, latency 822.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `protected_disabled`, candidate `deterministic`, candidate_reason `python_functions_native_structured:institution`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:institution`
  answer: Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `llamaindex`: status 200, latency 1001.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `status administrativo autenticado exige service deterministico`
  answer: Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `specialist_supervisor`: status 200, latency 962.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:admin_finance_overview`
  answer: Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).

### Quero ver as proximas avaliacoes dos meus filhos em um resumo unico.

- Slice: `protected`
- Thread: `retrieval_protected_upcoming_assessments` turn `1`
- `langgraph`: status 200, latency 794.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Proximas avaliacoes das contas vinculadas:
- Lucas Oliveira (1o Ano A)
  - Biologia - Avaliacao B1: 2026-04-10
  - Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
  - Historia - Avaliacao B1: 2026-04-10
  - Ingles - Avaliacao B1: 2026-04-10
- Ana Oliveira (1o Ano A)
  - Biologia - Avaliacao B1: 2026-04-10
  - Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
  - Historia - Avaliacao B1: 2026-04-10
  - Ingles - Avaliacao B1: 2026-04-10
- `python_functions`: status 200, latency 573.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `protected_disabled`, candidate `deterministic`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
  answer: Proximas avaliacoes das contas vinculadas:
- Lucas Oliveira (1o Ano A)
  - Biologia - Avaliacao B1: 2026-04-10
  - Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
  - Historia - Avaliacao B1: 2026-04-10
  - Ingles - Avaliacao B1: 2026-04-10
- Ana Oliveira (1o Ano A)
  - Biologia - Avaliacao B1: 2026-04-10
  - Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
  - Historia - Avaliacao B1: 2026-04-10
  - Ingles - Avaliacao B1: 2026-04-10
- `llamaindex`: status 200, latency 623.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Proximas avaliacoes das contas vinculadas:
- Lucas Oliveira (1o Ano A)
  - Biologia - Avaliacao B1: 2026-04-10
  - Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
  - Historia - Avaliacao B1: 2026-04-10
  - Ingles - Avaliacao B1: 2026-04-10
- Ana Oliveira (1o Ano A)
  - Biologia - Avaliacao B1: 2026-04-10
  - Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
  - Historia - Avaliacao B1: 2026-04-10
  - Ingles - Avaliacao B1: 2026-04-10
- `specialist_supervisor`: status 200, latency 676.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:upcoming_assessments_aggregate`
  answer: Proximas avaliacoes das contas vinculadas:
- Lucas Oliveira (1o Ano A)
  - Biologia - Avaliacao B1: 2026-04-10
  - Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
  - Historia - Avaliacao B1: 2026-04-10
  - Ingles - Avaliacao B1: 2026-04-10
- Ana Oliveira (1o Ano A)
  - Biologia - Avaliacao B1: 2026-04-10
  - Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
  - Historia - Avaliacao B1: 2026-04-10
  - Ingles - Avaliacao B1: 2026-04-10

### Mantendo o contexto, quero apenas a Ana com as proximas provas e entregas.

- Slice: `protected`
- Thread: `retrieval_protected_upcoming_assessments` turn `1`
- `langgraph`: status 200, latency 553.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Proximas avaliacoes de Ana Oliveira:
- Turma: 1o Ano A
- Biologia - Avaliacao B1: 2026-04-10
- Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
- Historia - Avaliacao B1: 2026-04-10
- Ingles - Avaliacao B1: 2026-04-10
- Matematica - Avaliacao 2026-B1 - MAT: 2026-04-10
- Matematica - Avaliacao B1: 2026-04-10
- `python_functions`: status 200, latency 523.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `protected_disabled`, candidate `deterministic`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
  answer: Proximas avaliacoes de Ana Oliveira:
- Turma: 1o Ano A
- Biologia - Avaliacao B1: 2026-04-10
- Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
- Historia - Avaliacao B1: 2026-04-10
- Ingles - Avaliacao B1: 2026-04-10
- Matematica - Avaliacao 2026-B1 - MAT: 2026-04-10
- Matematica - Avaliacao B1: 2026-04-10
- `llamaindex`: status 200, latency 470.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Proximas avaliacoes de Ana Oliveira:
- Turma: 1o Ano A
- Biologia - Avaliacao B1: 2026-04-10
- Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
- Historia - Avaliacao B1: 2026-04-10
- Ingles - Avaliacao B1: 2026-04-10
- Matematica - Avaliacao 2026-B1 - MAT: 2026-04-10
- Matematica - Avaliacao B1: 2026-04-10
- `specialist_supervisor`: status 200, latency 358.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:upcoming_assessments`
  answer: Proximas avaliacoes de Ana Oliveira:
- Turma: 1o Ano A
- Biologia - Avaliacao B1: 2026-04-10
- Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
- Historia - Avaliacao B1: 2026-04-10
- Ingles - Avaliacao B1: 2026-04-10
- Matematica - Avaliacao 2026-B1 - MAT: 2026-04-10
- Matematica - Avaliacao B1: 2026-04-10

### Traga as disciplinas ou componentes em que a Ana aparece com as menores medias agora.

- Slice: `protected`
- Thread: `retrieval_protected_grade_components` turn `1`
- `langgraph`: status 200, latency 307.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Os componentes em que Ana Oliveira aparece com as menores medias agora sao:
- Fisica: media parcial 6,4
- Educacao Fisica: media parcial 7,0
- Geografia: media parcial 7,0
- Redacao: media parcial 7,1
- `python_functions`: status 200, latency 321.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `protected_disabled`, candidate `deterministic`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
  answer: Os componentes em que Ana Oliveira aparece com as menores medias agora sao:
- Fisica: media parcial 6,4
- Educacao Fisica: media parcial 7,0
- Geografia: media parcial 7,0
- Redacao: media parcial 7,1
- `llamaindex`: status 200, latency 390.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Os componentes em que Ana Oliveira aparece com as menores medias agora sao:
- Fisica: media parcial 6,4
- Educacao Fisica: media parcial 7,0
- Geografia: media parcial 7,0
- Redacao: media parcial 7,1
- `specialist_supervisor`: status 200, latency 341.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_tool_first:academic_summary`
  answer: Notas de Ana Oliveira:
- Historia: media parcial 7,3
- Fisica: media parcial 6,4
- Matematica: media parcial 7,4
- Portugues: media parcial 8,4

### No financeiro da familia, separe para mim o que esta vencido, o que esta parcialmente quitado e o que vem a seguir.

- Slice: `protected`
- Thread: `retrieval_protected_finance_detail` turn `1`
- `langgraph`: status 200, latency 449.6ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `python_functions`: status 200, latency 389.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `protected_disabled`, candidate `deterministic`, candidate_reason `python_functions_native_structured:finance`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `llamaindex`: status 200, latency 370.8ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `specialist_supervisor`: status 200, latency 286.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_resolved_intent:financial_summary_aggregate`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00

### Recorte so o Lucas e diga onde a frequencia dele esta mais sensivel por faltas recentes.

- Slice: `protected`
- Thread: `retrieval_protected_attendance_detail` turn `1`
- `langgraph`: status 200, latency 390.2ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Na frequencia de Lucas Oliveira, o ponto mais sensivel hoje aparece em Biologia: 1 falta(s), 0 atraso(s) e 3 presenca(s) neste recorte.
- `python_functions`: status 200, latency 380.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `protected_disabled`, candidate `deterministic`, candidate_reason `python_functions_native_structured:academic`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `python_functions_native_structured:academic`
  answer: Na frequencia de Lucas Oliveira, o ponto mais sensivel hoje aparece em Biologia: 1 falta(s), 0 atraso(s) e 3 presenca(s) neste recorte.
- `llamaindex`: status 200, latency 533.5ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `dados estruturados devem passar por service deterministico`
  answer: Na frequencia de Lucas Oliveira, o ponto mais sensivel hoje aparece em Biologia: 1 falta(s), 0 atraso(s) e 3 presenca(s) neste recorte.
- `specialist_supervisor`: status 200, latency 273.1ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, candidate `none`, candidate_reason `none`, probe_topic `none`, cache_hit `False`, cache_kind `none`, reason `specialist_supervisor_resolved_intent:attendance_summary`
  answer: Na frequencia de Lucas Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 7 atraso(s) e 19 presenca(s) neste recorte.

