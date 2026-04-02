# Retrieval 20Q Cross-Path Report

Date: 2026-04-02T08:27:32.827612+00:00

Dataset: `tests/evals/datasets/retrieval_20q_probe_cases.generated.20260404.json`

Run prefix: `debug:retrieval20:20260402T082220Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `20/20` | `12/20` | `92.0` | `1992.5 ms` |
| `crewai` | `20/20` | `10/20` | `89.4` | `3362.5 ms` |
| `python_functions` | `20/20` | `11/20` | `90.4` | `205.4 ms` |
| `llamaindex` | `20/20` | `8/20` | `86.2` | `3321.0 ms` |
| `specialist_supervisor` | `19/20` | `15/20` | `90.4` | `6643.2 ms` |

## By Retrieval Type

- `protected_structured_academic`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 3754.7ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 212.5ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 181.2ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 35924.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 19221.1ms
- `protected_structured_admin`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 172.0ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 459.2ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 175.5ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 207.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 217.4ms
- `protected_structured_finance`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 152.1ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 196.6ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 137.0ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 161.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 88.0, latency 142.7ms
- `protected_structured_followup`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 3895.9ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 20808.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 236.6ms
  - `llamaindex`: keyword pass 0/1, quality 55.0, latency 2209.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 195.2ms
- `public_deep_multi_doc`
  - `langgraph`: keyword pass 2/2, quality 100.0, latency 1300.5ms
  - `crewai`: keyword pass 1/2, quality 90.0, latency 193.4ms
  - `python_functions`: keyword pass 2/2, quality 100.0, latency 136.8ms
  - `llamaindex`: keyword pass 1/2, quality 90.0, latency 118.5ms
  - `specialist_supervisor`: keyword pass 2/2, quality 100.0, latency 71.7ms
- `public_documents_credentials`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 1826.5ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 182.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 116.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 140.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 66.7ms
- `public_family_new_bundle`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 6169.2ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 188.3ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 146.4ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 138.7ms
  - `specialist_supervisor`: keyword pass 0/1, quality 0.0, latency 60061.1ms
- `public_first_month_risks`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 2396.9ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 185.8ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 127.7ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 147.3ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 151.7ms
- `public_permanence_support`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2212.4ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 231.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 123.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 81.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 70.8ms
- `public_policy_bridge`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 3902.9ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 270.9ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 135.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 142.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 147.8ms
- `public_process_compare`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2100.2ms
  - `crewai`: keyword pass 1/1, quality 88.0, latency 20591.5ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 118.1ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 144.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 37416.4ms
- `public_section_aware`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2334.8ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 185.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 140.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 87.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 76.1ms
- `public_timeline`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4235.3ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 206.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 134.1ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 149.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 140.9ms
- `public_visibility_boundary`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2092.6ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 20273.4ms
  - `python_functions`: keyword pass 0/1, quality 68.0, latency 199.1ms
  - `llamaindex`: keyword pass 0/1, quality 68.0, latency 24620.7ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 12569.4ms
- `restricted_doc_denied`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 215.9ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 211.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 129.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 163.7ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 132.9ms
- `restricted_doc_negative`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 461.6ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 696.9ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 428.9ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 428.6ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 521.1ms
- `restricted_doc_positive`
  - `langgraph`: keyword pass 1/3, quality 86.7, latency 441.9ms
  - `crewai`: keyword pass 1/3, quality 86.7, latency 654.2ms
  - `python_functions`: keyword pass 1/3, quality 86.7, latency 434.5ms
  - `llamaindex`: keyword pass 1/3, quality 86.7, latency 479.1ms
  - `specialist_supervisor`: keyword pass 1/3, quality 86.7, latency 529.5ms

## Failures

- `Q201` `crewai` `public_policy_bridge` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q202` `llamaindex` `public_timeline` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q204` `crewai` `public_family_new_bundle` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q204` `python_functions` `public_family_new_bundle` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q204` `llamaindex` `public_family_new_bundle` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q204` `specialist_supervisor` `public_family_new_bundle` quality `0` mode `error` reason `TimeoutError: ` errors `request_failed`
- `Q206` `crewai` `public_process_compare` quality `88` mode `structured_tool` reason `crewai_public_flow_timeout` errors `unnecessary_clarification`
- `Q207` `langgraph` `public_first_month_risks` quality `80` mode `structured_tool` reason `langgraph_public_canonical_lane:public_bundle.first_month_risks` errors `missing_expected_keyword`
- `Q207` `crewai` `public_first_month_risks` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q207` `python_functions` `public_first_month_risks` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q207` `llamaindex` `public_first_month_risks` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q207` `specialist_supervisor` `public_first_month_risks` quality `80` mode `structured_tool` reason `specialist_supervisor_fast_path:service_credentials_bundle` errors `missing_expected_keyword`
- `Q208` `llamaindex` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q210` `crewai` `public_visibility_boundary` quality `80` mode `structured_tool` reason `crewai_public_flow_timeout` errors `missing_expected_keyword`
- `Q210` `python_functions` `public_visibility_boundary` quality `68` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, unnecessary_clarification`
- `Q210` `llamaindex` `public_visibility_boundary` quality `68` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, unnecessary_clarification`
- `Q211` `crewai` `public_deep_multi_doc` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q212` `langgraph` `protected_structured_academic` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q212` `crewai` `protected_structured_academic` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q212` `python_functions` `protected_structured_academic` quality `80` mode `structured_tool` reason `python_functions_native_structured:institution` errors `missing_expected_keyword`
- `Q212` `llamaindex` `protected_structured_academic` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q213` `langgraph` `protected_structured_followup` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q213` `llamaindex` `protected_structured_followup` quality `55` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `forbidden_entity_or_value`
- `Q214` `langgraph` `protected_structured_finance` quality `80` mode `structured_tool` reason `dados estruturados devem passar por service deterministico` errors `missing_expected_keyword`
- `Q214` `crewai` `protected_structured_finance` quality `80` mode `structured_tool` reason `protected_shadow_needs_student_clarification` errors `missing_expected_keyword`
- `Q214` `python_functions` `protected_structured_finance` quality `80` mode `structured_tool` reason `python_functions_native_structured:finance` errors `missing_expected_keyword`
- `Q214` `llamaindex` `protected_structured_finance` quality `80` mode `structured_tool` reason `dados estruturados devem passar por service deterministico` errors `missing_expected_keyword`
- `Q214` `specialist_supervisor` `protected_structured_finance` quality `88` mode `clarify` reason `specialist_supervisor_resolved_intent:finance_student_clarify` errors `unnecessary_clarification`
- `Q215` `langgraph` `protected_structured_admin` quality `80` mode `structured_tool` reason `a solicitacao pode ser executada por workflow estruturado com protocolo` errors `missing_expected_keyword`
- `Q215` `python_functions` `protected_structured_admin` quality `80` mode `structured_tool` reason `python_functions_native_structured:support` errors `missing_expected_keyword`
- `Q215` `llamaindex` `protected_structured_admin` quality `80` mode `structured_tool` reason `a solicitacao pode ser executada por workflow estruturado com protocolo` errors `missing_expected_keyword`
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

### `Q201` Quando a ausencia por saude coincide com prova, como a escola conecta comprovacao, segunda chamada e recuperacao na politica publica?

- Retrieval type: `public_policy_bridge`
- Slice: `public`
- `langgraph`: status 200, latency 3902.9ms, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`, backend `qdrant_hybrid`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `crewai`: status 200, latency 270.9ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 135.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 142.5ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 147.8ms, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`, backend `none`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### `Q202` Como fica a sequencia entre abertura da matricula, inicio das aulas e a primeira reuniao com responsaveis em 2026?

- Retrieval type: `public_timeline`
- Slice: `public`
- `langgraph`: status 200, latency 4235.3ms, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`, backend `none`, strategy `direct_answer`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento. Depois do inicio das aulas: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro. Primeira reuniao com responsaveis: A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `crewai`: status 200, latency 206.6ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. | 2025-10-06 | familias interessadas | O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. | 2026-02-02 | alunos e familias | A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. | 2026-03-28 | responsaveis e familias | A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `python_functions`: status 200, latency 134.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento. Depois do inicio das aulas: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro. Primeira reuniao com responsaveis: A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `llamaindex`: status 200, latency 149.2ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a base publica de Colegio Horizonte nao traz um marco institucional estruturado para essa data.
- `specialist_supervisor`: status 200, latency 140.9ms, quality `100`, reason `specialist_supervisor_tool_first:public_timeline_bundle`, backend `none`, strategy `structured_tool`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.

