from __future__ import annotations

# ruff: noqa: F401,F403,F405

"""Native LlamaIndex execution plan extracted from llamaindex_native_runtime.py."""

LOCAL_EXTRACTED_NAMES = {'maybe_execute_llamaindex_native_plan'}

from . import llamaindex_native_runtime as _native
from .llamaindex_native_preflight_runtime import maybe_execute_llamaindex_native_preflight
from .semantic_ingress_runtime import (
    apply_turn_frame_preview,
    build_turn_frame_public_plan,
    maybe_resolve_turn_frame,
)

def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value

async def maybe_execute_llamaindex_native_plan(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
    path_profile: PathExecutionProfile | None = None,
) -> KernelRunResult | None:
    _refresh_native_namespace()
    started_at = monotonic()
    restricted_doc_fast_path = await _maybe_execute_llamaindex_restricted_doc_fast_path(
        request=request,
        settings=settings,
        plan=plan,
        engine_name=engine_name,
        engine_mode=engine_mode,
    )
    if restricted_doc_fast_path is not None:
        return restricted_doc_fast_path
    effective_path_profile = path_profile or get_path_execution_profile(engine_name)
    if not _should_use_llamaindex_native_public_router(plan):
        return None

    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    effective_conversation_id = rt._effective_conversation_id(request)
    conversation_context_bundle = await rt._fetch_conversation_context(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
    )
    conversation_context = rt._conversation_context_payload(conversation_context_bundle)
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    native_preflight_result = await maybe_execute_llamaindex_native_preflight(
        request=request,
        settings=settings,
        plan=plan,
        engine_name=engine_name,
        engine_mode=engine_mode,
        actor=actor,
        effective_conversation_id=effective_conversation_id,
        conversation_context=conversation_context,
        school_profile=school_profile,
        started_at=started_at,
    )
    if native_preflight_result is not None:
        return native_preflight_result

    contextual_public_profile = school_profile
    early_turn_frame = None
    early_turn_frame_public_plan = None
    try:
        early_turn_frame = await maybe_resolve_turn_frame(
            settings=settings,
            request_message=request.message,
            conversation_context=conversation_context,
            preview=plan.preview.model_copy(deep=True),
            stack_label='llamaindex',
            authenticated=bool(getattr(request.user, 'authenticated', False)),
        )
        early_turn_frame_public_plan = build_turn_frame_public_plan(early_turn_frame)
    except Exception:
        early_turn_frame = None
        early_turn_frame_public_plan = None
    early_public_answer = await _resolve_early_llamaindex_public_answer(
        request=request,
        plan=plan,
        settings=settings,
        school_profile=contextual_public_profile if isinstance(contextual_public_profile, dict) else None,
        conversation_context=conversation_context,
    )
    if early_public_answer:
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.98,
            reason='consulta publica contextual resolvida antes do routing protegido do llamaindex',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        preview.needs_authentication = False
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta publica contextual resolvida antes do caminho protegido do LlamaIndex.',
        )
        suggested_replies = rt._build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=contextual_public_profile if isinstance(contextual_public_profile, dict) else {},
            conversation_context=conversation_context,
        )
        message_text = early_public_answer.answer_text
        composer_used = False
        if isinstance(contextual_public_profile, dict):
            resolved_public_plan = early_turn_frame_public_plan or rt._build_public_institution_plan(
                request.message,
                list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                conversation_context=conversation_context,
                school_profile=contextual_public_profile,
            )
            composed_public_answer = await rt._compose_public_profile_answer_agentic(
                settings=settings,
                profile=contextual_public_profile,
                actor=actor,
                message=request.message,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=resolved_public_plan,
            )
            if composed_public_answer:
                message_text = composed_public_answer
                composer_used = True
        message_text = rt._normalize_response_wording(message_text)
        early_reason_label = {
            'canonical_lane': (
                f'llamaindex canonical public lane fast path:{early_public_answer.canonical_lane}'
                if early_public_answer.canonical_lane
                else 'llamaindex canonical public lane fast path'
            ),
            'contextual_boundary': 'llamaindex contextual public boundary fast path',
            'pricing_projection': 'llamaindex contextual public pricing fast path',
            'contextual_direct': 'llamaindex contextual public direct fast path',
        }.get(early_public_answer.reason, 'llamaindex contextual public direct fast path')
        early_graph_marker = {
            'canonical_lane': (
                f'llamaindex:canonical_public_lane_fast_path:{early_public_answer.canonical_lane}'
                if early_public_answer.canonical_lane
                else 'llamaindex:canonical_public_lane_fast_path'
            ),
            'contextual_boundary': 'llamaindex:contextual_public_boundary_fast_path',
            'pricing_projection': 'llamaindex:contextual_public_pricing_fast_path',
            'contextual_direct': 'llamaindex:contextual_public_direct_fast_path',
        }.get(early_public_answer.reason, 'llamaindex:contextual_public_direct_fast_path')
        early_response_reason = {
            'canonical_lane': (
                f'llamaindex_public_canonical_lane:{early_public_answer.canonical_lane}'
                if early_public_answer.canonical_lane
                else 'llamaindex_canonical_public_lane_fast_path'
            ),
            'contextual_boundary': 'llamaindex_contextual_public_boundary_fast_path',
            'pricing_projection': 'llamaindex_contextual_public_pricing_fast_path',
            'contextual_direct': 'llamaindex_contextual_public_direct_fast_path',
        }.get(early_public_answer.reason, 'llamaindex_contextual_public_direct_fast_path')
        early_candidate_reason = {
            'canonical_lane': (
                f'public_canonical_lane:{early_public_answer.canonical_lane}'
                if early_public_answer.canonical_lane
                else 'canonical_public_lane_fast_path'
            ),
            'contextual_boundary': 'contextual_public_boundary_fast_path',
            'pricing_projection': 'contextual_public_pricing_fast_path',
            'contextual_direct': 'contextual_public_direct_fast_path',
        }.get(early_public_answer.reason, 'contextual_public_direct_fast_path')
        await rt._persist_conversation_turn(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            actor=actor,
            user_message=request.message,
            assistant_message=message_text,
        )
        await rt._persist_operational_trace(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            preview=preview,
            school_profile=contextual_public_profile if isinstance(contextual_public_profile, dict) else {},
            conversation_context=conversation_context,
            public_plan=None,
            request_message=request.message,
            message_text=message_text,
            citations_count=0,
            suggested_reply_count=len(suggested_replies),
            visual_asset_count=0,
            answer_verifier_valid=True,
            answer_verifier_reason=early_reason_label,
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )
        response = MessageResponse(
            message_text=message_text,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=suggested_replies,
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=preview.needs_authentication,
            graph_path=[
                *preview.graph_path,
                'llamaindex:public',
                early_graph_marker,
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason=early_response_reason,
            candidate_chosen='deterministic',
            candidate_reason=early_candidate_reason,
            retrieval_probe_topic=None,
            response_cache_hit=False,
            response_cache_kind=None,
            used_llm=composer_used,
            llm_stages=['public_answer_composer'] if composer_used else [],
            final_polish_eligible=composer_used,
            final_polish_applied=composer_used,
            final_polish_mode='grounded_public_composition' if composer_used else None,
            final_polish_reason='public_answer_composer' if composer_used else None,
            final_polish_changed_text=composer_used,
            final_polish_preserved_fallback=False,
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason=early_reason_label,
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                early_graph_marker,
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )
    analysis_message = rt._build_analysis_message(request.message, conversation_context_bundle)
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    if not isinstance(school_profile, dict):
        return None
    if rt._is_public_timeline_query(request.message):
        timeline = await rt._fetch_public_timeline(settings=settings)
        if isinstance(timeline, dict):
            school_profile.setdefault('school_name', timeline.get('school_name'))
            school_profile['public_timeline'] = timeline.get('entries', [])
    if rt._is_public_calendar_event_query(request.message) or rt._is_public_calendar_visibility_query(request.message):
        calendar_events = await rt._fetch_public_calendar_events(settings=settings)
        if calendar_events:
            school_profile['public_calendar_events'] = calendar_events
    semantic_ingress_preview = plan.preview.model_copy(deep=True)
    semantic_ingress_plan = await maybe_resolve_semantic_ingress_plan(
        settings=settings,
        request_message=request.message,
        conversation_context=conversation_context,
        preview=semantic_ingress_preview,
        stack_label='llamaindex',
    )
    if (
        (semantic_ingress_plan is None or not is_terminal_semantic_ingress_plan(semantic_ingress_plan))
        and actor is not None
        and request.user.authenticated
        and not rt._is_high_confidence_public_profile_query(
            request.message,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    ):
        rt._apply_protected_domain_rescue(
            preview=semantic_ingress_preview,
            actor=actor,
            message=request.message,
            conversation_context=conversation_context,
        )
    if semantic_ingress_plan is not None:
        semantic_ingress_preview = apply_semantic_ingress_preview(
            preview=semantic_ingress_preview,
            plan=semantic_ingress_plan,
            stack_name='llamaindex',
        )
    semantic_ingress_public_plan = (
        build_semantic_ingress_public_plan(semantic_ingress_plan)
        if semantic_ingress_plan is not None
        else None
    )
    turn_frame = None
    turn_frame_public_plan = None
    if semantic_ingress_plan is None or not is_terminal_semantic_ingress_plan(semantic_ingress_plan):
        turn_frame = await maybe_resolve_turn_frame(
            settings=settings,
            request_message=request.message,
            conversation_context=conversation_context,
            preview=semantic_ingress_preview,
            stack_label='llamaindex',
            authenticated=bool(request.user.authenticated),
        )
        if turn_frame is not None:
            semantic_ingress_preview = apply_turn_frame_preview(
                preview=semantic_ingress_preview,
                turn_frame=turn_frame,
                stack_name='llamaindex',
            )
            turn_frame_public_plan = build_turn_frame_public_plan(turn_frame)
    semantic_ingress_native_decision = (
        _semantic_ingress_native_public_decision(public_plan=semantic_ingress_public_plan)
        if semantic_ingress_public_plan is not None
        else None
    )
    semantic_ingress_terminal_answer = None
    if (
        semantic_ingress_public_plan is not None
        and is_terminal_semantic_ingress_plan(semantic_ingress_plan)
    ):
        semantic_ingress_terminal_answer = _compose_semantic_ingress_terminal_answer(
            school_profile=school_profile,
            request_message=request.message,
            actor=actor,
            conversation_context=conversation_context,
            public_plan=semantic_ingress_public_plan,
        )
    if semantic_ingress_terminal_answer:
        preview = semantic_ingress_preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.reason = f'llamaindex_semantic_ingress:{semantic_ingress_plan.conversation_act}'
        preview.classification = _public_classification_for_act(
            semantic_ingress_public_plan.conversation_act,
            'ato terminal do semantic ingress resolvido antes de qualquer roteamento nativo do llamaindex',
        )
        preview.needs_authentication = False
        preview.selected_tools = list(
            dict.fromkeys([*preview.selected_tools, *list(semantic_ingress_public_plan.required_tools)])
        )
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Ato terminal de semantic ingress resolvido antes do roteamento nativo do LlamaIndex.',
        )
        suggested_replies = rt._build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        message_text = rt._normalize_response_wording(semantic_ingress_terminal_answer)
        await rt._persist_conversation_turn(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            actor=actor,
            user_message=request.message,
            assistant_message=message_text,
        )
        await rt._persist_operational_trace(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            preview=preview,
            school_profile=school_profile,
            conversation_context=conversation_context,
            public_plan=semantic_ingress_public_plan,
            request_message=request.message,
            message_text=message_text,
            citations_count=0,
            suggested_reply_count=len(suggested_replies),
            visual_asset_count=0,
            answer_verifier_valid=True,
            answer_verifier_reason='llamaindex terminal semantic ingress',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )
        response = MessageResponse(
            message_text=message_text,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=suggested_replies,
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=preview.needs_authentication,
            graph_path=[
                *preview.graph_path,
                'llamaindex:public',
                f'llamaindex:semantic_ingress:{semantic_ingress_plan.conversation_act}',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason=preview.reason,
            candidate_chosen='deterministic',
            candidate_reason=f'semantic_ingress:{semantic_ingress_plan.conversation_act}',
            retrieval_probe_topic=None,
            response_cache_hit=False,
            response_cache_kind=None,
            used_llm=True,
            llm_stages=['semantic_ingress_classifier'],
            final_polish_eligible=False,
            final_polish_applied=False,
            final_polish_mode='skip',
            final_polish_reason='semantic_ingress_terminal',
            final_polish_changed_text=False,
            final_polish_preserved_fallback=False,
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='llamaindex terminal semantic ingress',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                f'semantic_ingress:{semantic_ingress_plan.conversation_act}',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )
    early_public_canonical_lane = None if semantic_ingress_plan is not None else (
        match_public_canonical_lane(request.message)
        or match_public_canonical_lane(analysis_message)
    )
    early_public_canonical_answer = (
        _canonical_lane_answer_for_message(
            canonical_lane=early_public_canonical_lane,
            message=request.message,
            school_profile=school_profile,
        )
        if early_public_canonical_lane
        else None
    )
    if early_public_canonical_answer:
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.99,
            reason='lane publica canonica resolvida antes do roteamento pesado do llamaindex',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        preview.needs_authentication = False
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta canônica pública resolvida antes do roteamento pesado do LlamaIndex.',
        )
        suggested_replies = rt._build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        message_text = rt._normalize_response_wording(early_public_canonical_answer)
        await rt._persist_conversation_turn(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            actor=actor,
            user_message=request.message,
            assistant_message=message_text,
        )
        await rt._persist_operational_trace(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            preview=preview,
            school_profile=school_profile,
            conversation_context=conversation_context,
            public_plan=None,
            request_message=request.message,
            message_text=message_text,
            citations_count=0,
            suggested_reply_count=len(suggested_replies),
            visual_asset_count=0,
            answer_verifier_valid=True,
            answer_verifier_reason='llamaindex canonical public lane fast path',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )
        response = MessageResponse(
            message_text=message_text,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=suggested_replies,
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=preview.needs_authentication,
            graph_path=[
                *preview.graph_path,
                'llamaindex:public',
                f'llamaindex:canonical_lane:{early_public_canonical_lane}',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason=f'llamaindex_public_canonical_lane:{early_public_canonical_lane}',
            candidate_chosen='deterministic',
            candidate_reason=f'public_canonical_lane:{early_public_canonical_lane}',
            retrieval_probe_topic=None,
            response_cache_hit=False,
            response_cache_kind=None,
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='llamaindex canonical public lane fast path',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                f'canonical_lane:{early_public_canonical_lane}',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )
    deterministic_public_decision = semantic_ingress_native_decision or _deterministic_llamaindex_native_public_decision(
        message=request.message,
        preview=semantic_ingress_preview,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    skip_fast_paths = semantic_ingress_plan is not None or _should_skip_llamaindex_public_fast_paths(
        request.message,
        heuristic_decision=deterministic_public_decision,
    )
    early_known_unknown_key = detect_public_known_unknown_key(analysis_message) or detect_public_known_unknown_key(request.message)
    early_public_canonical_lane = (
        match_public_canonical_lane(request.message)
        or match_public_canonical_lane(analysis_message)
    ) if not skip_fast_paths else None
    contextual_fast_public_answer = None
    fast_public_channel_answer = None
    if not skip_fast_paths:
        contextual_fast_public_answer = await _maybe_contextual_public_direct_answer(
            request=request,
            analysis_message=analysis_message,
            preview=semantic_ingress_preview,
            settings=settings,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        fast_public_channel_answer = contextual_fast_public_answer
    if not fast_public_channel_answer and not skip_fast_paths:
        fast_public_channel_answer = rt._try_public_channel_fast_answer(
            message=request.message,
            profile=school_profile,
        )
    if fast_public_channel_answer and (contextual_fast_public_answer is not None or not early_public_canonical_lane):
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.98,
            reason='consulta publica resolvida deterministicamente antes do routing pesado do llamaindex',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        preview.needs_authentication = False
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta publica deterministica servida antes do routing documental pesado do LlamaIndex.',
        )
        suggested_replies = rt._build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        message_text = rt._normalize_response_wording(fast_public_channel_answer)
        await rt._persist_conversation_turn(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            actor=actor,
            user_message=request.message,
            assistant_message=message_text,
        )
        await rt._persist_operational_trace(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            preview=preview,
            school_profile=school_profile,
            conversation_context=conversation_context,
            public_plan=None,
            request_message=request.message,
            message_text=message_text,
            citations_count=0,
            suggested_reply_count=len(suggested_replies),
            visual_asset_count=0,
            answer_verifier_valid=True,
            answer_verifier_reason='llamaindex deterministic public fast path',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )
        response = MessageResponse(
            message_text=message_text,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=suggested_replies,
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=preview.needs_authentication,
            graph_path=[
                *preview.graph_path,
                'llamaindex:public',
                'llamaindex:contextual_public_direct',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason='contextual_public_direct_answer',
            candidate_chosen='deterministic',
            candidate_reason='contextual_public_direct_answer',
            retrieval_probe_topic=None,
            response_cache_hit=False,
            response_cache_kind=None,
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='llamaindex deterministic public fast path',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                'llamaindex:contextual_public_direct',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )

    orphan_workflow_follow_up = None
    if not early_public_canonical_lane and not early_known_unknown_key and not rt._is_service_routing_query(request.message):
        orphan_workflow_follow_up = rt._compose_orphan_workflow_follow_up_answer(
            request.message,
            conversation_context,
        )
    if orphan_workflow_follow_up:
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.public if not request.user.authenticated else AccessTier.authenticated,
            confidence=0.95,
            reason='follow-up de workflow resgatado do contexto antes do roteamento nativo do llamaindex',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_workflow_status']))
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Follow-up de workflow recuperado do contexto conversacional.',
        )
        response = MessageResponse(
            message_text=orphan_workflow_follow_up,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=[],
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=False,
            graph_path=[
                *preview.graph_path,
                'llamaindex:workflow',
                'llamaindex:orphan_workflow_followup',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason='llamaindex_orphan_workflow_followup',
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='follow-up de workflow resgatado deterministicamente do contexto',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                'llamaindex_tool:get_workflow_status',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )

    llm_forced_mode = rt._llm_forced_mode_enabled(settings=settings, request=request)
    public_canonical_lane = None if llm_forced_mode else (match_public_canonical_lane(request.message) or match_public_canonical_lane(analysis_message))
    public_canonical_answer = (
        _canonical_lane_answer_for_message(
            canonical_lane=public_canonical_lane,
            message=request.message,
            school_profile=school_profile,
        )
        if public_canonical_lane
        else None
    )
    if public_canonical_answer:
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = _public_classification_for_act(
            'support_routing',
            'pergunta publica canonica resolvida deterministicamente antes do roteador nativo do llamaindex',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta publica canonica resolvida por lane deterministica compartilhada.',
        )
        response = MessageResponse(
            message_text=public_canonical_answer,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=[],
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=False,
            graph_path=[
                *preview.graph_path,
                'llamaindex:public',
                'llamaindex:canonical_lane',
                public_canonical_lane,
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason=f'llamaindex_public_canonical_lane:{public_canonical_lane}',
            candidate_chosen='deterministic',
            candidate_reason=f'public_canonical_lane:{public_canonical_lane}',
            retrieval_probe_topic=None,
            response_cache_hit=False,
            response_cache_kind=None,
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='llamaindex deterministic canonical public lane',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                f'canonical_lane:{public_canonical_lane}',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )

    llamaindex_llm = _build_llamaindex_llm(settings=settings)
    llm_native_public_decision = None
    if semantic_ingress_native_decision is None and _should_use_llamaindex_llm_public_resolver(
        request=request,
        plan=plan,
        heuristic_decision=deterministic_public_decision,
        settings=settings,
    ):
        deterministic_public_plan = rt._build_public_institution_plan(
            request.message,
            list(getattr(semantic_ingress_preview, 'selected_tools', ()) or ()),
            semantic_plan=None,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        llm_native_public_decision = await _resolve_llamaindex_native_public_decision(
            llm=llamaindex_llm,
            settings=settings,
            message=request.message,
            preview=semantic_ingress_preview,
            school_profile=school_profile,
            conversation_context=conversation_context,
            deterministic_plan=deterministic_public_plan,
        )
    native_public_decision = semantic_ingress_native_decision or _merge_llamaindex_native_public_decisions(
        llm_decision=llm_native_public_decision,
        heuristic_decision=deterministic_public_decision,
    )

    public_plan = semantic_ingress_public_plan or turn_frame_public_plan or await rt._resolve_public_institution_plan(
        settings=settings,
        message=request.message,
        preview=semantic_ingress_preview,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    if native_public_decision is not None:
        public_plan = _native_public_plan_from_decision(
            message=request.message,
            decision=native_public_decision,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    elif _looks_like_llamaindex_value_prop_query(request.message):
        native_public_decision = LlamaIndexNativePublicDecision(
            conversation_act='highlight',
            answer_mode='documentary',
            required_tools=['get_public_school_profile'],
            use_conversation_context=True,
        )
        public_plan = _native_public_plan_from_decision(
            message=request.message,
            decision=native_public_decision,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    preview = semantic_ingress_preview.model_copy(deep=True)
    preview.selected_tools = list(public_plan.required_tools)
    if (
        preview.mode is OrchestrationMode.clarify
        and native_public_decision is not None
        and native_public_decision.answer_mode != 'clarify'
    ):
        preview.mode = OrchestrationMode.structured_tool
        preview.reason = 'llamaindex_native_public_resolver'
    if native_public_decision is not None and native_public_decision.answer_mode != 'clarify':
        preview.classification = _public_classification_for_act(
            public_plan.conversation_act,
            'roteamento publico nativo do llamaindex resolveu a pergunta sem clarificacao',
        )
        preview.needs_authentication = False
    effective_analysis_message = _build_llamaindex_analysis_query(
        original_message=request.message,
        analysis_message=analysis_message,
        native_decision=native_public_decision,
        public_plan=public_plan,
    )
    effective_retrieval_query = _build_llamaindex_retrieval_query(
        original_message=request.message,
        native_decision=native_public_decision,
        public_plan=public_plan,
    )
    skip_fast_paths = _should_skip_llamaindex_public_fast_paths(
        request.message,
        heuristic_decision=deterministic_public_decision,
        native_decision=native_public_decision,
    )
    public_canonical_lane = (
        (
            match_public_canonical_lane(request.message)
            or match_public_canonical_lane(effective_analysis_message)
        )
        if not skip_fast_paths and not llm_forced_mode
        else None
    )
    public_canonical_answer = (
        _canonical_lane_answer_for_message(
            canonical_lane=public_canonical_lane,
            message=request.message,
            school_profile=school_profile,
        )
        if public_canonical_lane
        else None
    )

    descriptions = _tool_descriptions(public_plan)
    native_public_unpublished_answer = _native_llamaindex_public_unpublished_answer(
        decision=native_public_decision,
        message=request.message,
        school_profile=school_profile,
    )
    retrieval_query_engine, citation_retriever = _build_public_retrieval_query_engine(
        settings=settings,
        preview=preview,
        original_message=request.message,
        llm=llamaindex_llm,
        prefer_citation_engine=effective_path_profile.prefer_native_llamaindex_citation_engine,
        prefer_native_qdrant_autoretriever=effective_path_profile.prefer_native_llamaindex_qdrant_autoretriever,
    )
    tools = {
        'public_profile': QueryEngineTool.from_defaults(
            query_engine=PublicProfileQueryEngine(
                settings=settings,
                request=request,
                preview=preview,
                profile=school_profile,
                actor=actor,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=public_plan,
            ),
            name='public_profile',
            description=descriptions['public_profile'],
        ),
        'pricing_projection': QueryEngineTool.from_defaults(
            query_engine=PublicPricingProjectionQueryEngine(
                settings=settings,
                request=request,
                preview=preview,
                profile=school_profile,
                actor=actor,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=public_plan,
            ),
            name='pricing_projection',
            description=descriptions['pricing_projection'],
        ),
        'public_retrieval': QueryEngineTool.from_defaults(
            query_engine=retrieval_query_engine,
            name='public_retrieval',
            description=descriptions['public_retrieval'],
        ),
    }
    selected_tool_names: tuple[str, ...] = ('unknown',)
    subquestion_result: tuple[Response, str] | None = None
    router_result: tuple[Response, tuple[str, ...]] | None = None
    tool_response: Response | None = None
    answer_text = ''
    citations: list[MessageResponseCitation] = []
    retrieval_backend = RetrievalBackend.none
    execution_reason = 'llamaindex_native_public_router'
    summary_store_hits = 0
    if (
        getattr(settings, 'retrieval_aware_routing_enabled', True)
        and public_canonical_lane is None
        and (
            rt._looks_like_public_documentary_open_query(request.message)
            or _has_documentary_retrieval_cues(request.message)
            or _looks_like_open_documentary_bundle_query(request.message)
        )
    ):
        try:
            summary_store_hits = len(
                _query_public_summary_store_parent_ref_keys(
                    query=effective_retrieval_query,
                    settings=settings,
                )
            )
        except Exception:
            summary_store_hits = 0
    llamaindex_probe = build_public_evidence_probe(
        message=request.message,
        canonical_lane=public_canonical_lane,
        primary_act=public_plan.conversation_act,
        secondary_acts=public_plan.secondary_acts,
        evidence_pack=None,
        retrieval_search=None,
        summary_store_hits=summary_store_hits,
    )
    telemetry_snapshot = get_stack_telemetry_snapshot('llamaindex')
    llamaindex_serving_policy = build_public_serving_policy(
        settings=settings,
        stack_name='llamaindex',
        request=request,
        probe=llamaindex_probe,
        load_snapshot=LoadSnapshot(
            llm_forced_mode=llm_forced_mode,
            recent_request_count=telemetry_snapshot.recent_request_count,
            recent_p95_latency_ms=telemetry_snapshot.recent_p95_latency_ms,
            recent_timeout_rate=telemetry_snapshot.recent_timeout_rate,
            recent_error_rate=telemetry_snapshot.recent_error_rate,
            recent_cache_hit_rate=telemetry_snapshot.recent_cache_hit_rate,
            recent_used_llm_rate=telemetry_snapshot.recent_used_llm_rate,
        ),
    )
    if (
        getattr(settings, 'public_response_cache_enabled', True)
        and llamaindex_serving_policy.prefer_cache
        and not llm_forced_mode
        and semantic_ingress_plan is None
    ):
        semantic_threshold = float(
            getattr(settings, 'public_response_semantic_jaccard_threshold', 0.84)
            if getattr(settings, 'public_response_semantic_cache_enabled', True)
            else 1.01
        )
        cached_public_response = get_cached_public_response(
            message=request.message,
            canonical_lane=public_canonical_lane,
            topic=llamaindex_probe.topic,
            evidence_fingerprint=llamaindex_probe.evidence_fingerprint,
            semantic_threshold=semantic_threshold,
        )
        if cached_public_response is not None:
            response = MessageResponse(
                message_text=cached_public_response.text,
                mode=preview.mode,
                classification=preview.classification,
                retrieval_backend=RetrievalBackend.none,
                selected_tools=list(dict.fromkeys([*preview.selected_tools, 'llamaindex_selector_router'])),
                citations=[],
                visual_assets=[],
                suggested_replies=[],
                calendar_events=[],
                evidence_pack=build_structured_tool_evidence_pack(
                    selected_tools=preview.selected_tools,
                    slice_name=plan.slice_name,
                    summary='Resposta publica reaproveitada do cache semantico do caminho LlamaIndex.',
                ),
                needs_authentication=preview.needs_authentication,
                graph_path=[*preview.graph_path, 'llamaindex:cache', cached_public_response.cache_kind],
                risk_flags=preview.risk_flags,
                reason=f'llamaindex_cache:{cached_public_response.reason or cached_public_response.cache_kind}',
                used_llm=False,
                llm_stages=[],
                final_polish_eligible=False,
                final_polish_applied=False,
                final_polish_mode='skip',
                final_polish_reason='cache_hit',
                final_polish_changed_text=False,
                final_polish_preserved_fallback=False,
                candidate_chosen=cached_public_response.candidate_kind or 'deterministic',
                candidate_reason=f'cache:{cached_public_response.reason or cached_public_response.cache_kind}',
                retrieval_probe_topic=llamaindex_probe.topic,
                response_cache_hit=True,
                response_cache_kind=cached_public_response.cache_kind,
            )
            record_stack_outcome(
                stack_name='llamaindex',
                latency_ms=(monotonic() - started_at) * 1000,
                success=True,
                timeout=False,
                cache_hit=True,
                used_llm=False,
                candidate_kind=response.candidate_chosen,
            )
            return KernelRunResult(
                plan=plan,
                reflection=KernelReflection(
                    grounded=True,
                    verifier_reason='cache_hit',
                    fallback_used=False,
                    answer_judge_used=False,
                    notes=['route:structured_tool', 'cache:semantic_or_exact', *plan.plan_notes],
                ),
                response=response.model_dump(mode='json'),
            )
    documentary_direct_retrieval = _should_force_llamaindex_documentary_retrieval(
        message=request.message,
        public_plan=public_plan,
        native_decision=native_public_decision,
    )
    if (
        getattr(settings, 'retrieval_aware_routing_enabled', True)
        and not llamaindex_serving_policy.allow_documentary_synthesis
        and not llm_forced_mode
    ):
        documentary_direct_retrieval = False

    agent_workflow_result = None
    function_agent_result = None
    if semantic_ingress_terminal_answer:
        preview.mode = OrchestrationMode.structured_tool
        preview.reason = f'llamaindex_semantic_ingress:{semantic_ingress_plan.conversation_act}'
        preview.classification = _public_classification_for_act(
            public_plan.conversation_act,
            'ato terminal do semantic ingress resolvido antes do roteamento pesado do llamaindex',
        )
        preview.needs_authentication = False
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, *list(public_plan.required_tools)]))
        answer_text = semantic_ingress_terminal_answer
        selected_tool_names = ('public_profile',)
        execution_reason = preview.reason
    elif public_canonical_answer:
        preview.mode = OrchestrationMode.structured_tool
        preview.reason = f'llamaindex_public_canonical_lane:{public_canonical_lane}'
        preview.classification = _public_classification_for_act(
            public_plan.conversation_act,
            'pergunta publica canonica resolvida por lane deterministica antes do roteador nativo',
        )
        preview.needs_authentication = False
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        answer_text = public_canonical_answer
        selected_tool_names = ('public_profile',)
        execution_reason = preview.reason
    elif native_public_unpublished_answer:
        preview.mode = OrchestrationMode.structured_tool
        preview.reason = 'llamaindex_public_unpublished_fact'
        preview.classification = _public_classification_for_act(
            public_plan.conversation_act,
            'a pergunta e publica e valida, mas o dado especifico nao esta publicado',
        )
        preview.needs_authentication = False
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        answer_text = native_public_unpublished_answer
        selected_tool_names = ('public_profile',)
        execution_reason = 'llamaindex_public_unpublished_fact'
    elif native_public_decision is not None and native_public_decision.answer_mode == 'profile':
        direct_profile_answer = await rt._compose_public_profile_answer_agentic(
            settings=settings,
            profile=school_profile,
            actor=actor,
            message=request.message,
            original_message=request.message,
            conversation_context=conversation_context,
            semantic_plan=public_plan,
        )
        direct_profile_answer = str(direct_profile_answer or '').strip()
        if (
            direct_profile_answer
            and not llm_forced_mode
            and not direct_profile_answer.startswith('Ainda nao encontrei evidencia publica suficiente')
            and not _should_avoid_llamaindex_public_profile_fast_path(
                message=request.message,
                public_plan=public_plan,
                native_decision=native_public_decision,
            )
        ):
            preview.mode = OrchestrationMode.structured_tool
            preview.reason = 'llamaindex_public_profile_fast_path'
            preview.needs_authentication = False
            preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
            answer_text = direct_profile_answer
            selected_tool_names = ('public_profile',)
            execution_reason = 'llamaindex_public_profile_fast_path'
        else:
            selected_tool_names = ('public_profile',)
            try:
                tool_response = await _await_with_llamaindex_timeout(
                    tools['public_profile'].query_engine.aquery(effective_analysis_message),
                    settings=settings,
                )
            except Exception:
                tool_response = None
    elif documentary_direct_retrieval:
        selected_tool_names = ('public_retrieval',)
        try:
            tool_response = await _await_with_llamaindex_timeout(
                tools['public_retrieval'].query_engine.aquery(effective_retrieval_query),
                settings=settings,
            )
        except Exception:
            tool_response = None
    elif (
        effective_path_profile.prefer_native_llamaindex_function_agent
        and _should_use_llamaindex_function_agent(request=request, public_plan=public_plan)
    ):
        agent_workflow_result = await _maybe_execute_llamaindex_agent_workflow(
            analysis_message=effective_analysis_message,
            conversation_context=conversation_context,
            llm=llamaindex_llm,
            tools=tools,
            session_id=effective_conversation_id,
            settings=settings,
        )
    if agent_workflow_result is not None:
        answer_text, selected_tool_names, workflow_citations, execution_reason = agent_workflow_result
        citations = list(workflow_citations)
        retrieval_backend = RetrievalBackend.qdrant_hybrid if citations else RetrievalBackend.none
    elif (
        effective_path_profile.prefer_native_llamaindex_function_agent
        and _should_use_llamaindex_function_agent(request=request, public_plan=public_plan)
    ):
        function_agent_result = await _maybe_execute_llamaindex_function_agent(
            analysis_message=effective_analysis_message,
            original_message=request.message,
            llm=llamaindex_llm,
            tools=tools,
            settings=settings,
        )
    if native_public_unpublished_answer:
        retrieval_backend = RetrievalBackend.none
    elif documentary_direct_retrieval:
        execution_reason = 'llamaindex_public_direct_retrieval'
    elif function_agent_result is not None:
        answer_text, selected_tool_names, function_agent_citations, execution_reason = function_agent_result
        citations = list(function_agent_citations)
        retrieval_backend = RetrievalBackend.qdrant_hybrid if citations else RetrievalBackend.none
    elif tool_response is None:
        if effective_path_profile.prefer_native_llamaindex_subquestions and _should_use_llamaindex_native_subquestions(
            request=request,
            public_plan=public_plan,
        ):
            subquestion_result = await _maybe_execute_llamaindex_subquestion_plan(
                analysis_message=effective_analysis_message,
                tools=tools,
                llm=llamaindex_llm,
                settings=settings,
            )
        if subquestion_result is not None:
            tool_response, selected_tool_name = subquestion_result
            selected_tool_names = (selected_tool_name,)
            execution_reason = 'llamaindex_subquestion_query_engine'
        elif _should_use_llamaindex_selector_router(
            settings=settings,
            native_decision=native_public_decision,
            public_plan=public_plan,
            llm=llamaindex_llm,
            profile=effective_path_profile,
        ):
            router_result = await _maybe_execute_llamaindex_router_query_engine(
                analysis_message=effective_analysis_message,
                tools=tools,
                llm=llamaindex_llm,
                settings=settings,
            )
            if router_result is not None:
                tool_response, selected_tool_names = router_result
                execution_reason = 'llamaindex_router_query_engine'
        else:
            selected_tool = _route_public_query_tool(
                request=request,
                plan=public_plan,
                tools=tools,
                embedding_model=settings.document_embedding_model,
                llm=None,
            )
            selected_tool_name = selected_tool.metadata.name
            selected_tool_names = (selected_tool_name,)
            try:
                tool_response = await _await_with_llamaindex_timeout(
                    selected_tool.query_engine.aquery(
                        effective_retrieval_query if selected_tool_name == 'public_retrieval' else effective_analysis_message
                    ),
                    settings=settings,
                )
            except Exception:
                tool_response = None
    if tool_response is not None:
        answer_text = str(getattr(tool_response, 'response', '') or str(tool_response)).strip()
        citations = list(_extract_response_citations(tool_response))
        if not citations and citation_retriever is not None:
            citations = list(citation_retriever.latest_citations())
        retrieval_backend = RetrievalBackend(
            str((tool_response.metadata or {}).get('retrieval_backend', RetrievalBackend.none.value))
        )
        execution_reason = str((tool_response.metadata or {}).get('reason', execution_reason))
        if citation_retriever is not None and 'public_retrieval' in selected_tool_names:
            retrieval_backend = RetrievalBackend.qdrant_hybrid
            latest_query_plan = citation_retriever.latest_query_plan()
            if execution_reason in {'llamaindex_native_public_router', 'llamaindex_router_query_engine'}:
                if bool(getattr(latest_query_plan, 'citation_first_recommended', False)):
                    execution_reason = 'llamaindex_public_citation_first'
                else:
                    execution_reason = 'llamaindex_public_citation_query_engine'
    low_confidence_documentary_answer = (
        answer_text.startswith('Ainda nao encontrei evidencia publica suficiente')
        and public_plan.conversation_act in {'highlight', 'pricing', 'comparative', 'curriculum'}
    )
    if low_confidence_documentary_answer:
        fallback_text = await rt._compose_public_profile_answer_agentic(
            settings=settings,
            profile=school_profile,
            actor=actor,
            message=request.message,
            original_message=request.message,
            conversation_context=conversation_context,
            semantic_plan=public_plan,
        )
        fallback_text = str(fallback_text or '').strip()
        if fallback_text and not fallback_text.startswith('Ainda nao encontrei evidencia publica suficiente'):
            answer_text = fallback_text
            selected_tool_names = tuple(dict.fromkeys([*selected_tool_names, 'public_profile']))
            citations = []
            retrieval_backend = RetrievalBackend.none
            execution_reason = 'llamaindex_public_retrieval_profile_fallback'
    if not answer_text and not llm_forced_mode:
        deterministic_public_fallback = await rt._compose_public_profile_answer_agentic(
            settings=settings,
            profile=school_profile,
            actor=actor,
            message=request.message,
            original_message=request.message,
            conversation_context=conversation_context,
            semantic_plan=public_plan,
        )
        deterministic_public_fallback = str(deterministic_public_fallback or '').strip()
        if (
            deterministic_public_fallback
            and not deterministic_public_fallback.startswith('Ainda nao encontrei evidencia publica suficiente')
        ):
            answer_text = deterministic_public_fallback
            selected_tool_names = tuple(dict.fromkeys([*selected_tool_names, 'public_profile']))
            citations = []
            retrieval_backend = RetrievalBackend.none
            execution_reason = 'llamaindex_deterministic_public_fallback'
    if not answer_text:
        fallback_text = await _maybe_contextual_public_direct_answer(
            request=request,
            analysis_message=analysis_message,
            preview=preview,
            settings=settings,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        if fallback_text:
            answer_text = fallback_text
            citations = []
            retrieval_backend = RetrievalBackend.none
            execution_reason = 'contextual_public_direct_answer'
    if not answer_text:
        return None

    message_text = answer_text
    llm_stages = _llamaindex_execution_llm_stages(
        execution_reason=execution_reason,
        semantic_judge_used=False,
    )
    if semantic_ingress_plan is not None:
        llm_stages.insert(0, 'semantic_ingress_classifier')
    final_polish_decision = build_final_polish_decision(
        settings=settings,
        stack_name=engine_name,
        request=request,
        preview=preview,
        response_reason=execution_reason,
        llm_stages=llm_stages,
        citations_count=len(citations),
        support_count=0,
        retrieval_backend=retrieval_backend,
    )
    final_polish_applied = False
    final_polish_changed_text = False
    final_polish_preserved_fallback = False
    if final_polish_decision.apply_polish:
        original_text = message_text
        raw_polished_text = await polish_llamaindex_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        polished_text = rt._preserve_capability_anchor_terms(
            original_text=original_text,
            polished_text=raw_polished_text,
            request_message=request.message,
        )
        final_polish_preserved_fallback = bool(
            raw_polished_text
            and polished_text == original_text
            and rt._normalize_text(raw_polished_text) != rt._normalize_text(original_text)
        )
        if polished_text:
            llm_stages.append('structured_polish')
            final_polish_applied = True
            final_polish_changed_text = rt._normalize_text(polished_text) != rt._normalize_text(original_text)
            message_text = polished_text
    if final_polish_decision.run_response_critic:
        revised_text = await revise_llamaindex_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        if revised_text:
            llm_stages.append('response_critic')
            message_text = revised_text

    verification_slot_memory = rt._build_conversation_slot_memory(
        actor=actor,
        profile=school_profile,
        conversation_context=conversation_context,
        request_message=request.message,
        public_plan=public_plan,
        preview=preview,
    )
    verification, semantic_judge_used = await verify_llamaindex_answer_against_contract(
        settings=settings,
        request_message=request.message,
        preview=preview,
        candidate_text=message_text,
        deterministic_fallback_text=answer_text,
        public_plan=public_plan,
        slot_memory=verification_slot_memory,
    )
    if (
        not verification.valid
        and _should_trust_llamaindex_native_deterministic_answer(
            native_decision=native_public_decision,
            selected_tool_names=selected_tool_names,
        )
    ):
        verification = rt.AnswerVerificationResult(
            valid=True,
            reason='llamaindex_native_deterministic_answer',
        )
        semantic_judge_used = False
    if not verification.valid:
        return None

    if citations:
        sources = rt._render_source_lines(citations)
        if sources and sources not in message_text:
            message_text = f'{message_text}\n\n{sources}'
    message_text = rt._normalize_response_wording(message_text)
    evidence_pack: MessageEvidencePack
    if citations:
        evidence_pack = build_retrieval_evidence_pack(
            citations=citations,
            selected_tools=selected_tool_names,
            retrieval_backend=retrieval_backend,
            summary='Resposta grounded em routing nativo do LlamaIndex com evidencias citadas.',
        )
    else:
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=selected_tool_names,
            slice_name=plan.slice_name,
            summary='Resposta grounded em roteamento nativo do LlamaIndex sobre ferramentas publicas.',
        )
    suggested_replies = rt._build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )

    await rt._persist_conversation_turn(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        actor=actor,
        user_message=request.message,
        assistant_message=message_text,
    )
    await rt._persist_operational_trace(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        engine_name=engine_name,
        engine_mode=engine_mode,
        actor=actor,
        preview=preview,
        school_profile=school_profile,
        conversation_context=conversation_context,
        public_plan=public_plan,
        request_message=request.message,
        message_text=message_text,
        citations_count=len(citations),
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=verification.valid,
        answer_verifier_reason=verification.reason,
        answer_verifier_fallback_used=False,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=semantic_judge_used,
        langgraph_trace_metadata={
            'llamaindex_selected_tool': ','.join(selected_tool_names),
            'llamaindex_execution_reason': execution_reason,
            'llamaindex_citation_engine_used': bool(citation_retriever),
            'llamaindex_function_agent_used': execution_reason == 'llamaindex_function_agent',
            'llamaindex_evidence_support_count': evidence_pack.support_count,
        },
    )

    selected_tools = list(
        dict.fromkeys(
            [
                *preview.selected_tools,
                *list(((tool_response.metadata or {}) if tool_response is not None else {}).get('selected_tools', [])),
                'llamaindex_selector_router',
                *selected_tool_names,
            ]
        )
    )
    llm_stages = _llamaindex_execution_llm_stages(
        execution_reason=execution_reason,
        semantic_judge_used=semantic_judge_used,
    ) + [stage for stage in llm_stages if stage in {'semantic_ingress_classifier', 'structured_polish', 'response_critic'}]
    llm_stages = list(dict.fromkeys(llm_stages))
    deterministic_candidate_text = await rt._compose_public_profile_answer_agentic(
        settings=settings,
        profile=school_profile,
        actor=actor,
        message=request.message,
        original_message=request.message,
        conversation_context=conversation_context,
        semantic_plan=public_plan,
    )
    deterministic_candidate_text = str(deterministic_candidate_text or '').strip()
    candidate_chosen = 'documentary_synthesis' if llm_stages else 'deterministic'
    candidate_reason = execution_reason
    retrieval_probe_topic = llamaindex_probe.topic
    response_cache_hit = False
    response_cache_kind = None
    if (
        deterministic_candidate_text
        and getattr(settings, 'candidate_chooser_enabled', True)
        and semantic_ingress_plan is None
    ):
        deterministic_candidate = build_response_candidate(
            kind='deterministic',
            text=deterministic_candidate_text,
            reason='llamaindex_deterministic_fallback',
            retrieval_backend=RetrievalBackend.none,
            selected_tools=tuple(selected_tools),
            source_count=max(1, len(citations)),
            support_count=evidence_pack.support_count,
        )
        current_candidate = build_response_candidate(
            kind='documentary_synthesis' if llm_stages else 'deterministic',
            text=message_text,
            reason=execution_reason,
            used_llm=bool(llm_stages),
            llm_stages=tuple(llm_stages),
            retrieval_backend=retrieval_backend,
            selected_tools=tuple(selected_tools),
            source_count=max(1, len(citations)),
            support_count=evidence_pack.support_count,
        )
        chosen_candidate = choose_best_candidate(
            candidates=[candidate for candidate in (deterministic_candidate, current_candidate) if candidate is not None],
            probe=llamaindex_probe,
            policy=llamaindex_serving_policy,
        )
        if chosen_candidate is not None:
            message_text = chosen_candidate.candidate.text
            candidate_chosen = chosen_candidate.candidate.kind
            candidate_reason = chosen_candidate.chooser_reason
    if getattr(settings, 'public_response_cache_enabled', True) and llamaindex_serving_policy.prefer_cache:
        store_cached_public_response(
            message=request.message,
            text=message_text,
            canonical_lane=public_canonical_lane,
            topic=llamaindex_probe.topic,
            evidence_fingerprint=llamaindex_probe.evidence_fingerprint,
            candidate_kind=candidate_chosen,
            reason=candidate_reason,
            ttl_seconds=float(getattr(settings, 'public_response_cache_ttl_seconds', 300.0)),
        )
    response = MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=retrieval_backend,
        selected_tools=selected_tools,
        citations=citations,
        visual_assets=[],
        suggested_replies=suggested_replies,
        calendar_events=[],
        evidence_pack=evidence_pack,
        needs_authentication=preview.needs_authentication,
        graph_path=[
            *preview.graph_path,
            'llamaindex:workflow',
            f'llamaindex:{execution_reason}',
            *[f'llamaindex:tool:{tool_name}' for tool_name in selected_tool_names],
            f'kernel:{plan.stack_name}',
        ],
        risk_flags=preview.risk_flags,
        reason=execution_reason,
        used_llm=bool(llm_stages),
        llm_stages=llm_stages,
        final_polish_eligible=final_polish_decision.eligible,
        final_polish_applied=final_polish_applied,
        final_polish_mode=final_polish_decision.mode,
        final_polish_reason=final_polish_decision.reason,
        final_polish_changed_text=final_polish_changed_text,
        final_polish_preserved_fallback=final_polish_preserved_fallback,
        candidate_chosen=candidate_chosen,
        candidate_reason=candidate_reason,
        retrieval_probe_topic=retrieval_probe_topic,
        response_cache_hit=response_cache_hit,
        response_cache_kind=response_cache_kind,
    )
    record_stack_outcome(
        stack_name='llamaindex',
        latency_ms=(monotonic() - started_at) * 1000,
        success=True,
        timeout=False,
        cache_hit=response_cache_hit,
        used_llm=bool(llm_stages),
        candidate_kind=candidate_chosen,
    )
    reflection = KernelReflection(
        grounded=verification.valid,
        verifier_reason=verification.reason,
        fallback_used=False,
        answer_judge_used=semantic_judge_used,
        notes=[
            f'route:{preview.mode.value}',
            f'slice:{plan.slice_name}',
            f'llamaindex_tool:{",".join(selected_tool_names)}',
            f'evidence:{evidence_pack.strategy}',
            *plan.plan_notes,
        ],
    )
    return KernelRunResult(
        plan=plan,
        reflection=reflection,
        response=response.model_dump(mode='json'),
    )
