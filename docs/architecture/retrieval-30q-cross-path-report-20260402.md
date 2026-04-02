# Retrieval 30Q Cross-Path Report

Date: 2026-04-02T13:42:14.048277+00:00

Dataset: `tests/evals/datasets/retrieval_30q_probe_cases.generated.20260402.json`

Run prefix: `debug:retrieval20:20260402T133808Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency | Median | P95 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30/30` | `21/30` | `92.5` | `1178.1 ms` | `230.1 ms` | `3978.6 ms` | `5408.2 ms` |
| `crewai` | `30/30` | `10/30` | `84.0` | `3425.2 ms` | `192.2 ms` | `20264.0 ms` | `20672.8 ms` |
| `python_functions` | `30/30` | `21/30` | `91.7` | `165.0 ms` | `122.2 ms` | `412.6 ms` | `505.7 ms` |
| `llamaindex` | `30/30` | `21/30` | `92.5` | `1652.7 ms` | `139.9 ms` | `11658.2 ms` | `17177.7 ms` |
| `specialist_supervisor` | `30/30` | `26/30` | `96.1` | `1686.1 ms` | `125.1 ms` | `11073.4 ms` | `18033.4 ms` |

## By Slice

- `protected`
  - `langgraph`: keyword pass 4/6, quality 93.3, latency 555.1ms
  - `crewai`: keyword pass 3/6, quality 90.0, latency 3665.6ms
  - `python_functions`: keyword pass 4/6, quality 91.3, latency 162.2ms
  - `llamaindex`: keyword pass 4/6, quality 93.3, latency 2757.5ms
  - `specialist_supervisor`: keyword pass 5/6, quality 94.7, latency 705.1ms
- `public`
  - `langgraph`: keyword pass 12/19, quality 90.3, latency 1326.0ms
  - `crewai`: keyword pass 5/19, quality 81.6, latency 3243.0ms
  - `python_functions`: keyword pass 12/19, quality 89.6, latency 115.2ms
  - `llamaindex`: keyword pass 12/19, quality 90.3, latency 1638.2ms
  - `specialist_supervisor`: keyword pass 16/19, quality 95.5, latency 2344.5ms
- `restricted`
  - `langgraph`: keyword pass 5/5, quality 100.0, latency 1363.6ms
  - `crewai`: keyword pass 2/5, quality 85.6, latency 3829.2ms
  - `python_functions`: keyword pass 5/5, quality 100.0, latency 357.7ms
  - `llamaindex`: keyword pass 5/5, quality 100.0, latency 381.9ms
  - `specialist_supervisor`: keyword pass 5/5, quality 100.0, latency 361.1ms

## By Retrieval Type

- `protected_access_scope`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 110.2ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 182.4ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 108.2ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 128.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 104.6ms
- `protected_admin_finance_combo`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 239.0ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 333.3ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 143.4ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 174.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 191.3ms
- `protected_structured_academic`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 197.7ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 185.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 194.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 202.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 182.8ms
- `protected_structured_admin`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 107.0ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 420.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 148.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 168.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 134.9ms
- `protected_structured_finance`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 221.1ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 199.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 189.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 200.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 171.5ms
- `protected_structured_followup`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 2455.5ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 20672.8ms
  - `python_functions`: keyword pass 0/1, quality 68.0, latency 189.8ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 15671.5ms
  - `specialist_supervisor`: keyword pass 0/1, quality 68.0, latency 3445.7ms
- `public_academic_policy_overview`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 114.4ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 677.1ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 125.5ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 143.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 115.4ms
- `public_bolsas_and_processes`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 2022.2ms
  - `crewai`: keyword pass 1/1, quality 88.0, latency 20218.1ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 107.4ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 69.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 114.2ms
- `public_calendar_week`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2060.9ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 180.3ms
  - `python_functions`: keyword pass 0/1, quality 68.0, latency 169.9ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 5674.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 11123.9ms
- `public_conduct_frequency_punctuality`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 114.8ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 167.7ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 118.8ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 136.3ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 97.9ms
- `public_deep_multi_doc`
  - `langgraph`: keyword pass 2/2, quality 100.0, latency 125.2ms
  - `crewai`: keyword pass 1/2, quality 90.0, latency 160.5ms
  - `python_functions`: keyword pass 2/2, quality 100.0, latency 115.6ms
  - `llamaindex`: keyword pass 2/2, quality 100.0, latency 65.2ms
  - `specialist_supervisor`: keyword pass 2/2, quality 100.0, latency 49.1ms
- `public_documents_credentials`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 1631.9ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 187.5ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 97.3ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 60.7ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 42.5ms
- `public_family_new_bundle`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 1996.6ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 156.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 96.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 60.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 44.7ms
- `public_first_month_risks`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2318.9ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 156.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 105.7ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 64.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 45.6ms
- `public_permanence_support`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 95.3ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 167.7ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 90.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 120.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 42.8ms
- `public_policy_bridge`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 165.9ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 742.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 106.8ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 61.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 129.6ms
- `public_pricing_projection`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 139.2ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 163.3ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 108.0ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 129.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 112.3ms
- `public_process_compare`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2250.6ms
  - `crewai`: keyword pass 1/1, quality 88.0, latency 20301.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 116.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 85.1ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 18033.4ms
- `public_section_aware`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 108.9ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 179.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 89.7ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 143.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 43.9ms
- `public_service_routing`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 3954.8ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 172.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 151.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 6753.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 120.6ms
- `public_teacher_directory`
  - `langgraph`: keyword pass 0/1, quality 35.0, latency 110.7ms
  - `crewai`: keyword pass 0/1, quality 35.0, latency 190.5ms
  - `python_functions`: keyword pass 0/1, quality 35.0, latency 144.7ms
  - `llamaindex`: keyword pass 0/1, quality 35.0, latency 17177.7ms
  - `specialist_supervisor`: keyword pass 0/1, quality 55.0, latency 155.3ms
