# Five-Path Chatbot Comparison Report

Date: 2026-04-01T01:13:12.268370+00:00

Dataset: `tests/evals/datasets/system_question_bank_strict_cases.json`

Run prefix: `debug:five-path:20260401T011233Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `19/19` | `19/19` | `100.0` | `171.4 ms` |
| `crewai` | `19/19` | `19/19` | `100.0` | `322.8 ms` |
| `python_functions` | `19/19` | `19/19` | `100.0` | `147.5 ms` |
| `llamaindex` | `19/19` | `19/19` | `100.0` | `187.8 ms` |
| `specialist_supervisor` | `19/19` | `19/19` | `100.0` | `1193.7 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 5/5, keyword pass 5/5, quality 100.0, latency 194.3ms
  - `crewai`: ok 5/5, keyword pass 5/5, quality 100.0, latency 423.5ms
  - `python_functions`: ok 5/5, keyword pass 5/5, quality 100.0, latency 191.4ms
  - `llamaindex`: ok 5/5, keyword pass 5/5, quality 100.0, latency 199.2ms
  - `specialist_supervisor`: ok 5/5, keyword pass 5/5, quality 100.0, latency 167.4ms
- `public`
  - `langgraph`: ok 12/12, keyword pass 12/12, quality 100.0, latency 160.7ms
  - `crewai`: ok 12/12, keyword pass 12/12, quality 100.0, latency 295.3ms
  - `python_functions`: ok 12/12, keyword pass 12/12, quality 100.0, latency 122.1ms
  - `llamaindex`: ok 12/12, keyword pass 12/12, quality 100.0, latency 174.4ms
  - `specialist_supervisor`: ok 12/12, keyword pass 12/12, quality 100.0, latency 1796.8ms
- `workflow`
  - `langgraph`: ok 2/2, keyword pass 2/2, quality 100.0, latency 178.6ms
  - `crewai`: ok 2/2, keyword pass 2/2, quality 100.0, latency 236.2ms
  - `python_functions`: ok 2/2, keyword pass 2/2, quality 100.0, latency 190.4ms
  - `llamaindex`: ok 2/2, keyword pass 2/2, quality 100.0, latency 239.2ms
  - `specialist_supervisor`: ok 2/2, keyword pass 2/2, quality 100.0, latency 140.8ms

## Error Types

- `langgraph`: nenhum
- `crewai`: nenhum
- `python_functions`: nenhum
- `llamaindex`: nenhum
- `specialist_supervisor`: nenhum

## Prompt Results

### Qual e o endereco completo da escola, o telefone principal e o melhor canal para falar com a secretaria hoje?

- Slice: `public`
- Thread: `sqb_public_address` turn `1`
- `langgraph`: status 200, latency 297.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O endereco publicado de Colegio Horizonte hoje e Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120. O telefone principal hoje e (11) 3333-4200. O canal mais direto para falar com a secretaria hoje e o WhatsApp (11) 97500-2041.
- `crewai`: status 200, latency 185.9ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Endereco: Rua das Acacias, 1450, Vila Mariana, Sao Paulo/SP, CEP 04567-120 O telefone principal hoje e (11) 3333-4200. O melhor canal para a secretaria hoje e (11) 97500-2040.
- `python_functions`: status 200, latency 138.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O endereco publicado de Colegio Horizonte hoje e Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120. O telefone principal hoje e (11) 3333-4200. O canal mais direto para falar com a secretaria hoje e o WhatsApp (11) 97500-2041.
- `llamaindex`: status 200, latency 187.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O endereco publicado de Colegio Horizonte hoje e Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120. O telefone principal hoje e (11) 3333-4200. O canal mais direto para falar com a secretaria hoje e o WhatsApp (11) 97500-2041.
- `specialist_supervisor`: status 200, latency 133.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:contact_bundle`
  answer: O endereco completo da escola hoje e Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120. O telefone principal e (11) 3333-4200. O melhor canal para a secretaria hoje e o WhatsApp (11) 97500-2041.

### Essa escola tem biblioteca de verdade ou so fala que tem? Qual e o nome e o horario?

- Slice: `public`
- Thread: `sqb_public_library` turn `1`
- `langgraph`: status 200, latency 157.7ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O horario de Biblioteca Aurora hoje funciona assim: Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `crewai`: status 200, latency 187.8ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Sim. Biblioteca Aurora: biblioteca   Biblioteca Aurora   service   True   Atendimento ao publico de segunda a sexta, das 7h30 as 18h00..
- `python_functions`: status 200, latency 185.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: O horario de Biblioteca Aurora hoje funciona assim: Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `llamaindex`: status 200, latency 216.7ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O horario de Biblioteca Aurora hoje funciona assim: Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `specialist_supervisor`: status 200, latency 116.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:library_hours`
  answer: A biblioteca se chama Biblioteca Aurora e funciona Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### Quem responde por direcao, orientacao educacional e atendimento comercial?

