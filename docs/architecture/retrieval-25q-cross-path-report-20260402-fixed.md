# Four-Path Chatbot Comparison Report

Date: 2026-04-02T16:40:22.400441+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_25q_probe_cases.generated.20260402.json`

Run prefix: `debug:four-path:20260402T163858Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `25/25` | `16/25` | `85.6` | `1412.3 ms` |
| `python_functions` | `25/25` | `16/25` | `85.6` | `138.9 ms` |
| `llamaindex` | `25/25` | `16/25` | `85.6` | `128.5 ms` |
| `specialist_supervisor` | `25/25` | `14/25` | `83.5` | `1641.5 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 4/4, keyword pass 1/4, quality 85.0, latency 231.4ms
  - `python_functions`: ok 4/4, keyword pass 1/4, quality 85.0, latency 207.7ms
  - `llamaindex`: ok 4/4, keyword pass 1/4, quality 85.0, latency 229.9ms
  - `specialist_supervisor`: ok 4/4, keyword pass 0/4, quality 80.0, latency 114.2ms
- `public`
  - `langgraph`: ok 16/16, keyword pass 14/16, quality 97.5, latency 2109.4ms
  - `python_functions`: ok 16/16, keyword pass 14/16, quality 97.5, latency 126.3ms
  - `llamaindex`: ok 16/16, keyword pass 14/16, quality 97.5, latency 96.1ms
  - `specialist_supervisor`: ok 16/16, keyword pass 13/16, quality 95.5, latency 2517.2ms
- `restricted`
  - `langgraph`: ok 5/5, keyword pass 1/5, quality 48.0, latency 126.1ms
  - `python_functions`: ok 5/5, keyword pass 1/5, quality 48.0, latency 124.3ms
  - `llamaindex`: ok 5/5, keyword pass 1/5, quality 48.0, latency 151.2ms
  - `specialist_supervisor`: ok 5/5, keyword pass 1/5, quality 48.0, latency 60.9ms

## Error Types

- `langgraph`: forbidden_entity_or_value=4, missing_expected_keyword=9
- `python_functions`: forbidden_entity_or_value=4, missing_expected_keyword=9
- `llamaindex`: forbidden_entity_or_value=4, missing_expected_keyword=9
- `specialist_supervisor`: forbidden_entity_or_value=4, missing_expected_keyword=11, unnecessary_clarification=1

## Prompt Results

### Se uma prova e perdida por motivo de saude, como atestado, segunda chamada e recuperacao aparecem conectados nos documentos publicos. Responda de forma direta.

- Slice: `public`
- Thread: `retrieval_public_policy_bridge` turn `1`
- `langgraph`: status 200, latency 305.3ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.health_second_call`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `python_functions`: status 200, latency 124.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 81.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.health_second_call`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 156.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### Sem sair do escopo do projeto, no cronograma publico de 2026, em que ordem aparecem abertura da matricula, comeco das aulas e primeiro encontro com responsaveis?

- Slice: `public`
- Thread: `retrieval_public_timeline_sequence` turn `1`
- `langgraph`: status 200, latency 1858.0ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.timeline_lifecycle`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `python_functions`: status 200, latency 116.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `llamaindex`: status 200, latency 97.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.timeline_lifecycle`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `specialist_supervisor`: status 200, latency 47.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.

### Sem sair do escopo do projeto, para resolver acesso e envio documental sem erro, como portal, credenciais e secretaria entram na ordem certa?

- Slice: `public`
- Thread: `retrieval_public_docs_credentials` turn `1`
- `langgraph`: status 200, latency 1590.0ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `python_functions`: status 200, latency 120.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 66.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `specialist_supervisor`: status 200, latency 49.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### Para uma casa que esta entrando no Colegio Horizonte agora, como matricula, inicio das aulas e avaliacoes se relacionam no comeco do ano?

- Slice: `public`
- Thread: `retrieval_public_family_new_bundle` turn `1`
- `langgraph`: status 200, latency 6041.9ms, keyword pass `False`, quality `80`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  errors: missing_expected_keyword
  answer: Olá! Para as famílias que estão chegando agora, o ciclo de matrículas para 2026 foi aberto em 6 de outubro de 2025, com pré-cadastro e visita orientada. As aulas para o Ensino Fundamental II e Médio começam em 2 de fevereiro de 2026, e teremos uma semana especial de acolhimento para o 6º ano e a 1ª série, de 2 a 6 de fevereiro.
- `python_functions`: status 200, latency 121.3ms, keyword pass `False`, quality `80`, reason `python_functions_native_contextual_public_answer`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 140.7ms, keyword pass `False`, quality `80`, reason `contextual_public_direct_answer`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `specialist_supervisor`: status 200, latency 114.3ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_tool_first:public_timeline_bundle`
  errors: missing_expected_keyword
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### Quais apoios publicos evitam que a familia se perca ao acompanhar permanencia e vida escolar do estudante. Responda de forma direta.

