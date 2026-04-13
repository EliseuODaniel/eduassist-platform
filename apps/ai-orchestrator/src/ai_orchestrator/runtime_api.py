from __future__ import annotations

# ruff: noqa: F401,F403,F405

"""Runtime API and persistence helpers extracted from runtime.py.

This module is imported lazily from runtime.py after the shared helper surface is
already defined. It intentionally reuses the legacy runtime namespace during the
ongoing decomposition, so extracted functions keep behavior while the monolith
is split into focused modules.
"""

from . import runtime_core as _runtime_core
from .engine_trace import build_engine_trace_sections


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


async def _api_core_get(
    *,
    settings: Any,
    path: str,
    params: dict[str, object] | None = None,
) -> tuple[dict[str, Any] | None, int | None]:
    headers = {'X-Internal-Api-Token': settings.internal_api_token}
    with start_span(
        'eduassist.api_core.get',
        tracer_name='eduassist.ai_orchestrator.runtime',
        **{
            'eduassist.api_core.path': path,
            'eduassist.api_core.has_params': bool(params),
        },
    ):
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get(
                    f'{settings.api_core_url}{path}', params=params, headers=headers
                )
            response.raise_for_status()
            payload = response.json()
            set_span_attributes(**{'http.status_code': response.status_code})
            if isinstance(payload, dict):
                return payload, response.status_code
            return None, response.status_code
        except httpx.HTTPStatusError as exc:
            set_span_attributes(**{'http.status_code': exc.response.status_code})
            return None, exc.response.status_code
        except Exception:
            return None, None


async def _api_core_post(
    *,
    settings: Any,
    path: str,
    payload: dict[str, object],
) -> tuple[dict[str, Any] | None, int | None]:
    headers = {
        'X-Internal-Api-Token': settings.internal_api_token,
        'Content-Type': 'application/json',
    }
    with start_span(
        'eduassist.api_core.post',
        tracer_name='eduassist.ai_orchestrator.runtime',
        **{
            'eduassist.api_core.path': path,
            'eduassist.api_core.has_payload': bool(payload),
        },
    ):
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.post(
                    f'{settings.api_core_url}{path}', json=payload, headers=headers
                )
            response.raise_for_status()
            body = response.json()
            set_span_attributes(**{'http.status_code': response.status_code})
            if isinstance(body, dict):
                return body, response.status_code
            return None, response.status_code
        except httpx.HTTPStatusError as exc:
            set_span_attributes(**{'http.status_code': exc.response.status_code})
            return None, exc.response.status_code
        except Exception:
            return None, None


async def _fetch_public_school_profile(settings: Any) -> dict[str, Any] | None:
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/school-profile',
    )
    if status_code != 200 or not isinstance(payload, dict):
        return None
    profile = payload.get('profile')
    return profile if isinstance(profile, dict) else None


async def _fetch_conversation_context(
    *,
    settings: Any,
    conversation_external_id: str | None,
    channel: str,
) -> ConversationContextBundle | None:
    if not conversation_external_id:
        return None

    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/internal/conversations/context',
        params={
            'conversation_external_id': conversation_external_id,
            'channel': channel,
            'limit': 6,
        },
    )
    if status_code != 200 or not isinstance(payload, dict):
        return None

    recent_messages = payload.get('recent_messages')
    if not isinstance(recent_messages, list):
        recent_messages = []

    return ConversationContextBundle(
        conversation_external_id=conversation_external_id,
        recent_messages=[item for item in recent_messages if isinstance(item, dict)],
        recent_tool_calls=[
            item for item in payload.get('recent_tool_calls', []) if isinstance(item, dict)
        ],
        message_count=int(payload.get('message_count', 0) or 0),
    )


