# Four-Path Chatbot Comparison Report

Date: 2026-04-03T00:26:09.122534+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_50q_probe_cases.generated.20260402.json`

Run prefix: `debug:four-path:20260403T002115Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `50/50` | `35/50` | `91.1` | `719.4 ms` |
| `python_functions` | `50/50` | `36/50` | `90.5` | `325.4 ms` |
| `llamaindex` | `50/50` | `35/50` | `91.1` | `1222.8 ms` |
| `specialist_supervisor` | `50/50` | `36/50` | `91.5` | `3524.9 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 12/12, keyword pass 9/12, quality 95.0, latency 285.2ms
  - `python_functions`: ok 12/12, keyword pass 9/12, quality 95.0, latency 289.9ms
  - `llamaindex`: ok 12/12, keyword pass 9/12, quality 95.0, latency 309.1ms
  - `specialist_supervisor`: ok 12/12, keyword pass 10/12, quality 95.7, latency 694.7ms
- `public`
  - `langgraph`: ok 29/29, keyword pass 20/29, quality 93.4, latency 981.4ms
  - `python_functions`: ok 29/29, keyword pass 21/29, quality 92.4, latency 361.3ms
  - `llamaindex`: ok 29/29, keyword pass 20/29, quality 93.4, latency 1887.9ms
  - `specialist_supervisor`: ok 29/29, keyword pass 20/29, quality 93.8, latency 5726.6ms
- `restricted`
  - `langgraph`: ok 9/9, keyword pass 6/9, quality 78.3, latency 454.0ms
  - `python_functions`: ok 9/9, keyword pass 6/9, quality 78.3, latency 256.7ms
  - `llamaindex`: ok 9/9, keyword pass 6/9, quality 78.3, latency 298.0ms
  - `specialist_supervisor`: ok 9/9, keyword pass 6/9, quality 78.3, latency 204.2ms

## Error Types

- `langgraph`: forbidden_entity_or_value=3, missing_expected_keyword=15, unnecessary_clarification=1
- `python_functions`: forbidden_entity_or_value=3, missing_expected_keyword=14, unnecessary_clarification=5
- `llamaindex`: forbidden_entity_or_value=3, missing_expected_keyword=15, unnecessary_clarification=1
- `specialist_supervisor`: forbidden_entity_or_value=3, missing_expected_keyword=14, unnecessary_clarification=1

## Prompt Results

### Pensando no caso pratico, pelos documentos publicos, como atestado de saude, segunda chamada e recuperacao se encadeiam quando o estudante perde uma avaliacao?

- Slice: `public`
- Thread: `retrieval_public_policy_bridge` turn `1`
- `langgraph`: status 200, latency 346.4ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.health_second_call`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `python_functions`: status 200, latency 149.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 88.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.health_second_call`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 196.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

### No cronograma publico de 2026, em que ordem aparecem abertura da matricula, comeco das aulas e primeiro encontro com responsaveis. Traga a resposta de forma concreta.

- Slice: `public`
- Thread: `retrieval_public_timeline_sequence` turn `1`
- `langgraph`: status 200, latency 166.4ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.timeline_lifecycle`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `python_functions`: status 200, latency 146.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `llamaindex`: status 200, latency 159.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.timeline_lifecycle`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Depois do inicio das aulas: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Primeira reuniao com responsaveis: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026.
- `specialist_supervisor`: status 200, latency 71.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.

### Para resolver acesso e envio documental sem erro, como portal, credenciais e secretaria entram na ordem certa. Traga a resposta de forma concreta.

- Slice: `public`
- Thread: `retrieval_public_docs_credentials` turn `1`
- `langgraph`: status 200, latency 185.4ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.secretaria_portal_credentials`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `python_functions`: status 200, latency 207.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `llamaindex`: status 200, latency 161.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.secretaria_portal_credentials`
  answer: Para documentos, portal e credenciais, a familia precisa tratar secretaria, canais digitais e suporte como um fluxo unico. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional.
- `specialist_supervisor`: status 200, latency 69.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:service_credentials_bundle`
  answer: Hoje o fluxo publico converge assim: a secretaria centraliza prazos, protocolos e documentacao; o portal e o aplicativo concentram acesso digital e credenciais; e a politica publica orienta como ativar, recuperar e usar essas credenciais com seguranca.

### Sem sair do escopo do projeto, entrando pela primeira vez na escola, como a familia deve juntar calendario, matricula e agenda de avaliacoes para nao perder marcos do primeiro bimestre?

- Slice: `public`
- Thread: `retrieval_public_family_new_bundle` turn `1`
- `langgraph`: status 200, latency 158.6ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `python_functions`: status 200, latency 152.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `llamaindex`: status 200, latency 132.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `specialist_supervisor`: status 200, latency 67.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Matricula: o manual orienta a entrada correta e a documentacao inicial. Calendario: o calendario letivo organiza o comeco do ano e os primeiros marcos escolares. Avaliacoes: a agenda avaliativa mostra quando entram devolutivas, provas e recuperacoes. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.

### De forma bem objetiva, pelos documentos publicos, como a familia acompanha permanencia escolar, apoio e vida escolar sem precisar recorrer a material interno?

- Slice: `public`
- Thread: `retrieval_public_permanence_support` turn `1`
- `langgraph`: status 200, latency 134.9ms, keyword pass `False`, quality `80`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 157.2ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 194.9ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 72.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:permanence_family_support`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### Se eu comparar rematricula, transferencia e cancelamento, quais mudancas reais aparecem em prazos e documentacao. Responda de forma direta.

- Slice: `public`
- Thread: `retrieval_public_process_compare` turn `1`
- `langgraph`: status 200, latency 166.1ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.process_compare`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `python_functions`: status 200, latency 147.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 117.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.process_compare`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 17360.4ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_budget_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### Nas primeiras semanas, que descuidos mais costumam estourar em problema de credenciais, documentacao e rotina escolar. Traga a resposta de forma concreta.

- Slice: `public`
- Thread: `retrieval_public_first_month_risks` turn `1`
- `langgraph`: status 200, latency 213.4ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.first_month_risks`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `python_functions`: status 200, latency 143.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `llamaindex`: status 200, latency 93.2ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.first_month_risks`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `specialist_supervisor`: status 200, latency 73.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:first_month_risks`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.

