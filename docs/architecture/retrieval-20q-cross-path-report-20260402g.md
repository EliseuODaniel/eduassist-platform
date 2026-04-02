# Retrieval 20Q Cross-Path Report

Date: 2026-04-02T12:49:39.661326+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_20q_probe_cases.generated.20260402g.json`

Run prefix: `debug:retrieval20:20260402T124528Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `20/20` | `15/20` | `95.0` | `1305.0 ms` |
| `crewai` | `20/20` | `6/20` | `84.2` | `2080.3 ms` |
| `python_functions` | `20/20` | `17/20` | `97.0` | `200.1 ms` |
| `llamaindex` | `20/20` | `17/20` | `97.0` | `1049.0 ms` |
| `specialist_supervisor` | `20/20` | `18/20` | `98.0` | `7841.1 ms` |

## By Retrieval Type

- `protected_structured_academic`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 243.3ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 205.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 225.3ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 232.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 210.1ms
- `protected_structured_admin`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 196.6ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 194.5ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 174.2ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 182.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 182.6ms
- `protected_structured_finance`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 220.6ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 199.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 203.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 231.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 202.7ms
- `protected_structured_followup`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 217.5ms
  - `crewai`: keyword pass 0/1, quality 55.0, latency 207.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 205.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 207.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 218.5ms
- `public_deep_multi_doc`
  - `langgraph`: keyword pass 0/2, quality 80.0, latency 155.0ms
  - `crewai`: keyword pass 0/2, quality 74.0, latency 10437.6ms
  - `python_functions`: keyword pass 0/2, quality 80.0, latency 186.8ms
  - `llamaindex`: keyword pass 0/2, quality 80.0, latency 8774.5ms
  - `specialist_supervisor`: keyword pass 1/2, quality 90.0, latency 43252.6ms
- `public_documents_credentials`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2134.7ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 163.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 198.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 70.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 66.6ms
- `public_family_new_bundle`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 109.5ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 186.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 109.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 70.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 47595.5ms
- `public_first_month_risks`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 2260.8ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 177.2ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 111.6ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 70.0ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 137.3ms
- `public_permanence_support`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4670.6ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 164.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 106.7ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 69.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 65.3ms
- `public_policy_bridge`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 183.7ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 194.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 127.3ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 68.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 131.8ms
- `public_process_compare`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2005.5ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 184.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 111.3ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 74.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 64.8ms
- `public_section_aware`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2204.4ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 181.4ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 113.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 70.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 61.7ms
- `public_timeline`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 3958.3ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 188.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 116.4ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 81.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 136.0ms
- `public_visibility_boundary`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 3775.8ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 178.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 107.7ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 85.6ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 19061.2ms
- `restricted_doc_denied`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 183.7ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 205.4ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 123.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 150.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 122.7ms
- `restricted_doc_negative`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 420.6ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 588.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 459.4ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 446.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 480.7ms
- `restricted_doc_positive`
  - `langgraph`: keyword pass 3/3, quality 100.0, latency 1001.8ms
  - `crewai`: keyword pass 0/3, quality 80.0, latency 5837.0ms
  - `python_functions`: keyword pass 3/3, quality 100.0, latency 378.6ms
  - `llamaindex`: keyword pass 3/3, quality 100.0, latency 440.3ms
  - `specialist_supervisor`: keyword pass 3/3, quality 100.0, latency 526.6ms

## Failures