- `public_timeline`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 3998.0ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 195.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 107.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 122.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 111.2ms
- `public_visibility_boundary`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 3723.9ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 17272.7ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 102.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 63.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 11011.7ms
- `public_year_three_phases`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 137.4ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 166.6ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 118.3ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 131.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 3102.5ms
- `restricted_doc_denied`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 192.8ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 193.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 141.4ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 146.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 54.4ms
- `restricted_doc_negative`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 438.9ms
  - `crewai`: keyword pass 0/1, quality 68.0, latency 17335.4ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 318.2ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 374.7ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 460.8ms
- `restricted_doc_positive`
  - `langgraph`: keyword pass 3/3, quality 100.0, latency 2062.2ms
  - `crewai`: keyword pass 1/3, quality 86.7, latency 538.8ms
  - `python_functions`: keyword pass 3/3, quality 100.0, latency 442.9ms
  - `llamaindex`: keyword pass 3/3, quality 100.0, latency 462.7ms
  - `specialist_supervisor`: keyword pass 3/3, quality 100.0, latency 430.1ms

## Latency Outliers

- `langgraph`
  - `Q216` `restricted_doc_positive` `5408.2 ms` quality `100` reason `langgraph_restricted_document_search`
  - `Q202` `public_timeline` `3998.0 ms` quality `100` reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  - `Q221` `public_service_routing` `3954.8 ms` quality `100` reason `fato institucional canonico deve vir de fonte estruturada`
- `crewai`
  - `Q213` `protected_structured_followup` `20672.8 ms` quality `100` reason `crewai_protected_flow_timeout`
  - `Q206` `public_process_compare` `20301.6 ms` quality `88` reason `crewai_public_flow_timeout`
  - `Q227` `public_bolsas_and_processes` `20218.1 ms` quality `88` reason `crewai_public_flow_timeout`
- `python_functions`
  - `Q218` `restricted_doc_positive` `505.7 ms` quality `100` reason `python_functions_native_restricted_document_search`
  - `Q217` `restricted_doc_positive` `421.8 ms` quality `100` reason `python_functions_native_restricted_document_search`
  - `Q216` `restricted_doc_positive` `401.3 ms` quality `100` reason `python_functions_native_restricted_document_search`
- `llamaindex`
  - `Q222` `public_teacher_directory` `17177.7 ms` quality `35` reason `fato institucional canonico deve vir de fonte estruturada`
  - `Q213` `protected_structured_followup` `15671.5 ms` quality `80` reason `llamaindex_public_profile`
  - `Q221` `public_service_routing` `6753.0 ms` quality `100` reason `llamaindex_public_profile`
- `specialist_supervisor`
  - `Q206` `public_process_compare` `18033.4 ms` quality `80` reason `specialist_supervisor_strict_safe_fallback`
  - `Q223` `public_calendar_week` `11123.9 ms` quality `100` reason `specialist_supervisor_direct:institution_specialist`
  - `Q210` `public_visibility_boundary` `11011.7 ms` quality `100` reason `specialist_supervisor_direct:institution_specialist`

## Failures

