from __future__ import annotations

# ruff: noqa: F401,F403,F405

"""Public profile and public-act runtime helpers extracted from runtime.py.

This module is imported lazily from runtime.py after the shared helper surface is
already defined. It intentionally reuses the legacy runtime namespace during the
ongoing decomposition, so extracted functions keep behavior while the monolith
is split into focused modules.
"""

from . import runtime_core as _runtime_core
from .conversation_focus_runtime import _assistant_already_introduced
from .conversation_focus_runtime import _normalize_text
from .conversation_focus_runtime import _recent_conversation_focus
from .conversation_focus_runtime import _recent_focus_follow_up_line
from .conversation_focus_runtime import _recent_message_lines
from .conversation_focus_runtime import _recent_trace_focus
from .conversation_focus_runtime import _is_greeting_only
from .intent_analysis_runtime import (
    _compose_required_documents_answer,
    _contains_any,
    _is_explicit_public_pricing_projection_query,
    _is_assistant_identity_query,
    _is_capability_query,
    _is_direct_service_routing_bundle_query,
    _is_follow_up_query,
    _is_positive_requirement_query,
    _is_public_pricing_navigation_query,
    _is_service_routing_query,
    _message_matches_term,
    _requested_operating_hours_attribute,
)
from .analysis_context_runtime import _extract_recent_assistant_message, _extract_recent_user_message
from .intent_analysis_runtime import _extract_salient_terms
from . import public_contact_runtime as _public_contact_runtime
from .public_contact_runtime import (
    _contact_entries,
    _contact_is_general_school_query,
    _contact_value,
    _count_public_contact_subjects,
    _extract_teacher_subject,
    _format_contact_origin,
    _is_public_teacher_directory_follow_up,
    _is_public_teacher_identity_query,
    _requested_contact_channel,
    _select_primary_contact_entry,
    _wants_contact_list,
)
from . import public_calendar_runtime as _public_calendar_runtime
from .public_calendar_runtime import _handle_public_calendar_events
from . import public_commercial_runtime as _public_commercial_runtime
from .public_commercial_runtime import (
    _compose_public_enrichment_answer,
    _compose_public_scholarship_answer,
    _is_public_enrichment_query,
    _is_public_scholarship_query,
)
from . import public_concierge_runtime as _public_concierge_runtime
from .public_concierge_runtime import (
    _compose_capability_answer,
    _compose_concierge_acknowledgement,
    _compose_concierge_greeting,
    _compose_public_pedagogical_answer,
    _compose_service_routing_answer,
    _compose_service_routing_menu,
    _explicit_service_routing_lines,
    _handle_public_acknowledgement,
    _handle_public_capabilities,
    _handle_public_features,
    _handle_public_greeting,
    _handle_public_operating_hours,
    _handle_public_service_routing,
    _is_acknowledgement_query,
    _target_public_feature_for_operating_hours,
)
from . import public_operations_runtime as _public_operations_runtime
from .public_operations_runtime import (
    _compose_public_pricing_projection_answer,
    _format_brl,
    _handle_public_capacity,
    _handle_public_pricing,
    _handle_public_schedule,
    _handle_public_segments,
    _is_public_pricing_projection_context,
    _parse_public_money,
)
from . import public_multi_intent_runtime as _public_multi_intent_runtime
from .public_multi_intent_runtime import (
    _candidate_public_multi_intent_acts,
    _compose_public_act_answer,
    _compose_public_multi_intent_answer,
)
from . import public_curriculum_runtime as _public_curriculum_runtime
from .public_curriculum_runtime import (
    _extract_public_curriculum_subject_focus,
    _handle_public_curriculum,
    _is_public_curriculum_query,
    _match_public_curriculum_component,
)
from . import public_document_policy_runtime as _public_document_policy_runtime
from .public_document_policy_runtime import (
    _compose_public_document_submission_answer,
    _compose_public_policy_answer,
    _compose_public_policy_compare_answer,
    _compose_public_service_credentials_bundle_answer,
    _handle_public_document_submission,
    _handle_public_policy,
    _handle_public_policy_compare,
    _handle_public_service_credentials_bundle,
    _is_public_document_submission_query,
    _is_public_policy_compare_query,
    _is_public_policy_query,
    _is_public_service_credentials_bundle_query,
)
from . import public_feature_runtime as _public_feature_runtime
from .public_feature_runtime import (
    _asks_why_feature_is_missing,
    _extract_feature_gap_focus,
    _feature_inventory_map,
    _feature_suggestion_replies,
    _is_public_feature_query,
    _recent_public_feature_key,
    _requested_public_features,
)
from . import public_handlers_runtime as _public_handlers_runtime
from .public_handlers_runtime import (
    NON_AGENTIC_PUBLIC_COMPOSITION_ACTS,
    _handle_public_access_scope,
    _handle_public_assistant_identity,
    _handle_public_auth_guidance,
    _handle_public_confessional,
    _handle_public_contacts,
    _handle_public_input_clarification,
    _handle_public_language_preference,
    _handle_public_location,
    _handle_public_school_name,
    _handle_public_scope_boundary,
    _handle_public_timeline,
    _handle_public_utility_date,
    _handle_public_visit,
    _public_profile_handler_registry,
)
from . import public_profile_support_runtime as _public_profile_support_runtime
from .public_profile_support_runtime import (
    _capability_summary_lines,
    _compose_assistant_identity_answer,
    _compose_concierge_topic_examples,
    _compose_public_segment_scope_gap,
    _concierge_topic_examples,
    _extract_grade_reference,
    _humanize_service_eta,
    _public_feature_inventory,
    _public_segment_matches,
    _public_service_catalog,
    _public_visit_offers,
    _published_public_segments,
    _requested_public_attribute,
    _requested_public_attributes,
    _requested_unpublished_public_segment,
    _school_object_reference,
    _school_subject_reference,
    _segment_semantic_key,
    _select_public_segment,
)
from . import public_profile_intent_runtime as _public_profile_intent_runtime
from .public_profile_intent_runtime import (
    _compose_external_public_facility_boundary_answer,
    _compose_input_clarification_answer,
    _compose_language_preference_answer,
    _compose_scope_boundary_answer,
    _has_public_multi_intent_signal,
    _is_public_bolsas_and_processes_query,
    _is_public_calendar_visibility_query,
    _is_public_capacity_query,
    _is_public_careers_query,
    _is_public_family_new_calendar_enrollment_query,
    _is_public_first_month_risks_query,
    _is_public_health_authorization_bridge_query,
    _is_public_health_second_call_query,
    _is_public_navigation_query,
    _is_public_operating_hours_query,
    _is_public_permanence_family_query,
    _is_public_process_compare_query,
    _is_public_school_name_query,
    _is_public_social_query,
    _is_public_web_query,
    _looks_like_public_documentary_open_query,
    _looks_like_teacher_internal_scope_query,
    _match_public_act_rule,
    _matched_public_act_rules,
    _prioritize_public_act_rules,
    _resolve_public_profile_act,
)
from . import public_profile_glue_runtime as _public_profile_glue_runtime
from .public_profile_glue_runtime import (
    _compose_public_feature_schedule_follow_up,
    _llm_forced_mode_enabled,
    _localize_pt_br_surface_labels,
    _matches_public_contact_rule,
    _recent_messages_mention,
    _recent_user_message_mentions,
)
from . import public_agentic_answer_runtime as _public_agentic_answer_runtime
from .public_agentic_answer_runtime import (
    _compose_public_profile_answer_agentic,
    _maybe_langgraph_open_documentary_candidate,
)
from . import public_answer_compose_runtime as _public_answer_compose_runtime
from .public_answer_compose_runtime import _compose_public_profile_answer
from . import public_followup_preservation_runtime as _public_followup_preservation_runtime
from .public_followup_preservation_runtime import (
    _contextualize_public_followup_message,
    _must_preserve_contextual_public_followup_message,
    _should_preserve_deterministic_public_answer,
    _should_prefer_raw_public_followup_message,
)
from . import public_organization_runtime as _public_organization_runtime
from .public_organization_runtime import (
    _compose_public_leadership_answer,
    _compose_public_teacher_directory_answer,
    _handle_public_highlight,
    _handle_public_kpi,
    _handle_public_leadership,
    _handle_public_teacher_directory,
    _is_leadership_specific_query,
    _leadership_inventory,
    _public_highlights,
    _public_kpis,
    _select_leadership_member,
    _select_public_highlight,
    _select_public_kpis,
)
from . import public_presence_runtime as _public_presence_runtime
from .public_presence_runtime import (
    _compose_public_comparative_answer,
    _compose_public_comparative_practical_answer,
    _handle_public_careers,
    _handle_public_comparative,
    _handle_public_social_presence,
    _handle_public_web_presence,
)
from .public_orchestration_runtime import _build_public_institution_plan, _should_use_public_open_documentary_synthesis
from . import public_service_routing_runtime as _public_service_routing_runtime
from .public_service_routing_runtime import (
    _is_generic_service_contact_follow_up,
    _preferred_contact_labels_from_context,
    _public_contact_reference_message,
    _recent_public_contact_subject,
    _recent_service_match,
    _routing_follow_up_context_message,
    _service_catalog_index,
    _service_matches_from_message,
)
from . import public_timeline_runtime as _public_timeline_runtime
from .public_timeline_runtime import (
    _compose_contextual_public_timeline_followup_answer,
    _compose_public_school_year_start_answer,
    _compose_public_timeline_before_after_answer,
    _compose_public_timeline_lifecycle_answer,
    _compose_public_timeline_order_only_answer,
    _compose_public_travel_planning_answer,
    _compose_public_year_three_phases_answer,
    _format_brazilian_date,
    _format_public_date_text,
    _is_explicit_school_year_start_query,
    _is_public_calendar_event_query,
    _is_public_date_query,
    _is_public_timeline_before_after_query,
    _is_public_timeline_lifecycle_query,
    _is_public_timeline_query,
    _is_public_travel_planning_query,
    _is_public_year_three_phase_query,
    _mentions_school_year_start_topic,
    _parse_iso_date_value,
)
from .student_scope_runtime import _compose_public_access_scope_answer


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