- `Q201` `crewai` `public_policy_bridge` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q204` `crewai` `public_family_new_bundle` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q206` `crewai` `public_process_compare` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q207` `langgraph` `public_first_month_risks` quality `80` mode `structured_tool` reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials` errors `missing_expected_keyword`
- `Q207` `crewai` `public_first_month_risks` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q207` `python_functions` `public_first_month_risks` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q207` `llamaindex` `public_first_month_risks` quality `80` mode `structured_tool` reason `llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials` errors `missing_expected_keyword`
- `Q207` `specialist_supervisor` `public_first_month_risks` quality `80` mode `structured_tool` reason `specialist_supervisor_fast_path:service_credentials_bundle` errors `missing_expected_keyword`
- `Q208` `langgraph` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` errors `missing_expected_keyword`
- `Q208` `crewai` `public_deep_multi_doc` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q208` `python_functions` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q208` `llamaindex` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q210` `langgraph` `public_visibility_boundary` quality `80` mode `structured_tool` reason `langgraph_public_canonical_lane:public_bundle.visibility_boundary` errors `missing_expected_keyword`
- `Q210` `crewai` `public_visibility_boundary` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q211` `langgraph` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` errors `missing_expected_keyword`
- `Q211` `crewai` `public_deep_multi_doc` quality `68` mode `structured_tool` reason `crewai_public_flow_timeout` errors `missing_expected_keyword, unnecessary_clarification`
- `Q211` `python_functions` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `python_functions_native_structured:institution` errors `missing_expected_keyword`
- `Q211` `llamaindex` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q211` `specialist_supervisor` `public_deep_multi_doc` quality `80` mode `clarify` reason `specialist_supervisor_strict_safe_fallback` errors `missing_expected_keyword`
- `Q213` `crewai` `protected_structured_followup` quality `55` mode `structured_tool` reason `crewai_protected_identity_backstop` errors `forbidden_entity_or_value`
- `Q214` `crewai` `protected_structured_finance` quality `80` mode `structured_tool` reason `protected_shadow_needs_student_clarification` errors `missing_expected_keyword`
- `Q215` `langgraph` `protected_structured_admin` quality `80` mode `structured_tool` reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` errors `missing_expected_keyword`
- `Q215` `crewai` `protected_structured_admin` quality `80` mode `structured_tool` reason `crewai_protected_identity_backstop` errors `missing_expected_keyword`
- `Q216` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `crewai_protected_flow_completed` errors `missing_expected_keyword`
- `Q217` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `protected_shadow_unmatched_student_reference` errors `missing_expected_keyword`
- `Q218` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q219` `crewai` `restricted_doc_negative` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`

## Prompt Results

### `Q201` Se o aluno perde uma prova por razao de saude, como a escola amarra comprovacao, segunda chamada e recuperacao no material publico?

- Retrieval type: `public_policy_bridge`
- Slice: `public`
- `langgraph`: status 200, latency 183.7ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.health_second_call`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `crewai`: status 200, latency 194.9ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 127.3ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 68.0ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.health_second_call`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 131.8ms, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`, backend `none`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### `Q202` Se eu olhar so a linha do tempo publica de 2026, como se distribuem matricula, inicio das aulas e reuniao inicial com as familias?

- Retrieval type: `public_timeline`
- Slice: `public`
- `langgraph`: status 200, latency 3958.3ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.timeline_lifecycle`, backend `none`, strategy `direct_answer`
  answer: Olá! Para 2026, o ciclo de matrículas públicas do Colégio Horizonte começa em 6 de outubro de 2025, com pré-cadastro e visita guiada. As aulas para o Ensino Fundamental II e Médio iniciam em 2 de fevereiro de 2026, e as reuniões gerais com os responsáveis estão agendadas para 28 de março, 27 de junho, 19 de setembro e 12 de dezembro.
