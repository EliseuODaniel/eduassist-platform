# Five-Path Chatbot Comparison Report

Date: 2026-04-01T20:21:27.724753+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/system_question_bank_wave_public_graphrag.json`

Run prefix: `debug:five-path:20260401T202002Z`

Stack execution mode: `sequential`

## Benchmark Context

- specialist benchmark mode: `source`
- api-core: `http://127.0.0.1:8001`
- ai-orchestrator: `http://127.0.0.1:8002`
- crewai pilot: `http://127.0.0.1:8004`
- specialist pilot: `http://127.0.0.1:8005`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `8/8` | `8/8` | `100.0` | `374.3 ms` |
| `crewai` | `8/8` | `8/8` | `100.0` | `7624.2 ms` |
| `python_functions` | `8/8` | `8/8` | `100.0` | `132.0 ms` |
| `llamaindex` | `8/8` | `8/8` | `100.0` | `150.7 ms` |
| `specialist_supervisor` | `8/8` | `8/8` | `100.0` | `2260.0 ms` |

## By Slice

- `public`
  - `langgraph`: ok 8/8, keyword pass 8/8, quality 100.0, latency 374.3ms
  - `crewai`: ok 8/8, keyword pass 8/8, quality 100.0, latency 7624.2ms
  - `python_functions`: ok 8/8, keyword pass 8/8, quality 100.0, latency 132.0ms
  - `llamaindex`: ok 8/8, keyword pass 8/8, quality 100.0, latency 150.7ms
  - `specialist_supervisor`: ok 8/8, keyword pass 8/8, quality 100.0, latency 2260.0ms

## Error Types

- `langgraph`: nenhum
- `crewai`: nenhum
- `python_functions`: nenhum
- `llamaindex`: nenhum
- `specialist_supervisor`: nenhum

## Prompt Results

### Compare o manual de regulamentos gerais com a politica de avaliacao e explique como os dois se complementam.

- Slice: `public`
- Thread: `system_bank:publico_multi_documento_e_graphrag:Q025` turn `1`
- `langgraph`: status 200, latency 273.8ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de 75,0% de presenca por componente. Ja a politica de avaliacao explica a aprovacao, a media de referencia 7,0, recuperacao, monitorias e criterios de promocao. Os dois se complementam porque a frequencia e os combinados gerais sustentam a rotina, enquanto a politica academica mostra como a escola trata avaliacao, recuperacao e aprovacao quando a meta nao e atingida.
- `crewai`: status 200, latency 183.9ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de 75% de presenca por componente. Ja a politica de avaliacao detalha aprovacao, media 7,0, recuperacao, monitorias e criterios de promocao. Os dois se complementam porque a frequencia sustenta a rotina, enquanto a politica academica mostra como a escola trata recuperacao e aprovacao quando a meta nao e atingida.
- `python_functions`: status 200, latency 126.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de 75,0% de presenca por componente. Ja a politica de avaliacao explica a aprovacao, a media de referencia 7,0, recuperacao, monitorias e criterios de promocao. Os dois se complementam porque a frequencia e os combinados gerais sustentam a rotina, enquanto a politica academica mostra como a escola trata avaliacao, recuperacao e aprovacao quando a meta nao e atingida.
- `llamaindex`: status 200, latency 153.7ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de 75,0% de presenca por componente. Ja a politica de avaliacao explica a aprovacao, a media de referencia 7,0, recuperacao, monitorias e criterios de promocao. Os dois se complementam porque a frequencia e os combinados gerais sustentam a rotina, enquanto a politica academica mostra como a escola trata avaliacao, recuperacao e aprovacao quando a meta nao e atingida.
- `specialist_supervisor`: status 200, latency 2424.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:policy_compare`
  answer: O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de 75,0% de presenca por componente. Ja a politica de avaliacao detalha aprovacao, media 7,0, recuperacao, monitorias e criterios de promocao. Os dois se complementam porque a frequencia e os combinados gerais sustentam a rotina, enquanto a politica academica mostra como a escola trata recuperacao e aprovacao quando a meta nao e atingida.

### Compare o calendario letivo, a agenda de avaliacoes e o manual de matricula do ponto de vista de uma familia nova.

- Slice: `public`
- Thread: `system_bank:publico_multi_documento_e_graphrag:Q026` turn `1`
- `langgraph`: status 200, latency 1916.0ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `crewai`: status 200, latency 462.0ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A mensalidade de referencia para Ensino Fundamental II e R$ 1280.00, com taxa de matricula de R$ 350.00.
- `python_functions`: status 200, latency 196.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `llamaindex`: status 200, latency 140.0ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.
- `specialist_supervisor`: status 200, latency 2284.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:family_new_calendar_enrollment`
  answer: Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares. Calendario letivo: As aulas do ensino fundamental II e do ensino medio comecam em 2 de fevereiro de 2026. Ingresso e marcos do ano: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita guiada opcional e triagem documental inicial. Relacao com a familia: As reunioes gerais com responsaveis acontecem em 28 de março, 27 de junho, 19 de setembro e 12 de dezembro de 2026. Agenda de avaliacoes: As avaliacoes bimestrais seguem o planejamento pedagogico de cada segmento e sao publicadas com antecedencia no portal academico. Recuperacao e ajustes: A recuperacao paralela acontece ao longo do bimestre, com reforco, devolutiva e atividades de recomposicao de aprendizagem. Comunicacao com responsaveis: Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. Manual de matricula: O processo de matricula ocorre em quatro etapas: pre-cadastro, envio de documentos, validacao pela secretaria e assinatura contratual. Documentos e envio: Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. O envio inicial dos documentos pode ser feito pelo portal institucional ou pelo e-mail oficial da secretaria para triagem e validacao. Em periodos de alta demanda, o atendimento inicial prioriza orientacao documental e agendamento. Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.