async def _persist_conversation_turn(
    *,
    settings: Any,
    conversation_external_id: str | None,
    channel: str,
    actor: dict[str, Any] | None,
    user_message: str,
    assistant_message: str,
) -> None:
    if not conversation_external_id:
        return

    actor_user_id = actor.get('user_id') if isinstance(actor, dict) else None
    payload = {
        'channel': channel,
        'conversation_external_id': conversation_external_id,
        'actor_user_id': actor_user_id,
        'messages': [
            {'sender_type': 'user', 'content': user_message},
            {'sender_type': 'assistant', 'content': assistant_message},
        ],
    }
    await _api_core_post(
        settings=settings,
        path='/v1/internal/conversations/messages',
        payload=payload,
    )


def _serialize_slot_memory(slot_memory: ConversationSlotMemory) -> dict[str, Any]:
    return {
        key: value
        for key, value in {
            'focus_kind': slot_memory.focus_kind,
            'protocol_code': slot_memory.protocol_code,
            'contact_subject': slot_memory.contact_subject,
            'feature_key': slot_memory.feature_key,
            'active_task': slot_memory.active_task,
            'active_entity': slot_memory.active_entity,
            'pending_question_type': slot_memory.pending_question_type,
            'pending_disambiguation': slot_memory.pending_disambiguation,
            'public_entity': slot_memory.public_entity,
            'public_attribute': slot_memory.public_attribute,
            'public_pricing_segment': slot_memory.public_pricing_segment,
            'public_pricing_grade_year': slot_memory.public_pricing_grade_year,
            'public_pricing_quantity': slot_memory.public_pricing_quantity,
            'public_pricing_price_kind': slot_memory.public_pricing_price_kind,
            'requested_channel': slot_memory.requested_channel,
            'time_reference': slot_memory.time_reference,
            'academic_student_name': slot_memory.academic_student_name,
            'academic_focus_kind': slot_memory.academic_focus_kind,
            'academic_attribute': slot_memory.academic_attribute,
            'admin_attribute': slot_memory.admin_attribute,
            'finance_student_name': slot_memory.finance_student_name,
            'finance_status_filter': slot_memory.finance_status_filter,
            'finance_attribute': slot_memory.finance_attribute,
            'finance_action': slot_memory.finance_action,
        }.items()
        if value
    }