- Slice: `public`
- Thread: `sqb_public_routing` turn `1`
- `langgraph`: status 200, latency 135.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `crewai`: status 200, latency 197.2ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Direcao geral: Helena Martins.
Para bolsa, desconto e matricula, o melhor canal hoje e Atendimento comercial / Admissoes. Admissoes (telefone): (11) 3333-4201
Para bullying, convivencia e apoio escolar, o canal indicado e a orientacao educacional. Orientacao educacional (telefone): (11) 3333-4202
- `python_functions`: status 200, latency 96.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `llamaindex`: status 200, latency 163.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `specialist_supervisor`: status 200, latency 118.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_routing`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- Direcao: bot, ouvidoria ou protocolo institucional.

### Se eu fosse uma familia nova e tivesse so 30 segundos, o que voce me diria sobre essa escola?

- Slice: `public`
- Thread: `sqb_public_pitch` turn `1`
- `langgraph`: status 200, latency 132.7ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Se eu tivesse 30 segundos para resumir Colegio Horizonte, eu diria isto: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Os diferenciais publicados com mais clareza hoje passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.
- `crewai`: status 200, latency 210.6ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Se eu tivesse 30 segundos para resumir esta escola, eu diria isto: ela combina aprendizagem por projetos, acompanhamento mais proximo e trilhas academicas no contraturno. No que esta publicado aqui, os diferenciais mais claros passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo. Colegio Horizonte em Sao Paulo/SP. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.
- `python_functions`: status 200, latency 104.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Se eu tivesse 30 segundos para resumir Colegio Horizonte, eu diria isto: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Os diferenciais publicados com mais clareza hoje passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.
- `llamaindex`: status 200, latency 207.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Se eu tivesse 30 segundos para resumir Colegio Horizonte, eu diria isto: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Os diferenciais publicados com mais clareza hoje passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.
- `specialist_supervisor`: status 200, latency 123.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:public_pitch`
  answer: Se eu tivesse 30 segundos para resumir esta escola, eu diria isto: ela combina aprendizagem por projetos, acompanhamento mais proximo e trilhas academicas no contraturno. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. No Ensino Medio, isso aparece junto de A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e uma rotina pedagogica mais explicita no dia a dia.

### Com quem eu falo sobre bolsa, com quem eu falo sobre boletos e com quem eu falo sobre bullying?

- Slice: `public`
- Thread: `sqb_public_channels` turn `1`
- `langgraph`: status 200, latency 167.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `crewai`: status 200, latency 192.8ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Para bolsa, desconto e matricula, o melhor canal hoje e Atendimento comercial / Admissoes. Admissoes (telefone): (11) 3333-4201
Para boletos, vencimentos e contratos, o melhor canal hoje e o financeiro. Financeiro (telefone): (11) 3333-4203
Para bullying, convivencia e apoio escolar, o canal indicado e a orientacao educacional. Orientacao educacional (telefone): (11) 3333-4202
- `python_functions`: status 200, latency 117.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `llamaindex`: status 200, latency 185.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `specialist_supervisor`: status 200, latency 125.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_routing`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.

### Quando abre a matricula de 2026 e quando comecam as aulas?

- Slice: `public`
- Thread: `sqb_public_timeline` turn `1`
- `langgraph`: status 200, latency 163.2ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `crewai`: status 200, latency 226.4ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. | 2025-10-06 | familias interessadas | O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. | 2026-02-02 | alunos e familias | A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `python_functions`: status 200, latency 130.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 142.1ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `specialist_supervisor`: status 200, latency 133.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:public_timeline_bundle`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### Quais documentos sao exigidos para matricula no ensino medio?

- Slice: `public`
- Thread: `sqb_public_documents` turn `1`
- `langgraph`: status 200, latency 163.1ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `crewai`: status 200, latency 866.1ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
- `python_functions`: status 200, latency 123.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `llamaindex`: status 200, latency 164.2ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `specialist_supervisor`: status 200, latency 10899.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Para a matrícula no Ensino Médio, o Colégio Horizonte exige os seguintes documentos:
* Formulário cadastral preenchido
* Documento de identificação do aluno
* CPF do aluno, quando houver
* Histórico escolar
* Comprovante de residência atualizado
* Documento de identificação do responsável legal

