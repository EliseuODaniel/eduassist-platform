from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

from .models import MessageResponseCitation


PlannerRequestKind = Literal['simple', 'complex', 'ambiguous', 'sensitive', 'multi_domain']
RetrievalStrategy = Literal[
    'direct_answer',
    'structured_tools',
    'hybrid_retrieval',
    'graph_rag',
    'document_search',
    'pricing_projection',
    'workflow_status',
    'clarify',
    'deny',
]
SpecialistId = Literal[
    'retrieval_planner',
    'institution_specialist',
    'academic_specialist',
    'finance_specialist',
    'workflow_specialist',
    'document_specialist',
    'judge_specialist',
]


@dataclass(frozen=True)
class SpecialistSpec:
    id: SpecialistId
    name: str
    description: str
    supported_domains: tuple[str, ...]
    supported_slices: tuple[str, ...]
    allowed_tools: tuple[str, ...]
    risk_level: str = 'medium'
    max_context_budget: int = 6
    activation_flag: bool = True


class SupervisorInputGuardrail(BaseModel):
    blocked: bool = False
    reason: str = ''
    safe_reply: str | None = None


class SupervisorPlan(BaseModel):
    request_kind: PlannerRequestKind
    primary_domain: str
    secondary_domains: list[str] = Field(default_factory=list)
    specialists: list[SpecialistId] = Field(default_factory=list)
    retrieval_strategy: RetrievalStrategy = 'direct_answer'
    requires_clarification: bool = False
    clarification_question: str | None = None
    should_deny: bool = False
    denial_reason: str | None = None
    reasoning_summary: str
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


class JudgeVerdict(BaseModel):
    approved: bool
    revised_answer_text: str | None = None
    needs_clarification: bool = False
    clarification_question: str | None = None
    grounding_score: float = Field(default=0.0, ge=0.0, le=1.0)
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    recommended_replies: list[str] = Field(default_factory=list)
    rationale: str = ''