### `Q203` Se eu ficar sem acesso e ainda precisar mandar documentos, qual e a ordem mais segura entre portal, credenciais e secretaria?

- Retrieval type: `public_documents_credentials`
- Slice: `public`
- `langgraph`: status 200, latency 1826.5ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `direct_answer`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `crewai`: status 200, latency 182.1ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 116.9ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 140.0ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 66.7ms, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### `Q204` Para uma familia entrando agora, como manual de matricula, calendario e agenda de avaliacoes se combinam no inicio do ano?

- Retrieval type: `public_family_new_bundle`
- Slice: `public`
- `langgraph`: status 200, latency 6169.2ms, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`, backend `none`, strategy `direct_answer`
  answer: Olá! Para as famílias que estão chegando agora, o manual de matrícula, o calendário e a agenda de avaliações se complementam para um bom começo. O ciclo de matrícula para 2026, por exemplo, começou em 6 de outubro de 2025, com o pré-cadastro e a visita orientada. Nosso atendimento comercial continua disponível enquanto houver vagas, e todos esses documentos serão apresentados e explicados para que vocês tenham todas as informações necessárias.
- `crewai`: status 200, latency 188.3ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 146.4ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `llamaindex`: status 200, latency 138.7ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a base publica de Colegio Horizonte nao traz um marco institucional estruturado para essa data.
- `specialist_supervisor`: status 599, latency 60061.1ms, quality `0`, reason `TimeoutError: `, backend `None`, strategy `None`
  errors: request_failed
  answer: 

### `Q205` Que mecanismos publicos ajudam a familia a acompanhar permanencia, apoio e vida escolar sem depender de informacao interna?

- Retrieval type: `public_permanence_support`
- Slice: `public`
- `langgraph`: status 200, latency 2212.4ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `crewai`: status 200, latency 231.0ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao educacional, monitorias, comunicados digitais, reunioes periodicas com responsaveis e acionamento de acompanhamento quando frequencia, adaptacao ou rotina de estudo exigem intervencao.
- `python_functions`: status 200, latency 123.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 81.9ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 70.8ms, quality `100`, reason `specialist_supervisor_preflight:permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### `Q206` Se eu comparar rematricula, transferencia e cancelamento, quais mudancas reais aparecem em prazos e documentacao?

