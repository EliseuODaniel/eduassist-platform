from __future__ import annotations

"""Grounded answer experience pipeline extracted from grounded_answer_experience.py."""

import asyncio
from typing import Any

from . import grounded_answer_experience as _experience_runtime
from .conversation_answer_state import build_focus_summary, resolve_answer_focus
from .grounded_answer_experience import (
    _actor_summary,
    _answer_experience_changed,
    _answer_experience_pipeline_enabled,
    _answer_experience_settings,
    _attempt_second_retrieval,
    _build_evidence_lines,
    _build_supplemental_focus,
    _cached_focus_slot_memory,
    _clarify_after_retry_message,
    _context_repair_enabled,
    _conversation_external_id,
    _dedupe_preserve_order,
    _deterministic_context_repair_plan,
    _deterministic_protected_academic_direct_answer,
    _deterministic_protected_attendance_direct_answer,
    _deterministic_protected_finance_direct_answer,
    _deterministic_public_calendar_followup,
    _deterministic_public_capacity_followup,
    _deterministic_public_direct_answer,
    _eligible_reason,
    _extract_recent_user_messages,
    _fallback_retry_query,
    _filtered_recent_messages,
    _is_restricted_document_no_match_response,
    _localize_surface_labels_for_request,
    _looks_like_internal_document_query,
    _looks_like_student_resolution_failure,
    _merge_conversation_context_with_cached_focus,
    _normalize_context_repair_plan,
    _normalize_text,
    _preserve_deterministic_answer_surface,
    _question_mentions_unasked_attendance_scope,
    _recent_family_attendance_context,
    _response_has_terminal_semantic_ingress,
    _retry_visibility_for_response,
    _should_attempt_context_repair,
    _should_prefer_supplemental_focus,
    _store_focus_cache,
    _terminal_semantic_ingress_act,
    _validated_answer_experience_text,
)
from .models import (
    AccessTier,
    MessageResponse,
    MessageResponseRequest,
    OrchestrationMode,
    RetrievalBackend,
)


def _is_admin_finance_combined_query(message: str) -> bool:
    from .intent_analysis_runtime import _is_admin_finance_combined_query as _impl

    return _impl(message)

