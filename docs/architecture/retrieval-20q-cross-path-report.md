# Retrieval 20Q Cross-Path Report

Date: 2026-04-02T07:28:32.622994+00:00

Dataset: `tests/evals/datasets/retrieval_20q_probe_cases.json`

Run prefix: `debug:retrieval20:20260402T072022Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `20/20` | `10/20` | `90.0` | `2426.2 ms` |
| `crewai` | `20/20` | `8/20` | `86.8` | `5533.2 ms` |
| `python_functions` | `20/20` | `10/20` | `90.0` | `367.3 ms` |
| `llamaindex` | `20/20` | `10/20` | `90.0` | `2613.9 ms` |
| `specialist_supervisor` | `20/20` | `14/20` | `93.4` | `13436.0 ms` |

## By Retrieval Type

- `protected_structured_academic`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 398.8ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 600.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 443.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 498.6ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 560.0ms
- `protected_structured_admin`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 236.2ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 826.4ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 274.5ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 326.2ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 30492.6ms
- `protected_structured_finance`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 415.2ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 19587.7ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 382.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 405.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 88.0, latency 185.0ms
- `protected_structured_followup`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 685.5ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 21685.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 326.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 387.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 249.5ms
- `public_deep_multi_doc`
  - `langgraph`: keyword pass 0/2, quality 80.0, latency 223.3ms
  - `crewai`: keyword pass 0/2, quality 80.0, latency 653.1ms
  - `python_functions`: keyword pass 0/2, quality 80.0, latency 262.9ms
  - `llamaindex`: keyword pass 0/2, quality 80.0, latency 6946.9ms
  - `specialist_supervisor`: keyword pass 1/2, quality 90.0, latency 37636.6ms
- `public_documents_credentials`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 1596.6ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 230.3ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 166.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 195.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 80.4ms
- `public_family_new_bundle`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 6403.2ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 301.0ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 713.0ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 21665.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 70519.1ms
- `public_first_month_risks`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 2455.0ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 256.7ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 171.0ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 198.5ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 171.2ms
- `public_permanence_support`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 5035.6ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 20398.4ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 173.4ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 117.6ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 67269.5ms
- `public_policy_bridge`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4814.2ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 343.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 207.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 236.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 178.3ms
- `public_process_compare`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4403.9ms
  - `crewai`: keyword pass 1/1, quality 88.0, latency 20368.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 177.7ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 214.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 87.3ms
- `public_section_aware`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 7920.4ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 282.8ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 254.4ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 10702.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 18075.5ms
- `public_timeline`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 4462.2ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 237.8ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 184.0ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 200.0ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 186.2ms
- `public_visibility_boundary`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 5724.7ms
  - `crewai`: keyword pass 1/1, quality 88.0, latency 20361.7ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 189.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 195.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 2752.0ms
- `restricted_doc_denied`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 269.0ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 294.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 151.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 221.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 138.3ms
- `restricted_doc_no_match`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 849.0ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 965.1ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 799.4ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 685.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 690.4ms
- `restricted_doc_positive`
  - `langgraph`: keyword pass 1/3, quality 86.7, latency 802.7ms
  - `crewai`: keyword pass 1/3, quality 86.7, latency 872.8ms
  - `python_functions`: keyword pass 1/3, quality 86.7, latency 735.2ms
  - `llamaindex`: keyword pass 1/3, quality 86.7, latency 711.9ms
  - `specialist_supervisor`: keyword pass 1/3, quality 86.7, latency 603.7ms

## Failures

- `Q201` `crewai` `public_policy_bridge` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q202` `langgraph` `public_timeline` quality `80` mode `structured_tool` reason `datas institucionais publicas devem vir de leitura estruturada e auditavel` errors `missing_expected_keyword`
- `Q202` `crewai` `public_timeline` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q202` `python_functions` `public_timeline` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q202` `llamaindex` `public_timeline` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q202` `specialist_supervisor` `public_timeline` quality `80` mode `structured_tool` reason `specialist_supervisor_tool_first:public_timeline_bundle` errors `missing_expected_keyword`
- `Q204` `langgraph` `public_family_new_bundle` quality `80` mode `structured_tool` reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno` errors `missing_expected_keyword`
- `Q204` `crewai` `public_family_new_bundle` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q204` `python_functions` `public_family_new_bundle` quality `80` mode `hybrid_retrieval` reason `python_functions_native_public_retrieval` errors `missing_expected_keyword`
- `Q204` `llamaindex` `public_family_new_bundle` quality `80` mode `hybrid_retrieval` reason `llamaindex_public_profile` errors `missing_expected_keyword`
- `Q205` `langgraph` `public_permanence_support` quality `80` mode `structured_tool` reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support` errors `missing_expected_keyword`
- `Q205` `crewai` `public_permanence_support` quality `80` mode `structured_tool` reason `crewai_public_flow_timeout` errors `missing_expected_keyword`
- `Q205` `python_functions` `public_permanence_support` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q205` `llamaindex` `public_permanence_support` quality `80` mode `structured_tool` reason `llamaindex_public_canonical_lane:public_bundle.permanence_family_support` errors `missing_expected_keyword`
- `Q206` `crewai` `public_process_compare` quality `88` mode `structured_tool` reason `crewai_public_flow_timeout` errors `unnecessary_clarification`
- `Q207` `langgraph` `public_first_month_risks` quality `80` mode `structured_tool` reason `langgraph_public_canonical_lane:public_bundle.first_month_risks` errors `missing_expected_keyword`
- `Q207` `crewai` `public_first_month_risks` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q207` `python_functions` `public_first_month_risks` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q207` `llamaindex` `public_first_month_risks` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q207` `specialist_supervisor` `public_first_month_risks` quality `80` mode `structured_tool` reason `specialist_supervisor_fast_path:service_credentials_bundle` errors `missing_expected_keyword`
- `Q208` `langgraph` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q208` `crewai` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q208` `python_functions` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q208` `llamaindex` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q209` `langgraph` `public_section_aware` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q209` `crewai` `public_section_aware` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q209` `python_functions` `public_section_aware` quality `80` mode `structured_tool` reason `python_functions_native_structured:institution` errors `missing_expected_keyword`
- `Q209` `llamaindex` `public_section_aware` quality `80` mode `structured_tool` reason `llamaindex_public_profile` errors `missing_expected_keyword`
- `Q210` `crewai` `public_visibility_boundary` quality `88` mode `structured_tool` reason `crewai_public_flow_timeout` errors `unnecessary_clarification`
- `Q211` `langgraph` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` errors `missing_expected_keyword`
- `Q211` `crewai` `public_deep_multi_doc` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q211` `python_functions` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `python_functions_native_structured:institution` errors `missing_expected_keyword`
- `Q211` `llamaindex` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q211` `specialist_supervisor` `public_deep_multi_doc` quality `80` mode `clarify` reason `specialist_supervisor_strict_safe_fallback` errors `missing_expected_keyword`
- `Q214` `crewai` `protected_structured_finance` quality `80` mode `structured_tool` reason `crewai_public_flow_completed` errors `missing_expected_keyword`
- `Q214` `specialist_supervisor` `protected_structured_finance` quality `88` mode `clarify` reason `specialist_supervisor_resolved_intent:finance_student_clarify` errors `unnecessary_clarification`
- `Q215` `langgraph` `protected_structured_admin` quality `80` mode `structured_tool` reason `a solicitacao pode ser executada por workflow estruturado com protocolo` errors `missing_expected_keyword`
- `Q215` `crewai` `protected_structured_admin` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q215` `python_functions` `protected_structured_admin` quality `80` mode `structured_tool` reason `python_functions_native_structured:support` errors `missing_expected_keyword`
- `Q215` `llamaindex` `protected_structured_admin` quality `80` mode `structured_tool` reason `a solicitacao pode ser executada por workflow estruturado com protocolo` errors `missing_expected_keyword`
- `Q215` `specialist_supervisor` `protected_structured_admin` quality `80` mode `structured_tool` reason `specialist_supervisor_manager_judge:workflow:workflow_status` errors `missing_expected_keyword`
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

