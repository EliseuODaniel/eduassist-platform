# Retrieval 25Q Cross-Path Report

Date: 2026-04-02T17:09:21.903007+00:00

Dataset: `tests/evals/datasets/retrieval_25q_probe_cases.generated.20260402.json`

Run prefix: `debug:retrieval20:20260402T170818Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency | Median | P95 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `25/25` | `24/25` | `99.2` | `2022.1 ms` | `1759.4 ms` | `5401.2 ms` | `6628.2 ms` |
| `python_functions` | `25/25` | `25/25` | `100.0` | `162.7 ms` | `148.2 ms` | `226.4 ms` | `238.9 ms` |
| `llamaindex` | `25/25` | `25/25` | `100.0` | `142.3 ms` | `96.5 ms` | `236.2 ms` | `242.8 ms` |
| `specialist_supervisor` | `25/25` | `24/25` | `98.7` | `123.5 ms` | `80.4 ms` | `205.3 ms` | `343.4 ms` |

## By Slice

- `protected`
  - `langgraph`: keyword pass 4/4, quality 100.0, latency 243.6ms
  - `python_functions`: keyword pass 4/4, quality 100.0, latency 200.9ms
  - `llamaindex`: keyword pass 4/4, quality 100.0, latency 220.4ms
  - `specialist_supervisor`: keyword pass 3/4, quality 92.0, latency 186.8ms
- `public`
  - `langgraph`: keyword pass 15/16, quality 98.8, latency 2913.2ms
  - `python_functions`: keyword pass 16/16, quality 100.0, latency 137.1ms
  - `llamaindex`: keyword pass 16/16, quality 100.0, latency 100.2ms
  - `specialist_supervisor`: keyword pass 16/16, quality 100.0, latency 99.1ms
- `restricted`
  - `langgraph`: keyword pass 5/5, quality 100.0, latency 593.4ms
  - `python_functions`: keyword pass 5/5, quality 100.0, latency 214.2ms
  - `llamaindex`: keyword pass 5/5, quality 100.0, latency 214.9ms
  - `specialist_supervisor`: keyword pass 5/5, quality 100.0, latency 151.2ms

## By Retrieval Type

- `protected_structured_academic`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 354.4ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 204.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 218.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 202.7ms
- `protected_structured_admin`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 196.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 199.7ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 216.2ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 166.9ms
- `protected_structured_finance`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 210.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 196.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 222.6ms
  - `specialist_supervisor`: keyword pass 1/1, quality 88.0, latency 193.2ms
- `protected_structured_followup`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 212.5ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 202.8ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 223.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 184.2ms
- `public_academic_policy_overview`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4536.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 125.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 86.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 78.2ms
- `public_calendar_week`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 5468.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 120.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 82.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 49.0ms
- `public_deep_multi_doc`
  - `langgraph`: keyword pass 2/2, quality 100.0, latency 1377.6ms
  - `python_functions`: keyword pass 2/2, quality 100.0, latency 137.1ms
  - `llamaindex`: keyword pass 2/2, quality 100.0, latency 80.3ms
  - `specialist_supervisor`: keyword pass 2/2, quality 100.0, latency 97.3ms
- `public_documents_credentials`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 1759.4ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 119.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 73.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 78.3ms
- `public_family_new_bundle`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 3146.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 148.2ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 92.6ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 80.4ms
- `public_first_month_risks`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2374.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 133.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 68.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 48.7ms
- `public_permanence_support`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2869.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 119.8ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 76.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 75.8ms
- `public_policy_bridge`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 362.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 167.3ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 84.6ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 343.4ms
- `public_process_compare`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 137.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 147.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 145.7ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 55.7ms
- `public_section_aware`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4720.5ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 152.7ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 77.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 78.9ms
- `public_service_routing`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 121.4ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 143.8ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 238.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 124.2ms
- `public_teacher_directory`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 5132.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 122.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 69.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 74.6ms
- `public_timeline`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2215.7ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 129.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 172.7ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 70.3ms
- `public_visibility_boundary`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4381.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 149.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 96.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 77.9ms
- `public_year_three_phases`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 6628.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 139.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 77.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 155.5ms
- `restricted_doc_denied`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 191.5ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 157.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 164.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 59.2ms
- `restricted_doc_negative`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 272.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 224.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 226.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 205.9ms
- `restricted_doc_positive`
  - `langgraph`: keyword pass 3/3, quality 100.0, latency 834.4ms
  - `python_functions`: keyword pass 3/3, quality 100.0, latency 229.9ms
  - `llamaindex`: keyword pass 3/3, quality 100.0, latency 227.9ms
  - `specialist_supervisor`: keyword pass 3/3, quality 100.0, latency 163.6ms

## Latency Outliers

- `langgraph`
  - `Q224` `public_year_three_phases` `6628.2 ms` quality `80` reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  - `Q223` `public_calendar_week` `5468.3 ms` quality `100` reason `langgraph_public_canonical_lane:public_bundle.calendar_week`
  - `Q222` `public_teacher_directory` `5132.8 ms` quality `100` reason `langgraph_public_canonical_lane:public_bundle.teacher_directory_boundary`
- `python_functions`
  - `Q217` `restricted_doc_positive` `238.9 ms` quality `100` reason `python_functions_native_restricted_document_no_match`
  - `Q216` `restricted_doc_positive` `227.0 ms` quality `100` reason `python_functions_native_restricted_document_no_match`
  - `Q219` `restricted_doc_negative` `224.0 ms` quality `100` reason `python_functions_native_restricted_document_no_match`
- `llamaindex`
  - `Q216` `restricted_doc_positive` `242.8 ms` quality `100` reason `llamaindex_restricted_doc_no_match`
  - `Q221` `public_service_routing` `238.5 ms` quality `100` reason `contextual_public_direct_answer`
  - `Q217` `restricted_doc_positive` `227.0 ms` quality `100` reason `llamaindex_restricted_doc_no_match`
- `specialist_supervisor`
  - `Q201` `public_policy_bridge` `343.4 ms` quality `100` reason `specialist_supervisor_fast_path:health_second_call`
  - `Q219` `restricted_doc_negative` `205.9 ms` quality `100` reason `specialist_supervisor_tool_first:restricted_document_no_match`
  - `Q212` `protected_structured_academic` `202.7 ms` quality `100` reason `specialist_supervisor_tool_first:academic_summary_aggregate_fallback`

## Failures

- `Q214` `specialist_supervisor` `protected_structured_finance` quality `88` mode `clarify` reason `specialist_supervisor_resolved_intent:finance_student_clarify` errors `unnecessary_clarification`
- `Q215` `specialist_supervisor` `protected_structured_admin` quality `80` mode `structured_tool` reason `specialist_supervisor_tool_first:academic_summary_scoped_fallback` errors `missing_expected_keyword`
- `Q224` `langgraph` `public_year_three_phases` quality `80` mode `structured_tool` reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao` errors `missing_expected_keyword`

