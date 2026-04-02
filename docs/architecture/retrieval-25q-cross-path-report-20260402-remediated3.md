# Retrieval 25Q Cross-Path Report

Date: 2026-04-02T17:01:38.355737+00:00

Dataset: `tests/evals/datasets/retrieval_25q_probe_cases.generated.20260402.json`

Run prefix: `debug:retrieval20:20260402T170035Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency | Median | P95 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `25/25` | `24/25` | `99.2` | `1901.2 ms` | `1065.8 ms` | `5659.5 ms` | `6240.1 ms` |
| `python_functions` | `25/25` | `25/25` | `100.0` | `145.5 ms` | `123.8 ms` | `222.3 ms` | `233.2 ms` |
| `llamaindex` | `25/25` | `25/25` | `100.0` | `128.2 ms` | `85.3 ms` | `222.5 ms` | `263.3 ms` |
| `specialist_supervisor` | `25/25` | `18/25` | `94.4` | `259.4 ms` | `103.9 ms` | `154.3 ms` | `4326.1 ms` |

## By Slice

- `protected`
  - `langgraph`: keyword pass 4/4, quality 100.0, latency 192.2ms
  - `python_functions`: keyword pass 4/4, quality 100.0, latency 201.5ms
  - `llamaindex`: keyword pass 4/4, quality 100.0, latency 198.0ms
  - `specialist_supervisor`: keyword pass 0/4, quality 80.0, latency 120.8ms
- `public`
  - `langgraph`: keyword pass 15/16, quality 98.8, latency 2795.2ms
  - `python_functions`: keyword pass 16/16, quality 100.0, latency 118.6ms
  - `llamaindex`: keyword pass 16/16, quality 100.0, latency 83.5ms
  - `specialist_supervisor`: keyword pass 15/16, quality 98.8, latency 335.1ms
- `restricted`
  - `langgraph`: keyword pass 5/5, quality 100.0, latency 407.7ms
  - `python_functions`: keyword pass 5/5, quality 100.0, latency 186.7ms
  - `llamaindex`: keyword pass 5/5, quality 100.0, latency 215.6ms
  - `specialist_supervisor`: keyword pass 3/5, quality 92.0, latency 127.8ms

## By Retrieval Type

- `protected_structured_academic`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 211.4ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 186.2ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 203.5ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 114.1ms
- `protected_structured_admin`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 174.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 233.2ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 202.1ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 127.9ms
- `protected_structured_finance`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 211.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 187.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 198.7ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 113.8ms
- `protected_structured_followup`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 171.7ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 199.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 187.6ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 127.6ms
- `public_academic_policy_overview`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4034.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 113.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 65.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 50.0ms
- `public_calendar_week`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 3232.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 121.3ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 84.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 48.7ms
- `public_deep_multi_doc`
  - `langgraph`: keyword pass 2/2, quality 100.0, latency 3004.1ms
  - `python_functions`: keyword pass 2/2, quality 100.0, latency 115.0ms
  - `llamaindex`: keyword pass 2/2, quality 100.0, latency 77.2ms
  - `specialist_supervisor`: keyword pass 2/2, quality 100.0, latency 49.2ms
- `public_documents_credentials`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2355.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 113.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 70.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 49.7ms
- `public_family_new_bundle`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2798.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 121.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 75.5ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 131.8ms
- `public_first_month_risks`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 3044.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 124.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 74.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 46.1ms
- `public_permanence_support`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 3434.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 109.3ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 71.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 103.9ms
- `public_policy_bridge`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 295.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 125.2ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 73.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 145.5ms
- `public_process_compare`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 119.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 116.4ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 126.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 48.2ms
- `public_section_aware`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2430.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 118.2ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 66.6ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 47.7ms
- `public_service_routing`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 118.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 130.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 141.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 109.8ms
- `public_teacher_directory`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4206.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 114.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 72.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 51.2ms
- `public_timeline`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 1677.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 123.8ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 104.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 55.1ms
- `public_visibility_boundary`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4729.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 119.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 82.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 50.1ms
- `public_year_three_phases`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 6240.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 118.2ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 74.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 4326.1ms
- `restricted_doc_denied`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 141.4ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 125.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 185.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 67.0ms
- `restricted_doc_negative`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 292.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 225.8ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 263.3ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 156.5ms
- `restricted_doc_positive`
  - `langgraph`: keyword pass 3/3, quality 100.0, latency 534.8ms
  - `python_functions`: keyword pass 3/3, quality 100.0, latency 194.1ms
  - `llamaindex`: keyword pass 3/3, quality 100.0, latency 209.8ms
  - `specialist_supervisor`: keyword pass 2/3, quality 93.3, latency 138.6ms

## Latency Outliers

- `langgraph`
  - `Q224` `public_year_three_phases` `6240.1 ms` quality `80` reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  - `Q211` `public_deep_multi_doc` `5892.0 ms` quality `100` reason `langgraph_public_canonical_lane:public_bundle.transversal_year`
  - `Q210` `public_visibility_boundary` `4729.6 ms` quality `100` reason `langgraph_public_canonical_lane:public_bundle.visibility_boundary`
- `python_functions`
  - `Q215` `protected_structured_admin` `233.2 ms` quality `100` reason `python_functions_native_structured:institution`
  - `Q219` `restricted_doc_negative` `225.8 ms` quality `100` reason `python_functions_native_restricted_document_no_match`
  - `Q217` `restricted_doc_positive` `208.5 ms` quality `100` reason `python_functions_native_restricted_document_no_match`
- `llamaindex`
  - `Q219` `restricted_doc_negative` `263.3 ms` quality `100` reason `llamaindex_restricted_doc_no_match`
  - `Q216` `restricted_doc_positive` `227.2 ms` quality `100` reason `llamaindex_restricted_doc_no_match`
  - `Q212` `protected_structured_academic` `203.5 ms` quality `100` reason `dados estruturados devem passar por service deterministico`
- `specialist_supervisor`
  - `Q224` `public_year_three_phases` `4326.1 ms` quality `100` reason `specialist_supervisor_fast_path:general_knowledge`
  - `Q219` `restricted_doc_negative` `156.5 ms` quality `80` reason `specialist_supervisor_resolved_intent:shift_offers`
  - `Q201` `public_policy_bridge` `145.5 ms` quality `100` reason `specialist_supervisor_fast_path:health_second_call`

## Failures

- `Q204` `specialist_supervisor` `public_family_new_bundle` quality `80` mode `structured_tool` reason `specialist_supervisor_tool_first:public_timeline_bundle` errors `missing_expected_keyword`
- `Q212` `specialist_supervisor` `protected_structured_academic` quality `80` mode `clarify` reason `specialist_supervisor_strict_safe_fallback` errors `missing_expected_keyword`
- `Q213` `specialist_supervisor` `protected_structured_followup` quality `80` mode `clarify` reason `specialist_supervisor_strict_safe_fallback` errors `missing_expected_keyword`
- `Q214` `specialist_supervisor` `protected_structured_finance` quality `80` mode `clarify` reason `specialist_supervisor_strict_safe_fallback` errors `missing_expected_keyword`
- `Q215` `specialist_supervisor` `protected_structured_admin` quality `80` mode `clarify` reason `specialist_supervisor_strict_safe_fallback` errors `missing_expected_keyword`
- `Q217` `specialist_supervisor` `restricted_doc_positive` quality `80` mode `clarify` reason `specialist_supervisor_strict_safe_fallback` errors `missing_expected_keyword`
- `Q219` `specialist_supervisor` `restricted_doc_negative` quality `80` mode `structured_tool` reason `specialist_supervisor_resolved_intent:shift_offers` errors `missing_expected_keyword`
- `Q224` `langgraph` `public_year_three_phases` quality `80` mode `structured_tool` reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao` errors `missing_expected_keyword`