## Prompt Results

### `Q201` Se um aluno perde prova por motivo de saude, como a politica publica conecta atestado, segunda chamada e recuperacao?

- Retrieval type: `public_policy_bridge`
- Slice: `public`
- `langgraph`: status 200, latency 4814.2ms, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`, backend `qdrant_hybrid`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `crewai`: status 200, latency 343.6ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 207.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 236.8ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 178.3ms, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`, backend `none`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### `Q202` Qual e a sequencia entre abertura da matricula, inicio das aulas e primeira reuniao com responsaveis em 2026?

- Retrieval type: `public_timeline`
- Slice: `public`
- `langgraph`: status 200, latency 4462.2ms, quality `80`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Olá! Para 2026, as matrículas do Colégio Horizonte foram abertas em 6 de outubro de 2025, com pré-cadastro e visita opcional. As aulas para o Ensino Fundamental II e Médio começam em 2 de fevereiro de 2026, e a semana de acolhimento para o 6º ano e 1ª série será de 2 a 6 de fevereiro.
- `crewai`: status 200, latency 237.8ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. | 2025-10-06 | familias interessadas | O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. | 2026-02-02 | alunos e familias | A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `python_functions`: status 200, latency 184.0ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 200.0ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a base publica de Colegio Horizonte nao traz um marco institucional estruturado para essa data.
- `specialist_supervisor`: status 200, latency 186.2ms, quality `80`, reason `specialist_supervisor_tool_first:public_timeline_bundle`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### `Q203` Se eu perder a senha e ainda precisar enviar documentos, em que ordem devo resolver portal, credenciais e secretaria?

