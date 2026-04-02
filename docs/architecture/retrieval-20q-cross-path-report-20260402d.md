# Retrieval 20Q Cross-Path Report

Date: 2026-04-02T09:14:15.600496+00:00

Dataset: `tests/evals/datasets/retrieval_20q_probe_cases.generated.20260402b.json`

Run prefix: `debug:retrieval20:20260402T091043Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `20/20` | `18/20` | `97.4` | `2096.1 ms` |
| `crewai` | `20/20` | `8/20` | `87.4` | `2120.1 ms` |
| `python_functions` | `20/20` | `17/20` | `96.4` | `291.4 ms` |
| `llamaindex` | `20/20` | `14/20` | `93.4` | `516.2 ms` |
| `specialist_supervisor` | `20/20` | `16/20` | `96.0` | `5478.9 ms` |

## By Retrieval Type

- `protected_structured_academic`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 292.7ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 206.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 249.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 254.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 220.2ms
- `protected_structured_admin`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 214.1ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 200.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 239.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 232.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 186.5ms
- `protected_structured_finance`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 162.0ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 209.1ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 160.8ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 214.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 265.8ms
- `protected_structured_followup`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 8440.4ms
  - `crewai`: keyword pass 1/1, quality 88.0, latency 18748.8ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 1885.2ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 6383.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 36023.1ms
- `public_deep_multi_doc`
  - `langgraph`: keyword pass 2/2, quality 100.0, latency 131.4ms
  - `crewai`: keyword pass 1/2, quality 90.0, latency 182.6ms
  - `python_functions`: keyword pass 2/2, quality 100.0, latency 110.2ms
  - `llamaindex`: keyword pass 1/2, quality 90.0, latency 110.9ms
  - `specialist_supervisor`: keyword pass 2/2, quality 100.0, latency 63.8ms
- `public_documents_credentials`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 118.2ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 185.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 123.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 132.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 64.6ms
- `public_family_new_bundle`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2368.2ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 182.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 150.1ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 141.7ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 126.0ms
- `public_first_month_risks`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4126.9ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 157.5ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 106.1ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 123.2ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 123.5ms
- `public_permanence_support`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4613.8ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 190.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 150.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 67.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 86.6ms
- `public_policy_bridge`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 6647.4ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 264.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 156.4ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 174.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 175.0ms
- `public_process_compare`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2058.1ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 240.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 127.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 176.5ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 55494.4ms
- `public_section_aware`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2259.7ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 208.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 109.0ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 163.6ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 66.1ms
- `public_timeline`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4293.3ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 240.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 127.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 140.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 218.2ms
- `public_visibility_boundary`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4240.9ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 18132.7ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 118.7ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 74.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 14424.3ms
- `restricted_doc_denied`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 213.7ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 213.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 118.4ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 164.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 103.3ms
- `restricted_doc_negative`
  - `langgraph`: keyword pass 1/1, quality 88.0, latency 419.2ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 663.6ms
  - `python_functions`: keyword pass 1/1, quality 88.0, latency 406.6ms
  - `llamaindex`: keyword pass 1/1, quality 88.0, latency 480.2ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 482.7ms
- `restricted_doc_positive`
  - `langgraph`: keyword pass 3/3, quality 100.0, latency 396.6ms
  - `crewai`: keyword pass 0/3, quality 80.0, latency 663.7ms
  - `python_functions`: keyword pass 3/3, quality 100.0, latency 459.9ms
  - `llamaindex`: keyword pass 3/3, quality 100.0, latency 392.6ms
  - `specialist_supervisor`: keyword pass 3/3, quality 100.0, latency 463.5ms

## Failures

- `Q201` `crewai` `public_policy_bridge` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q204` `llamaindex` `public_family_new_bundle` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q204` `specialist_supervisor` `public_family_new_bundle` quality `80` mode `structured_tool` reason `specialist_supervisor_tool_first:public_timeline_bundle` errors `missing_expected_keyword`
- `Q206` `crewai` `public_process_compare` quality `80` mode `structured_tool` reason `workflow_not_found` errors `missing_expected_keyword`
- `Q206` `specialist_supervisor` `public_process_compare` quality `80` mode `clarify` reason `specialist_supervisor_grounding_gate:safe_clarify` errors `missing_expected_keyword`
- `Q207` `crewai` `public_first_month_risks` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q207` `python_functions` `public_first_month_risks` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q207` `llamaindex` `public_first_month_risks` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q207` `specialist_supervisor` `public_first_month_risks` quality `80` mode `structured_tool` reason `specialist_supervisor_fast_path:service_credentials_bundle` errors `missing_expected_keyword`
- `Q208` `crewai` `public_deep_multi_doc` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q208` `llamaindex` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q209` `crewai` `public_section_aware` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q209` `llamaindex` `public_section_aware` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q212` `crewai` `protected_structured_academic` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q213` `langgraph` `protected_structured_followup` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q213` `crewai` `protected_structured_followup` quality `88` mode `structured_tool` reason `crewai_protected_flow_completed` errors `unnecessary_clarification`
- `Q213` `python_functions` `protected_structured_followup` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q213` `llamaindex` `protected_structured_followup` quality `80` mode `structured_tool` reason `llamaindex_public_profile` errors `missing_expected_keyword`
- `Q214` `langgraph` `protected_structured_finance` quality `80` mode `structured_tool` reason `a solicitacao pode ser executada por workflow estruturado com protocolo` errors `missing_expected_keyword`
- `Q214` `crewai` `protected_structured_finance` quality `80` mode `structured_tool` reason `protected_shadow_needs_student_clarification` errors `missing_expected_keyword`
- `Q214` `python_functions` `protected_structured_finance` quality `80` mode `structured_tool` reason `python_functions_native_structured:support` errors `missing_expected_keyword`
- `Q214` `llamaindex` `protected_structured_finance` quality `80` mode `structured_tool` reason `a solicitacao pode ser executada por workflow estruturado com protocolo` errors `missing_expected_keyword`
- `Q215` `crewai` `protected_structured_admin` quality `80` mode `structured_tool` reason `protected_shadow_unmatched_student_reference` errors `missing_expected_keyword`
- `Q216` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q217` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q218` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q219` `langgraph` `restricted_doc_negative` quality `88` mode `hybrid_retrieval` reason `langgraph_restricted_document_no_match` errors `unnecessary_clarification`
- `Q219` `crewai` `restricted_doc_negative` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q219` `python_functions` `restricted_doc_negative` quality `88` mode `hybrid_retrieval` reason `python_functions_native_restricted_document_no_match` errors `unnecessary_clarification`
- `Q219` `llamaindex` `restricted_doc_negative` quality `88` mode `hybrid_retrieval` reason `llamaindex_restricted_doc_no_match` errors `unnecessary_clarification`
- `Q219` `specialist_supervisor` `restricted_doc_negative` quality `80` mode `hybrid_retrieval` reason `specialist_supervisor_tool_first:restricted_document_no_match` errors `missing_expected_keyword`

## Prompt Results

### `Q201` Se uma prova e perdida por motivo de saude, como atestado, segunda chamada e recuperacao aparecem conectados nos documentos publicos?

- Retrieval type: `public_policy_bridge`
- Slice: `public`
- `langgraph`: status 200, latency 6647.4ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.health_second_call`, backend `qdrant_hybrid`, strategy `direct_answer`
  answer: Olá! Se um aluno perde uma prova por motivo de saúde e apresenta um atestado, ele tem direito à segunda chamada. É importante que a justificativa seja entregue dentro do prazo estabelecido pela escola para que possamos analisar e organizar essa segunda oportunidade.