### Como funciona a politica de avaliacao, recuperacao e promocao da escola?

- Slice: `public`
- Thread: `sqb_public_policy` turn `1`
- `langgraph`: status 200, latency 191.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No Colegio Horizonte, a referencia publica de aprovacao e media 7,0/10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico. A referencia publica de aprovacao usada nas orientacoes do colegio e 7,0, com fechamento final sempre acompanhado pela equipe pedagogica no periodo letivo.
- `crewai`: status 200, latency 816.3ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A referencia publica de aprovacao hoje e media 7.0 na escala 0-10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico.
- `python_functions`: status 200, latency 130.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No Colegio Horizonte, a referencia publica de aprovacao e media 7,0/10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico. A referencia publica de aprovacao usada nas orientacoes do colegio e 7,0, com fechamento final sempre acompanhado pela equipe pedagogica no periodo letivo.
- `llamaindex`: status 200, latency 194.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: No Colegio Horizonte, a referencia publica de aprovacao e media 7,0/10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico. A referencia publica de aprovacao usada nas orientacoes do colegio e 7,0, com fechamento final sempre acompanhado pela equipe pedagogica no periodo letivo.
- `specialist_supervisor`: status 200, latency 9457.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:academic_specialist`
  answer: A política de avaliação, recuperação e promoção do Colégio Horizonte funciona da seguinte forma:

**Política de Avaliação e Promoção:**
A média para aprovação é de **7,0** em uma escala de **0 a 10**.

**Recuperação:**
Quando a média do estudante fica abaixo de 7,0, a escola oferece suporte por meio de monitorias, plantões e orientações de recuperação, seguindo o calendário pedagógico.

**Frequência:**
A frequência mínima exigida para aprovação é de **75%**. Se a frequência de um componente curricular cair abaixo desse percentual, o estudante entra em alerta acadêmico e a coordenação poderá acionar a família. A permanência abaixo desse limite pode comprometer a aprovação por frequência. O acompanhamento é feito pela coordenação pedagógica e orientação educacional, que também avalia justificativas e a necessidade de planos de recomposição junto à família e ao estudante.

### Quais os prazos e canais para secretaria receber documentos, declaracoes e atualizacoes cadastrais?

- Slice: `public`
- Thread: `sqb_public_secretaria` turn `1`
- `langgraph`: status 200, latency 126.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
Prazo esperado da secretaria: retorno em ate 2 dias uteis.
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 178.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje a secretaria recebe documentos, declaracoes e atualizacoes cadastrais pelo portal institucional, pelo email da secretaria e pela secretaria presencial. Prazo esperado da secretaria: retorno em ate 2 dias uteis.
- `python_functions`: status 200, latency 101.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
Prazo esperado da secretaria: retorno em ate 2 dias uteis.
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 186.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
Prazo esperado da secretaria: retorno em ate 2 dias uteis.
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 122.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:document_submission_policy`
  answer: Voce pode mandar documentos pelo portal institucional, pelo email da secretaria ou levar na secretaria presencial para conferencia final. Prazo esperado da secretaria: retorno em ate 2 dias uteis. No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria. O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### Compare o manual de regulamentos gerais com a politica de avaliacao e explique como os dois se complementam.