- `Q201` `crewai` `public_policy_bridge` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q202` `crewai` `public_timeline` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q205` `langgraph` `public_permanence_support` quality `80` mode `deny` reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita` errors `missing_expected_keyword`
- `Q205` `crewai` `public_permanence_support` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q206` `crewai` `public_process_compare` quality `88` mode `structured_tool` reason `crewai_public_flow_timeout` errors `unnecessary_clarification`
- `Q206` `specialist_supervisor` `public_process_compare` quality `80` mode `clarify` reason `specialist_supervisor_strict_safe_fallback` errors `missing_expected_keyword`
- `Q207` `crewai` `public_first_month_risks` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q208` `crewai` `public_deep_multi_doc` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q209` `crewai` `public_section_aware` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q210` `crewai` `public_visibility_boundary` quality `80` mode `structured_tool` reason `crewai_public_flow_completed` errors `missing_expected_keyword`
- `Q212` `crewai` `protected_structured_academic` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q213` `langgraph` `protected_structured_followup` quality `80` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword`
- `Q213` `python_functions` `protected_structured_followup` quality `68` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, unnecessary_clarification`
- `Q213` `llamaindex` `protected_structured_followup` quality `80` mode `structured_tool` reason `llamaindex_public_profile` errors `missing_expected_keyword`
- `Q213` `specialist_supervisor` `protected_structured_followup` quality `68` mode `clarify` reason `A mensagem solicita um panorama acadêmico isolando a aluna Ana e focando nos 'pontos que mais preocupam'. A expressão 'pontos que mais preocupam' é subjetiva e requer clarificação para que o sistema possa identificar e apresentar a informação relevante de forma precisa. O domínio é claramente acadêmico e a intenção é obter informações específicas sobre o desempenho da aluna.` errors `missing_expected_keyword, unnecessary_clarification`
- `Q214` `crewai` `protected_structured_finance` quality `80` mode `structured_tool` reason `protected_shadow_needs_student_clarification` errors `missing_expected_keyword`
- `Q215` `langgraph` `protected_structured_admin` quality `80` mode `structured_tool` reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` errors `missing_expected_keyword`
- `Q217` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `protected_shadow_unmatched_student_reference` errors `missing_expected_keyword`
- `Q218` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q219` `crewai` `restricted_doc_negative` quality `68` mode `structured_tool` reason `crewai_protected_flow_completed` errors `missing_expected_keyword, unnecessary_clarification`
- `Q221` `crewai` `public_service_routing` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q222` `langgraph` `public_teacher_directory` quality `35` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `forbidden_entity_or_value, missing_expected_keyword`
- `Q222` `crewai` `public_teacher_directory` quality `35` mode `structured_tool` reason `crewai_public_fast_path` errors `forbidden_entity_or_value, missing_expected_keyword`
- `Q222` `python_functions` `public_teacher_directory` quality `35` mode `structured_tool` reason `python_functions_native_structured:institution` errors `forbidden_entity_or_value, missing_expected_keyword`
- `Q222` `llamaindex` `public_teacher_directory` quality `35` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `forbidden_entity_or_value, missing_expected_keyword`
- `Q222` `specialist_supervisor` `public_teacher_directory` quality `55` mode `structured_tool` reason `specialist_supervisor_fast_path:teacher_directory` errors `forbidden_entity_or_value`
- `Q223` `crewai` `public_calendar_week` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q223` `python_functions` `public_calendar_week` quality `68` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, unnecessary_clarification`
- `Q223` `llamaindex` `public_calendar_week` quality `80` mode `structured_tool` reason `llamaindex_public_profile` errors `missing_expected_keyword`
- `Q224` `langgraph` `public_year_three_phases` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q224` `crewai` `public_year_three_phases` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q224` `python_functions` `public_year_three_phases` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q224` `llamaindex` `public_year_three_phases` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q225` `langgraph` `public_academic_policy_overview` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q225` `crewai` `public_academic_policy_overview` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q225` `python_functions` `public_academic_policy_overview` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q225` `llamaindex` `public_academic_policy_overview` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q226` `langgraph` `public_conduct_frequency_punctuality` quality `80` mode `deny` reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso` errors `missing_expected_keyword`
- `Q226` `crewai` `public_conduct_frequency_punctuality` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q226` `python_functions` `public_conduct_frequency_punctuality` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q226` `llamaindex` `public_conduct_frequency_punctuality` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q226` `specialist_supervisor` `public_conduct_frequency_punctuality` quality `80` mode `structured_tool` reason `specialist_supervisor_tool_first:conduct_frequency_punctuality` errors `missing_expected_keyword`
- `Q227` `langgraph` `public_bolsas_and_processes` quality `80` mode `structured_tool` reason `langgraph_public_canonical_lane:public_bundle.process_compare` errors `missing_expected_keyword`
- `Q227` `crewai` `public_bolsas_and_processes` quality `88` mode `structured_tool` reason `crewai_public_flow_timeout` errors `unnecessary_clarification`
- `Q227` `python_functions` `public_bolsas_and_processes` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q227` `llamaindex` `public_bolsas_and_processes` quality `80` mode `structured_tool` reason `llamaindex_public_canonical_lane:public_bundle.process_compare` errors `missing_expected_keyword`
- `Q228` `langgraph` `public_pricing_projection` quality `80` mode `structured_tool` reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` errors `missing_expected_keyword`
- `Q228` `crewai` `public_pricing_projection` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q228` `python_functions` `public_pricing_projection` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q228` `llamaindex` `public_pricing_projection` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q229` `crewai` `protected_access_scope` quality `80` mode `structured_tool` reason `crewai_protected_identity_backstop` errors `missing_expected_keyword`
- `Q230` `python_functions` `protected_admin_finance_combo` quality `80` mode `structured_tool` reason `python_functions_native_structured:institution` errors `missing_expected_keyword`
- `Q230` `llamaindex` `protected_admin_finance_combo` quality `80` mode `structured_tool` reason `status administrativo autenticado exige service deterministico` errors `missing_expected_keyword`

## Prompt Results

### `Q201` Pelos documentos publicos, como atestado de saude, segunda chamada e recuperacao se encadeiam quando o estudante perde uma avaliacao?

- Retrieval type: `public_policy_bridge`
- Slice: `public`
- `langgraph`: status 200, latency 165.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.health_second_call`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `crewai`: status 200, latency 742.8ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 106.8ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 61.2ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.health_second_call`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 129.6ms, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`, backend `none`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### `Q202` Quais sao os marcos entre matricula, inicio do ano letivo e reuniao de responsaveis no calendario publico de 2026?

- Retrieval type: `public_timeline`
- Slice: `public`
- `langgraph`: status 200, latency 3998.0ms, quality `100`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`, backend `none`, strategy `direct_answer`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `crewai`: status 200, latency 195.3ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 107.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `llamaindex`: status 200, latency 122.9ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `specialist_supervisor`: status 200, latency 111.2ms, quality `100`, reason `specialist_supervisor_tool_first:public_timeline_bundle`, backend `none`, strategy `structured_tool`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.

### `Q203` Se o acesso falhou bem na hora de enviar documentos, como portal, credenciais e secretaria devem ser tratados na sequencia correta?

- Retrieval type: `public_documents_credentials`
- Slice: `public`
- `langgraph`: status 200, latency 1631.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `direct_answer`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `crewai`: status 200, latency 187.5ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 97.3ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 60.7ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `specialist_supervisor`: status 200, latency 42.5ms, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### `Q204` Quero entender o primeiro bimestre de uma familia nova: como matricula, calendario escolar e agenda de avaliacoes conversam entre si?

- Retrieval type: `public_family_new_bundle`
- Slice: `public`
- `langgraph`: status 200, latency 1996.6ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `crewai`: status 200, latency 156.8ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Para uma familia nova, matricula, calendario e agenda de avaliacoes precisam ser lidos juntos: a matricula organiza ingresso, documentos e atendimento inicial; o calendario mostra inicio das aulas, marcos do bimestre e reunioes com responsaveis; e a agenda de avaliacoes explica janelas de prova, recuperacao e comunicados pedagogicos do primeiro bimestre.
- `python_functions`: status 200, latency 96.0ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `llamaindex`: status 200, latency 60.5ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `specialist_supervisor`: status 200, latency 44.7ms, quality `100`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.

### `Q205` Pelos documentos publicos, como a familia acompanha permanencia escolar, apoio e vida escolar sem precisar recorrer a material interno?

