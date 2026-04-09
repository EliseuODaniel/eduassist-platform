# Four-Path Chatbot Comparison Report

Date: 2026-04-03T19:25:46.233422+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_5q_llm_compare.generated.20260403.json`

LLM forced: `True`

Run prefix: `debug:four-path:llm-forced:20260403T192231Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency | Final polish |
| --- | --- | --- | --- | --- | --- |
| `langgraph` | `5/5` | `2/5` | `88.0` | `7506.5 ms` | `5/5` |
| `python_functions` | `5/5` | `3/5` | `92.0` | `4061.4 ms` | `0/5` |
| `llamaindex` | `4/5` | `3/5` | `76.0` | `15071.7 ms` | `3/5` |
| `specialist_supervisor` | `4/5` | `1/5` | `68.0` | `12311.6 ms` | `0/5` |

## By Slice

- `public`
  - `langgraph`: ok 5/5, keyword pass 2/5, quality 88.0, latency 7506.5ms, final polish 5/5
  - `python_functions`: ok 5/5, keyword pass 3/5, quality 92.0, latency 4061.4ms, final polish 0/5
  - `llamaindex`: ok 4/5, keyword pass 3/5, quality 76.0, latency 15071.7ms, final polish 3/5
  - `specialist_supervisor`: ok 4/5, keyword pass 1/5, quality 68.0, latency 12311.6ms, final polish 0/5

## Error Types

- `langgraph`: missing_expected_keyword=3
- `python_functions`: missing_expected_keyword=2
- `llamaindex`: missing_expected_keyword=1, request_failed=1
- `specialist_supervisor`: missing_expected_keyword=3, request_failed=1

## Prompt Results

### Olhando apenas para a base publica da escola, que continuidade de apoio aparece quando se cruzam orientacao educacional, mediacao de convivio, estudo guiado e relacao com a familia?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_support_continuum_open` turn `1`
- `langgraph`: status 200, latency 3725.7ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `python_functions`: status 200, latency 484.1ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 599, latency 31202.1ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, reason `exception`
  errors: request_failed
  answer: 
- `specialist_supervisor`: status 200, latency 2031.0ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `stack_not_enabled`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.

### Sem repetir slogans, que arquitetura de rotina escolar aparece quando se combinam turno estendido, oficinas, refeicao, estudo acompanhado e permanencia no contraturno?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_extended_day_ecosystem_open` turn `1`
- `langgraph`: status 200, latency 8261.1ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `structured_polish, answer_verifier_judge`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  answer: No Colégio Horizonte, a combinação de turno estendido, oficinas, refeição, estudo acompanhado e permanência no contraturno forma uma rotina de período integral. Essa opção complementar oferece aos estudantes um acompanhamento mais próximo, uma rotina organizada e atividades formativas adicionais. A tarde é composta por acolhimento, almoço ou lanche, um bloco de estudo e atividades complementares, como oficinas de leitura, projetos maker, cultura digital, práticas artísticas, monitorias e recomposição de aprendizagem.
- `python_functions`: status 200, latency 3919.6ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  answer: No Colégio Horizonte, a combinação de turno estendido, oficinas, refeição, estudo acompanhado e permanência no contraturno forma uma rotina de período integral. Essa opção complementar oferece aos estudantes um acompanhamento mais próximo, uma rotina organizada e atividades formativas adicionais. A tarde geralmente inclui acolhimento, almoço ou lanche, um bloco de estudo e uma atividade complementar, como oficinas de leitura, projetos maker, cultura digital, práticas artísticas ou monitorias.
- `llamaindex`: status 200, latency 4658.5ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `answer_composition, structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `llamaindex_documentary_synthesis`, reason `llamaindex_public_profile`
  errors: missing_expected_keyword
  answer: Fora da sala regular, o material publico mostra que periodo integral e estudo orientado se completam como camadas de apoio ao estudante. O periodo integral e uma opcao complementar destinada a familias que desejam ampliar a permanencia do estudante na escola com acompanhamento, rotina organizada e atividades formativas adicionais. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Em geral, a rotina da tarde combina acolhimento, almoco ou lanche conforme o plano contratado, bloco de estudo, atividade complementar e horario de saida definido. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O estudo orientado ajuda o aluno a manter rotina e prioridade, mas nao garante, por si so, desempenho academico especifico.
- `specialist_supervisor`: status 200, latency 14613.3ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `specialist_execution`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, reason `specialist_supervisor_budget_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### Se uma familia precisa entender por onde um tema caminha dentro da escola, que trilha institucional os documentos publicos sugerem entre secretaria, coordenacao, direcao e canais oficiais?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_governance_channels_open` turn `1`
- `langgraph`: status 200, latency 9089.9ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `structured_polish, answer_verifier_judge`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: missing_expected_keyword
  answer: Para entender o andamento de um tema, a trilha institucional do Colégio Horizonte sugere que as famílias busquem a coordenação pedagógica como primeiro contato. Você pode falar com a Coordenadora Luciana Ferraz para o Ensino Médio (ensinomedio@colegiohorizonte.edu.br) ou com o Coordenador Ricardo Paiva para o Ensino Fundamental II (fundamental2@colegiohorizonte.edu.br). A Diretora Geral, Helena Martins (direcao@colegiohorizonte.edu.br), atende por agenda e participa dos encontros bimestrais, sendo o contato para questões de governança e relacionamento institucional.
