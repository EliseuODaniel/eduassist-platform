import {
  Activity,
  Bot,
  Braces,
  Database,
  FileText,
  Fingerprint,
  Gauge,
  GitBranch,
  GraduationCap,
  HardDrive,
  KeyRound,
  LockKeyhole,
  MessageSquare,
  Network,
  Radar,
  Route,
  ScrollText,
  Server,
  ShieldCheck,
  UserRoundCog,
  Workflow,
} from "lucide-react";
import type { ComponentType } from "react";

export type AtlasView = "overview" | "runtime" | "protected" | "rag" | "operations";

export type AtlasNodeKind =
  | "channel"
  | "service"
  | "runtime"
  | "endpoint"
  | "contract"
  | "data"
  | "policy"
  | "pipeline"
  | "document"
  | "gate";

export type AtlasNode = {
  id: string;
  label: string;
  kind: AtlasNodeKind;
  summary: string;
  whyItMatters: string;
  files: string[];
  reads?: string[];
  safeguards?: string[];
  icon: ComponentType<{ size?: number; strokeWidth?: number }>;
  viewTags: AtlasView[];
};

export type AtlasEdge = {
  id: string;
  source: string;
  target: string;
  label: string;
  viewTags: AtlasView[];
  criticality: "normal" | "security" | "evidence" | "ops";
};

export type Journey = {
  id: AtlasView;
  label: string;
  promise: string;
  readOrder: string[];
  focusNodes: string[];
};

export type Gate = {
  label: string;
  command: string;
  protects: string;
  evidence: string;
  status: "baseline" | "strict" | "watch";
};

export type DrilldownGraph = {
  id: string;
  title: string;
  subtitle: string;
  parentNodeId: string;
  nodes: AtlasNode[];
  edges: AtlasEdge[];
  readOrder: string[];
};

export const journeys: Journey[] = [
  {
    id: "overview",
    label: "Como tudo se conecta",
    promise:
      "A relacao entre as quatro trilhas: uma mensagem entra pelo runtime, consulta a fonte correta, e a operacao prova que o comportamento esta seguro.",
    readOrder: [
      "README.md",
      "docs/architecture/system-architecture.md",
      "docs/architecture/service-catalog.md",
      "docs/security/security-architecture.md",
      "docs/operations/release-readiness.md",
    ],
    focusNodes: [
      "overview-question",
      "overview-runtime",
      "overview-decision",
      "overview-protected",
      "overview-rag",
      "overview-operations",
    ],
  },
  {
    id: "runtime",
    label: "Runtime dedicado",
    promise:
      "Siga uma mensagem do Telegram ate a resposta final e veja onde cada decisao acontece.",
    readOrder: [
      "README.md",
      "docs/architecture/dedicated-first-reference-state.md",
      "docs/architecture/system-architecture.md",
      "docs/architecture/service-catalog.md",
      "apps/telegram-gateway/src/telegram_gateway/main.py",
      "apps/ai-orchestrator/src/ai_orchestrator/runtime_api.py",
    ],
    focusNodes: [
      "telegram",
      "gateway",
      "semantic",
      "runtime-api",
      "python-functions",
      "langgraph",
      "llamaindex",
      "specialist",
      "answer-refiner",
    ],
  },
  {
    id: "protected",
    label: "Dados protegidos",
    promise:
      "Mostra por que notas, frequencia e financeiro nunca devem ser resolvidos por memoria do modelo.",
    readOrder: [
      "docs/security/security-architecture.md",
      "docs/security/access-control-matrix.md",
      "docs/data/data-model.md",
      "apps/api-core/src/api_core/services/identity.py",
      "apps/api-core/src/api_core/services/policy.py",
      "apps/api-core/src/api_core/services/domain.py",
    ],
    focusNodes: [
      "identity",
      "authz",
      "api-core",
      "postgres",
      "opa-rls",
      "academic",
      "finance",
      "audit",
    ],
  },
  {
    id: "rag",
    label: "RAG e corpus",
    promise:
      "Explica o caminho documental: corpus, MinIO, Postgres FTS, Qdrant, rerank e resposta grounded.",
    readOrder: [
      "docs/architecture/system-architecture.md",
      "docs/data/data-model.md",
      "apps/worker/src/worker_app/pipeline.py",
      "apps/ai-orchestrator/src/ai_orchestrator/retrieval.py",
      "apps/ai-orchestrator/src/ai_orchestrator/retrieval_capability_policy.py",
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/grounded_public_answer.py",
    ],
    focusNodes: [
      "worker",
      "corpus",
      "minio",
      "postgres",
      "qdrant",
      "retrieval",
      "evidence-pack",
      "grounded-answer",
    ],
  },
  {
    id: "operations",
    label: "Operacao e gates",
    promise:
      "Conecta handoff humano, observabilidade, scorecard, smokes e release readiness.",
    readOrder: [
      "docs/operations/local-development.md",
      "docs/operations/release-readiness.md",
      "docs/architecture/framework-native-scorecard.md",
      "tools/ops/promotion_gate.py",
      "tools/ops/release_readiness.py",
      "apps/admin-web/app/page.tsx",
    ],
    focusNodes: [
      "admin-web",
      "handoff",
      "observability",
      "scorecard",
      "readiness",
      "evals",
      "release-artifacts",
    ],
  },
];