### Sintetize tudo o que uma familia precisa entender sobre secretaria, portal, credenciais e envio de documentos.

- Slice: `public`
- Thread: `system_bank:publico_multi_documento_e_graphrag:Q027` turn `1`
- `langgraph`: status 200, latency 124.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 176.4ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 122.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 202.6ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 2483.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_credentials_bundle`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### Quais temas atravessam varios documentos publicos quando o assunto e permanencia escolar e acompanhamento da familia?

- Slice: `public`
- Thread: `system_bank:publico_multi_documento_e_graphrag:Q028` turn `1`
- `langgraph`: status 200, latency 136.0ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `crewai`: status 200, latency 205.0ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 129.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `llamaindex`: status 200, latency 152.3ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal. Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio.
- `specialist_supervisor`: status 200, latency 2568.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:permanence_family_support`
  answer: Quando o tema e permanencia escolar, os documentos publicos convergem em acompanhamento continuo do estudante, dialogo com a familia e intervencoes antes que a dificuldade vire ruptura. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### Relacione saude, medicacao, segunda chamada, saidas pedagogicas e autorizacoes em uma unica explicacao coerente.

- Slice: `public`
- Thread: `system_bank:publico_multi_documento_e_graphrag:Q029` turn `1`
- `langgraph`: status 200, latency 137.7ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `crewai`: status 200, latency 18951.4ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: Os documentos fornecidos tratam esses tópicos como políticas separadas. Você gostaria de informações sobre cada um deles individualmente, ou está procurando por uma conexão específica entre eles que não está explicitamente detalhada nas fontes?
- `python_functions`: status 200, latency 157.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 161.6ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 2300.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:health_authorizations_bridge`
  answer: A administracao de medicacao pela escola depende de orientacao formal da familia e, quando cabivel, de prescricao ou instrucao adequada. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. A participacao em atividades externas depende do envio da autorizacao no prazo estabelecido. Estudantes sem autorizacao valida, com impedimento medico relevante nao conciliado ou com pendencia operacional especifica podem ter a participacao reavaliada caso a caso pela coordenacao. Em situacoes de emergencia, a prioridade e proteger o estudante e acionar rapidamente os contatos indicados.

### Se eu fosse um aluno novo e muito esquecido, quais regras e prazos eu mais correria risco de perder no primeiro mes?

- Slice: `public`
- Thread: `system_bank:publico_multi_documento_e_graphrag:Q030` turn `1`
- `langgraph`: status 200, latency 139.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `crewai`: status 200, latency 20229.5ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_timeout`
  answer: Olá! Para os novos alunos, é importante ficar de olho em algumas datas e regras essenciais: o prazo de matrícula vai até 15 de agosto, e a entrega de documentos deve ser feita até 30 de agosto. O acesso ao portal do aluno será liberado a partir de 10 de agosto. É obrigatório participar da semana de integração, que acontece de 18 a 22 de agosto, e a orientação acadêmica para calouros será no dia 20 de agosto, às 10h, no Auditório Principal. As aulas começam em 25 de agosto, e o período de ajuste de disciplinas vai de 25 a 29 de agosto.
