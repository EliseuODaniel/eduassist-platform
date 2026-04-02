# Retrieval 20Q Cross-Path Report

Date: 2026-04-02T06:13:26.512526+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_20q_probe_cases.json`

Run prefix: `debug:retrieval20:20260402T060753Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `20/20` | `6/20` | `83.2` | `2502.8 ms` |
| `crewai` | `20/20` | `5/20` | `80.3` | `7860.8 ms` |
| `llamaindex` | `19/20` | `6/20` | `79.7` | `6271.6 ms` |

## By Retrieval Type

- `protected_structured_academic`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 1945.2ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 207.2ms
  - `llamaindex`: keyword pass 0/1, quality 68.0, latency 35602.6ms
- `protected_structured_admin`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 157.8ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 456.4ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 191.6ms
- `protected_structured_finance`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 2086.4ms
  - `crewai`: keyword pass 0/1, quality 68.0, latency 20282.2ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 213.8ms
- `protected_structured_followup`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 5657.4ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 20771.3ms
  - `llamaindex`: keyword pass 0/1, quality 58.0, latency 15403.2ms
- `public_deep_multi_doc`
  - `langgraph`: keyword pass 0/2, quality 80.0, latency 133.7ms
  - `crewai`: keyword pass 0/2, quality 80.0, latency 4177.6ms
  - `llamaindex`: keyword pass 0/2, quality 80.0, latency 6014.9ms
- `public_documents_credentials`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 98.0ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 169.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 128.8ms
- `public_family_new_bundle`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 6563.9ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 192.2ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 21011.5ms
- `public_first_month_risks`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 109.3ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 180.6ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 136.0ms
- `public_permanence_support`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 2134.7ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 20282.3ms
  - `llamaindex`: keyword pass 0/1, quality 0.0, latency 12751.0ms
- `public_policy_bridge`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 3621.0ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 1355.9ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 142.4ms
- `public_process_compare`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 151.0ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 20316.8ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 133.0ms
- `public_section_aware`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 5914.0ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 182.3ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 8321.2ms
- `public_timeline`
  - `langgraph`: keyword pass 0/1, quality 80.0, latency 4433.0ms
  - `crewai`: keyword pass 0/1, quality 80.0, latency 247.1ms
  - `llamaindex`: keyword pass 0/1, quality 80.0, latency 128.5ms
- `public_visibility_boundary`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 6122.0ms
  - `crewai`: keyword pass 0/1, quality 68.0, latency 20242.0ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 132.0ms
- `restricted_doc_denied`
  - `langgraph`: keyword pass 0/1, quality 23.0, latency 2431.1ms
  - `crewai`: keyword pass 0/1, quality 23.0, latency 23000.0ms
  - `llamaindex`: keyword pass 0/1, quality 68.0, latency 17704.6ms
- `restricted_doc_no_match`
  - `langgraph`: keyword pass 1/1, quality 100.0, latency 4010.3ms
  - `crewai`: keyword pass 1/1, quality 100.0, latency 218.6ms
  - `llamaindex`: keyword pass 1/1, quality 100.0, latency 362.6ms
- `restricted_doc_positive`
  - `langgraph`: keyword pass 1/3, quality 86.7, latency 1450.9ms
  - `crewai`: keyword pass 1/3, quality 82.7, latency 6919.2ms
  - `llamaindex`: keyword pass 1/3, quality 86.7, latency 346.5ms

## Failures

- `Q201` `crewai` `public_policy_bridge` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q202` `langgraph` `public_timeline` quality `80` mode `structured_tool` reason `datas institucionais publicas devem vir de leitura estruturada e auditavel` errors `missing_expected_keyword`
- `Q202` `crewai` `public_timeline` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q202` `llamaindex` `public_timeline` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q204` `langgraph` `public_family_new_bundle` quality `80` mode `structured_tool` reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno` errors `missing_expected_keyword`
- `Q204` `crewai` `public_family_new_bundle` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q204` `llamaindex` `public_family_new_bundle` quality `80` mode `hybrid_retrieval` reason `llamaindex_public_profile` errors `missing_expected_keyword`
- `Q205` `langgraph` `public_permanence_support` quality `80` mode `structured_tool` reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno` errors `missing_expected_keyword`
- `Q205` `crewai` `public_permanence_support` quality `80` mode `structured_tool` reason `crewai_public_flow_completed` errors `missing_expected_keyword`
- `Q205` `llamaindex` `public_permanence_support` quality `0` mode `error` reason `WorkflowRuntimeError: Error in step 'execute': 3 validation errors for KernelRunResult
plan
  Field required [type=missing, input_value={'message_text': 'A equip...manence_family_support'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
reflection
  Field required [type=missing, input_value={'message_text': 'A equip...manence_family_support'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
response
  Field required [type=missing, input_value={'message_text': 'A equip...manence_family_support'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing` errors `request_failed`
