from __future__ import annotations

from enum import StrEnum
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
    qdrant_url: str
    graph_rag_enabled: bool
    available_modes: list[OrchestrationMode]
    retrieval_backends: list[RetrievalBackend]