### De forma bem objetiva, junte regulamento, frequencia e recuperacao para explicar o que a escola faz quando o aluno entra em zona de risco academico.

- Slice: `public`
- Thread: `retrieval_public_discipline_recovery` turn `1`
- `langgraph`: status 200, latency 155.8ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `python_functions`: status 200, latency 176.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `llamaindex`: status 200, latency 128.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `specialist_supervisor`: status 200, latency 58.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.

### Sem sair do escopo do projeto, como biblioteca e laboratorios entram nas regras de uso e no apoio ao estudo do ensino medio?

- Slice: `public`
- Thread: `retrieval_public_facilities_study` turn `1`
- `langgraph`: status 200, latency 184.4ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.facilities_study_support`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `python_functions`: status 200, latency 148.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `llamaindex`: status 200, latency 101.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.
- `specialist_supervisor`: status 200, latency 62.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:facilities_study_support`
  answer: Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. A biblioteca da escola se chama Biblioteca Aurora. A Biblioteca Aurora oferece consulta local, emprestimo domiciliar para alunos regularmente matriculados, apoio a projetos de pesquisa e uso de mesas de estudo em grupo mediante agendamento no portal institucional. O laboratorio de ciencias funciona prioritariamente por agendamento docente e apoio a aulas praticas. O laboratorio de informatica apoia aulas de tecnologia, pesquisa e producao de trabalhos. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.

### Sem sair do escopo do projeto, nos canais da escola, onde termina o conteudo publico e onde comeca o que exige autenticacao da familia?

- Slice: `public`
- Thread: `retrieval_public_visibility_boundary` turn `1`
- `langgraph`: status 200, latency 181.7ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.visibility_boundary`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `python_functions`: status 200, latency 140.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `llamaindex`: status 200, latency 128.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.visibility_boundary`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 12260.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Nos canais do Colégio Horizonte, o conteúdo público abrange informações gerais sobre a escola, seu projeto pedagógico, currículo, equipes de liderança, calendário de eventos abertos (como reuniões de pais e mostras culturais), dados de contato e descrições dos serviços oferecidos. Qualquer informação que não seja específica de um aluno ou família é considerada pública e está acessível a todos.

Conteúdos que exigem autenticação da família são aqueles relacionados a informações individualizadas e sensíveis, como:

*   **Documentos e processos de matrícula:** Embora o envio inicial possa ser digital, a validação final e a submissão de documentos completos ou dados sensíveis devem ser feitas pelo portal institucional autenticado ou e-mail da secretaria, e não pelo chat aberto.
*   **Informações financeiras:** Boletos, vencimentos, contratos, acordos e esclarecimentos financeiros são tratados através do portal autenticado ou diretamente com o departamento financeiro.
*   **Acompanhamento pedagógico e socioemocional individualizado:** Reuniões com a coordenação pedagógica ou orientação educacional, bem como o acesso a notas, frequência e outros detalhes acadêmicos ou de bem-estar específicos do estudante, são acessados por canais que exigem autenticação, como o portal escolar ou comunicação direta (e-mail, secretaria).
*   **Suporte digital e acesso ao portal:** Questões de acesso, senhas e dificuldades no uso do portal escolar são direcionadas ao suporte digital, que pode exigir autenticação para resolver problemas específicos do usuário.

Em resumo, a escola disponibiliza abertamente informações de caráter geral, mas para assuntos pessoais de estudantes e famílias, como dados financeiros, envio de documentos sensíveis ou acompanhamento individual, é necessário utilizar os canais autenticados, como o portal escolar, para garantir a segurança e a privacidade das informações.

### Pensando no caso pratico, ao longo do ano letivo, como comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais passam a depender uns dos outros?

- Slice: `public`
- Thread: `retrieval_public_transversal_year` turn `1`
- `langgraph`: status 200, latency 160.4ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.transversal_year`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `python_functions`: status 200, latency 142.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `llamaindex`: status 200, latency 106.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.transversal_year`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.
- `specialist_supervisor`: status 200, latency 64.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:transversal_year_bundle`
  answer: Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais. Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.

### Faca um resumo academico dos meus dois filhos e destaque qual deles esta mais perto do corte de aprovacao. Seja objetivo e grounded.

- Slice: `protected`
- Thread: `retrieval_protected_family_panorama` turn `1`
- `langgraph`: status 200, latency 256.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `python_functions`: status 200, latency 251.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `llamaindex`: status 200, latency 271.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `specialist_supervisor`: status 200, latency 191.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate_fallback`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina.

### Pensando no caso pratico, agora quero apenas a Ana: em quais materias ela aparece mais exposta?

- Slice: `protected`
- Thread: `retrieval_protected_family_panorama` turn `1`
- `langgraph`: status 200, latency 284.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o resumo academico detalhado para apontar com seguranca os maiores riscos.
- `python_functions`: status 200, latency 255.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o resumo academico detalhado para apontar com seguranca os maiores riscos.
- `llamaindex`: status 200, latency 284.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o resumo academico detalhado para apontar com seguranca os maiores riscos.
- `specialist_supervisor`: status 200, latency 180.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_scoped_fallback`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.

### De forma bem objetiva, como esta a situacao financeira da familia neste momento, incluindo atrasos, vencimentos proximos e proximo passo?

- Slice: `protected`
- Thread: `retrieval_protected_finance_panorama` turn `1`
- `langgraph`: status 200, latency 259.4ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Resumo financeiro da familia hoje: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora os vencimentos e proximos passos detalhados, mas o recorte continua sendo o financeiro das contas vinculadas.
- `python_functions`: status 200, latency 279.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro da familia hoje: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora os vencimentos e proximos passos detalhados, mas o recorte continua sendo o financeiro das contas vinculadas.
- `llamaindex`: status 200, latency 324.2ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Resumo financeiro da familia hoje: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora os vencimentos e proximos passos detalhados, mas o recorte continua sendo o financeiro das contas vinculadas.
- `specialist_supervisor`: status 200, latency 213.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:financial_summary_aggregate_fallback`
  answer: Resumo financeiro da familia hoje: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora os vencimentos e proximos passos detalhados.

