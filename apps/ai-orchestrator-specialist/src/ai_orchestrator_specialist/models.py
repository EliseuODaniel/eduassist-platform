from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field
from pydantic import model_validator

from eduassist_observability import canonicalize_evidence_strategy, canonicalize_risk_flags


class ConversationChannel(StrEnum):
    telegram = "telegram"
    web = "web"
    api = "api"


class UserContext(BaseModel):
    role: str = "anonymous"
    authenticated: bool = False
    linked_student_ids: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)


class RetrievalBackend(StrEnum):
    qdrant_hybrid = 'qdrant_hybrid'
    graph_rag = 'graph_rag'
    none = 'none'


class RetrievalProfile(StrEnum):
    cheap = 'cheap'
    default = 'default'
    deep = 'deep'


class RetrievalCitation(BaseModel):
    document_title: str
    version_label: str
    storage_path: str
    chunk_id: str
    chunk_index: int
    section_path: str | None = None


class RetrievalHit(BaseModel):
    chunk_id: str
    document_title: str
    document_set_slug: str | None = None
    category: str
    audience: str
    visibility: str
    text_excerpt: str
    contextual_summary: str | None = None
    section_path: str | None = None
    section_parent: str | None = None
    section_title: str | None = None
    parent_ref_key: str | None = None
    labels: dict[str, list[str]] = Field(default_factory=dict)
    fused_score: float
    document_score: float | None = None
    lexical_score: float | None = None
    vector_score: float | None = None
    rerank_score: float | None = None
    citation: RetrievalCitation


class RetrievalDocumentGroup(BaseModel):
    document_title: str
    document_set_slug: str | None = None
    category: str
    audience: str
    visibility: str
    document_score: float
    primary_excerpt: str
    primary_summary: str | None = None
    primary_section: str | None = None
    parent_ref_key: str | None = None
    support_excerpt_count: int = 0
    section_titles: list[str] = Field(default_factory=list)
    citation: RetrievalCitation


class RetrievalQueryPlan(BaseModel):
    intent: str
    profile: RetrievalProfile = RetrievalProfile.default
    normalized_query: str
    query_variants: list[str] = Field(default_factory=list)
    subqueries: list[str] = Field(default_factory=list)
    subquery_coverage: dict[str, float] = Field(default_factory=dict)
    uncovered_subqueries_final: list[str] = Field(default_factory=list)
    coverage_ratio: float = 1.0
    citation_first_recommended: bool = False
    graph_rag_candidate: bool = False
    reranker_applied: bool = False
    corrective_retry_applied: bool = False
    reranker_model: str | None = None
    category_bias: str | None = None
    canonical_lane: str | None = None
    candidate_pool_size: int = 0
    lexical_limit: int = 0
    vector_limit: int = 0
    rerank_limit: int = 0
    max_chunks_per_document: int = 0


class RetrievalSearchResponse(BaseModel):
    query: str
    retrieval_backend: RetrievalBackend
    total_hits: int
    hits: list[RetrievalHit]
    document_groups: list[RetrievalDocumentGroup] = Field(default_factory=list)
    query_plan: RetrievalQueryPlan | None = None
    context_pack: str | None = None


class SpecialistSupervisorRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: ConversationChannel = ConversationChannel.telegram
    user: UserContext = Field(default_factory=UserContext)
    allow_graph_rag: bool = True
    allow_handoff: bool = True
    debug_options: dict[str, Any] = Field(default_factory=dict)


class MessageResponseCitation(BaseModel):
    document_title: str
    version_label: str
    storage_path: str
    chunk_id: str
    excerpt: str


class MessageEvidenceSupport(BaseModel):
    kind: str
    label: str
    detail: str | None = None
    excerpt: str | None = None


class MessageEvidencePack(BaseModel):
    strategy: str
    summary: str
    source_count: int = 0
    support_count: int = 0
    supports: list[MessageEvidenceSupport] = Field(default_factory=list)


class MessageResponseSuggestedReply(BaseModel):
    text: str = Field(min_length=1, max_length=80)