## Prompt Results

### `Q201` Se uma prova e perdida por motivo de saude, como atestado, segunda chamada e recuperacao aparecem conectados nos documentos publicos. Responda de forma direta.

- Retrieval type: `public_policy_bridge`
- Slice: `public`
- `langgraph`: status 200, latency 362.2ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.health_second_call`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `python_functions`: status 200, latency 167.3ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 84.6ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.health_second_call`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 343.4ms, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`, backend `none`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### `Q202` Sem sair do escopo do projeto, no cronograma publico de 2026, em que ordem aparecem abertura da matricula, comeco das aulas e primeiro encontro com responsaveis?

- Retrieval type: `public_timeline`
- Slice: `public`
- `langgraph`: status 200, latency 2215.7ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.timeline_lifecycle`, backend `none`, strategy `direct_answer`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `python_functions`: status 200, latency 129.9ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `llamaindex`: status 200, latency 172.7ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.timeline_lifecycle`, backend `none`, strategy `structured_tool`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `specialist_supervisor`: status 200, latency 70.3ms, quality `100`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.

### `Q203` Sem sair do escopo do projeto, para resolver acesso e envio documental sem erro, como portal, credenciais e secretaria entram na ordem certa?

- Retrieval type: `public_documents_credentials`
- Slice: `public`
- `langgraph`: status 200, latency 1759.4ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `direct_answer`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `python_functions`: status 200, latency 119.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 73.1ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `specialist_supervisor`: status 200, latency 78.3ms, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### `Q204` Para uma casa que esta entrando no Colegio Horizonte agora, como matricula, inicio das aulas e avaliacoes se relacionam no comeco do ano?

- Retrieval type: `public_family_new_bundle`
- Slice: `public`
- `langgraph`: status 200, latency 3146.3ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `python_functions`: status 200, latency 148.2ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `llamaindex`: status 200, latency 92.6ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `specialist_supervisor`: status 200, latency 80.4ms, quality `100`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.

### `Q205` Quais apoios publicos evitam que a familia se perca ao acompanhar permanencia e vida escolar do estudante. Responda de forma direta.

- Retrieval type: `public_permanence_support`
- Slice: `public`
- `langgraph`: status 200, latency 2869.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `python_functions`: status 200, latency 119.8ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 76.5ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 75.8ms, quality `100`, reason `specialist_supervisor_preflight:permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### `Q206` Quando comparo rematricula, transferencia de entrada e cancelamento, o que muda de verdade em prazo, protocolo e documentos. Traga a resposta de forma concreta.