### Quero ver o quadro documental da Ana: o que esta pendente e o que a familia precisa fazer em seguida. Responda de forma direta.

- Slice: `protected`
- Thread: `retrieval_protected_admin_docs` turn `1`
- `langgraph`: status 200, latency 214.8ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje Ana Oliveira ainda aparece com pendencias administrativas. Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo seguir pelo portal autenticado ou pela secretaria escolar.
- `python_functions`: status 200, latency 240.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje Ana Oliveira ainda aparece com pendencias administrativas. Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo seguir pelo portal autenticado ou pela secretaria escolar.
- `llamaindex`: status 200, latency 262.3ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje Ana Oliveira ainda aparece com pendencias administrativas. Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo seguir pelo portal autenticado ou pela secretaria escolar.
- `specialist_supervisor`: status 200, latency 164.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:administrative_status_scoped_fallback`
  answer: Hoje Ana Oliveira ainda aparece com pendencias administrativas. Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo seguir pelo portal autenticado ou pela secretaria escolar.

### Pensando no caso pratico, quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia?

- Slice: `restricted`
- Thread: `retrieval_restricted_finance_playbook` turn `1`
- `langgraph`: status 200, latency 1819.8ms, keyword pass `True`, quality `100`, reason `langgraph_restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia".
- `python_functions`: status 200, latency 291.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia".
- `llamaindex`: status 200, latency 332.4ms, keyword pass `True`, quality `100`, reason `llamaindex_restricted_doc_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia".
- `specialist_supervisor`: status 200, latency 515.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para: "Pensando no caso pratico, quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia".

### O manual interno do professor diz o que sobre registro de avaliacoes e comunicacao pedagogica. Traga a resposta de forma concreta.

- Slice: `restricted`
- Thread: `retrieval_restricted_teacher_manual` turn `1`
- `langgraph`: status 200, latency 486.8ms, keyword pass `True`, quality `100`, reason `langgraph_restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "O manual interno do professor diz o que sobre registro de avaliacoes e comunicacao pedagogica. Traga a resposta de forma concreta".
- `python_functions`: status 200, latency 322.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "O manual interno do professor diz o que sobre registro de avaliacoes e comunicacao pedagogica. Traga a resposta de forma concreta".
- `llamaindex`: status 200, latency 366.5ms, keyword pass `True`, quality `100`, reason `llamaindex_restricted_doc_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "O manual interno do professor diz o que sobre registro de avaliacoes e comunicacao pedagogica. Traga a resposta de forma concreta".
- `specialist_supervisor`: status 200, latency 265.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para: "O manual interno do professor diz o que sobre registro de avaliacoes e comunicacao pedagogica. Traga a resposta de forma concreta".

### Como o protocolo interno de escopo parcial descreve as restricoes de acesso no Telegram para esse tipo de responsavel. Traga a resposta de forma concreta.

- Slice: `restricted`
- Thread: `retrieval_restricted_scope_protocol` turn `1`
- `langgraph`: status 200, latency 436.2ms, keyword pass `True`, quality `100`, reason `langgraph_restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Como o protocolo interno de escopo parcial descreve as restricoes de acesso no Telegram para esse tipo de responsavel. Traga a resposta de forma concreta".
- `python_functions`: status 200, latency 296.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Como o protocolo interno de escopo parcial descreve as restricoes de acesso no Telegram para esse tipo de responsavel. Traga a resposta de forma concreta".
- `llamaindex`: status 200, latency 387.2ms, keyword pass `True`, quality `100`, reason `llamaindex_restricted_doc_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: "Como o protocolo interno de escopo parcial descreve as restricoes de acesso no Telegram para esse tipo de responsavel. Traga a resposta de forma concreta".
- `specialist_supervisor`: status 200, latency 383.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica para: "Como o protocolo interno de escopo parcial descreve as restricoes de acesso no Telegram para esse tipo de responsavel. Traga a resposta de forma concreta".

### Os documentos internos mencionam algum protocolo para excursao internacional com pernoite no ensino medio. Traga a resposta de forma concreta.

- Slice: `restricted`
- Thread: `retrieval_restricted_no_match` turn `1`
- `langgraph`: status 200, latency 379.2ms, keyword pass `True`, quality `100`, reason `langgraph_restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `python_functions`: status 200, latency 364.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `llamaindex`: status 200, latency 402.1ms, keyword pass `True`, quality `100`, reason `llamaindex_restricted_doc_no_match`
  answer: Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.
- `specialist_supervisor`: status 200, latency 271.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_no_match`
  answer: Consultei os documentos internos disponiveis do Colegio Horizonte, mas nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio.

### De forma bem objetiva, pode me mostrar aqui no bot o manual interno do professor?

- Slice: `restricted`
- Thread: `retrieval_restricted_denied` turn `1`
- `langgraph`: status 200, latency 263.0ms, keyword pass `True`, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 287.3ms, keyword pass `True`, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 259.1ms, keyword pass `True`, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 89.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### Com quem eu falo sobre bolsa, financeiro e direcao? Quero os setores e canais mais diretos.

- Slice: `public`
- Thread: `retrieval_public_service_routing` turn `1`
- `langgraph`: status 200, latency 189.8ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `python_functions`: status 200, latency 180.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `llamaindex`: status 200, latency 184.7ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- `specialist_supervisor`: status 200, latency 163.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_routing`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Direcao: bot, ouvidoria ou protocolo institucional.

### Para falar com o professor de matematica, o contato e publico ou a familia precisa passar pela coordenacao?

