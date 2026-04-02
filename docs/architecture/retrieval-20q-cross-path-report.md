# Retrieval 20Q Cross-Path Report

Date: 2026-04-02T08:11:00.124069+00:00

Dataset: `tests/evals/datasets/retrieval_20q_probe_cases.generated.json`

Run prefix: `debug:retrieval20:20260402T080859Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `20/20` | `14/20` | `93.4` | `2167.6 ms` |
| `crewai` | `20/20` | `13/20` | `92.4` | `2582.8 ms` |
| `python_functions` | `20/20` | `15/20` | `95.0` | `280.2 ms` |
| `llamaindex` | `20/20` | `11/20` | `91.0` | `316.2 ms` |
| `specialist_supervisor` | `20/20` | `16/20` | `95.4` | `557.3 ms` |

## By Retrieval Type

- `protected_structured_academic`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 194.1ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 329.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 213.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 232.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 352.3ms
- `protected_structured_admin`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 245.9ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 850.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 249.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 266.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 262.7ms
- `protected_structured_finance`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 170.6ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 302.9ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 183.1ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 207.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 88.0, latency 215.9ms
- `protected_structured_followup`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 309.4ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 21282.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 274.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 297.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 255.8ms
- `public_deep_multi_doc`
  - `langgraph`: keyword pass 2/2, quality 100.0, latency 1321.4ms
  - `crewai`: keyword pass 2/2, quality 100.0, latency 252.9ms
  - `python_functions`: keyword pass 2/2, quality 100.0, latency 171.9ms
  - `llamaindex`: keyword pass 1/2, quality 90.0, latency 159.8ms
  - `specialist_supervisor`: keyword pass 2/2, quality 100.0, latency 105.5ms
- `public_documents_credentials`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2411.7ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 282.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 154.7ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 198.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 110.8ms
- `public_family_new_bundle`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 5272.0ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 288.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 175.6ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 239.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 93.7ms
- `public_first_month_risks`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 2859.7ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 265.5ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 163.8ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 187.9ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 215.7ms
- `public_permanence_support`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 4523.6ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 276.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 271.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 107.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 117.3ms
- `public_policy_bridge`
  - `langgraph`: keyword pass 1/1, quality 88.0, latency 6304.3ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 331.7ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 176.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 193.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 216.5ms
- `public_process_compare`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 185.1ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 345.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 157.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 193.6ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 126.1ms
- `public_section_aware`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2330.1ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 256.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 160.6ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 196.6ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 129.6ms
- `public_timeline`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4589.1ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 252.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 165.0ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 181.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 212.8ms
- `public_visibility_boundary`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 5946.6ms
  - `crewai`: keyword pass 1/1, quality 88.0, latency 22065.5ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 165.2ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 198.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 5585.2ms
- `restricted_doc_denied`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 305.0ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 300.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 197.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 217.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 145.6ms
- `restricted_doc_negative`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 939.5ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 820.9ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 643.6ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 821.8ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 827.5ms
- `restricted_doc_positive`
  - `langgraph`: keyword pass 1/3, quality 86.7, latency 1374.1ms
  - `crewai`: keyword pass 1/3, quality 86.7, latency 966.2ms
  - `python_functions`: keyword pass 1/3, quality 86.7, latency 636.1ms
  - `llamaindex`: keyword pass 1/3, quality 86.7, latency 755.6ms
  - `specialist_supervisor`: keyword pass 1/3, quality 86.7, latency 689.3ms

## Failures

- `Q201` `langgraph` `public_policy_bridge` quality `88` mode `structured_tool` reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno` errors `unnecessary_clarification`
- `Q201` `crewai` `public_policy_bridge` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q202` `llamaindex` `public_timeline` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q204` `llamaindex` `public_family_new_bundle` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q205` `langgraph` `public_permanence_support` quality `80` mode `structured_tool` reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support` errors `missing_expected_keyword`
- `Q206` `crewai` `public_process_compare` quality `80` mode `structured_tool` reason `workflow_not_found` errors `missing_expected_keyword`
- `Q207` `langgraph` `public_first_month_risks` quality `80` mode `structured_tool` reason `langgraph_public_canonical_lane:public_bundle.first_month_risks` errors `missing_expected_keyword`
- `Q207` `crewai` `public_first_month_risks` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q207` `python_functions` `public_first_month_risks` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q207` `llamaindex` `public_first_month_risks` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q207` `specialist_supervisor` `public_first_month_risks` quality `80` mode `structured_tool` reason `specialist_supervisor_preflight:first_month_risks` errors `missing_expected_keyword`
- `Q208` `llamaindex` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q209` `llamaindex` `public_section_aware` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q210` `crewai` `public_visibility_boundary` quality `88` mode `structured_tool` reason `crewai_public_flow_timeout` errors `unnecessary_clarification`
- `Q214` `langgraph` `protected_structured_finance` quality `80` mode `structured_tool` reason `dados estruturados devem passar por service deterministico` errors `missing_expected_keyword`
- `Q214` `crewai` `protected_structured_finance` quality `80` mode `structured_tool` reason `protected_shadow_unmatched_student_reference` errors `missing_expected_keyword`
- `Q214` `python_functions` `protected_structured_finance` quality `80` mode `structured_tool` reason `python_functions_native_structured:finance` errors `missing_expected_keyword`
- `Q214` `llamaindex` `protected_structured_finance` quality `80` mode `structured_tool` reason `dados estruturados devem passar por service deterministico` errors `missing_expected_keyword`
- `Q214` `specialist_supervisor` `protected_structured_finance` quality `88` mode `clarify` reason `specialist_supervisor_resolved_intent:finance_student_clarify` errors `unnecessary_clarification`
- `Q217` `langgraph` `restricted_doc_positive` quality `80` mode `hybrid_retrieval` reason `langgraph_restricted_document_search` errors `missing_expected_keyword`
- `Q217` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q217` `python_functions` `restricted_doc_positive` quality `80` mode `hybrid_retrieval` reason `python_functions_native_restricted_document_search` errors `missing_expected_keyword`
- `Q217` `llamaindex` `restricted_doc_positive` quality `80` mode `hybrid_retrieval` reason `llamaindex_restricted_doc_fast_path` errors `missing_expected_keyword`
- `Q217` `specialist_supervisor` `restricted_doc_positive` quality `80` mode `hybrid_retrieval` reason `specialist_supervisor_tool_first:restricted_document_search` errors `missing_expected_keyword`
- `Q218` `langgraph` `restricted_doc_positive` quality `80` mode `hybrid_retrieval` reason `langgraph_restricted_document_search` errors `missing_expected_keyword`
- `Q218` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q218` `python_functions` `restricted_doc_positive` quality `80` mode `hybrid_retrieval` reason `python_functions_native_restricted_document_search` errors `missing_expected_keyword`
- `Q218` `llamaindex` `restricted_doc_positive` quality `80` mode `hybrid_retrieval` reason `llamaindex_restricted_doc_fast_path` errors `missing_expected_keyword`
- `Q218` `specialist_supervisor` `restricted_doc_positive` quality `80` mode `hybrid_retrieval` reason `specialist_supervisor_tool_first:restricted_document_search` errors `missing_expected_keyword`
- `Q219` `langgraph` `restricted_doc_negative` quality `80` mode `hybrid_retrieval` reason `langgraph_restricted_document_search` errors `missing_expected_keyword`
- `Q219` `crewai` `restricted_doc_negative` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q219` `python_functions` `restricted_doc_negative` quality `80` mode `hybrid_retrieval` reason `python_functions_native_restricted_document_search` errors `missing_expected_keyword`
- `Q219` `llamaindex` `restricted_doc_negative` quality `80` mode `hybrid_retrieval` reason `llamaindex_restricted_doc_fast_path` errors `missing_expected_keyword`
- `Q219` `specialist_supervisor` `restricted_doc_negative` quality `80` mode `hybrid_retrieval` reason `specialist_supervisor_tool_first:restricted_document_search` errors `missing_expected_keyword`