## Prompt Results

### `Q201` Se uma prova e perdida por motivo de saude, como atestado, segunda chamada e recuperacao aparecem conectados nos documentos publicos. Responda de forma direta.

- Retrieval type: `public_policy_bridge`
- Slice: `public`
- `langgraph`: status 200, latency 295.1ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.health_second_call`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `python_functions`: status 200, latency 125.2ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 73.4ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.health_second_call`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 145.5ms, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`, backend `none`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### `Q202` Sem sair do escopo do projeto, no cronograma publico de 2026, em que ordem aparecem abertura da matricula, comeco das aulas e primeiro encontro com responsaveis?

- Retrieval type: `public_timeline`
- Slice: `public`
- `langgraph`: status 200, latency 1677.0ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.timeline_lifecycle`, backend `none`, strategy `direct_answer`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `python_functions`: status 200, latency 123.8ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `llamaindex`: status 200, latency 104.3ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.timeline_lifecycle`, backend `none`, strategy `structured_tool`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `specialist_supervisor`: status 200, latency 55.1ms, quality `100`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.

### `Q203` Sem sair do escopo do projeto, para resolver acesso e envio documental sem erro, como portal, credenciais e secretaria entram na ordem certa?

- Retrieval type: `public_documents_credentials`
- Slice: `public`
- `langgraph`: status 200, latency 2355.0ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `direct_answer`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `python_functions`: status 200, latency 113.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 70.8ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `specialist_supervisor`: status 200, latency 49.7ms, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### `Q204` Para uma casa que esta entrando no Colegio Horizonte agora, como matricula, inicio das aulas e avaliacoes se relacionam no comeco do ano?

- Retrieval type: `public_family_new_bundle`
- Slice: `public`
- `langgraph`: status 200, latency 2798.1ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `python_functions`: status 200, latency 121.9ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `llamaindex`: status 200, latency 75.5ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `specialist_supervisor`: status 200, latency 131.8ms, quality `80`, reason `specialist_supervisor_tool_first:public_timeline_bundle`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### `Q205` Quais apoios publicos evitam que a familia se perca ao acompanhar permanencia e vida escolar do estudante. Responda de forma direta.

- Retrieval type: `public_permanence_support`
- Slice: `public`
- `langgraph`: status 200, latency 3434.8ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `python_functions`: status 200, latency 109.3ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 71.3ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 103.9ms, quality `100`, reason `specialist_supervisor_preflight:permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### `Q206` Quando comparo rematricula, transferencia de entrada e cancelamento, o que muda de verdade em prazo, protocolo e documentos. Traga a resposta de forma concreta.