- `crewai`: status 200, latency 188.0ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. | 2025-10-06 | familias interessadas | O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. | 2026-02-02 | alunos e familias | A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. | 2026-03-28 | responsaveis e familias | A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `python_functions`: status 200, latency 116.4ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `llamaindex`: status 200, latency 81.8ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.timeline_lifecycle`, backend `none`, strategy `structured_tool`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `specialist_supervisor`: status 200, latency 136.0ms, quality `100`, reason `specialist_supervisor_tool_first:public_timeline_bundle`, backend `none`, strategy `structured_tool`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.

### `Q203` Quando o problema e acesso mais entrega de documentos ao mesmo tempo, como portal, credenciais e secretaria entram na ordem correta?

- Retrieval type: `public_documents_credentials`
- Slice: `public`
- `langgraph`: status 200, latency 2134.7ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `direct_answer`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `crewai`: status 200, latency 163.8ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 198.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 70.0ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `specialist_supervisor`: status 200, latency 66.6ms, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### `Q204` Estamos fazendo a primeira matricula da familia: como calendario, agenda de avaliacoes e processo de ingresso se organizam no primeiro bimestre?

- Retrieval type: `public_family_new_bundle`
- Slice: `public`
- `langgraph`: status 200, latency 109.5ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `crewai`: status 200, latency 186.2ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: A mensalidade de referencia para Ensino Fundamental II e R$ 1280.00, com taxa de matricula de R$ 350.00.
- `python_functions`: status 200, latency 109.9ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `llamaindex`: status 200, latency 70.8ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `specialist_supervisor`: status 200, latency 47595.5ms, quality `100`, reason `specialist_supervisor_manager_judge:institution:structured_tools`, backend `none`, strategy `structured_tool`
  answer: Para a primeira matrícula de sua família no Colégio Horizonte, o primeiro bimestre (aproximadamente de fevereiro a maio) se organiza da seguinte forma:

**Calendário e Agenda de Avaliações (Primeiro Bimestre - 2026):**
*   O ano letivo para o Ensino Fundamental II e Ensino Médio inicia em **2 de fevereiro de 2026**.
*   A primeira reunião geral com pais e responsáveis para a apresentação do planejamento do primeiro bimestre ocorrerá em **28 de março de 2026**. Haverá reuniões específicas para o Ensino Fundamental II (também em 28 de março) e para o Ensino Médio (29 de março).
*   Para esclarecimentos sobre notas e frequência, haverá um **Plantão Pedagógico do primeiro bimestre em 11 de abril de 2026**.
*   Eventos como a Mostra de Ciências e Tecnologia estão previstos para **16 e 23 de maio de 2026**.
*   Datas específicas de avaliações (provas, trabalhos) não estão detalhadas no calendário público, mas são comunicadas internamente durante o planejamento do bimestre.

**Processo de Ingresso (Matrícula):**
*   O ciclo público de matrícula para 2026 foi aberto em **6 de outubro de 2025**, incluindo pré-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial continua enquanto houver vagas.
*   O processo de matrícula envolve análise documental, entrevista de acolhimento e assinatura contratual.
*   Os documentos necessários para a matrícula são: formulário cadastral preenchido, documento de identificação do aluno, CPF do aluno (se houver), histórico escolar, comprovante de residência atualizado e documento de identificação do responsável legal.
*   O envio inicial de documentos pode ser feito digitalmente (portal institucional ou e-mail da secretaria), mas a validação final ocorre presencialmente na secretaria.
*   A escola oferece atendimento comercial para visitas, apresentação pedagógica e simulação financeira, além de possíveis descontos para irmãos e campanhas de matrícula antecipada. Você pode agendar uma visita guiada para famílias interessadas em **6 de abril de 2026**.
*   Para informações sobre bolsas e descontos, haverá uma oficina aberta em **18 de abril de 2026**.

Para mais informações ou agendamento de visita, você pode contatar a equipe de Admissões pelo telefone (11) 3333-4201 ou e-mail admissoes@colegiohorizonte.edu.br.

### `Q205` Que trilha publica a familia encontra para acompanhar apoio ao estudante, permanencia e vida escolar sem depender de acesso privado?

- Retrieval type: `public_permanence_support`
- Slice: `public`
- `langgraph`: status 200, latency 4670.6ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Que bom que você se preocupa em acompanhar de perto a vida escolar! Aqui no Colégio Horizonte, oferecemos várias formas para a família acompanhar o apoio ao estudante, a permanência e a vida escolar, mesmo sem precisar de acesso privado.

Nossa equipe de orientação pedagógica está sempre atenta à adaptação, rotina de estudos e desenvolvimento de hábitos de aprendizagem. Além disso, temos monitorias agendadas e plantões de dúvidas para dar aquele suporte extra nas disciplinas.

Para manter todos informados, usamos comunicados digitais, reuniões periódicas e, se necessário, fazemos chamadas de acompanhamento. E lembre-se que a frequência mínima é super importante para o desempenho do estudante. No Ensino Médio, ainda temos o Projeto de Vida, que é um componente curricular e um eixo de tutoria para os alunos.
- `crewai`: status 200, latency 164.3ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao educacional, monitorias, comunicados digitais, reunioes periodicas com responsaveis e acionamento de acompanhamento quando frequencia, adaptacao ou rotina de estudo exigem intervencao.
- `python_functions`: status 200, latency 106.7ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 69.1ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 65.3ms, quality `100`, reason `specialist_supervisor_preflight:permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### `Q206` Na pratica, o que muda entre rematricula, transferencia de entrada e cancelamento quando olho prazos e documentos?

