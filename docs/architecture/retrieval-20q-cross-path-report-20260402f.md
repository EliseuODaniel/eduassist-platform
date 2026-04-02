# Retrieval 20Q Cross-Path Report

Date: 2026-04-02T12:33:51.903987+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_20q_probe_cases.generated.20260402f.json`

Run prefix: `debug:retrieval20:20260402T123150Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `20/20` | `18/20` | `96.8` | `1314.9 ms` |
| `crewai` | `20/20` | `9/20` | `89.0` | `3307.6 ms` |
| `python_functions` | `20/20` | `18/20` | `96.8` | `326.4 ms` |
| `llamaindex` | `20/20` | `18/20` | `98.0` | `532.9 ms` |
| `specialist_supervisor` | `20/20` | `18/20` | `97.4` | `498.2 ms` |

## By Retrieval Type

- `protected_structured_academic`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 222.9ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 198.5ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 237.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 288.6ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 221.8ms
- `protected_structured_admin`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 176.3ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 444.7ms
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 179.0ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 197.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 214.1ms
- `protected_structured_finance`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 226.2ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 20270.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 217.3ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 232.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 201.5ms
- `protected_structured_followup`
  - `langgraph`: keyword pass 0/1, quality 55.0, latency 3648.6ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 20799.2ms
  - `python_functions`: keyword pass 0/1, quality 55.0, latency 2884.7ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 6988.5ms
  - `specialist_supervisor`: keyword pass 0/1, quality 68.0, latency 6216.8ms
- `public_deep_multi_doc`
  - `langgraph`: keyword pass 2/2, quality 100.0, latency 121.7ms
  - `crewai`: keyword pass 1/2, quality 90.0, latency 178.6ms
  - `python_functions`: keyword pass 2/2, quality 100.0, latency 127.8ms
  - `llamaindex`: keyword pass 2/2, quality 100.0, latency 72.8ms
  - `specialist_supervisor`: keyword pass 2/2, quality 100.0, latency 69.0ms
- `public_documents_credentials`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2496.4ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 167.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 119.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 69.8ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 73.4ms
- `public_family_new_bundle`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2546.6ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 188.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 113.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 85.4ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 76.3ms
- `public_first_month_risks`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4676.4ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 193.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 121.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 65.7ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 74.6ms
- `public_permanence_support`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 3192.2ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 171.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 122.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 73.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 74.9ms
- `public_policy_bridge`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 176.7ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 203.7ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 124.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 74.1ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 34.5ms
- `public_process_compare`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 132.1ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 191.6ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 115.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 135.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 146.1ms
- `public_section_aware`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2714.0ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 174.8ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 125.5ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 75.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 75.7ms
- `public_timeline`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 2108.6ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 203.0ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 120.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 83.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 82.2ms
- `public_visibility_boundary`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 126.8ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 163.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 115.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 156.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 140.8ms
- `restricted_doc_denied`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 155.1ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 200.4ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 124.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 153.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 111.5ms
- `restricted_doc_negative`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 431.1ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 620.2ms
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 450.7ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 435.7ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 405.7ms
- `restricted_doc_positive`
  - `langgraph`: keyword pass 3/3, quality 100.0, latency 1008.5ms
  - `crewai`: keyword pass 0/3, quality 80.0, latency 7201.8ms
  - `python_functions`: keyword pass 3/3, quality 100.0, latency 366.3ms
  - `llamaindex`: keyword pass 3/3, quality 100.0, latency 466.2ms
  - `specialist_supervisor`: keyword pass 3/3, quality 100.0, latency 558.9ms

## Failures