- Slice: `public`
- Thread: `retrieval_public_teacher_directory` turn `1`
- `langgraph`: status 200, latency 183.7ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.teacher_directory_boundary`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.
- `python_functions`: status 200, latency 164.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.
- `llamaindex`: status 200, latency 111.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.teacher_directory_boundary`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.
- `specialist_supervisor`: status 200, latency 61.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:teacher_directory_boundary`
  answer: O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional.

### Quais eventos publicos para familias e responsaveis aparecem nesta base agora?

- Slice: `public`
- Thread: `retrieval_public_calendar_week` turn `1`
- `langgraph`: status 200, latency 1799.9ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: No momento, a base de informações que tenho não apresenta nenhum evento público específico para famílias e responsáveis.
- `python_functions`: status 200, latency 249.7ms, keyword pass `False`, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 7566.0ms, keyword pass `False`, quality `80`, reason `llamaindex_public_profile`
  errors: missing_expected_keyword
  answer: Hoje a base publica de eventos de Colegio Horizonte nao trouxe agenda estruturada para esse pedido.
- `specialist_supervisor`: status 200, latency 2612.4ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_fast_path:general_knowledge`
  errors: missing_expected_keyword
  answer: Não tenho acesso a informações em tempo real sobre eventos específicos ou bases de dados locais.

### Se eu resumir o ano escolar em tres etapas publicas, como aparecem admissao, rotina academica e fechamento?

- Slice: `public`
- Thread: `retrieval_public_year_three_phases` turn `1`
- `langgraph`: status 200, latency 3034.7ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Olá! Para resumir o ano escolar no Colégio Horizonte em três etapas públicas, podemos organizar da seguinte forma:

1.  **Admissão:** Esta etapa geralmente ocorre antes do início das aulas e inclui o processo de matrícula, que pode ser feito através do nosso bot, setor de admissões, WhatsApp comercial ou com uma visita guiada à escola. Também é o momento para agendar visitas e conhecer nossas instalações.
2.  **Rotina Acadêmica:** Durante o ano letivo, esta fase abrange o dia a dia dos estudantes, com as aulas, atividades curriculares e extracurriculares. É quando acontecem as reuniões com a coordenação pedagógica, o acompanhamento da orientação educacional e o uso do Espaço Maker. A secretaria escolar e o portal do aluno são os canais para documentos e informações acadêmicas.
3.  **Fechamento:** Ao final do ano, esta etapa envolve a conclusão das atividades acadêmicas, avaliações finais e, para os alunos que concluem um ciclo, a preparação para a próxima fase. O financeiro escolar e os contratos também são tratados neste período, através do nosso bot, setor financeiro, portal autenticado ou e-mail institucional.

Espero que essa organização ajude a entender melhor o fluxo do ano escolar aqui no Colégio Horizonte!
- `python_functions`: status 200, latency 259.0ms, keyword pass `False`, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 13175.4ms, keyword pass `False`, quality `80`, reason `llamaindex_public_direct_retrieval`
  errors: missing_expected_keyword
  answer: Empty Response
- `specialist_supervisor`: status 200, latency 12216.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_multi_direct:institution_specialist+document_specialist`
  answer: Institucional: O ano escolar no Colégio Horizonte pode ser dividido em três etapas públicas principais: admissão, rotina acadêmica e fechamento, conforme as seguintes características:

**1. Admissão:**
O ciclo de matrícula para um novo ano letivo, como 2026, geralmente se inicia em outubro do ano anterior (ex: 6 de outubro de 2025 para 2026). Este processo envolve pré-cadastro, a opção de visitas guiadas para famílias interessadas e uma triagem inicial de documentos. O atendimento comercial da escola auxilia com visitas, apresentações pedagógicas e simulações financeiras. A efetivação da matrícula está condicionada à análise documental, a uma entrevista de acolhimento e à assinatura do contrato.

**2. Rotina Acadêmica:**
As aulas do ano letivo, tanto para o Ensino Fundamental II quanto para o Ensino Médio, começam em fevereiro (ex: 2 de fevereiro de 2026). A semana inicial é dedicada ao acolhimento das novas turmas, especialmente para o 6º ano e a 1ª série. A rotina é pautada por um projeto pedagógico laico, com foco em aprendizagem por projetos, cultura digital responsável, acompanhamento socioemocional e preparação acadêmica. O currículo segue a BNCC, com componentes como Língua Portuguesa, Matemática, Ciências, História, Geografia, Inglês, Educação Física e Projeto de Vida, além de trilhas eletivas e monitorias no contraturno. Ao longo do ano, são realizados eventos como plantões pedagógicos, mostras de ciências e tecnologia, e feiras de orientação acadêmica e vocacional. A política acadêmica prevê uma média de aprovação de 7,0 e exige frequência mínima de 75%, com suporte de recuperação para casos de desempenho abaixo da média e acompanhamento para frequência baixa.

**3. Fechamento:**
O encerramento do ano letivo para o Ensino Fundamental II é marcado por cerimônias internas, como a formatura do 9º ano, que geralmente ocorre em dezembro (ex: 12 de dezembro de 2026). Embora não haja uma data única para o fechamento de todo o ano escolar no documento, a formatura do 9º ano indica o término do ciclo para essa etapa de ensino, e o calendário de eventos e o início das aulas em fevereiro sugerem que dezembro é o mês de conclusão das atividades acadêmicas regulares.

Documentos: Em um ano escolar público, as três etapas de admissão, rotina acadêmica e fechamento geralmente se desdobram da seguinte forma:

*   **Admissão:** Esta etapa ocorre geralmente antes do início do ano letivo e envolve a matrícula ou rematrícula dos estudantes. Para escolas públicas, o processo costuma ser regulamentado por editais estaduais ou municipais, com prazos definidos para inscrição, alocação de vagas (muitas vezes baseada em critérios como proximidade da residência, irmãos na mesma escola, ou sorteio), e efetivação da matrícula com a apresentação de documentos. Pode haver também um período para transferência de alunos entre instituições.

*   **Rotina Acadêmica:** Esta é a etapa mais longa e central do ano escolar, começando com o início das aulas e estendendo-se por todo o período letivo. Envolve a frequência diária dos alunos, o desenvolvimento do currículo pedagógico, a realização de atividades em sala de aula, trabalhos, provas e avaliações contínuas. Inclui também o acompanhamento do desempenho dos estudantes pelos professores, reuniões de pais e mestres, projetos interdisciplinares, eventos culturais e esportivos, e a distribuição de boletins ou relatórios de progresso.

*   **Fechamento:** A etapa de fechamento marca o final do ano letivo. Nela, são realizadas as últimas avaliações, conselhos de classe para definição do resultado final dos alunos (aprovação, recuperação ou reprovação), e a entrega de documentos como históricos escolares e certificados. Também é o período para a preparação da instituição para o próximo ano, incluindo planejamento pedagógico, manutenção das instalações e, em muitos casos, o início do processo de rematrícula para o ano seguinte.

### Sem usar dados privados, como a escola descreve avaliacao, recuperacao, promocao, media e frequencia minima?

- Slice: `public`
- Thread: `retrieval_public_academic_policy_overview` turn `1`
- `langgraph`: status 200, latency 210.9ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `python_functions`: status 200, latency 192.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `llamaindex`: status 200, latency 135.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.
- `specialist_supervisor`: status 200, latency 73.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.

### Nos documentos publicos, como a escola trata pontualidade, frequencia e convivencia como parte do mesmo acompanhamento?

- Slice: `public`
- Thread: `retrieval_public_conduct_frequency_punctuality` turn `1`
- `langgraph`: status 200, latency 199.1ms, keyword pass `True`, quality `100`, reason `langgraph_public_canonical_lane:public_bundle.conduct_frequency_punctuality`
  answer: Pontualidade, frequencia e convivencia aparecem juntas nos documentos publicos da escola. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia.
- `python_functions`: status 200, latency 187.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Pontualidade, frequencia e convivencia aparecem juntas nos documentos publicos da escola. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia.
- `llamaindex`: status 200, latency 133.7ms, keyword pass `True`, quality `100`, reason `llamaindex_public_canonical_lane:public_bundle.conduct_frequency_punctuality`
  answer: Pontualidade, frequencia e convivencia aparecem juntas nos documentos publicos da escola. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia.
- `specialist_supervisor`: status 200, latency 71.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:conduct_frequency_punctuality`
  answer: Pontualidade, frequencia e convivencia aparecem juntas nos documentos publicos da escola. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao.