- Retrieval type: `public_documents_credentials`
- Slice: `public`
- `langgraph`: status 200, latency 1596.6ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `direct_answer`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `crewai`: status 200, latency 230.3ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 166.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 195.3ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 80.4ms, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### `Q204` Estou chegando agora com meu primeiro filho: como matricula, calendario e agenda de avaliacoes se encaixam no primeiro bimestre?

- Retrieval type: `public_family_new_bundle`
- Slice: `public`
- `langgraph`: status 200, latency 6403.2ms, quality `80`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`, backend `qdrant_hybrid`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Que bom ter você conosco! Para a matrícula de 2026, o processo começou em 6 de outubro de 2025, com pré-cadastro e triagem de documentos. Nosso atendimento comercial continua enquanto houver vagas.

Para o primeiro bimestre, temos dois eventos importantes: uma visita guiada para famílias interessadas em 6 de abril de 2026, às 9h, e o plantão pedagógico em 11 de abril de 2026, às 8h.
- `crewai`: status 200, latency 301.0ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 713.0ms, quality `80`, reason `python_functions_native_public_retrieval`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: A base publica atual nao sustenta com seguranca todos os pontos dessa pergunta, especialmente sobre: agora, bimestre, chegando, encaixam, estou, filho, primeiro. Para evitar uma orientacao incorreta, prefiro nao inferir alem do que esta documentado. Se quiser, eu posso responder apenas o que esta explicitamente registrado na base atual.

Fontes:
- Calendario Letivo 2026 (v2026.2)
- Agenda de Avaliacoes, Recuperacoes e Simulados 2026 (v2026.3)
- Politica de Avaliacao, Recuperacao e Promocao (v2026.3)
- `llamaindex`: status 200, latency 21665.0ms, quality `80`, reason `llamaindex_public_profile`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.

Hoje a base publica de eventos de Colegio Horizonte nao trouxe agenda estruturada para esse pedido.

Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
Prazo esperado da secretaria: retorno em ate 2 dias uteis.
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 70519.1ms, quality `100`, reason `specialist_supervisor_manager_judge:academic:hybrid_retrieval`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Seja bem-vindo(a) ao Colégio Horizonte! Compreendo que, como novo(a) responsável, você tenha dúvidas sobre os primeiros passos. Aqui está um resumo sobre o processo de matrícula, o calendário escolar e a agenda de avaliações para o primeiro bimestre:

**Processo de Matrícula:**
Para a matrícula no Colégio Horizonte, o processo envolve um pré-cadastro, visita orientada opcional e triagem inicial de documentos. A matrícula é condicionada à análise documental, entrevista de acolhimento e assinatura do contrato.

Você pode entrar em contato com o setor de Admissões pelo telefone (11) 3333-4201 ou WhatsApp (11) 97500-2040.

**Calendário Escolar (Eventos Principais 2026):**
*   O ano letivo de 2026 para o Ensino Fundamental II e Ensino Médio começa em 2 de fevereiro.
*   As reuniões de pais e responsáveis para apresentação do planejamento do primeiro bimestre ocorrem em 28 de março de 2026 (geral e Fundamental II) e 29 de março de 2026 (Ensino Médio).

**Agenda de Avaliações do Primeiro Bimestre:**
Em relação à agenda de avaliações, um "Plantão pedagógico do primeiro bimestre" está agendado para 11 de abril de 2026, com atendimento de professores para esclarecimento de notas e frequência. Embora uma agenda detalhada de avaliações não esteja publicamente disponível no calendário geral, este plantão é o momento principal para discutir o desempenho no primeiro bimestre. As reuniões de pais no final de março também abordarão as rotinas de avaliação.

Para informações sobre a agenda de avaliações do seu filho, preciso do nome completo dele.

### `Q205` Que mecanismos publicos a escola descreve para que a familia acompanhe permanencia, apoio e vida escolar sem se perder?

- Retrieval type: `public_permanence_support`
- Slice: `public`
- `langgraph`: status 200, latency 5035.6ms, quality `80`, reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Que bom que você quer acompanhar de perto a vida escolar! Aqui no Colégio Horizonte, a equipe de orientação pedagógica está sempre atenta à adaptação, rotina de estudos e desenvolvimento de hábitos de aprendizagem dos nossos alunos.

Para dar um suporte extra, oferecemos monitorias agendadas e plantões de dúvidas, especialmente nas disciplinas que costumam apresentar mais desafios. Além disso, mantemos a família sempre informada através de comunicados digitais, reuniões periódicas e, se necessário, fazemos chamadas de acompanhamento individual.

É importante lembrar que a aprovação do aluno considera tanto o desempenho acadêmico quanto a frequência mínima exigida. E para os estudantes do Ensino Médio, temos o Projeto de Vida, que funciona como um componente curricular e um eixo de tutoria, auxiliando-os em suas escolhas e caminhos.
- `crewai`: status 200, latency 20398.4ms, quality `80`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: No momento, não temos informações detalhadas sobre os mecanismos de apoio à família nos documentos disponíveis. Para saber mais sobre como a escola oferece suporte às famílias, por favor, entre em contato diretamente com a secretaria da escola ou consulte o site oficial.
- `python_functions`: status 200, latency 173.4ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 117.6ms, quality `80`, reason `llamaindex_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 67269.5ms, quality `100`, reason `specialist_supervisor_manager_judge:institution:hybrid_retrieval`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: O Colégio Horizonte oferece diversos mecanismos públicos para que as famílias possam acompanhar a permanência, o apoio e a vida escolar dos estudantes. Esses mecanismos incluem canais de comunicação diretos como a Coordenação Pedagógica e a Orientação Educacional, que monitoram a frequência e oferecem suporte socioemocional e acadêmico. A escola também disponibiliza múltiplos canais de contato como portal oficial, Telegram, telefones, e-mails e WhatsApp, além de promover reuniões, plantões pedagógicos e eventos abertos à participação familiar para acompanhamento geral da vida escolar. Atividades extracurriculares também enriquecem a experiência dos alunos e são divulgadas periodicamente.

