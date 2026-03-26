from __future__ import annotations

from pydantic import BaseModel, Field


class CrewAIPublicPlan(BaseModel):
    intent: str = 'unknown'
    entity: str | None = None
    attribute: str | None = None
    needs_clarification: bool = False
    required_tools: list[str] = Field(default_factory=list)


class CrewAIPublicFlowState(BaseModel):
    conversation_id: str | None = None
    message: str
    normalized_message: str
    engine_name: str = 'crewai'
    slice_name: str = 'public'
    planner_status: str = 'pending'
    composer_status: str = 'pending'
    judge_status: str = 'pending'
    dependency_available: bool = False
    dependency_reason: str = ''
    plan: CrewAIPublicPlan = Field(default_factory=CrewAIPublicPlan)
    evidence_summary: dict[str, str] = Field(default_factory=dict)