- `crewai`: status 200, latency 264.2ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 156.4ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 174.1ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 175.0ms, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`, backend `none`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### `Q202` No calendario publico de 2026, qual vem primeiro entre matricula, inicio das aulas e encontro inicial com responsaveis?

- Retrieval type: `public_timeline`
- Slice: `public`
- `langgraph`: status 200, latency 4293.3ms, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `crewai`: status 200, latency 240.1ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. | 2025-10-06 | familias interessadas | O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. | 2026-02-02 | alunos e familias | A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. | 2026-03-28 | responsaveis e familias | A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `python_functions`: status 200, latency 127.0ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `llamaindex`: status 200, latency 140.5ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `specialist_supervisor`: status 200, latency 218.2ms, quality `100`, reason `specialist_supervisor_tool_first:public_timeline_bundle`, backend `none`, strategy `structured_tool`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.

### `Q203` Quando perco a senha e ainda tenho documento para enviar, como devo organizar portal, credenciais e secretaria?

- Retrieval type: `public_documents_credentials`
- Slice: `public`
- `langgraph`: status 200, latency 118.2ms, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 185.6ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 123.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 132.4ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 64.6ms, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### `Q204` Para quem esta entrando este ano com o primeiro filho, como matricula, calendario e agenda de avaliacoes se amarram no comeco das aulas?

- Retrieval type: `public_family_new_bundle`
- Slice: `public`
- `langgraph`: status 200, latency 2368.2ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `crewai`: status 200, latency 182.6ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Para uma familia nova, matricula, calendario e agenda de avaliacoes precisam ser lidos juntos: a matricula organiza ingresso, documentos e atendimento inicial; o calendario mostra inicio das aulas, marcos do bimestre e reunioes com responsaveis; e a agenda de avaliacoes explica janelas de prova, recuperacao e comunicados pedagogicos do primeiro bimestre.
- `python_functions`: status 200, latency 150.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `llamaindex`: status 200, latency 141.7ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `specialist_supervisor`: status 200, latency 126.0ms, quality `80`, reason `specialist_supervisor_tool_first:public_timeline_bundle`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### `Q205` Quais apoios publicos evitam que a familia se perca ao acompanhar permanencia e vida escolar do estudante?

- Retrieval type: `public_permanence_support`
- Slice: `public`
- `langgraph`: status 200, latency 4613.8ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Que bom que você se preocupa em acompanhar de perto a vida escolar! Aqui no Colégio Horizonte, oferecemos uma combinação de orientações, monitorias e comunicação constante para que as famílias se sintam sempre seguras e informadas.

Nossa equipe de orientação pedagógica está sempre à disposição para ajudar na adaptação, rotina de estudos e desenvolvimento de bons hábitos. Além disso, temos monitorias agendadas e plantões de dúvidas para dar aquele suporte extra nas disciplinas.

Para manter a comunicação fluida, usamos comunicados digitais, reuniões periódicas e, se necessário, fazemos chamadas para um acompanhamento mais próximo. E claro, a frequência escolar é super importante e também é monitorada de perto. No Ensino Médio, o Projeto de Vida é um componente curricular e eixo de tutoria, oferecendo um apoio ainda mais completo.
- `crewai`: status 200, latency 190.8ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao educacional, monitorias, comunicados digitais, reunioes periodicas com responsaveis e acionamento de acompanhamento quando frequencia, adaptacao ou rotina de estudo exigem intervencao.
- `python_functions`: status 200, latency 150.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 67.2ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 86.6ms, quality `100`, reason `specialist_supervisor_preflight:permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### `Q206` Olhando prazos, protocolo e documentacao, como rematricula, transferencia e cancelamento se diferenciam na pratica?