- Slice: `public`
- Thread: `retrieval_public_permanence_support` turn `1`
- `langgraph`: status 200, latency 1901.7ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `python_functions`: status 200, latency 163.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 70.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.permanence_family_support`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 51.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:permanence_family_support`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### Quando comparo rematricula, transferencia de entrada e cancelamento, o que muda de verdade em prazo, protocolo e documentos. Traga a resposta de forma concreta.

- Slice: `public`
- Thread: `retrieval_public_process_compare` turn `1`
- `langgraph`: status 200, latency 123.4ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.process_compare`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `python_functions`: status 200, latency 116.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 127.3ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 47.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:process_compare`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### No arranque do ano letivo, que descuidos mais costumam explodir entre credenciais, papelada e rotina da casa?

- Slice: `public`
- Thread: `retrieval_public_first_month_risks` turn `1`
- `langgraph`: status 200, latency 2238.9ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.first_month_risks`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `python_functions`: status 200, latency 129.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `llamaindex`: status 200, latency 67.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.first_month_risks`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `specialist_supervisor`: status 200, latency 18032.5ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_strict_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### Relacione convivencia, frequencia e recuperacao usando os documentos publicos mais relevantes da escola.

- Slice: `public`
- Thread: `retrieval_public_discipline_recovery` turn `1`
- `langgraph`: status 200, latency 126.1ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `python_functions`: status 200, latency 129.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `llamaindex`: status 200, latency 88.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `specialist_supervisor`: status 200, latency 58.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:conduct_frequency_recovery`
  answer: Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.

### Pensando no caso pratico, na base publica do ensino medio, como biblioteca, laboratorios e apoio ao estudo aparecem amarrados na rotina academica?

- Slice: `public`
- Thread: `retrieval_public_facilities_study` turn `1`
- `langgraph`: status 200, latency 2193.1ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.facilities_study_support`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `python_functions`: status 200, latency 134.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `llamaindex`: status 200, latency 83.2ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `specialist_supervisor`: status 200, latency 54.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:facilities_study_support`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.

### Pensando no caso pratico, nos canais digitais da escola, o que ainda e publico e o que passa a depender da autenticacao da familia?

- Slice: `public`
- Thread: `retrieval_public_visibility_boundary` turn `1`
- `langgraph`: status 200, latency 3582.2ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.visibility_boundary`
  answer: Olá! No nosso calendário público, você sempre encontrará os marcos institucionais gerais e os eventos coletivos da escola. Já os detalhes individuais de cada aluno, convites direcionados, protocolos específicos, situações financeiras e acompanhamentos protegidos, esses sim, dependem de autenticação para acesso. Fique tranquila, sempre que houver alguma atualização importante no calendário de avaliações, nós avisaremos pelo portal e pelos nossos canais oficiais.
- `python_functions`: status 200, latency 134.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `llamaindex`: status 200, latency 84.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.visibility_boundary`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 45.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:visibility_boundary`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.

### Como os materiais publicos mostram a relacao entre agenda avaliativa, comunicacao com responsaveis, estudo orientado e meios digitais durante o ano?

- Slice: `public`
- Thread: `retrieval_public_transversal_year` turn `1`
- `langgraph`: status 200, latency 4623.9ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.transversal_year`
  answer: Que bom que você perguntou! No Colégio Horizonte, a agenda avaliativa, a comunicação com os responsáveis, o estudo orientado e os meios digitais trabalham juntos para apoiar o aprendizado. Sempre que há alguma mudança importante no calendário de avaliações, nós atualizamos o portal e avisamos as famílias pelos nossos canais oficiais.

Para o estudo orientado, oferecemos apoio na organização das tarefas, prazos e hábitos de estudo, com atividades como oficinas de leitura e monitorias. Além disso, usamos comunicados digitais e reuniões para manter todos informados, e fazemos chamadas de acompanhamento quando um aluno precisa de um suporte extra.

É importante lembrar que, embora o ambiente digital amplie nosso atendimento, ele não substitui todos os processos formais. Por isso, quando há ajustes ou novas orientações, publicamos no portal, reforçamos pelos canais oficiais e entramos em contato com a família se for necessário um acompanhamento mais próximo.
- `python_functions`: status 200, latency 121.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `llamaindex`: status 200, latency 119.7ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.transversal_year`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `specialist_supervisor`: status 200, latency 13788.4ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_budget_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### Quero comparar rapidamente a situacao academica dos meus dois filhos e saber quem esta mais proximo do limite de aprovacao. Seja objetivo e grounded.