## Prompt Results

### `Q201` Como a base publica da escola articula atestado medico, segunda chamada e recuperacao quando o aluno perde uma prova?

- Retrieval type: `public_policy_bridge`
- Slice: `public`
- `langgraph`: status 200, latency 6304.3ms, quality `88`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`, backend `qdrant_hybrid`, strategy `direct_answer`
  errors: unnecessary_clarification
  answer: Olá! Entendo sua preocupação. Quando um aluno perde uma prova, atestados médicos e outras justificativas formais são importantes para analisarmos a situação. Eles podem apoiar a solicitação de uma segunda chamada ou até mesmo uma adaptação temporária na rotina. Lembre-se que os pedidos de segunda chamada precisam ser feitos dentro do prazo que a escola orienta, ok?
- `crewai`: status 200, latency 331.7ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 176.0ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 193.0ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 216.5ms, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`, backend `none`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### `Q202` Ordene matricula, comeco das aulas e primeira reuniao com responsaveis no ciclo publico de 2026.

- Retrieval type: `public_timeline`
- Slice: `public`
- `langgraph`: status 200, latency 4589.1ms, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`, backend `none`, strategy `direct_answer`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento. Depois do inicio das aulas: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro. Primeira reuniao com responsaveis: A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `crewai`: status 200, latency 252.9ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. | 2025-10-06 | familias interessadas | O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. | 2026-02-02 | alunos e familias | A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. | 2026-03-28 | responsaveis e familias | A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `python_functions`: status 200, latency 165.0ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento. Depois do inicio das aulas: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro. Primeira reuniao com responsaveis: A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `llamaindex`: status 200, latency 181.1ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a base publica de Colegio Horizonte nao traz um marco institucional estruturado para essa data.
- `specialist_supervisor`: status 200, latency 212.8ms, quality `100`, reason `specialist_supervisor_tool_first:public_timeline_bundle`, backend `none`, strategy `structured_tool`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.

### `Q203` Para resolver acesso e envio documental sem erro, como portal, credenciais e secretaria entram na ordem certa?

- Retrieval type: `public_documents_credentials`
- Slice: `public`
- `langgraph`: status 200, latency 2411.7ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `direct_answer`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `crewai`: status 200, latency 282.9ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 154.7ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 198.9ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 110.8ms, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### `Q204` Como uma familia nova deve ler matricula, calendario e avaliacoes para entender o primeiro bimestre sem se perder?

- Retrieval type: `public_family_new_bundle`
- Slice: `public`
- `langgraph`: status 200, latency 5272.0ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `qdrant_hybrid`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `crewai`: status 200, latency 288.0ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Para uma familia nova, matricula, calendario e agenda de avaliacoes precisam ser lidos juntos: a matricula organiza ingresso, documentos e atendimento inicial; o calendario mostra inicio das aulas, marcos do bimestre e reunioes com responsaveis; e a agenda de avaliacoes explica janelas de prova, recuperacao e comunicados pedagogicos do primeiro bimestre.
- `python_functions`: status 200, latency 175.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `llamaindex`: status 200, latency 239.2ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Se eu tivesse 30 segundos para resumir Colegio Horizonte, eu diria isto: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Os diferenciais publicados com mais clareza hoje passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.
- `specialist_supervisor`: status 200, latency 93.7ms, quality `100`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.

### `Q205` Como a escola descreve publicamente os canais para a familia acompanhar permanencia, apoio e vida escolar?

- Retrieval type: `public_permanence_support`
- Slice: `public`
- `langgraph`: status 200, latency 4523.6ms, quality `80`, reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Que bom que você quer saber mais sobre como acompanhamos nossos estudantes! Aqui no Colégio Horizonte, a gente se dedica a oferecer um suporte completo. Para isso, combinamos orientação, monitorias, comunicação constante e um acompanhamento atento da frequência.

Nossa equipe de orientação está sempre de olho na adaptação, na rotina de estudos e no desenvolvimento de bons hábitos de aprendizagem. Além disso, temos monitorias agendadas e plantões de dúvidas para ajudar nas matérias mais desafiadoras.

A comunicação com as famílias é feita por comunicados digitais, reuniões periódicas e, se necessário, chamadas de acompanhamento. E lembre-se que a promoção do estudante considera tanto o desempenho acadêmico quanto a frequência mínima. No Ensino Médio, o Projeto de Vida é um componente curricular e um eixo importante de tutoria.
- `crewai`: status 200, latency 276.1ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao educacional, monitorias, comunicados digitais, reunioes periodicas com responsaveis e acionamento de acompanhamento quando frequencia, adaptacao ou rotina de estudo exigem intervencao.
- `python_functions`: status 200, latency 271.9ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 107.1ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 117.3ms, quality `100`, reason `specialist_supervisor_preflight:permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### `Q206` Compare rematricula, transferencia e cancelamento destacando diferencas de prazo, protocolo e papelada.