- Retrieval type: `public_process_compare`
- Slice: `public`
- `langgraph`: status 200, latency 119.3ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.process_compare`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `python_functions`: status 200, latency 116.4ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 126.2ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 48.2ms, quality `100`, reason `specialist_supervisor_preflight:process_compare`, backend `none`, strategy `direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### `Q207` No arranque do ano letivo, que descuidos mais costumam explodir entre credenciais, papelada e rotina da casa?

- Retrieval type: `public_first_month_risks`
- Slice: `public`
- `langgraph`: status 200, latency 3044.1ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.first_month_risks`, backend `none`, strategy `direct_answer`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `python_functions`: status 200, latency 124.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `llamaindex`: status 200, latency 74.2ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.first_month_risks`, backend `none`, strategy `structured_tool`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `specialist_supervisor`: status 200, latency 46.1ms, quality `100`, reason `specialist_supervisor_preflight:first_month_risks`, backend `none`, strategy `direct_answer`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.

### `Q208` Relacione convivencia, frequencia e recuperacao usando os documentos publicos mais relevantes da escola.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 116.2ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.academic_policy_overview`, backend `none`, strategy `structured_tool`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `python_functions`: status 200, latency 110.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `llamaindex`: status 200, latency 69.1ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`, backend `none`, strategy `structured_tool`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `specialist_supervisor`: status 200, latency 45.7ms, quality `100`, reason `specialist_supervisor_preflight:academic_policy_overview`, backend `none`, strategy `direct_answer`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.

### `Q209` Pensando no caso pratico, na base publica do ensino medio, como biblioteca, laboratorios e apoio ao estudo aparecem amarrados na rotina academica?

- Retrieval type: `public_section_aware`
- Slice: `public`
- `langgraph`: status 200, latency 2430.1ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `python_functions`: status 200, latency 118.2ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `llamaindex`: status 200, latency 66.6ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `specialist_supervisor`: status 200, latency 47.7ms, quality `100`, reason `specialist_supervisor_preflight:facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.

### `Q210` Pensando no caso pratico, nos canais digitais da escola, o que ainda e publico e o que passa a depender da autenticacao da familia?

- Retrieval type: `public_visibility_boundary`
- Slice: `public`
- `langgraph`: status 200, latency 4729.6ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.visibility_boundary`, backend `none`, strategy `direct_answer`
  answer: Olá! No nosso calendário público, você sempre encontrará os marcos institucionais gerais e os eventos coletivos da escola. Já os detalhes individuais de cada aluno, convites específicos, protocolos, informações financeiras e acompanhamentos protegidos dependem de autenticação ou de um contexto interno. Fique tranquila, sempre que houver alguma mudança importante no calendário de avaliações, nós atualizamos o portal e reforçamos a comunicação pelos nossos canais oficiais.