class MessageIntentClassification(BaseModel):
    domain: str
    access_tier: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str = ""


class SupervisorAnswerPayload(BaseModel):
    message_text: str
    mode: str
    classification: MessageIntentClassification
    retrieval_backend: str = "none"
    selected_tools: list[str] = Field(default_factory=list)
    citations: list[MessageResponseCitation] = Field(default_factory=list)
    visual_assets: list[dict[str, Any]] = Field(default_factory=list)
    suggested_replies: list[MessageResponseSuggestedReply] = Field(default_factory=list)
    calendar_events: list[dict[str, Any]] = Field(default_factory=list)
    evidence_pack: MessageEvidencePack | None = None
    needs_authentication: bool = False
    graph_path: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    reason: str
    used_llm: bool = False
    llm_stages: list[str] = Field(default_factory=list)
    final_polish_eligible: bool = False
    final_polish_applied: bool = False
    final_polish_mode: str | None = None
    final_polish_reason: str | None = None
    final_polish_changed_text: bool = False
    final_polish_preserved_fallback: bool = False

    @model_validator(mode="after")
    def _normalize_contract(self) -> "SupervisorAnswerPayload":
        self.risk_flags = canonicalize_risk_flags(self.risk_flags)
        if self.evidence_pack is not None:
            self.evidence_pack.strategy = canonicalize_evidence_strategy(
                self.evidence_pack.strategy,
                retrieval_backend=self.retrieval_backend,
            )
        return self


class SpecialistSupervisorResponse(BaseModel):
    engine_name: str = "specialist_supervisor"
    executed: bool = True
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    answer: SupervisorAnswerPayload | None = None


PlannerRequestKind = Literal["simple", "complex", "ambiguous", "sensitive", "multi_domain"]
RetrievalStrategy = Literal[
    "direct_answer",
    "structured_tools",
    "hybrid_retrieval",
    "graph_rag",
    "document_search",
    "pricing_projection",
    "workflow_status",
    "clarify",
    "deny",
]
SpecialistId = Literal[
    "retrieval_planner",
    "institution_specialist",
    "academic_specialist",
    "finance_specialist",
    "workflow_specialist",
    "document_specialist",
    "judge_specialist",
]
ExecutionBudgetTier = Literal["cheap", "standard", "premium"]
PlannerMode = Literal["deterministic", "adaptive"]


class SpecialistSpec(BaseModel):
    id: SpecialistId
    name: str
    description: str
    supported_domains: list[str] = Field(default_factory=list)
    supported_slices: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    risk_level: str = "medium"
    max_context_budget: int = 6
    execution_priority: int = 100
    allow_parallel: bool = True
    allow_precompute: bool = True
    manager_policy: Literal["always", "prefer_direct"] = "always"
    preferred_categories: list[str] = Field(default_factory=list)
    latency_tier: Literal["low", "medium", "high"] = "medium"
    compose_label: str | None = None
    compose_template: Literal["paragraph", "bullet", "summary"] = "paragraph"
    combinable_with: list[SpecialistId] = Field(default_factory=list)
    memory_topics: list[str] = Field(default_factory=list)
    handoff_enabled: bool = False
    handoff_queue: str | None = None
    activation_flag: bool = True


class SupervisorInputGuardrail(BaseModel):
    blocked: bool = False
    reason: str = ""
    safe_reply: str | None = None


class OperationalMemory(BaseModel):
    active_domain: str | None = None
    active_domains: list[str] = Field(default_factory=list)
    active_student_id: str | None = None
    active_student_name: str | None = None
    alternate_student_id: str | None = None
    alternate_student_name: str | None = None
    active_subject: str | None = None
    active_topic: str | None = None
    pending_kind: str | None = None
    pending_prompt: str | None = None
    multi_intent_domains: list[str] = Field(default_factory=list)
    last_specialists: list[str] = Field(default_factory=list)
    last_route: str | None = None
    last_reason: str | None = None