- `Q206` `crewai` `public_process_compare` quality `80` mode `structured_tool` reason `crewai_public_flow_completed` errors `missing_expected_keyword`
- `Q207` `langgraph` `public_first_month_risks` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q207` `crewai` `public_first_month_risks` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q207` `llamaindex` `public_first_month_risks` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q208` `langgraph` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q208` `crewai` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q208` `llamaindex` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `contextual_public_direct_answer` errors `missing_expected_keyword`
- `Q209` `langgraph` `public_section_aware` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q209` `crewai` `public_section_aware` quality `80` mode `structured_tool` reason `crewai_public_fast_path` errors `missing_expected_keyword`
- `Q209` `llamaindex` `public_section_aware` quality `80` mode `structured_tool` reason `llamaindex_public_profile` errors `missing_expected_keyword`
- `Q210` `crewai` `public_visibility_boundary` quality `68` mode `structured_tool` reason `crewai_public_flow_timeout` errors `missing_expected_keyword, unnecessary_clarification`
- `Q211` `langgraph` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` errors `missing_expected_keyword`
- `Q211` `crewai` `public_deep_multi_doc` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q211` `llamaindex` `public_deep_multi_doc` quality `80` mode `structured_tool` reason `fato institucional canonico deve vir de fonte estruturada` errors `missing_expected_keyword`
- `Q212` `langgraph` `protected_structured_academic` quality `80` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword`
- `Q212` `llamaindex` `protected_structured_academic` quality `68` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, unnecessary_clarification`
- `Q213` `langgraph` `protected_structured_followup` quality `80` mode `structured_tool` reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno` errors `missing_expected_keyword`
- `Q213` `llamaindex` `protected_structured_followup` quality `58` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, repetitive_reply, unnecessary_clarification`
- `Q214` `langgraph` `protected_structured_finance` quality `80` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword`
- `Q214` `crewai` `protected_structured_finance` quality `68` mode `structured_tool` reason `crewai_public_flow_timeout` errors `missing_expected_keyword, unnecessary_clarification`
- `Q214` `llamaindex` `protected_structured_finance` quality `80` mode `structured_tool` reason `llamaindex_protected_records_fast_path` errors `missing_expected_keyword`
- `Q215` `langgraph` `protected_structured_admin` quality `80` mode `structured_tool` reason `a solicitacao pode ser executada por workflow estruturado com protocolo` errors `missing_expected_keyword`
- `Q215` `crewai` `protected_structured_admin` quality `80` mode `structured_tool` reason `crewai_protected_fast_path` errors `missing_expected_keyword`
- `Q215` `llamaindex` `protected_structured_admin` quality `80` mode `structured_tool` reason `a solicitacao pode ser executada por workflow estruturado com protocolo` errors `missing_expected_keyword`
- `Q216` `langgraph` `restricted_doc_positive` quality `80` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword`
- `Q216` `crewai` `restricted_doc_positive` quality `88` mode `structured_tool` reason `crewai_public_flow_timeout` errors `unnecessary_clarification`
- `Q217` `langgraph` `restricted_doc_positive` quality `80` mode `structured_tool` reason `dados estruturados devem passar por service deterministico` errors `missing_expected_keyword`
- `Q217` `crewai` `restricted_doc_positive` quality `80` mode `deny` reason `crewai_protected_auth_required` errors `missing_expected_keyword`
- `Q217` `llamaindex` `restricted_doc_positive` quality `80` mode `hybrid_retrieval` reason `llamaindex_restricted_doc_fast_path` errors `missing_expected_keyword`
- `Q218` `crewai` `restricted_doc_positive` quality `80` mode `structured_tool` reason `workflow_not_found` errors `missing_expected_keyword`
- `Q218` `llamaindex` `restricted_doc_positive` quality `80` mode `hybrid_retrieval` reason `llamaindex_restricted_doc_fast_path` errors `missing_expected_keyword`
- `Q220` `langgraph` `restricted_doc_denied` quality `23` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `forbidden_entity_or_value, missing_expected_keyword, unnecessary_clarification`
- `Q220` `crewai` `restricted_doc_denied` quality `23` mode `structured_tool` reason `crewai_public_flow_completed` errors `forbidden_entity_or_value, missing_expected_keyword, unnecessary_clarification`
- `Q220` `llamaindex` `restricted_doc_denied` quality `68` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, unnecessary_clarification`

## Prompt Results

### `Q201` Se um aluno perde prova por motivo de saude, como a politica publica conecta atestado, segunda chamada e recuperacao?

- Retrieval type: `public_policy_bridge`
- Slice: `public`
- `langgraph`: status 200, latency 3621.0ms, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`, backend `qdrant_hybrid`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `crewai`: status 200, latency 1355.9ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `llamaindex`: status 200, latency 142.4ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### `Q202` Qual e a sequencia entre abertura da matricula, inicio das aulas e primeira reuniao com responsaveis em 2026?