### `Q206` Na pratica, o que muda entre rematricula, transferencia de entrada e cancelamento olhando prazos e papelada?

- Retrieval type: `public_process_compare`
- Slice: `public`
- `langgraph`: status 200, latency 4403.9ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.process_compare`, backend `none`, strategy `direct_answer`
  answer: Olá! Entendo sua dúvida sobre esses processos.

A rematrícula é para quem já está conosco e acontece em um período específico, divulgado em nossos canais. Já a transferência de entrada é para novos alunos e depende de vaga e análise. Se a família deseja transferir o aluno para outra escola, é uma transferência de saída, e o cancelamento é quando o vínculo com a escola é encerrado.

Para todos esses casos, os prazos e a documentação necessária são informados pela secretaria, e declarações simples geralmente são liberadas em até dois dias úteis.
- `crewai`: status 200, latency 20368.1ms, quality `88`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Para te ajudar melhor, poderia me dizer para qual processo específico você gostaria de saber os prazos e a papelada? Por exemplo, você busca informações sobre rematrícula, transferência de entrada ou cancelamento, ou gostaria de uma tabela comparativa detalhada?
- `python_functions`: status 200, latency 177.7ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 214.9ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 87.3ms, quality `100`, reason `specialist_supervisor_preflight:process_compare`, backend `none`, strategy `direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### `Q207` Quais deslizes do primeiro mes mais costumam dar problema com credenciais, documentos e rotina?

