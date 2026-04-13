from __future__ import annotations

# ruff: noqa: F401,F403,F405

LOCAL_EXTRACTED_NAMES = {'_public_compound'}

from . import langgraph_message_workflow as _native


def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value


async def _public_compound(state: LangGraphMessageState) -> LangGraphMessageState:
    _refresh_native_namespace()
    request = state['request']
    settings = state['settings']
    actor = state['actor']
    preview = state['preview']
    school_profile = state['school_profile']
    conversation_context = state['conversation_context']
    effective_conversation_id = state['effective_conversation_id']
    analysis_message = state['analysis_message']
    turn_frame_public_plan = state.get('turn_frame_public_plan')

    if not isinstance(school_profile, dict):
        return await _delegate_runtime(state)

    public_boundary_answer = rt._compose_contextual_public_boundary_answer(
        message=request.message,
        conversation_context=conversation_context,
        profile=school_profile,
    )
    if public_boundary_answer:
        message_text = rt._normalize_response_wording(public_boundary_answer)
        suggested_replies = rt._build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        evidence_pack = rt._build_runtime_evidence_pack(
            request_message=request.message,
            message_text=message_text,
            preview=preview,
            selected_tools=list(preview.selected_tools),
            citations=[],
            school_profile=school_profile,
            actor=actor,
            conversation_context=conversation_context,
            public_plan=None,
            retrieval_backend=RetrievalBackend.none,
        )
        await rt._persist_operational_trace(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            engine_name=state['engine_name'],
            engine_mode=state['engine_mode'],
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
            answer_verifier_reason='langgraph_public_compound_public_boundary',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
            langgraph_trace_metadata=state.get('langgraph_trace_metadata'),
        )
        await rt._persist_conversation_turn(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            actor=actor,
            user_message=request.message,
            assistant_message=message_text,
        )
        response = MessageResponse(
            message_text=message_text,
            mode=OrchestrationMode.structured_tool,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
            citations=[],
            suggested_replies=suggested_replies,
            evidence_pack=evidence_pack,
            needs_authentication=False,
            graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_compound_public_boundary'],
            risk_flags=rt._build_runtime_risk_flags(
                request_message=request.message,
                message_text=message_text,
                preview=preview,
            ),
            reason='langgraph_public_compound_public_boundary',
            used_llm=False,
            llm_stages=[],
        )
        return {'response': response}

    if any(
        rt._message_matches_term(rt._normalize_text(request.message), term)
        for term in {
            'antes ou depois',
            'primeira reuniao',
            'primeira reunião',
            'antes das aulas',
            'depois das aulas',
            'so esse recorte',
            'só esse recorte',
            'nao quero o calendario inteiro',
            'não quero o calendário inteiro',
            'recorte em ordem',
        }
    ):
        explicit_timeline_answer = rt._try_public_channel_fast_answer(
            message=request.message,
            profile=school_profile,
        )
        if explicit_timeline_answer:
            message_text = rt._normalize_response_wording(explicit_timeline_answer)
            suggested_replies = rt._build_suggested_replies(
                request=request,
                preview=preview,
                actor=actor,
                school_profile=school_profile,
                conversation_context=conversation_context,
            )
            evidence_pack = rt._build_runtime_evidence_pack(
                request_message=request.message,
                message_text=message_text,
                preview=preview,
                selected_tools=list(preview.selected_tools),
                citations=[],
                school_profile=school_profile,
                actor=actor,
                conversation_context=conversation_context,
                public_plan=None,
                retrieval_backend=RetrievalBackend.none,
            )
            await rt._persist_operational_trace(
                settings=settings,
                conversation_external_id=effective_conversation_id,
                channel=request.channel.value,
                engine_name=state['engine_name'],
                engine_mode=state['engine_mode'],
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
                answer_verifier_reason='langgraph_public_timeline_direct',
                answer_verifier_fallback_used=False,
                deterministic_fallback_available=True,
                answer_verifier_judge_used=False,
                langgraph_trace_metadata=state.get('langgraph_trace_metadata'),
            )
            await rt._persist_conversation_turn(
                settings=settings,
                conversation_external_id=effective_conversation_id,
                channel=request.channel.value,
                actor=actor,
                user_message=request.message,
                assistant_message=message_text,
            )
            response = MessageResponse(
                message_text=message_text,
                mode=OrchestrationMode.structured_tool,
                classification=preview.classification,
                retrieval_backend=RetrievalBackend.none,
                selected_tools=list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile', 'get_public_timeline'])),
                citations=[],
                suggested_replies=suggested_replies,
                evidence_pack=evidence_pack,
                needs_authentication=False,
                graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_timeline_direct'],
                risk_flags=rt._build_runtime_risk_flags(
                    request_message=request.message,
                    message_text=message_text,
                    preview=preview,
                ),
                reason='langgraph_public_timeline_direct',
                used_llm=False,
                llm_stages=[],
            )
            return {'response': response}

    contextual_public_message = rt._contextualize_public_followup_message(
        request_message=request.message,
        analysis_message=analysis_message,
        conversation_context=conversation_context,
    )
    timeline_followup_answer = rt._compose_contextual_public_timeline_followup_answer(
        request_message=request.message,
        conversation_context=conversation_context,
        profile=school_profile,
    )
    if timeline_followup_answer:
        message_text = rt._normalize_response_wording(timeline_followup_answer)
        suggested_replies = rt._build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        evidence_pack = rt._build_runtime_evidence_pack(
            request_message=request.message,
            message_text=message_text,
            preview=preview,
            selected_tools=list(preview.selected_tools),
            citations=[],
            school_profile=school_profile,
            actor=actor,
            conversation_context=conversation_context,
            public_plan=None,
            retrieval_backend=RetrievalBackend.none,
        )
        await rt._persist_operational_trace(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            engine_name=state['engine_name'],
            engine_mode=state['engine_mode'],
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
            answer_verifier_reason='langgraph_public_timeline_followup_repair',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
            langgraph_trace_metadata=state.get('langgraph_trace_metadata'),
        )
        await rt._persist_conversation_turn(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            actor=actor,
            user_message=request.message,
            assistant_message=message_text,
        )
        response = MessageResponse(
            message_text=message_text,
            mode=OrchestrationMode.structured_tool,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
            citations=[],
            suggested_replies=suggested_replies,
            evidence_pack=evidence_pack,
            needs_authentication=False,
            graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_timeline_followup_repair'],
            risk_flags=rt._build_runtime_risk_flags(
                request_message=request.message,
                message_text=message_text,
                preview=preview,
            ),
            reason='langgraph_public_timeline_followup_repair',
            used_llm=False,
            llm_stages=[],
        )
        return {'response': response}
    prefer_fast_public_direct = (
        str(contextual_public_message).strip() != str(request.message).strip()
        or rt._is_service_routing_query(request.message)
        or rt._has_public_multi_intent_signal(request.message)
        or rt._is_public_timeline_query(request.message)
        or rt._is_public_timeline_lifecycle_query(request.message)
        or rt._is_public_year_three_phase_query(request.message)
        or rt._is_access_scope_query(request.message)
        or rt._is_positive_requirement_query(request.message)
        or (
            any(rt._message_matches_term(rt._normalize_text(request.message), term) for term in {'documento', 'documentos'})
            and any(
                rt._message_matches_term(rt._normalize_text(request.message), term)
                for term in {'matricula', 'matrícula', 'exigido', 'exigidos'}
            )
        )
    )
    fast_public_message = (
        request.message
        if rt._is_high_confidence_public_profile_query(
            request.message,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        else contextual_public_message
    )
    if prefer_fast_public_direct and rt._base_profile_supports_fast_public_answer(
        message=fast_public_message,
        profile=school_profile,
    ):
        fast_public_answer = rt._try_public_channel_fast_answer(
            message=fast_public_message,
            profile=school_profile,
        )
        if fast_public_answer:
            composer_used = False
            message_text = fast_public_answer
            resolved_public_plan = turn_frame_public_plan or rt._build_public_institution_plan(
                request.message,
                list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                conversation_context=conversation_context,
                school_profile=school_profile,
            )
            composed_public_answer = await rt._compose_public_profile_answer_agentic(
                settings=settings,
                profile=school_profile,
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
            suggested_replies = rt._build_suggested_replies(
                request=request,
                preview=preview,
                actor=actor,
                school_profile=school_profile,
                conversation_context=conversation_context,
            )
            evidence_pack = rt._build_runtime_evidence_pack(
                request_message=request.message,
                message_text=message_text,
                preview=preview,
                selected_tools=list(preview.selected_tools),
                citations=[],
                school_profile=school_profile,
                actor=actor,
                conversation_context=conversation_context,
                public_plan=None,
                retrieval_backend=RetrievalBackend.none,
            )
            await rt._persist_operational_trace(
                settings=settings,
                conversation_external_id=effective_conversation_id,
                channel=request.channel.value,
                engine_name=state['engine_name'],
                engine_mode=state['engine_mode'],
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
                answer_verifier_reason='langgraph_public_compound_contextual_direct',
                answer_verifier_fallback_used=False,
                deterministic_fallback_available=True,
                answer_verifier_judge_used=False,
                langgraph_trace_metadata=state.get('langgraph_trace_metadata'),
            )
            await rt._persist_conversation_turn(
                settings=settings,
                conversation_external_id=effective_conversation_id,
                channel=request.channel.value,
                actor=actor,
                user_message=request.message,
                assistant_message=message_text,
            )
            response = MessageResponse(
                message_text=message_text,
                mode=OrchestrationMode.structured_tool,
                classification=preview.classification,
                retrieval_backend=RetrievalBackend.none,
                selected_tools=list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                citations=[],
                suggested_replies=suggested_replies,
                evidence_pack=evidence_pack,
                needs_authentication=False,
                graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_compound_contextual_direct'],
                risk_flags=rt._build_runtime_risk_flags(
                    request_message=request.message,
                    message_text=message_text,
                    preview=preview,
                ),
                reason='langgraph_public_compound_contextual_direct',
                used_llm=composer_used,
                llm_stages=['public_answer_composer'] if composer_used else [],
            )
            return {'response': response}

    canonical_lane = rt.match_public_canonical_lane(request.message) or rt.match_public_canonical_lane(analysis_message)
    if canonical_lane:
        composer_used = False
        message_text = (
            rt.compose_public_conduct_policy_contextual_answer(request.message, profile=school_profile)
            if canonical_lane == 'public_bundle.conduct_frequency_punctuality'
            else rt.compose_public_canonical_lane_answer(canonical_lane, profile=school_profile)
        )
        resolved_public_plan = turn_frame_public_plan or rt._build_public_institution_plan(
            request.message,
            list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        composed_public_answer = await rt._compose_public_profile_answer_agentic(
            settings=settings,
            profile=school_profile,
            actor=actor,
            message=request.message,
            original_message=request.message,
            conversation_context=conversation_context,
            semantic_plan=resolved_public_plan,
        )
        if composed_public_answer:
            message_text = composed_public_answer
            composer_used = True
        if message_text:
            if rt._message_matches_term(rt._normalize_text(request.message), 'apenas o que e publico nesse tema'):
                message_text = (
                    'Sobre esse tema, eu continuo sem acesso ao protocolo interno; '
                    f'so posso trazer o que e publico. {message_text}'
                )
            message_text = rt._normalize_response_wording(message_text)
            suggested_replies = rt._build_suggested_replies(
                request=request,
                preview=preview,
                actor=actor,
                school_profile=school_profile,
                conversation_context=conversation_context,
            )
            evidence_pack = rt._build_runtime_evidence_pack(
                request_message=request.message,
                message_text=message_text,
                preview=preview,
                selected_tools=list(preview.selected_tools),
                citations=[],
                school_profile=school_profile,
                actor=actor,
                conversation_context=conversation_context,
                public_plan=None,
                retrieval_backend=RetrievalBackend.none,
            )
            await rt._persist_operational_trace(
                settings=settings,
                conversation_external_id=effective_conversation_id,
                channel=request.channel.value,
                engine_name=state['engine_name'],
                engine_mode=state['engine_mode'],
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
                answer_verifier_reason='langgraph_public_compound_canonical',
                answer_verifier_fallback_used=False,
                deterministic_fallback_available=True,
                answer_verifier_judge_used=False,
                langgraph_trace_metadata=state.get('langgraph_trace_metadata'),
            )
            await rt._persist_conversation_turn(
                settings=settings,
                conversation_external_id=effective_conversation_id,
                channel=request.channel.value,
                actor=actor,
                user_message=request.message,
                assistant_message=message_text,
            )
            response = MessageResponse(
                message_text=message_text,
                mode=OrchestrationMode.structured_tool,
                classification=preview.classification,
                retrieval_backend=RetrievalBackend.none,
                selected_tools=list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                citations=[],
                suggested_replies=suggested_replies,
                evidence_pack=evidence_pack,
                needs_authentication=False,
                graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_compound_canonical'],
                risk_flags=rt._build_runtime_risk_flags(
                    request_message=request.message,
                    message_text=message_text,
                    preview=preview,
                ),
                reason='langgraph_public_compound_canonical',
                used_llm=composer_used,
                llm_stages=['public_answer_composer'] if composer_used else [],
            )
            return {'response': response}

    known_unknown_key = detect_public_known_unknown_key(analysis_message) or detect_public_known_unknown_key(request.message)
    if known_unknown_key:
        message_text = compose_public_known_unknown_answer(
            key=known_unknown_key,
            school_name=str(school_profile.get('school_name', 'Colegio Horizonte')),
        )
        if message_text:
            message_text = rt._normalize_response_wording(message_text)
            suggested_replies = rt._build_suggested_replies(
                request=request,
                preview=preview,
                actor=actor,
                school_profile=school_profile,
                conversation_context=conversation_context,
            )
            evidence_pack = rt._build_runtime_evidence_pack(
                request_message=request.message,
                message_text=message_text,
                preview=preview,
                selected_tools=list(preview.selected_tools),
                citations=[],
                school_profile=school_profile,
                actor=actor,
                conversation_context=conversation_context,
                public_plan=None,
                retrieval_backend=RetrievalBackend.none,
            )
            await rt._persist_operational_trace(
                settings=settings,
                conversation_external_id=effective_conversation_id,
                channel=request.channel.value,
                engine_name=state['engine_name'],
                engine_mode=state['engine_mode'],
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
                answer_verifier_reason='langgraph_public_compound_known_unknown',
                answer_verifier_fallback_used=False,
                deterministic_fallback_available=True,
                answer_verifier_judge_used=False,
                langgraph_trace_metadata=state.get('langgraph_trace_metadata'),
            )
            await rt._persist_conversation_turn(
                settings=settings,
                conversation_external_id=effective_conversation_id,
                channel=request.channel.value,
                actor=actor,
                user_message=request.message,
                assistant_message=message_text,
            )
            response = MessageResponse(
                message_text=message_text,
                mode=OrchestrationMode.structured_tool,
                classification=preview.classification,
                retrieval_backend=RetrievalBackend.none,
                selected_tools=list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                citations=[],
                suggested_replies=suggested_replies,
                evidence_pack=evidence_pack,
                needs_authentication=False,
                graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_compound_known_unknown'],
                risk_flags=rt._build_runtime_risk_flags(
                    request_message=request.message,
                    message_text=message_text,
                    preview=preview,
                ),
                reason='langgraph_public_compound_known_unknown',
                used_llm=False,
                llm_stages=[],
            )
            return {'response': response}

    public_plan = rt._build_public_institution_plan(
        analysis_message,
        list(preview.selected_tools),
        semantic_plan=None,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    message_text = await rt._compose_public_profile_answer_agentic(
        settings=settings,
        profile=school_profile,
        actor=actor,
        message=analysis_message,
        original_message=request.message,
        conversation_context=conversation_context,
        semantic_plan=public_plan,
    )
    message_text = rt._normalize_response_wording(message_text)
    suggested_replies = rt._build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )
    evidence_pack = rt._build_runtime_evidence_pack(
        request_message=request.message,
        message_text=message_text,
        preview=preview,
        selected_tools=list(preview.selected_tools),
        citations=[],
        school_profile=school_profile,
        actor=actor,
        conversation_context=conversation_context,
        public_plan=public_plan,
        retrieval_backend=RetrievalBackend.none,
    )
    await rt._persist_operational_trace(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        engine_name=state['engine_name'],
        engine_mode=state['engine_mode'],
        actor=actor,
        preview=preview,
        school_profile=school_profile,
        conversation_context=conversation_context,
        public_plan=public_plan,
        request_message=request.message,
        message_text=message_text,
        citations_count=0,
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=True,
        answer_verifier_reason='langgraph_public_compound_direct',
        answer_verifier_fallback_used=False,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=False,
        langgraph_trace_metadata=state.get('langgraph_trace_metadata'),
    )
    await rt._persist_conversation_turn(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        actor=actor,
        user_message=request.message,
        assistant_message=message_text,
    )
    response = MessageResponse(
        message_text=message_text,
        mode=OrchestrationMode.structured_tool,
        classification=preview.classification,
        retrieval_backend=RetrievalBackend.none,
        selected_tools=list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
        citations=[],
        suggested_replies=suggested_replies,
        evidence_pack=evidence_pack,
        needs_authentication=False,
        graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_compound'],
        risk_flags=rt._build_runtime_risk_flags(
            request_message=request.message,
            message_text=message_text,
            preview=preview,
        ),
        reason='langgraph_public_compound_direct',
        used_llm=False,
        llm_stages=[],
    )
    return {'response': response}
