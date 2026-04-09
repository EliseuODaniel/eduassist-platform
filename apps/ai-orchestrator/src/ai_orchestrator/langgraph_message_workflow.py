from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from . import runtime as rt
from .langgraph_local_llm import (
    compose_langgraph_with_provider,
    polish_langgraph_with_provider,
    revise_langgraph_with_provider,
    verify_langgraph_answer_against_contract,
)
from .langgraph_runtime import (
    get_langgraph_artifacts,
    invoke_orchestration_graph,
    resolve_langgraph_thread_id,
)
from .models import MessageResponse, OrchestrationMode, QueryDomain, RetrievalBackend, RetrievalProfile
from .public_known_unknowns import compose_public_known_unknown_answer, detect_public_known_unknown_key
from .retrieval import (
    can_read_restricted_documents,
    compose_restricted_document_grounded_answer_for_query,
    compose_restricted_document_no_match_answer,
    get_retrieval_service,
    looks_like_restricted_document_query,
    select_relevant_restricted_hits,
)


class LangGraphMessageState(TypedDict, total=False):
    request: Any
    settings: Any
    engine_name: str
    engine_mode: str
    actor: dict[str, Any] | None
    effective_user: Any
    effective_conversation_id: str | None
    conversation_context_bundle: Any
    conversation_context: dict[str, Any] | None
    analysis_message: str
    school_profile: dict[str, Any] | None
    preview: Any
    langgraph_thread_id: str | None
    langgraph_trace_metadata: dict[str, Any] | None
    route: str
    response: MessageResponse | None


def _deterministic_retrieval_fallback(*, citations: list[Any], context_pack: str | None) -> str:
    if context_pack:
        return rt._normalize_response_wording(context_pack)
    if citations:
        lines = [citation.excerpt for citation in citations[:3] if str(citation.excerpt or '').strip()]
        if lines:
            return rt._normalize_response_wording('\n'.join(lines))
    return 'Nao encontrei evidencias publicas suficientes para responder com seguranca.'


def _route_native_path(preview: Any, request_message: str, analysis_message: str | None = None) -> str:
    analysis_message = analysis_message or request_message
    if analysis_message.strip() != str(request_message).strip():
        if rt.match_public_canonical_lane(analysis_message):
            return 'public_compound'
        if rt._is_public_timeline_query(analysis_message):
            return 'public_compound'
    if (
        preview.classification.access_tier.value == 'public'
        and rt._has_public_multi_intent_signal(request_message)
        and not rt._looks_like_public_documentary_open_query(request_message)
        and any(
            matcher(request_message)
            for matcher in (
                rt._is_service_routing_query,
                rt._matches_public_contact_rule,
                rt._is_public_pricing_navigation_query,
                rt._is_public_timeline_query,
                rt._is_public_calendar_event_query,
                rt._is_public_curriculum_query,
            )
        )
    ):
        return 'public_compound'
    if preview.mode is not OrchestrationMode.hybrid_retrieval:
        return 'delegate_runtime'
    if preview.classification.access_tier.value == 'public':
        return 'public_retrieval'
    if looks_like_restricted_document_query(request_message):
        return 'restricted_retrieval'
    return 'delegate_runtime'


