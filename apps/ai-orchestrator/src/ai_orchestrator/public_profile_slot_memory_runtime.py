from __future__ import annotations

"""Conversation slot memory extracted from public_profile_runtime.py."""

from .conversation_focus_runtime import _recent_conversation_focus
from .intent_analysis_runtime import (
    _derive_active_entity,
    _derive_active_task,
    _derive_pending_question_type,
    _detect_academic_focus_kind,
    _detect_admin_attribute_request,
    _detect_public_pricing_price_kind,
    _detect_time_reference,
    _effective_academic_attribute_request,
    _effective_finance_attribute_request,
    _effective_finance_status_filter,
    _extract_grade_reference,
    _extract_public_pricing_grade_year,
    _message_matches_term,
    _normalize_text,
    _primary_public_entity_hint,
    _recent_slot_value,
    _requested_operating_hours_attribute,
    _should_reuse_public_context,
    _should_reuse_public_pricing_slots,
    _should_track_contact_subject,
    _should_track_feature_key,
    _wants_finance_second_copy,
)
from .public_profile_runtime import (
    _recent_public_contact_subject,
    _recent_public_feature_key,
    _select_public_segment,
)
from .student_scope_runtime import (
    _derive_pending_disambiguation,
    _is_children_overview_query,
    _is_student_focus_activation_query,
    _recent_student_from_context,
    _student_focus_candidate,
)
from .models import ConversationSlotMemory, PublicInstitutionPlan, QueryDomain
from .runtime_core import resolve_entity_hints
from .runtime_core_constants import SUPPORT_FINANCE_TERMS
from typing import Any