- Retrieval type: `public_timeline`
- Slice: `public`
- `langgraph`: status 200, latency 4433.0ms, quality `80`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Olá! Para 2026, as matrículas do Colégio Horizonte foram abertas em 6 de outubro de 2025, com pré-cadastro e visita opcional. As aulas para o Ensino Fundamental II e Médio começam em 2 de fevereiro de 2026, e a semana de acolhimento para o 6º ano e 1ª série será de 2 a 6 de fevereiro.
- `crewai`: status 200, latency 247.1ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. | 2025-10-06 | familias interessadas | O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. | 2026-02-02 | alunos e familias | A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 128.5ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a base publica de Colegio Horizonte nao traz um marco institucional estruturado para essa data.

### `Q203` Se eu perder a senha e ainda precisar enviar documentos, em que ordem devo resolver portal, credenciais e secretaria?

- Retrieval type: `public_documents_credentials`
- Slice: `public`
- `langgraph`: status 200, latency 98.0ms, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 169.0ms, quality `100`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `llamaindex`: status 200, latency 128.8ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### `Q204` Estou chegando agora com meu primeiro filho: como matricula, calendario e agenda de avaliacoes se encaixam no primeiro bimestre?

- Retrieval type: `public_family_new_bundle`
- Slice: `public`
- `langgraph`: status 200, latency 6563.9ms, quality `80`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`, backend `qdrant_hybrid`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Olá! Que bom ter você conosco. Para a matrícula do seu filho em 2026, o ciclo público começou em 6 de outubro de 2025, com pré-cadastro e triagem de documentos. Nosso atendimento comercial continua enquanto houver vagas.

Sobre o primeiro bimestre, temos uma visita guiada para famílias interessadas em 6 de abril de 2026, às 9h, e um plantão pedagógico em 11 de abril de 2026, às 8h.
- `crewai`: status 200, latency 192.2ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `llamaindex`: status 200, latency 21011.5ms, quality `80`, reason `llamaindex_public_profile`, backend `none`, strategy `structured_tool`
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

### `Q205` Que mecanismos publicos a escola descreve para que a familia acompanhe permanencia, apoio e vida escolar sem se perder?

- Retrieval type: `public_permanence_support`
- Slice: `public`
- `langgraph`: status 200, latency 2134.7ms, quality `80`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`, backend `qdrant_hybrid`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Descreve Para Que, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 200, latency 20282.3ms, quality `80`, reason `crewai_public_flow_completed`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `llamaindex`: status 599, latency 12751.0ms, quality `0`, reason `WorkflowRuntimeError: Error in step 'execute': 3 validation errors for KernelRunResult
plan
  Field required [type=missing, input_value={'message_text': 'A equip...manence_family_support'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
reflection
  Field required [type=missing, input_value={'message_text': 'A equip...manence_family_support'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
response
  Field required [type=missing, input_value={'message_text': 'A equip...manence_family_support'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing`, backend `None`, strategy `None`
  errors: request_failed
  answer: 

### `Q206` Na pratica, o que muda entre rematricula, transferencia de entrada e cancelamento olhando prazos e papelada?