- `python_functions`: status 200, latency 119.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `llamaindex`: status 200, latency 82.3ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.visibility_boundary`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 50.1ms, quality `100`, reason `specialist_supervisor_preflight:visibility_boundary`, backend `none`, strategy `direct_answer`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.

### `Q211` Como os materiais publicos mostram a relacao entre agenda avaliativa, comunicacao com responsaveis, estudo orientado e meios digitais durante o ano?

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 5892.0ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `direct_answer`
  answer: No Colégio Horizonte, a agenda avaliativa, a comunicação com os responsáveis, o estudo orientado e os meios digitais trabalham juntos para apoiar o aprendizado. Sempre que há alguma mudança importante no calendário de avaliações, nós atualizamos o portal e reforçamos a comunicação pelos nossos canais oficiais.

Utilizamos comunicados digitais, reuniões e chamadas de acompanhamento para manter as famílias informadas, especialmente quando um estudante precisa de um suporte extra. O estudo orientado oferece um apoio valioso na organização de tarefas, prazos e na construção de bons hábitos de estudo, com atividades como oficinas de leitura, projetos e monitorias.

É importante lembrar que, para um atendimento protegido no Telegram, é preciso vincular a conta ao cadastro da escola. O ambiente digital amplia nosso alcance, mas não substitui todos os nossos processos formais. Quando há ajustes no calendário, reforço pedagógico ou novas orientações, publicamos no portal, reforçamos pelos canais oficiais e entramos em contato com a família quando o acompanhamento é mais próximo.
- `python_functions`: status 200, latency 119.9ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `llamaindex`: status 200, latency 85.3ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `specialist_supervisor`: status 200, latency 52.7ms, quality `100`, reason `specialist_supervisor_preflight:transversal_year_bundle`, backend `none`, strategy `direct_answer`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.

### `Q212` Quero comparar rapidamente a situacao academica dos meus dois filhos e saber quem esta mais proximo do limite de aprovacao. Seja objetivo e grounded.

- Retrieval type: `protected_structured_academic`
- Slice: `protected`
- `langgraph`: status 200, latency 211.4ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `python_functions`: status 200, latency 186.2ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `llamaindex`: status 200, latency 203.5ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `specialist_supervisor`: status 200, latency 114.1ms, quality `80`, reason `specialist_supervisor_strict_safe_fallback`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### `Q213` Mantendo o contexto dos meus filhos, filtre para a Ana e mostre as materias em que ela esta mais vulneravel.

- Retrieval type: `protected_structured_followup`
- Slice: `protected`
- `langgraph`: status 200, latency 171.7ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.
- `python_functions`: status 200, latency 199.1ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.
- `llamaindex`: status 200, latency 187.6ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.
- `specialist_supervisor`: status 200, latency 127.6ms, quality `80`, reason `specialist_supervisor_strict_safe_fallback`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### `Q214` Pensando no caso pratico, como esta o financeiro da familia hoje, incluindo vencimentos e proximos passos?

- Retrieval type: `protected_structured_finance`
- Slice: `protected`
- `langgraph`: status 200, latency 211.6ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro da familia hoje: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora os vencimentos e proximos passos detalhados, mas o recorte continua sendo o financeiro das contas vinculadas.
- `python_functions`: status 200, latency 187.5ms, quality `100`, reason `python_functions_native_structured:finance`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro da familia hoje: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora os vencimentos e proximos passos detalhados, mas o recorte continua sendo o financeiro das contas vinculadas.
- `llamaindex`: status 200, latency 198.7ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro da familia hoje: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora os vencimentos e proximos passos detalhados, mas o recorte continua sendo o financeiro das contas vinculadas.
- `specialist_supervisor`: status 200, latency 113.8ms, quality `80`, reason `specialist_supervisor_strict_safe_fallback`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### `Q215` Hoje, o que ainda falta na parte administrativa da Ana e como a familia deve agir em seguida?

- Retrieval type: `protected_structured_admin`
- Slice: `protected`
- `langgraph`: status 200, latency 174.3ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira ainda aparece com pendencias administrativas. Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo seguir pelo portal autenticado ou pela secretaria escolar.
- `python_functions`: status 200, latency 233.2ms, quality `100`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira ainda aparece com pendencias administrativas. Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo seguir pelo portal autenticado ou pela secretaria escolar.
- `llamaindex`: status 200, latency 202.1ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira ainda aparece com pendencias administrativas. Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo seguir pelo portal autenticado ou pela secretaria escolar.
- `specialist_supervisor`: status 200, latency 127.9ms, quality `80`, reason `specialist_supervisor_strict_safe_fallback`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### `Q216` Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia. Responda de forma direta.

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 1065.8ms, quality `100`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia. Responda de forma direta".
- `python_functions`: status 200, latency 182.2ms, quality `100`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia. Responda de forma direta".
- `llamaindex`: status 200, latency 227.2ms, quality `100`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia. Responda de forma direta".
- `specialist_supervisor`: status 200, latency 144.0ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para: "Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia. Responda de forma direta".

### `Q217` No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica. Seja objetivo e grounded.

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 339.1ms, quality `100`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica. Seja objetivo e grounded".
- `python_functions`: status 200, latency 208.5ms, quality `100`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica. Seja objetivo e grounded".
- `llamaindex`: status 200, latency 201.7ms, quality `100`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica. Seja objetivo e grounded".
- `specialist_supervisor`: status 200, latency 134.4ms, quality `80`, reason `specialist_supervisor_strict_safe_fallback`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### `Q218` Pensando no caso pratico, segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 199.5ms, quality `100`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil".
- `python_functions`: status 200, latency 191.6ms, quality `100`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil".
- `llamaindex`: status 200, latency 200.4ms, quality `100`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil".
- `specialist_supervisor`: status 200, latency 137.3ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil".

### `Q219` De forma bem objetiva, existe orientacao interna para viagem internacional com hospedagem envolvendo turmas do ensino medio?

- Retrieval type: `restricted_doc_negative`
- Slice: `restricted`
- `langgraph`: status 200, latency 292.9ms, quality `100`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `python_functions`: status 200, latency 225.8ms, quality `100`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `llamaindex`: status 200, latency 263.3ms, quality `100`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `specialist_supervisor`: status 200, latency 156.5ms, quality `80`, reason `specialist_supervisor_resolved_intent:shift_offers`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje o Colegio Horizonte publica estes turnos de atendimento escolar:
- Ensino Medio: Manha (07:15 as 12:50).
- Fundamental II e Ensino Medio: Integral opcional (07:00 as 17:30).

### `Q220` Sou responsavel e quero que voce abra o manual interno do professor para mim. Seja objetivo e grounded.

- Retrieval type: `restricted_doc_denied`
- Slice: `restricted`
- `langgraph`: status 200, latency 141.4ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 125.5ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 185.2ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 67.0ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### `Q221` Por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola?

- Retrieval type: `public_service_routing`
- Slice: `public`
- `langgraph`: status 200, latency 118.6ms, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `python_functions`: status 200, latency 130.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `llamaindex`: status 200, latency 141.3ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `specialist_supervisor`: status 200, latency 109.8ms, quality `100`, reason `specialist_supervisor_fast_path:service_routing`, backend `none`, strategy `direct_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Direcao: bot, ouvidoria ou protocolo institucional.