- Retrieval type: `public_first_month_risks`
- Slice: `public`
- `langgraph`: status 200, latency 2455.0ms, quality `80`, reason `langgraph_public_canonical_lane:public_bundle.first_month_risks`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `crewai`: status 200, latency 256.7ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 171.0ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `llamaindex`: status 200, latency 198.5ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 171.2ms, quality `80`, reason `specialist_supervisor_fast_path:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### `Q208` Cruze regulamentos gerais, politica de avaliacao e orientacao ao estudante para explicar como disciplina, frequencia e recuperacao se influenciam.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 190.5ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `crewai`: status 200, latency 1027.0ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: A proposta pedagogica publicada hoje combina A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo. Na pratica, isso aparece em frentes como Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes.
- `python_functions`: status 200, latency 263.4ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `llamaindex`: status 200, latency 255.0ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `specialist_supervisor`: status 200, latency 192.8ms, quality `100`, reason `specialist_supervisor_tool_first:conduct_frequency_punctuality`, backend `none`, strategy `structured_tool`
  answer: O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia.

### `Q209` Como biblioteca e laboratorios aparecem nas regras de uso e no apoio ao estudo do ensino medio?

- Retrieval type: `public_section_aware`
- Slice: `public`
- `langgraph`: status 200, latency 7920.4ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.

Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
- `crewai`: status 200, latency 282.8ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Sim. Biblioteca Aurora: biblioteca   Biblioteca Aurora   service   True   Atendimento ao publico de segunda a sexta, das 7h30 as 18h00..
- `python_functions`: status 200, latency 254.4ms, quality `80`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Hoje Colegio Horizonte atende estes segmentos:
- Ensino Fundamental II (6o ao 9o ano)
- Ensino Medio (1a a 3a serie)
- `llamaindex`: status 200, latency 10702.0ms, quality `80`, reason `llamaindex_public_profile`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Hoje Colegio Horizonte atende estes segmentos:
- Ensino Fundamental II (6o ao 9o ano)
- Ensino Medio (1a a 3a serie)
- `specialist_supervisor`: status 200, latency 18075.5ms, quality `100`, reason `specialist_supervisor_direct:institution_specialist`, backend `none`, strategy `structured_tool`
  answer: A biblioteca e os laboratórios do Colégio Horizonte são importantes recursos de apoio ao estudo para o ensino médio. 

A **Biblioteca Aurora** funciona de segunda a sexta-feira, das 7h30 às 18h00, oferecendo atendimento ao público e **estudo orientado**. 

O **Laboratório de Ciências** é utilizado em aulas práticas, clubes de ciências e mostras semestrais. Além disso, os estudantes do ensino médio têm acesso a laboratórios no contraturno, a partir das 14h00, para trilhas eletivas e monitorias. O **Espaço Maker** também é integrado ao currículo, sendo um ambiente para robótica, prototipagem leve e projetos interdisciplinares de ciências, tecnologia e cultura digital, o que complementa o apoio ao estudo prático.

### `Q210` O que e publico no calendario e no portal, e o que ja depende de autenticacao da familia?

- Retrieval type: `public_visibility_boundary`
- Slice: `public`
- `langgraph`: status 200, latency 5724.7ms, quality `100`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`, backend `qdrant_hybrid`, strategy `direct_answer`
  answer: No nosso calendário público, você encontra os marcos institucionais e eventos coletivos. Já os detalhes individuais de cada aluno, convites específicos, informações financeiras e acompanhamentos protegidos dependem de autenticação. Sempre que houver alguma atualização importante no calendário de avaliações, avisaremos no portal e pelos nossos canais oficiais.