- Retrieval type: `public_process_compare`
- Slice: `public`
- `langgraph`: status 200, latency 151.0ms, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `crewai`: status 200, latency 20316.8ms, quality `80`, reason `crewai_public_flow_completed`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `llamaindex`: status 200, latency 133.0ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### `Q207` Quais deslizes do primeiro mes mais costumam dar problema com credenciais, documentos e rotina?

- Retrieval type: `public_first_month_risks`
- Slice: `public`
- `langgraph`: status 200, latency 109.3ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 180.6ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `llamaindex`: status 200, latency 136.0ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### `Q208` Cruze regulamentos gerais, politica de avaliacao e orientacao ao estudante para explicar como disciplina, frequencia e recuperacao se influenciam.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 115.4ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `crewai`: status 200, latency 8175.8ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: A proposta pedagogica publicada hoje combina A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo. Na pratica, isso aparece em frentes como Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes.
- `llamaindex`: status 200, latency 182.1ms, quality `80`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.

### `Q209` Como biblioteca e laboratorios aparecem nas regras de uso e no apoio ao estudo do ensino medio?

- Retrieval type: `public_section_aware`
- Slice: `public`
- `langgraph`: status 200, latency 5914.0ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: A Biblioteca Aurora está disponível para todos os alunos do Ensino Médio, de segunda a sexta, das 7h30 às 18h00. Ela é um espaço importante para o apoio aos estudos e o acesso a recursos.
- `crewai`: status 200, latency 182.3ms, quality `80`, reason `crewai_public_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Sim. Biblioteca Aurora: biblioteca   Biblioteca Aurora   service   True   Atendimento ao publico de segunda a sexta, das 7h30 as 18h00..
- `llamaindex`: status 200, latency 8321.2ms, quality `80`, reason `llamaindex_public_profile`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Hoje Colegio Horizonte atende estes segmentos:
- Ensino Fundamental II (6o ao 9o ano)
- Ensino Medio (1a a 3a serie)

### `Q210` O que e publico no calendario e no portal, e o que ja depende de autenticacao da familia?

- Retrieval type: `public_visibility_boundary`
- Slice: `public`
- `langgraph`: status 200, latency 6122.0ms, quality `100`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`, backend `qdrant_hybrid`, strategy `direct_answer`
  answer: No nosso calendário público, você encontra os marcos institucionais e eventos coletivos da escola. Já os detalhes individuais de cada aluno, convites específicos, informações financeiras e acompanhamentos protegidos são acessíveis apenas com autenticação. Fique tranquila, sempre que houver alguma atualização importante no calendário de avaliações, avisaremos no portal e pelos nossos canais oficiais.
- `crewai`: status 200, latency 20242.0ms, quality `68`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Olá! Os documentos que consultei não especificam quais informações ou serviços são acessíveis sem autenticação no calendário e no portal. Você gostaria de saber sobre quais informações ou serviços específicos você tem interesse em acessar sem autenticação?
- `llamaindex`: status 200, latency 132.0ms, quality `100`, reason `contextual_public_direct_answer`, backend `none`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.

### `Q211` Monte uma visao transversal de como comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se afetam ao longo do ano.

- Retrieval type: `public_deep_multi_doc`
- Slice: `public`
- `langgraph`: status 200, latency 152.0ms, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 179.3ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `llamaindex`: status 200, latency 11847.7ms, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje o Colegio Horizonte divulga atividades complementares no contraturno de forma assim: - Ensino Fundamental II: Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados. - Ensino Medio: Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00. - Fundamental II e Ensino Medio: Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno. Entre as ofertas que aparecem com mais clareza hoje estao Biblioteca Aurora, Oficina de danca e expressao corporal, Oficina de teatro, Futsal e treinos esportivos, Volei escolar, Espaco Maker.

### `Q212` Faca um panorama academico dos meus filhos e destaque quem esta mais perto da media minima.

- Retrieval type: `protected_structured_academic`
- Slice: `protected`
- `langgraph`: status 200, latency 1945.2ms, quality `80`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword
  answer: Para acessar um panorama acadêmico detalhado dos seus filhos e verificar quem está mais próximo da média mínima, é necessário que você se autentique em nosso portal. Lá, você terá acesso a todas as informações de desempenho individual.