### Como bolsas e descontos se cruzam com rematricula, transferencia e cancelamento no material publico?

- Slice: `public`
- Thread: `retrieval_public_bolsas_and_processes` turn `1`
- `langgraph`: status 200, latency 236.3ms, keyword pass `False`, quality `80`, reason `langgraph_public_canonical_lane:public_bundle.process_compare`
  errors: missing_expected_keyword
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `python_functions`: status 200, latency 192.8ms, keyword pass `False`, quality `80`, reason `python_functions_native_contextual_public_answer`
  errors: missing_expected_keyword
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 172.7ms, keyword pass `False`, quality `80`, reason `llamaindex_public_canonical_lane:public_bundle.process_compare`
  errors: missing_expected_keyword
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 243.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:bolsas_and_processes`
  answer: O edital disciplina pedidos de bolsa social, desconto institucional, politica para irmaos e condicoes de manutencao do beneficio no ano letivo de 2026. Pedidos devem ser feitos dentro da janela informada pela escola, com envio de documentacao socioeconomica e demais comprovantes solicitados no regulamento especifico. A concessao de bolsas e descontos depende de analise documental, criterios internos, disponibilidade orcamentaria e validacao administrativa. Beneficios podem depender de cumprimento das condicoes previstas, como adimplencia, atualizacao cadastral e apresentacao tempestiva de documentos complementares quando solicitados. A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### Quanto eu pagaria de matricula e por mes para 3 filhos usando a referencia publica atual?

- Slice: `public`
- Thread: `retrieval_public_pricing_projection` turn `1`
- `langgraph`: status 200, latency 299.5ms, keyword pass `False`, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `python_functions`: status 200, latency 227.3ms, keyword pass `False`, quality `80`, reason `python_functions_native_contextual_public_answer`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 263.1ms, keyword pass `False`, quality `80`, reason `contextual_public_direct_answer`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 182.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:pricing_projection`
  answer: Usando a referencia publica atual para Ensino Fundamental II. 3 aluno(s) dariam R$ 1.050,00 de matricula e R$ 3.840,00 por mes,

### Estou autenticado como quem e com qual escopo? Quero saber o que consigo ver de academico e financeiro.

- Slice: `protected`
- Thread: `retrieval_protected_access_scope` turn `1`
- `langgraph`: status 200, latency 186.8ms, keyword pass `True`, quality `100`, reason `capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `python_functions`: status 200, latency 208.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_authenticated_account_scope`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `llamaindex`: status 200, latency 223.7ms, keyword pass `True`, quality `100`, reason `capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `specialist_supervisor`: status 200, latency 193.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:access_scope`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Neste canal eu consigo consultar academico e financeiro dos alunos vinculados dentro das permissoes da conta.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiroSe quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro da Ana".

### Cruze meu status documental com o financeiro e diga se existe bloqueio ou pendencia relevante.