- Retrieval type: `public_process_compare`
- Slice: `public`
- `langgraph`: status 200, latency 2058.1ms, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `crewai`: status 200, latency 240.6ms, quality `80`, reason `workflow_not_found`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao encontrei um protocolo ativo nesta conversa para retomar agora. Se voce quiser, eu posso abrir o pedido, te dizer o protocolo, consultar o status ou montar um resumo quando houver um fluxo ativo.
- `python_functions`: status 200, latency 127.0ms, quality `100`, reason `contextual_public_direct_answer`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 176.5ms, quality `100`, reason `contextual_public_direct_answer`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 55494.4ms, quality `80`, reason `specialist_supervisor_grounding_gate:safe_clarify`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword
  answer: Ainda nao consegui sustentar essa resposta com evidencias suficientes por aqui. Se quiser, reformule em uma frase mais direta ou me diga o assunto exato para eu buscar o canal certo.

### `Q207` Quais deslizes do primeiro mes mais viram problema com credenciais, documentos e rotina escolar?

- Retrieval type: `public_first_month_risks`
- Slice: `public`
- `langgraph`: status 200, latency 4126.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `direct_answer`
  answer: Olá! Para evitar problemas com credenciais, documentos e a rotina escolar no primeiro mês, é importante que a família veja a secretaria, os canais digitais e o suporte como um fluxo único. O envio de documentos pode ser feito pelo portal, e-mail da secretaria ou presencialmente, dependendo do tipo e da sensibilidade da informação.