Se precisar de ajuda para acessar o portal ou tiver alguma dúvida sobre as informações, a Secretaria Escolar pode te auxiliar.
- `crewai`: status 200, latency 207.2ms, quality `100`, reason `crewai_protected_identity_backstop`, backend `none`, strategy `None`
  answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.
- `llamaindex`: status 200, latency 35602.6ms, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".

### `Q213` Agora foque so na Ana e diga em quais componentes ela esta mais vulneravel.

- Retrieval type: `protected_structured_followup`
- Slice: `protected`
- `langgraph`: status 200, latency 5657.4ms, quality `80`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`, backend `qdrant_hybrid`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Para acessar informações detalhadas sobre o desempenho acadêmico da Ana e identificar os componentes em que ela pode precisar de mais apoio, é necessário que você se autentique em nosso portal. Lá, você terá acesso completo ao histórico dela.
- `crewai`: status 200, latency 20771.3ms, quality `100`, reason `crewai_protected_flow_timeout`, backend `none`, strategy `None`
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora sobre Ana Oliveira. Se quiser, me diga exatamente se voce quer notas, faltas, provas, documentacao, matricula ou financeiro.
- `llamaindex`: status 200, latency 15403.2ms, quality `58`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, repetitive_reply, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".

### `Q214` Resuma a situacao financeira atual da familia, com vencimentos, atrasos e proximos passos.

- Retrieval type: `protected_structured_finance`
- Slice: `protected`
- `langgraph`: status 200, latency 2086.4ms, quality `80`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword
  answer: Para acessar informações detalhadas sobre a situação financeira da família, incluindo vencimentos, atrasos e próximos passos, é necessário que você faça login no portal autenticado da escola. Lá, você terá acesso seguro e personalizado a todos os dados financeiros.

Se precisar de ajuda para acessar o portal ou tiver alguma dúvida específica, nossa equipe do setor financeiro está à disposição para auxiliar. Você pode entrar em contato com eles por e-mail institucional ou presencialmente.
- `crewai`: status 200, latency 20282.2ms, quality `68`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Para ter um resumo da sua situação financeira específica, incluindo vencimentos, atrasos e próximos passos, você precisará entrar em contato com o departamento financeiro da escola. Gostaria de saber como fazer isso?
- `llamaindex`: status 200, latency 213.8ms, quality `80`, reason `llamaindex_protected_records_fast_path`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Situacao administrativa do seu cadastro hoje: com pendencias.

### `Q215` Quais pendencias documentais da Ana ainda pedem acao e qual e o proximo passo recomendado?

- Retrieval type: `protected_structured_admin`
- Slice: `protected`
- `langgraph`: status 200, latency 157.8ms, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `crewai`: status 200, latency 456.4ms, quality `80`, reason `crewai_protected_fast_path`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: O proximo pagamento de Ana Oliveira vence em 2026-03-10 no valor de 1450.00.
- `llamaindex`: status 200, latency 191.6ms, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.

### `Q216` No playbook interno de negociacao financeira, quais criterios orientam uma negociacao com a familia?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 2069.1ms, quality `80`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword
  answer: Compreendo sua pergunta sobre os critérios de negociação financeira. No entanto, o playbook interno de negociação financeira é um documento restrito e não temos acesso a ele para compartilhar os critérios específicos.

Para informações sobre negociações financeiras, o ideal é entrar em contato diretamente com o setor financeiro da escola. Eles poderão te orientar sobre os procedimentos e critérios aplicáveis.
- `crewai`: status 200, latency 20269.7ms, quality `88`, reason `crewai_public_flow_timeout`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Olá! Para te ajudar com a sua pergunta sobre negociação financeira, os documentos que temos descrevem os serviços financeiros disponíveis, como bolsas, descontos e simulação financeira inicial, além do atendimento comercial para famílias. Você gostaria de saber mais sobre esses serviços ou especificamente sobre os critérios para a concessão de bolsas e descontos?
- `llamaindex`: status 200, latency 348.5ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para pagamento parcial e negociacao:
Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Playbook interno de negociacao financeira: Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Procedimento interno para transferencia no meio do ano: Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

### `Q217` Segundo o Manual interno do professor, como a escola orienta registro de avaliacoes e comunicacao pedagogica?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 187.5ms, quality `80`, reason `dados estruturados devem passar por service deterministico`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Orienta Registro Avaliacoes, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 200, latency 273.4ms, quality `80`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `llamaindex`: status 200, latency 364.6ms, quality `80`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Manual interno do professor:
Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.
Roteiro interno de acolhimento do 6o ano: No acolhimento do 6o ano, a escola prioriza ambientacao, apresentacao de rotinas, combinados de convivencia e acompanhamento da adaptacao nas primeiras semanas.
Procedimento interno para transferencia no meio do ano: Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.

### `Q218` O Protocolo interno para responsaveis com escopo parcial diz o que sobre limites de acesso no Telegram?

- Retrieval type: `restricted_doc_positive`
- Slice: `restricted`
- `langgraph`: status 200, latency 2096.1ms, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Olá! Sobre o acesso no Telegram, o atendimento protegido por lá depende da vinculação da sua conta de mensageria com o cadastro institucional. Esse processo é importante para proteger informações restritas, como notas, frequência e dados financeiros.

Fontes:
- Politica de Uso do Portal, Aplicativo e Credenciais (v2026.3)
- Protocolo de Saude, Medicacao e Emergencias (v2026.3)
- Inclusao, Acessibilidade e Seguranca (v2026.2)
- `crewai`: status 200, latency 214.6ms, quality `80`, reason `workflow_not_found`, backend `none`, strategy `None`
  errors: missing_expected_keyword
  answer: Nao encontrei um protocolo ativo nesta conversa para retomar agora. Se voce quiser, eu posso abrir o pedido, te dizer o protocolo, consultar o status ou montar um resumo quando houver um fluxo ativo.
- `llamaindex`: status 200, latency 326.4ms, quality `80`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Protocolo interno para responsaveis com escopo parcial:
Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. Excecoes dependem de validacao humana formal.
Procedimento interno para pagamento parcial e negociacao: Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. O sistema nao deve assumir quitacao total sem evidencia transacional.
Procedimento interno para transferencia no meio do ano: Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. O atendimento humano coordena a conclusao do caso.

### `Q219` Existe algum procedimento interno sobre excursao internacional com hospedagem para o ensino medio?

- Retrieval type: `restricted_doc_no_match`
- Slice: `restricted`
- `langgraph`: status 200, latency 4010.3ms, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`, backend `none`, strategy `direct_answer`
  answer: Hoje Colegio Horizonte atende estes segmentos:
