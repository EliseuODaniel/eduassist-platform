from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrewAgentSpec:
    role: str
    goal: str
    backstory: str


def build_public_agent_specs() -> tuple[CrewAgentSpec, CrewAgentSpec, CrewAgentSpec]:
    return (
        CrewAgentSpec(
            role='planner',
            goal='Resolve public institutional intent, entity, attribute, and tool needs.',
            backstory='A bounded planner for public institutional questions.',
        ),
        CrewAgentSpec(
            role='composer',
            goal='Compose a grounded, concise, natural public answer from evidence.',
            backstory='A grounded answer writer for institutional public flows.',
        ),
        CrewAgentSpec(
            role='judge',
            goal='Verify semantic coverage and groundedness before acceptance.',
            backstory='A lightweight semantic reviewer for public institutional answers.',
        ),
    )