async def _persist_operational_trace(
    *,
    settings: Any,
    conversation_external_id: str | None,
    channel: str,
    engine_name: str,
    engine_mode: str,
    actor: dict[str, Any] | None,
    preview: Any,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    public_plan: PublicInstitutionPlan | None,
    request_message: str,
    message_text: str,
    citations_count: int,
    suggested_reply_count: int,
    visual_asset_count: int,
    answer_verifier_valid: bool,
    answer_verifier_reason: str | None,
    answer_verifier_fallback_used: bool,
    deterministic_fallback_available: bool,
    answer_verifier_judge_used: bool,
    langgraph_trace_metadata: dict[str, Any] | None = None,
    engine_trace_metadata: dict[str, Any] | None = None,
) -> None:
    if not conversation_external_id:
        return

    actor_user_id = actor.get('user_id') if isinstance(actor, dict) else None
    slot_memory = _build_conversation_slot_memory(
        actor=actor,
        profile=school_profile,
        conversation_context=conversation_context,
        request_message=request_message,
        public_plan=public_plan,
        preview=preview,
    )
    trace_request_payload: dict[str, Any] = {
        'engine_name': engine_name,
        'engine_mode': engine_mode,
        'mode': preview.mode.value,
        'domain': preview.classification.domain.value,
        'access_tier': preview.classification.access_tier.value,
        'selected_tools': list(preview.selected_tools),
        'graph_path': list(preview.graph_path),
        'reason': preview.reason,
        'slot_memory': _serialize_slot_memory(slot_memory),
    }
    if public_plan is not None:
        trace_request_payload['public_plan'] = {
            'conversation_act': public_plan.conversation_act,
            'secondary_acts': list(public_plan.secondary_acts),
            'semantic_source': public_plan.semantic_source,
            'use_conversation_context': public_plan.use_conversation_context,
            'fetch_profile': public_plan.fetch_profile,
            'focus_hint': public_plan.focus_hint,
            'requested_attribute': public_plan.requested_attribute,
            'requested_channel': public_plan.requested_channel,
            'required_tools': list(public_plan.required_tools),
        }
    if isinstance(langgraph_trace_metadata, dict) and langgraph_trace_metadata:
        langgraph_trace_sections = build_langgraph_trace_sections(
            langgraph_trace_metadata,
            graph_path=list(getattr(preview, 'graph_path', []) or []),
        )
        if langgraph_trace_sections.get('request'):
            trace_request_payload['langgraph'] = langgraph_trace_sections['request']
    if engine_name != 'specialist_supervisor' and isinstance(engine_trace_metadata, dict) and engine_trace_metadata:
        engine_trace_sections = build_engine_trace_sections(
            engine_trace_metadata,
            graph_path=list(getattr(preview, 'graph_path', []) or []),
        )
        if engine_trace_sections.get('request'):
            trace_request_payload[engine_name] = engine_trace_sections['request']
    trace_response_payload = {
        'mode': preview.mode.value,
        'domain': preview.classification.domain.value,
        'access_tier': preview.classification.access_tier.value,
        'retrieval_backend': preview.retrieval_backend.value,
        'graph_path': list(getattr(preview, 'graph_path', []) or []),
        'selected_tools': list(getattr(preview, 'selected_tools', []) or []),
        'risk_flags': canonicalize_risk_flags(getattr(preview, 'risk_flags', [])),
        'evidence_strategy': canonicalize_evidence_strategy(
            preview.mode.value,
            retrieval_backend=preview.retrieval_backend.value,
        ),
        'evidence_source_count': citations_count,
        'evidence_support_count': citations_count
        or len(getattr(preview, 'selected_tools', []) or []),
        'message_length': len(message_text),
        'citations_count': citations_count,
        'suggested_reply_count': suggested_reply_count,
        'visual_asset_count': visual_asset_count,
        'answer_verifier_valid': answer_verifier_valid,
        'answer_verifier_reason': answer_verifier_reason or '',
        'answer_verifier_fallback_used': answer_verifier_fallback_used,
        'deterministic_fallback_available': deterministic_fallback_available,
        'answer_verifier_judge_used': answer_verifier_judge_used,
    }
    if isinstance(langgraph_trace_metadata, dict) and langgraph_trace_metadata:
        langgraph_trace_sections = build_langgraph_trace_sections(
            langgraph_trace_metadata,
            graph_path=list(getattr(preview, 'graph_path', []) or []),
        )
        if langgraph_trace_sections.get('response'):
            trace_response_payload['langgraph'] = langgraph_trace_sections['response']
    if engine_name != 'specialist_supervisor' and isinstance(engine_trace_metadata, dict) and engine_trace_metadata:
        engine_trace_sections = build_engine_trace_sections(
            engine_trace_metadata,
            graph_path=list(getattr(preview, 'graph_path', []) or []),
        )
        if engine_trace_sections.get('response'):
            trace_response_payload[engine_name] = engine_trace_sections['response']
    if engine_name == 'specialist_supervisor':
        specialist_trace_sections = build_specialist_trace_sections(
            engine_trace_metadata,
            graph_path=list(getattr(preview, 'graph_path', []) or []),
        )
        if specialist_trace_sections.get('request'):
            trace_request_payload['specialist_supervisor'] = specialist_trace_sections['request']
        if specialist_trace_sections.get('response'):
            trace_response_payload['specialist_supervisor'] = specialist_trace_sections['response']
    await _api_core_post(
        settings=settings,
        path='/v1/internal/conversations/tool-calls',
        payload={
            'channel': channel,
            'conversation_external_id': conversation_external_id,
            'actor_user_id': actor_user_id,
            'tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'status': 'ok',
                    'request_payload': trace_request_payload,
                    'response_payload': trace_response_payload,
                }
            ],
        },
    )