- Retrieval type: `public_process_compare`
- Slice: `public`
- `langgraph`: status 200, latency 2100.2ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.process_compare`, backend `none`, strategy `direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `crewai`: status 200, latency 20591.5ms, quality `88`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Para te ajudar melhor, você gostaria de mais detalhes sobre a documentação necessária para rematrícula, transferência e cancelamento, e os prazos específicos para rematrícula?
- `python_functions`: status 200, latency 118.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 144.8ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 37416.4ms, quality `100`, reason `specialist_supervisor_manager_judge:institution:document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: O Colégio Horizonte não disponibiliza publicamente detalhes comparativos sobre os prazos e a documentação específica para rematrícula, transferência e cancelamento de matrícula. No entanto, sua solicitação foi encaminhada para a secretaria com o número de ticket ATD-20260402-AF602266. Um atendente entrará em contato com você em breve para fornecer as informações necessárias. Para futuras consultas, você pode entrar em contato diretamente com os seguintes canais: Secretaria: Para questões administrativas como transferência e emissão de documentos. Telefone (11) 3333-4200 ou e-mail secretaria@colegiohorizonte.edu.br. Atendimento de Admissões: Para dúvidas sobre o processo de ingresso e documentos (incluindo potencialmente rematrícula). Telefone (11) 3333-4201 ou e-mail admissoes@colegiohorizonte.edu.br.

### `Q207` No primeiro mes, que erros mais comprometem credenciais, documentacao e rotina da familia?

- Retrieval type: `public_first_month_risks`
- Slice: `public`
- `langgraph`: status 200, latency 2396.9ms, quality `80`, reason `langgraph_public_canonical_lane:public_bundle.first_month_risks`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `crewai`: status 200, latency 185.8ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 127.7ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `llamaindex`: status 200, latency 147.3ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 151.7ms, quality `80`, reason `specialist_supervisor_fast_path:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### `Q208` Como regulamentos, frequencia minima e recuperacao se conectam quando o aluno entra em dificuldade academica?

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 2438.2ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.conduct_frequency_recovery`, backend `none`, strategy `direct_answer`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `crewai`: status 200, latency 192.0ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Regulamentos gerais, politica de avaliacao e orientacao ao estudante se conectam assim: disciplina e convivio sustentam a rotina; frequencia minima e justificativas influenciam alerta academico; e recuperacao, segunda chamada e apoio pedagogico entram quando desempenho ou assiduidade exigem recomposicao.
- `python_functions`: status 200, latency 129.0ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `llamaindex`: status 200, latency 163.1ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `specialist_supervisor`: status 200, latency 69.9ms, quality `100`, reason `specialist_supervisor_preflight:conduct_frequency_recovery`, backend `none`, strategy `direct_answer`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.

### `Q209` Como a escola conecta biblioteca, laboratorios e estudo orientado para o ensino medio?

- Retrieval type: `public_section_aware`
- Slice: `public`
- `langgraph`: status 200, latency 2334.8ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `crewai`: status 200, latency 185.1ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Biblioteca e laboratorios aparecem como apoio ao estudo do ensino medio: a Biblioteca Aurora oferece consulta, emprestimo e estudo orientado; os laboratorios apoiam aulas praticas, pesquisa e projetos maker; e o contraturno conecta esses espacos a monitorias, cultura digital e projetos interdisciplinares.
- `python_functions`: status 200, latency 140.9ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `llamaindex`: status 200, latency 87.3ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `specialist_supervisor`: status 200, latency 76.1ms, quality `100`, reason `specialist_supervisor_preflight:facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.