- Retrieval type: `public_process_compare`
- Slice: `public`
- `langgraph`: status 200, latency 185.1ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.process_compare`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `crewai`: status 200, latency 345.3ms, quality `80`, reason `workflow_not_found`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao encontrei um protocolo ativo nesta conversa para retomar agora. Se voce quiser, eu posso abrir o pedido, te dizer o protocolo, consultar o status ou montar um resumo quando houver um fluxo ativo.
- `python_functions`: status 200, latency 157.0ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 193.6ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 126.1ms, quality `100`, reason `specialist_supervisor_preflight:process_compare`, backend `none`, strategy `direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### `Q207` Que riscos do primeiro mes costumam surgir quando a familia atrasa documentos, credenciais e rotina?

- Retrieval type: `public_first_month_risks`
- Slice: `public`
- `langgraph`: status 200, latency 2859.7ms, quality `80`, reason `langgraph_public_canonical_lane:public_bundle.first_month_risks`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `crewai`: status 200, latency 265.5ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 163.8ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `llamaindex`: status 200, latency 187.9ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 215.7ms, quality `80`, reason `specialist_supervisor_preflight:first_month_risks`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.

### `Q208` Cruze regulamentos gerais, politica de avaliacao e orientacao ao estudante para explicar como disciplina, frequencia e recuperacao se influenciam.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 2484.2ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.conduct_frequency_recovery`, backend `none`, strategy `direct_answer`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `crewai`: status 200, latency 245.6ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Regulamentos gerais, politica de avaliacao e orientacao ao estudante se conectam assim: disciplina e convivio sustentam a rotina; frequencia minima e justificativas influenciam alerta academico; e recuperacao, segunda chamada e apoio pedagogico entram quando desempenho ou assiduidade exigem recomposicao.
- `python_functions`: status 200, latency 184.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `llamaindex`: status 200, latency 191.5ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `specialist_supervisor`: status 200, latency 118.2ms, quality `100`, reason `specialist_supervisor_preflight:conduct_frequency_recovery`, backend `none`, strategy `direct_answer`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.

