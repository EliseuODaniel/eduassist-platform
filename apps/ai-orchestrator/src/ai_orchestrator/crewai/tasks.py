from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrewTaskSpec:
    name: str
    expected_output: str


def build_public_task_specs() -> tuple[CrewTaskSpec, CrewTaskSpec, CrewTaskSpec]:
    return (
        CrewTaskSpec(
            name='public_planning',
            expected_output='Structured public plan with intent, entity, attribute, and tools.',
        ),
        CrewTaskSpec(
            name='public_composition',
            expected_output='Grounded natural-language answer draft for the public slice.',
        ),
        CrewTaskSpec(
            name='public_judging',
            expected_output='Structured validity decision with reason and revision flag.',
        ),
    )
