from __future__ import annotations

from typing import Any

from .public_doc_knowledge import (
    compose_public_academic_policy_overview,
    compose_public_bolsas_and_processes,
    compose_public_calendar_visibility,
    compose_public_calendar_week,
    compose_public_canonical_lane_answer as _shared_compose_public_canonical_lane_answer,
    compose_public_conduct_policy_contextual_answer as _shared_compose_public_conduct_policy_contextual_answer,
    compose_public_conduct_frequency_punctuality,
    compose_public_conduct_frequency_recovery_bridge,
    compose_public_facilities_and_study_support,
    compose_public_family_new_calendar_assessment_enrollment,
    compose_public_first_month_risks,
    compose_public_governance_protocol,
    compose_public_health_authorizations_bridge,
    compose_public_health_emergency_bundle,
    compose_public_health_second_call,
    compose_public_inclusion_accessibility,
    compose_public_integral_study_support,
    compose_public_outings_authorizations,
    compose_public_permanence_and_family_support,
    compose_public_process_compare,
    compose_public_secretaria_portal_credentials,
    compose_public_teacher_directory_boundary,
    compose_public_timeline_lifecycle_bundle,
    compose_public_transversal_year_bundle,
    compose_public_transport_uniform_bundle,
    compose_public_year_three_phases,
    match_public_canonical_lane as _shared_match_public_canonical_lane,
)


def match_public_canonical_lane(message: str) -> str | None:
    return _shared_match_public_canonical_lane(message)


def compose_public_canonical_lane_answer(
    lane: str,
    *,
    profile: dict[str, Any] | None = None,
) -> str | None:
    return _shared_compose_public_canonical_lane_answer(lane, profile=profile)


def compose_public_conduct_policy_contextual_answer(
    message: str,
    *,
    profile: dict[str, Any] | None = None,
) -> str | None:
    return _shared_compose_public_conduct_policy_contextual_answer(message, profile=profile)