- Retrieval type: `public_process_compare`
- Slice: `public`
- `langgraph`: status 200, latency 137.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.process_compare`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `python_functions`: status 200, latency 147.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 145.7ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 55.7ms, quality `100`, reason `specialist_supervisor_preflight:process_compare`, backend `none`, strategy `direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### `Q207` No arranque do ano letivo, que descuidos mais costumam explodir entre credenciais, papelada e rotina da casa?

- Retrieval type: `public_first_month_risks`
- Slice: `public`
- `langgraph`: status 200, latency 2374.8ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.first_month_risks`, backend `none`, strategy `direct_answer`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `python_functions`: status 200, latency 133.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `llamaindex`: status 200, latency 68.5ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.first_month_risks`, backend `none`, strategy `structured_tool`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `specialist_supervisor`: status 200, latency 48.7ms, quality `100`, reason `specialist_supervisor_preflight:first_month_risks`, backend `none`, strategy `direct_answer`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.

### `Q208` Relacione convivencia, frequencia e recuperacao usando os documentos publicos mais relevantes da escola.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 161.2ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.academic_policy_overview`, backend `none`, strategy `structured_tool`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `python_functions`: status 200, latency 138.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `llamaindex`: status 200, latency 89.4ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`, backend `none`, strategy `structured_tool`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `specialist_supervisor`: status 200, latency 73.7ms, quality `100`, reason `specialist_supervisor_preflight:academic_policy_overview`, backend `none`, strategy `direct_answer`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.

### `Q209` Pensando no caso pratico, na base publica do ensino medio, como biblioteca, laboratorios e apoio ao estudo aparecem amarrados na rotina academica?

- Retrieval type: `public_section_aware`
- Slice: `public`
- `langgraph`: status 200, latency 4720.5ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Que ótima pergunta! Aqui no Colégio Horizonte, a Biblioteca Aurora e os laboratórios são parte integrante da rotina acadêmica, não apenas espaços isolados. Eles são pensados para enriquecer o aprendizado e apoiar os projetos dos nossos alunos.

A Biblioteca Aurora oferece desde consulta e empréstimo até apoio a projetos de pesquisa e mesas de estudo em grupo, que podem ser agendadas pelo portal. Já os laboratórios de ciências e informática são usados para aulas práticas, pesquisas e desenvolvimento de trabalhos, sempre com agendamento.

Além disso, temos o estudo orientado, que ajuda na organização das tarefas, prazos e na formação de bons hábitos de estudo. No Ensino Médio, isso se traduz em monitorias, projetos de pesquisa, cultura digital e atividades práticas no contraturno, como oficinas de leitura e projetos maker.
- `python_functions`: status 200, latency 152.7ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `llamaindex`: status 200, latency 77.4ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `specialist_supervisor`: status 200, latency 78.9ms, quality `100`, reason `specialist_supervisor_preflight:facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.

### `Q210` Pensando no caso pratico, nos canais digitais da escola, o que ainda e publico e o que passa a depender da autenticacao da familia?

- Retrieval type: `public_visibility_boundary`
- Slice: `public`
- `langgraph`: status 200, latency 4381.2ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.visibility_boundary`, backend `none`, strategy `direct_answer`
  answer: Olá! No nosso calendário público, você sempre encontrará os marcos institucionais gerais e os eventos coletivos da escola. Já os detalhes individuais de cada aluno, convites específicos, protocolos, informações financeiras e acompanhamentos protegidos dependem de autenticação ou de um contexto interno. Fique tranquila, sempre que houver alguma mudança importante no calendário de avaliações, nós atualizamos o portal e reforçamos a comunicação pelos nossos canais oficiais.