async def apply_grounded_answer_experience(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    settings: Any,
    stack_name: str,
    forced_reason: str | None = None,
) -> MessageResponse:
    reason = forced_reason or _eligible_reason(
        request=request,
        response=response,
        settings=settings,
        stack_name=stack_name,
    )
    if not _answer_experience_pipeline_enabled(
        request=request,
        response=response,
        settings=settings,
        stack_name=stack_name,
    ):
        return response
    base_reason = reason or 'contextual_answer_repair'

    if (
        _looks_like_internal_document_query(request.message)
        and response.classification.access_tier != AccessTier.public
        and response.retrieval_backend != RetrievalBackend.none
    ):
        return response.model_copy(
            update={
                'answer_experience_eligible': True,
                'answer_experience_applied': False,
            }
        )

    if _is_restricted_document_no_match_response(response):
        return response.model_copy(
            update={
                'answer_experience_eligible': True,
                'answer_experience_applied': False,
            }
        )

    conversation_external_id = _conversation_external_id(request)
    conversation_context, school_profile, actor = await asyncio.gather(
        _experience_runtime._fetch_conversation_context(settings=settings, request=request),
        _experience_runtime._fetch_public_school_profile(settings),
        _experience_runtime._fetch_actor_context(settings=settings, request=request),
    )
    from .public_orchestration_runtime import (
        _build_effective_actor_context as _build_effective_actor_context_local,
        _compose_scope_boundary_answer as _compose_scope_boundary_answer_local,
        _is_explicit_open_world_scope_boundary_query as _is_explicit_open_world_scope_boundary_query_local,
    )

    actor = _build_effective_actor_context_local(actor, request.user)
    conversation_context = _merge_conversation_context_with_cached_focus(
        conversation_context,
        cached_slot_memory=_cached_focus_slot_memory(conversation_external_id),
    )
    if _is_explicit_open_world_scope_boundary_query_local(request.message):
        return response.model_copy(
            update={
                'message_text': _compose_scope_boundary_answer_local(
                    school_profile or {},
                    conversation_context=conversation_context,
                ),
                'answer_experience_eligible': True,
                'answer_experience_applied': True,
                'answer_experience_reason': f'{base_reason}:explicit_open_world_scope_boundary',
            }
        )
    focus = resolve_answer_focus(
        request_message=request.message,
        actor=actor,
        conversation_context=conversation_context,
    )
    _store_focus_cache(
        conversation_external_id=conversation_external_id,
        focus=focus,
    )
    supplemental = await _experience_runtime._build_supplemental_focus(
        settings=settings,
        request=request,
        focus=focus,
        school_profile=school_profile,
        actor=actor,
        conversation_context=conversation_context,
    )
    provider_settings = _answer_experience_settings(settings)
    actor_summary = _actor_summary(actor)
    evidence_lines = _dedupe_preserve_order(
        [*(supplemental or {}).get('evidence_lines', []), *_build_evidence_lines(response)]
    )
    recent_messages = _filtered_recent_messages(conversation_context=conversation_context, focus=focus)
    recent_user_messages = _extract_recent_user_messages(conversation_context)
    supplemental_focused_draft = str((supplemental or {}).get('focused_draft') or '')
    effective_draft_text = supplemental_focused_draft or response.message_text

    preserve_reason = _preserve_deterministic_answer_surface(
        request=request,
        response=response,
        focus=focus,
        actor=actor,
        conversation_context=conversation_context,
    )
    if preserve_reason:
        preserved_message_text = response.message_text
        answer_experience_applied = False
        if preserve_reason == 'preserve_scope_boundary_surface':
            from .public_profile_runtime import _compose_scope_boundary_answer as _compose_scope_boundary_answer_local

            canonical_scope_boundary = _compose_scope_boundary_answer_local(
                school_profile or {},
                conversation_context=conversation_context,
            )
            answer_experience_applied = _answer_experience_changed(
                response.message_text,
                canonical_scope_boundary,
            )
            preserved_message_text = canonical_scope_boundary
        return response.model_copy(
            update={
                'message_text': preserved_message_text,
                'answer_experience_eligible': True,
                'answer_experience_applied': answer_experience_applied,
                'answer_experience_reason': f'{base_reason}:{preserve_reason}',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    deterministic_public_calendar = _deterministic_public_calendar_followup(
        request=request,
        response=response,
        conversation_context=conversation_context,
    )
    if deterministic_public_calendar:
        return response.model_copy(
            update={
                'message_text': deterministic_public_calendar,
                'answer_experience_eligible': True,
                'answer_experience_applied': _answer_experience_changed(response.message_text, deterministic_public_calendar),
                'answer_experience_reason': f'{base_reason}:public_temporal_followup',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    deterministic_public_capacity, deterministic_capacity_mode = _deterministic_public_capacity_followup(
        request=request,
        response=response,
        conversation_context=conversation_context,
    )
    if deterministic_public_capacity:
        return response.model_copy(
            update={
                'message_text': deterministic_public_capacity,
                'mode': deterministic_capacity_mode or response.mode,
                'answer_experience_eligible': True,
                'answer_experience_applied': _answer_experience_changed(response.message_text, deterministic_public_capacity),
                'answer_experience_reason': f'{base_reason}:public_capacity_followup',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    deterministic_public_direct = await _deterministic_public_direct_answer(
        request=request,
        response=response,
        school_profile=school_profile,
        settings=settings,
        conversation_context=conversation_context,
    )
    if deterministic_public_direct:
        return response.model_copy(
            update={
                'message_text': deterministic_public_direct,
                'mode': OrchestrationMode.structured_tool,
                'answer_experience_eligible': True,
                'answer_experience_applied': _answer_experience_changed(response.message_text, deterministic_public_direct),
                'answer_experience_reason': f'{base_reason}:public_direct_answer',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    prefer_attendance_before_academic = bool(
        focus.topic == 'attendance'
        or _question_mentions_unasked_attendance_scope(request.message)
        or any('attendance' in str(tool or '').lower() for tool in response.selected_tools)
        or _recent_family_attendance_context(conversation_context)
    )
    protected_direct_sequence = (
        (
            (
                'attendance',
                await _deterministic_protected_attendance_direct_answer(
                    request=request,
                    response=response,
                    focus=focus,
                    actor=actor,
                    settings=settings,
                    conversation_context=conversation_context,
                ),
            ),
            (
                'academic',
                await _deterministic_protected_academic_direct_answer(
                    request=request,
                    response=response,
                    focus=focus,
                    actor=actor,
                    settings=settings,
                    conversation_context=conversation_context,
                ),
            ),
        )
        if prefer_attendance_before_academic
        else (
            (
                'academic',
                await _deterministic_protected_academic_direct_answer(
                    request=request,
                    response=response,
                    focus=focus,
                    actor=actor,
                    settings=settings,
                    conversation_context=conversation_context,
                ),
            ),
            (
                'attendance',
                await _deterministic_protected_attendance_direct_answer(
                    request=request,
                    response=response,
                    focus=focus,
                    actor=actor,
                    settings=settings,
                    conversation_context=conversation_context,
                ),
            ),
        )
    )
    for protected_kind, protected_text in protected_direct_sequence:
        if not protected_text:
            continue
        return response.model_copy(
            update={
                'message_text': protected_text,
                'mode': OrchestrationMode.structured_tool,
                'answer_experience_eligible': True,
                'answer_experience_applied': _answer_experience_changed(response.message_text, protected_text),
                'answer_experience_reason': f'{base_reason}:protected_{protected_kind}_direct',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    prefer_supplemental_focus = _should_prefer_supplemental_focus(
        request_message=request.message,
        original_text=response.message_text,
        focus=focus,
        supplemental_focused_draft=supplemental_focused_draft,
    )
    prefer_supplemental_before_finance_direct = (
        focus.topic == 'admin_finance_combo'
        or _is_admin_finance_combined_query(request.message)
        or (
            prefer_supplemental_focus
            and _looks_like_student_resolution_failure(response.message_text)
        )
    )

    deterministic_protected_finance = None
    if not prefer_supplemental_before_finance_direct:
        deterministic_protected_finance = await _deterministic_protected_finance_direct_answer(
            request=request,
            response=response,
            actor=actor,
            settings=settings,
            conversation_context=conversation_context,
        )
    if deterministic_protected_finance:
        return response.model_copy(
            update={
                'message_text': deterministic_protected_finance,
                'mode': OrchestrationMode.structured_tool,
                'answer_experience_eligible': True,
                'answer_experience_applied': _answer_experience_changed(response.message_text, deterministic_protected_finance),
                'answer_experience_reason': f'{base_reason}:protected_finance_direct',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    if prefer_supplemental_focus:
        validated_direct = _validated_answer_experience_text(
            request_message=request.message,
            original_text=response.message_text,
            candidate_text=supplemental_focused_draft,
            focus=focus,
        )
        if validated_direct:
            resolved_mode = (
                OrchestrationMode.structured_tool
                if response.mode == OrchestrationMode.clarify
                else response.mode
            )
            return response.model_copy(
                update={
                    'message_text': validated_direct,
                    'mode': resolved_mode,
                    'used_llm': bool(response.used_llm),
                    'answer_experience_eligible': True,
                    'answer_experience_applied': _answer_experience_changed(response.message_text, validated_direct),
                    'answer_experience_reason': f'{base_reason}:supplemental_focus_direct',
                    'answer_experience_provider': provider_settings.llm_provider,
                    'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
                }
            )

    terminal_ingress_act = _terminal_semantic_ingress_act(response)
    if terminal_ingress_act == 'language_preference':
        preserved_text = _localize_surface_labels_for_request(
            request_message=request.message,
            text=response.message_text,
        )
        return response.model_copy(
            update={
                'message_text': preserved_text,
                'answer_experience_eligible': True,
                'answer_experience_applied': _answer_experience_changed(response.message_text, preserved_text),
                'answer_experience_reason': f'{base_reason}:terminal_language_preference_preserved',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    if (
        not _response_has_terminal_semantic_ingress(response)
        and _context_repair_enabled(settings=settings, stack_name=stack_name)
        and _should_attempt_context_repair(
            request=request,
            response=response,
            focus=focus,
            actor=actor,
        )
    ):
        deterministic_plan = _deterministic_context_repair_plan(
            request=request,
            focus=focus,
            actor=actor,
            conversation_context=conversation_context,
        )
        repair_plan = _normalize_context_repair_plan(
            await _experience_runtime.plan_context_repair_with_provider(
                settings=provider_settings,
                request_message=request.message,
                draft_text=effective_draft_text,
                mode=response.mode.value,
                domain=response.classification.domain.value,
                access_tier=response.classification.access_tier.value,
                selected_tools=list(response.selected_tools),
                evidence_lines=evidence_lines,
                recent_messages=recent_messages,
                school_profile=school_profile,
                reason=response.reason,
                focus_summary=build_focus_summary(focus),
                actor_summary=actor_summary,
            )
        )
        if deterministic_plan is not None:
            if focus.unknown_student_name or focus.unknown_subject_name or focus.is_repair_followup or focus.needs_disambiguation:
                repair_plan = deterministic_plan
            elif repair_plan is None:
                repair_plan = deterministic_plan
            else:
                current_action = str(repair_plan.get('action') or 'keep')
                current_confidence = float(repair_plan.get('confidence') or 0.0)
                if current_action in {'keep', 'unavailable'} or current_confidence < 0.8:
                    repair_plan = deterministic_plan
        if repair_plan is None and response.mode == OrchestrationMode.clarify:
            retry_query = _fallback_retry_query(
                request=request,
                focus=focus,
                recent_user_messages=recent_user_messages,
            )
            repair_plan = {
                'action': 'retry_retrieval' if _retry_visibility_for_response(response) else 'clarify',
                'message': 'Você pode me dizer exatamente qual aluno, disciplina ou período devo considerar?',
                'retry_query': retry_query,
                'confidence': 0.45,
                'reason': 'fallback_context_repair',
            }
        elif repair_plan is None:
            repair_plan = {'action': 'keep', 'message': '', 'retry_query': '', 'confidence': 0.0, 'reason': 'planner_unavailable'}

        action = str(repair_plan.get('action') or 'keep')
        planner_message = _normalize_text(repair_plan.get('message'))
        retry_query = _normalize_text(repair_plan.get('retry_query')) or _fallback_retry_query(
            request=request,
            focus=focus,
            recent_user_messages=recent_user_messages,
        )
        confidence = float(repair_plan.get('confidence') or 0.0)
        planner_reason = _normalize_text(repair_plan.get('reason')) or action
        should_retry_before_unavailable = (
            action in {'retry_retrieval', 'unavailable'}
            and _retry_visibility_for_response(response) is not None
            and (action != 'unavailable' or confidence < 0.9)
        )
        if should_retry_before_unavailable:
            retry_response = await _experience_runtime._attempt_second_retrieval(
                settings=settings,
                request=request,
                response=response,
                retry_query=retry_query,
                focus=focus,
                recent_messages=recent_messages,
                school_profile=school_profile,
                provider_settings=provider_settings,
                actor_summary=actor_summary,
            )
            if retry_response is not None:
                return retry_response
            clarify_after_retry = _clarify_after_retry_message(
                request=request,
                focus=focus,
                actor=actor,
                conversation_context=conversation_context,
            )
            if clarify_after_retry:
                llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
                if 'context_repair_planner' not in llm_stages:
                    llm_stages.append('context_repair_planner')
                return response.model_copy(
                    update={
                        'message_text': clarify_after_retry,
                        'mode': OrchestrationMode.clarify,
                        'used_llm': True,
                        'llm_stages': llm_stages,
                        'answer_experience_eligible': True,
                        'answer_experience_applied': True,
                        'answer_experience_reason': f'{base_reason}:context_repair_clarify_after_retry',
                        'answer_experience_provider': provider_settings.llm_provider,
                        'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
                        'context_repair_applied': True,
                        'context_repair_action': 'clarify',
                        'context_repair_reason': 'retry_failed_clarify',
                    }
                )
        if action == 'clarify' and planner_message:
            llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
            if 'context_repair_planner' not in llm_stages:
                llm_stages.append('context_repair_planner')
            return response.model_copy(
                update={
                    'message_text': planner_message,
                    'mode': OrchestrationMode.clarify,
                    'used_llm': True,
                    'llm_stages': llm_stages,
                    'answer_experience_eligible': True,
                    'answer_experience_applied': True,
                    'answer_experience_reason': f'{base_reason}:context_repair_clarify',
                    'answer_experience_provider': provider_settings.llm_provider,
                    'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
                    'context_repair_applied': True,
                    'context_repair_action': 'clarify',
                    'context_repair_reason': planner_reason,
                }
            )
        if action == 'unavailable' and planner_message and confidence >= 0.9:
            llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
            if 'context_repair_planner' not in llm_stages:
                llm_stages.append('context_repair_planner')
            return response.model_copy(
                update={
                    'message_text': planner_message,
                    'used_llm': True,
                    'llm_stages': llm_stages,
                    'answer_experience_eligible': True,
                    'answer_experience_applied': True,
                    'answer_experience_reason': f'{base_reason}:context_repair_unavailable',
                    'answer_experience_provider': provider_settings.llm_provider,
                    'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
                    'context_repair_applied': True,
                    'context_repair_action': 'unavailable',
                    'context_repair_reason': planner_reason,
                }
            )
    if not reason:
        return response
    candidate_text = await _experience_runtime.compose_grounded_answer_experience_with_provider(
        settings=provider_settings,
        request_message=request.message,
        draft_text=effective_draft_text,
        mode=response.mode.value,
        domain=response.classification.domain.value,
        access_tier=response.classification.access_tier.value,
        selected_tools=list(response.selected_tools),
        evidence_lines=evidence_lines,
        recent_messages=recent_messages,
        school_profile=school_profile,
        reason=response.reason,
        focus_summary=build_focus_summary(focus),
    )
    validated_text = _validated_answer_experience_text(
        request_message=request.message,
        original_text=effective_draft_text,
        candidate_text=candidate_text or '',
        focus=focus,
    )
    if not validated_text:
        supplemental_fallback = _validated_answer_experience_text(
            request_message=request.message,
            original_text=response.message_text,
            candidate_text=supplemental_focused_draft,
            focus=focus,
        )
        if supplemental_fallback:
            llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
            used_llm = bool(candidate_text) or bool(response.used_llm)
            if used_llm and 'grounded_answer_experience' not in llm_stages:
                llm_stages.append('grounded_answer_experience')
            return response.model_copy(
            update={
                'message_text': supplemental_fallback,
                'used_llm': used_llm,
                    'llm_stages': llm_stages,
                    'answer_experience_eligible': True,
                'answer_experience_applied': _answer_experience_changed(response.message_text, supplemental_fallback),
                'answer_experience_reason': f'{base_reason}:supplemental_focus_fallback',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
                'context_repair_applied': bool(getattr(response, 'context_repair_applied', False)),
                'context_repair_action': getattr(response, 'context_repair_action', None),
                'context_repair_reason': getattr(response, 'context_repair_reason', None),
                'retrieval_retry_applied': bool(getattr(response, 'retrieval_retry_applied', False)),
                'retrieval_retry_reason': getattr(response, 'retrieval_retry_reason', None),
            }
        )
        return response.model_copy(
            update={
                'answer_experience_eligible': True,
                'answer_experience_applied': False,
                'answer_experience_reason': f'{base_reason}:fallback_to_original',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
    if 'grounded_answer_experience' not in llm_stages:
        llm_stages.append('grounded_answer_experience')
    return response.model_copy(
        update={
            'message_text': validated_text,
            'used_llm': True,
            'llm_stages': llm_stages,
            'answer_experience_eligible': True,
            'answer_experience_applied': _answer_experience_changed(response.message_text, validated_text),
            'answer_experience_reason': base_reason,
            'answer_experience_provider': provider_settings.llm_provider,
            'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            'context_repair_applied': bool(getattr(response, 'context_repair_applied', False)),
            'context_repair_action': getattr(response, 'context_repair_action', None),
            'context_repair_reason': getattr(response, 'context_repair_reason', None),
            'retrieval_retry_applied': bool(getattr(response, 'retrieval_retry_applied', False)),
            'retrieval_retry_reason': getattr(response, 'retrieval_retry_reason', None),
        }
    )