### `Q209` No ensino medio, de que forma biblioteca e laboratorios aparecem como apoio ao estudo na base publica?

- Retrieval type: `public_section_aware`
- Slice: `public`
- `langgraph`: status 200, latency 2330.1ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `crewai`: status 200, latency 256.6ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Biblioteca e laboratorios aparecem como apoio ao estudo do ensino medio: a Biblioteca Aurora oferece consulta, emprestimo e estudo orientado; os laboratorios apoiam aulas praticas, pesquisa e projetos maker; e o contraturno conecta esses espacos a monitorias, cultura digital e projetos interdisciplinares.
- `python_functions`: status 200, latency 160.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `llamaindex`: status 200, latency 196.6ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 129.6ms, quality `100`, reason `specialist_supervisor_preflight:facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.

### `Q210` O que fica publico no calendario e no portal, e o que ja depende de autenticacao da familia?

- Retrieval type: `public_visibility_boundary`
- Slice: `public`
- `langgraph`: status 200, latency 5946.6ms, quality `100`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`, backend `qdrant_hybrid`, strategy `direct_answer`
  answer: No calendário público e no portal, você encontra os marcos institucionais e eventos coletivos da escola. Já os detalhes individuais de cada aluno, convites específicos, informações financeiras e acompanhamentos protegidos dependem de autenticação. Sempre que houver alguma mudança importante no calendário de avaliações, nós atualizamos o portal e comunicamos pelos canais oficiais.