- `python_functions`: status 200, latency 149.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `llamaindex`: status 200, latency 96.5ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.visibility_boundary`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 77.9ms, quality `100`, reason `specialist_supervisor_preflight:visibility_boundary`, backend `none`, strategy `direct_answer`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.

### `Q211` Como os materiais publicos mostram a relacao entre agenda avaliativa, comunicacao com responsaveis, estudo orientado e meios digitais durante o ano?

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 2594.0ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `direct_answer`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `python_functions`: status 200, latency 135.7ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `llamaindex`: status 200, latency 71.3ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `specialist_supervisor`: status 200, latency 121.0ms, quality `100`, reason `specialist_supervisor_preflight:transversal_year_bundle`, backend `none`, strategy `direct_answer`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.

### `Q212` Quero comparar rapidamente a situacao academica dos meus dois filhos e saber quem esta mais proximo do limite de aprovacao. Seja objetivo e grounded.

- Retrieval type: `protected_structured_academic`
- Slice: `protected`
- `langgraph`: status 200, latency 354.4ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `python_functions`: status 200, latency 204.1ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `llamaindex`: status 200, latency 218.9ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `specialist_supervisor`: status 200, latency 202.7ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate_fallback`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina.

### `Q213` Mantendo o contexto dos meus filhos, filtre para a Ana e mostre as materias em que ela esta mais vulneravel.