class IntentRouteSpec(BaseModel):
    key: str
    domain: str
    subintent: str
    capability: str
    access_tier: str = "public"
    priority: int = 100
    requires_auth: bool = False
    requires_grounding: bool = True
    any_terms: list[str] = Field(default_factory=list)
    all_terms: list[str] = Field(default_factory=list)
    none_terms: list[str] = Field(default_factory=list)
    preview_domains: list[str] = Field(default_factory=list)
    memory_domains: list[str] = Field(default_factory=list)
    carry_active_student: bool = False
    carry_active_subject: bool = False
    examples: list[str] = Field(default_factory=list)


class ResolvedTurnIntent(BaseModel):
    key: str = "unknown"
    domain: str = "unknown"
    subintent: str = "unknown"
    capability: str = "unknown"
    access_tier: str = "public"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    requires_grounding: bool = False
    referenced_student_id: str | None = None
    referenced_student_name: str | None = None
    referenced_subject: str | None = None
    used_operational_memory: bool = False
    rationale: str = ""


class SupervisorPlan(BaseModel):
    request_kind: PlannerRequestKind
    primary_domain: str
    secondary_domains: list[str] = Field(default_factory=list)
    specialists: list[SpecialistId] = Field(default_factory=list)
    retrieval_strategy: RetrievalStrategy = "direct_answer"
    requires_clarification: bool = False
    clarification_question: str | None = None
    should_deny: bool = False
    denial_reason: str | None = None
    reasoning_summary: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class RetrievalPlannerAdvice(BaseModel):
    normalized_query: str
    primary_domain: str
    secondary_domains: list[str] = Field(default_factory=list)
    retrieval_strategy: RetrievalStrategy = "direct_answer"
    recommended_specialists: list[SpecialistId] = Field(default_factory=list)
    preferred_category: str | None = None
    evidence_queries: list[str] = Field(default_factory=list)
    requires_grounding: bool = False
    requires_clarification: bool = False
    clarification_question: str | None = None
    should_deny: bool = False
    denial_reason: str | None = None
    rationale: str = ""
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ExecutionBudget(BaseModel):
    tier: ExecutionBudgetTier = "standard"
    planner_mode: PlannerMode = "deterministic"
    target_latency_ms: int = Field(default=1500, ge=100)
    max_specialists: int = Field(default=1, ge=0, le=4)
    allow_parallel_specialists: bool = True
    allow_manager: bool = False
    allow_judge: bool = False
    allow_repair: bool = False
    allow_session_memory: bool = False
    prefer_direct_answer: bool = True
    specialist_max_turns: int = Field(default=4, ge=1, le=12)
    manager_max_turns: int = Field(default=6, ge=1, le=12)
    judge_max_turns: int = Field(default=3, ge=1, le=8)
    repair_max_turns: int = Field(default=3, ge=1, le=8)
    reasons: list[str] = Field(default_factory=list)


class SpecialistResult(BaseModel):
    specialist_id: SpecialistId
    answer_text: str
    evidence_summary: str
    tool_names: list[str] = Field(default_factory=list)
    support_points: list[str] = Field(default_factory=list)
    citations: list[MessageResponseCitation] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ManagerDraft(BaseModel):
    answer_text: str
    answer_summary: str
    specialists_used: list[SpecialistId] = Field(default_factory=list)
    citations: list[MessageResponseCitation] = Field(default_factory=list)
    suggested_replies: list[str] = Field(default_factory=list)


class RepairDraft(BaseModel):
    answer_text: str
    answer_summary: str
    specialists_used: list[SpecialistId] = Field(default_factory=list)
    citations: list[MessageResponseCitation] = Field(default_factory=list)
    suggested_replies: list[str] = Field(default_factory=list)
    repair_notes: list[str] = Field(default_factory=list)


class JudgeVerdict(BaseModel):
    approved: bool
    revised_answer_text: str | None = None
    needs_clarification: bool = False
    clarification_question: str | None = None
    grounding_score: float = Field(default=0.0, ge=0.0, le=1.0)
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    recommended_replies: list[str] = Field(default_factory=list)
    rationale: str = ""