- `crewai`: status 200, latency 20361.7ms, quality `88`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Olá! Para te ajudar com os níveis de acesso, posso te dizer que o calendário escolar e o portal da escola são públicos e podem ser acessados por qualquer pessoa, sem precisar de autenticação. Já para informações e serviços mais específicos, como notas, frequência e histórico escolar, é necessário fazer login com as credenciais que a escola fornece. Você poderia me dizer quais informações ou serviços públicos no calendário e no portal você gostaria de saber, ou quais informações específicas você busca que dependem de autenticação?
- `python_functions`: status 200, latency 189.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `llamaindex`: status 200, latency 195.3ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 2752.0ms, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`, backend `none`, strategy `direct_answer`
  answer: No contexto de um calendário e portal, geralmente:

*   **Público (no calendário e no portal):** São informações de acesso geral, como eventos abertos à comunidade, notícias gerais, comunicados amplos, feriados, informações de contato e endereço, e outros conteúdos que não são específicos para um indivíduo ou família.
*   **Depende de autenticação da família:** São informações personalizadas e restritas, como notas de alunos, frequência, comunicados específicos para uma família, boletos de pagamento, horários individuais de aulas, ou qualquer dado que seja privado e exija a identificação do usuário.

### `Q211` Monte uma visao transversal de como comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se afetam ao longo do ano.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 256.1ms, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 279.2ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 262.4ms, quality `80`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje o Colegio Horizonte divulga atividades complementares no contraturno de forma assim: - Ensino Fundamental II: Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados. - Ensino Medio: Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00. - Fundamental II e Ensino Medio: Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno. Entre as ofertas que aparecem com mais clareza hoje estao Biblioteca Aurora, Oficina de danca e expressao corporal, Oficina de teatro, Futsal e treinos esportivos, Volei escolar, Espaco Maker.
- `llamaindex`: status 200, latency 13638.7ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje o Colegio Horizonte divulga atividades complementares no contraturno de forma assim: - Ensino Fundamental II: Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados. - Ensino Medio: Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00. - Fundamental II e Ensino Medio: Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno. Entre as ofertas que aparecem com mais clareza hoje estao Biblioteca Aurora, Oficina de danca e expressao corporal, Oficina de teatro, Futsal e treinos esportivos, Volei escolar, Espaco Maker.
- `specialist_supervisor`: status 200, latency 75080.3ms, quality `80`, reason `specialist_supervisor_strict_safe_fallback`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### `Q212` Faca um panorama academico dos meus filhos e destaque quem esta mais perto da media minima.

- Retrieval type: `protected_structured_academic`
- Slice: `protected`
- `langgraph`: status 200, latency 398.8ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `crewai`: status 200, latency 600.6ms, quality `100`, reason `crewai_protected_identity_backstop`, backend `none`, strategy `None`
  answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.
- `python_functions`: status 200, latency 443.5ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 498.6ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 560.0ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4

### `Q213` Agora foque so na Ana e diga em quais componentes ela esta mais vulneravel.

- Retrieval type: `protected_structured_followup`
- Slice: `protected`
- `langgraph`: status 200, latency 685.5ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
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
- `crewai`: status 200, latency 21685.0ms, quality `100`, reason `crewai_protected_flow_timeout`, backend `none`, strategy `None`
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora sobre Ana Oliveira. Se quiser, me diga exatamente se voce quer notas, faltas, provas, documentacao, matricula ou financeiro.
- `python_functions`: status 200, latency 326.5ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
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
- `llamaindex`: status 200, latency 387.3ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
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
- `specialist_supervisor`: status 200, latency 249.5ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary`, backend `none`, strategy `structured_tool`
  answer: Notas de Ana Oliveira:
- Historia: media parcial 7,3
- Fisica: media parcial 6,4
- Matematica: media parcial 7,4
- Portugues: media parcial 8,4

### `Q214` Resuma a situacao financeira atual da familia, com vencimentos, atrasos e proximos passos.

- Retrieval type: `protected_structured_finance`
- Slice: `protected`
- `langgraph`: status 200, latency 415.2ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- `crewai`: status 200, latency 19587.7ms, quality `80`, reason `crewai_public_flow_completed`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Olá! Para consultar os vencimentos, atrasos e os próximos passos relacionados à situação financeira da sua família, sugiro que entre em contato diretamente com o serviço responsável. As informações detalhadas não estão disponíveis nos documentos que tenho aqui.
- `python_functions`: status 200, latency 382.6ms, quality `100`, reason `python_functions_native_structured:finance`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- `llamaindex`: status 200, latency 405.2ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- `specialist_supervisor`: status 200, latency 185.0ms, quality `88`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### `Q215` Quais pendencias documentais da Ana ainda pedem acao e qual e o proximo passo recomendado?

- Retrieval type: `protected_structured_admin`
- Slice: `protected`
- `langgraph`: status 200, latency 236.2ms, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `crewai`: status 200, latency 826.4ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: O proximo pagamento de Ana Oliveira vence em 2026-03-10 no valor de 1450.00.
- `python_functions`: status 200, latency 274.5ms, quality `80`, reason `python_functions_native_structured:support`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 326.2ms, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `specialist_supervisor`: status 200, latency 30492.6ms, quality `80`, reason `specialist_supervisor_manager_judge:workflow:workflow_status`, backend `none`, strategy `workflow_status`
  errors: missing_expected_keyword
  answer: Não foram encontradas pendências documentais específicas para Ana em nossos registros no momento. Para obter uma verificação mais detalhada e personalizada, posso abrir um chamado para que um atendente possa analisar a situação e informar os próximos passos recomendados.