É fundamental que cada usuário utilize suas próprias credenciais para acessar o portal, aplicativo e canais autenticados. Caso surjam problemas de acesso, esquecimento de senha ou inconsistências cadastrais, por favor, entre em contato com a secretaria ou o suporte institucional.
- `crewai`: status 200, latency 157.5ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 106.1ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 123.2ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 123.5ms, quality `80`, reason `specialist_supervisor_fast_path:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### `Q208` Usando os documentos publicos, explique como convivencia, frequencia e recuperacao passam a se influenciar quando o aluno entra em dificuldade.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 113.7ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.conduct_frequency_recovery`, backend `none`, strategy `structured_tool`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `crewai`: status 200, latency 183.7ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 106.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `llamaindex`: status 200, latency 146.8ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Os diferenciais pedagogicos mais claros aqui passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes.
- `specialist_supervisor`: status 200, latency 65.1ms, quality `100`, reason `specialist_supervisor_preflight:conduct_frequency_recovery`, backend `none`, strategy `direct_answer`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.

### `Q209` Na documentacao publica do ensino medio, como biblioteca, laboratorios e estudo orientado aparecem conectados como apoio academico?

- Retrieval type: `public_section_aware`
- Slice: `public`
- `langgraph`: status 200, latency 2259.7ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `crewai`: status 200, latency 208.2ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 109.0ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `llamaindex`: status 200, latency 163.6ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 66.1ms, quality `100`, reason `specialist_supervisor_preflight:facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.

### `Q210` Nos canais digitais da escola, o que ainda e publico e o que passa a depender da autenticacao da familia?

- Retrieval type: `public_visibility_boundary`
- Slice: `public`
- `langgraph`: status 200, latency 4240.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.visibility_boundary`, backend `none`, strategy `direct_answer`
  answer: Olá! No nosso calendário público, você sempre encontrará os marcos institucionais gerais e os eventos coletivos da escola. Já os detalhes individuais de cada aluno, convites direcionados, protocolos específicos, situações financeiras e acompanhamentos protegidos dependem de autenticação. Sempre que houver alguma atualização importante no calendário de avaliações, nós avisaremos no portal e reforçaremos a comunicação pelos nossos canais oficiais.
- `crewai`: status 200, latency 18132.7ms, quality `100`, reason `crewai_public_flow_completed`, backend `none`, strategy `None`
  answer: Os canais digitais da escola funcionam assim: o Site da Escola tem acesso público, ou seja, qualquer pessoa pode navegar. Já o Portal do Aluno e o Aplicativo da Escola são de acesso autenticado, o que significa que você precisa de um login para utilizá-los.