- `Q201` `crewai` `public_policy_bridge` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q201` `specialist_supervisor` `public_policy_bridge` quality `80` mode `clarify` reason `specialist_supervisor_strict_safe_fallback` errors `missing_expected_keyword`
- `Q204` `crewai` `public_family_new_bundle` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q206` `crewai` `public_process_compare` quality `80` mode `structured_tool` reason `workflow_not_found` errors `missing_expected_keyword`
- `Q207` `crewai` `public_first_month_risks` quality `80` mode `structured_tool` reason `workflow_not_supported` errors `missing_expected_keyword`
- `Q208` `crewai` `public_deep_multi_doc` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q210` `crewai` `public_visibility_boundary` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q213` `langgraph` `protected_structured_followup` quality `55` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `forbidden_entity_or_value`
- `Q213` `python_functions` `protected_structured_followup` quality `55` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `forbidden_entity_or_value`
- `Q213` `llamaindex` `protected_structured_followup` quality `80` mode `structured_tool` reason `llamaindex_public_profile` errors `missing_expected_keyword`
- `Q213` `specialist_supervisor` `protected_structured_followup` quality `68` mode `clarify` reason `Para identificar os pontos de maior risco acadêmico da Ana, é necessário saber qual é a média mínima para aprovação no Colégio Horizonte, pois a pergunta anterior já indicava a necessidade de comparar com a 'media minima'.` errors `missing_expected_keyword, unnecessary_clarification`
- `Q214` `crewai` `protected_structured_finance` quality `80` mode `structured_tool` reason `crewai_public_flow_timeout` errors `missing_expected_keyword`
- `Q215` `langgraph` `protected_structured_admin` quality `80` mode `structured_tool` reason `a solicitacao pode ser executada por workflow estruturado com protocolo` errors `missing_expected_keyword`
- `Q215` `python_functions` `protected_structured_admin` quality `80` mode `structured_tool` reason `python_functions_native_structured:support` errors `missing_expected_keyword`
- `Q215` `llamaindex` `protected_structured_admin` quality `80` mode `structured_tool` reason `a solicitacao pode ser executada por workflow estruturado com protocolo` errors `missing_expected_keyword`
- `Q216` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `crewai_protected_flow_timeout` errors `missing_expected_keyword`
- `Q217` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q218` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q219` `crewai` `restricted_doc_negative` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`

## Prompt Results

### `Q201` Se um estudante faltar a uma avaliacao por motivo de saude, como os documentos publicos ligam atestado, segunda chamada e recuperacao?

- Retrieval type: `public_policy_bridge`
- Slice: `public`
- `langgraph`: status 200, latency 176.7ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.health_second_call`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `crewai`: status 200, latency 203.7ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 124.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 74.1ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.health_second_call`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 34.5ms, quality `80`, reason `specialist_supervisor_strict_safe_fallback`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### `Q202` No cronograma publico de 2026, em que ordem aparecem abertura da matricula, comeco das aulas e primeiro encontro com responsaveis?

- Retrieval type: `public_timeline`
- Slice: `public`
- `langgraph`: status 200, latency 2108.6ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.timeline_lifecycle`, backend `none`, strategy `direct_answer`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `crewai`: status 200, latency 203.0ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. | 2025-10-06 | familias interessadas | O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. | 2026-02-02 | alunos e familias | A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. | 2026-03-28 | responsaveis e familias | A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `python_functions`: status 200, latency 120.9ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `llamaindex`: status 200, latency 83.3ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.timeline_lifecycle`, backend `none`, strategy `structured_tool`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `specialist_supervisor`: status 200, latency 82.2ms, quality `100`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.

### `Q203` Se a familia ficou sem login justamente na etapa de envio documental, qual e a sequencia mais segura entre portal, credenciais e secretaria?

- Retrieval type: `public_documents_credentials`
- Slice: `public`
- `langgraph`: status 200, latency 2496.4ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `direct_answer`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `crewai`: status 200, latency 167.0ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 119.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 69.8ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials`, backend `none`, strategy `structured_tool`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `specialist_supervisor`: status 200, latency 73.4ms, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### `Q204` Minha familia vai entrar este ano pela primeira vez: como matricula, calendario e agenda de avaliacoes se conectam logo no inicio das aulas?