### `Q216` No playbook interno de negociacao financeira, quais criterios orientam uma negociacao com a familia?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 609.6ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `crewai`: status 200, latency 826.0ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao: Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Protocolo interno para responsaveis com escopo parcial: Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
- `python_functions`: status 200, latency 692.7ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `llamaindex`: status 200, latency 685.3ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.
- `specialist_supervisor`: status 200, latency 598.8ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao: Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

### `Q217` Segundo o Manual interno do professor, como a escola orienta registro de avaliacoes e comunicacao pedagogica?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 880.6ms, quality `80`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Roteiro interno de acolhimento do 6o ano (Rotina interna para acolhimento pedagogico.): No acolhimento do 6o ano, a escola prioriza ambientacao, apresentacao de rotinas, combinados de convivencia e acompanhamento da adaptacao nas primeiras semanas.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.

Fontes:
- Manual interno do professor (v1)
- Roteiro interno de acolhimento do 6o ano (v1)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `crewai`: status 200, latency 927.8ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Playbook interno de negociacao financeira: Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
- `python_functions`: status 200, latency 674.1ms, quality `80`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Roteiro interno de acolhimento do 6o ano (Rotina interna para acolhimento pedagogico.): No acolhimento do 6o ano, a escola prioriza ambientacao, apresentacao de rotinas, combinados de convivencia e acompanhamento da adaptacao nas primeiras semanas.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.

Fontes:
- Manual interno do professor (v1)
- Roteiro interno de acolhimento do 6o ano (v1)
- Procedimento interno para transferencia no meio do ano (v2026.3)
- `llamaindex`: status 200, latency 782.7ms, quality `80`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Roteiro interno de acolhimento do 6o ano (Rotina interna para acolhimento pedagogico.): No acolhimento do 6o ano, a escola prioriza ambientacao, apresentacao de rotinas, combinados de convivencia e acompanhamento da adaptacao nas primeiras semanas.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
- `specialist_supervisor`: status 200, latency 654.8ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

### `Q218` O Protocolo interno para responsaveis com escopo parcial diz o que sobre limites de acesso no Telegram?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 917.8ms, quality `80`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
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
- `crewai`: status 200, latency 864.6ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao: Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Manual interno do professor: Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `python_functions`: status 200, latency 838.7ms, quality `80`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
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
- `llamaindex`: status 200, latency 667.6ms, quality `80`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.
- `specialist_supervisor`: status 200, latency 557.4ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao: Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

### `Q219` Existe algum procedimento interno sobre excursao internacional com hospedagem para o ensino medio?

- Retrieval type: `restricted_doc_no_match`
- Slice: `restricted`
- `langgraph`: status 200, latency 849.0ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao > Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.
Playbook interno de negociacao financeira (Procedimento interno de atendimento financeiro.): Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.

Fontes:
- Procedimento interno para transferencia no meio do ano (v2026.3)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Playbook interno de negociacao financeira (v1)
- `crewai`: status 200, latency 965.1ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Manual interno do professor: Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Playbook interno de negociacao financeira: Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
- `python_functions`: status 200, latency 799.4ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao - Procedimento interno para pagamento parcial e negociacao > Procedimento interno para pagamento parcial e negociacao): A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.
Playbook interno de negociacao financeira (Procedimento interno de atendimento financeiro.): Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.

Fontes:
- Procedimento interno para transferencia no meio do ano (v2026.3)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- Playbook interno de negociacao financeira (v1)
- `llamaindex`: status 200, latency 685.3ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Secao relevante: Procedimento interno para transferencia no meio do ano.
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Playbook interno de negociacao financeira (Procedimento interno de atendimento financeiro.): Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Manual interno do professor (Procedimento interno de registro academico docente.): Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `specialist_supervisor`: status 200, latency 690.4ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Procedimento interno para pagamento parcial e negociacao: A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. O bot pode abrir handoff, mas nao aprova acordo sozinho.

### `Q220` Como responsavel, quero ver o manual interno do professor.

- Retrieval type: `restricted_doc_denied`
- Slice: `restricted`
- `langgraph`: status 200, latency 269.0ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `crewai`: status 200, latency 294.8ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 151.6ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 221.0ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 138.3ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