- `python_functions`: status 200, latency 4722.0ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  errors: missing_expected_keyword
  answer: Na base publica do Colegio Horizonte, coordenacao e direcao aparecem em uma trilha clara de governanca e protocolo. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar.
- `llamaindex`: status 200, latency 14200.5ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_composition, structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `llamaindex_documentary_synthesis`, reason `llamaindex_public_profile`
  answer: Na base publica do Colegio Horizonte, coordenacao e direcao aparecem em uma trilha clara de governanca e protocolo. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar.

Fontes:
- Governanca e Lideranca Institucional (v2026.2)
- FAQ de Secretaria e Vida Academica (v2026.3)
- `specialist_supervisor`: status 200, latency 7062.8ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `stack_not_enabled`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: missing_expected_keyword
  answer: Na base publica do Colegio Horizonte, coordenacao e direcao aparecem em uma trilha clara de governanca e protocolo. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar.

### Que logica institucional aparece quando a escola conecta comprovacao de saude, ausencia em atividade avaliativa, comunicacao com a familia e reorganizacao pedagogica?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_health_reorganization_open` turn `1`
- `langgraph`: status 200, latency 8491.0ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `structured_polish, answer_verifier_judge`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: missing_expected_keyword
  answer: No Colégio Horizonte, quando um estudante precisa se ausentar por motivos de saúde, é importante que a família apresente a comprovação. Isso nos permite justificar a falta, organizar uma segunda chamada para atividades avaliativas e, se necessário, adaptar o plano pedagógico para que o aprendizado não seja prejudicado. Nosso objetivo é sempre garantir o bem-estar do aluno e o acompanhamento de seu desenvolvimento.
- `python_functions`: status 200, latency 4407.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  answer: No Colégio Horizonte, a lógica institucional conecta a comprovação de saúde, a comunicação com a família e a reorganização pedagógica para garantir o bem-estar e o acompanhamento do estudante. Atestados médicos e justificativas formais são importantes para analisar ausências, solicitar segunda chamada ou adaptar temporariamente a rotina. Em casos de desempenho abaixo do esperado, a escola pode oferecer recuperação paralela, atividades orientadas ou avaliações substitutivas, sempre com a família informada.
- `llamaindex`: status 200, latency 13370.6ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `llamaindex_not_eligible`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  answer: No Colégio Horizonte, a lógica institucional conecta a comprovação de saúde, a comunicação com a família e a reorganização pedagógica para garantir o bem-estar e o acompanhamento do estudante. Atestados médicos e justificativas formais são importantes para analisar ausências, solicitar segunda chamada ou adaptar temporariamente a rotina. Em casos de desempenho abaixo do esperado, a escola pode oferecer recuperação paralela, atividades orientadas ou avaliações substitutivas, sempre com a família informada.
- `specialist_supervisor`: status 599, latency 20002.2ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, reason `exception`
  errors: request_failed
  answer: 