### `Q222` Vocês divulgam o nome ou contato direto do professor de matematica? Se nao, para onde a familia deve ir?

- Retrieval type: `public_teacher_directory`
- Slice: `public`
- `langgraph`: status 200, latency 4206.0ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.teacher_directory_boundary`, backend `none`, strategy `direct_answer`
  answer: Olá! No Colégio Horizonte, por questão de privacidade e organização, não divulgamos o nome ou contato direto de professores individualmente. Se precisar conversar sobre algo relacionado à disciplina de matemática, por favor, procure a coordenação pedagógica. Eles farão a ponte com o professor e te ajudarão com o que for preciso.
- `python_functions`: status 200, latency 114.0ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.
- `llamaindex`: status 200, latency 72.2ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.teacher_directory_boundary`, backend `none`, strategy `structured_tool`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.
- `specialist_supervisor`: status 200, latency 51.2ms, quality `100`, reason `specialist_supervisor_preflight:teacher_directory_boundary`, backend `none`, strategy `direct_answer`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.

### `Q223` Dentro do calendario publico, quais eventos parecem mais importantes para familias e responsaveis?

- Retrieval type: `public_calendar_week`
- Slice: `public`
- `langgraph`: status 200, latency 3232.3ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.calendar_week`, backend `none`, strategy `direct_answer`
  answer: No nosso calendário público, os eventos mais importantes para as famílias e responsáveis são geralmente os marcos coletivos e os comunicados institucionais. Qualquer ajuste relevante no calendário de avaliações é sempre atualizado no portal e reforçado pelos nossos canais oficiais. Para detalhes específicos de turma, aluno ou ajustes finos de agenda, a comunicação é feita diretamente com os responsáveis pelos canais autenticados.
- `python_functions`: status 200, latency 121.3ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico da escola, os eventos que mais costumam importar para familias e responsaveis sao marcos coletivos e comunicados institucionais. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Quando algum detalhe depende de turma, aluno ou ajuste fino de agenda, a comunicacao segue para responsaveis pelos canais autenticados e oficiais.
- `llamaindex`: status 200, latency 84.5ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.calendar_week`, backend `none`, strategy `structured_tool`
  answer: No calendario publico da escola, os eventos que mais costumam importar para familias e responsaveis sao marcos coletivos e comunicados institucionais. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Quando algum detalhe depende de turma, aluno ou ajuste fino de agenda, a comunicacao segue para responsaveis pelos canais autenticados e oficiais.