export const atlasNodes: AtlasNode[] = [
  {
    id: "overview-question",
    label: "Pergunta do usuario",
    kind: "channel",
    summary:
      "Toda trilha comeca com uma pergunta real: publica, protegida, documental, operacional ou ambigua.",
    whyItMatters:
      "O sistema precisa preservar a pergunta atual acima do historico herdado; esse e o ponto de partida comum.",
    files: ["README.md", "apps/telegram-gateway/src/telegram_gateway/main.py"],
    icon: MessageSquare,
    viewTags: ["overview"],
  },
  {
    id: "overview-runtime",
    label: "1. Runtime entende e executa",
    kind: "runtime",
    summary:
      "A trilha Runtime mostra o caminho Telegram -> semantic ingress -> stack dedicada -> resposta final.",
    whyItMatters:
      "Ela e a espinha dorsal. Sem runtime, as outras trilhas nao sao acionadas.",
    files: [
      "docs/architecture/system-architecture.md",
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/turn_router.py",
    ],
    safeguards: ["TurnFrame", "runtime dedicado", "answer surface refiner"],
    icon: Workflow,
    viewTags: ["overview"],
  },
  {
    id: "overview-decision",
    label: "Decisao de fonte da verdade",
    kind: "contract",
    summary:
      "Depois de entender o turno, o sistema decide se a resposta deve vir de dado protegido, documento/RAG, handoff ou limite de escopo.",
    whyItMatters:
      "Essa decisao liga as quatro trilhas e impede usar a fonte errada para a pergunta certa.",
    files: [
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/turn_router.py",
      "apps/ai-orchestrator/src/ai_orchestrator/retrieval_capability_policy.py",
    ],
    safeguards: ["capability", "scope", "access_tier", "confidence"],
    icon: Route,
    viewTags: ["overview"],
  },
  {
    id: "overview-protected",
    label: "2. Dados protegidos",
    kind: "policy",
    summary:
      "Se a pergunta envolve aluno, notas, frequencia, financeiro ou agenda docente, a resposta passa por api-core, authz, OPA/RLS e auditoria.",
    whyItMatters:
      "E a trilha que protege pessoas e dados sensiveis. A LLM nao vira fonte de verdade transacional.",
    files: [
      "docs/security/access-control-matrix.md",
      "apps/api-core/src/api_core/services/policy.py",
    ],
    safeguards: ["default deny", "ActorContext", "OPA + RLS", "audit trail"],
    icon: ShieldCheck,
    viewTags: ["overview"],
  },
  {
    id: "overview-rag",
    label: "3. RAG e corpus",
    kind: "pipeline",
    summary:
      "Se a pergunta e institucional/documental, o sistema busca evidencia em Postgres FTS, Qdrant, MinIO e rerank antes de responder.",
    whyItMatters:
      "E a trilha que evita responder por memoria do modelo quando existe documento institucional.",
    files: [
      "apps/worker/src/worker_app/pipeline.py",
      "apps/ai-orchestrator/src/ai_orchestrator/retrieval.py",
    ],
    safeguards: ["visibility filters", "hybrid retrieval", "evidence pack", "grounded answer"],
    icon: Radar,
    viewTags: ["overview"],
  },
  {
    id: "overview-operations",
    label: "4. Operacao e gates",
    kind: "gate",
    summary:
      "Operacao observa, escala para humano, roda smokes/evals/readiness e decide se mudancas podem ser promovidas.",
    whyItMatters:
      "E a trilha que fecha o ciclo: sem gates e observabilidade, qualidade vira opiniao.",
    files: ["docs/operations/release-readiness.md", "tools/ops/promotion_gate.py"],
    safeguards: ["smokes", "runtime parity", "scorecard", "release readiness"],
    icon: Gauge,
    viewTags: ["overview"],
  },
  {
    id: "overview-answer",
    label: "Resposta segura e auditavel",
    kind: "contract",
    summary:
      "A resposta final pode ser refinada, mas deve preservar fatos, nomes, valores, datas, escopo, evidencia e policy.",
    whyItMatters:
      "Esse e o resultado compartilhado das quatro trilhas: util para o usuario e defensavel tecnicamente.",
    files: [
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/answer_surface_refiner.py",
      "docs/architecture/system-architecture.md",
    ],
    safeguards: ["validated refiner", "fallback preservado", "trace opcional"],
    icon: ScrollText,
    viewTags: ["overview"],
  },
  {
    id: "telegram",
    label: "Telegram",
    kind: "channel",
    summary: "Canal real de entrada: mensagens publicas, pedidos protegidos, comandos /start e vinculo de conta.",
    whyItMatters:
      "O Telegram nao e uma fronteira de seguranca. Ele inicia a conversa, mas identidade e autorizacao acontecem no backend.",
    files: ["apps/telegram-gateway/src/telegram_gateway/main.py"],
    safeguards: ["webhook secret", "idempotencia por update", "lock por chat"],
    icon: MessageSquare,
    viewTags: ["runtime", "protected", "operations"],
  },
  {
    id: "gateway",
    label: "telegram-gateway",
    kind: "service",
    summary:
      "Normaliza updates, resolve contexto do ator, consome link codes e chama o runtime dedicado configurado.",
    whyItMatters:
      "Mantem o canal fino: sem regra escolar profunda, sem banco direto, sem autorizacao sensivel local.",
    files: ["apps/telegram-gateway/src/telegram_gateway/main.py"],
    reads: ["TELEGRAM_WEBHOOK_SECRET", "RUNTIME_RESPOND_URL", "X-Internal-Api-Token"],
    safeguards: ["dedupe update_id", "stale chat update guard", "service token / SPIFFE-ready bridge"],
    icon: Bot,
    viewTags: ["runtime", "protected", "operations"],
  },
  {
    id: "semantic",
    label: "Semantic ingress",
    kind: "contract",
    summary:
      "Classifica ato conversacional, capability, escopo e follow-up curto antes da execucao por stack.",
    whyItMatters:
      "Evita que cada stack reinvente roteamento semantico e reduz drift entre usuario autenticado e pergunta publica.",
    files: [
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/runtime.py",
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/turn_router.py",
    ],
    safeguards: ["TurnFrame", "FocusFrame", "candidate top-k", "schema strict output"],
    icon: Route,
    viewTags: ["runtime", "protected", "rag"],
  },
  {
    id: "runtime-api",
    label: "POST /v1/messages/respond",
    kind: "contract",
    summary:
      "Contrato interno de serving usado pelos runtimes dedicados para receber pergunta, contexto e devolver resposta traceavel.",
    whyItMatters:
      "E a fronteira entre canal e execucao. O gateway nao precisa saber se a stack e LangGraph, LlamaIndex ou specialist.",
    files: ["apps/ai-orchestrator/src/ai_orchestrator/runtime_api.py"],
    icon: Braces,
    viewTags: ["runtime", "protected", "rag"],
  },
  {
    id: "python-functions",
    label: "python_functions",
    kind: "runtime",
    summary:
      "Stack mais enxuta e previsivel; resolve por handlers tipados e caminhos deterministas de baixa latencia.",
    whyItMatters:
      "Funciona como referencia para execucao simples quando a capability ja esta clara.",
    files: [
      "apps/ai-orchestrator/src/ai_orchestrator/main_python_functions.py",
      "apps/ai-orchestrator/src/ai_orchestrator/python_functions_runtime.py",
    ],
    icon: Workflow,
    viewTags: ["runtime", "protected", "rag"],
  },
  {
    id: "langgraph",
    label: "LangGraph",
    kind: "runtime",
    summary:
      "Stack de workflow com estado explicito, edges condicionais, checkpoints e auditabilidade de decisao.",
    whyItMatters:
      "Boa para explicar por que o sistema escolheu uma rota e como follow-ups evoluem.",
    files: [
      "apps/ai-orchestrator/src/ai_orchestrator/main_langgraph.py",
      "apps/ai-orchestrator/src/ai_orchestrator/langgraph_runtime.py",
      "apps/ai-orchestrator/src/ai_orchestrator/langgraph_message_workflow.py",
    ],
    icon: GitBranch,
    viewTags: ["runtime", "rag"],
  },
  {
    id: "llamaindex",
    label: "LlamaIndex",
    kind: "runtime",
    summary:
      "Stack orientada a documentos, query routing e sintese baseada em fontes institucionais.",
    whyItMatters:
      "Importante quando a pergunta exige combinar documentos, evidencias e resumo grounded.",
    files: [
      "apps/ai-orchestrator/src/ai_orchestrator/main_llamaindex.py",
      "apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_runtime.py",
    ],
    icon: Network,
    viewTags: ["runtime", "rag"],
  },
  {
    id: "specialist",
    label: "specialist_supervisor",
    kind: "runtime",
    summary:
      "Caminho premium quality-first: supervisor, ferramentas especialistas, repair, fast paths e refino validado.",
    whyItMatters:
      "Usado para casos mais exigentes, especialmente quando ha risco semantico ou fluxo protegido complexo.",
    files: [
      "apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/main.py",
      "apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/supervisor_run_flow.py",
      "apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/specialist_tools.py",
    ],
    icon: GraduationCap,
    viewTags: ["runtime", "protected", "rag"],
  },
  {
    id: "answer-refiner",
    label: "Answer surface refiner",
    kind: "contract",
    summary:
      "Melhora a superficie final sem alterar fatos, datas, valores, nomes, escopo ou decisoes de policy.",
    whyItMatters:
      "Permite respostas menos rigidas sem abrir espaco para vazamento ou invencao.",
    files: [
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/answer_surface_refiner.py",
      "apps/ai-orchestrator/src/ai_orchestrator/stack_answer_surface_refiner.py",
    ],
    safeguards: ["validator local", "fallback preservado", "bloqueios sensiveis fora do refino livre"],
    icon: ScrollText,
    viewTags: ["runtime", "protected", "rag"],
  },
  {
    id: "identity",
    label: "Actor context",
    kind: "contract",
    summary:
      "Resolve usuario, papeis, vinculos, alunos relacionados e escopo efetivo da sessao.",
    whyItMatters:
      "Sem ActorContext correto, nenhuma consulta protegida deveria prosseguir.",
    files: [
      "apps/api-core/src/api_core/services/identity.py",
      "apps/api-core/src/api_core/contracts.py",
    ],
    safeguards: ["telegram_chat_id binding", "roles", "guardian/student/teacher links"],
    icon: Fingerprint,
    viewTags: ["protected", "runtime"],
  },
  {
    id: "api-core",
    label: "api-core",
    kind: "service",
    summary:
      "Fonte deterministica de identidade, dominio escolar, suporte, protocolos, memoria persistida e auditoria.",
    whyItMatters:
      "E a barreira entre IA e dados escolares sensiveis. A LLM orquestra; api-core decide e consulta.",
    files: ["apps/api-core/src/api_core/main.py", "apps/api-core/src/api_core/services/domain.py"],
    safeguards: ["internal token", "SPIFFE-ready allowlist", "policy check", "RLS context"],
    icon: Server,
    viewTags: ["protected", "runtime", "operations"],
  },
  {
    id: "authz",
    label: "Autorizacao contextual",
    kind: "policy",
    summary:
      "Combina Keycloak, OPA, RLS e regras de escopo para negar por padrao e liberar apenas o permitido.",
    whyItMatters:
      "Responsavel ve apenas alunos vinculados; professor ve turmas atribuidas; financeiro nao vira admin academico.",
    files: [
      "docs/security/access-control-matrix.md",
      "apps/api-core/src/api_core/services/policy.py",
      "tools/ops/check_db_rls.py",
    ],
    safeguards: ["default deny", "OPA decision", "Postgres RLS", "non-superuser runtime role"],
    icon: ShieldCheck,
    viewTags: ["protected", "operations"],
  },
  {
    id: "opa-rls",
    label: "OPA + RLS",
    kind: "policy",
    summary:
      "Dupla camada de autorizacao: decisao contextual e enforcement no banco com papel runtime limitado.",
    whyItMatters:
      "Mesmo se uma rota errar, a camada de banco continua reduzindo blast radius.",
    files: ["docs/security/security-architecture.md", "tools/ops/check_db_runtime_role.py"],
    icon: LockKeyhole,
    viewTags: ["protected", "operations"],
  },
  {
    id: "academic",
    label: "Resumo academico",
    kind: "contract",
    summary:
      "Notas, frequencia, avaliacoes e horarios consultados por servicos estruturados.",
    whyItMatters:
      "E dado transacional. Deve vir de Postgres/api-core, nao de RAG ou memoria do modelo.",
    files: [
      "apps/api-core/src/api_core/db/models/academic.py",
      "apps/api-core/src/api_core/services/domain.py",
    ],
    icon: GraduationCap,
    viewTags: ["protected"],
  },
  {
    id: "finance",
    label: "Resumo financeiro",
    kind: "contract",
    summary:
      "Contratos, faturas, pagamentos e bolsas dentro do escopo autorizado.",
    whyItMatters:
      "E um dos dominios de maior risco de exposicao indevida.",
    files: [
      "apps/api-core/src/api_core/db/models/finance.py",
      "apps/api-core/src/api_core/services/domain.py",
    ],
    icon: KeyRound,
    viewTags: ["protected"],
  },
  {
    id: "audit",
    label: "Auditoria",
    kind: "data",
    summary:
      "Registro tecnico de decisoes, acessos e eventos relevantes para depuracao e prestacao de contas.",
    whyItMatters:
      "Sem auditoria, autorizacao correta continua dificil de provar.",
    files: [
      "apps/api-core/src/api_core/services/audit.py",
      "apps/api-core/src/api_core/db/models/audit.py",
    ],
    icon: FileText,
    viewTags: ["protected", "operations"],
  },
  {
    id: "postgres",
    label: "PostgreSQL",
    kind: "data",
    summary:
      "Fonte relacional: usuarios, vinculos, alunos, notas, frequencia, financeiro, documentos, conversas e auditoria.",
    whyItMatters:
      "E a fonte de verdade para dados estruturados e tambem participa do retrieval via FTS.",
    files: ["docs/data/data-model.md", "apps/api-core/alembic/versions"],
    icon: Database,
    viewTags: ["protected", "rag", "operations"],
  },
  {
    id: "worker",
    label: "worker",
    kind: "pipeline",
    summary:
      "Sincroniza corpus, metadados, chunks, objetos e vetores para alimentar respostas documentais.",
    whyItMatters:
      "Sem pipeline documental, o RAG nao tem evidencias confiaveis para responder.",
    files: ["apps/worker/src/worker_app/pipeline.py", "apps/worker/src/worker_app/main.py"],
    icon: HardDrive,
    viewTags: ["rag"],
  },
  {
    id: "corpus",
    label: "Corpus institucional",
    kind: "document",
    summary:
      "Documentos Markdown com frontmatter versionados em data/corpus/public e catalogos restritos.",
    whyItMatters:
      "E a base textual que responde FAQ publica, calendario, matricula, bolsas e secretaria.",
    files: ["data/corpus/public/README.md", "data/corpus/public"],
    icon: FileText,
    viewTags: ["rag"],
  },
  {
    id: "minio",
    label: "MinIO",
    kind: "data",
    summary: "Armazena fontes documentais e objetos brutos do corpus.",
    whyItMatters:
      "Preserva origem do documento enquanto Postgres/Qdrant guardam indices e representacoes.",
    files: ["infra/compose/compose.yaml", "apps/worker/src/worker_app/pipeline.py"],
    icon: HardDrive,
    viewTags: ["rag"],
  },
  {
    id: "qdrant",
    label: "Qdrant",
    kind: "data",
    summary:
      "Indice vetorial para busca semantica e colecoes documentais com alias ativo.",
    whyItMatters:
      "Complementa FTS para perguntas que precisam de correspondencia semantica.",
    files: ["infra/compose/compose.yaml", "apps/worker/src/worker_app/pipeline.py"],
    icon: Radar,
    viewTags: ["rag"],
  },
  {
    id: "retrieval",
    label: "Hybrid retrieval",
    kind: "pipeline",
    summary:
      "Combina FTS, Qdrant, query variants, visibilidade, late interaction e cross-encoder rerank.",
    whyItMatters:
      "Busca evidencia antes de responder e reduz dependencia de memoria parametrica.",
    files: [
      "apps/ai-orchestrator/src/ai_orchestrator/retrieval.py",
      "apps/ai-orchestrator/src/ai_orchestrator/retrieval_capability_policy.py",
    ],
    safeguards: ["visibility filters", "weighted fusion", "rerank", "answerable evidence"],
    icon: Radar,
    viewTags: ["rag", "runtime"],
  },
  {
    id: "evidence-pack",
    label: "Evidence pack",
    kind: "contract",
    summary:
      "Trechos, fontes e sinais de grounding empacotados para composicao final.",
    whyItMatters:
      "E a fronteira entre busca e resposta: tudo que a LLM verbaliza deve estar suportado.",
    files: ["apps/ai-orchestrator/src/ai_orchestrator/evidence_pack.py"],
    icon: ScrollText,
    viewTags: ["rag"],
  },
  {
    id: "grounded-answer",
    label: "Resposta grounded",
    kind: "contract",
    summary:
      "Composicao final com evidencia, abstencao/clarificacao quando necessario e preservacao de escopo.",
    whyItMatters:
      "Boa resposta nao e so fluente; precisa ser fiel ao documento e ao que foi perguntado.",
    files: [
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/grounded_public_answer.py",
      "apps/ai-orchestrator/src/ai_orchestrator/grounded_answer_pipeline_runtime.py",
    ],
    icon: ScrollText,
    viewTags: ["rag", "runtime"],
  },
  {
    id: "admin-web",
    label: "admin-web",
    kind: "service",
    summary:
      "Painel operacional autenticado para fila humana, historico de conversas e vinculacao Telegram.",
    whyItMatters:
      "A IA precisa de uma saida segura quando nao deve resolver sozinha.",
    files: [
      "apps/admin-web/app/page.tsx",
      "apps/admin-web/app/support-handoff-panel.tsx",
      "apps/admin-web/lib/auth.ts",
    ],
    icon: UserRoundCog,
    viewTags: ["operations"],
  },
  {
    id: "handoff",
    label: "Handoff humano",
    kind: "pipeline",
    summary:
      "Cria ticket, conversa, status, prioridade e SLA para atendimento por operador.",
    whyItMatters:
      "Transforma limite seguro da IA em processo operacional, nao em beco sem saida.",
    files: [
      "apps/api-core/src/api_core/services/support.py",
      "apps/api-core/src/api_core/services/institutional_workflows.py",
    ],
    icon: UserRoundCog,
    viewTags: ["operations", "protected"],
  },
  {
    id: "observability",
    label: "Observabilidade",
    kind: "pipeline",
    summary:
      "OpenTelemetry, Tempo, Prometheus, Loki e Grafana para traces, metricas e logs.",
    whyItMatters:
      "Permite explicar latencia, falhas de provider, retrieval, roteamento e regressao.",
    files: [
      "packages/observability/python/src/eduassist_observability/runtime.py",
      "infra/compose/otel/otel-collector-config.yaml",
    ],
    icon: Activity,
    viewTags: ["operations", "runtime"],
  },
  {
    id: "scorecard",
    label: "Scorecard",
    kind: "gate",
    summary:
      "Artefato de promocao e rollout controlado por slices/allowlist.",
    whyItMatters:
      "Evita promover runtime ou modelo sem evidencias agregadas.",
    files: ["docs/architecture/framework-native-scorecard.json", "tools/ops/promotion_gate.py"],
    icon: Gauge,
    viewTags: ["operations"],
  },
  {
    id: "readiness",
    label: "Release readiness",
    kind: "gate",
    summary:
      "Consolida checks de papel runtime, RLS, evals, smokes e benchmark GraphRAG baseline.",
    whyItMatters:
      "Define quando o projeto esta pronto para demo local, handoff tecnico ou fechamento de etapa.",
    files: ["docs/operations/release-readiness.md", "tools/ops/release_readiness.py"],
    icon: Gauge,
    viewTags: ["operations"],
  },
  {
    id: "evals",
    label: "Evals cross-stack",
    kind: "gate",
    summary:
      "Suites de comparacao, retrieval probes, real-world Telegram replay e regressao multiturno.",
    whyItMatters:
      "A comparacao entre stacks so e justa quando usa dataset e contratos equivalentes.",
    files: ["tools/evals", "tests/evals/datasets/orchestrator_cases.json"],
    icon: Gauge,
    viewTags: ["operations", "runtime", "rag"],
  },
  {
    id: "release-artifacts",
    label: "Artefatos de release",
    kind: "document",
    summary:
      "Relatorios em artifacts/ e docs/architecture usados como evidencia historica, nao como fonte canonica isolada.",
    whyItMatters:
      "Ajuda a separar decisao atual de ruido de benchmark antigo.",
    files: ["docs/architecture", "artifacts"],
    icon: FileText,
    viewTags: ["operations"],
  },
];