- Retrieval type: `public_family_new_bundle`
- Slice: `public`
- `langgraph`: status 200, latency 2546.6ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `crewai`: status 200, latency 188.2ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. | 2025-10-06 | familias interessadas | O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. | 2026-02-02 | alunos e familias | A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026. | 2026-03-28 | responsaveis e familias | A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.
- `python_functions`: status 200, latency 113.0ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `llamaindex`: status 200, latency 85.4ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`, backend `none`, strategy `structured_tool`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `specialist_supervisor`: status 200, latency 76.3ms, quality `100`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`, backend `none`, strategy `direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.

### `Q205` Sem usar informacao interna, quais recursos publicos a escola oferece para a familia acompanhar permanencia, apoio e vida escolar?

- Retrieval type: `public_permanence_support`
- Slice: `public`
- `langgraph`: status 200, latency 3192.2ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `crewai`: status 200, latency 171.6ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao educacional, monitorias, comunicados digitais, reunioes periodicas com responsaveis e acionamento de acompanhamento quando frequencia, adaptacao ou rotina de estudo exigem intervencao.
- `python_functions`: status 200, latency 122.6ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 73.1ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.permanence_family_support`, backend `none`, strategy `structured_tool`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 74.9ms, quality `100`, reason `specialist_supervisor_preflight:permanence_family_support`, backend `none`, strategy `direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### `Q206` Quando comparo rematricula, transferencia de entrada e cancelamento, o que muda de verdade em prazo, protocolo e documentos?

- Retrieval type: `public_process_compare`
- Slice: `public`
- `langgraph`: status 200, latency 132.1ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.process_compare`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `crewai`: status 200, latency 191.6ms, quality `80`, reason `workflow_not_found`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao encontrei um protocolo ativo nesta conversa para retomar agora. Se voce quiser, eu posso abrir o pedido, te dizer o protocolo, consultar o status ou montar um resumo quando houver um fluxo ativo.
- `python_functions`: status 200, latency 115.0ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 135.1ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 146.1ms, quality `100`, reason `specialist_supervisor_preflight:process_compare`, backend `none`, strategy `direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### `Q207` Nas primeiras semanas, que descuidos mais costumam estourar em problema de credenciais, documentacao e rotina escolar?

- Retrieval type: `public_first_month_risks`
- Slice: `public`
- `langgraph`: status 200, latency 4676.4ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.first_month_risks`, backend `none`, strategy `direct_answer`
  answer: Olha, nas primeiras semanas, os problemas mais comuns que costumam surgir são a perda de prazos para entrega de documentos, o cadastro desatualizado, o uso inadequado das credenciais de acesso e a falta de atenção aos alertas de frequência e pontualidade. Tudo isso pode acabar comprometendo a rotina escolar e o acesso a informações importantes.

Para evitar isso, é bom ficar de olho nos prazos de entrega de documentos, que podem variar. Você pode enviar pelo portal, e-mail da secretaria ou presencialmente, dependendo do tipo de documento.

É fundamental que cada um use suas próprias credenciais para acessar o portal e os canais da escola. Se tiver qualquer dificuldade com acesso ou senha, ou se precisar atualizar o cadastro, é só entrar em contato com a secretaria ou o suporte.

E, claro, a pontualidade e a frequência nas aulas são muito importantes desde o início para garantir o bom andamento do ano letivo.
- `crewai`: status 200, latency 193.0ms, quality `80`, reason `workflow_not_supported`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa acao agora. Se quiser, me diga se voce quer consultar status, protocolo, remarcar ou cancelar.
- `python_functions`: status 200, latency 121.9ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `llamaindex`: status 200, latency 65.7ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.first_month_risks`, backend `none`, strategy `structured_tool`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `specialist_supervisor`: status 200, latency 74.6ms, quality `100`, reason `specialist_supervisor_preflight:first_month_risks`, backend `none`, strategy `direct_answer`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.

### `Q208` Como os materiais publicos articulam disciplina, frequencia e recuperacao quando o aluno comeca a acumular dificuldades?

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 124.7ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.conduct_frequency_recovery`, backend `none`, strategy `structured_tool`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `crewai`: status 200, latency 186.0ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 120.7ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `llamaindex`: status 200, latency 72.9ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.conduct_frequency_recovery`, backend `none`, strategy `structured_tool`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.
- `specialist_supervisor`: status 200, latency 67.1ms, quality `100`, reason `specialist_supervisor_preflight:conduct_frequency_recovery`, backend `none`, strategy `direct_answer`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.

### `Q209` Na base publica do ensino medio, como biblioteca, laboratorios e apoio ao estudo aparecem amarrados na rotina academica?

- Retrieval type: `public_section_aware`
- Slice: `public`
- `langgraph`: status 200, latency 2714.0ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `crewai`: status 200, latency 174.8ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Biblioteca e laboratorios aparecem como apoio ao estudo do ensino medio: a Biblioteca Aurora oferece consulta, emprestimo e estudo orientado; os laboratorios apoiam aulas praticas, pesquisa e projetos maker; e o contraturno conecta esses espacos a monitorias, cultura digital e projetos interdisciplinares.
- `python_functions`: status 200, latency 125.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `llamaindex`: status 200, latency 75.0ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`, backend `none`, strategy `structured_tool`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `specialist_supervisor`: status 200, latency 75.7ms, quality `100`, reason `specialist_supervisor_preflight:facilities_study_support`, backend `none`, strategy `direct_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.

### `Q210` O que qualquer familia ve no calendario e portal sem login, e o que so surge depois da autenticacao?

- Retrieval type: `public_visibility_boundary`
- Slice: `public`
- `langgraph`: status 200, latency 126.8ms, quality `100`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`, backend `none`, strategy `direct_answer`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `crewai`: status 200, latency 163.2ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 115.9ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `llamaindex`: status 200, latency 156.2ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos gerais como Visita guiada para familias interessadas, Plantao pedagogico do primeiro bimestre, Oficina aberta sobre bolsas e descontos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 140.8ms, quality `100`, reason `specialist_supervisor_fast_path:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### `Q211` Pelos documentos publicos, como comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se encadeiam ao longo do ano letivo?

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 118.6ms, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `crewai`: status 200, latency 171.2ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais funcionam como um circuito unico: o portal publica cronogramas e ajustes, a escola reforca comunicados pelos canais oficiais, e estudo orientado ou acompanhamento adicional entram quando calendario, desempenho ou rotina pedem suporte mais proximo.
- `python_functions`: status 200, latency 134.9ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `llamaindex`: status 200, latency 72.8ms, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.transversal_year`, backend `none`, strategy `structured_tool`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `specialist_supervisor`: status 200, latency 71.0ms, quality `100`, reason `specialist_supervisor_preflight:transversal_year_bundle`, backend `none`, strategy `direct_answer`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.