def _build_conversation_slot_memory_impl(
    *,
    actor: dict[str, Any] | None,
    profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    request_message: str | None = None,
    public_plan: PublicInstitutionPlan | None = None,
    preview: Any | None = None,
) -> ConversationSlotMemory:
    focus = _recent_conversation_focus(conversation_context) or {}
    protocol_code = str(focus.get('protocol_code', '') or '').strip() or None
    focus_kind = str(focus.get('kind', '') or '').strip() or None
    safe_profile = profile if isinstance(profile, dict) else {}
    current_message = request_message or ''
    allow_public_context = _should_reuse_public_context(
        message=current_message,
        public_plan=public_plan,
    )
    public_entity = (
        public_plan.focus_hint if public_plan and public_plan.focus_hint else None
    ) or _primary_public_entity_hint(
        current_message,
        conversation_context if allow_public_context else None,
    )
    pricing_context_active = (
        public_plan is not None and public_plan.conversation_act == 'pricing'
    ) or str(focus.get('active_task', '') or '').strip() == 'public:pricing'
    reuse_public_pricing_slots = pricing_context_active and _should_reuse_public_pricing_slots(
        current_message
    )
    public_attribute = (
        public_plan.requested_attribute if public_plan and public_plan.requested_attribute else None
    ) or (
        _recent_slot_value(conversation_context, 'public_attribute')
        if allow_public_context
        else None
    )
    public_pricing_segment = _select_public_segment(current_message)
    if (
        public_pricing_segment is None
        and (allow_public_context or reuse_public_pricing_slots)
        and (pricing_context_active or reuse_public_pricing_slots)
    ):
        public_pricing_segment = _recent_slot_value(conversation_context, 'public_pricing_segment')
    public_pricing_grade_year = _extract_public_pricing_grade_year(current_message)
    if (
        public_pricing_grade_year is None
        and (allow_public_context or reuse_public_pricing_slots)
        and reuse_public_pricing_slots
    ):
        public_pricing_grade_year = _recent_slot_value(
            conversation_context, 'public_pricing_grade_year'
        )
    quantity_hint = resolve_entity_hints(current_message).quantity_hint
    public_pricing_quantity = (
        str(quantity_hint) if quantity_hint is not None and quantity_hint > 0 else None
    )
    if (
        public_pricing_quantity is None
        and (allow_public_context or reuse_public_pricing_slots)
        and reuse_public_pricing_slots
    ):
        public_pricing_quantity = _recent_slot_value(
            conversation_context, 'public_pricing_quantity'
        )
    public_pricing_price_kind = _detect_public_pricing_price_kind(current_message)
    if (
        public_pricing_price_kind is None
        and (allow_public_context or reuse_public_pricing_slots)
        and reuse_public_pricing_slots
    ):
        public_pricing_price_kind = _recent_slot_value(
            conversation_context, 'public_pricing_price_kind'
        )
    requested_channel = (
        public_plan.requested_channel if public_plan and public_plan.requested_channel else None
    ) or (
        _recent_slot_value(conversation_context, 'requested_channel')
        if allow_public_context
        else None
    )
    time_reference = _detect_time_reference(current_message) or (
        _recent_slot_value(conversation_context, 'time_reference') if allow_public_context else None
    )
    academic_student = _recent_student_from_context(
        actor,
        capability='academic',
        conversation_context=conversation_context,
    )
    finance_student = _recent_student_from_context(
        actor,
        capability='finance',
        conversation_context=conversation_context,
    )
    mentioned_student = _student_focus_candidate(actor, current_message)
    if isinstance(mentioned_student, dict) and bool(
        mentioned_student.get('can_view_academic', False)
    ):
        academic_student = mentioned_student
    if isinstance(mentioned_student, dict) and bool(
        mentioned_student.get('can_view_finance', False)
    ):
        finance_student = mentioned_student
    preview_domain = getattr(getattr(preview, 'classification', None), 'domain', None)
    if (
        preview_domain not in {QueryDomain.academic, QueryDomain.finance}
        and mentioned_student is None
        and not _is_student_focus_activation_query(current_message, actor)
        and not _is_children_overview_query(current_message, actor)
    ):
        academic_student = None
        finance_student = None
    academic_focus_kind = None
    academic_attribute = None
    admin_attribute = None
    finance_status_filter = None
    finance_attribute = None
    finance_action = None
    if public_plan is not None and public_plan.conversation_act == 'operating_hours':
        public_attribute = (
            _requested_operating_hours_attribute(
                current_message,
                conversation_context=conversation_context,
            )
            or public_attribute
        )
    if preview is not None and getattr(preview, 'classification', None) is not None:
        domain = getattr(preview.classification, 'domain', None)
        if domain is QueryDomain.support and not focus_kind:
            selected_tool_names = {
                str(tool_name).strip()
                for tool_name in getattr(preview, 'selected_tools', [])
                if isinstance(tool_name, str)
            }
            if {'schedule_school_visit', 'update_visit_booking'} & selected_tool_names:
                focus_kind = 'visit'
            elif {
                'create_institutional_request',
                'update_institutional_request',
            } & selected_tool_names:
                focus_kind = 'request'
            elif 'create_support_ticket' in selected_tool_names and any(
                _message_matches_term(_normalize_text(current_message), term)
                for term in SUPPORT_FINANCE_TERMS
            ):
                focus_kind = 'finance'
            elif {'create_support_ticket', 'handoff_to_human'} & selected_tool_names:
                focus_kind = 'support'
        if domain is QueryDomain.academic:
            academic_focus_kind = _detect_academic_focus_kind(
                current_message
            ) or _recent_slot_value(
                conversation_context,
                'academic_focus_kind',
            )
            academic_attribute_request = _effective_academic_attribute_request(
                current_message,
                conversation_context=conversation_context,
            )
            academic_attribute = (
                academic_attribute_request.attribute
                if academic_attribute_request is not None
                else None
            ) or _recent_slot_value(conversation_context, 'academic_attribute')
        elif domain is QueryDomain.finance:
            effective_status = _effective_finance_status_filter(
                current_message,
                conversation_context=conversation_context,
            )
            finance_status_filter = (
                ','.join(sorted(effective_status))
                if effective_status
                else _recent_slot_value(
                    conversation_context,
                    'finance_status_filter',
                )
            )
            finance_attribute_request = _effective_finance_attribute_request(
                current_message,
                conversation_context=conversation_context,
            )
            finance_attribute = (
                finance_attribute_request.attribute
                if finance_attribute_request is not None
                else None
            ) or _recent_slot_value(conversation_context, 'finance_attribute')
            if _wants_finance_second_copy(
                current_message, conversation_context=conversation_context
            ):
                finance_action = 'second_copy'
            else:
                finance_action = _recent_slot_value(conversation_context, 'finance_action')
        elif domain is QueryDomain.institution:
            selected_tool_names = {
                str(tool_name).strip()
                for tool_name in getattr(preview, 'selected_tools', [])
                if isinstance(tool_name, str)
            }
            if {
                'get_administrative_status',
                'get_student_administrative_status',
            } & selected_tool_names:
                admin_attribute = _detect_admin_attribute_request(
                    current_message,
                    conversation_context=conversation_context,
                ) or _recent_slot_value(conversation_context, 'admin_attribute')
    if public_plan is not None:
        focus_kind = 'public'
    contact_subject = (
        _recent_public_contact_subject(safe_profile, conversation_context)
        if _should_track_contact_subject(
            message=current_message,
            public_plan=public_plan,
            recent_focus=focus,
        )
        else None
    )
    feature_key = (
        _recent_public_feature_key(conversation_context)
        if _should_track_feature_key(
            message=current_message,
            public_plan=public_plan,
            recent_focus=focus,
        )
        else None
    )
    academic_student_name = (
        str(academic_student.get('full_name', '')).strip()
        if isinstance(academic_student, dict)
        else None
    ) or None
    finance_student_name = (
        str(finance_student.get('full_name', '')).strip()
        if isinstance(finance_student, dict)
        else None
    ) or None
    active_task = _derive_active_task(
        current_message=current_message,
        public_plan=public_plan,
        focus_kind=focus_kind,
        academic_focus_kind=academic_focus_kind,
        academic_student_name=academic_student_name,
        finance_student_name=finance_student_name,
        finance_attribute=finance_attribute,
        finance_action=finance_action,
        preview=preview,
    )
    active_entity = _derive_active_entity(
        active_task=active_task,
        focus_kind=focus_kind,
        public_plan=public_plan,
        public_entity=public_entity,
        contact_subject=contact_subject,
        feature_key=feature_key,
        current_message=current_message,
        time_reference=time_reference,
        academic_student_name=academic_student_name,
        finance_student_name=finance_student_name,
    )
    pending_question_type = _derive_pending_question_type(
        message=current_message,
        public_plan=public_plan,
        public_attribute=public_attribute,
        requested_channel=requested_channel,
        academic_attribute=academic_attribute,
        admin_attribute=admin_attribute,
        finance_attribute=finance_attribute,
        finance_action=finance_action,
        time_reference=time_reference,
        focus_kind=focus_kind,
    )
    pending_disambiguation = _derive_pending_disambiguation(
        actor=actor,
        message=current_message,
        preview=preview,
        conversation_context=conversation_context,
    )
    return ConversationSlotMemory(
        focus_kind=focus_kind,
        protocol_code=protocol_code,
        contact_subject=contact_subject,
        feature_key=feature_key,
        active_task=active_task,
        active_entity=active_entity,
        pending_question_type=pending_question_type,
        pending_disambiguation=pending_disambiguation,
        public_entity=public_entity,
        public_attribute=public_attribute,
        public_pricing_segment=public_pricing_segment,
        public_pricing_grade_year=public_pricing_grade_year,
        public_pricing_quantity=public_pricing_quantity,
        public_pricing_price_kind=public_pricing_price_kind,
        requested_channel=requested_channel,
        time_reference=time_reference,
        academic_student_name=academic_student_name,
        academic_focus_kind=academic_focus_kind,
        academic_attribute=academic_attribute,
        admin_attribute=admin_attribute,
        finance_student_name=finance_student_name,
        finance_status_filter=finance_status_filter,
        finance_attribute=finance_attribute,
        finance_action=finance_action,
    )

_build_conversation_slot_memory = _build_conversation_slot_memory_impl