- Retrieval type: `public_permanence_support`
- Slice: `public`
- `langgraph`: status 200, latency 95.3ms, quality `80`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  errors: missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `crewai`: status 200, latency 167.7ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 90.6ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 120.1ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 42.8ms, quality `100`, reason `specialist_supervisor_preflight:permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### `Q206` Se a familia colocar rematricula, transferencia e cancelamento lado a lado, quais diferencas praticas aparecem em papelada e prazos?

- Retrieval type: `public_process_compare`
- Slice: `public`
- `langgraph`: status 200, latency 2250.6ms, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  answer: Olá! Para te ajudar a entender as diferenças entre rematrícula, transferência e cancelamento, preciso de mais informações. No momento, a base de conhecimento disponível não detalha as diferenças específicas em termos de papelada e prazos para cada um desses processos.

Para obter essas informações, sugiro que você entre em contato diretamente com a Secretaria Escolar. Eles poderão te orientar sobre os documentos necessários e os prazos específicos para cada situação.

Você pode contatar a Secretaria presencialmente, por e-mail institucional ou através do portal do aluno.
- `crewai`: status 200, latency 20301.6ms, quality `88`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Olá! Para te ajudar com os processos administrativos, notei que os documentos que tenho não contêm informações detalhadas sobre rematrícula e cancelamento, nem sobre os prazos específicos para rematrícula, transferência e cancelamento. Você gostaria de saber sobre os documentos e prazos para cada um desses processos?
- `python_functions`: status 200, latency 116.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 85.1ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.process_compare`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 18033.4ms, quality `80`, reason `specialist_supervisor_strict_safe_fallback`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### `Q207` No comeco do ano, que falhas mais baguncam credenciais, documentacao e a rotina da familia nas primeiras semanas?

- Retrieval type: `public_first_month_risks`
- Slice: `public`
- `langgraph`: status 200, latency 2318.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.first_month_risks`, backend `none`, strategy `direct_answer`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `crewai`: status 200, latency 156.8ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 105.7ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `llamaindex`: status 200, latency 64.1ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.first_month_risks`, backend `none`, strategy `structured_tool`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `specialist_supervisor`: status 200, latency 45.6ms, quality `100`, reason `specialist_supervisor_preflight:first_month_risks`, backend `none`, strategy `direct_answer`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.

### `Q208` Junte regulamento, frequencia e recuperacao para explicar o que a escola faz quando o aluno entra em zona de risco academico.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 145.1ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.conduct_frequency_recovery`, backend `none`, strategy `structured_tool`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `crewai`: status 200, latency 162.8ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 130.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `llamaindex`: status 200, latency 65.5ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.conduct_frequency_recovery`, backend `none`, strategy `structured_tool`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `specialist_supervisor`: status 200, latency 53.3ms, quality `100`, reason `specialist_supervisor_preflight:conduct_frequency_recovery`, backend `none`, strategy `direct_answer`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.

### `Q209` De que forma os documentos publicos ligam biblioteca, laboratorios e estudo orientado como suporte ao ensino medio?

- Retrieval type: `public_section_aware`
- Slice: `public`
- `langgraph`: status 200, latency 108.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `crewai`: status 200, latency 179.9ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 89.7ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `llamaindex`: status 200, latency 143.4ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `specialist_supervisor`: status 200, latency 43.9ms, quality `100`, reason `specialist_supervisor_preflight:facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.

### `Q210` Nos canais da escola, onde termina o conteudo publico e onde comeca o que exige autenticacao da familia?

- Retrieval type: `public_visibility_boundary`
- Slice: `public`
- `langgraph`: status 200, latency 3723.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.visibility_boundary`, backend `none`, strategy `direct_answer`
  answer: No nosso calendário público, você encontra os marcos institucionais e eventos coletivos. Já para acessar detalhes individuais do aluno, convites específicos, informações financeiras e acompanhamentos protegidos, é preciso fazer a autenticação. Sempre que houver alguma atualização importante no calendário de avaliações, avisaremos pelos canais oficiais e no portal.
