from __future__ import annotations

from typing import Any

from .conversation_focus_runtime import _assistant_already_introduced
from .intent_analysis_runtime import (
    _is_follow_up_query,
    _message_matches_term,
    _normalize_text,
    _should_reuse_public_pricing_slots,
)
from .public_contact_runtime import (
    _contact_is_general_school_query,
    _requested_contact_channel,
)
from .public_profile_slot_memory_runtime import _build_conversation_slot_memory_impl
from .public_profile_support_runtime import _select_public_segment
from .public_service_routing_runtime import (
    _preferred_contact_labels_from_context,
    _public_contact_reference_message,
)
from .runtime_core_constants import PUBLIC_SCHEDULE_TERMS


def _build_public_profile_context_impl(
    profile: dict[str, Any],
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: Any | None = None,
    public_profile_context_cls: type[Any],
) -> Any:
    effective_conversation_context = conversation_context
    if semantic_plan is not None and semantic_plan.conversation_act == 'greeting':
        # A terminal greeting classified at ingress should not inherit the
        # previous workflow as if it were a follow-up.
        effective_conversation_context = None
    source_message = original_message or message
    normalized = _normalize_text(source_message)
    analysis_normalized = _normalize_text(message)
    slot_memory = _build_conversation_slot_memory_impl(
        actor=None,
        profile=profile,
        conversation_context=effective_conversation_context,
        request_message=source_message,
        public_plan=semantic_plan,
    )
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    school_reference = (
        'a escola' if _assistant_already_introduced(effective_conversation_context) else school_name
    )
    school_reference_capitalized = (
        'A escola' if school_reference == 'a escola' else school_reference
    )
    postal_code_raw = profile.get('postal_code')
    website_url_raw = profile.get('website_url')
    fax_number_raw = profile.get('fax_number')
    curriculum_basis_raw = profile.get('curriculum_basis')
    segment = _select_public_segment(message) or _select_public_segment(source_message)
    if segment is None and _should_reuse_public_pricing_slots(source_message):
        segment = slot_memory.public_pricing_segment
    schedule_context_normalized = normalized
    if _is_follow_up_query(source_message) and any(
        _message_matches_term(analysis_normalized, term) for term in PUBLIC_SCHEDULE_TERMS
    ):
        schedule_context_normalized = analysis_normalized
    contact_reference_message = _public_contact_reference_message(
        profile=profile,
        source_message=source_message,
        analysis_message=message,
        conversation_context=effective_conversation_context,
    )
    preferred_contact_labels = tuple(
        _preferred_contact_labels_from_context(
            profile,
            source_message,
            effective_conversation_context,
        )
    )
    if _contact_is_general_school_query(contact_reference_message):
        preferred_contact_labels = ()
    return public_profile_context_cls(
        profile=profile,
        actor=actor,
        message=message,
        source_message=source_message,
        normalized=normalized,
        analysis_normalized=analysis_normalized,
        school_name=school_name,
        school_reference=school_reference,
        school_reference_capitalized=school_reference_capitalized,
        city=str(profile.get('city', '')),
        state=str(profile.get('state', '')),
        district=str(profile.get('district', '')),
        address_line=str(profile.get('address_line', '')),
        postal_code=postal_code_raw.strip() if isinstance(postal_code_raw, str) else '',
        website_url=website_url_raw.strip() if isinstance(website_url_raw, str) else '',
        fax_number=fax_number_raw.strip() if isinstance(fax_number_raw, str) else '',
        curriculum_basis=curriculum_basis_raw.strip()
        if isinstance(curriculum_basis_raw, str)
        else '',
        curriculum_components=tuple(
            str(item).strip()
            for item in profile.get('curriculum_components', [])
            if isinstance(item, str) and str(item).strip()
        ),
        confessional_status=str(profile.get('confessional_status', '')).strip().lower(),
        segment=segment,
        schedule_context_normalized=schedule_context_normalized,
        shift_offers=tuple(row for row in profile.get('shift_offers', []) if isinstance(row, dict)),
        tuition_reference=tuple(
            row for row in profile.get('tuition_reference', []) if isinstance(row, dict)
        ),
        semantic_act=semantic_plan.conversation_act if semantic_plan else None,
        contact_reference_message=contact_reference_message,
        preferred_contact_labels=preferred_contact_labels,
        requested_channel=(
            semantic_plan.requested_channel
            if semantic_plan and semantic_plan.requested_channel
            else _requested_contact_channel(contact_reference_message)
        ),
        requested_attribute_override=(
            semantic_plan.requested_attribute
            if semantic_plan and semantic_plan.requested_attribute
            else None
        ),
        slot_memory=slot_memory,
        conversation_context=effective_conversation_context,
        semantic_plan=semantic_plan,
    )
