# Retrieval 20Q Cross-Path Report

Date: 2026-04-02T06:01:13.588967+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_20q_probe_cases.json`

Run prefix: `debug:retrieval20:20260402T055637Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `python_functions` | `19/20` | `6/20` | `78.5` | `354.2 ms` |
| `specialist_supervisor` | `20/20` | `11/20` | `89.8` | `13428.5 ms` |

## By Retrieval Type

- `canonical_family_bundle`
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 1567.0ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 56733.9ms
- `canonical_first_month_bundle`
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 123.7ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 57.4ms
- `canonical_lane_or_docs_bundle`
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 105.1ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 56.2ms
- `canonical_permanence_bundle`
  - `python_functions`: keyword pass 0/1, quality 0.0, latency 89.1ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 28210.5ms
- `canonical_process_compare`
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 125.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 44.8ms
- `deep_public_multi_doc`
  - `python_functions`: keyword pass 0/2, quality 80.0, latency 140.3ms
  - `specialist_supervisor`: keyword pass 1/2, quality 84.0, latency 37001.5ms
- `known_unknown_public_boundary`
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 108.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 3227.3ms
- `protected_followup_context`
  - `python_functions`: keyword pass 0/1, quality 58.0, latency 374.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 21196.8ms
- `protected_structured_academic`
  - `python_functions`: keyword pass 0/1, quality 68.0, latency 185.2ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 20615.9ms
- `protected_structured_admin`
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 200.9ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 30637.4ms
- `protected_structured_finance`
  - `python_functions`: keyword pass 0/1, quality 68.0, latency 185.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 88.0, latency 90.4ms
- `public_policy_section_bridge`
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 344.3ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 5953.1ms
- `public_timeline`
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 120.6ms
  - `specialist_supervisor`: keyword pass 0/1, quality 80.0, latency 61.8ms
- `restricted_document_denied`
  - `python_functions`: keyword pass 0/1, quality 68.0, latency 175.0ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 61.2ms
- `restricted_document_no_match`
  - `python_functions`: keyword pass 1/1, quality 100.0, latency 157.9ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 66.0ms
- `restricted_document_positive`
  - `python_functions`: keyword pass 1/3, quality 82.7, latency 930.2ms
  - `specialist_supervisor`: keyword pass 0/3, quality 80.0, latency 62.7ms
- `section_aware_public`
  - `python_functions`: keyword pass 0/1, quality 80.0, latency 150.5ms
  - `specialist_supervisor`: keyword pass 1/1, quality 100.0, latency 27365.2ms

## Failures