def _extract_langgraph_snapshot_metadata(snapshot: Any) -> dict[str, Any]:
    values = dict(getattr(snapshot, 'values', {}) or {})
    config = getattr(snapshot, 'config', None)
    parent_config = getattr(snapshot, 'parent_config', None)
    metadata = getattr(snapshot, 'metadata', None)
    configurable = config.get('configurable', {}) if isinstance(config, dict) else {}
    parent_configurable = (
        parent_config.get('configurable', {}) if isinstance(parent_config, dict) else {}
    )
    next_nodes = [str(item) for item in (getattr(snapshot, 'next', None) or ())]
    task_names = [
        str(getattr(task, 'name', ''))
        for task in (getattr(snapshot, 'tasks', None) or ())
        if str(getattr(task, 'name', '')).strip()
    ]
    top_level_interrupts = list(getattr(snapshot, 'interrupts', None) or ())
    task_interrupt_count = sum(
        len(getattr(task, 'interrupts', None) or ())
        for task in (getattr(snapshot, 'tasks', None) or ())
    )
    payload: dict[str, Any] = {
        'state_available': True,
        'created_at': str(getattr(snapshot, 'created_at', '') or ''),
        'next_nodes': next_nodes,
        'task_names': task_names,
        'top_level_interrupt_count': len(top_level_interrupts),
        'task_interrupt_count': task_interrupt_count,
        'has_pending_interrupt': bool(top_level_interrupts or task_interrupt_count),
        'state_route': values.get('route'),
        'state_slice_name': values.get('slice_name'),
        'hitl_status': values.get('hitl_status'),
    }
    checkpoint_id = configurable.get('checkpoint_id') or parent_configurable.get('checkpoint_id')
    checkpoint_ns = configurable.get('checkpoint_ns') or parent_configurable.get('checkpoint_ns')
    if checkpoint_id:
        payload['checkpoint_id'] = str(checkpoint_id)
    if checkpoint_ns:
        payload['checkpoint_ns'] = str(checkpoint_ns)
    if isinstance(metadata, dict) and metadata:
        payload['snapshot_metadata'] = {
            str(key): value
            for key, value in metadata.items()
            if isinstance(value, (str, int, float, bool)) or value is None
        }
    return payload


def _capture_langgraph_trace_metadata(
    *,
    graph: Any,
    thread_id: str | None,
    langgraph_artifacts: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        'thread_id': thread_id or '',
        'checkpointer_enabled': bool(getattr(langgraph_artifacts, 'checkpointer_enabled', False)),
        'checkpointer_backend': str(getattr(langgraph_artifacts, 'checkpointer_backend', '') or ''),
        'state_available': False,
    }
    if not thread_id or not getattr(langgraph_artifacts, 'checkpointer_enabled', False):
        return payload
    try:
        snapshot = get_orchestration_state_snapshot(
            graph=graph, thread_id=thread_id, subgraphs=True
        )
    except Exception as exc:
        payload['state_fetch_error'] = exc.__class__.__name__
        payload['state_fetch_error_message'] = str(exc)
        return payload
    payload.update(_extract_langgraph_snapshot_metadata(snapshot))
    return payload


async def _fetch_actor_context(
    *, settings: Any, telegram_chat_id: int | None
) -> dict[str, Any] | None:
    if telegram_chat_id is None:
        return None
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/internal/identity/context',
        params={'telegram_chat_id': telegram_chat_id},
    )
    if status_code != 200 or payload is None:
        return None
    actor = payload.get('actor')
    return actor if isinstance(actor, dict) else None


def _get_cached_public_resource(cache_key: str) -> Any | None:
    entry = _PUBLIC_RESOURCE_CACHE.get(cache_key)
    if not isinstance(entry, dict):
        return None
    expires_at = float(entry.get('expires_at', 0.0) or 0.0)
    if expires_at <= monotonic():
        _PUBLIC_RESOURCE_CACHE.pop(cache_key, None)
        return None
    return entry.get('value')


def _store_cached_public_resource(cache_key: str, value: Any) -> Any:
    _PUBLIC_RESOURCE_CACHE[cache_key] = {
        'value': value,
        'expires_at': monotonic() + _PUBLIC_RESOURCE_CACHE_TTL_SECONDS,
    }
    return value