- Retrieval type: `public_process_compare`
- Slice: `public`
- `langgraph`: status 200, latency 2005.5ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.process_compare`, backend `none`, strategy `direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `crewai`: status 200, latency 184.1ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 111.3ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 74.4ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.process_compare`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 64.8ms, quality `100`, reason `specialist_supervisor_preflight:process_compare`, backend `none`, strategy `direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### `Q207` Se a familia se enrola no inicio do ano, quais erros mais costumam virar problema de login, documentacao e rotina escolar?

- Retrieval type: `public_first_month_risks`
- Slice: `public`
- `langgraph`: status 200, latency 2260.8ms, quality `80`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `crewai`: status 200, latency 177.2ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 111.6ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 70.0ms, quality `80`, reason `llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `specialist_supervisor`: status 200, latency 137.3ms, quality `80`, reason `specialist_supervisor_fast_path:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### `Q208` Quero uma sintese publica de como disciplina, faltas e recuperacao se cruzam quando o desempenho do aluno cai.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 153.7ms, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 178.2ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 126.2ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 143.9ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 11436.0ms, quality `100`, reason `specialist_supervisor_direct:academic_specialist`, backend `none`, strategy `structured_tool`
  answer: No Colégio Horizonte, a política acadêmica estabelece que, em casos de queda de desempenho, o cruzamento entre frequência e recuperação é gerenciado da seguinte forma:

*   **Faltas (Frequência):** Se a frequência de um estudante em qualquer componente curricular cair abaixo de 75%, ele entra em alerta acadêmico. Nesses casos, a coordenação pedagógica pode acionar a família para acompanhamento e, se a frequência permanecer abaixo desse limite, a aprovação por frequência pode ser comprometida. A escola acompanha justificativas e pode propor planos de recomposição.

*   **Recuperação:** Quando a média de um estudante fica abaixo da referência de aprovação (7.0), a escola oferece suporte de recuperação. Este suporte inclui monitorias, plantões e orientações específicas, seguindo o calendário pedagógico.

É importante notar que a política pública fornecida não detalha especificamente como a 'disciplina' em si, no sentido comportamental, se cruza com a queda de desempenho do aluno nas políticas de recuperação ou frequência, mas foca nas dimensões de assiduidade e rendimento acadêmico.

### `Q209` Como biblioteca e laboratorios entram nas regras de uso e no apoio ao estudo do ensino medio?