- Slice: `protected`
- Thread: `retrieval_protected_admin_finance_combo` turn `1`
- `langgraph`: status 200, latency 541.8ms, keyword pass `False`, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  errors: missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `python_functions`: status 200, latency 514.7ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:finance`
  errors: missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 516.4ms, keyword pass `False`, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  errors: missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 151.5ms, keyword pass `False`, quality `68`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### No material publico, como ficam juntas medicacao, cuidado em saude e resposta a emergencias?

- Slice: `public`
- Thread: `retrieval_public_health_emergency_bundle` turn `1`
- `langgraph`: status 200, latency 1671.5ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Olá! Para questões que envolvem medicação, cuidados em saúde e resposta a emergências, o Colégio Horizonte não possui informações detalhadas disponíveis no material público.

Para obter orientações específicas sobre esses temas, sugiro que entre em contato diretamente com a Secretaria Escolar. Eles poderão informar sobre os procedimentos e recursos disponíveis na escola para essas situações.
- `python_functions`: status 200, latency 297.5ms, keyword pass `False`, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 8046.7ms, keyword pass `False`, quality `80`, reason `llamaindex_public_profile`
  errors: missing_expected_keyword
  answer: Colegio Horizonte: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno.
- `specialist_supervisor`: status 200, latency 18008.6ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_strict_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### Como a escola apresenta publicamente a relacao entre periodo integral, estudo orientado e acompanhamento do aluno?

- Slice: `public`
- Thread: `retrieval_public_integral_study_support` turn `1`
- `langgraph`: status 200, latency 4289.5ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje o Colegio Horizonte divulga atividades complementares no contraturno de forma assim: - Ensino Fundamental II: Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados. - Ensino Medio: Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00. - Fundamental II e Ensino Medio: Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno. Entre as ofertas que aparecem com mais clareza hoje estao Biblioteca Aurora, Oficina de danca e expressao corporal, Oficina de teatro, Futsal e treinos esportivos, Volei escolar, Espaco Maker.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `python_functions`: status 200, latency 364.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje o Colegio Horizonte divulga atividades complementares no contraturno de forma assim: - Ensino Fundamental II: Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados. - Ensino Medio: Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00. - Fundamental II e Ensino Medio: Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno. Entre as ofertas que aparecem com mais clareza hoje estao Biblioteca Aurora, Oficina de danca e expressao corporal, Oficina de teatro, Futsal e treinos esportivos, Volei escolar, Espaco Maker.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `llamaindex`: status 200, latency 2822.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje o Colegio Horizonte divulga atividades complementares no contraturno de forma assim: - Ensino Fundamental II: Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados. - Ensino Medio: Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00. - Fundamental II e Ensino Medio: Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno. Entre as ofertas que aparecem com mais clareza hoje estao Biblioteca Aurora, Oficina de danca e expressao corporal, Oficina de teatro, Futsal e treinos esportivos, Volei escolar, Espaco Maker.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `specialist_supervisor`: status 200, latency 9159.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: A escola oferece o período integral opcional, que inclui estudo orientado, almoço, oficinas, esportes e acompanhamento no contraturno. No Ensino Médio, cada estudante participa de trilhas de tutoria e planejamento acadêmico com acompanhamento próximo ao longo do ano. O contraturno combina monitorias, tutorias e trilhas eletivas, todas acompanhadas pela coordenação e orientação educacional.

### Quero uma visao publica de transporte, alimentacao e uniforme para entender a rotina da familia.

- Slice: `public`
- Thread: `retrieval_public_transport_uniform_bundle` turn `1`
- `langgraph`: status 200, latency 239.0ms, keyword pass `False`, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `python_functions`: status 200, latency 205.5ms, keyword pass `False`, quality `80`, reason `python_functions_native_contextual_public_answer`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 236.4ms, keyword pass `False`, quality `80`, reason `contextual_public_direct_answer`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 9553.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Para entender a rotina da família, o Colégio Horizonte oferece uma cantina com lanches e almoço por adesão, especialmente para os estudantes que permanecem no contraturno. Quanto ao uniforme, ele é cobrado à parte e a secretaria escolar pode fornecer orientações administrativas sobre o tema. Não foram encontradas informações públicas sobre serviços de transporte escolar fornecidos ou organizados diretamente pela escola.

### No material publico, como se articulam inclusao, acessibilidade e cuidado com a seguranca escolar?

- Slice: `public`
- Thread: `retrieval_public_inclusion_accessibility` turn `1`
- `langgraph`: status 200, latency 2186.7ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Nossa base de conhecimento atual não contém informações detalhadas sobre como a inclusão, acessibilidade e segurança escolar se articulam especificamente no material público do Colégio Horizonte.

Para obter essas informações, sugiro que você entre em contato diretamente com a nossa secretaria escolar ou consulte os documentos institucionais disponíveis no portal da escola. Eles poderão fornecer os detalhes sobre nossas políticas e práticas nessas áreas.
- `python_functions`: status 200, latency 296.5ms, keyword pass `False`, quality `68`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 11420.2ms, keyword pass `False`, quality `80`, reason `llamaindex_public_direct_retrieval`
  errors: missing_expected_keyword
  answer: Empty Response
- `specialist_supervisor`: status 200, latency 18006.8ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_strict_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### No material publico, como a escola organiza saidas pedagogicas, eventos e autorizacoes das familias?

- Slice: `public`
- Thread: `retrieval_public_outings_authorizations` turn `1`
- `langgraph`: status 200, latency 3556.6ms, keyword pass `False`, quality `80`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`
  errors: missing_expected_keyword
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.
- `python_functions`: status 200, latency 4915.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_public_retrieval`
  answer: Olá! As saídas pedagógicas, feiras, mostras e visitas externas são parte integrante do projeto formativo do Colégio Horizonte. Elas podem envolver preparação prévia em sala de aula, regras de conduta específicas e, claro, a autorização formal da família.

Os comunicados gerais e avisos acadêmicos sobre esses eventos são publicados no portal da escola e reforçados pelos nossos canais oficiais. Reuniões de responsáveis, convocações individuais e alterações importantes na agenda são informadas de acordo com o público envolvido.

Fontes:
- Saidas Pedagogicas, Eventos e Autorizacoes (v2026.3)
- FAQ de Secretaria e Vida Academica (v2026.3)
- Programa de Periodo Integral e Estudo Orientado (v2026.3)
- `llamaindex`: status 200, latency 2729.5ms, keyword pass `False`, quality `80`, reason `llamaindex_public_profile`
  errors: missing_expected_keyword
  answer: Colegio Horizonte: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno.
- `specialist_supervisor`: status 200, latency 9974.5ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_budget_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### Pelos documentos publicos, como uma familia deve escalar um tema da rotina para direcao e protocolo formal?

- Slice: `public`
- Thread: `retrieval_public_governance_protocol` turn `1`
- `langgraph`: status 200, latency 274.6ms, keyword pass `True`, quality `88`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  errors: unnecessary_clarification
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260403-8F675D. Assunto: Pelos documentos publicos, como uma familia deve escalar um tema da rotina para direcao e protocolo formal? Fila responsavel: direcao. Ticket operacional: ATD-20260403-74280C37. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `python_functions`: status 200, latency 262.8ms, keyword pass `True`, quality `88`, reason `python_functions_native_structured:support`
  errors: unnecessary_clarification
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260403-FBC753. Assunto: Pelos documentos publicos, como uma familia deve escalar um tema da rotina para direcao e protocolo formal? Fila responsavel: direcao. Ticket operacional: ATD-20260403-254320D9. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `llamaindex`: status 200, latency 278.5ms, keyword pass `True`, quality `88`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  errors: unnecessary_clarification
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260403-6D9B7C. Assunto: Pelos documentos publicos, como uma familia deve escalar um tema da rotina para direcao e protocolo formal? Fila responsavel: direcao. Ticket operacional: ATD-20260403-C0835EFB. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `specialist_supervisor`: status 200, latency 18018.5ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_strict_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### A escola informa publicamente a quantidade de professores? Se nao, me diga isso de forma direta.

- Slice: `public`
- Thread: `retrieval_public_known_unknown_total_teachers` turn `1`
- `langgraph`: status 200, latency 2527.8ms, keyword pass `False`, quality `80`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  errors: missing_expected_keyword
  answer: A base publica atual nao sustenta com seguranca todos os pontos dessa pergunta, especialmente sobre: diga, direta, nao, professores, publicamente, quantidade. Para evitar uma orientacao incorreta, prefiro nao inferir alem do que esta documentado. Se quiser, eu posso responder apenas o que esta explicitamente registrado na base atual.

Fontes:
- FAQ de Secretaria e Vida Academica (v2026.3)
- Agenda de Avaliacoes, Recuperacoes e Simulados 2026 (v2026.3)
- Politica de Avaliacao, Recuperacao e Promocao (v2026.3)
- `python_functions`: status 200, latency 268.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_public_unpublished_fact`
  answer: Hoje os canais publicos de Colegio Horizonte nao informam a quantidade total de professores. Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.
