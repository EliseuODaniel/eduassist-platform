from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ConversationChannel(StrEnum):
    telegram = "telegram"
    web = "web"
    api = "api"


class UserContext(BaseModel):
    role: str = "anonymous"
    authenticated: bool = False
    linked_student_ids: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)


class SpecialistSupervisorRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: ConversationChannel = ConversationChannel.telegram
    user: UserContext = Field(default_factory=UserContext)
    allow_graph_rag: bool = True
    allow_handoff: bool = True


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