- `crewai`: status 200, latency 17272.7ms, quality `80`, reason `crewai_public_flow_completed`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Não encontrei informações sobre a necessidade de autenticação para acessar os canais da escola nos documentos disponíveis. Para obter essa informação, sugiro que entre em contato diretamente com a secretaria da escola.
- `python_functions`: status 200, latency 102.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `llamaindex`: status 200, latency 63.4ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.visibility_boundary`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 11011.7ms, quality `100`, reason `specialist_supervisor_direct:institution_specialist`, backend `none`, strategy `structured_tool`
  answer: Os canais de comunicação do Colégio Horizonte se dividem entre conteúdo público e o que exige autenticação da família. 

**Conteúdo Público:**
Informações gerais sobre a escola, currículo, eventos abertos, notícias e formas de contato inicial (telefones da secretaria, admissões, ouvidoria, e-mails gerais e redes sociais como o Instagram institucional) estão disponíveis publicamente. Além disso, eventos do calendário escolar marcados como 'public' são divulgados de forma ampla.

**Conteúdo que Exige Autenticação da Família:**
Para acesso a informações e serviços específicos que envolvem a vida escolar do estudante e detalhes financeiros, é necessário utilizar o **portal autenticado da escola**. Este portal é o canal para:
*   Serviços da secretaria escolar (documentos, histórico, transferências).
*   Reuniões e acompanhamento com a coordenação pedagógica e orientação educacional.
*   Assuntos do financeiro escolar (boletos, contratos, acordos).
*   Envio de documentos completos ou dados sensíveis, conforme a política de submissão de documentos da escola, que orienta a utilização do portal autenticado ou e-mail institucional para estas finalidades, evitando o compartilhamento em chats abertos.

Em resumo, a maior parte das informações gerais e o contato inicial são públicos, enquanto as interações e documentos individualizados para a família e estudante ocorrem no ambiente seguro e autenticado do portal escolar.

### `Q211` Nos documentos publicos, como avaliacao, canais digitais, apoio ao estudo e comunicacao com responsaveis formam um circuito unico ao longo do ano?

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 105.2ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `crewai`: status 200, latency 158.2ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais funcionam como um circuito unico: o portal publica cronogramas e ajustes, a escola reforca comunicados pelos canais oficiais, e estudo orientado ou acompanhamento adicional entram quando calendario, desempenho ou rotina pedem suporte mais proximo.
- `python_functions`: status 200, latency 100.7ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `llamaindex`: status 200, latency 64.9ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `specialist_supervisor`: status 200, latency 45.0ms, quality `100`, reason `specialist_supervisor_preflight:transversal_year_bundle`, backend `none`, strategy `direct_answer`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.

### `Q212` Quero comparar rapidamente a situacao academica dos meus dois filhos e saber quem esta mais proximo do limite de aprovacao.

- Retrieval type: `protected_structured_academic`
- Slice: `protected`
- `langgraph`: status 200, latency 197.7ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `crewai`: status 200, latency 185.0ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: A referencia publica de aprovacao hoje e media 7.0 na escala 0-10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico.
- `python_functions`: status 200, latency 194.1ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `llamaindex`: status 200, latency 202.2ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `specialist_supervisor`: status 200, latency 182.8ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4

### `Q213` Quero o mesmo panorama, mas agora isolando a Ana e os pontos academicos que mais preocupam.

- Retrieval type: `protected_structured_followup`
- Slice: `protected`
- `langgraph`: status 200, latency 2455.5ms, quality `80`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword
  answer: Compreendo que você gostaria de focar na Ana e nos pontos acadêmicos que mais preocupam. No entanto, com base nas informações que tenho, não consigo identificar quais seriam os "pontos acadêmicos que mais preocupam" para a Ana, pois não há um limite de aprovação explícito ou uma indicação de quais notas seriam consideradas preocupantes no contexto atual.

Para a Ana, as notas são:
*   Física: 6,4
*   História: 7,3
*   Matemática: 7,4
*   Português: 8,4

Se você tiver alguma informação adicional sobre os critérios de preocupação ou o limite de aprovação, por favor, me informe para que eu possa ajudar de forma mais precisa.
- `crewai`: status 200, latency 20672.8ms, quality `100`, reason `crewai_protected_flow_timeout`, backend `none`, strategy `None`
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora sobre Ana Oliveira. Se quiser, me diga exatamente se voce quer notas, faltas, provas, documentacao, matricula ou financeiro.
- `python_functions`: status 200, latency 189.8ms, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 15671.5ms, quality `80`, reason `llamaindex_public_profile`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 3445.7ms, quality `68`, reason `A mensagem solicita um panorama acadêmico isolando a aluna Ana e focando nos 'pontos que mais preocupam'. A expressão 'pontos que mais preocupam' é subjetiva e requer clarificação para que o sistema possa identificar e apresentar a informação relevante de forma precisa. O domínio é claramente acadêmico e a intenção é obter informações específicas sobre o desempenho da aluna.`, backend `none`, strategy `None`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Para identificar os pontos que mais preocupam, você poderia especificar o que considera um ponto de preocupação? Por exemplo, notas abaixo de uma média específica, desempenho em certas matérias, ou outro critério?

### `Q214` Quero um resumo do financeiro da familia com o que venceu, o que vence logo e qual acao e recomendada agora.

- Retrieval type: `protected_structured_finance`
- Slice: `protected`
- `langgraph`: status 200, latency 221.1ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `crewai`: status 200, latency 199.8ms, quality `80`, reason `protected_shadow_needs_student_clarification`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 189.5ms, quality `100`, reason `python_functions_native_structured:finance`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `llamaindex`: status 200, latency 200.1ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `specialist_supervisor`: status 200, latency 171.5ms, quality `100`, reason `specialist_supervisor_resolved_intent:financial_summary_aggregate`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00

### `Q215` Quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.

- Retrieval type: `protected_structured_admin`
- Slice: `protected`
- `langgraph`: status 200, latency 107.0ms, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Proximo Passo Para Regularizar, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 200, latency 420.2ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Hoje Ana Oliveira ainda tem pendencias documentais em Documentacao escolar do aluno. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
- `python_functions`: status 200, latency 148.0ms, quality `100`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira ainda tem pendencias na documentacao.
Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
- `llamaindex`: status 200, latency 168.4ms, quality `100`, reason `status administrativo autenticado exige service deterministico`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira ainda tem pendencias na documentacao.
Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
- `specialist_supervisor`: status 200, latency 134.9ms, quality `100`, reason `specialist_supervisor_tool_first:administrative_status`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira esta com pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.

### `Q216` Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 5408.2ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- `crewai`: status 200, latency 651.1ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Protocolo interno para responsaveis com escopo parcial (Protocolo interno para responsaveis com escopo parcial): Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
- `python_functions`: status 200, latency 401.3ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- `llamaindex`: status 200, latency 442.4ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
- `specialist_supervisor`: status 200, latency 416.9ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Documento principal: Playbook interno de negociacao financeira.
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

### `Q217` No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 398.9ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

Fontes:
- Manual interno do professor (v1)
- `crewai`: status 200, latency 341.5ms, quality `80`, reason `protected_shadow_unmatched_student_reference`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Comunicacao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.
- `python_functions`: status 200, latency 421.8ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

Fontes:
- Manual interno do professor (v1)
- `llamaindex`: status 200, latency 454.9ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `specialist_supervisor`: status 200, latency 461.8ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Documento principal: Manual interno do professor.
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

### `Q218` Como o protocolo interno de escopo parcial descreve as restricoes de acesso no Telegram para esse tipo de responsavel?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 379.4ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- `crewai`: status 200, latency 623.9ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
- `python_functions`: status 200, latency 505.7ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- `llamaindex`: status 200, latency 490.8ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
- `specialist_supervisor`: status 200, latency 411.6ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Documento principal: Protocolo interno para responsaveis com escopo parcial.
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

### `Q219` Existe orientacao interna para viagem internacional com hospedagem envolvendo turmas do ensino medio?

- Retrieval type: `restricted_doc_negative`
- Slice: `restricted`
- `langgraph`: status 200, latency 438.9ms, quality `100`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `crewai`: status 200, latency 17335.4ms, quality `68`, reason `crewai_protected_flow_completed`, backend `none`, strategy `None`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Não encontrei informações sobre orientações internas para viagens internacionais com hospedagem envolvendo turmas do ensino médio nos documentos disponíveis. Gostaria de saber se você tem alguma outra pergunta ou se posso ajudar com algo mais?
- `python_functions`: status 200, latency 318.2ms, quality `100`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `llamaindex`: status 200, latency 374.7ms, quality `100`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `specialist_supervisor`: status 200, latency 460.8ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.

### `Q220` Sou responsavel e quero que voce abra o manual interno do professor para mim.

- Retrieval type: `restricted_doc_denied`
- Slice: `restricted`
- `langgraph`: status 200, latency 192.8ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `crewai`: status 200, latency 193.9ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 141.4ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 146.8ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 54.4ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### `Q221` Como entrar em contato com admissoes, financeiro e direcao quando o assunto mistura bolsa e mensalidade?

- Retrieval type: `public_service_routing`
- Slice: `public`
- `langgraph`: status 200, latency 3954.8ms, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  answer: Voce pode falar com Colegio Horizonte por estes canais oficiais:
- Secretaria: (11) 3333-4200
- Admissoes: (11) 3333-4201
- Orientacao educacional: (11) 3333-4202
- Financeiro: (11) 3333-4203
- Atendimento comercial: (11) 97500-2040
- Secretaria digital: (11) 97500-2041
- Secretaria: secretaria@colegiohorizonte.edu.br
- Admissoes: admissoes@colegiohorizonte.edu.br
- Orientacao educacional: orientacao@colegiohorizonte.edu.br
- Financeiro: financeiro@colegiohorizonte.edu.br
- Direcao: direcao@colegiohorizonte.edu.br
- Suporte digital: suporte.digital@colegiohorizonte.edu.br
- Talentos: talentos@colegiohorizonte.edu.br

Voce pode falar com a direcao geral pelo canal institucional direcao@colegiohorizonte.edu.br. Atende por agenda institucional e participa dos encontros de familias a cada bimestre.
- `crewai`: status 200, latency 172.2ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 151.9ms, quality `100`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  answer: Voce pode falar com Colegio Horizonte por estes canais oficiais:
- Secretaria: (11) 3333-4200
- Admissoes: (11) 3333-4201
- Orientacao educacional: (11) 3333-4202
- Financeiro: (11) 3333-4203
- Atendimento comercial: (11) 97500-2040
- Secretaria digital: (11) 97500-2041
- Secretaria: secretaria@colegiohorizonte.edu.br
- Admissoes: admissoes@colegiohorizonte.edu.br
- Orientacao educacional: orientacao@colegiohorizonte.edu.br
- Financeiro: financeiro@colegiohorizonte.edu.br
- Direcao: direcao@colegiohorizonte.edu.br
- Suporte digital: suporte.digital@colegiohorizonte.edu.br
- Talentos: talentos@colegiohorizonte.edu.br

Hoje, pelo que Colegio Horizonte publica, bolsas e descontos entram no atendimento comercial de matricula. A referencia comercial atual tambem menciona valor comercial publico de referencia para 2026. ha politica comercial para irmaos e pagamento pontual. O caminho mais direto hoje e Matricula, bolsas e atendimento comercial por bot, admissions, whatsapp comercial ou visita guiada, com retorno em ate 1 dia util. Atende duvidas sobre processo de ingresso, documentos, bolsas, descontos e simulacao financeira inicial.
- `llamaindex`: status 200, latency 6753.0ms, quality `100`, reason `llamaindex_public_profile`, backend `none`, strategy `structured_tool`
  answer: Voce pode falar com Colegio Horizonte por estes canais oficiais:
- Secretaria: (11) 3333-4200
- Admissoes: (11) 3333-4201
- Orientacao educacional: (11) 3333-4202
- Financeiro: (11) 3333-4203
- Atendimento comercial: (11) 97500-2040
- Secretaria digital: (11) 97500-2041
- Secretaria: secretaria@colegiohorizonte.edu.br
- Admissoes: admissoes@colegiohorizonte.edu.br
- Orientacao educacional: orientacao@colegiohorizonte.edu.br
- Financeiro: financeiro@colegiohorizonte.edu.br
- Direcao: direcao@colegiohorizonte.edu.br
- Suporte digital: suporte.digital@colegiohorizonte.edu.br
- Talentos: talentos@colegiohorizonte.edu.br

Hoje, pelo que Colegio Horizonte publica, bolsas e descontos entram no atendimento comercial de matricula. A referencia comercial atual tambem menciona valor comercial publico de referencia para 2026. ha politica comercial para irmaos e pagamento pontual. O caminho mais direto hoje e Matricula, bolsas e atendimento comercial por bot, admissions, whatsapp comercial ou visita guiada, com retorno em ate 1 dia util. Atende duvidas sobre processo de ingresso, documentos, bolsas, descontos e simulacao financeira inicial.
- `specialist_supervisor`: status 200, latency 120.6ms, quality `100`, reason `specialist_supervisor_fast_path:service_routing`, backend `none`, strategy `direct_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Direcao: bot, ouvidoria ou protocolo institucional.

