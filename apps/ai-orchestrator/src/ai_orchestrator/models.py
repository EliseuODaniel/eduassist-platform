from __future__ import annotations

from enum import StrEnum
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UserRole(StrEnum):
    anonymous = 'anonymous'
    guardian = 'guardian'
    student = 'student'
    teacher = 'teacher'
    staff = 'staff'
    finance = 'finance'
    coordinator = 'coordinator'
    admin = 'admin'


class QueryDomain(StrEnum):
    institution = 'institution'
    calendar = 'calendar'
    academic = 'academic'
    finance = 'finance'
    support = 'support'
    unknown = 'unknown'


class AccessTier(StrEnum):
    public = 'public'
    authenticated = 'authenticated'
    sensitive = 'sensitive'


class OrchestrationMode(StrEnum):
    hybrid_retrieval = 'hybrid_retrieval'
    graph_rag = 'graph_rag'
    structured_tool = 'structured_tool'
    handoff = 'handoff'
    clarify = 'clarify'
    deny = 'deny'


class RetrievalBackend(StrEnum):
    qdrant_hybrid = 'qdrant_hybrid'
    graph_rag = 'graph_rag'
    none = 'none'


class RetrievalProfile(StrEnum):
    cheap = 'cheap'
    default = 'default'
    deep = 'deep'


class ToolKind(StrEnum):
    retrieval = 'retrieval'
    data_service = 'data_service'
    operation = 'operation'


class UserContext(BaseModel):
    role: UserRole = UserRole.anonymous
    authenticated: bool = False
    linked_student_ids: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)


class OrchestrationRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    user: UserContext = Field(default_factory=UserContext)
    allow_graph_rag: bool = True
    allow_handoff: bool = True


class IntentClassification(BaseModel):
    domain: QueryDomain
    access_tier: AccessTier
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class ToolContract(BaseModel):
    name: str
    description: str
    kind: ToolKind
    access_tier: AccessTier
    source_of_truth: str
    deterministic: bool
    input_schema: dict[str, Any]
    output_contract: str
    triggers: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class OrchestrationPreview(BaseModel):
    mode: OrchestrationMode
    classification: IntentClassification
    retrieval_backend: RetrievalBackend = RetrievalBackend.none
    selected_tools: list[str] = Field(default_factory=list)
    citations_required: bool = False
    needs_authentication: bool = False
    graph_path: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    reason: str
    output_contract: str


class RuntimeCapabilities(BaseModel):
    service: str
    llm_provider: str
    openai_model: str
    google_model: str
    llm_configured: bool
    graph_rag_enabled: bool
    graph_rag_workspace_ready: bool
    strict_framework_isolation_enabled: bool
    supported_primary_stacks: list[str]
    python_functions_available: bool
    llamaindex_workflow_available: bool
    specialist_supervisor_available: bool = False
    telegram_debug_trace_footer_enabled: bool = False
    experimental_stack_readiness: dict[str, dict[str, object]] = Field(default_factory=dict)
    available_modes: list[OrchestrationMode]
    retrieval_backends: list[RetrievalBackend]


class RetrievalSearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=4000)
    top_k: int = Field(default=6, ge=1, le=20)
    visibility: str = Field(default='public')
    category: str | None = None
    profile: RetrievalProfile | None = None


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
    support_excerpt_count: int = 0
    section_titles: list[str] = Field(default_factory=list)
    citation: RetrievalCitation


class RetrievalQueryPlan(BaseModel):
    intent: str
    profile: RetrievalProfile = RetrievalProfile.default
    normalized_query: str
    query_variants: list[str] = Field(default_factory=list)
    graph_rag_candidate: bool = False
    reranker_applied: bool = False
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


class ConversationChannel(StrEnum):
    telegram = 'telegram'
    web = 'web'
    api = 'api'


class CalendarEventCard(BaseModel):
    event_id: str
    title: str
    description: str | None = None
    category: str
    audience: str
    visibility: str
    starts_at: datetime
    ends_at: datetime


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


class MessageResponseVisualAsset(BaseModel):
    asset_type: str = 'image'
    title: str
    mime_type: str
    base64_data: str
    caption: str | None = None


class MessageResponseSuggestedReply(BaseModel):
    text: str = Field(min_length=1, max_length=80)


class MessageResponseRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: ConversationChannel = ConversationChannel.telegram
    user: UserContext = Field(default_factory=UserContext)
    allow_graph_rag: bool = True
    allow_handoff: bool = True


class MessageResponse(BaseModel):
    message_text: str
    mode: OrchestrationMode
    classification: IntentClassification
    retrieval_backend: RetrievalBackend = RetrievalBackend.none
    selected_tools: list[str] = Field(default_factory=list)
    citations: list[MessageResponseCitation] = Field(default_factory=list)
    visual_assets: list[MessageResponseVisualAsset] = Field(default_factory=list)
    suggested_replies: list[MessageResponseSuggestedReply] = Field(default_factory=list)
    calendar_events: list[CalendarEventCard] = Field(default_factory=list)
    evidence_pack: MessageEvidencePack | None = None
    needs_authentication: bool = False
    graph_path: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    reason: str
    debug_trace: dict[str, Any] | None = None