export const atlasEdges: AtlasEdge[] = [
  { id: "ov-e1", source: "overview-question", target: "overview-runtime", label: "entra no canal", viewTags: ["overview"], criticality: "normal" },
  { id: "ov-e2", source: "overview-runtime", target: "overview-decision", label: "TurnFrame/capability", viewTags: ["overview"], criticality: "normal" },
  { id: "ov-e3", source: "overview-decision", target: "overview-protected", label: "se e sensivel", viewTags: ["overview"], criticality: "security" },
  { id: "ov-e4", source: "overview-decision", target: "overview-rag", label: "se e documental", viewTags: ["overview"], criticality: "evidence" },
  { id: "ov-e5", source: "overview-decision", target: "overview-operations", label: "se exige humano/gate", viewTags: ["overview"], criticality: "ops" },
  { id: "ov-e6", source: "overview-protected", target: "overview-answer", label: "dado autorizado", viewTags: ["overview"], criticality: "security" },
  { id: "ov-e7", source: "overview-rag", target: "overview-answer", label: "evidencia grounded", viewTags: ["overview"], criticality: "evidence" },
  { id: "ov-e8", source: "overview-operations", target: "overview-runtime", label: "feedback e regressao", viewTags: ["overview"], criticality: "ops" },
  { id: "ov-e9", source: "overview-operations", target: "overview-answer", label: "prova qualidade", viewTags: ["overview"], criticality: "ops" },
  { id: "e1", source: "telegram", target: "gateway", label: "webhook update", viewTags: ["runtime", "protected", "operations"], criticality: "normal" },
  { id: "e2", source: "gateway", target: "identity", label: "resolve actor", viewTags: ["protected", "runtime"], criticality: "security" },
  { id: "e3", source: "gateway", target: "runtime-api", label: "respond request", viewTags: ["runtime"], criticality: "normal" },
  { id: "e4", source: "runtime-api", target: "semantic", label: "TurnFrame", viewTags: ["runtime", "protected", "rag"], criticality: "normal" },
  { id: "e5", source: "semantic", target: "python-functions", label: "capability adapter", viewTags: ["runtime"], criticality: "normal" },
  { id: "e6", source: "semantic", target: "langgraph", label: "state graph", viewTags: ["runtime"], criticality: "normal" },
  { id: "e7", source: "semantic", target: "llamaindex", label: "query routing", viewTags: ["runtime", "rag"], criticality: "evidence" },
  { id: "e8", source: "semantic", target: "specialist", label: "premium supervisor", viewTags: ["runtime", "protected", "rag"], criticality: "normal" },
  { id: "e9", source: "python-functions", target: "answer-refiner", label: "surface polish", viewTags: ["runtime"], criticality: "normal" },
  { id: "e10", source: "langgraph", target: "answer-refiner", label: "surface polish", viewTags: ["runtime"], criticality: "normal" },
  { id: "e11", source: "llamaindex", target: "answer-refiner", label: "grounded polish", viewTags: ["runtime", "rag"], criticality: "evidence" },
  { id: "e12", source: "specialist", target: "answer-refiner", label: "validated refiner", viewTags: ["runtime", "protected", "rag"], criticality: "security" },
  { id: "e13", source: "identity", target: "authz", label: "scope + roles", viewTags: ["protected"], criticality: "security" },
  { id: "e14", source: "authz", target: "opa-rls", label: "policy enforcement", viewTags: ["protected", "operations"], criticality: "security" },
  { id: "e15", source: "authz", target: "api-core", label: "allowed request", viewTags: ["protected"], criticality: "security" },
  { id: "e16", source: "api-core", target: "academic", label: "structured read", viewTags: ["protected"], criticality: "security" },
  { id: "e17", source: "api-core", target: "finance", label: "structured read", viewTags: ["protected"], criticality: "security" },
  { id: "e18", source: "api-core", target: "audit", label: "audit trail", viewTags: ["protected", "operations"], criticality: "ops" },
  { id: "e19", source: "api-core", target: "postgres", label: "source of truth", viewTags: ["protected", "operations"], criticality: "security" },
  { id: "e20", source: "worker", target: "corpus", label: "load markdown", viewTags: ["rag"], criticality: "evidence" },
  { id: "e21", source: "worker", target: "minio", label: "source objects", viewTags: ["rag"], criticality: "evidence" },
  { id: "e22", source: "worker", target: "postgres", label: "catalog + FTS", viewTags: ["rag"], criticality: "evidence" },
  { id: "e23", source: "worker", target: "qdrant", label: "vectors", viewTags: ["rag"], criticality: "evidence" },
  { id: "e24", source: "semantic", target: "retrieval", label: "document capability", viewTags: ["rag"], criticality: "evidence" },
  { id: "e25", source: "retrieval", target: "postgres", label: "FTS + metadata", viewTags: ["rag"], criticality: "evidence" },
  { id: "e26", source: "retrieval", target: "qdrant", label: "semantic search", viewTags: ["rag"], criticality: "evidence" },
  { id: "e27", source: "retrieval", target: "evidence-pack", label: "ranked context", viewTags: ["rag"], criticality: "evidence" },
  { id: "e28", source: "evidence-pack", target: "grounded-answer", label: "supported claims", viewTags: ["rag"], criticality: "evidence" },
  { id: "e29", source: "grounded-answer", target: "answer-refiner", label: "safe wording", viewTags: ["rag", "runtime"], criticality: "evidence" },
  { id: "e30", source: "api-core", target: "handoff", label: "ticket + conversation", viewTags: ["operations", "protected"], criticality: "ops" },
  { id: "e31", source: "handoff", target: "admin-web", label: "operator queue", viewTags: ["operations"], criticality: "ops" },
  { id: "e32", source: "runtime-api", target: "observability", label: "trace spans", viewTags: ["operations", "runtime"], criticality: "ops" },
  { id: "e33", source: "retrieval", target: "observability", label: "retrieval traces", viewTags: ["operations", "rag"], criticality: "ops" },
  { id: "e34", source: "evals", target: "scorecard", label: "quality signal", viewTags: ["operations", "runtime", "rag"], criticality: "ops" },
  { id: "e35", source: "scorecard", target: "readiness", label: "promotion gate", viewTags: ["operations"], criticality: "ops" },
  { id: "e36", source: "readiness", target: "release-artifacts", label: "readiness report", viewTags: ["operations"], criticality: "ops" },
];