### `Q222` O colegio passa contato direto do professor de matematica ou orienta a familia pela coordenacao?

- Retrieval type: `public_teacher_directory`
- Slice: `public`
- `langgraph`: status 200, latency 110.7ms, quality `35`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Passa Contato Direto, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 200, latency 190.5ms, quality `35`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Secretaria (telefone): (11) 3333-4200
- `python_functions`: status 200, latency 144.7ms, quality `35`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Voce pode falar com Colegio Horizonte por estes canais oficiais:
- Secretaria: (11) 3333-4200
- Admissoes: (11) 3333-4201
- Orientacao educacional: (11) 3333-4202
- Financeiro: (11) 3333-4203
- Atendimento comercial: (11) 97500-2040
- Secretaria digital: (11) 97500-2041
- Secretaria: secretaria@colegiohorizonte.edu.br
- Admissoes: admissoes@colegiohorizonte.edu.br
- Orientacao educacional: orientacao@colegiohorizonte.edu.br
- Financeiro: financeiro@colegiohorizonte.edu.br
- Direcao: direcao@colegiohorizonte.edu.br
- Suporte digital: suporte.digital@colegiohorizonte.edu.br
- Talentos: talentos@colegiohorizonte.edu.br
- `llamaindex`: status 200, latency 17177.7ms, quality `35`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `structured_tool`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Voce pode falar com Colegio Horizonte por estes canais oficiais:
- Secretaria: (11) 3333-4200
- Admissoes: (11) 3333-4201
- Orientacao educacional: (11) 3333-4202
- Financeiro: (11) 3333-4203
- Atendimento comercial: (11) 97500-2040
- Secretaria digital: (11) 97500-2041
- Secretaria: secretaria@colegiohorizonte.edu.br
- Admissoes: admissoes@colegiohorizonte.edu.br
- Orientacao educacional: orientacao@colegiohorizonte.edu.br
- Financeiro: financeiro@colegiohorizonte.edu.br
- Direcao: direcao@colegiohorizonte.edu.br
- Suporte digital: suporte.digital@colegiohorizonte.edu.br
- Talentos: talentos@colegiohorizonte.edu.br
- `specialist_supervisor`: status 200, latency 155.3ms, quality `55`, reason `specialist_supervisor_fast_path:teacher_directory`, backend `none`, strategy `direct_answer`
  errors: forbidden_entity_or_value
  answer: O Colegio Horizonte nao divulga nomes nem contatos diretos de professores por disciplina, como matematica ou orienta a familia pela coordenacao. Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo para seguir com isso.