- Retrieval type: `protected_structured_followup`
- Slice: `protected`
- `langgraph`: status 200, latency 212.5ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.
- `python_functions`: status 200, latency 202.8ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.
- `llamaindex`: status 200, latency 223.8ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.
- `specialist_supervisor`: status 200, latency 184.2ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_scoped_fallback`, backend `none`, strategy `structured_tool`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.

### `Q214` Pensando no caso pratico, como esta o financeiro da familia hoje, incluindo vencimentos e proximos passos?

- Retrieval type: `protected_structured_finance`
- Slice: `protected`
- `langgraph`: status 200, latency 210.6ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro da familia hoje: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora os vencimentos e proximos passos detalhados, mas o recorte continua sendo o financeiro das contas vinculadas.
- `python_functions`: status 200, latency 196.9ms, quality `100`, reason `python_functions_native_structured:finance`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro da familia hoje: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora os vencimentos e proximos passos detalhados, mas o recorte continua sendo o financeiro das contas vinculadas.
- `llamaindex`: status 200, latency 222.6ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro da familia hoje: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora os vencimentos e proximos passos detalhados, mas o recorte continua sendo o financeiro das contas vinculadas.
- `specialist_supervisor`: status 200, latency 193.2ms, quality `88`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### `Q215` Hoje, o que ainda falta na parte administrativa da Ana e como a familia deve agir em seguida?

- Retrieval type: `protected_structured_admin`
- Slice: `protected`
- `langgraph`: status 200, latency 196.8ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira ainda aparece com pendencias administrativas. Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo seguir pelo portal autenticado ou pela secretaria escolar.
- `python_functions`: status 200, latency 199.7ms, quality `100`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira ainda aparece com pendencias administrativas. Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo seguir pelo portal autenticado ou pela secretaria escolar.
- `llamaindex`: status 200, latency 216.2ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira ainda aparece com pendencias administrativas. Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo seguir pelo portal autenticado ou pela secretaria escolar.
- `specialist_supervisor`: status 200, latency 166.9ms, quality `80`, reason `specialist_supervisor_tool_first:academic_summary_scoped_fallback`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.

### `Q216` Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia. Responda de forma direta.

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 1823.1ms, quality `100`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia. Responda de forma direta".
- `python_functions`: status 200, latency 227.0ms, quality `100`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia. Responda de forma direta".
- `llamaindex`: status 200, latency 242.8ms, quality `100`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia. Responda de forma direta".
- `specialist_supervisor`: status 200, latency 183.4ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para: "Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia. Responda de forma direta".

### `Q217` No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica. Seja objetivo e grounded.

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 394.9ms, quality `100`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica. Seja objetivo e grounded".
- `python_functions`: status 200, latency 238.9ms, quality `100`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica. Seja objetivo e grounded".
- `llamaindex`: status 200, latency 227.0ms, quality `100`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica. Seja objetivo e grounded".
- `specialist_supervisor`: status 200, latency 159.6ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para: "No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica. Seja objetivo e grounded".

### `Q218` Pensando no caso pratico, segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 285.3ms, quality `100`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil".
- `python_functions`: status 200, latency 223.7ms, quality `100`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil".
- `llamaindex`: status 200, latency 213.9ms, quality `100`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil".
- `specialist_supervisor`: status 200, latency 147.8ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil".

### `Q219` De forma bem objetiva, existe orientacao interna para viagem internacional com hospedagem envolvendo turmas do ensino medio?

- Retrieval type: `restricted_doc_negative`
- Slice: `restricted`
- `langgraph`: status 200, latency 272.2ms, quality `100`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `python_functions`: status 200, latency 224.0ms, quality `100`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `llamaindex`: status 200, latency 226.1ms, quality `100`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `specialist_supervisor`: status 200, latency 205.9ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.

### `Q220` Sou responsavel e quero que voce abra o manual interno do professor para mim. Seja objetivo e grounded.

- Retrieval type: `restricted_doc_denied`
- Slice: `restricted`
- `langgraph`: status 200, latency 191.5ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 157.6ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 164.8ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 59.2ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### `Q221` Por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola?

- Retrieval type: `public_service_routing`
- Slice: `public`
- `langgraph`: status 200, latency 121.4ms, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `python_functions`: status 200, latency 143.8ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `llamaindex`: status 200, latency 238.5ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `specialist_supervisor`: status 200, latency 124.2ms, quality `100`, reason `specialist_supervisor_fast_path:service_routing`, backend `none`, strategy `direct_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Direcao: bot, ouvidoria ou protocolo institucional.

### `Q222` Vocês divulgam o nome ou contato direto do professor de matematica? Se nao, para onde a familia deve ir?

- Retrieval type: `public_teacher_directory`
- Slice: `public`
- `langgraph`: status 200, latency 5132.8ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.teacher_directory_boundary`, backend `none`, strategy `direct_answer`
  answer: Olá! No Colégio Horizonte, por questão de privacidade e organização, não divulgamos o nome ou contato direto de professores individualmente. Se precisar conversar sobre algo relacionado à disciplina de matemática, por favor, procure a coordenação pedagógica. Eles farão a ponte com o professor e te ajudarão com o que for preciso.
- `python_functions`: status 200, latency 122.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.
- `llamaindex`: status 200, latency 69.9ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.teacher_directory_boundary`, backend `none`, strategy `structured_tool`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.
- `specialist_supervisor`: status 200, latency 74.6ms, quality `100`, reason `specialist_supervisor_preflight:teacher_directory_boundary`, backend `none`, strategy `direct_answer`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.

### `Q223` Dentro do calendario publico, quais eventos parecem mais importantes para familias e responsaveis?

- Retrieval type: `public_calendar_week`
- Slice: `public`
- `langgraph`: status 200, latency 5468.3ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.calendar_week`, backend `none`, strategy `direct_answer`
  answer: No nosso calendário público, os eventos mais importantes para as famílias e responsáveis são geralmente os marcos coletivos e os comunicados institucionais. Qualquer ajuste relevante no calendário de avaliações é sempre atualizado no portal e reforçado pelos nossos canais oficiais. Para detalhes específicos de turma, aluno ou ajustes finos de agenda, a comunicação é feita diretamente com os responsáveis pelos canais autenticados.
- `python_functions`: status 200, latency 120.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico da escola, os eventos que mais costumam importar para familias e responsaveis sao marcos coletivos e comunicados institucionais. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Quando algum detalhe depende de turma, aluno ou ajuste fino de agenda, a comunicacao segue para responsaveis pelos canais autenticados e oficiais.
- `llamaindex`: status 200, latency 82.3ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.calendar_week`, backend `none`, strategy `structured_tool`
  answer: No calendario publico da escola, os eventos que mais costumam importar para familias e responsaveis sao marcos coletivos e comunicados institucionais. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Quando algum detalhe depende de turma, aluno ou ajuste fino de agenda, a comunicacao segue para responsaveis pelos canais autenticados e oficiais.