### Para uma familia que ainda esta conhecendo a escola, como a base publica deixa clara a fronteira entre o que ja se entende por calendarios e orientacoes abertas e o que so aparece com portal, login e conta vinculada?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_visibility_boundary_onboarding_open` turn `1`
- `langgraph`: status 200, latency 7964.8ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `structured_polish, answer_verifier_judge`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  answer: Olá! Para as famílias que estão nos conhecendo, é importante saber que temos algumas frentes de comunicação. A Secretaria cuida de declarações, históricos e orientações administrativas. Já o Portal Institucional é o lugar para protocolos e envio digital de documentos.

Para acessar informações mais específicas, como calendários detalhados e orientações personalizadas, você precisará das credenciais de login e senha do portal. Se precisar de ajuda para recuperar o acesso, a Secretaria ou o suporte digital estão à disposição.

Lembre-se que o envio inicial de documentos pode ser feito pelo portal, e-mail da secretaria ou presencialmente. Por segurança, o chat aberto não deve ser usado para documentos completos ou dados sensíveis.
- `python_functions`: status 200, latency 6773.7ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 11926.6ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_composition, structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `llamaindex_documentary_synthesis`, reason `llamaindex_public_profile`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. A fronteira pratica aparece assim: orientacoes abertas circulam no calendario publico, no portal institucional aberto e nos canais oficiais; o que so ganha detalhe depois do login e da conta vinculada no portal sao informacoes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 17848.8ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `specialist_execution`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Para uma família que está conhecendo o Colégio Horizonte, a fronteira entre as informações públicas e aquelas que exigem portal, login e conta vinculada é clara.

**Informações Públicas e Abertas:**

A base pública do Colégio Horizonte, acessível através de seu website, contatos de admissão, visitas guiadas e canais de atendimento comercial (telefone, WhatsApp, e-mail e Instagram), disponibiliza um panorama abrangente da escola. Isso inclui:

*   **Perfil Institucional:** Nome, endereço, modelo educacional, currículo, segmentos de ensino (Fundamental II e Ensino Médio), turnos de funcionamento, valores de mensalidade de referência, diferenciais pedagógicos (tutoria, espaço maker, acolhimento de famílias) e infraestrutura.
*   **Calendários e Orientação Geral:** Datas importantes do ano letivo (início das aulas, reuniões gerais de pais e responsáveis, eventos culturais e esportivos abertos ao público), política acadêmica resumida (média de aprovação, política de frequência mínima, sumário do projeto de vida) e canais de contato para diversos setores.
*   **Processo de Admissão:** Detalhes sobre o processo de matrícula, documentos necessários para inscrição, ofertas de visita guiada e informações sobre bolsas e descontos.
*   **Equipe de Liderança:** Nomes e contatos de e-mail da direção e coordenações.

**Informações Acessíveis com Portal, Login e Conta Vinculada:**

Uma vez que a família se torna parte da comunidade escolar, com a matrícula efetivada, o acesso a um portal e conta vinculada se torna necessário para informações e serviços personalizados e seguros. Isso abrange:

*   **Dados Acadêmicos Individuais:** Notas, boletins, frequência detalhada do estudante em cada disciplina, comunicados pedagógicos específicos e acompanhamento individualizado.
*   **Informações Financeiras Pessoais:** Boletos de mensalidade, histórico de pagamentos, contratos financeiros e detalhes de acordos. O serviço de "Financeiro escolar e contratos" menciona explicitamente o "portal autenticado" para essas interações.
*   **Documentação e Processos Administrativos:** Envio seguro de documentos pessoais e administrativos (além da fase inicial de matrícula), solicitação de declarações e históricos escolares, e interação com a secretaria digital para assuntos que requerem identificação e confidencialidade.
*   **Comunicações Diretas e Restritas:** Mensagens e avisos da coordenação pedagógica, professores e orientação educacional específicos para o estudante ou sua família.
*   **Suporte Digital:** O serviço de "Suporte de portal, acesso e atendimento digital" é dedicado a auxiliar no acesso e uso do portal escolar, indicando a existência de uma plataforma que requer credenciais.