def _bind_explicit_public_runtime_helpers() -> None:
    for module, names in (
        (
            _public_contact_runtime,
            (
                '_contact_entries',
                '_contact_is_general_school_query',
                '_contact_value',
                '_count_public_contact_subjects',
                '_extract_teacher_subject',
                '_format_contact_origin',
                '_is_public_teacher_directory_follow_up',
                '_is_public_teacher_identity_query',
                '_requested_contact_channel',
                '_select_primary_contact_entry',
                '_wants_contact_list',
            ),
        ),
        (
            _public_calendar_runtime,
            ('_handle_public_calendar_events',),
        ),
        (
            _public_document_policy_runtime,
            (
                '_compose_public_document_submission_answer',
                '_compose_public_policy_answer',
                '_compose_public_policy_compare_answer',
                '_compose_public_service_credentials_bundle_answer',
                '_handle_public_document_submission',
                '_handle_public_policy',
                '_handle_public_policy_compare',
                '_handle_public_service_credentials_bundle',
                '_is_public_document_submission_query',
                '_is_public_policy_compare_query',
                '_is_public_policy_query',
                '_is_public_service_credentials_bundle_query',
            ),
        ),
        (
            _public_curriculum_runtime,
            (
                '_extract_public_curriculum_subject_focus',
                '_handle_public_curriculum',
                '_is_public_curriculum_query',
                '_match_public_curriculum_component',
            ),
        ),
        (
            _public_commercial_runtime,
            (
                '_compose_public_enrichment_answer',
                '_compose_public_scholarship_answer',
                '_is_public_enrichment_query',
                '_is_public_scholarship_query',
            ),
        ),
        (
            _public_operations_runtime,
            (
                '_compose_public_pricing_projection_answer',
                '_format_brl',
                '_handle_public_capacity',
                '_handle_public_pricing',
                '_handle_public_schedule',
                '_handle_public_segments',
                '_is_public_pricing_projection_context',
                '_parse_public_money',
            ),
        ),
        (
            _public_concierge_runtime,
            (
                '_compose_capability_answer',
                '_compose_concierge_acknowledgement',
                '_compose_concierge_greeting',
                '_compose_public_pedagogical_answer',
                '_compose_service_routing_answer',
                '_compose_service_routing_menu',
                '_explicit_service_routing_lines',
                '_handle_public_acknowledgement',
                '_handle_public_capabilities',
                '_handle_public_features',
                '_handle_public_greeting',
                '_handle_public_operating_hours',
                '_handle_public_service_routing',
                '_is_acknowledgement_query',
                '_target_public_feature_for_operating_hours',
            ),
        ),
        (
            _public_multi_intent_runtime,
            (
                '_candidate_public_multi_intent_acts',
                '_compose_public_act_answer',
                '_compose_public_multi_intent_answer',
            ),
        ),
        (
            _public_organization_runtime,
            (
                '_compose_public_leadership_answer',
                '_compose_public_teacher_directory_answer',
                '_handle_public_highlight',
                '_handle_public_kpi',
                '_handle_public_leadership',
                '_handle_public_teacher_directory',
                '_is_leadership_specific_query',
                '_leadership_inventory',
                '_public_highlights',
                '_public_kpis',
                '_select_leadership_member',
                '_select_public_highlight',
                '_select_public_kpis',
            ),
        ),
        (
            _public_presence_runtime,
            (
                '_compose_public_comparative_answer',
                '_compose_public_comparative_practical_answer',
                '_handle_public_careers',
                '_handle_public_comparative',
                '_handle_public_social_presence',
                '_handle_public_web_presence',
            ),
        ),
        (
            _public_feature_runtime,
            (
                '_asks_why_feature_is_missing',
                '_extract_feature_gap_focus',
                '_feature_inventory_map',
                '_feature_suggestion_replies',
                '_is_public_feature_query',
                '_recent_public_feature_key',
                '_requested_public_features',
            ),
        ),
        (
            _public_handlers_runtime,
            (
                'NON_AGENTIC_PUBLIC_COMPOSITION_ACTS',
                '_handle_public_access_scope',
                '_handle_public_assistant_identity',
                '_handle_public_auth_guidance',
                '_handle_public_confessional',
                '_handle_public_contacts',
                '_handle_public_input_clarification',
                '_handle_public_language_preference',
                '_handle_public_location',
                '_handle_public_school_name',
                '_handle_public_scope_boundary',
                '_handle_public_timeline',
                '_handle_public_utility_date',
                '_handle_public_visit',
                '_public_profile_handler_registry',
            ),
        ),
        (
            _public_profile_support_runtime,
            (
                '_capability_summary_lines',
                '_compose_assistant_identity_answer',
                '_compose_concierge_topic_examples',
                '_compose_public_segment_scope_gap',
                '_concierge_topic_examples',
                '_extract_grade_reference',
                '_humanize_service_eta',
                '_public_feature_inventory',
                '_public_segment_matches',
                '_public_service_catalog',
                '_public_visit_offers',
                '_published_public_segments',
                '_requested_public_attribute',
                '_requested_public_attributes',
                '_requested_unpublished_public_segment',
                '_school_object_reference',
                '_school_subject_reference',
                '_segment_semantic_key',
                '_select_public_segment',
            ),
        ),
        (
            _public_profile_intent_runtime,
            (
                '_compose_external_public_facility_boundary_answer',
                '_compose_input_clarification_answer',
                '_compose_language_preference_answer',
                '_compose_scope_boundary_answer',
                '_has_public_multi_intent_signal',
                '_is_public_bolsas_and_processes_query',
                '_is_public_calendar_visibility_query',
                '_is_public_capacity_query',
                '_is_public_careers_query',
                '_is_public_family_new_calendar_enrollment_query',
                '_is_public_first_month_risks_query',
                '_is_public_health_authorization_bridge_query',
                '_is_public_health_second_call_query',
                '_is_public_navigation_query',
                '_is_public_operating_hours_query',
                '_is_public_permanence_family_query',
                '_is_public_process_compare_query',
                '_is_public_school_name_query',
                '_is_public_social_query',
                '_is_public_web_query',
                '_looks_like_public_documentary_open_query',
                '_looks_like_teacher_internal_scope_query',
                '_match_public_act_rule',
                '_matched_public_act_rules',
                '_prioritize_public_act_rules',
                '_resolve_public_profile_act',
            ),
        ),
        (
            _public_profile_glue_runtime,
            (
                '_compose_public_feature_schedule_follow_up',
                '_llm_forced_mode_enabled',
                '_localize_pt_br_surface_labels',
                '_matches_public_contact_rule',
                '_recent_messages_mention',
                '_recent_user_message_mentions',
            ),
        ),
        (
            _public_agentic_answer_runtime,
            (
                '_compose_public_profile_answer_agentic',
                '_maybe_langgraph_open_documentary_candidate',
            ),
        ),
        (
            _public_answer_compose_runtime,
            ('_compose_public_profile_answer',),
        ),
        (
            _public_followup_preservation_runtime,
            (
                '_contextualize_public_followup_message',
                '_must_preserve_contextual_public_followup_message',
                '_should_preserve_deterministic_public_answer',
                '_should_prefer_raw_public_followup_message',
            ),
        ),
        (
            _public_service_routing_runtime,
            (
                '_is_generic_service_contact_follow_up',
                '_preferred_contact_labels_from_context',
                '_public_contact_reference_message',
                '_recent_public_contact_subject',
                '_recent_service_match',
                '_routing_follow_up_context_message',
                '_service_catalog_index',
                '_service_matches_from_message',
            ),
        ),
        (
            _public_timeline_runtime,
            (
                '_compose_contextual_public_timeline_followup_answer',
                '_compose_public_school_year_start_answer',
                '_compose_public_timeline_before_after_answer',
                '_compose_public_timeline_lifecycle_answer',
                '_compose_public_timeline_order_only_answer',
                '_compose_public_travel_planning_answer',
                '_compose_public_year_three_phases_answer',
                '_format_brazilian_date',
                '_format_public_date_text',
                '_is_explicit_school_year_start_query',
                '_is_public_calendar_event_query',
                '_is_public_date_query',
                '_is_public_timeline_before_after_query',
                '_is_public_timeline_lifecycle_query',
                '_is_public_timeline_query',
                '_is_public_travel_planning_query',
                '_is_public_year_three_phase_query',
                '_mentions_school_year_start_topic',
                '_parse_iso_date_value',
            ),
        ),
    ):
        for name in names:
            globals()[name] = getattr(module, name)