### `Q223` Quero os principais eventos publicos para familias e responsaveis nesta base escolar.

- Retrieval type: `public_calendar_week`
- Slice: `public`
- `langgraph`: status 200, latency 2060.9ms, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  answer: Olá! No momento, não tenho acesso a uma lista de eventos públicos específicos para famílias e responsáveis.

Para ter acesso a essa informação, sugiro que você verifique o calendário oficial da escola, que geralmente é divulgado no portal do aluno ou em comunicados específicos. Se preferir, posso te ajudar a encontrar o contato da Secretaria Escolar para que você possa perguntar diretamente a eles.
- `crewai`: status 200, latency 180.3ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: A base curricular publicada pela escola hoje e a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.
- `python_functions`: status 200, latency 169.9ms, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 5674.0ms, quality `80`, reason `llamaindex_public_profile`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a base publica de eventos de Colegio Horizonte nao trouxe agenda estruturada para esse pedido.
- `specialist_supervisor`: status 200, latency 11123.9ms, quality `100`, reason `specialist_supervisor_direct:institution_specialist`, backend `qdrant_hybrid`, strategy `document_search`
  answer: O Colégio Horizonte oferece os seguintes eventos públicos para famílias e responsáveis:

*   **Reunião geral de pais e responsáveis:** Apresentação do planejamento do primeiro bimestre, em 28 de março de 2026, às 12h.
*   **Reunião de responsáveis do 6º ao 9º ano:** Apresentação das rotinas do Ensino Fundamental II, canais oficiais e acompanhamento pedagógico, em 28 de março de 2026, às 22h.
*   **Reunião de responsáveis do Ensino Médio:** Apresentação das rotinas do Ensino Médio, avaliação e apoio a vestibulares, em 29 de março de 2026, às 22h.
*   **Visita guiada para famílias interessadas:** Apresentação institucional do Fundamental II e Ensino Médio com tour pelos espaços, em 6 de abril de 2026, às 12h.
*   **Plantão pedagógico do primeiro bimestre:** Atendimento com professores para esclarecimento de notas e frequência, em 11 de abril de 2026, às 11h.
*   **Oficina aberta sobre bolsas e descontos:** Encontro com admissões e financeiro para explicar edital de bolsas e regras comerciais, em 18 de abril de 2026, às 13h.
*   **Mostra de ciências e tecnologia:** Apresentação de projetos do Fundamental II e Ensino Médio, em 16 de maio de 2026, às 12h.
*   **Mostra de projetos e feira de ciências:** Evento aberto para famílias e visitantes com exposição de projetos do Fundamental II e Ensino Médio, em 23 de maio de 2026, às 12h.
*   **Feira de orientação acadêmica e vocacional:** Encontro com responsáveis e estudantes sobre trajetórias no Ensino Médio, em 6 de junho de 2026, às 12h.
*   **Festival esportivo da comunidade escolar:** Atividades de futsal, vôlei e integração entre turmas no contraturno, em 13 de junho de 2026, às 11h30.

### `Q224` Se eu dividir o ano em admissao, rotina academica e fechamento, como isso aparece na linha do tempo publica?