- Retrieval type: `public_section_aware`
- Slice: `public`
- `langgraph`: status 200, latency 2204.4ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `crewai`: status 200, latency 181.4ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Biblioteca e laboratorios aparecem como apoio ao estudo do ensino medio: a Biblioteca Aurora oferece consulta, emprestimo e estudo orientado; os laboratorios apoiam aulas praticas, pesquisa e projetos maker; e o contraturno conecta esses espacos a monitorias, cultura digital e projetos interdisciplinares.
- `python_functions`: status 200, latency 113.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `llamaindex`: status 200, latency 70.3ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `specialist_supervisor`: status 200, latency 61.7ms, quality `100`, reason `specialist_supervisor_preflight:facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.

### `Q210` Qual e a fronteira entre o que a escola publica no calendario/portal e o que exige autenticacao?

- Retrieval type: `public_visibility_boundary`
- Slice: `public`
- `langgraph`: status 200, latency 3775.8ms, quality `80`, reason `langgraph_public_canonical_lane:public_bundle.visibility_boundary`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Olá! No nosso calendário e portal, você encontra os marcos institucionais gerais e eventos coletivos. Já os detalhes individuais de cada aluno, convites específicos, informações financeiras e acompanhamentos protegidos exigem autenticação. Sempre que houver alguma mudança importante no calendário de avaliações, nós atualizamos o portal e reforçamos a comunicação pelos nossos canais oficiais.
- `crewai`: status 200, latency 178.9ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo. Colegio Horizonte em Sao Paulo/SP. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `python_functions`: status 200, latency 107.7ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `llamaindex`: status 200, latency 85.6ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.visibility_boundary`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos gerais como Visita guiada para familias interessadas, Plantao pedagogico do primeiro bimestre, Oficina aberta sobre bolsas e descontos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 19061.2ms, quality `100`, reason `specialist_supervisor_direct:institution_specialist`, backend `qdrant_hybrid`, strategy `document_search`
  answer: A fronteira entre o que a escola publica no calendário/portal e o que exige autenticação pode ser compreendida da seguinte forma:

**Informações Públicas (disponíveis no portal e calendário sem autenticação):**

*   **Perfil Institucional:** Nome da escola, endereço, site, modelo educacional, currículo, segmentos, horários de turno, valores de mensalidade de referência, canais de contato gerais, infraestrutura (biblioteca, laboratório, quadra), destaques e indicadores de desempenho público.
*   **Agenda e Eventos:** Calendário acadêmico com o início do ano letivo, reuniões gerais de pais, formaturas, visitas guiadas, plantões pedagógicos públicos, oficinas abertas sobre bolsas e descontos, mostras de ciências e tecnologia, feiras de orientação acadêmica e vocacional, e festivais esportivos.
*   **Serviços Gerais:** Descrição de serviços como atendimento comercial (matrículas, visitas), secretaria escolar para orientações administrativas gerais, e suporte para acesso e dúvidas sobre o portal.
*   **Corpo Diretivo:** Nomes e títulos dos membros da equipe de liderança.
*   **Política de Submissão de Documentos:** Orientações gerais sobre o envio de documentos, indicando que o chat aberto não deve receber documentos completos ou dados sensíveis, e que o portal autenticado ou e-mail institucional são os canais recomendados para tais envios.

**Informações que Exigem Autenticação (acessíveis via portal autenticado ou canais seguros):**

*   **Serviços Específicos:** Interações que envolvem dados pessoais do estudante, informações financeiras detalhadas, ou submissão de documentos sensíveis, como:
    *   **Secretaria Escolar e Documentos:** Para solicitação de declarações, histórico, transferência, comprovantes e orientações administrativas que envolvam dados específicos do aluno.
    *   **Financeiro Escolar e Contratos:** Para consulta de boletos, vencimentos, contratos e acordos financeiros.
    *   **Acompanhamento Individual:** Reuniões com coordenação pedagógica e orientação educacional que tratem do desempenho ou bem-estar específico de um estudante.
    *   **Envio de Documentos:** Para o processo de matrícula, o envio de formulários cadastrais preenchidos, documentos de identificação, histórico escolar e comprovantes de residência é feito preferencialmente pelo portal autenticado ou e-mail institucional.