- `llamaindex`: status 200, latency 3426.7ms, keyword pass `True`, quality `100`, reason `llamaindex_public_unpublished_fact`
  answer: Hoje os canais publicos de Colegio Horizonte nao informam a quantidade total de professores. Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.
- `specialist_supervisor`: status 200, latency 7692.7ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_direct:institution_specialist`
  errors: missing_expected_keyword
  answer: A escola não informa publicamente a quantidade exata de professores em seus documentos institucionais disponíveis.

### Existe numero publico da quantidade de livros da biblioteca?

- Slice: `public`
- Thread: `retrieval_public_known_unknown_library_books` turn `1`
- `langgraph`: status 200, latency 3494.6ms, keyword pass `False`, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`
  errors: missing_expected_keyword
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
- `python_functions`: status 200, latency 164.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_public_unpublished_fact`
  answer: Hoje os canais publicos de Colegio Horizonte nao informam a quantidade total de livros da biblioteca. Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.
- `llamaindex`: status 200, latency 868.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_unpublished_fact`
  answer: Hoje os canais publicos de Colegio Horizonte nao informam a quantidade total de livros da biblioteca. Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.
- `specialist_supervisor`: status 200, latency 7534.5ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_direct:institution_specialist`
  errors: missing_expected_keyword
  answer: Não encontrei um número público da quantidade de livros da biblioteca do Colégio Horizonte nas informações disponíveis. A biblioteca, chamada Biblioteca Aurora, está disponível de segunda a sexta, das 7h30 às 18h00, mas o volume do acervo não é detalhado no perfil institucional público.

### Se eu quiser confirmar idade minima para ingresso, isso aparece publicamente ou depende de admissions?

- Slice: `public`
- Thread: `retrieval_public_known_unknown_minimum_age` turn `1`
- `langgraph`: status 200, latency 1819.5ms, keyword pass `False`, quality `80`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  errors: missing_expected_keyword
  answer: Olá! A idade mínima para ingresso no Colégio Horizonte é uma informação pública e pode ser consultada diretamente. Não depende de um processo de admissão específico para ter acesso a essa informação.
- `python_functions`: status 200, latency 167.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_public_unpublished_fact`
  answer: Hoje os canais publicos de Colegio Horizonte nao publicam uma idade minima exata para ingresso. O que aparece oficialmente sao os segmentos atendidos e o enquadramento por serie; para confirmar idade e adequacao de ingresso, o canal certo e admissions.
- `llamaindex`: status 200, latency 1548.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_unpublished_fact`
  answer: Hoje os canais publicos de Colegio Horizonte nao publicam uma idade minima exata para ingresso. O que aparece oficialmente sao os segmentos atendidos e o enquadramento por serie; para confirmar idade e adequacao de ingresso, o canal certo e admissions.
- `specialist_supervisor`: status 200, latency 12921.6ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_direct:institution_specialist`
  errors: missing_expected_keyword
  answer: A idade mínima para ingresso não é informada publicamente como uma política separada. A escola funciona com os segmentos de Ensino Fundamental II (6º ao 9º ano) e Ensino Médio (1ª a 3ª série). A matrícula depende de análise documental e entrevista de acolhimento. Para mais detalhes, é recomendado entrar em contato com o setor de Admissões.

### Quero saber se a escola publica o cardapio da cantina ou se isso fica fora dos canais publicos.

- Slice: `public`
- Thread: `retrieval_public_known_unknown_cafeteria_menu` turn `1`
- `langgraph`: status 200, latency 193.9ms, keyword pass `False`, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `python_functions`: status 200, latency 170.6ms, keyword pass `False`, quality `80`, reason `python_functions_native_contextual_public_answer`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 215.4ms, keyword pass `False`, quality `80`, reason `contextual_public_direct_answer`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 9219.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: A escola possui uma cantina que oferece lanches e almoço por adesão para os estudantes do contraturno. No entanto, as informações públicas disponíveis não especificam se o cardápio da cantina é divulgado em seus canais oficiais. Para obter essa informação, sugiro entrar em contato diretamente com a escola através dos canais de atendimento.

### Me de um panorama de faltas e frequencia dos meus filhos, apontando quem exige maior atencao agora.