- `crewai`: status 200, latency 22065.5ms, quality `88`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Olá! Pelo que entendi, você quer saber sobre o acesso às informações escolares. As informações financeiras e contratos estão disponíveis mediante autenticação no portal. No entanto, não encontrei detalhes específicos sobre o que é público no calendário ou em outras áreas do portal. Você gostaria de mais detalhes sobre o que é público ou sobre o calendário?
- `python_functions`: status 200, latency 165.2ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `llamaindex`: status 200, latency 198.9ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 5585.2ms, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`, backend `none`, strategy `direct_answer`
  answer: Geralmente, funciona assim:

**No calendário e portal públicos (sem autenticação):**
*   Eventos gerais da instituição (feriados, datas de reuniões de pais, eventos abertos à comunidade).
*   Notícias e comunicados amplos.
*   Informações de contato gerais da instituição.
*   Processos de matrícula e prazos.

**Com autenticação da família (login e senha):**
*   Informações específicas do aluno (notas, frequência, horários).
*   Comunicados individualizados para a família.
*   Dados financeiros (mensalidades, pagamentos).
*   Acesso a documentos pessoais ou formulários específicos.
*   Agendamentos personalizados (ex: horários de reunião com professores).

### `Q211` Conecte comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais ao longo do ano letivo.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 158.6ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `crewai`: status 200, latency 260.1ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais funcionam como um circuito unico: o portal publica cronogramas e ajustes, a escola reforca comunicados pelos canais oficiais, e estudo orientado ou acompanhamento adicional entram quando calendario, desempenho ou rotina pedem suporte mais proximo.
- `python_functions`: status 200, latency 159.3ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `llamaindex`: status 200, latency 128.0ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `specialist_supervisor`: status 200, latency 92.7ms, quality `100`, reason `specialist_supervisor_preflight:transversal_year_bundle`, backend `none`, strategy `direct_answer`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.

### `Q212` Entre meus filhos, quem esta mais vulneravel academicamente hoje? Me de um panorama curto.

- Retrieval type: `protected_structured_academic`
- Slice: `protected`
- `langgraph`: status 200, latency 194.1ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `crewai`: status 200, latency 329.6ms, quality `100`, reason `crewai_protected_identity_backstop`, backend `none`, strategy `None`
  answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.
- `python_functions`: status 200, latency 213.9ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 232.0ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 352.3ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4

### `Q213` Agora foque so na Ana e diga em quais componentes ela esta mais vulneravel.

- Retrieval type: `protected_structured_followup`
- Slice: `protected`
- `langgraph`: status 200, latency 309.4ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo academico de Ana Oliveira:
- Turma: 1o Ano A
- Serie atual: 1
Notas mais recentes:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
Frequencia:
- Biologia: 3 presencas, 1 atrasos, 0 faltas (10 min)
- Educacao Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- `crewai`: status 200, latency 21282.9ms, quality `100`, reason `crewai_protected_flow_timeout`, backend `none`, strategy `None`
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora sobre Ana Oliveira. Se quiser, me diga exatamente se voce quer notas, faltas, provas, documentacao, matricula ou financeiro.
- `python_functions`: status 200, latency 274.0ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  answer: Resumo academico de Ana Oliveira:
- Turma: 1o Ano A
- Serie atual: 1
Notas mais recentes:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
Frequencia:
- Biologia: 3 presencas, 1 atrasos, 0 faltas (10 min)
- Educacao Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- `llamaindex`: status 200, latency 297.8ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo academico de Ana Oliveira:
- Turma: 1o Ano A
- Serie atual: 1
Notas mais recentes:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
Frequencia:
- Biologia: 3 presencas, 1 atrasos, 0 faltas (10 min)
- Educacao Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- `specialist_supervisor`: status 200, latency 255.8ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary`, backend `none`, strategy `structured_tool`
  answer: Notas de Ana Oliveira:
- Historia: media parcial 7,3
- Fisica: media parcial 6,4
- Matematica: media parcial 7,4
- Portugues: media parcial 8,4

### `Q214` Quero um panorama financeiro da familia com boletos, atrasos e o que precisa ser feito agora.

- Retrieval type: `protected_structured_finance`
- Slice: `protected`
- `langgraph`: status 200, latency 170.6ms, quality `80`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Familia entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `crewai`: status 200, latency 302.9ms, quality `80`, reason `protected_shadow_unmatched_student_reference`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Que entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.
- `python_functions`: status 200, latency 183.1ms, quality `80`, reason `python_functions_native_structured:finance`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Familia entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `llamaindex`: status 200, latency 207.0ms, quality `80`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Familia entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `specialist_supervisor`: status 200, latency 215.9ms, quality `88`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### `Q215` Na documentacao da Ana, o que ainda esta pendente e qual e a acao recomendada agora?

- Retrieval type: `protected_structured_admin`
- Slice: `protected`
- `langgraph`: status 200, latency 245.9ms, quality `100`, reason `status administrativo autenticado exige service deterministico`, backend `none`, strategy `structured_tool`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
- `crewai`: status 200, latency 850.3ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Hoje Ana Oliveira ainda tem pendencias documentais em Documentacao escolar do aluno. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
- `python_functions`: status 200, latency 249.5ms, quality `100`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
- `llamaindex`: status 200, latency 266.3ms, quality `100`, reason `status administrativo autenticado exige service deterministico`, backend `none`, strategy `structured_tool`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
- `specialist_supervisor`: status 200, latency 262.7ms, quality `100`, reason `specialist_supervisor_tool_first:administrative_status`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira esta com pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.