export const gates: Gate[] = [
  {
    label: "Dedicated smoke",
    command: "make smoke-dedicated",
    protects: "runtime dedicado e contrato /v1/messages/respond",
    evidence: "docs/architecture/dedicated-first-reference-state.md",
    status: "baseline",
  },
  {
    label: "Multiturn memory",
    command: "make smoke-dedicated-multiturn",
    protects: "follow-ups, TurnFrame e FocusFrame",
    evidence: "packages/semantic-ingress/python/src/eduassist_semantic_ingress/turn_router.py",
    status: "baseline",
  },
  {
    label: "Authz and RLS",
    command: "make smoke-authz && make db-check-rls",
    protects: "dados protegidos e default deny",
    evidence: "docs/security/access-control-matrix.md",
    status: "baseline",
  },
  {
    label: "Telegram real",
    command: "make smoke-telegram-dedicated",
    protects: "gateway -> runtime -> api-core",
    evidence: "apps/telegram-gateway/src/telegram_gateway/main.py",
    status: "baseline",
  },
  {
    label: "Promotion gate",
    command: "make promotion-gate-check",
    protects: "rollout por scorecard e slices",
    evidence: "tools/ops/promotion_gate.py",
    status: "baseline",
  },
  {
    label: "Strict GraphRAG",
    command: "make release-readiness-strict",
    protects: "benchmark GraphRAG completo com provider valido",
    evidence: "docs/operations/release-readiness.md",
    status: "strict",
  },
];

