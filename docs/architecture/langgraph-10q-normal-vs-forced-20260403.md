# LangGraph 10Q Normal Vs Forced

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_10q_llm_targeted.generated.20260403.json`

- normal: `{'ok': 10, 'keyword_pass': 6, 'quality_avg': 92.0, 'avg_latency_ms': 251.6, 'used_llm': 0}`
- forced: `{'ok': 10, 'keyword_pass': 4, 'quality_avg': 88.0, 'avg_latency_ms': 5660.5, 'used_llm': 9}`

## Que sinais a base publica da escola da de que necessidades especificas do aluno, mediacao de rotina e seguranca fazem parte da mesma postura institucional?
- `normal`: status 200, quality 80, latency 452.3ms, used_llm False, reason `langgraph_public_canonical_lane:public_bundle.inclusion_accessibility`
- `forced`: status 200, quality 80, latency 4422.8ms, used_llm True, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`

## Sem repetir texto comercial, que desenho de rotina ampliada aparece quando voce junta turno estendido, estudo guiado, refeicao e oficinas no contraturno?
- `normal`: status 200, quality 100, latency 246.2ms, used_llm False, reason `langgraph_public_canonical_lane:public_bundle.integral_study_support`
- `forced`: status 200, quality 100, latency 7943.3ms, used_llm True, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`

## O que os documentos publicos deixam claro sobre como a escola administra risco em atividades fora da sala, desde anuencia da familia ate impedimentos de saude e retorno?
- `normal`: status 200, quality 80, latency 211.5ms, used_llm False, reason `langgraph_public_canonical_lane:public_bundle.outings_authorizations`
- `forced`: status 200, quality 80, latency 8242.3ms, used_llm True, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`

## Quando um impasse deixa de ser rotina normal, que trilha institucional a base publica sugere entre secretaria, coordenacao e lideranca maior?
- `normal`: status 200, quality 100, latency 245.1ms, used_llm False, reason `langgraph_public_canonical_lane:public_bundle.governance_protocol`
- `forced`: status 200, quality 80, latency 1525.2ms, used_llm False, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`

## Como a escola costura comprovacao de saude, falta em dia avaliativo e reorganizacao pedagogica sem tratar isso como evento isolado?
- `normal`: status 200, quality 80, latency 236.5ms, used_llm False, reason `langgraph_public_canonical_lane:public_bundle.health_emergency_bundle`
- `forced`: status 200, quality 80, latency 8443.4ms, used_llm True, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`

## Para quem chegou agora, que fronteira aparece entre orientacoes abertas nos canais da escola e aquilo que so ganha detalhe depois da conta vinculada?
- `normal`: status 200, quality 100, latency 188.3ms, used_llm False, reason `langgraph_public_canonical_lane:public_bundle.visibility_boundary`
- `forced`: status 200, quality 100, latency 8023.8ms, used_llm True, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`

## Que ecossistema de apoio ao estudante aparece quando voce cruza orientacao educacional, monitorias, estudo guiado e conversa com a familia?
- `normal`: status 200, quality 100, latency 181.0ms, used_llm False, reason `langgraph_public_canonical_lane:public_bundle.permanence_family_support`
- `forced`: status 200, quality 100, latency 8220.9ms, used_llm True, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`

## No cotidiano fora da aula, que experiencia operacional do aluno aparece quando a base publica fala de deslocamento, refeicao, identificacao e uso diario de itens institucionais?
- `normal`: status 200, quality 100, latency 244.0ms, used_llm False, reason `langgraph_public_canonical_lane:public_bundle.transport_uniform_bundle`
- `forced`: status 200, quality 80, latency 1989.8ms, used_llm True, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`

## Se eu montar o ano do ponto de vista da familia, como entrada, encontros com responsaveis, devolutivas e recomposicao academica se encadeiam?
- `normal`: status 200, quality 100, latency 310.5ms, used_llm False, reason `langgraph_public_canonical_lane:public_bundle.family_new_calendar_assessment_enrollment`
- `forced`: status 200, quality 100, latency 4260.4ms, used_llm True, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`

## Que imagem de autoridade institucional e de canais de fala emerge quando voce cruza lideranca, atendimento digital e regras de encaminhamento com familias?
- `normal`: status 200, quality 80, latency 200.8ms, used_llm False, reason `langgraph_public_canonical_lane:public_bundle.governance_protocol`
- `forced`: status 200, quality 80, latency 3533.1ms, used_llm True, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`