- Slice: `public`
- Thread: `sqb_graphrag_compare` turn `1`
- `langgraph`: status 200, latency 139.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de 75,0% de presenca por componente. Ja a politica de avaliacao explica a aprovacao, a media de referencia 7,0, recuperacao, monitorias e criterios de promocao. Os dois se complementam porque a frequencia e os combinados gerais sustentam a rotina, enquanto a politica academica mostra como a escola trata avaliacao, recuperacao e aprovacao quando a meta nao e atingida.
- `crewai`: status 200, latency 172.3ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de 75% de presenca por componente. Ja a politica de avaliacao detalha aprovacao, media 7,0, recuperacao, monitorias e criterios de promocao. Os dois se complementam porque a frequencia sustenta a rotina, enquanto a politica academica mostra como a escola trata recuperacao e aprovacao quando a meta nao e atingida.
- `python_functions`: status 200, latency 106.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de 75,0% de presenca por componente. Ja a politica de avaliacao explica a aprovacao, a media de referencia 7,0, recuperacao, monitorias e criterios de promocao. Os dois se complementam porque a frequencia e os combinados gerais sustentam a rotina, enquanto a politica academica mostra como a escola trata avaliacao, recuperacao e aprovacao quando a meta nao e atingida.
- `llamaindex`: status 200, latency 141.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de 75,0% de presenca por componente. Ja a politica de avaliacao explica a aprovacao, a media de referencia 7,0, recuperacao, monitorias e criterios de promocao. Os dois se complementam porque a frequencia e os combinados gerais sustentam a rotina, enquanto a politica academica mostra como a escola trata avaliacao, recuperacao e aprovacao quando a meta nao e atingida.
- `specialist_supervisor`: status 200, latency 125.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:policy_compare`
  answer: O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de 75,0% de presenca por componente. Ja a politica de avaliacao detalha aprovacao, media 7,0, recuperacao, monitorias e criterios de promocao. Os dois se complementam porque a frequencia e os combinados gerais sustentam a rotina, enquanto a politica academica mostra como a escola trata recuperacao e aprovacao quando a meta nao e atingida.

### Sintetize tudo o que uma familia precisa entender sobre secretaria, portal, credenciais e envio de documentos.

- Slice: `public`
- Thread: `sqb_graphrag_secretaria` turn `1`
- `langgraph`: status 200, latency 136.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 155.4ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 132.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 186.7ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 115.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_credentials_bundle`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### Como eu vinculo meu Telegram a minha conta da escola?

- Slice: `public`
- Thread: `sqb_identity_link` turn `1`
- `langgraph`: status 200, latency 118.6ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 154.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Para vincular o Telegram a sua conta da escola, entre no portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando /start link_<codigo>.
- `python_functions`: status 200, latency 100.1ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 116.6ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 90.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:auth_guidance`
  answer: Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal do Colegio Horizonte. No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`. Depois disso, eu passo a consultar seus dados autorizados por este canal.

### Qual e exatamente o meu escopo: posso ver academico, financeiro ou os dois para cada filho?

- Slice: `protected`
- Thread: `sqb_guardian_scope` turn `1`
- `langgraph`: status 200, latency 112.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `crewai`: status 200, latency 192.5ms, keyword pass `True`, quality `100`, reason `crewai_protected_identity_backstop`
  answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira. Hoje eu consigo consultar exatamente: notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.
Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro
Se quiser, ja posso abrir um desses assuntos agora.
- `python_functions`: status 200, latency 103.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_authenticated_account_scope`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `llamaindex`: status 200, latency 114.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `specialist_supervisor`: status 200, latency 109.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:access_scope`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Neste canal eu consigo consultar academico e financeiro dos alunos vinculados dentro das permissoes da conta.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiroSe quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro da Ana".

### Quero ver as notas do Lucas Oliveira.

- Slice: `protected`
- Thread: `sqb_guardian_academic` turn `1`
- `langgraph`: status 200, latency 184.8ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `crewai`: status 200, latency 535.5ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: As notas mais recentes de Lucas Oliveira incluem Biologia: 8.40/10.00; Educacao Fisica: 6.40/10.00; Filosofia: 7.00/10.00; Fisica: 5.80/10.00; Geografia: 6.40/10.00; Historia: 6.70/10.00; Ingles: 8.90/10.00; Matematica: 8.70/10.00.
- `python_functions`: status 200, latency 186.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `llamaindex`: status 200, latency 186.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `specialist_supervisor`: status 200, latency 167.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:student_grades`
  answer: Notas de Lucas Oliveira:
- Historia: media parcial 6,8
- Fisica: media parcial 5,9
- Matematica: media parcial 7,7
- Portugues: media parcial 8,3

### E a frequencia?

- Slice: `protected`
- Thread: `sqb_guardian_academic` turn `2`
- `langgraph`: status 200, latency 232.5ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama de frequencia de Lucas Oliveira:
Resumo geral:
- Presencas registradas: 19
- Faltas registradas: 6
- Atrasos registrados: 7
- Minutos somados de ausencia: 370
- `crewai`: status 200, latency 505.6ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: Na frequencia de Lucas Oliveira, eu encontrei 12 registros neste recorte: 7 presencas, 2 faltas e 3 atrasos.
- `python_functions`: status 200, latency 185.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Panorama de frequencia de Lucas Oliveira:
Resumo geral:
- Presencas registradas: 19
- Faltas registradas: 6
- Atrasos registrados: 7
- Minutos somados de ausencia: 370
- `llamaindex`: status 200, latency 216.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama de frequencia de Lucas Oliveira:
Resumo geral:
- Presencas registradas: 19
- Faltas registradas: 6
- Atrasos registrados: 7
- Minutos somados de ausencia: 370
- `specialist_supervisor`: status 200, latency 166.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:attendance_summary`
  answer: Na frequencia de Lucas Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 7 atraso(s) e 19 presenca(s) neste recorte.