- `specialist_supervisor`: status 200, latency 48.7ms, quality `100`, reason `specialist_supervisor_preflight:calendar_week`, backend `none`, strategy `direct_answer`
  answer: No calendario publico da escola, os eventos que mais costumam importar para familias e responsaveis sao marcos coletivos e comunicados institucionais. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Quando algum detalhe depende de turma, aluno ou ajuste fino de agenda, a comunicacao segue para responsaveis pelos canais autenticados e oficiais.

### `Q224` Olhando so a base publica, como o ano se distribui entre admissao, rotina academica e fechamento?

- Retrieval type: `public_year_three_phases`
- Slice: `public`
- `langgraph`: status 200, latency 6240.1ms, quality `80`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Que bom que você está se planejando! O ano letivo de 2026 no Colégio Horizonte começa com as matrículas abertas em 6 de outubro de 2025, incluindo pré-cadastro e visita opcional. As aulas para o Ensino Fundamental II e Ensino Médio iniciam em 2 de fevereiro de 2026, e a cerimônia de conclusão do Ensino Fundamental II está agendada para 12 de dezembro de 2026.
- `python_functions`: status 200, latency 118.2ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Admissao: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos.
Rotina academica: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
Fechamento: A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, no fim da tarde, apos o encerramento do ano letivo.
- `llamaindex`: status 200, latency 74.1ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.year_three_phases`, backend `none`, strategy `structured_tool`
  answer: Admissao: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento. Rotina academica: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro. Fechamento: A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, no fim da tarde, apos o encerramento do ano letivo. A agenda final e reconfirmada pela escola perto da data.
- `specialist_supervisor`: status 200, latency 4326.1ms, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`, backend `none`, strategy `direct_answer`
  answer: Um ano acadêmico geralmente se distribui da seguinte forma:

1.  **Admissão:** Ocorre antes do início das aulas, envolvendo processos seletivos, matrículas e planejamento.
2.  **Rotina Acadêmica:** Abrange o período principal de aulas, atividades, avaliações e projetos, distribuídos em semestres ou trimestres.
3.  **Fechamento:** Inclui as avaliações finais, encerramento de disciplinas, formaturas e procedimentos administrativos de final de período.

### `Q225` Quero um panorama publico da escola sobre politica de avaliacao, recuperacao, promocao, media e frequencia minima.

- Retrieval type: `public_academic_policy_overview`
- Slice: `public`
- `langgraph`: status 200, latency 4034.2ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.academic_policy_overview`, backend `none`, strategy `direct_answer`
  answer: Olá! No Colégio Horizonte, nossa avaliação é bem completa, combinando atividades em sala, projetos, textos, simulados e provas bimestrais. Você e sua família podem acompanhar o desempenho pelo portal acadêmico, em reuniões e nas devolutivas pedagógicas.

Se o desempenho não for o esperado, oferecemos diversas opções de recuperação, como atividades paralelas, monitorias e estudos dirigidos, dependendo da disciplina e do período. Para segunda chamada, é só apresentar a justificativa no prazo.

Nossa média para aprovação é 7,0 e a frequência mínima é de 75% por disciplina. A promoção leva em conta todo o percurso do estudante, incluindo o desempenho global, as recuperações e a frequência.
- `python_functions`: status 200, latency 113.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `llamaindex`: status 200, latency 65.1ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`, backend `none`, strategy `structured_tool`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `specialist_supervisor`: status 200, latency 50.0ms, quality `100`, reason `specialist_supervisor_preflight:academic_policy_overview`, backend `none`, strategy `direct_answer`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.