### `Q210` O que e publico nos canais digitais e o que so aparece depois de autenticacao da familia?

- Retrieval type: `public_visibility_boundary`
- Slice: `public`
- `langgraph`: status 200, latency 2092.6ms, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  answer: Olá! Para te ajudar com essa dúvida, preciso de um pouco mais de contexto. A nossa base de conhecimento atual não especifica quais informações são públicas nos canais digitais e quais exigem autenticação da família.

Para informações mais detalhadas sobre o acesso aos nossos canais e o que está disponível em cada um, sugiro que você entre em contato com a nossa Secretaria Escolar. Eles poderão te orientar sobre o portal do aluno/família e outros recursos digitais.
- `crewai`: status 200, latency 20273.4ms, quality `80`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Não encontrei informações sobre a acessibilidade dos serviços digitais por autenticação nos documentos que tenho. Por favor, verifique outras fontes ou entre em contato diretamente para obter essa informação.
- `python_functions`: status 200, latency 199.1ms, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 24620.7ms, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 12569.4ms, quality `100`, reason `specialist_supervisor_direct:institution_specialist`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Os canais digitais públicos do Colégio Horizonte incluem o site institucional (www.colegiohorizonte.edu.br) e as redes sociais, como o Instagram (@colegiohorizonte), onde são divulgadas informações gerais, notícias e eventos. Além disso, contatos como telefone e e-mail de secretária, admissões e outros departamentos são acessíveis publicamente.

Informações que requerem autenticação da família são acessadas através do **portal autenticado**. Este portal é utilizado para assuntos mais sensíveis e personalizados, como o acesso a boletos, vencimentos, contratos financeiros e o envio de documentos completos ou dados sensíveis, que não devem ser compartilhados em canais abertos, como chats. O suporte digital da escola pode auxiliar em questões de acesso e senha para este portal.

### `Q211` Como responsaveis, avaliacoes, estudo orientado e canais digitais se influenciam mutuamente durante o ano?

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 162.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `crewai`: status 200, latency 194.8ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 144.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `llamaindex`: status 200, latency 73.9ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `specialist_supervisor`: status 200, latency 73.4ms, quality `100`, reason `specialist_supervisor_preflight:transversal_year_bundle`, backend `none`, strategy `direct_answer`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.

### `Q212` Resuma o quadro academico dos meus dois filhos e diga quem esta mais perto do limite de aprovacao.