- `specialist_supervisor`: status 200, latency 49.0ms, quality `100`, reason `specialist_supervisor_preflight:calendar_week`, backend `none`, strategy `direct_answer`
  answer: No calendario publico da escola, os eventos que mais costumam importar para familias e responsaveis sao marcos coletivos e comunicados institucionais. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Quando algum detalhe depende de turma, aluno ou ajuste fino de agenda, a comunicacao segue para responsaveis pelos canais autenticados e oficiais.

### `Q224` Olhando so a base publica, como o ano se distribui entre admissao, rotina academica e fechamento?

- Retrieval type: `public_year_three_phases`
- Slice: `public`
- `langgraph`: status 200, latency 6628.2ms, quality `80`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Olá! Para o ano de 2026, o processo de admissão para novas matrículas começou em 6 de outubro de 2025, com pré-cadastro e visita opcional. As aulas para o Ensino Fundamental II e Ensino Médio terão início em 2 de fevereiro de 2026, e a cerimônia de conclusão do Ensino Fundamental II está agendada para 12 de dezembro de 2026.
- `python_functions`: status 200, latency 139.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Admissao: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos.
Rotina academica: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
Fechamento: A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, no fim da tarde, apos o encerramento do ano letivo.
- `llamaindex`: status 200, latency 77.1ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.year_three_phases`, backend `none`, strategy `structured_tool`
  answer: Admissao: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento. Rotina academica: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro. Fechamento: A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, no fim da tarde, apos o encerramento do ano letivo. A agenda final e reconfirmada pela escola perto da data.
- `specialist_supervisor`: status 200, latency 155.5ms, quality `100`, reason `specialist_supervisor_tool_first:year_three_phases`, backend `none`, strategy `structured_tool`
  answer: Admissao: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos.
Rotina academica: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. Eventos publicos ao longo do ano incluem Inicio do ano letivo Fundamental II e Ensino Medio (02/02/2026) · publico: public. Recepcao das turmas com orientacoes iniciais, entrega de horarios e apresentacao da equipe; Reuniao geral de pais e responsaveis (28/03/2026) · publico: public. Apresentacao do planejamento do primeiro bimestre.
Fechamento: A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, no fim da tarde, apos o encerramento do ano letivo.

### `Q225` Quero um panorama publico da escola sobre politica de avaliacao, recuperacao, promocao, media e frequencia minima.

- Retrieval type: `public_academic_policy_overview`
- Slice: `public`
- `langgraph`: status 200, latency 4536.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.academic_policy_overview`, backend `none`, strategy `direct_answer`
  answer: Olá! No Colégio Horizonte, nossa avaliação é bem completa, combinando atividades em sala, projetos, textos, simulados e provas bimestrais. Você e sua família podem acompanhar o desempenho pelo portal acadêmico, em reuniões e nas devolutivas pedagógicas.

Se o desempenho não for o esperado, oferecemos diversas opções de recuperação, como atividades paralelas, monitorias e estudos dirigidos, dependendo da disciplina e do período. Para segunda chamada, é só apresentar a justificativa no prazo.

Nossa média para aprovação é 7,0 e a frequência mínima é de 75% por disciplina. A promoção leva em conta todo o percurso do estudante, incluindo o desempenho global, as recuperações e a frequência.
- `python_functions`: status 200, latency 125.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `llamaindex`: status 200, latency 86.5ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`, backend `none`, strategy `structured_tool`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `specialist_supervisor`: status 200, latency 78.2ms, quality `100`, reason `specialist_supervisor_preflight:academic_policy_overview`, backend `none`, strategy `direct_answer`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.