async def _public_compound(state: LangGraphMessageState) -> LangGraphMessageState:
    request = state['request']
    settings = state['settings']
    actor = state['actor']
    preview = state['preview']
    school_profile = state['school_profile']
    conversation_context = state['conversation_context']
    effective_conversation_id = state['effective_conversation_id']
    analysis_message = state['analysis_message']

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
    if prefer_fast_public_direct and rt._base_profile_supports_fast_public_answer(
        message=contextual_public_message,
        profile=school_profile,
    ):
        fast_public_answer = rt._try_public_channel_fast_answer(
            message=contextual_public_message,
            profile=school_profile,
        )
        if fast_public_answer:
            message_text = rt._normalize_response_wording(fast_public_answer)
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
                used_llm=False,
                llm_stages=[],
            )
            return {'response': response}

    canonical_lane = rt.match_public_canonical_lane(analysis_message) or rt.match_public_canonical_lane(request.message)
    if canonical_lane:
        message_text = rt.compose_public_canonical_lane_answer(canonical_lane, profile=school_profile)
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
                used_llm=False,
                llm_stages=[],
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
    message_text = rt._compose_public_profile_answer(
        school_profile,
        analysis_message,
        actor=actor,
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


async def _bootstrap_context(state: LangGraphMessageState) -> LangGraphMessageState:
    request = state['request']
    settings = state['settings']
    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    effective_user = rt._merge_user_context(actor, request.user)
    effective_conversation_id = rt._effective_conversation_id(request)
    conversation_context_bundle = await rt._fetch_conversation_context(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
    )
    conversation_context = rt._conversation_context_payload(conversation_context_bundle)
    analysis_message = rt._build_analysis_message(request.message, conversation_context_bundle)
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    langgraph_artifacts = get_langgraph_artifacts(settings)
    langgraph_thread_id = resolve_langgraph_thread_id(
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        telegram_chat_id=request.telegram_chat_id,
    )
    preview_request = request.model_copy(update={'message': analysis_message})
    graph_state = invoke_orchestration_graph(
        graph=langgraph_artifacts.graph,
        state_input=rt._build_preview_state_input(
            request=preview_request,
            user_context=effective_user,
            settings=settings,
        ),
        thread_id=langgraph_thread_id,
    )
    preview = rt.to_preview(graph_state)
    if actor is not None and request.user.authenticated:
        rt._apply_protected_domain_rescue(
            preview=preview,
            actor=actor,
            message=request.message,
            conversation_context=conversation_context,
        )
    langgraph_trace_metadata = rt._capture_langgraph_trace_metadata(
        graph=langgraph_artifacts.graph,
        thread_id=langgraph_thread_id,
        langgraph_artifacts=langgraph_artifacts,
    )
    return {
        'actor': actor,
        'effective_user': effective_user,
        'effective_conversation_id': effective_conversation_id,
        'conversation_context_bundle': conversation_context_bundle,
        'conversation_context': conversation_context,
        'analysis_message': analysis_message,
        'school_profile': school_profile,
        'preview': preview,
        'langgraph_thread_id': langgraph_thread_id,
        'langgraph_trace_metadata': langgraph_trace_metadata,
        'route': _route_native_path(preview, request.message, analysis_message),
    }


def _after_bootstrap(state: LangGraphMessageState) -> str:
    return str(state.get('route') or 'delegate_runtime')


async def _delegate_runtime(state: LangGraphMessageState) -> LangGraphMessageState:
    response = await rt.generate_message_response(
        request=state['request'],
        settings=state['settings'],
        engine_name=state['engine_name'],
        engine_mode=state['engine_mode'],
    )
    return {'response': response}


async def _public_retrieval(state: LangGraphMessageState) -> LangGraphMessageState:
    request = state['request']
    settings = state['settings']
    preview = state['preview']
    actor = state['actor']
    conversation_context = state['conversation_context']
    school_profile = state['school_profile']
    analysis_message = state['analysis_message']
    effective_conversation_id = state['effective_conversation_id']

    if rt._is_meta_repair_context_query(request.message):
        meta_repair_answer = rt._compose_meta_repair_follow_up_answer(conversation_context)
        if meta_repair_answer:
            message_text = rt._normalize_response_wording(meta_repair_answer)
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
                answer_verifier_reason='langgraph_public_retrieval_meta_repair',
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
                selected_tools=list(preview.selected_tools),
                citations=[],
                suggested_replies=suggested_replies,
                evidence_pack=evidence_pack,
                needs_authentication=False,
                graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_retrieval_meta_repair'],
                risk_flags=rt._build_runtime_risk_flags(
                    request_message=request.message,
                    message_text=message_text,
                    preview=preview,
                ),
                reason='langgraph_public_retrieval_meta_repair',
                used_llm=False,
                llm_stages=[],
            )
            return {'response': response}

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
            answer_verifier_reason='langgraph_public_retrieval_public_boundary',
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
            graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_retrieval_public_boundary'],
            risk_flags=rt._build_runtime_risk_flags(
                request_message=request.message,
                message_text=message_text,
                preview=preview,
            ),
            reason='langgraph_public_retrieval_public_boundary',
            used_llm=False,
            llm_stages=[],
        )
        return {'response': response}

    known_unknown_key = detect_public_known_unknown_key(analysis_message) or detect_public_known_unknown_key(request.message)
    if known_unknown_key:
        message_text = compose_public_known_unknown_answer(
            key=known_unknown_key,
            school_name=str((school_profile or {}).get('school_name', 'Colegio Horizonte')),
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
                answer_verifier_reason='langgraph_public_retrieval_known_unknown',
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
                graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_retrieval_known_unknown'],
                risk_flags=rt._build_runtime_risk_flags(
                    request_message=request.message,
                    message_text=message_text,
                    preview=preview,
                ),
                reason='langgraph_public_retrieval_known_unknown',
                used_llm=False,
                llm_stages=[],
            )
            return {'response': response}

    retrieval_service = get_retrieval_service(
        database_url=str(settings.database_url),
        qdrant_url=str(settings.qdrant_url),
        collection_name=str(settings.qdrant_documents_collection),
        embedding_model=str(settings.document_embedding_model),
        enable_query_variants=bool(settings.retrieval_enable_query_variants),
        enable_late_interaction_rerank=bool(settings.retrieval_enable_late_interaction_rerank),
        late_interaction_model=str(settings.retrieval_late_interaction_model),
        candidate_pool_size=int(settings.retrieval_candidate_pool_size),
        cheap_candidate_pool_size=int(settings.retrieval_cheap_candidate_pool_size),
        deep_candidate_pool_size=int(settings.retrieval_deep_candidate_pool_size),
        rerank_fused_weight=float(settings.retrieval_rerank_fused_weight),
        rerank_late_interaction_weight=float(settings.retrieval_rerank_late_interaction_weight),
    )
    search = retrieval_service.hybrid_search(
        query=analysis_message,
        top_k=4,
        visibility='public',
        category=rt._category_for_domain(preview.classification.domain),
        profile=RetrievalProfile.deep if preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar} else None,
    )
    citations = rt._collect_citations(search.hits, limit=3)
    deterministic_fallback_text = _deterministic_retrieval_fallback(
        citations=citations,
        context_pack=search.context_pack,
    )
    draft_text = await compose_langgraph_with_provider(
        settings=settings,
        request_message=request.message,
        analysis_message=analysis_message,
        preview=preview,
        citations=citations,
        calendar_events=[],
        conversation_context=conversation_context,
        school_profile=school_profile,
        context_pack=search.context_pack,
    )
    message_text = draft_text or deterministic_fallback_text
    llm_stages: list[str] = ['answer_composition'] if draft_text else []

    revised = await revise_langgraph_with_provider(
        settings=settings,
        request_message=request.message,
        preview=preview,
        draft_text=message_text,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    if revised:
        message_text = revised
        llm_stages.append('answer_revision')

    polished = await polish_langgraph_with_provider(
        settings=settings,
        request_message=request.message,
        preview=preview,
        draft_text=message_text,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    if polished:
        message_text = polished
        llm_stages.append('answer_polish')

    verification, semantic_judge_used = await verify_langgraph_answer_against_contract(
        settings=settings,
        request_message=request.message,
        preview=preview,
        candidate_text=message_text,
        deterministic_fallback_text=deterministic_fallback_text,
        public_plan=None,
        slot_memory=rt._build_conversation_slot_memory(
            actor=actor,
            profile=school_profile,
            conversation_context=conversation_context,
            request_message=request.message,
            public_plan=None,
            preview=preview,
        ),
    )
    if not verification.valid:
        message_text = deterministic_fallback_text
        llm_stages = []

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
        citations=citations,
        school_profile=school_profile,
        actor=actor,
        conversation_context=conversation_context,
        public_plan=None,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
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
        citations_count=len(citations),
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=verification.valid,
        answer_verifier_reason=verification.reason,
        answer_verifier_fallback_used=not verification.valid,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=semantic_judge_used,
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
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
        selected_tools=list(preview.selected_tools),
        citations=citations,
        suggested_replies=suggested_replies,
        evidence_pack=evidence_pack,
        needs_authentication=preview.needs_authentication,
        graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_retrieval'],
        risk_flags=rt._build_runtime_risk_flags(
            request_message=request.message,
            message_text=message_text,
            preview=preview,
        ),
        reason='langgraph_native_public_retrieval',
        used_llm=bool(llm_stages),
        llm_stages=llm_stages + (['answer_verifier_judge'] if semantic_judge_used else []),
        retrieval_retry_applied=bool(getattr(search.query_plan, 'corrective_retry_applied', False)),
        retrieval_retry_reason='subquery_coverage_retry' if getattr(search.query_plan, 'corrective_retry_applied', False) else None,
    )
    return {'response': response}


async def _restricted_retrieval(state: LangGraphMessageState) -> LangGraphMessageState:
    request = state['request']
    settings = state['settings']
    preview = state['preview']
    actor = state['actor']
    effective_user = state['effective_user']
    conversation_context = state['conversation_context']
    school_profile = state['school_profile']
    effective_conversation_id = state['effective_conversation_id']
    if not can_read_restricted_documents(effective_user):
        return await _delegate_runtime(state)

    retrieval_service = get_retrieval_service(
        database_url=str(settings.database_url),
        qdrant_url=str(settings.qdrant_url),
        collection_name=str(settings.qdrant_documents_collection),
        embedding_model=str(settings.document_embedding_model),
        enable_query_variants=bool(settings.retrieval_enable_query_variants),
        enable_late_interaction_rerank=bool(settings.retrieval_enable_late_interaction_rerank),
        late_interaction_model=str(settings.retrieval_late_interaction_model),
        candidate_pool_size=int(settings.retrieval_candidate_pool_size),
        cheap_candidate_pool_size=int(settings.retrieval_cheap_candidate_pool_size),
        deep_candidate_pool_size=int(settings.retrieval_deep_candidate_pool_size),
        rerank_fused_weight=float(settings.retrieval_rerank_fused_weight),
        rerank_late_interaction_weight=float(settings.retrieval_rerank_late_interaction_weight),
    )
    search = retrieval_service.hybrid_search(
        query=request.message,
        top_k=3,
        visibility='restricted',
        profile=RetrievalProfile.deep,
    )
    relevant_hits = select_relevant_restricted_hits(request.message, list(search.hits))
    citations = rt._collect_citations(relevant_hits[:3], limit=3)
    restricted_reason = 'langgraph_restricted_doc_grounded' if relevant_hits else 'langgraph_restricted_doc_no_match'
    message_text = rt._normalize_response_wording(
        (
            compose_restricted_document_grounded_answer_for_query(request.message, relevant_hits[:3])
            if relevant_hits
            else compose_restricted_document_no_match_answer(request.message)
        )
    )
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
        citations=citations,
        school_profile=school_profile,
        actor=actor,
        conversation_context=conversation_context,
        public_plan=None,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
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
        citations_count=len(citations),
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=True,
        answer_verifier_reason=restricted_reason,
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
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
        selected_tools=list(preview.selected_tools),
        citations=citations,
        suggested_replies=suggested_replies,
        evidence_pack=evidence_pack,
        needs_authentication=True,
        graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'restricted_retrieval'],
        risk_flags=rt._build_runtime_risk_flags(
            request_message=request.message,
            message_text=message_text,
            preview=preview,
        ),
        reason=restricted_reason,
        used_llm=False,
        llm_stages=[],
        retrieval_retry_applied=bool(getattr(search.query_plan, 'corrective_retry_applied', False)),
        retrieval_retry_reason='subquery_coverage_retry' if getattr(search.query_plan, 'corrective_retry_applied', False) else None,
    )
    return {'response': response}