Em resumo, o portal e calendário públicos oferecem uma visão abrangente da escola e de suas atividades gerais, enquanto o portal autenticado é o canal para interações personalizadas e acesso a dados e serviços que exigem a identificação do usuário, garantindo a segurança e a privacidade das informações. A escola orienta o uso do portal autenticado ou e-mail institucional para o envio de documentos completos e dados sensíveis.

### `Q211` Explique de forma transversal como provas, estudo orientado, comunicados digitais e relacionamento com responsaveis se encadeiam ao longo do ano.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 156.3ms, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 20697.0ms, quality `68`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Os documentos disponíveis abordam principalmente a comunicação com os responsáveis e como acompanhar comunicados. Você gostaria de focar nesses aspectos ou busca uma explicação mais detalhada sobre a interconexão de provas e estudo orientado com os demais itens?
- `python_functions`: status 200, latency 247.5ms, quality `80`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje o Colegio Horizonte divulga atividades complementares no contraturno de forma assim: - Ensino Fundamental II: Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados. - Ensino Medio: Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00. - Fundamental II e Ensino Medio: Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno. Entre as ofertas que aparecem com mais clareza hoje estao Biblioteca Aurora, Oficina de danca e expressao corporal, Oficina de teatro, Futsal e treinos esportivos, Volei escolar, Espaco Maker.
- `llamaindex`: status 200, latency 17405.0ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje o Colegio Horizonte divulga atividades complementares no contraturno de forma assim: - Ensino Fundamental II: Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados. - Ensino Medio: Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00. - Fundamental II e Ensino Medio: Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno. Entre as ofertas que aparecem com mais clareza hoje estao Biblioteca Aurora, Oficina de danca e expressao corporal, Oficina de teatro, Futsal e treinos esportivos, Volei escolar, Espaco Maker.
- `specialist_supervisor`: status 200, latency 75069.2ms, quality `80`, reason `specialist_supervisor_strict_safe_fallback`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### `Q212` Me de um panorama academico dos meus filhos e diga qual deles aparece mais perto da media minima agora.

- Retrieval type: `protected_structured_academic`
- Slice: `protected`
- `langgraph`: status 200, latency 243.3ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `crewai`: status 200, latency 205.6ms, quality `100`, reason `crewai_protected_identity_backstop`, backend `none`, strategy `None`
  answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.
- `python_functions`: status 200, latency 225.3ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `llamaindex`: status 200, latency 232.4ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `specialist_supervisor`: status 200, latency 210.1ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4

### `Q213` Depois do panorama dos meus filhos, fique apenas com a Ana e diga quais componentes merecem mais atencao agora.

- Retrieval type: `protected_structured_followup`
- Slice: `protected`
- `langgraph`: status 200, latency 217.5ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
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
- `crewai`: status 200, latency 207.3ms, quality `55`, reason `crewai_protected_identity_backstop`, backend `none`, strategy `None`
  errors: forbidden_entity_or_value
  answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.