- `python_functions`: status 200, latency 118.7ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `llamaindex`: status 200, latency 74.9ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.visibility_boundary`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 14424.3ms, quality `100`, reason `specialist_supervisor_direct:institution_specialist`, backend `none`, strategy `structured_tool`
  answer: No Colégio Horizonte, os canais digitais operam com diferentes níveis de acesso para garantir a segurança e a privacidade das informações.

**O que é público e de acesso geral:**
*   Informações institucionais disponíveis no site oficial da escola e redes sociais, como o Instagram (@colegiohorizonte).
*   Canais de contato iniciais para admissões e dúvidas comerciais, como o bot, WhatsApp comercial e e-mails institucionais (secretaria@colegiohorizonte.edu.br, admissoes@colegiohorizonte.edu.br, etc.).
*   Agendamento de visitas institucionais.
*   O envio inicial de documentos para matrícula pode ser feito digitalmente através do portal institucional ou e-mail da secretaria, embora a validação final seja presencial.

**O que depende da autenticação da família:**
*   O portal institucional autenticado é necessário para acesso a informações financeiras, como boletos, vencimentos e contratos.
*   Envio de documentos completos ou dados sensíveis, onde o portal autenticado ou o e-mail institucional são os canais recomendados para maior segurança.
*   Serviços como reunião com a coordenação pedagógica e orientação educacional podem ser solicitados via portal (implicando acesso autenticado para detalhes específicos do aluno).
*   Suporte relacionado ao acesso ao portal escolar, senhas e dificuldades com atendimento digital.

**Importante:** O chat aberto e os canais públicos não devem ser usados para compartilhar documentos completos ou dados sensíveis.

### `Q211` Ao longo do ano letivo, como comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais passam a depender uns dos outros?

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 149.1ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `crewai`: status 200, latency 181.4ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais funcionam como um circuito unico: o portal publica cronogramas e ajustes, a escola reforca comunicados pelos canais oficiais, e estudo orientado ou acompanhamento adicional entram quando calendario, desempenho ou rotina pedem suporte mais proximo.
- `python_functions`: status 200, latency 114.3ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `llamaindex`: status 200, latency 74.9ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `specialist_supervisor`: status 200, latency 62.5ms, quality `100`, reason `specialist_supervisor_preflight:transversal_year_bundle`, backend `none`, strategy `direct_answer`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.

### `Q212` Faca um resumo academico dos meus dois filhos e destaque qual deles esta mais perto do corte de aprovacao.

- Retrieval type: `protected_structured_academic`
- Slice: `protected`
- `langgraph`: status 200, latency 292.7ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `crewai`: status 200, latency 206.6ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: A referencia publica de aprovacao hoje e media 7.0 na escala 0-10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico.
- `python_functions`: status 200, latency 249.1ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `llamaindex`: status 200, latency 254.4ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `specialist_supervisor`: status 200, latency 220.2ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4

### `Q213` Seguindo o panorama anterior, isole a Ana e diga onde ela aparece mais fragilizada academicamente.

- Retrieval type: `protected_structured_followup`
- Slice: `protected`
- `langgraph`: status 200, latency 8440.4ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Colegio Horizonte e uma escola laica. A proposta institucional e plural e nao confessional.
- `crewai`: status 200, latency 18748.8ms, quality `88`, reason `crewai_protected_flow_completed`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: As informações disponíveis não indicam fragilidade acadêmica para Ana Oliveira. Você gostaria de saber sobre o status administrativo ou financeiro, ou há alguma outra informação acadêmica específica que você procura?
- `python_functions`: status 200, latency 1885.2ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Colegio Horizonte e uma escola laica. A proposta institucional e plural e nao confessional.

Os indicadores publicos mais recentes de Colegio Horizonte sao:
- Aprovacao global: 96.4% (ano letivo 2025)
- Frequencia media: 97.1% (ano letivo 2025)
- Familias que avaliaram o atendimento como bom ou excelente: 92.0% (pesquisa institucional 2025)
- `llamaindex`: status 200, latency 6383.8ms, quality `80`, reason `llamaindex_public_profile`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Os indicadores publicos mais recentes de Colegio Horizonte sao:
- Aprovacao global: 96.4% (ano letivo 2025)
- Frequencia media: 97.1% (ano letivo 2025)
- Familias que avaliaram o atendimento como bom ou excelente: 92.0% (pesquisa institucional 2025)
- `specialist_supervisor`: status 200, latency 36023.1ms, quality `100`, reason `specialist_supervisor_manager_judge:academic:structured_tools`, backend `none`, strategy `structured_tool`
  answer: Ana Oliveira apresenta maior fragilidade acadêmica na disciplina de **Física**, com a menor média de notas (6.4). Outras áreas que merecem atenção devido a notas relativamente baixas e/ou faltas são Educação Física (média de 7.0), Geografia (média de 7.0 e uma falta de 50 minutos), e Redação (média de 7.1 e uma falta de 50 minutos). Além disso, Inglês e Português, apesar de notas satisfatórias, registraram os maiores tempos de ausência (75 e 65 minutos, respectivamente).

### `Q214` Me de um quadro financeiro da familia hoje, com o que venceu, o que esta por vencer e o proximo passo recomendado.

- Retrieval type: `protected_structured_finance`
- Slice: `protected`
- `langgraph`: status 200, latency 162.0ms, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `crewai`: status 200, latency 209.1ms, quality `80`, reason `protected_shadow_needs_student_clarification`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 160.8ms, quality `80`, reason `python_functions_native_structured:support`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 214.3ms, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `specialist_supervisor`: status 200, latency 265.8ms, quality `100`, reason `specialist_supervisor_resolved_intent:financial_summary_aggregate`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00

### `Q215` Na parte administrativa da Ana, quais pendencias documentais ainda restam e o que a familia deve fazer agora?

- Retrieval type: `protected_structured_admin`
- Slice: `protected`
- `langgraph`: status 200, latency 214.1ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
- `crewai`: status 200, latency 200.8ms, quality `80`, reason `protected_shadow_unmatched_student_reference`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Que entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.
- `python_functions`: status 200, latency 239.0ms, quality `100`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
- `llamaindex`: status 200, latency 232.5ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
- `specialist_supervisor`: status 200, latency 186.5ms, quality `100`, reason `specialist_supervisor_tool_first:administrative_status`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira esta com pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.

### `Q216` Pelo playbook interno de negociacao financeira, quais criterios a equipe usa para conduzir uma conversa com a familia?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 362.1ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao > Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- `crewai`: status 200, latency 621.9ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao > Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.
Protocolo interno para responsaveis com escopo parcial (Protocolo interno para responsaveis com escopo parcial): Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
- `python_functions`: status 200, latency 385.6ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao > Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- `llamaindex`: status 200, latency 414.3ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao > Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.
- `specialist_supervisor`: status 200, latency 470.9ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Documento principal: Playbook interno de negociacao financeira.
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao > Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.

### `Q217` Dentro do manual interno do professor, qual e a orientacao sobre registro de avaliacoes e comunicacao pedagogica?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 417.1ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

Fontes:
- Manual interno do professor (v1)
- `crewai`: status 200, latency 611.5ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `python_functions`: status 200, latency 595.8ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

Fontes:
- Manual interno do professor (v1)
- `llamaindex`: status 200, latency 348.5ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `specialist_supervisor`: status 200, latency 447.0ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Documento principal: Manual interno do professor.
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

### `Q218` Segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 410.7ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- `crewai`: status 200, latency 757.8ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Manual interno do professor (Procedimento interno de registro academico docente.): Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `python_functions`: status 200, latency 398.2ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- `llamaindex`: status 200, latency 414.9ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
- `specialist_supervisor`: status 200, latency 472.6ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Documento principal: Protocolo interno para responsaveis com escopo parcial.
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

### `Q219` Nos documentos internos, existe alguma orientacao especifica para excursao internacional com hospedagem no ensino medio?

- Retrieval type: `restricted_doc_negative`
- Slice: `restricted`
- `langgraph`: status 200, latency 419.2ms, quality `88`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  errors: unnecessary_clarification
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Nos documentos internos, existe alguma orientacao especifica para excursao internacional com hospedagem no ensino medio?". Se quiser, eu posso orientar pelo material publico correspondente ou encaminhar o caso para validacao humana.
- `crewai`: status 200, latency 663.6ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial.
Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
- `python_functions`: status 200, latency 406.6ms, quality `88`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: unnecessary_clarification
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Nos documentos internos, existe alguma orientacao especifica para excursao internacional com hospedagem no ensino medio?". Se quiser, eu posso orientar pelo material publico correspondente ou encaminhar o caso para validacao humana.
- `llamaindex`: status 200, latency 480.2ms, quality `88`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: unnecessary_clarification
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Nos documentos internos, existe alguma orientacao especifica para excursao internacional com hospedagem no ensino medio?". Se quiser, eu posso orientar pelo material publico correspondente ou encaminhar o caso para validacao humana.
- `specialist_supervisor`: status 200, latency 482.7ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para esse pedido. Se quiser, eu posso te orientar pelo material publico correspondente ou abrir um handoff para validacao humana.

### `Q220` Preciso que voce me mostre o manual interno do professor aqui no chat.

- Retrieval type: `restricted_doc_denied`
- Slice: `restricted`
- `langgraph`: status 200, latency 213.7ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `crewai`: status 200, latency 213.6ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 118.4ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 164.9ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 103.3ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