### `Q216` Quais criterios o playbook interno usa para conduzir negociacao financeira com a familia?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 2592.6ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `crewai`: status 200, latency 993.3ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Protocolo interno para responsaveis com escopo parcial (Protocolo interno para responsaveis com escopo parcial): Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
- `python_functions`: status 200, latency 647.6ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `llamaindex`: status 200, latency 708.0ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.
- `specialist_supervisor`: status 200, latency 591.9ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

### `Q217` O manual interno do professor diz o que sobre registro de avaliacoes e comunicacao pedagogica?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 745.4ms, quality `80`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Roteiro interno de acolhimento do 6o ano (Rotina interna para acolhimento pedagogico.): No acolhimento do 6o ano, a escola prioriza ambientacao, apresentacao de rotinas, combinados de convivencia e acompanhamento da adaptacao nas primeiras semanas.

Fontes:
- Manual interno do professor (v1)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- Roteiro interno de acolhimento do 6o ano (v1)
- `crewai`: status 200, latency 984.0ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `python_functions`: status 200, latency 596.3ms, quality `80`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Roteiro interno de acolhimento do 6o ano (Rotina interna para acolhimento pedagogico.): No acolhimento do 6o ano, a escola prioriza ambientacao, apresentacao de rotinas, combinados de convivencia e acompanhamento da adaptacao nas primeiras semanas.

Fontes:
- Manual interno do professor (v1)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- Roteiro interno de acolhimento do 6o ano (v1)
- `llamaindex`: status 200, latency 739.8ms, quality `80`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Roteiro interno de acolhimento do 6o ano (Rotina interna para acolhimento pedagogico.): No acolhimento do 6o ano, a escola prioriza ambientacao, apresentacao de rotinas, combinados de convivencia e acompanhamento da adaptacao nas primeiras semanas.
- `specialist_supervisor`: status 200, latency 691.1ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Roteiro interno de acolhimento do 6o ano (Rotina interna para acolhimento pedagogico.): No acolhimento do 6o ano, a escola prioriza ambientacao, apresentacao de rotinas, combinados de convivencia e acompanhamento da adaptacao nas primeiras semanas.

### `Q218` No protocolo interno de escopo parcial, como ficam os limites de acesso no Telegram?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 784.2ms, quality `80`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `crewai`: status 200, latency 921.2ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
- `python_functions`: status 200, latency 664.4ms, quality `80`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `llamaindex`: status 200, latency 819.1ms, quality `80`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
- `specialist_supervisor`: status 200, latency 784.9ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.

### `Q219` Existe algum procedimento interno sobre excursao internacional com hospedagem para o ensino medio?

- Retrieval type: `restricted_doc_negative`
- Slice: `restricted`
- `langgraph`: status 200, latency 939.5ms, quality `80`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao > Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.
Playbook interno de negociacao financeira (Procedimento interno de atendimento financeiro.): Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.

Fontes:
- Procedimento interno para transferencia no meio do ano (v2026.3)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Playbook interno de negociacao financeira (v1)
- `crewai`: status 200, latency 820.9ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Manual interno do professor (Procedimento interno de registro academico docente.): Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Playbook interno de negociacao financeira (Procedimento interno de atendimento financeiro.): Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
- `python_functions`: status 200, latency 643.6ms, quality `80`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao > Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.
Playbook interno de negociacao financeira (Procedimento interno de atendimento financeiro.): Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.

Fontes:
- Procedimento interno para transferencia no meio do ano (v2026.3)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Playbook interno de negociacao financeira (v1)
- `llamaindex`: status 200, latency 821.8ms, quality `80`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Playbook interno de negociacao financeira (Procedimento interno de atendimento financeiro.): Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Manual interno do professor (Procedimento interno de registro academico docente.): Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `specialist_supervisor`: status 200, latency 827.5ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao > Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.
Playbook interno de negociacao financeira (Procedimento interno de atendimento financeiro.): Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.

### `Q220` Mostre o manual interno do professor para mim.

- Retrieval type: `restricted_doc_denied`
- Slice: `restricted`
- `langgraph`: status 200, latency 305.0ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `crewai`: status 200, latency 300.3ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 197.6ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 217.2ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 145.6ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