- Slice: `protected`
- Thread: `retrieval_protected_family_panorama` turn `1`
- `langgraph`: status 200, latency 210.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `python_functions`: status 200, latency 187.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 211.8ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 113.2ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_strict_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Mantendo o contexto dos meus filhos, filtre para a Ana e mostre as materias em que ela esta mais vulneravel.

- Slice: `protected`
- Thread: `retrieval_protected_family_panorama` turn `1`
- `langgraph`: status 200, latency 189.4ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Seu perfil nao tem permissao para consultar esses dados academicos.
- `python_functions`: status 200, latency 189.9ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:academic`
  errors: missing_expected_keyword
  answer: Seu perfil nao tem permissao para consultar esses dados academicos.
- `llamaindex`: status 200, latency 184.0ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Seu perfil nao tem permissao para consultar esses dados academicos.
- `specialist_supervisor`: status 200, latency 117.8ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_strict_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Pensando no caso pratico, como esta o financeiro da familia hoje, incluindo vencimentos e proximos passos?

- Slice: `protected`
- Thread: `retrieval_protected_finance_panorama` turn `1`
- `langgraph`: status 200, latency 342.1ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `python_functions`: status 200, latency 263.9ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:finance`
  errors: missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 301.6ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 108.1ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_strict_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Hoje, o que ainda falta na parte administrativa da Ana e como a familia deve agir em seguida?

- Slice: `protected`
- Thread: `retrieval_protected_admin_docs` turn `1`
- `langgraph`: status 200, latency 183.5ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Seu perfil nao tem permissao para consultar a documentacao desse aluno.
- `python_functions`: status 200, latency 189.2ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:institution`
  errors: missing_expected_keyword
  answer: Seu perfil nao tem permissao para consultar a documentacao desse aluno.
- `llamaindex`: status 200, latency 222.0ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Seu perfil nao tem permissao para consultar a documentacao desse aluno.
- `specialist_supervisor`: status 200, latency 117.8ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_strict_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia. Responda de forma direta.

- Slice: `restricted`
- Thread: `retrieval_restricted_finance_playbook` turn `1`
- `langgraph`: status 200, latency 125.6ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 130.4ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 149.3ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 54.9ms, keyword pass `False`, quality `35`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica. Seja objetivo e grounded.

- Slice: `restricted`
- Thread: `retrieval_restricted_teacher_manual` turn `1`
- `langgraph`: status 200, latency 118.7ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 114.4ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 147.1ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 56.4ms, keyword pass `False`, quality `35`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### Pensando no caso pratico, segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil?

- Slice: `restricted`
- Thread: `retrieval_restricted_scope_protocol` turn `1`
- `langgraph`: status 200, latency 120.9ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 122.3ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 149.1ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 72.0ms, keyword pass `False`, quality `35`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### De forma bem objetiva, existe orientacao interna para viagem internacional com hospedagem envolvendo turmas do ensino medio?

- Slice: `restricted`
- Thread: `retrieval_restricted_no_match` turn `1`
- `langgraph`: status 200, latency 124.2ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 132.2ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 155.1ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 62.8ms, keyword pass `False`, quality `35`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### Sou responsavel e quero que voce abra o manual interno do professor para mim. Seja objetivo e grounded.

- Slice: `restricted`
- Thread: `retrieval_restricted_denied` turn `1`
- `langgraph`: status 200, latency 141.3ms, keyword pass `True`, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 122.4ms, keyword pass `True`, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 155.3ms, keyword pass `True`, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 58.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### Por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola?

- Slice: `public`
- Thread: `retrieval_public_service_routing` turn `1`
- `langgraph`: status 200, latency 121.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `python_functions`: status 200, latency 130.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `llamaindex`: status 200, latency 138.8ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `specialist_supervisor`: status 200, latency 118.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_routing`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Direcao: bot, ouvidoria ou protocolo institucional.

### Vocês divulgam o nome ou contato direto do professor de matematica? Se nao, para onde a familia deve ir?