- Slice: `protected`
- Thread: `retrieval_protected_attendance_panorama` turn `1`
- `langgraph`: status 200, latency 280.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `python_functions`: status 200, latency 289.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `llamaindex`: status 200, latency 322.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `specialist_supervisor`: status 200, latency 202.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate_fallback`
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina.

### Agora foque so no Lucas e diga o que mais preocupa na frequencia dele.

- Slice: `protected`
- Thread: `retrieval_protected_attendance_panorama` turn `1`
- `langgraph`: status 200, latency 292.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Lucas Oliveira e o foco desta consulta academica. Nao consegui carregar agora o resumo academico detalhado para apontar com seguranca os maiores riscos.
- `python_functions`: status 200, latency 330.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Lucas Oliveira e o foco desta consulta academica. Nao consegui carregar agora o resumo academico detalhado para apontar com seguranca os maiores riscos.
- `llamaindex`: status 200, latency 326.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Lucas Oliveira e o foco desta consulta academica. Nao consegui carregar agora o resumo academico detalhado para apontar com seguranca os maiores riscos.
- `specialist_supervisor`: status 200, latency 267.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_scoped_fallback`
  answer: Lucas Oliveira e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.

### Quero um quadro unico com as proximas avaliacoes dos meus filhos.

- Slice: `protected`
- Thread: `retrieval_protected_upcoming_assessments` turn `1`
- `langgraph`: status 200, latency 301.4ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `python_functions`: status 200, latency 304.5ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:academic`
  errors: missing_expected_keyword
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `llamaindex`: status 200, latency 302.7ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina, mas o foco continua sendo comparar os alunos vinculados desta conta.
- `specialist_supervisor`: status 200, latency 208.6ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_tool_first:academic_summary_aggregate_fallback`
  errors: missing_expected_keyword
  answer: Panorama academico das contas vinculadas: Lucas Oliveira, Ana Oliveira. Nao consegui carregar agora o detalhamento objetivo por disciplina.

### Continuando a consulta, isole a Ana e me mostre apenas as avaliacoes dela.

- Slice: `protected`
- Thread: `retrieval_protected_upcoming_assessments` turn `1`
- `langgraph`: status 200, latency 243.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o resumo academico detalhado para apontar com seguranca os maiores riscos.
- `python_functions`: status 200, latency 285.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o resumo academico detalhado para apontar com seguranca os maiores riscos.
- `llamaindex`: status 200, latency 282.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o resumo academico detalhado para apontar com seguranca os maiores riscos.
- `specialist_supervisor`: status 200, latency 176.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_scoped_fallback`
  answer: Ana Oliveira e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.

### Quem sao exatamente os alunos vinculados ao meu acesso neste canal?

- Slice: `protected`
- Thread: `retrieval_protected_identity_linked_students` turn `1`
- `langgraph`: status 200, latency 276.7ms, keyword pass `True`, quality `100`, reason `capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada`
  answer: Os alunos vinculados a esta conta hoje sao Lucas Oliveira e Ana Oliveira. Eu posso consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro do que sua vinculacao permitir. Se quiser, me diga direto algo como "notas do Lucas" ou "financeiro da Ana".
- `python_functions`: status 200, latency 205.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Os alunos vinculados a esta conta hoje sao Lucas Oliveira e Ana Oliveira. Eu posso consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro do que sua vinculacao permitir. Se quiser, me diga direto algo como "notas do Lucas" ou "financeiro da Ana".
- `llamaindex`: status 200, latency 242.5ms, keyword pass `True`, quality `100`, reason `capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada`
  answer: Os alunos vinculados a esta conta hoje sao Lucas Oliveira e Ana Oliveira. Eu posso consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro do que sua vinculacao permitir. Se quiser, me diga direto algo como "notas do Lucas" ou "financeiro da Ana".
- `specialist_supervisor`: status 200, latency 139.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:access_scope`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Neste canal eu consigo consultar academico e financeiro dos alunos vinculados dentro das permissoes da conta.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiroSe quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro da Ana".

### Hoje existe alguma pendencia administrativa no meu cadastro pessoal aqui na escola?

- Slice: `protected`
- Thread: `retrieval_protected_administrative_self_status` turn `1`
- `langgraph`: status 200, latency 285.3ms, keyword pass `False`, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  errors: missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `python_functions`: status 200, latency 314.1ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:finance`
  errors: missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 350.6ms, keyword pass `False`, quality `80`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  errors: missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 6246.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Não consigo verificar pendências administrativas pessoais. Como EduAssist, tenho acesso apenas a informações públicas e gerais da instituição, não a dados cadastrais individuais. Para saber sobre pendências em seu cadastro pessoal, por favor, entre em contato diretamente com a secretaria da escola. Você pode usar os canais disponíveis, como o telefone (11) 3333-4200 ou o e-mail secretaria@colegiohorizonte.edu.br.

### Pelo manual interno do professor, como a escola orienta a devolutiva pedagogica ao aluno?

- Slice: `restricted`
- Thread: `retrieval_restricted_teacher_feedback` turn `1`
- `langgraph`: status 200, latency 190.4ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 217.6ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 261.7ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 83.1ms, keyword pass `False`, quality `35`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### Pelo protocolo interno, que limite de escopo o Telegram precisa respeitar para responsavel com acesso parcial?

- Slice: `restricted`
- Thread: `retrieval_restricted_scope_protocol_variant` turn `1`
- `langgraph`: status 200, latency 167.3ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 186.5ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 222.2ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 73.5ms, keyword pass `False`, quality `35`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### A escola tem algum protocolo interno para intercambio internacional com hospedagem no ensino medio?

- Slice: `restricted`
- Thread: `retrieval_restricted_exchange_no_match` turn `1`
- `langgraph`: status 200, latency 161.3ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 165.7ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 221.0ms, keyword pass `False`, quality `35`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 73.5ms, keyword pass `False`, quality `35`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  errors: forbidden_entity_or_value, missing_expected_keyword
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### Sou responsavel e quero acessar o playbook interno de negociacao financeira pelo bot.

- Slice: `restricted`
- Thread: `retrieval_restricted_denied_playbook` turn `1`
- `langgraph`: status 200, latency 182.3ms, keyword pass `True`, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `python_functions`: status 200, latency 179.2ms, keyword pass `True`, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `llamaindex`: status 200, latency 230.1ms, keyword pass `True`, quality `100`, reason `documentos internos exigem perfil com autorizacao explicita para leitura restrita`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal para perfis sem autorizacao explicita. Se quiser, eu posso orientar pelo material publico correspondente.
- `specialist_supervisor`: status 200, latency 81.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