- `Q202` `python_functions` `public_timeline` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q204` `python_functions` `canonical_family_bundle` quality `80` mode `hybrid_retrieval` reason `python_functions_native_public_retrieval` errors `missing_expected_keyword`
- `Q205` `python_functions` `canonical_permanence_bundle` quality `0` mode `error` reason `ValidationError: 3 validation errors for KernelRunResult
plan
  Field required [type=missing, input_value={'message_text': 'A equip...manence_family_support'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
reflection
  Field required [type=missing, input_value={'message_text': 'A equip...manence_family_support'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
response
  Field required [type=missing, input_value={'message_text': 'A equip...manence_family_support'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing` errors `request_failed`
- `Q207` `python_functions` `canonical_first_month_bundle` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q208` `python_functions` `deep_public_multi_doc` quality `80` mode `structured_tool` reason `python_functions_native_contextual_public_answer` errors `missing_expected_keyword`
- `Q209` `python_functions` `section_aware_public` quality `80` mode `structured_tool` reason `python_functions_native_structured:institution` errors `missing_expected_keyword`
- `Q211` `python_functions` `deep_public_multi_doc` quality `80` mode `structured_tool` reason `python_functions_native_structured:institution` errors `missing_expected_keyword`
- `Q212` `python_functions` `protected_structured_academic` quality `68` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, unnecessary_clarification`
- `Q213` `python_functions` `protected_followup_context` quality `58` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, repetitive_reply, unnecessary_clarification`
- `Q214` `python_functions` `protected_structured_finance` quality `68` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, unnecessary_clarification`
- `Q215` `python_functions` `protected_structured_admin` quality `80` mode `structured_tool` reason `python_functions_native_structured:support` errors `missing_expected_keyword`
- `Q216` `python_functions` `restricted_document_positive` quality `68` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, unnecessary_clarification`
- `Q217` `python_functions` `restricted_document_positive` quality `80` mode `structured_tool` reason `python_functions_native_structured:academic` errors `missing_expected_keyword`
- `Q220` `python_functions` `restricted_document_denied` quality `68` mode `clarify` reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` errors `missing_expected_keyword, unnecessary_clarification`
- `Q202` `specialist_supervisor` `public_timeline` quality `80` mode `structured_tool` reason `specialist_supervisor_tool_first:public_timeline_bundle` errors `missing_expected_keyword`
- `Q204` `specialist_supervisor` `canonical_family_bundle` quality `80` mode `hybrid_retrieval` reason `specialist_supervisor_manager_judge:institution:hybrid_retrieval` errors `missing_expected_keyword`
- `Q205` `specialist_supervisor` `canonical_permanence_bundle` quality `80` mode `clarify` reason `specialist_supervisor_grounding_gate:safe_clarify` errors `missing_expected_keyword`
- `Q207` `specialist_supervisor` `canonical_first_month_bundle` quality `80` mode `structured_tool` reason `specialist_supervisor_fast_path:service_credentials_bundle` errors `missing_expected_keyword`
- `Q211` `specialist_supervisor` `deep_public_multi_doc` quality `68` mode `clarify` reason `specialist_supervisor_grounding_gate:clarify` errors `missing_expected_keyword, unnecessary_clarification`
- `Q214` `specialist_supervisor` `protected_structured_finance` quality `88` mode `clarify` reason `specialist_supervisor_resolved_intent:finance_student_clarify` errors `unnecessary_clarification`
- `Q215` `specialist_supervisor` `protected_structured_admin` quality `80` mode `structured_tool` reason `specialist_supervisor_manager_judge:document:structured_tools` errors `missing_expected_keyword`
- `Q216` `specialist_supervisor` `restricted_document_positive` quality `80` mode `hybrid_retrieval` reason `specialist_supervisor_tool_first:restricted_document_no_match` errors `missing_expected_keyword`
- `Q217` `specialist_supervisor` `restricted_document_positive` quality `80` mode `hybrid_retrieval` reason `specialist_supervisor_tool_first:restricted_document_no_match` errors `missing_expected_keyword`
- `Q218` `specialist_supervisor` `restricted_document_positive` quality `80` mode `hybrid_retrieval` reason `specialist_supervisor_tool_first:restricted_document_no_match` errors `missing_expected_keyword`

## Prompt Results

### `Q201` Se um aluno perde prova por motivo de saude, como a politica publica conecta atestado, segunda chamada e recuperacao?

- Retrieval type: `public_policy_section_bridge`
- Slice: `public`
- `python_functions`: status 200, latency 344.3ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 5953.1ms, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`, backend `none`, strategy `direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### `Q202` Qual e a sequencia entre abertura da matricula, inicio das aulas e primeira reuniao com responsaveis em 2026?

- Retrieval type: `public_timeline`
- Slice: `public`
- `python_functions`: status 200, latency 120.6ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `specialist_supervisor`: status 200, latency 61.8ms, quality `80`, reason `specialist_supervisor_tool_first:public_timeline_bundle`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### `Q203` Se eu perder a senha e ainda precisar enviar documentos, em que ordem devo resolver portal, credenciais e secretaria?

- Retrieval type: `canonical_lane_or_docs_bundle`
- Slice: `public`
- `python_functions`: status 200, latency 105.1ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 56.2ms, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### `Q204` Estou chegando agora com meu primeiro filho: como matricula, calendario e agenda de avaliacoes se encaixam no primeiro bimestre?

- Retrieval type: `canonical_family_bundle`
- Slice: `public`
- `python_functions`: status 200, latency 1567.0ms, quality `80`, reason `python_functions_native_public_retrieval`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: A base publica atual nao sustenta com seguranca todos os pontos dessa pergunta, especialmente sobre: agora, bimestre, chegando, encaixam, estou, filho, primeiro. Para evitar uma orientacao incorreta, prefiro nao inferir alem do que esta documentado. Se quiser, eu posso responder apenas o que esta explicitamente registrado na base atual.

Fontes:
- Calendario Letivo 2026 (v2026.2)
- Agenda de Avaliacoes, Recuperacoes e Simulados 2026 (v2026.3)
- Politica de Avaliacao, Recuperacao e Promocao (v2026.3)
- `specialist_supervisor`: status 200, latency 56733.9ms, quality `80`, reason `specialist_supervisor_manager_judge:institution:hybrid_retrieval`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  errors: missing_expected_keyword
  answer: Para a matrícula do seu filho no Colégio Horizonte, o processo inicia com uma visita à escola, apresentação pedagógica e entrevista de acolhimento. Os documentos necessários incluem formulário cadastral preenchido, documento de identificação e CPF do aluno (se houver), histórico escolar, comprovante de residência atualizado e documento de identificação do responsável legal. A documentação inicial pode ser enviada digitalmente, mas a validação final é feita presencialmente na secretaria.

O ano letivo de 2026 para o Ensino Fundamental II e Ensino Médio terá início em 2 de fevereiro de 2026, com uma semana de acolhimento para o 6º ano e a 1ª série entre 2 e 6 de fevereiro. No primeiro bimestre, está prevista uma Reunião Geral de Pais e Responsáveis em 28 de março de 2026, para apresentação do planejamento. Além disso, haverá um Plantão Pedagógico do primeiro bimestre em 11 de abril de 2026, onde os professores estarão disponíveis para esclarecer notas e frequência.

Em relação à agenda de avaliações do primeiro bimestre, as datas específicas não foram detalhadas nos documentos públicos consultados. No entanto, a realização do Plantão Pedagógico em 11 de abril de 2026 para esclarecimento de notas e frequência sugere que as avaliações já terão sido realizadas antes dessa data. Para obter a agenda detalhada das avaliações, é recomendável entrar em contato diretamente com a secretaria ou coordenação pedagógica do Colégio Horizonte.

### `Q205` Que mecanismos publicos a escola descreve para que a familia acompanhe permanencia, apoio e vida escolar sem se perder?

- Retrieval type: `canonical_permanence_bundle`
- Slice: `public`
- `python_functions`: status 599, latency 89.1ms, quality `0`, reason `ValidationError: 3 validation errors for KernelRunResult
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
- `specialist_supervisor`: status 200, latency 28210.5ms, quality `80`, reason `specialist_supervisor_grounding_gate:safe_clarify`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword
  answer: Ainda nao consegui sustentar essa resposta com evidencias suficientes por aqui. Se quiser, reformule em uma frase mais direta ou me diga o assunto exato para eu buscar o canal certo.

### `Q206` Na pratica, o que muda entre rematricula, transferencia de entrada e cancelamento olhando prazos e papelada?

- Retrieval type: `canonical_process_compare`
- Slice: `public`
- `python_functions`: status 200, latency 125.5ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 44.8ms, quality `100`, reason `specialist_supervisor_preflight:process_compare`, backend `none`, strategy `direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### `Q207` Quais deslizes do primeiro mes mais costumam dar problema com credenciais, documentos e rotina?

- Retrieval type: `canonical_first_month_bundle`
- Slice: `public`
- `python_functions`: status 200, latency 123.7ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 57.4ms, quality `80`, reason `specialist_supervisor_fast_path:service_credentials_bundle`, backend `none`, strategy `direct_answer`
  errors: missing_expected_keyword
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### `Q208` Cruze regulamentos gerais, politica de avaliacao e orientacao ao estudante para explicar como disciplina, frequencia e recuperacao se influenciam.

- Retrieval type: `deep_public_multi_doc`
- Slice: `public`
- `python_functions`: status 200, latency 116.2ms, quality `80`, reason `python_functions_native_contextual_public_answer`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `specialist_supervisor`: status 200, latency 57.5ms, quality `100`, reason `specialist_supervisor_tool_first:conduct_frequency_punctuality`, backend `none`, strategy `structured_tool`
  answer: O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia.

### `Q209` Como biblioteca e laboratorios aparecem nas regras de uso e no apoio ao estudo do ensino medio?

- Retrieval type: `section_aware_public`
- Slice: `public`
- `python_functions`: status 200, latency 150.5ms, quality `80`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Hoje Colegio Horizonte atende estes segmentos:
- Ensino Fundamental II (6o ao 9o ano)
- Ensino Medio (1a a 3a serie)
- `specialist_supervisor`: status 200, latency 27365.2ms, quality `100`, reason `specialist_supervisor_manager_judge:institution:document_search`, backend `qdrant_hybrid`, strategy `document_search`
  answer: O Colégio Horizonte oferece a Biblioteca Aurora e os Laboratórios de Ciências para apoiar o estudo no ensino médio. A Biblioteca Aurora funciona de segunda a sexta-feira, das 7h30 às 18h00, e disponibiliza estudo orientado. Os Laboratórios de Ciências são utilizados para aulas práticas, clubes de ciências e mostras semestrais, enriquecendo a aprendizagem em diversas disciplinas. Contudo, não foram encontradas informações detalhadas sobre as regras de uso específicas da biblioteca e dos laboratórios nos documentos públicos consultados.

### `Q210` O que e publico no calendario e no portal, e o que ja depende de autenticacao da familia?

- Retrieval type: `known_unknown_public_boundary`
- Slice: `public`
- `python_functions`: status 200, latency 108.0ms, quality `100`, reason `python_functions_native_contextual_public_answer`, backend `qdrant_hybrid`, strategy `structured_tool`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 3227.3ms, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`, backend `none`, strategy `direct_answer`
  answer: Em geral, funciona assim:

**Público no calendário e no portal:**
*   Datas de eventos gerais (feriados, reuniões abertas, eventos esportivos para o público).
*   Notícias e comunicados de interesse geral.
*   Informações de contato da instituição.
*   Horários de funcionamento.

**Depende de autenticação da família:**
*   Notas e desempenho individual do aluno.
*   Frequência e histórico de presença.
*   Comunicados e mensagens personalizadas para a família.
*   Informações financeiras específicas (mensalidades, pagamentos).
*   Documentos e formulários específicos do aluno ou da família.
*   Agendamento de reuniões individuais com professores.

### `Q211` Monte uma visao transversal de como comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se afetam ao longo do ano.

- Retrieval type: `deep_public_multi_doc`
- Slice: `public`
- `python_functions`: status 200, latency 164.5ms, quality `80`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Hoje o Colegio Horizonte divulga atividades complementares no contraturno de forma assim: - Ensino Fundamental II: Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados. - Ensino Medio: Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00. - Fundamental II e Ensino Medio: Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno. Entre as ofertas que aparecem com mais clareza hoje estao Biblioteca Aurora, Oficina de danca e expressao corporal, Oficina de teatro, Futsal e treinos esportivos, Volei escolar, Espaco Maker.
- `specialist_supervisor`: status 200, latency 73945.5ms, quality `68`, reason `specialist_supervisor_grounding_gate:clarify`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Você gostaria de informações mais detalhadas sobre a política de comunicação com responsáveis, o estudo orientado ou os canais digitais, mesmo que não seja uma visão transversal completa?

### `Q212` Faca um panorama academico dos meus filhos e destaque quem esta mais perto da media minima.

- Retrieval type: `protected_structured_academic`
- Slice: `protected`
- `python_functions`: status 200, latency 185.2ms, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 20615.9ms, quality `100`, reason `specialist_supervisor_direct:academic_specialist`, backend `none`, strategy `structured_tool`
  answer: Aqui está um panorama acadêmico dos seus filhos:

**Lucas Oliveira:**
*   **Média Geral:** 7.22 (considerando a média das médias por disciplina)
*   **Disciplinas com média abaixo de 7.0:**
    *   **Educação Física:** 6.50 (faltam 0.50 para a média)
    *   **Física:** 5.90 (faltam 1.10 para a média)
    *   **Geografia:** 6.50 (faltam 0.50 para a média)
    *   **História:** 6.80 (faltam 0.20 para a média)
    *   **Química:** 6.90 (faltam 0.10 para a média)
    *   **Redação:** 6.70 (faltam 0.30 para a média)
    *   **Tecnologia e Cultura Digital:** 6.80 (faltam 0.20 para a média)

**Ana Oliveira:**
*   **Média Geral:** 7.41 (considerando a média das médias por disciplina)
*   **Disciplinas com média abaixo de 7.0:**
    *   **Física:** 6.40 (faltam 0.60 para a média)

**Quem está mais perto da média mínima (7.0):**
Ana Oliveira está mais perto da média mínima. Ela tem apenas uma disciplina (Física) com a média abaixo de 7.0, precisando de 0.60 pontos para atingir a aprovação nessa matéria. Lucas, por outro lado, tem sete disciplinas abaixo da média, com um total de 2.90 pontos a serem recuperados para atingir a média em todas elas.

### `Q213` Agora foque so na Ana e diga em quais componentes ela esta mais vulneravel.

- Retrieval type: `protected_followup_context`
- Slice: `protected`
- `python_functions`: status 200, latency 374.2ms, quality `58`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, repetitive_reply, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 21196.8ms, quality `100`, reason `specialist_supervisor_direct:academic_specialist`, backend `none`, strategy `structured_tool`
  answer: Ana Oliveira está mais vulnerável nas disciplinas de Física, Matemática, Educação Física e Geografia, apresentando as notas mais baixas e feedbacks que indicam a necessidade de revisão.

### `Q214` Resuma a situacao financeira atual da familia, com vencimentos, atrasos e proximos passos.

- Retrieval type: `protected_structured_finance`
- Slice: `protected`
- `python_functions`: status 200, latency 185.9ms, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 90.4ms, quality `88`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`, backend `none`, strategy `None`
  errors: unnecessary_clarification
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### `Q215` Quais pendencias documentais da Ana ainda pedem acao e qual e o proximo passo recomendado?

- Retrieval type: `protected_structured_admin`
- Slice: `protected`
- `python_functions`: status 200, latency 200.9ms, quality `80`, reason `python_functions_native_structured:support`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `specialist_supervisor`: status 200, latency 30637.4ms, quality `80`, reason `specialist_supervisor_manager_judge:document:structured_tools`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Não foi possível encontrar informações sobre as pendências documentais da Ana. No entanto, sua solicitação foi encaminhada para a secretaria e o protocolo de atendimento é ATD-20260402-3D12B9FD. Eles poderão fornecer as informações detalhadas e os próximos passos recomendados.

### `Q216` No playbook interno de negociacao financeira, quais criterios orientam uma negociacao com a familia?

- Retrieval type: `restricted_document_positive`
- Slice: `restricted`
- `python_functions`: status 200, latency 198.3ms, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 70.2ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para esse pedido. Se quiser, eu posso te orientar pelo material publico correspondente ou abrir um handoff para validacao humana.

### `Q217` Segundo o Manual interno do professor, como a escola orienta registro de avaliacoes e comunicacao pedagogica?

- Retrieval type: `restricted_document_positive`
- Slice: `restricted`
- `python_functions`: status 200, latency 160.4ms, quality `80`, reason `python_functions_native_structured:academic`, backend `none`, strategy `structured_tool`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 58.7ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para esse pedido. Se quiser, eu posso te orientar pelo material publico correspondente ou abrir um handoff para validacao humana.

### `Q218` O Protocolo interno para responsaveis com escopo parcial diz o que sobre limites de acesso no Telegram?

- Retrieval type: `restricted_document_positive`
- Slice: `restricted`
- `python_functions`: status 200, latency 2432.0ms, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`, backend `qdrant_hybrid`, strategy `hybrid_retrieval`
  answer: Olá! Sobre os limites de acesso no Telegram, nosso Protocolo de Uso do Portal, Aplicativo e Credenciais (v2026.3) informa que o atendimento protegido por lá depende da vinculação entre a conta de mensageria e o cadastro institucional. Esse processo é importante para reduzir o risco de exposição de informações restritas, como notas, frequência e dados financeiros.

Se precisar de mais detalhes ou tiver outras dúvidas, é só perguntar!

Fontes:
- Politica de Uso do Portal, Aplicativo e Credenciais (v2026.3)
- Protocolo de Saude, Medicacao e Emergencias (v2026.3)
- Inclusao, Acessibilidade e Seguranca (v2026.2)
- `specialist_supervisor`: status 200, latency 59.2ms, quality `80`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  errors: missing_expected_keyword
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para esse pedido. Se quiser, eu posso te orientar pelo material publico correspondente ou abrir um handoff para validacao humana.

### `Q219` Existe algum procedimento interno sobre excursao internacional com hospedagem para o ensino medio?

- Retrieval type: `restricted_document_no_match`
- Slice: `restricted`
- `python_functions`: status 200, latency 157.9ms, quality `100`, reason `python_functions_native_structured:institution`, backend `none`, strategy `structured_tool`
  answer: Hoje Colegio Horizonte atende estes segmentos:
- Ensino Fundamental II (6o ao 9o ano)
- Ensino Medio (1a a 3a serie)
- `specialist_supervisor`: status 200, latency 66.0ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`, backend `qdrant_hybrid`, strategy `document_search`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para esse pedido. Se quiser, eu posso te orientar pelo material publico correspondente ou abrir um handoff para validacao humana.

### `Q220` Como responsavel, quero ver o manual interno do professor.

- Retrieval type: `restricted_document_denied`
- Slice: `restricted`
- `python_functions`: status 200, latency 175.0ms, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`, backend `none`, strategy `clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 61.2ms, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`, backend `none`, strategy `deny`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