- Slice: `public`
- Thread: `retrieval_public_teacher_directory` turn `1`
- `langgraph`: status 200, latency 3908.6ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.teacher_directory_boundary`
  answer: Olá! No Colégio Horizonte, por questão de privacidade e organização, não divulgamos o nome ou contato direto de professores individualmente. Se precisar conversar sobre algo relacionado à disciplina de matemática, por favor, entre em contato com a coordenação pedagógica. Eles farão a ponte com o professor e te ajudarão com o que for preciso.
- `python_functions`: status 200, latency 114.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.
- `llamaindex`: status 200, latency 69.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.teacher_directory_boundary`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.
- `specialist_supervisor`: status 200, latency 112.4ms, keyword pass `True`, quality `88`, reason `specialist_supervisor_fast_path:teacher_directory`
  errors: unnecessary_clarification
  answer: O Colegio Horizonte nao divulga nomes nem contatos diretos de professores por disciplina, como matematica? se nao, para onde a familia deve ir. Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo para seguir com isso.

### Dentro do calendario publico, quais eventos parecem mais importantes para familias e responsaveis?

- Slice: `public`
- Thread: `retrieval_public_calendar_week` turn `1`
- `langgraph`: status 200, latency 3304.3ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.calendar_week`
  answer: No nosso calendário público, os eventos mais importantes para as famílias e responsáveis são os marcos coletivos e os comunicados institucionais. Qualquer ajuste relevante no calendário de avaliações é sempre atualizado no portal e reforçado pelos nossos canais oficiais. Para detalhes específicos de turma, aluno ou ajustes finos de agenda, a comunicação é feita diretamente com os responsáveis pelos canais autenticados.
- `python_functions`: status 200, latency 118.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No calendario publico da escola, os eventos que mais costumam importar para familias e responsaveis sao marcos coletivos e comunicados institucionais. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Quando algum detalhe depende de turma, aluno ou ajuste fino de agenda, a comunicacao segue para responsaveis pelos canais autenticados e oficiais.
- `llamaindex`: status 200, latency 81.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.calendar_week`
  answer: No calendario publico da escola, os eventos que mais costumam importar para familias e responsaveis sao marcos coletivos e comunicados institucionais. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Quando algum detalhe depende de turma, aluno ou ajuste fino de agenda, a comunicacao segue para responsaveis pelos canais autenticados e oficiais.
- `specialist_supervisor`: status 200, latency 3992.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`
  answer: Dentro do calendário público, os eventos que parecem mais importantes para famílias e responsáveis incluem:

*   **Férias escolares (de verão e de julho):** Períodos cruciais para viagens, atividades em família e organização do cuidado com as crianças.
*   **Natal:** Uma das celebrações familiares mais significativas, com reuniões e troca de presentes.
*   **Ano Novo:** Frequentemente celebrado em família, marcando o início de um novo ciclo.
*   **Páscoa:** Envolve tradições familiares, refeições especiais e atividades com as crianças.
*   **Dia das Mães e Dia dos Pais:** Datas dedicadas à celebração e homenagem aos pais.
*   **Dia das Crianças:** Focado em atividades e presentes para os pequenos.
*   **Carnaval:** Período de feriado prolongado que muitas famílias aproveitam para viajar ou participar de eventos locais.

### Olhando so a base publica, como o ano se distribui entre admissao, rotina academica e fechamento?

- Slice: `public`
- Thread: `retrieval_public_year_three_phases` turn `1`
- `langgraph`: status 200, latency 140.5ms, keyword pass `False`, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `python_functions`: status 200, latency 125.2ms, keyword pass `False`, quality `80`, reason `python_functions_native_contextual_public_answer`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 142.4ms, keyword pass `False`, quality `80`, reason `contextual_public_direct_answer`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 3485.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`
  answer: Um ano acadêmico geralmente se distribui da seguinte forma:

1.  **Admissão:** Ocorre antes do início das aulas, envolvendo processos seletivos, matrículas e planejamento.
2.  **Rotina Acadêmica:** Abrange o período principal de aulas, atividades, avaliações e projetos, distribuídos em semestres ou trimestres.
3.  **Fechamento:** Inclui as avaliações finais, encerramento de disciplinas, formaturas e procedimentos administrativos de final de período.

### Quero um panorama publico da escola sobre politica de avaliacao, recuperacao, promocao, media e frequencia minima.

- Slice: `public`
- Thread: `retrieval_public_academic_policy_overview` turn `1`
- `langgraph`: status 200, latency 1690.9ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `python_functions`: status 200, latency 120.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `llamaindex`: status 200, latency 77.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `specialist_supervisor`: status 200, latency 123.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.