_bind_explicit_public_runtime_helpers()
def _build_conversation_slot_memory(
    *,
    actor: dict[str, Any] | None,
    profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    request_message: str | None = None,
    public_plan: PublicInstitutionPlan | None = None,
    preview: Any | None = None,
) -> ConversationSlotMemory:
    from .public_profile_slot_memory_runtime import _build_conversation_slot_memory_impl as _impl

    return _impl(
        actor=actor,
        profile=profile,
        conversation_context=conversation_context,
        request_message=request_message,
        public_plan=public_plan,
        preview=preview,
    )



def _compose_public_feature_answer(
    profile: dict[str, Any],
    *,
    original_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    from .public_profile_routes_runtime import _compose_public_feature_answer_impl as _impl

    return _impl(
        profile=profile,
        original_message=original_message,
        analysis_message=analysis_message,
        conversation_context=conversation_context,
    )

def _base_profile_supports_fast_public_answer(
    *,
    message: str,
    profile: dict[str, Any] | None,
) -> bool:
    if not isinstance(profile, dict):
        return False
    if _is_public_timeline_query(message):
        return bool(profile.get('public_timeline'))
    if _is_public_calendar_event_query(message):
        return bool(profile.get('public_calendar_events'))
    return True


def _try_public_channel_fast_answer(
    profile: dict[str, Any],
    message: str,
    *,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> str | None:
    from .public_profile_routes_runtime import _try_public_channel_fast_answer_impl as _impl

    return _impl(
        profile,
        message,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )



def _compose_public_profile_answer_legacy(
    profile: dict[str, Any],
    message: str,
    *,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> str:
    from .public_profile_legacy_runtime import _compose_public_profile_answer_legacy as _impl

    return _impl(
        profile,
        message,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )



def _build_public_profile_context(
    profile: dict[str, Any],
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> PublicProfileContext:
    from .public_profile_routes_runtime import _build_public_profile_context_impl as _impl

    return _impl(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