### `Q212` Quero um panorama academico dos meus filhos com quem esta mais perto da media minima.

- Retrieval type: `protected_structured_academic`
- Slice: `protected`
- `langgraph`: status 200, latency 222.9ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `crewai`: status 200, latency 198.5ms, quality `100`, reason `crewai_protected_identity_backstop`, backend `none`, strategy `None`
  answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.
- `python_functions`: status 200, latency 237.9ms, quality `100`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `llamaindex`: status 200, latency 288.6ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4; Portugues 8,4
Quem hoje aparece mais perto do limite de aprovacao e Lucas Oliveira, principalmente em Quimica.
- `specialist_supervisor`: status 200, latency 221.8ms, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`, backend `none`, strategy `structured_tool`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4

### `Q213` Mantendo o contexto anterior, me diga so os pontos de maior risco da Ana.

- Retrieval type: `protected_structured_followup`
- Slice: `protected`
- `langgraph`: status 200, latency 3648.6ms, quality `55`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: forbidden_entity_or_value
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `crewai`: status 200, latency 20799.2ms, quality `100`, reason `crewai_protected_flow_timeout`, backend `none`, strategy `None`
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora sobre Ana Oliveira. Se quiser, me diga exatamente se voce quer notas, faltas, provas, documentacao, matricula ou financeiro.
- `python_functions`: status 200, latency 2884.7ms, quality `55`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `structured_tool`
  errors: forbidden_entity_or_value
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `llamaindex`: status 200, latency 6988.5ms, quality `80`, reason `llamaindex_public_profile`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Os indicadores publicos mais recentes de Colegio Horizonte sao:
- Aprovacao global: 96.4% (ano letivo 2025)
- Frequencia media: 97.1% (ano letivo 2025)
- Familias que avaliaram o atendimento como bom ou excelente: 92.0% (pesquisa institucional 2025)
- `specialist_supervisor`: status 200, latency 6216.8ms, quality `68`, reason `Para identificar os pontos de maior risco acadêmico da Ana, é necessário saber qual é a média mínima para aprovação no Colégio Horizonte, pois a pergunta anterior já indicava a necessidade de comparar com a 'media minima'.`, backend `none`, strategy `None`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Qual é a média mínima para aprovação no Colégio Horizonte?

### `Q214` Como esta a situacao financeira da familia neste momento, incluindo atrasos, vencimentos proximos e proximo passo?

- Retrieval type: `protected_structured_finance`
- Slice: `protected`
- `langgraph`: status 200, latency 226.2ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `crewai`: status 200, latency 20270.8ms, quality `80`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Poxa, não encontrei detalhes sobre a situação financeira da família nos documentos que consultei. Para te ajudar com isso, o ideal seria entrar em contato diretamente com o serviço responsável.
- `python_functions`: status 200, latency 217.3ms, quality `100`, reason `python_functions_native_structured:finance`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `llamaindex`: status 200, latency 232.1ms, quality `100`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 10 de abril de 2026 (1450.00).
- Ana Oliveira: 2 em aberto, 0 vencida(s), proximo vencimento 10 de marco de 2026 (1450.00).
- `specialist_supervisor`: status 200, latency 201.5ms, quality `100`, reason `specialist_supervisor_resolved_intent:financial_summary_aggregate`, backend `none`, strategy `structured_tool`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00

### `Q215` Sobre a Ana, quais pendencias administrativas ou documentais ainda exigem acao e qual e o proximo passo?

- Retrieval type: `protected_structured_admin`
- Slice: `protected`
- `langgraph`: status 200, latency 176.3ms, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `crewai`: status 200, latency 444.7ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Hoje Ana Oliveira ainda tem pendencias documentais em Documentacao escolar do aluno. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
- `python_functions`: status 200, latency 179.0ms, quality `80`, reason `python_functions_native_structured:support`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 197.8ms, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `specialist_supervisor`: status 200, latency 214.1ms, quality `100`, reason `specialist_supervisor_tool_first:administrative_status`, backend `none`, strategy `structured_tool`
  answer: Hoje Ana Oliveira esta com pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.

### `Q216` No material interno de negociacao financeira, quais criterios orientam a conversa da escola com a familia?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 2183.4ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- `crewai`: status 200, latency 20279.9ms, quality `80`, reason `crewai_protected_flow_timeout`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora. Se quiser, me diga qual aluno e qual dado voce quer consultar.
- `python_functions`: status 200, latency 330.5ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

Fontes:
- Playbook interno de negociacao financeira (v1)
- Procedimento interno para pagamento parcial e negociacao (v2026.3)
- `llamaindex`: status 200, latency 459.4ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Nos documentos internos consultados, a orientacao mais relevante aparece em Playbook interno de negociacao financeira:
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
- `specialist_supervisor`: status 200, latency 548.5ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:
Documento principal: Playbook interno de negociacao financeira.
Secao relevante: Procedimento interno de atendimento financeiro..
Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.

### `Q217` Pelo manual interno do professor, qual e a regra para registro de avaliacoes e comunicacao com foco pedagogico?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 413.0ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

Fontes:
- Manual interno do professor (v1)
- `crewai`: status 200, latency 782.0ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Protocolo interno para responsaveis com escopo parcial (Protocolo interno para responsaveis com escopo parcial): Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
- `python_functions`: status 200, latency 388.9ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

Fontes:
- Manual interno do professor (v1)
- `llamaindex`: status 200, latency 476.6ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
- `specialist_supervisor`: status 200, latency 530.2ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:
Documento principal: Manual interno do professor.
Secao relevante: Procedimento interno de registro academico docente..
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

### `Q218` No protocolo interno para responsaveis com escopo parcial, quais limites de acesso no Telegram sao definidos?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 429.1ms, quality `100`, reason `langgraph_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- `crewai`: status 200, latency 543.4ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao (Procedimento interno para pagamento parcial e negociacao): Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano - Procedimento interno para transferencia no meio do ano > Procedimento interno para transferencia no meio do ano): Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.
- `python_functions`: status 200, latency 379.5ms, quality `100`, reason `python_functions_native_restricted_document_search`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