- `python_functions`: status 200, latency 205.5ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
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
- `llamaindex`: status 200, latency 207.2ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
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
- `specialist_supervisor`: status 200, latency 218.5ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary`, backend `none`, strategy `structured_tool`
  answer: Notas de Ana Oliveira:
- Historia: media parcial 7,3
- Fisica: media parcial 6,4
- Matematica: media parcial 7,4
- Portugues: media parcial 8,4

### `Q214` Como esta o financeiro da familia hoje, incluindo vencimentos e proximos passos. Responda de forma direta.

- Retrieval type: `protected_structured_finance`
- Slice: `protected`
- `langgraph`: status 200, latency 220.6ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `crewai`: status 200, latency 199.2ms, quality `80`, reason `protected_shadow_needs_student_clarification`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 203.0ms, quality `100`, reason `python_functions_native_structured:finance`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `llamaindex`: status 200, latency 231.8ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `specialist_supervisor`: status 200, latency 202.7ms, quality `100`, reason `specialist_supervisor_resolved_intent:financial_summary_aggregate`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00

### `Q215` No cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?

- Retrieval type: `protected_structured_admin`
- Slice: `protected`
- `langgraph`: status 200, latency 196.6ms, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Resumo financeiro de Ana Oliveira:
- Contrato: CTR-2026-002
- Responsavel financeiro: Maria Oliveira
- Mensalidade base: 1450.00
- Faturas em aberto: 2
- Faturas vencidas: 0
Faturas em aberto ou vencidas:
- 2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- 2026-04: vencimento 2026-04-10, status em aberto, valor 1450.00
- `crewai`: status 200, latency 194.5ms, quality `80`, reason `crewai_protected_identity_backstop`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Para atualizar seu cadastro, o caminho mais seguro e revisar os dados no portal e, se precisar de alteracao assistida, falar com a secretaria. Se quiser, eu posso te orientar sobre qual dado voce precisa ajustar primeiro.
- `python_functions`: status 200, latency 174.2ms, quality `100`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- Matricula: MAT-2026-002
- Responsavel vinculado: Maria Oliveira
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
- `llamaindex`: status 200, latency 182.2ms, quality `100`, reason `status administrativo autenticado exige service deterministico`, backend `none`, strategy `structured_tool`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- Matricula: MAT-2026-002
- Responsavel vinculado: Maria Oliveira
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
- `specialist_supervisor`: status 200, latency 182.6ms, quality `100`, reason `specialist_supervisor_tool_first:administrative_status`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira esta com pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.

### `Q216` No material interno de negociacao financeira, quais criterios orientam a conversa da escola com a familia. Seja objetivo e grounded.

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 2037.3ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- `crewai`: status 200, latency 16549.1ms, quality `80`, reason `crewai_protected_flow_completed`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Não encontrei informações sobre os critérios de negociação financeira nos documentos disponíveis.
- `python_functions`: status 200, latency 340.4ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- `llamaindex`: status 200, latency 411.5ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
- `specialist_supervisor`: status 200, latency 511.4ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Documento principal: Playbook interno de negociacao financeira.
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

### `Q217` Pensando no caso pratico, no material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 510.7ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

Fontes:
- Manual interno do professor (v1)
- `crewai`: status 200, latency 383.2ms, quality `80`, reason `protected_shadow_unmatched_student_reference`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Comunicacao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.
- `python_functions`: status 200, latency 382.5ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

Fontes:
- Manual interno do professor (v1)
- `llamaindex`: status 200, latency 423.1ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `specialist_supervisor`: status 200, latency 556.6ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Documento principal: Manual interno do professor.
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

### `Q218` De forma bem objetiva, no protocolo interno de escopo parcial, como ficam os limites de acesso no Telegram?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 457.3ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- `crewai`: status 200, latency 578.8ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao > Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
- `python_functions`: status 200, latency 412.8ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- `llamaindex`: status 200, latency 486.3ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
- `specialist_supervisor`: status 200, latency 511.7ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Documento principal: Protocolo interno para responsaveis com escopo parcial.
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

### `Q219` Os documentos internos mencionam algum protocolo para excursao internacional com pernoite no ensino medio?

- Retrieval type: `restricted_doc_negative`
- Slice: `restricted`
- `langgraph`: status 200, latency 420.6ms, quality `100`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `crewai`: status 200, latency 588.0ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
- `python_functions`: status 200, latency 459.4ms, quality `100`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `llamaindex`: status 200, latency 446.2ms, quality `100`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `specialist_supervisor`: status 200, latency 480.7ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.

### `Q220` Preciso que voce me mostre o manual interno do professor aqui no chat. Traga a resposta de forma concreta.

- Retrieval type: `restricted_doc_denied`
- Slice: `restricted`
- `langgraph`: status 200, latency 183.7ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `crewai`: status 200, latency 205.4ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 123.1ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 150.4ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 122.7ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