- Ensino Fundamental II (6o ao 9o ano)
- Ensino Medio (1a a 3a serie)
- `crewai`: status 200, latency 218.6ms, quality `100`, reason `crewai_protected_auth_required`, backend `none`, strategy `None`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `llamaindex`: status 200, latency 362.6ms, quality `100`, reason `llamaindex_restricted_doc_fast_path`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Nos documentos internos consultados, a orientacao mais relevante aparece em Procedimento interno para transferencia no meio do ano:
Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. A secretaria registra protocolo e acompanha a emissao dos documentos finais.
Playbook interno de negociacao financeira: Em casos de atraso, a equipe financeira deve registrar contexto, verificar historico recente de pagamentos e orientar proposta de regularizacao antes de prometer condicao excepcional.
Manual interno do professor: Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.

### `Q220` Como responsavel, quero ver o manual interno do professor.

- Retrieval type: `restricted_doc_denied`
- Slice: `restricted`
- `langgraph`: status 200, latency 2431.1ms, quality `23`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: forbidden_entity_or_value, missing_expected_keyword, unnecessary_clarification
  answer: Olá! Como responsável, entendo seu interesse em conhecer melhor os materiais da escola. No entanto, o manual interno do professor é um documento de uso exclusivo dos nossos educadores.

Se você tiver alguma dúvida específica sobre a metodologia de ensino, o currículo ou o dia a dia pedagógico, posso te ajudar a encontrar as informações em nossos documentos públicos ou direcionar sua pergunta para a coordenação pedagógica.

Com quem você gostaria de falar sobre o assunto?
- `crewai`: status 200, latency 23000.0ms, quality `23`, reason `crewai_public_flow_completed`, backend `none`, strategy `None`
  errors: forbidden_entity_or_value, missing_expected_keyword, unnecessary_clarification
  answer: Olá! Não encontrei informações sobre o manual interno do professor nos documentos disponíveis. Você gostaria de saber sobre outro tópico relacionado a professores ou à escola?
- `llamaindex`: status 200, latency 17704.6ms, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".