Fontes:
- Protocolo interno para responsaveis com escopo parcial (v2026.3)
- `llamaindex`: status 200, latency 462.6ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
- `specialist_supervisor`: status 200, latency 598.0ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:
Documento principal: Protocolo interno para responsaveis com escopo parcial.
Secao relevante: Protocolo interno para responsaveis com escopo parcial - Protocolo interno para responsaveis com escopo parcial > Protocolo interno para responsaveis com escopo parcial.
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.

### `Q219` A escola tem documento interno sobre excursao internacional com hospedagem para o ensino medio?

- Retrieval type: `restricted_doc_negative`
- Slice: `restricted`
- `langgraph`: status 200, latency 431.1ms, quality `100`, reason `langgraph_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `crewai`: status 200, latency 620.2ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Secao relevante: Protocolo interno para responsaveis com escopo parcial.
Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.
Procedimento interno para transferencia no meio do ano (Procedimento interno para transferencia no meio do ano): Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Roteiro interno de acolhimento do 6o ano (Rotina interna para acolhimento pedagogico.): No acolhimento do 6o ano, a escola prioriza ambientacao, apresentacao de rotinas, combinados de convivencia e acompanhamento da adaptacao nas primeiras semanas.
- `python_functions`: status 200, latency 450.7ms, quality `100`, reason `python_functions_native_restricted_document_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `llamaindex`: status 200, latency 435.7ms, quality `100`, reason `llamaindex_restricted_doc_no_match`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `specialist_supervisor`: status 200, latency 405.7ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.

### `Q220` Pode me mostrar aqui no bot o manual interno do professor?

- Retrieval type: `restricted_doc_denied`
- Slice: `restricted`
- `langgraph`: status 200, latency 155.1ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `crewai`: status 200, latency 200.4ms, quality `100`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 124.9ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 153.2ms, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 111.5ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