- Retrieval type: `protected_structured_academic`
- Slice: `protected`
- `langgraph`: status 200, latency 3754.7ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal da escola. No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`. Depois disso, eu passo a consultar seus dados autorizados por este canal.

Os indicadores publicos mais recentes de Colegio Horizonte sao:
- Aprovacao global: 96.4% (ano letivo 2025)
- Frequencia media: 97.1% (ano letivo 2025)
- Familias que avaliaram o atendimento como bom ou excelente: 92.0% (pesquisa institucional 2025)
- `crewai`: status 200, latency 212.5ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: A referencia publica de aprovacao hoje e media 7.0 na escala 0-10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico.
- `python_functions`: status 200, latency 181.2ms, quality `80`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Os indicadores publicos mais recentes de Colegio Horizonte sao:
- Aprovacao global: 96.4% (ano letivo 2025)
- Frequencia media: 97.1% (ano letivo 2025)
- Familias que avaliaram o atendimento como bom ou excelente: 92.0% (pesquisa institucional 2025)
- `llamaindex`: status 200, latency 35924.1ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Os indicadores publicos mais recentes de Colegio Horizonte sao:
- Aprovacao global: 96.4% (ano letivo 2025)
- Frequencia media: 97.1% (ano letivo 2025)
- Familias que avaliaram o atendimento como bom ou excelente: 92.0% (pesquisa institucional 2025)
- `specialist_supervisor`: status 200, latency 19221.1ms, quality `100`, reason `specialist_supervisor_direct:academic_specialist`, backend `none`, strategy `structured_tool`
  answer: Para Lucas Oliveira:
Lucas possui uma média de 7.9 em Biologia, 6.5 em Educação Física, 7.1 em Filosofia, 5.9 em Física, 6.5 em Geografia, 6.8 em História, 8.1 em Inglês, 7.7 em Matemática, 8.3 em Português, 6.9 em Química, 6.7 em Redação, 7.3 em Sociologia e 6.8 em Tecnologia e Cultura Digital. Ele já atingiu a média de aprovação em Biologia, Filosofia, Inglês, Matemática, Português e Sociologia. Ele precisa de 0.5 pontos em Educação Física, 1.1 pontos em Física, 0.5 pontos em Geografia, 0.2 pontos em História, 0.1 pontos em Química, 0.3 pontos em Redação e 0.2 pontos em Tecnologia e Cultura Digital para atingir a média de 7.0 nessas disciplinas.

Para Ana Oliveira:
Ana possui uma média de 8.0 em Biologia, 7.0 em Educação Física, 7.5 em Filosofia, 6.4 em Física, 7.0 em Geografia, 7.3 em História, 8.5 em Inglês, 7.4 em Matemática, 8.4 em Português, 7.4 em Química, 7.1 em Redação, 7.7 em Sociologia e 7.3 em Tecnologia e Cultura Digital. Ela já atingiu a média de aprovação em todas as disciplinas, exceto Física, onde precisa de 0.6 pontos para atingir a média de 7.0.

Comparando o quadro acadêmico de seus filhos, Ana Oliveira está mais perto do limite de aprovação, necessitando de apenas 0.6 pontos na disciplina de Física para atingir o alvo de aprovação, enquanto Lucas Oliveira precisa de um total de 2.9 pontos distribuídos em diversas disciplinas.

### `Q213` Agora quero apenas a Ana: em quais materias ela aparece mais exposta?

- Retrieval type: `protected_structured_followup`
- Slice: `protected`
- `langgraph`: status 200, latency 3895.9ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal da escola. No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`. Depois disso, eu passo a consultar seus dados autorizados por este canal.
- `crewai`: status 200, latency 20808.3ms, quality `100`, reason `crewai_protected_flow_timeout`, backend `none`, strategy `None`
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora sobre Ana Oliveira. Se quiser, me diga exatamente se voce quer notas, faltas, provas, documentacao, matricula ou financeiro.
- `python_functions`: status 200, latency 236.6ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
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
- `llamaindex`: status 200, latency 2209.2ms, quality `55`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `structured_tool`
  errors: forbidden_entity_or_value
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `specialist_supervisor`: status 200, latency 195.2ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary`, backend `none`, strategy `structured_tool`
  answer: Notas de Ana Oliveira:
- Historia: media parcial 7,3
- Fisica: media parcial 6,4
- Matematica: media parcial 7,4
- Portugues: media parcial 8,4

### `Q214` Como esta o financeiro da familia hoje, incluindo vencimentos e proximos passos?

- Retrieval type: `protected_structured_finance`
- Slice: `protected`
- `langgraph`: status 200, latency 152.1ms, quality `80`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Familia Hoje entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `crewai`: status 200, latency 196.6ms, quality `80`, reason `protected_shadow_needs_student_clarification`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 137.0ms, quality `80`, reason `python_functions_native_structured:finance`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Familia Hoje entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `llamaindex`: status 200, latency 161.3ms, quality `80`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Familia Hoje entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `specialist_supervisor`: status 200, latency 142.7ms, quality `88`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### `Q215` Quero o status documental da Ana com as pendencias e o proximo passo recomendado.

- Retrieval type: `protected_structured_admin`
- Slice: `protected`
- `langgraph`: status 200, latency 172.0ms, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `crewai`: status 200, latency 459.2ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Hoje Ana Oliveira ainda tem pendencias documentais em Documentacao escolar do aluno. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
- `python_functions`: status 200, latency 175.5ms, quality `80`, reason `python_functions_native_structured:support`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 207.2ms, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `specialist_supervisor`: status 200, latency 217.4ms, quality `100`, reason `specialist_supervisor_tool_first:administrative_status`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira esta com pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.

### `Q216` Segundo o playbook interno de negociacao financeira, que criterios guiam o atendimento a uma familia?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 398.2ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `crewai`: status 200, latency 659.1ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.
- `python_functions`: status 200, latency 462.6ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `llamaindex`: status 200, latency 485.4ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.
- `specialist_supervisor`: status 200, latency 497.9ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

### `Q217` No manual interno do professor, como ficam registro de avaliacoes e comunicacao pedagogica?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 465.0ms, quality `80`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
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
- `crewai`: status 200, latency 665.1ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `python_functions`: status 200, latency 388.7ms, quality `80`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
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
- `llamaindex`: status 200, latency 472.4ms, quality `80`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Roteiro interno de acolhimento do 6o ano (Rotina interna para acolhimento pedagogico.): No acolhimento do 6o ano, a escola prioriza ambientacao, apresentacao de rotinas, combinados de convivencia e acompanhamento da adaptacao nas primeiras semanas.
- `specialist_supervisor`: status 200, latency 537.6ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Roteiro interno de acolhimento do 6o ano (Rotina interna para acolhimento pedagogico.): No acolhimento do 6o ano, a escola prioriza ambientacao, apresentacao de rotinas, combinados de convivencia e acompanhamento da adaptacao nas primeiras semanas.

### `Q218` Que limite de acesso no Telegram aparece no protocolo interno para responsaveis com escopo parcial?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 462.6ms, quality `80`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `crewai`: status 200, latency 638.5ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Manual interno do professor (Procedimento interno de registro academico docente.): Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `python_functions`: status 200, latency 452.2ms, quality `80`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `llamaindex`: status 200, latency 479.4ms, quality `80`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.
- `specialist_supervisor`: status 200, latency 553.1ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

### `Q219` Ha procedimento interno de viagem internacional com hospedagem para alunos do ensino medio?

- Retrieval type: `restricted_doc_negative`
- Slice: `restricted`
- `langgraph`: status 200, latency 461.6ms, quality `80`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Manual interno do professor (Procedimento interno de registro academico docente.): Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

Fontes:
- Procedimento interno para transferencia no meio do ano (v2026.3)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Manual interno do professor (v1)
- `crewai`: status 200, latency 696.9ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial.
Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Manual interno do professor (Procedimento interno de registro academico docente.): Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `python_functions`: status 200, latency 428.9ms, quality `80`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Manual interno do professor (Procedimento interno de registro academico docente.): Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

Fontes:
- Procedimento interno para transferencia no meio do ano (v2026.3)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Manual interno do professor (v1)
- `llamaindex`: status 200, latency 428.6ms, quality `80`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Manual interno do professor (Procedimento interno de registro academico docente.): Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `specialist_supervisor`: status 200, latency 521.1ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Manual interno do professor (Procedimento interno de registro academico docente.): Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

### `Q220` Quero acessar o manual interno do professor pelo bot.

- Retrieval type: `restricted_doc_denied`
- Slice: `restricted`
- `langgraph`: status 200, latency 215.9ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `crewai`: status 200, latency 211.8ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 129.9ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 163.7ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 132.9ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