export const nodeKindLabels: Record<AtlasNodeKind, string> = {
  channel: "Canal",
  service: "Servico",
  runtime: "Runtime",
  endpoint: "Endpoint",
  contract: "Contrato",
  data: "Dado",
  policy: "Policy",
  pipeline: "Pipeline",
  document: "Documento",
  gate: "Gate",
};

const allViews: AtlasView[] = ["runtime", "protected", "rag", "operations"];

function microNode(
  id: string,
  label: string,
  kind: AtlasNodeKind,
  summary: string,
  whyItMatters: string,
  files: string[],
  icon: ComponentType<{ size?: number; strokeWidth?: number }>,
  tags: AtlasView[] = allViews,
  safeguards?: string[],
): AtlasNode {
  return {
    id,
    label,
    kind,
    summary,
    whyItMatters,
    files,
    icon,
    viewTags: tags,
    safeguards,
  };
}

function microEdge(
  id: string,
  source: string,
  target: string,
  label: string,
  criticality: AtlasEdge["criticality"] = "normal",
): AtlasEdge {
  return { id, source, target, label, criticality, viewTags: allViews };
}

export const drilldowns: Record<string, DrilldownGraph> = {
  langgraph: {
    id: "langgraph",
    parentNodeId: "langgraph",
    title: "LangGraph por dentro",
    subtitle:
      "Como o caminho LangGraph recebe o TurnFrame, monta estado, escolhe edges condicionais e preserva rastreabilidade.",
    readOrder: [
      "apps/ai-orchestrator/src/ai_orchestrator/main_langgraph.py",
      "apps/ai-orchestrator/src/ai_orchestrator/langgraph_runtime.py",
      "apps/ai-orchestrator/src/ai_orchestrator/langgraph_message_workflow.py",
      "apps/ai-orchestrator/src/ai_orchestrator/langgraph_trace.py",
      "apps/ai-orchestrator/src/ai_orchestrator/stack_postprocessing.py",
    ],
    nodes: [
      microNode("lg-entry", "FastAPI entrypoint", "endpoint", "Servidor dedicado do LangGraph recebe /v1/messages/respond.", "Isola serving dedicado do control plane central.", ["apps/ai-orchestrator/src/ai_orchestrator/main_langgraph.py"], Braces),
      microNode("lg-frame", "TurnFrame bootstrap", "contract", "Injeta capability, escopo, contexto recente e preview semantico no estado inicial.", "A stack executa sobre uma interpretacao compartilhada, nao sobre heuristica isolada.", ["apps/ai-orchestrator/src/ai_orchestrator/langgraph_runtime.py", "packages/semantic-ingress/python/src/eduassist_semantic_ingress/turn_router.py"], Route),
      microNode("lg-state", "Workflow state", "contract", "Estado do grafo carrega mensagem, usuario, trace, evidencias e decisao de rota.", "Permite explicar cada transicao e reproduzir decisoes.", ["apps/ai-orchestrator/src/ai_orchestrator/langgraph_message_workflow.py"], GitBranch),
      microNode("lg-router", "Conditional routing", "pipeline", "Edges condicionais escolhem publico, protegido, retrieval, clarificacao, handoff ou fallback.", "E aqui que LangGraph ganha auditabilidade visual.", ["apps/ai-orchestrator/src/ai_orchestrator/langgraph_message_workflow.py"], Workflow),
      microNode("lg-public", "Public structured path", "pipeline", "Perguntas publicas fortes seguem handlers e retrieval quando necessario.", "Evita cair em dominio protegido so porque o usuario esta autenticado.", ["apps/ai-orchestrator/src/ai_orchestrator/langgraph_public_retrieval_runtime.py"], FileText),
      microNode("lg-protected", "Protected path", "policy", "Consultas protegidas chamam api-core e preservam policy/escopo.", "LangGraph nao le banco direto.", ["apps/ai-orchestrator/src/ai_orchestrator/protected_records_runtime.py"], ShieldCheck),
      microNode("lg-trace", "Trace envelope", "document", "Registra decisao, engine, capability, eventos e footer de debug.", "Sem trace, o grafo vira caixa-preta.", ["apps/ai-orchestrator/src/ai_orchestrator/langgraph_trace.py"], Activity),
      microNode("lg-polish", "Stack postprocessing", "contract", "Refino final validado preserva fatos e bloqueios.", "Melhora texto sem reabrir decisao de policy.", ["apps/ai-orchestrator/src/ai_orchestrator/stack_postprocessing.py"], ScrollText),
    ],
    edges: [
      microEdge("lg-e1", "lg-entry", "lg-frame", "request -> semantic frame"),
      microEdge("lg-e2", "lg-frame", "lg-state", "bootstrap state"),
      microEdge("lg-e3", "lg-state", "lg-router", "conditional graph"),
      microEdge("lg-e4", "lg-router", "lg-public", "public/documental", "evidence"),
      microEdge("lg-e5", "lg-router", "lg-protected", "protected capability", "security"),
      microEdge("lg-e6", "lg-public", "lg-trace", "events"),
      microEdge("lg-e7", "lg-protected", "lg-trace", "policy events", "security"),
      microEdge("lg-e8", "lg-trace", "lg-polish", "final surface"),
    ],
  },
  "python-functions": {
    id: "python-functions",
    parentNodeId: "python-functions",
    title: "python_functions por dentro",
    subtitle:
      "Caminho deterministico: TurnFrame reduz ambiguidade, planner escolhe handler tipado e postprocessing valida a superficie.",
    readOrder: [
      "apps/ai-orchestrator/src/ai_orchestrator/main_python_functions.py",
      "apps/ai-orchestrator/src/ai_orchestrator/python_functions_runtime.py",
      "apps/ai-orchestrator/src/ai_orchestrator/python_functions_native_plan_runtime.py",
      "apps/ai-orchestrator/src/ai_orchestrator/python_functions_public_knowledge.py",
      "apps/ai-orchestrator/src/ai_orchestrator/stack_postprocessing.py",
    ],
    nodes: [
      microNode("pf-entry", "Dedicated FastAPI", "endpoint", "Entry point dedicado da stack python_functions.", "Mantem baixa latencia e separa serving do control plane.", ["apps/ai-orchestrator/src/ai_orchestrator/main_python_functions.py"], Braces),
      microNode("pf-turn", "TurnFrame intake", "contract", "Recebe capability, scope, access_tier e candidatos.", "Evita duplicar classificadores por handler.", ["apps/ai-orchestrator/src/ai_orchestrator/python_functions_runtime.py"], Route),
      microNode("pf-plan", "Native plan", "pipeline", "Planeja rota nativa: publico, protegido, retrieval, workflow ou clarificacao.", "A decisao fica pequena, testavel e previsivel.", ["apps/ai-orchestrator/src/ai_orchestrator/python_functions_native_plan_runtime.py"], Workflow),
      microNode("pf-handlers", "Typed handlers", "runtime", "Handlers especializados executam capabilities conhecidas.", "Boa stack de referencia para comportamento esperado.", ["apps/ai-orchestrator/src/ai_orchestrator/python_functions_runtime.py"], Workflow),
      microNode("pf-public", "Public knowledge", "pipeline", "FAQ e conhecimento publico usam rotas estruturadas e retrieval.", "Reduz custo quando resposta publica e direta.", ["apps/ai-orchestrator/src/ai_orchestrator/python_functions_public_knowledge.py"], FileText),
      microNode("pf-protected", "Protected tools", "policy", "Dados sensiveis passam por api-core e contracts.", "Mantem a LLM fora do banco.", ["apps/ai-orchestrator/src/ai_orchestrator/protected_records_runtime.py"], ShieldCheck),
      microNode("pf-post", "Postprocessing", "contract", "Refino final so e aceito quando preserva fatos.", "Nao sacrifica confiabilidade por fluidez.", ["apps/ai-orchestrator/src/ai_orchestrator/stack_postprocessing.py"], ScrollText),
    ],
    edges: [
      microEdge("pf-e1", "pf-entry", "pf-turn", "request"),
      microEdge("pf-e2", "pf-turn", "pf-plan", "capability plan"),
      microEdge("pf-e3", "pf-plan", "pf-handlers", "dispatch"),
      microEdge("pf-e4", "pf-handlers", "pf-public", "public lane", "evidence"),
      microEdge("pf-e5", "pf-handlers", "pf-protected", "protected lane", "security"),
      microEdge("pf-e6", "pf-public", "pf-post", "answer"),
      microEdge("pf-e7", "pf-protected", "pf-post", "safe answer", "security"),
    ],
  },
  llamaindex: {
    id: "llamaindex",
    parentNodeId: "llamaindex",
    title: "LlamaIndex por dentro",
    subtitle:
      "Como a stack documental transforma capability em query engines, retrieval, sintese e resposta grounded.",
    readOrder: [
      "apps/ai-orchestrator/src/ai_orchestrator/main_llamaindex.py",
      "apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_runtime.py",
      "apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_plan_runtime.py",
      "apps/ai-orchestrator/src/ai_orchestrator/llamaindex_retrieval.py",
      "apps/ai-orchestrator/src/ai_orchestrator/llamaindex_public_knowledge.py",
    ],
    nodes: [
      microNode("li-entry", "Dedicated endpoint", "endpoint", "Servidor dedicado LlamaIndex.", "Separa workflow documental de outras stacks.", ["apps/ai-orchestrator/src/ai_orchestrator/main_llamaindex.py"], Braces),
      microNode("li-turn", "TurnFrame planner", "contract", "Usa capability para reduzir o conjunto de query engines elegiveis.", "Roteamento documental fica orientado ao dominio.", ["apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_plan_runtime.py"], Route),
      microNode("li-kernel", "LlamaIndex kernel", "runtime", "Kernel nativo organiza query, engines e composicao.", "E o nucleo da stack documental.", ["apps/ai-orchestrator/src/ai_orchestrator/llamaindex_kernel.py"], Network),
      microNode("li-retrieval", "LlamaIndex retrieval", "pipeline", "Busca chunks, documentos e conhecimento publico.", "A stack se destaca aqui.", ["apps/ai-orchestrator/src/ai_orchestrator/llamaindex_retrieval.py"], Radar),
      microNode("li-source", "Source synthesis", "contract", "Sintese deve permanecer orientada a fontes.", "Garante resposta grounded.", ["apps/ai-orchestrator/src/ai_orchestrator/llamaindex_public_knowledge.py"], FileText),
      microNode("li-fallback", "Known unknowns", "policy", "Quando evidencia nao sustenta resposta, abstencao/clarificacao vence.", "Evita alucinacao documental.", ["apps/ai-orchestrator/src/ai_orchestrator/llamaindex_public_known_unknowns.py"], ShieldCheck),
    ],
    edges: [
      microEdge("li-e1", "li-entry", "li-turn", "request"),
      microEdge("li-e2", "li-turn", "li-kernel", "plan"),
      microEdge("li-e3", "li-kernel", "li-retrieval", "query engines", "evidence"),
      microEdge("li-e4", "li-retrieval", "li-source", "nodes + sources", "evidence"),
      microEdge("li-e5", "li-source", "li-fallback", "answerability check", "evidence"),
    ],
  },
  specialist: {
    id: "specialist",
    parentNodeId: "specialist",
    title: "specialist_supervisor por dentro",
    subtitle:
      "Supervisor premium: fast paths, ferramentas especialistas, retrieval local, repair e refino validado.",
    readOrder: [
      "apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/runtime.py",
      "apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/supervisor_run_flow.py",
      "apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/specialist_executor.py",
      "apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/specialist_tools.py",
      "apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/judge_repair_flow.py",
    ],
    nodes: [
      microNode("sp-entry", "Specialist runtime", "endpoint", "Entrada dedicada do runtime premium.", "Isola custo e complexidade do caminho quality-first.", ["apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/main.py"], Braces),
      microNode("sp-fast", "Fast paths", "pipeline", "Respostas obvias ou deterministicas evitam supervisor desnecessario.", "Economiza latencia e reduz risco.", ["apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/fast_path_answer_runtime.py"], Workflow),
      microNode("sp-supervisor", "Supervisor flow", "runtime", "Coordena especialistas, ferramentas, evidencia e decisao final.", "Centro do caminho premium.", ["apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/supervisor_run_flow.py"], GraduationCap),
      microNode("sp-tools", "Specialist tools", "contract", "Ferramentas estreitas para dados, documentos, workflows e contexto.", "Tool surface auditavel e limitada.", ["apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/specialist_tools.py"], ShieldCheck),
      microNode("sp-retrieval", "Local retrieval", "pipeline", "Busca e rerank local com contratos proprios.", "Dá evidencia ao supervisor.", ["apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/local_retrieval.py"], Radar),
      microNode("sp-repair", "Judge/repair", "policy", "Julga e repara saidas de risco ou baixa qualidade.", "Controle adicional do caminho caro.", ["apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/judge_repair_flow.py"], Gauge),
      microNode("sp-refine", "Validated refiner", "contract", "Refino final com validacao de fatos e escopo.", "Evita polish inseguro.", ["apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/answer_payloads.py"], ScrollText),
    ],
    edges: [
      microEdge("sp-e1", "sp-entry", "sp-fast", "precheck"),
      microEdge("sp-e2", "sp-fast", "sp-supervisor", "needs premium"),
      microEdge("sp-e3", "sp-supervisor", "sp-tools", "tool calls", "security"),
      microEdge("sp-e4", "sp-supervisor", "sp-retrieval", "evidence", "evidence"),
      microEdge("sp-e5", "sp-tools", "sp-repair", "tool result"),
      microEdge("sp-e6", "sp-retrieval", "sp-repair", "retrieved evidence", "evidence"),
      microEdge("sp-e7", "sp-repair", "sp-refine", "accepted answer", "security"),
    ],
  },
  semantic: {
    id: "semantic",
    parentNodeId: "semantic",
    title: "Semantic ingress por dentro",
    subtitle:
      "O nucleo que impede drift semantico entre stacks: normalize, candidate generation, FocusFrame, classificador e budget.",
    readOrder: [
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/runtime.py",
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/turn_router.py",
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/context_budget.py",
      "packages/semantic-ingress/python/src/eduassist_semantic_ingress/turn_preview.py",
    ],
    nodes: [
      microNode("se-normalize", "Normalize input", "pipeline", "Normaliza texto e detecta atos curtos/opacos.", "Protege contra fallback errado em entrada ambigua.", ["packages/semantic-ingress/python/src/eduassist_semantic_ingress/runtime.py"], Route),
      microNode("se-focus", "FocusFrame", "contract", "Memoria curta: entidade, atributo, ator e capability ativos.", "Follow-up curto precisa de contexto, mas com limites.", ["packages/semantic-ingress/python/src/eduassist_semantic_ingress/turn_router.py"], Fingerprint),
      microNode("se-candidates", "Capability candidates", "pipeline", "Gera top-k por aliases, auth, memoria e sinais do turno.", "Reduz espaco de decisao da LLM.", ["packages/semantic-ingress/python/src/eduassist_semantic_ingress/turn_router.py"], Workflow),
      microNode("se-budget", "Context budget", "contract", "Empacota historico e candidatas por estimativa de tokens.", "Evita truncamento silencioso.", ["packages/semantic-ingress/python/src/eduassist_semantic_ingress/context_budget.py"], Gauge),
      microNode("se-llm", "Structured classifier", "runtime", "LLM escolhe capability sob schema e regras de precedencia.", "Classifica; nao responde ao usuario.", ["packages/semantic-ingress/python/src/eduassist_semantic_ingress/turn_router.py"], Braces),
      microNode("se-frame", "TurnFrame", "contract", "Resultado canonico consumido pelas stacks.", "Contrato que unifica o sistema.", ["packages/semantic-ingress/python/src/eduassist_semantic_ingress/turn_router.py"], ScrollText),
    ],
    edges: [
      microEdge("se-e1", "se-normalize", "se-focus", "recent context"),
      microEdge("se-e2", "se-focus", "se-candidates", "carryover signals"),
      microEdge("se-e3", "se-candidates", "se-budget", "candidate payload"),
      microEdge("se-e4", "se-budget", "se-llm", "bounded prompt"),
      microEdge("se-e5", "se-llm", "se-frame", "strict JSON"),
    ],
  },
  "api-core": {
    id: "api-core",
    parentNodeId: "api-core",
    title: "api-core por dentro",
    subtitle:
      "Fronteira deterministica para identidade, authz, dominio escolar, suporte, auditoria e banco.",
    readOrder: [
      "apps/api-core/src/api_core/main.py",
      "apps/api-core/src/api_core/services/identity.py",
      "apps/api-core/src/api_core/services/policy.py",
      "apps/api-core/src/api_core/services/domain.py",
      "apps/api-core/src/api_core/services/support.py",
    ],
    nodes: [
      microNode("api-entry", "FastAPI routes", "endpoint", "Endpoints publicos, internos e autenticados.", "Centraliza contratos de dados.", ["apps/api-core/src/api_core/main.py"], Braces),
      microNode("api-settings", "Settings + internal auth", "policy", "Configura token interno, Keycloak, OPA, DB e allowlists.", "Protege chamadas service-to-service.", ["apps/api-core/src/api_core/config.py"], LockKeyhole),
      microNode("api-identity", "Identity service", "contract", "Resolve ator, papeis e vinculos.", "Sem isso nao ha acesso protegido.", ["apps/api-core/src/api_core/services/identity.py"], Fingerprint),
      microNode("api-policy", "Policy service", "policy", "Chama OPA e configura contexto RLS.", "Default deny no caminho sensivel.", ["apps/api-core/src/api_core/services/policy.py"], ShieldCheck),
      microNode("api-domain", "Domain services", "service", "Academico, financeiro, calendario e perfil publico.", "Dado estruturado sai daqui.", ["apps/api-core/src/api_core/services/domain.py"], Server),
      microNode("api-support", "Support/workflows", "pipeline", "Handoffs, visitas, protocolos e status operacional.", "Liga IA a atendimento humano.", ["apps/api-core/src/api_core/services/support.py", "apps/api-core/src/api_core/services/institutional_workflows.py"], UserRoundCog),
      microNode("api-audit", "Audit trail", "data", "Registra eventos e consultas sensiveis.", "Prova tecnica de comportamento.", ["apps/api-core/src/api_core/services/audit.py"], FileText),
    ],
    edges: [
      microEdge("api-e1", "api-entry", "api-settings", "internal guard", "security"),
      microEdge("api-e2", "api-entry", "api-identity", "actor context", "security"),
      microEdge("api-e3", "api-identity", "api-policy", "roles + scope", "security"),
      microEdge("api-e4", "api-policy", "api-domain", "allowed", "security"),
      microEdge("api-e5", "api-domain", "api-audit", "record access", "ops"),
      microEdge("api-e6", "api-entry", "api-support", "handoff workflows", "ops"),
      microEdge("api-e7", "api-support", "api-audit", "operator trail", "ops"),
    ],
  },
  worker: {
    id: "worker",
    parentNodeId: "worker",
    title: "worker documental por dentro",
    subtitle:
      "Como o corpus versionado vira objetos, chunks, FTS, vetores e aliases prontos para retrieval.",
    readOrder: [
      "apps/worker/src/worker_app/main.py",
      "apps/worker/src/worker_app/pipeline.py",
      "apps/worker/src/worker_app/llamaindex_pipeline.py",
      "data/corpus/public/README.md",
    ],
    nodes: [
      microNode("wk-cli", "Worker command", "endpoint", "CLI/job para sync documental.", "Permite reconstruir indices localmente.", ["apps/worker/src/worker_app/main.py"], Braces),
      microNode("wk-load", "Load corpus", "document", "Le Markdown/frontmatter e catalogos restritos.", "A qualidade do RAG comeca na fonte.", ["apps/worker/src/worker_app/pipeline.py", "data/corpus/public"], FileText),
      microNode("wk-chunk", "Chunking", "pipeline", "Divide documentos e preserva metadados.", "Chunks ruins produzem respostas ruins.", ["apps/worker/src/worker_app/pipeline.py"], Workflow),
      microNode("wk-minio", "Upload source", "data", "Publica arquivo original no MinIO.", "Preserva origem.", ["apps/worker/src/worker_app/pipeline.py"], HardDrive),
      microNode("wk-postgres", "Catalog + FTS", "data", "Grava document sets, versions, chunks e indices textuais.", "Base lexical e auditavel.", ["apps/worker/src/worker_app/pipeline.py"], Database),
      microNode("wk-qdrant", "Qdrant publish", "data", "Publica vetores, payload indexes e alias ativo.", "Base semantica para retrieval.", ["apps/worker/src/worker_app/pipeline.py"], Radar),
    ],
    edges: [
      microEdge("wk-e1", "wk-cli", "wk-load", "sync"),
      microEdge("wk-e2", "wk-load", "wk-chunk", "parse"),
      microEdge("wk-e3", "wk-chunk", "wk-minio", "source object", "evidence"),
      microEdge("wk-e4", "wk-chunk", "wk-postgres", "chunks + FTS", "evidence"),
      microEdge("wk-e5", "wk-chunk", "wk-qdrant", "embeddings", "evidence"),
    ],
  },
};