def _build_langgraph_message_workflow() -> Any:
    workflow = StateGraph(LangGraphMessageState)
    workflow.add_node('bootstrap_context', _bootstrap_context)
    workflow.add_node('public_compound', _public_compound)
    workflow.add_node('public_retrieval', _public_retrieval)
    workflow.add_node('restricted_retrieval', _restricted_retrieval)
    workflow.add_node('delegate_runtime', _delegate_runtime)
    workflow.add_edge(START, 'bootstrap_context')
    workflow.add_conditional_edges(
        'bootstrap_context',
        _after_bootstrap,
        {
            'public_compound': 'public_compound',
            'public_retrieval': 'public_retrieval',
            'restricted_retrieval': 'restricted_retrieval',
            'delegate_runtime': 'delegate_runtime',
        },
    )
    workflow.add_edge('public_compound', END)
    workflow.add_edge('public_retrieval', END)
    workflow.add_edge('restricted_retrieval', END)
    workflow.add_edge('delegate_runtime', END)
    return workflow.compile()


_LANGGRAPH_MESSAGE_WORKFLOW = _build_langgraph_message_workflow()


async def run_langgraph_message_workflow(
    *,
    request: Any,
    settings: Any,
    engine_name: str,
    engine_mode: str,
) -> MessageResponse:
    result = await _LANGGRAPH_MESSAGE_WORKFLOW.ainvoke(
        {
            'request': request,
            'settings': settings,
            'engine_name': engine_name,
            'engine_mode': engine_mode,
        }
    )
    response = result.get('response') if isinstance(result, dict) else None
    if isinstance(response, MessageResponse):
        return response
    raise RuntimeError('langgraph_message_workflow_missing_response')