- `python_functions`: status 200, latency 113.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `llamaindex`: status 200, latency 136.1ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.
- `specialist_supervisor`: status 200, latency 2085.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:first_month_risks`
  answer: No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. Declaracoes simples tendem a ter prazo menor do que historicos, transferencias e regularizacoes documentais mais complexas. Cada usuario deve utilizar credenciais proprias para acesso ao portal, ao aplicativo e aos canais autenticados da escola. O atendimento protegido no Telegram depende de vinculacao entre a conta de mensageria e o cadastro institucional. Problemas de acesso, esquecimento de senha, falhas de vinculacao e inconsistencias cadastrais podem ser registrados com a secretaria ou pelo suporte institucional. O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel.

### Quais sao os principais pilares do colegio quando cruzamos proposta pedagogica, diferenciais, inclusao e vida escolar?

- Slice: `public`
- Thread: `system_bank:publico_multi_documento_e_graphrag:Q031` turn `1`
- `langgraph`: status 200, latency 127.8ms, keyword pass `True`, quality `100`, reason `a pergunta pede visao global ou conexoes multi-documento`
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Quando Cruzamos Proposta Pedagogica, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 200, latency 177.0ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A proposta pedagogica publicada hoje combina aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e aprofundamento academico progressivo. No Ensino Medio, isso aparece junto da BNCC, de um curriculo proprio com projeto de vida, producao textual e trilhas academicas no contraturno.
- `python_functions`: status 200, latency 111.0ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. No Ensino Medio, isso aparece junto de A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.. Na pratica, isso aparece em frentes como Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. Isso se traduz em acompanhamento mais proximo da aprendizagem e em uma proposta pedagogica explicita no dia a dia.
- `llamaindex`: status 200, latency 135.2ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. No Ensino Medio, isso aparece junto de A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.. Na pratica, isso aparece em frentes como Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. Isso se traduz em acompanhamento mais proximo da aprendizagem e em uma proposta pedagogica explicita no dia a dia.
- `specialist_supervisor`: status 200, latency 2123.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:pedagogical_proposal`
  answer: A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. No Ensino Medio, isso aparece junto de A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e uma rotina pedagogica mais explicita no dia a dia.

### Compare rematricula, transferencia e cancelamento destacando o que muda em prazo, documentos e consequencias.

- Slice: `public`
- Thread: `system_bank:publico_multi_documento_e_graphrag:Q032` turn `1`
- `langgraph`: status 200, latency 138.9ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `crewai`: status 200, latency 20608.8ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_timeout`
  answer: Para a rematrícula, o prazo para garantir sua vaga e evitar multas é até 20 de janeiro de 2023. Após essa data, será aplicada uma multa de 2% e juros de 1% ao mês. A não rematrícula implica na perda da vaga. Os documentos mencionados são o contrato de prestação de serviços educacionais e a ficha de matrícula. Para o cancelamento de matrícula, se realizado até 20 de janeiro de 2023, você fica isento de multa. Após essa data, há uma multa de 20% sobre o valor total do semestre. É necessário um requerimento de cancelamento. Já para a transferência, os documentos necessários incluem histórico escolar, plano de ensino das disciplinas cursadas, atestado de vínculo com a instituição de origem e comprovante de regularidade com o ENADE. As evidências não especificam um prazo ou as consequências para a transferência.
- `python_functions`: status 200, latency 100.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 124.1ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 1811.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_preflight:process_compare`
  answer: Rematricula: A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Transferencia de entrada: Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Transferencia de saida: Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Cancelamento: Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Prazos e documentos: Declaracoes simples costumam ser liberadas em ate dois dias uteis.