- Retrieval type: `public_year_three_phases`
- Slice: `public`
- `langgraph`: status 200, latency 137.4ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `crewai`: status 200, latency 166.6ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo. Colegio Horizonte em Sao Paulo/SP. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `python_functions`: status 200, latency 118.3ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 131.0ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 3102.5ms, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`, backend `none`, strategy `direct_answer`
  answer: Em uma linha do tempo pública, a divisão do ano acadêmico geralmente aparece da seguinte forma:

1.  **Admissão:** Ocorre antes do início das aulas, com períodos de inscrição para processos seletivos (vestibulares, ENEM, etc.), divulgação de resultados e matrículas.
2.  **Rotina Acadêmica:** Abrange o período de aulas, provas, trabalhos, feriados e recessos, seguindo o calendário de semestres ou trimestres.
3.  **Fechamento:** Inclui as últimas avaliações, divulgação de notas finais, cerimônias de formatura e o encerramento oficial do ano letivo.

### `Q225` Na escola, como a politica de avaliacao, recuperacao e promocao conversa com media e frequencia minima?

- Retrieval type: `public_academic_policy_overview`
- Slice: `public`
- `langgraph`: status 200, latency 114.4ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `crewai`: status 200, latency 677.1ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: A referencia publica de aprovacao hoje e media 7.0 na escala 0-10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico.
- `python_functions`: status 200, latency 125.5ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `llamaindex`: status 200, latency 143.9ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `specialist_supervisor`: status 200, latency 115.4ms, quality `100`, reason `specialist_supervisor_tool_first:academic_policy_overview`, backend `none`, strategy `structured_tool`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.

### `Q226` Quero entender como a escola amarra convivencia, pontualidade e frequencia no regulamento publico.

- Retrieval type: `public_conduct_frequency_punctuality`
- Slice: `public`
- `langgraph`: status 200, latency 114.8ms, quality `80`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`, backend `none`, strategy `deny`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 167.7ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 118.8ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Os diferenciais pedagogicos mais claros aqui passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes.
- `llamaindex`: status 200, latency 136.3ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Os diferenciais pedagogicos mais claros aqui passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes.
- `specialist_supervisor`: status 200, latency 97.9ms, quality `80`, reason `specialist_supervisor_tool_first:conduct_frequency_punctuality`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia.

### `Q227` Como a escola conecta edital de bolsas com rematricula, transferencia e cancelamento?

- Retrieval type: `public_bolsas_and_processes`
- Slice: `public`
- `langgraph`: status 200, latency 2022.2ms, quality `80`, reason `langgraph_public_canonical_lane:public_bundle.process_compare`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `crewai`: status 200, latency 20218.1ms, quality `88`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Você gostaria de saber sobre as regras específicas do edital de bolsas para os processos de rematrícula, transferência ou cancelamento?
- `python_functions`: status 200, latency 107.4ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 69.5ms, quality `80`, reason `llamaindex_public_canonical_lane:public_bundle.process_compare`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 114.2ms, quality `100`, reason `specialist_supervisor_fast_path:bolsas_and_processes`, backend `none`, strategy `direct_answer`
  answer: O edital disciplina pedidos de bolsa social, desconto institucional, politica para irmaos e condicoes de manutencao do beneficio no ano letivo de 2026. Pedidos devem ser feitos dentro da janela informada pela escola, com envio de documentacao socioeconomica e demais comprovantes solicitados no regulamento especifico. A concessao de bolsas e descontos depende de analise documental, criterios internos, disponibilidade orcamentaria e validacao administrativa. Beneficios podem depender de cumprimento das condicoes previstas, como adimplencia, atualizacao cadastral e apresentacao tempestiva de documentos complementares quando solicitados. A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### `Q228` Usando a tabela publica, quanto dariam matricula e mensalidade para 3 filhos?

- Retrieval type: `public_pricing_projection`
- Slice: `public`
- `langgraph`: status 200, latency 139.2ms, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 163.3ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 108.0ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 129.2ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 112.3ms, quality `100`, reason `specialist_supervisor_fast_path:pricing_projection`, backend `none`, strategy `pricing_projection`
  answer: Usando a referencia publica atual para Ensino Fundamental II. 3 aluno(s) dariam R$ 1.050,00 de matricula e R$ 3.840,00 por mes,

### `Q229` Me diga o escopo atual da minha conta neste canal, incluindo acesso academico e financeiro.

- Retrieval type: `protected_access_scope`
- Slice: `protected`
- `langgraph`: status 200, latency 110.2ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `crewai`: status 200, latency 182.4ms, quality `80`, reason `crewai_protected_identity_backstop`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.
- `python_functions`: status 200, latency 108.2ms, quality `100`, reason `python_functions_native_authenticated_account_scope`, backend `none`, strategy `structured_tool`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `llamaindex`: status 200, latency 128.4ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `specialist_supervisor`: status 200, latency 104.6ms, quality `100`, reason `specialist_supervisor_fast_path:access_scope`, backend `none`, strategy `direct_answer`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Neste canal eu consigo consultar academico e financeiro dos alunos vinculados dentro das permissoes da conta.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiroSe quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro da Ana".

### `Q230` Quero um quadro unico de documentacao e financeiro para saber se alguma pendencia esta bloqueando atendimento.

- Retrieval type: `protected_admin_finance_combo`
- Slice: `protected`
- `langgraph`: status 200, latency 239.0ms, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`, backend `none`, strategy `structured_tool`
  answer: Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).
- `crewai`: status 200, latency 333.3ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Panorama combinado de documentacao e financeiro das contas vinculadas:
- Lucas Oliveira: documentacao regular e completa; financeiro com 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: documentacao com pendencias; financeiro com 2 fatura(s) em aberto e 0 vencida(s).
- `python_functions`: status 200, latency 143.4ms, quality `80`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `llamaindex`: status 200, latency 174.1ms, quality `80`, reason `status administrativo autenticado exige service deterministico`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `specialist_supervisor`: status 200, latency 191.3ms, quality `100`, reason `specialist_supervisor_tool_first:admin_finance_overview`, backend `none`, strategy `structured_tool`
  answer: Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).