async def _fetch_public_school_profile(*, settings: Any) -> dict[str, Any] | None:
    cached = _get_cached_public_resource('public_school_profile')
    if isinstance(cached, dict):
        return dict(cached)
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/school-profile',
    )
    if status_code != 200 or payload is None:
        return None
    profile = payload.get('profile')
    if not isinstance(profile, dict):
        return None
    hydrated_profile = dict(profile)
    if not isinstance(hydrated_profile.get('public_timeline'), list):
        timeline = await _fetch_public_timeline(settings=settings)
        timeline_entries = timeline.get('entries') if isinstance(timeline, dict) else None
        if isinstance(timeline_entries, list):
            hydrated_profile['public_timeline'] = timeline_entries
    return dict(_store_cached_public_resource('public_school_profile', hydrated_profile))


async def _fetch_public_assistant_capabilities(*, settings: Any) -> dict[str, Any] | None:
    cached = _get_cached_public_resource('public_assistant_capabilities')
    if isinstance(cached, dict):
        return dict(cached)
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/assistant-capabilities',
    )
    if status_code != 200 or payload is None:
        return None
    capabilities = payload.get('capabilities')
    return (
        dict(_store_cached_public_resource('public_assistant_capabilities', dict(capabilities)))
        if isinstance(capabilities, dict)
        else None
    )


async def _fetch_public_org_directory(*, settings: Any) -> dict[str, Any] | None:
    cached = _get_cached_public_resource('public_org_directory')
    if isinstance(cached, dict):
        return dict(cached)
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/org-directory',
    )
    if status_code != 200 or payload is None:
        return None
    directory = payload.get('directory')
    return (
        dict(_store_cached_public_resource('public_org_directory', dict(directory)))
        if isinstance(directory, dict)
        else None
    )


async def _fetch_public_service_directory(*, settings: Any) -> dict[str, Any] | None:
    cached = _get_cached_public_resource('public_service_directory')
    if isinstance(cached, dict):
        return dict(cached)
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/service-directory',
    )
    if status_code != 200 or payload is None:
        return None
    directory = payload.get('directory')
    return (
        dict(_store_cached_public_resource('public_service_directory', dict(directory)))
        if isinstance(directory, dict)
        else None
    )


async def _fetch_public_timeline(*, settings: Any) -> dict[str, Any] | None:
    cached = _get_cached_public_resource('public_timeline')
    if isinstance(cached, dict):
        return dict(cached)
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/timeline',
    )
    if status_code != 200 or payload is None:
        return None
    timeline = payload.get('timeline')
    return (
        dict(_store_cached_public_resource('public_timeline', dict(timeline)))
        if isinstance(timeline, dict)
        else None
    )


async def _fetch_public_calendar_events(*, settings: Any) -> list[dict[str, Any]]:
    cached = _get_cached_public_resource('public_calendar_events')
    if isinstance(cached, list):
        return [dict(item) for item in cached if isinstance(item, dict)]
    today = date.today()
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/calendar/public',
        params={
            'date_from': today.isoformat(),
            'date_to': (today + timedelta(days=180)).isoformat(),
            'limit': 12,
        },
    )
    if status_code != 200 or payload is None:
        return []
    events = payload.get('events')
    if not isinstance(events, list):
        return []
    filtered = [dict(item) for item in events if isinstance(item, dict)]
    _store_cached_public_resource('public_calendar_events', filtered)
    return filtered


async def _fetch_internal_workflow_status(
    *,
    settings: Any,
    conversation_external_id: str,
    protocol_code: str | None = None,
    workflow_kind: str | None = None,
) -> dict[str, Any] | None:
    params: dict[str, object] = {
        'conversation_external_id': conversation_external_id,
        'channel': 'telegram',
    }
    if protocol_code:
        params['protocol_code'] = protocol_code
    if workflow_kind:
        params['workflow_kind'] = workflow_kind

    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/internal/workflows/status',
        params=params,
    )
    if status_code != 200 or payload is None:
        return None
    return payload if isinstance(payload, dict) else None