### Quero ver o financeiro da Ana Oliveira.

- Slice: `protected`
- Thread: `sqb_guardian_finance` turn `1`
- `langgraph`: status 200, latency 184.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro de Ana Oliveira:
- Contrato: CTR-2026-002
- Responsavel financeiro: Maria Oliveira
- Mensalidade base: 1450.00
- Faturas em aberto: 2
- Faturas vencidas: 0
Ultimas faturas:
- 2026-01: vencimento 2026-01-10, status paga, valor 1450.00
- 2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- 2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- 2026-04: vencimento 2026-04-10, status em aberto, valor 1450.00
- `crewai`: status 200, latency 471.0ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: Resumo financeiro de Ana Oliveira: a mensalidade de referencia e 1450.00 e ha 2 fatura(s) em aberto, sendo 0 vencida(s).
- `python_functions`: status 200, latency 224.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro de Ana Oliveira:
- Contrato: CTR-2026-002
- Responsavel financeiro: Maria Oliveira
- Mensalidade base: 1450.00
- Faturas em aberto: 2
- Faturas vencidas: 0
Ultimas faturas:
- 2026-01: vencimento 2026-01-10, status paga, valor 1450.00
- 2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- 2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- 2026-04: vencimento 2026-04-10, status em aberto, valor 1450.00
- `llamaindex`: status 200, latency 189.5ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro de Ana Oliveira:
- Contrato: CTR-2026-002
- Responsavel financeiro: Maria Oliveira
- Mensalidade base: 1450.00
- Faturas em aberto: 2
- Faturas vencidas: 0
Ultimas faturas:
- 2026-01: vencimento 2026-01-10, status paga, valor 1450.00
- 2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- 2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- 2026-04: vencimento 2026-04-10, status em aberto, valor 1450.00
- `specialist_supervisor`: status 200, latency 160.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_summary`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 2
- Total de faturas vencidas: 0
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00

### Quero saber se minha documentacao esta regular e se ha algo financeiro bloqueando atendimento.

- Slice: `protected`
- Thread: `sqb_guardian_admin_finance` turn `1`
- `langgraph`: status 200, latency 257.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).
- `crewai`: status 200, latency 413.1ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: Panorama combinado de documentacao e financeiro das contas vinculadas:
- Lucas Oliveira: documentacao regular e completa; financeiro com 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: documentacao com pendencias; financeiro com 2 fatura(s) em aberto e 0 vencida(s).
- `python_functions`: status 200, latency 256.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).
- `llamaindex`: status 200, latency 289.5ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).
- `specialist_supervisor`: status 200, latency 233.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:admin_finance_overview`
  answer: Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).

### Quero agendar uma visita para conhecer a escola.

- Slice: `workflow`
- Thread: `sqb_workflow_visit` turn `1`
- `langgraph`: status 200, latency 185.7ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-8FF15F. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-DE546A8B. A equipe comercial valida a janela e retorna com a confirmacao.
- `crewai`: status 200, latency 241.9ms, keyword pass `True`, quality `100`, reason `workflow_visit_create`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-2BDE2A. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-6C1889DE. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 153.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-855035. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-EC9059DF. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 230.2ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-B01821. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-BD38FD21. A equipe comercial valida a janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 160.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_booking`
  answer: Pedido de visita registrado. Protocolo: VIS-20260401-A89E95. Preferencia registrada: janela a confirmar. Ticket operacional: ATD-20260401-0B7BFDDE. Se quiser, eu tambem posso acompanhar o status ou remarcar a visita.

### Pode ser na quinta a tarde?

- Slice: `workflow`
- Thread: `sqb_workflow_visit` turn `2`
- `langgraph`: status 200, latency 171.4ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-8FF15F. Ticket operacional: ATD-20260401-DE546A8B. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `crewai`: status 200, latency 230.4ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule`
  answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260401-2BDE2A - Ticket operacional: ATD-20260401-6C1889DE - Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30) Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 227.3ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-855035. Ticket operacional: ATD-20260401-EC9059DF. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 248.2ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-B01821. Ticket operacional: ATD-20260401-BD38FD21. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 121.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule`
  answer: Pedido de visita atualizado. Protocolo: VIS-20260401-A89E95. Nova preferencia: quinta-feira, 14:30. Admissions valida a nova janela e retorna com a confirmacao.

